"""
扫描版PDF识别器
专门针对扫描版PDF进行优化的OCR识别程序
基于最佳实践配置，支持中英文文档智能识别
"""

import os
import re
import argparse
import time
from pathlib import Path
from datetime import datetime
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import cv2
import numpy as np
import io

# 导入配置文件
from .scan_config import (
    SCAN_IMAGE_ENHANCEMENT,
    SCAN_TEXT_CLEANING,
    FOLDER_CONFIG,
    SCAN_OUTPUT_CONFIG,
    OUTPUT_FORMAT_CONFIG,
    DEFAULT_CHINESE_OCR_CONFIG,
    DEFAULT_ENGLISH_OCR_CONFIG,
    select_chinese_ocr_config,
)

# 导入语言检测模块
from .language_detector import (
    detect_language,
    get_sample_text_for_detection,
)

# 导入文档分析模块
from .document_analyzer import detect_document_type

# 设置Tesseract路径（Windows）
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 获取程序所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 全局变量
processed_files = set()  # 记录已处理的文件
is_monitoring = False  # 监控状态


def enhance_image_quality(image):
    """
    图像质量增强处理

    Args:
        image: PIL Image对象

    Returns:
        PIL Image: 增强后的图像
    """
    try:
        # 转换为OpenCV格式
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # 转换为灰度图
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # 对比度增强 - CLAHE
        clahe = cv2.createCLAHE(
            clipLimit=SCAN_IMAGE_ENHANCEMENT["clahe_clip_limit"],
            tileGridSize=SCAN_IMAGE_ENHANCEMENT["clahe_tile_size"],
        )
        enhanced = clahe.apply(gray)

        # 锐化处理
        if SCAN_IMAGE_ENHANCEMENT["sharpness"]:
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            enhanced = cv2.filter2D(enhanced, -1, kernel)

        # 去噪处理
        if SCAN_IMAGE_ENHANCEMENT["denoise"]:
            enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)

        # 转回PIL格式
        enhanced_pil = Image.fromarray(enhanced)

        return enhanced_pil

    except Exception as e:
        print(f"⚠️ 图像增强失败: {e}")
        return image


def multi_ocr_recognize(image):
    """
    基于最佳实践的多语言OCR识别
    直接使用最佳实践配置，智能选择最优配置

    Args:
        image: PIL Image对象

    Returns:
        str: 识别文本
    """
    try:
        # 1. 快速OCR获取样本文本进行语言检测
        sample_text = get_sample_text_for_detection(image)

        if sample_text:
            # 2. 语言检测
            detected_language, confidence = detect_language(sample_text)

            print(
                f"🔍 语言检测结果: {detected_language} " f"(置信度: {confidence:.2f})"
            )
            print(f"📝 样本文本长度: {len(sample_text)} 字符")
            print(f"📝 样本文本预览: {sample_text[:100]}...")

            # 3. 智能配置选择
            if detected_language == "zh":
                # 中文文档：智能检测文档类型并选择最佳配置
                document_type = detect_document_type(image, sample_text)
                config = select_chinese_ocr_config(document_type)
            elif detected_language == "en":
                # 英文文档使用英文配置
                config = DEFAULT_ENGLISH_OCR_CONFIG
                print(f"📋 使用英文配置: {config['name']}")
            else:
                # 其他语言：使用智能中文配置
                document_type = detect_document_type(image, sample_text)
                config = select_chinese_ocr_config(document_type)

        else:
            # 样本文本提取失败，使用默认配置
            print("⚠️ 样本文本提取失败，使用默认配置")
            config = DEFAULT_CHINESE_OCR_CONFIG

        # 4. 使用选定的配置进行OCR识别
        try:
            # 构建OCR参数
            custom_config = f'--psm {config["psm"]} --dpi {config["dpi"]}'

            # 执行OCR识别
            ocr_text = pytesseract.image_to_string(
                image, lang=config["lang"], config=custom_config
            )

            print(f"✅ OCR识别完成，使用配置: {config['name']}")

            return ocr_text

        except Exception as e:
            print(f"⚠️ OCR识别失败: {e}")
            return ""

    except Exception as e:
        print(f"⚠️ 语言检测失败，使用默认配置: {e}")
        # 语言检测失败，使用默认配置
        try:
            config = DEFAULT_CHINESE_OCR_CONFIG
            custom_config = f'--psm {config["psm"]} --dpi {config["dpi"]}'

            ocr_text = pytesseract.image_to_string(
                image, lang=config["lang"], config=custom_config
            )

            print("✅ 使用默认配置完成OCR识别")

            return ocr_text

        except Exception as e:
            print(f"⚠️ 默认配置OCR识别失败: {e}")
            return ""


def clean_text(text):
    """
    文本清理和格式化

    Args:
        text: 原始文本

    Returns:
        str: 清理后的文本
    """
    if not text:
        return text

    # 移除多余空格
    if SCAN_TEXT_CLEANING["remove_extra_spaces"]:
        text = re.sub(r" +", " ", text)

    # 规范化换行
    if SCAN_TEXT_CLEANING["normalize_newlines"]:
        text = re.sub(r"\n\s*\n\s*\n", "\n\n", text)

    # 修复常见错误
    if SCAN_TEXT_CLEANING["fix_common_errors"]:
        # 修复常见OCR错误
        text = re.sub(r"[0O]", "0", text)  # 0和O混淆
        text = re.sub(r"[1l]", "1", text)  # 1和l混淆

    # 移除行首行尾空格
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines)


def convert_to_markdown(text_content, pdf_path):
    """
    将文本内容转换为Markdown格式

    Args:
        text_content: 原始文本内容
        pdf_path: PDF文件路径

    Returns:
        str: Markdown格式的内容
    """
    # 获取文件名作为标题
    file_name = os.path.basename(pdf_path)
    base_name = Path(file_name).stem

    # 生成Markdown内容
    md_content = f"# {base_name}\n\n"

    # 添加元数据
    if OUTPUT_FORMAT_CONFIG["include_metadata"]:
        md_content += generate_markdown_metadata(pdf_path)
        md_content += "\n"

    # 处理页面内容
    pages = text_content.split("=== 第")
    if len(pages) > 1:
        # 有页面分隔符的情况
        for i, page in enumerate(pages[1:], 1):  # 跳过第一个空元素
            # 提取页面内容
            lines = page.split("\n", 1)
            if len(lines) > 1:
                page_content = lines[1].strip()
                if page_content:
                    if OUTPUT_FORMAT_CONFIG["page_headers"]:
                        md_content += f"## 第 {i} 页\n\n"
                    md_content += page_content + "\n\n"
                    if OUTPUT_FORMAT_CONFIG["separator_line"]:
                        md_content += f"{OUTPUT_FORMAT_CONFIG['separator_line']}\n\n"
    else:
        # 没有页面分隔符的情况，直接添加内容
        md_content += text_content.strip() + "\n\n"

    # 添加处理信息
    if OUTPUT_FORMAT_CONFIG["processing_info"]:
        md_content += "## 处理信息\n\n"
        md_content += f"- **字符数**: {len(text_content.replace('=== 第', '').replace('页 ===', '').strip()):,}\n"
        md_content += (
            f"- **处理时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

    return md_content


def generate_markdown_metadata(pdf_path):
    """
    生成Markdown元数据

    Args:
        pdf_path: PDF文件路径

    Returns:
        str: Markdown格式的元数据
    """
    file_name = os.path.basename(pdf_path)
    file_size = os.path.getsize(pdf_path)
    file_size_mb = file_size / (1024 * 1024)

    metadata = "## 文档信息\n\n"
    metadata += f"- **文件名**: {file_name}\n"
    metadata += f"- **文件大小**: {file_size_mb:.2f} MB\n"
    metadata += f"- **处理时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    metadata += "\n"
    return metadata


def save_markdown_content(content, output_path):
    """
    保存Markdown内容到文件

    Args:
        content: Markdown内容
        output_path: 输出文件路径

    Returns:
        bool: 是否成功
    """
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(
            output_path, "w", encoding=SCAN_OUTPUT_CONFIG["default_encoding"]
        ) as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"❌ Markdown保存失败: {e}")
        return False


def extract_scan_pdf(
    pdf_path, output_path=None, enhance_quality=True, output_format=None
):
    """
    扫描版PDF识别主函数

    Args:
        pdf_path: PDF文件路径
        output_path: 输出文件路径（可选）
        enhance_quality: 是否启用图像质量增强

    Returns:
        bool: 是否成功
    """
    try:
        # 检查文件
        if not os.path.exists(pdf_path):
            print(f"❌ 文件不存在: {pdf_path}")
            return False

        # 确定输出格式
        if output_format is None:
            output_format = OUTPUT_FORMAT_CONFIG["default_format"]

        # 生成输出文件名
        if not output_path:
            base_name = Path(pdf_path).stem
            file_ext = ".md" if output_format == "md" else ".txt"
            output_path = os.path.join(
                SCRIPT_DIR,
                FOLDER_CONFIG["outputs_folder"],
                f"{base_name}_扫描识别{file_ext}",
            )

        print(f"📂 处理文件: {os.path.basename(pdf_path)}")
        print(f"💾 输出文件: {output_path}")
        print(f"📄 输出格式: {output_format.upper()}")
        print(f"🔧 图像增强: {'启用' if enhance_quality else '禁用'}")
        print("-" * 50)

        # 打开PDF文档
        pdf_document = fitz.open(pdf_path)
        total_pages = len(pdf_document)

        print(f"📖 扫描版PDF识别，共 {total_pages} 页...")

        text_content = ""

        for page_num in range(total_pages):
            print(f"\r   OCR进度: {page_num + 1}/{total_pages}", end="")

            # 加载页面
            page = pdf_document.load_page(page_num)

            # 转换为高分辨率图片
            matrix = fitz.Matrix(
                SCAN_IMAGE_ENHANCEMENT["scale_factor"],
                SCAN_IMAGE_ENHANCEMENT["scale_factor"],
            )
            pix = page.get_pixmap(matrix=matrix)
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))

            # 图像质量增强
            if enhance_quality:
                image = enhance_image_quality(image)

            # OCR识别（包含语言检测）
            ocr_text = multi_ocr_recognize(image)

            # 添加页面分隔符
            if SCAN_OUTPUT_CONFIG["include_page_breaks"]:
                text_content += f"\n=== 第 {page_num + 1} 页 ===\n"

            if ocr_text:
                text_content += ocr_text.strip()

            text_content += "\n"

        print()  # 换行
        pdf_document.close()

        # 文本清理
        cleaned_content = clean_text(text_content)

        # 根据格式保存结果
        if output_format in ["md", "markdown"]:
            # 转换为Markdown格式
            md_content = convert_to_markdown(cleaned_content, pdf_path)
            save_success = save_markdown_content(md_content, output_path)
        else:
            # 保存为文本格式
            save_success = save_content(cleaned_content, output_path)

        if save_success:
            # 统计信息
            clean_content = re.sub(r"=== 第 \d+ 页 ===\s*", "", cleaned_content).strip()
            char_count = len(clean_content)

            print("\n✅ 识别完成!")
            print(f"📝 提取字符数: {char_count:,}")
            print(f"💾 已保存到: {output_path}")

            return True
        else:
            return False

    except Exception as e:
        print(f"❌ 扫描版PDF识别失败: {e}")
        return False


def save_content(content, output_path):
    """
    保存内容到文件

    Args:
        content: 文本内容
        output_path: 输出文件路径

    Returns:
        bool: 是否成功
    """
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(
            output_path, "w", encoding=SCAN_OUTPUT_CONFIG["default_encoding"]
        ) as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False


def scan_ocr_uploads_folder():
    """
    扫描ocr_uploads文件夹，返回待处理的PDF文件列表
    参考主项目的文件处理方式

    Returns:
        list: 待处理的PDF文件路径列表
    """
    uploads_folder = os.path.join(SCRIPT_DIR, FOLDER_CONFIG["ocr_uploads_folder"])

    if not os.path.exists(uploads_folder):
        print(f"❌ 文件夹不存在: {uploads_folder}")
        return []

    # 扫描PDF文件
    pdf_files = []
    for file in os.listdir(uploads_folder):
        if file.lower().endswith(".pdf"):
            file_path = os.path.join(uploads_folder, file)
            # 检查文件是否已处理
            if file_path not in processed_files:
                pdf_files.append(file_path)

    return pdf_files


def process_ocr_uploads_folder(output_format=None):
    """
    处理ocr_uploads文件夹中的所有PDF文件
    参考主项目的批量处理方式
    """
    pdf_files = scan_ocr_uploads_folder()

    if not pdf_files:
        uploads_folder = os.path.join(SCRIPT_DIR, FOLDER_CONFIG["ocr_uploads_folder"])
        print(f"📁 {uploads_folder} 文件夹中没有新的PDF文件")
        return

    print("📄 扫描版PDF识别器")
    print("=" * 40)
    uploads_folder = os.path.join(SCRIPT_DIR, FOLDER_CONFIG["ocr_uploads_folder"])
    print(f"📁 扫描 {uploads_folder} 文件夹...")
    print(f"📄 发现 {len(pdf_files)} 个待处理PDF文件")

    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"   {i}. {os.path.basename(pdf_file)}")

    print("\n🔄 开始批量处理...")

    success_count = 0
    total_chars = 0

    for pdf_file in pdf_files:
        print(f"\n📖 处理: {os.path.basename(pdf_file)}")
        success = extract_scan_pdf(
            pdf_file, enhance_quality=True, output_format=output_format
        )

        if success:
            success_count += 1
            # 记录已处理的文件
            processed_files.add(pdf_file)

            # 统计字符数
            file_ext = ".md" if output_format == "md" else ".txt"
            output_file = os.path.join(
                SCRIPT_DIR,
                FOLDER_CONFIG["outputs_folder"],
                f"{Path(pdf_file).stem}_扫描识别{file_ext}",
            )
            if os.path.exists(output_file):
                with open(output_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    total_chars += len(content)

    print("\n🎉 批量处理完成!")
    print("📊 处理统计:")
    print(f"   - 总文件数: {len(pdf_files)}")
    print(f"   - 成功处理: {success_count}")
    print(f"   - 失败文件: {len(pdf_files) - success_count}")
    print(f"   - 总字符数: {total_chars:,}")
    outputs_folder = os.path.join(SCRIPT_DIR, FOLDER_CONFIG["outputs_folder"])
    print(f"💾 结果保存在: {outputs_folder}/ 文件夹")


def monitor_ocr_uploads_folder():
    """
    监控ocr_uploads文件夹，自动处理新文件
    参考主项目的监控模式
    """
    global is_monitoring

    uploads_folder = os.path.join(SCRIPT_DIR, FOLDER_CONFIG["ocr_uploads_folder"])
    print(f"🔍 开始监控 {uploads_folder} 文件夹...")
    print("📝 按 Ctrl+C 停止监控")

    is_monitoring = True

    try:
        while is_monitoring:
            # 扫描新文件
            new_files = scan_ocr_uploads_folder()

            if new_files:
                print(f"\n🆕 发现 {len(new_files)} 个新文件，开始处理...")
                process_ocr_uploads_folder()
            else:
                # 等待一段时间再扫描
                time.sleep(5)

    except KeyboardInterrupt:
        print("\n⏹️ 停止监控")
        is_monitoring = False


def main():
    """
    程序入口函数
    参考主项目的设计模式
    """
    parser = argparse.ArgumentParser(description="扫描版PDF识别器")
    parser.add_argument("pdf_file", nargs="?", help="PDF文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("--enhance", action="store_true", help="启用图像质量增强")
    parser.add_argument(
        "--monitor", action="store_true", help="监控模式，自动处理ocr_uploads文件夹"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="批量处理模式，处理ocr_uploads文件夹中的所有文件",
    )
    parser.add_argument(
        "--format",
        choices=["md", "txt"],
        default="md",
        help="输出格式：md(Markdown) 或 txt(文本)",
    )

    args = parser.parse_args()

    # 监控模式
    if args.monitor:
        monitor_ocr_uploads_folder()
        return

    # 批量处理模式
    if args.batch or not args.pdf_file:
        process_ocr_uploads_folder(output_format=args.format)
        return

    # 处理单个文件
    success = extract_scan_pdf(
        args.pdf_file,
        args.output,
        enhance_quality=args.enhance,
        output_format=args.format,
    )

    if success:
        print("\n🎉 处理完成！")
    else:
        print("\n💡 处理失败，请检查文件格式或Tesseract安装")


if __name__ == "__main__":
    main()

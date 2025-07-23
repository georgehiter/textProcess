"""
扫描版PDF转换器
集成scan_pdf_ocr功能，提供与Marker转换器兼容的接口
"""

import os
import re
import time
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import cv2
import numpy as np
import io

# 导入配置和工具
from api.models import OCRConfig, OutputFormat
from utils.file_handler import FileHandler
from utils.progress import progress_manager, ProgressCallback

# 导入OCR引擎
from utils.ocr_engine import OCREngine

# 设置Tesseract路径（Windows）
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class ScanPDFConverter:
    """扫描版PDF转换器 - 集成OCR功能"""

    def __init__(self, config: OCRConfig):
        """
        初始化扫描转换器

        Args:
            config: OCRConfig配置对象
        """
        self.config = config
        self._extract_config_params()

    def _extract_config_params(self):
        """提取配置参数为实例变量"""
        self.output_format = self.config.output_format
        self.enhance_quality = self.config.enhance_quality
        self.language_detection = self.config.language_detection
        self.document_type_detection = self.config.document_type_detection
        self.ocr_quality = self.config.ocr_quality
        self.target_languages = self.config.target_languages

    async def convert_pdf_async(
        self, pdf_path: str, task_id: str, output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        异步OCR转换

        Args:
            pdf_path: PDF文件路径
            task_id: 任务ID
            output_dir: 输出目录

        Returns:
            转换结果字典
        """
        start_time = time.time()

        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

        # 开始任务
        progress_manager.start_task(task_id, total_stages=4)
        progress_callback = ProgressCallback(task_id, progress_manager)

        try:
            # 阶段1: 初始化
            progress_callback(10)
            await asyncio.sleep(0.1)

            # 阶段2: 设置输出目录
            if output_dir is None:
                file_handler = FileHandler()
                output_dir = file_handler.ensure_output_directory(task_id)
            else:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)

            # 阶段3: 执行OCR转换
            progress_callback(30)
            result = await asyncio.to_thread(
                self._process_pdf_pages, pdf_path, output_dir
            )

            # 阶段4: 处理结果
            progress_callback(80)

            end_time = time.time()
            processing_time = end_time - start_time

            # 完成任务
            progress_callback(100)
            progress_manager.complete_task(task_id, "OCR转换完成")

            # 输出统计信息
            if result.get("success") and result.get("text"):
                char_count = len(result["text"])
                print(f"✅ OCR转换完成! 提取字符数: {char_count:,}")
            else:
                print("✅ OCR转换完成!")

            return {
                "success": True,
                "output_file": result.get("output_file"),
                "metadata_file": result.get("metadata_file"),
                "image_paths": result.get("image_paths", []),
                "processing_time": processing_time,
                "output_format": self.output_format.value,
                "conversion_mode": "ocr",
                "text": result.get("text"),
                "content": result.get("content"),
            }

        except Exception as e:
            error_msg = f"OCR转换失败: {str(e)}"
            progress_manager.fail_task(task_id, error_msg)
            return {
                "success": False,
                "error": error_msg,
                "processing_time": time.time() - start_time,
                "conversion_mode": "ocr",
            }

    def _process_pdf_pages(self, pdf_path: str, output_dir: Path) -> Dict[str, Any]:
        """处理PDF页面并执行OCR"""
        try:
            # 验证文件路径
            pdf_path = str(Path(pdf_path).resolve())
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

            print(f"📂 处理文件: {pdf_path}")

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
                    OCREngine.get_scan_image_enhancement()["scale_factor"],
                    OCREngine.get_scan_image_enhancement()["scale_factor"],
                )
                pix = page.get_pixmap(matrix=matrix)
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))

                # 图像质量增强
                if self.enhance_quality:
                    image = self._enhance_image_quality(image)

                # OCR识别
                ocr_text = self._multi_ocr_recognize(image)

                # 添加页面分隔符
                if OCREngine.get_scan_output_config()["include_page_breaks"]:
                    text_content += f"\n=== 第 {page_num + 1} 页 ===\n"

                if ocr_text:
                    text_content += ocr_text.strip()

                text_content += "\n"

            print()  # 换行
            pdf_document.close()

            # 文本清理
            cleaned_content = self._clean_text(text_content)

            # 生成输出文件路径
            base_name = Path(pdf_path).stem
            output_file = self._save_content(
                cleaned_content, output_dir, base_name, pdf_path
            )

            # 保存元数据
            metadata_file = self._save_metadata(
                {
                    "source_file": pdf_path,
                    "total_pages": total_pages,
                    "processing_time": datetime.now().isoformat(),
                    "ocr_config": {
                        "enhance_quality": self.enhance_quality,
                        "language_detection": self.language_detection,
                        "document_type_detection": (self.document_type_detection),
                        "ocr_quality": self.ocr_quality,
                        "target_languages": self.target_languages,
                    },
                },
                output_dir,
            )

            return {
                "success": True,
                "output_file": str(output_file),
                "metadata_file": str(metadata_file),
                "image_paths": [],
                "text": cleaned_content,
                "content": cleaned_content,
            }

        except Exception as e:
            print(f"❌ PDF处理失败: {e}")
            print(f"📂 文件路径: {pdf_path}")
            print(f"📁 输出目录: {output_dir}")
            return {
                "success": False,
                "output_file": None,
                "metadata_file": None,
                "image_paths": [],
                "text": None,
                "content": None,
            }

    def _enhance_image_quality(self, image: Image.Image) -> Image.Image:
        """图像质量增强处理"""
        try:
            # 转换为OpenCV格式
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # 转换为灰度图
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

            # 对比度增强 - CLAHE
            enhancement_config = OCREngine.get_scan_image_enhancement()
            clahe = cv2.createCLAHE(
                clipLimit=enhancement_config["clahe_clip_limit"],
                tileGridSize=enhancement_config["clahe_tile_size"],
            )
            enhanced = clahe.apply(gray)

            # 锐化处理
            if enhancement_config["sharpness"]:
                kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
                enhanced = cv2.filter2D(enhanced, -1, kernel)

            # 去噪处理
            if enhancement_config["denoise"]:
                enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)

            # 转回PIL格式
            enhanced_pil = Image.fromarray(enhanced)

            return enhanced_pil

        except Exception as e:
            print(f"⚠️ 图像增强失败: {e}")
            return image

    def _multi_ocr_recognize(self, image: Image.Image) -> str:
        """基于最佳实践的多语言OCR识别"""
        try:
            # 1. 快速OCR获取样本文本进行语言检测
            sample_text = OCREngine.get_sample_text_for_detection(image)

            if sample_text and self.language_detection:
                # 2. 语言检测
                detected_language, confidence = OCREngine.detect_language(sample_text)

                print(
                    f"🔍 语言检测结果: {detected_language} "
                    f"(置信度: {confidence:.2f})"
                )

                # 3. 智能配置选择
                if detected_language == "zh":
                    # 中文文档：智能检测文档类型并选择最佳配置
                    if self.document_type_detection:
                        document_type = OCREngine.detect_document_type(
                            image, sample_text
                        )
                        config = OCREngine.select_chinese_ocr_config(document_type)
                    else:
                        config = OCREngine.get_default_chinese_ocr_config()
                elif detected_language == "en":
                    # 英文文档使用英文配置
                    config = OCREngine.get_default_english_ocr_config()
                    print(f"📋 使用英文配置: {config['name']}")
                else:
                    # 其他语言：使用智能中文配置
                    if self.document_type_detection:
                        document_type = OCREngine.detect_document_type(
                            image, sample_text
                        )
                        config = OCREngine.select_chinese_ocr_config(document_type)
                    else:
                        config = OCREngine.get_default_chinese_ocr_config()

            else:
                # 样本文本提取失败或禁用语言检测，使用默认配置
                print("⚠️ 使用默认配置")
                config = OCREngine.get_default_chinese_ocr_config()

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
                config = OCREngine.get_default_chinese_ocr_config()
                custom_config = f'--psm {config["psm"]} --dpi {config["dpi"]}'

                ocr_text = pytesseract.image_to_string(
                    image, lang=config["lang"], config=custom_config
                )

                print("✅ 使用默认配置完成OCR识别")

                return ocr_text

            except Exception as e:
                print(f"⚠️ 默认配置OCR识别失败: {e}")
                return ""

    def _clean_text(self, text: str) -> str:
        """文本清理和格式化"""
        if not text:
            return text

        # 获取文本清理配置
        text_cleaning_config = OCREngine.get_scan_text_cleaning()

        # 移除多余空格
        if text_cleaning_config["remove_extra_spaces"]:
            text = re.sub(r" +", " ", text)

        # 规范化换行
        if text_cleaning_config["normalize_newlines"]:
            text = re.sub(r"\n\s*\n\s*\n", "\n\n", text)

        # 修复常见错误
        if text_cleaning_config["fix_common_errors"]:
            # 修复常见OCR错误
            text = re.sub(r"[0O]", "0", text)  # 0和O混淆
            text = re.sub(r"[1l]", "1", text)  # 1和l混淆

        # 移除行首行尾空格
        lines = [line.strip() for line in text.split("\n")]
        return "\n".join(lines)

    def _convert_to_markdown(self, text_content: str, pdf_path: str) -> str:
        """将文本内容转换为Markdown格式"""
        # 获取文件名作为标题
        file_name = os.path.basename(pdf_path)
        base_name = Path(file_name).stem

        # 生成Markdown内容
        md_content = f"# {base_name}\n\n"

        # 获取输出格式配置
        output_format_config = OCREngine.get_output_format_config()

        # 添加元数据
        if output_format_config["include_metadata"]:
            md_content += self._generate_markdown_metadata(pdf_path)
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
                        if output_format_config["page_headers"]:
                            md_content += f"## 第 {i} 页\n\n"
                        md_content += page_content + "\n\n"
                        if output_format_config["separator_line"]:
                            md_content += (
                                f"{output_format_config['separator_line']}\n\n"
                            )
        else:
            # 没有页面分隔符的情况，直接添加内容
            md_content += text_content.strip() + "\n\n"

        # 添加处理信息
        if output_format_config["processing_info"]:
            md_content += "## 处理信息\n\n"
            clean_content = re.sub(
                r"=== 第", "", text_content.replace("页 ===", "").strip()
            )
            md_content += f"- **字符数**: {len(clean_content):,}\n"
            md_content += (
                f"- **处理时间**: " f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

        return md_content

    def _generate_markdown_metadata(self, pdf_path: str) -> str:
        """生成Markdown元数据"""
        file_name = os.path.basename(pdf_path)
        file_size = os.path.getsize(pdf_path)
        file_size_mb = file_size / (1024 * 1024)

        metadata = "## 文档信息\n\n"
        metadata += f"- **文件名**: {file_name}\n"
        metadata += f"- **文件大小**: {file_size_mb:.2f} MB\n"
        metadata += (
            f"- **处理时间**: " f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        metadata += "\n"
        return metadata

    def _save_content(
        self, content: str, output_dir: Path, filename: str, pdf_path: str
    ) -> Path:
        """保存主要内容"""
        if self.output_format == OutputFormat.markdown:
            output_file = output_dir / f"{filename}.md"
            # 转换为Markdown格式 - 使用完整的pdf_path
            md_content = self._convert_to_markdown(content, pdf_path)
            # 处理markdown内容中的图片引用
            processed_content = self._process_markdown_images(md_content, output_dir)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(processed_content)
        else:
            output_file = output_dir / f"{filename}.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)

        print(f"💾 已保存到: {output_file}")
        return output_file

    def _process_markdown_images(self, content: str, output_dir: Path) -> str:
        """处理markdown内容中的图片引用，替换为API路径"""
        # 获取任务ID（从输出目录名）
        task_id = output_dir.name

        # 查找图片目录
        image_dir = output_dir / "images"
        if not image_dir.exists():
            return content

        # 获取所有图片文件
        image_files = list(image_dir.glob("*.png"))
        image_files.extend(list(image_dir.glob("*.jpeg")))
        image_files.extend(list(image_dir.glob("*.jpg")))

        def replace_image_ref(match):
            alt_text = match.group(1)  # 获取alt文本
            img_path = match.group(2)  # 获取图片路径

            # 提取文件名（去除路径）
            filename = img_path.split("/")[-1]

            # 检查是否有对应的图片文件
            for img_file in image_files:
                # 现在文件名应该完全匹配
                if img_file.name == filename:
                    # 替换为API路径
                    return f"![{alt_text}](/api/images/{task_id}/{filename})"

            # 如果找不到对应的图片文件，保持原样
            return match.group(0)

        # 使用正则表达式替换图片引用
        # 匹配 ![alt](filename) 格式
        pattern = r"!\[([^\]]*)\]\(([^)]+)\)"
        processed_content = re.sub(pattern, replace_image_ref, content)

        return processed_content

    def _save_metadata(self, metadata: Dict, output_dir: Path) -> Path:
        """保存元数据"""
        metadata_file = output_dir / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        return metadata_file


async def scan_convert_pdf_task(
    pdf_path: str, task_id: str, config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    执行OCR转换任务 - 使用OCRConfig对象

    Args:
        pdf_path: PDF文件路径
        task_id: 任务ID
        config: 转换配置（字典格式）

    Returns:
        转换结果
    """
    # 将字典配置转换为OCRConfig对象
    try:
        ocr_config = OCRConfig(**config)
        converter = ScanPDFConverter(config=ocr_config)
        print(f"🔧 OCR转换配置: {ocr_config.ocr_quality}模式")

    except Exception as e:
        print(f"❌ OCR配置处理失败: {str(e)}")
        # 使用默认配置作为后备
        ocr_config = OCRConfig()
        converter = ScanPDFConverter(config=ocr_config)
        print("⚠️ 使用默认OCR配置继续转换")

    output_dir = FileHandler().ensure_output_directory(task_id)
    return await converter.convert_pdf_async(pdf_path, task_id, output_dir)

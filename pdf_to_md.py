import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from marker.output import text_from_rendered


class MarkerPDFConverter:
    """Marker PDF 转换器封装类"""

    def __init__(self, output_format: str = "markdown", use_llm: bool = False):
        """
        初始化转换器

        Args:
            output_format: 输出格式 ("markdown", "json", "html", "chunks")
            use_llm: 是否使用 LLM 提升准确性
        """
        self.output_format = output_format
        self.use_llm = use_llm
        self.converter = None
        self._setup_converter()

    def _setup_converter(self):
        """设置转换器配置"""
        config = {
            "output_format": self.output_format,
            "disable_image_extraction": False,
            "force_ocr": False,
            "format_lines": True,  # 重新格式化行
            "use_llm": self.use_llm,
        }

        config_parser = ConfigParser(config)

        self.converter = PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=create_model_dict(),
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
            llm_service=config_parser.get_llm_service() if self.use_llm else None,
        )

    def convert_pdf(
        self, pdf_path: str, output_dir: Optional[str] = None, save_images: bool = True
    ) -> Dict[str, Any]:
        """
        转换 PDF 文件

        Args:
            pdf_path: PDF 文件路径
            output_dir: 输出目录，如果为 None 则使用默认目录
            save_images: 是否保存提取的图片

        Returns:
            包含转换结果的字典
        """
        start_time = time.time()

        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

        print(f"开始转换 PDF: {pdf_path}")
        print(f"输出格式: {self.output_format}")

        # 执行转换
        try:
            rendered = self.converter(pdf_path)

            # 提取文本和图片
            if self.output_format == "markdown":
                text, metadata, images = text_from_rendered(rendered)
                content = text
            else:
                content = rendered
                metadata = getattr(rendered, "metadata", {})
                images = getattr(rendered, "images", {})

            # 设置输出目录
            if output_dir is None:
                pdf_name = Path(pdf_path).stem
                output_dir = f"./output/{pdf_name}"

            os.makedirs(output_dir, exist_ok=True)

            # 保存主要内容
            output_file = self._save_content(content, output_dir, Path(pdf_path).stem)

            # 保存图片
            image_paths = []
            if save_images and images:
                image_paths = self._save_images(images, output_dir)

            # 保存元数据
            metadata_file = self._save_metadata(metadata, output_dir)

            end_time = time.time()
            processing_time = end_time - start_time

            result = {
                "success": True,
                "output_file": output_file,
                "metadata_file": metadata_file,
                "image_paths": image_paths,
                "processing_time": processing_time,
                "output_format": self.output_format,
                "content": content if self.output_format != "markdown" else None,
                "text": text if self.output_format == "markdown" else None,
            }

            print(f"转换完成! 耗时: {processing_time:.2f} 秒")
            print(f"输出文件: {output_file}")
            print(f"提取图片数量: {len(image_paths)}")

            return result

        except Exception as e:
            print(f"转换失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time,
            }

    def _save_content(self, content: Any, output_dir: str, filename: str) -> str:
        """保存主要内容"""
        if self.output_format == "markdown":
            output_file = os.path.join(output_dir, f"{filename}.md")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
        elif self.output_format == "json":
            output_file = os.path.join(output_dir, f"{filename}.json")
            with open(output_file, "w", encoding="utf-8") as f:
                if hasattr(content, "model_dump"):
                    json.dump(content.model_dump(), f, ensure_ascii=False, indent=2)
                else:
                    json.dump(content, f, ensure_ascii=False, indent=2)
        elif self.output_format == "html":
            output_file = os.path.join(output_dir, f"{filename}.html")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(str(content))
        else:  # chunks
            output_file = os.path.join(output_dir, f"{filename}_chunks.json")
            with open(output_file, "w", encoding="utf-8") as f:
                if hasattr(content, "model_dump"):
                    json.dump(content.model_dump(), f, ensure_ascii=False, indent=2)
                else:
                    json.dump(content, f, ensure_ascii=False, indent=2)

        return output_file

    def _save_images(self, images: Dict, output_dir: str) -> list:
        """保存提取的图片"""
        image_dir = os.path.join(output_dir, "images")
        os.makedirs(image_dir, exist_ok=True)

        image_paths = []
        for img_name, img_data in images.items():
            if img_data:
                # 处理不同的图片数据格式
                if isinstance(img_data, bytes):
                    img_path = os.path.join(image_dir, f"{img_name}.png")
                    with open(img_path, "wb") as f:
                        f.write(img_data)
                    image_paths.append(img_path)
                elif hasattr(img_data, "save"):  # PIL Image
                    img_path = os.path.join(image_dir, f"{img_name}.png")
                    img_data.save(img_path)
                    image_paths.append(img_path)

        return image_paths

    def _save_metadata(self, metadata: Dict, output_dir: str) -> str:
        """保存元数据"""
        metadata_file = os.path.join(output_dir, "metadata.json")
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        return metadata_file


def convert_single_pdf(
    pdf_path: str,
    output_format: str = "markdown",
    output_dir: Optional[str] = None,
    use_llm: bool = False,
) -> Dict[str, Any]:
    """
    便捷函数：转换单个 PDF 文件

    Args:
        pdf_path: PDF 文件路径
        output_format: 输出格式 ("markdown", "json", "html", "chunks")
        output_dir: 输出目录
        use_llm: 是否使用 LLM 提升准确性

    Returns:
        转换结果字典
    """
    converter = MarkerPDFConverter(output_format=output_format, use_llm=use_llm)
    return converter.convert_pdf(pdf_path, output_dir)


def batch_convert_pdfs(
    pdf_folder: str,
    output_folder: str = "./batch_output",
    output_format: str = "markdown",
    use_llm: bool = False,
) -> Dict[str, Any]:
    """
    批量转换 PDF 文件

    Args:
        pdf_folder: 包含 PDF 文件的文件夹路径
        output_folder: 输出文件夹
        output_format: 输出格式
        use_llm: 是否使用 LLM

    Returns:
        批量转换结果
    """
    pdf_files = list(Path(pdf_folder).glob("*.pdf"))

    if not pdf_files:
        return {"success": False, "error": "未找到 PDF 文件"}

    converter = MarkerPDFConverter(output_format=output_format, use_llm=use_llm)
    results = {}

    print(f"找到 {len(pdf_files)} 个 PDF 文件")

    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n处理文件 {i}/{len(pdf_files)}: {pdf_file.name}")

        output_dir = os.path.join(output_folder, pdf_file.stem)
        result = converter.convert_pdf(str(pdf_file), output_dir)
        results[pdf_file.name] = result

    return {"success": True, "total_files": len(pdf_files), "results": results}


# 路径配置
INPUT_FOLDER = "./input"
OUTPUT_FOLDER = "./output"


def scan_input_folder() -> list:
    """扫描输入文件夹中的 PDF 文件"""
    input_path = Path(INPUT_FOLDER)

    if not input_path.exists():
        print(f"错误: 输入文件夹不存在: {INPUT_FOLDER}")
        return []

    pdf_files = list(input_path.glob("*.pdf"))

    if not pdf_files:
        print(f"警告: 在 {INPUT_FOLDER} 中未找到 PDF 文件")
        return []

    print(f"在 {INPUT_FOLDER} 中找到 {len(pdf_files)} 个 PDF 文件:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name}")

    return pdf_files


def process_pdf_files(pdf_files: list, use_llm: bool = False) -> dict:
    """处理 PDF 文件列表"""
    if not pdf_files:
        return {"success": False, "error": "没有可处理的 PDF 文件"}

    total_start_time = time.time()
    results = {}

    print(f"\n开始批量转换 {len(pdf_files)} 个文件...")

    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n处理文件 {i}/{len(pdf_files)}: {pdf_file.name}")

        # 设置输出目录
        output_dir = os.path.join(OUTPUT_FOLDER, pdf_file.stem)

        # 转换文件
        result = convert_single_pdf(
            pdf_path=str(pdf_file),
            output_format="markdown",
            output_dir=output_dir,
            use_llm=use_llm,
        )

        results[pdf_file.name] = result

        if result["success"]:
            print(f"✓ 转换成功: {result['output_file']}")
            print(f"  处理时间: {result['processing_time']:.2f} 秒")
        else:
            print(f"✗ 转换失败: {result['error']}")

    total_time = time.time() - total_start_time

    return {
        "success": True,
        "total_files": len(pdf_files),
        "total_time": total_time,
        "results": results,
    }


# 使用示例
if __name__ == "__main__":
    # 扫描输入文件夹
    pdf_files = scan_input_folder()

    if pdf_files:
        # 批量处理所有 PDF 文件
        batch_result = process_pdf_files(pdf_files, use_llm=False)

        if batch_result["success"]:
            print(f"\n批量转换完成!")
            print(f"总文件数: {batch_result['total_files']}")
            print(f"总耗时: {batch_result['total_time']:.2f} 秒")

            # 统计成功和失败的文件
            success_count = sum(
                1 for result in batch_result["results"].values() if result["success"]
            )
            print(f"成功转换: {success_count}/{batch_result['total_files']} 个文件")
        else:
            print(f"批量转换失败: {batch_result['error']}")
    else:
        print("没有找到可处理的 PDF 文件，程序退出。")

    # 示例: 单个文件转换（保留作为备选方案）
    # result = convert_single_pdf(
    #     pdf_path="zhong-et-al-2024-regional-poverty-alleviation-partnership-and-e-commerce-trade.pdf",
    #     output_format="markdown",
    #     output_dir="./output/single_test",
    #     use_llm=False,
    # )
    #
    # if result["success"]:
    #     print(f"转换成功!")
    #     print(f"输出文件: {result['output_file']}")
    #     print(f"处理时间: {result['processing_time']:.2f} 秒")
    # else:
    #     print(f"转换失败: {result['error']}")

    # 示例: 批量转换（保留作为备选方案）
    # batch_result = batch_convert_pdfs(
    #     pdf_folder="./input",
    #     output_folder="./output",
    #     output_format="markdown"
    # )

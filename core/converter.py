import os
import json
import time
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from marker.output import text_from_rendered
from utils.progress import progress_manager, ProgressCallback
from utils.file_handler import FileHandler
from core.config import settings


class MarkerPDFConverter:
    """Marker PDF 转换器封装类"""

    def __init__(
        self,
        output_format: str = "markdown",
        use_llm: bool = False,
        force_ocr: bool = False,
        save_images: bool = False,  # 优化：关闭图片保存以提升速度
        format_lines: bool = False,  # 关闭行格式化以提升速度
        disable_image_extraction: bool = True,  # 优化：禁用图片提取以提升速度
        strip_existing_ocr: bool = True,  # 新增：去除已有OCR文本以提升速度
    ):
        """
        初始化转换器

        Args:
            output_format: 输出格式 ("markdown", "json", "html", "chunks")
            use_llm: 是否使用 LLM 提升准确性
            force_ocr: 是否强制使用OCR
            save_images: 是否保存提取的图片
            format_lines: 是否重新格式化行
            disable_image_extraction: 是否禁用图片提取
        """
        self.output_format = output_format
        self.use_llm = use_llm
        self.force_ocr = force_ocr
        self.save_images = save_images
        self.format_lines = format_lines
        self.disable_image_extraction = disable_image_extraction
        self.strip_existing_ocr = strip_existing_ocr
        self.converter = None

        # 应用GPU配置
        self._apply_gpu_config()
        self._setup_converter()

    def _apply_gpu_config(self):
        """应用GPU配置"""
        # 直接应用GPU环境变量
        settings.apply_gpu_environment()

    def _setup_converter(self):
        """设置转换器配置"""
        config = {
            "output_format": self.output_format,
            "disable_image_extraction": self.disable_image_extraction,
            "force_ocr": self.force_ocr,
            "format_lines": self.format_lines,
            "use_llm": self.use_llm,
            "strip_existing_ocr": self.strip_existing_ocr,
        }

        # 添加调试日志
        print("🔍 [DEBUG] 转换器配置:")
        print(f"   - force_ocr: {self.force_ocr}")
        print(f"   - strip_existing_ocr: {self.strip_existing_ocr}")
        print(f"   - save_images: {self.save_images}")
        print(f"   - format_lines: {self.format_lines}")
        print(f"   - disable_image_extraction: " f"{self.disable_image_extraction}")

        config_parser = ConfigParser(config)

        self.converter = PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=create_model_dict(),
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
            llm_service=config_parser.get_llm_service() if self.use_llm else None,
        )

    async def convert_pdf_async(
        self, pdf_path: str, task_id: str, output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        异步转换 PDF 文件

        Args:
            pdf_path: PDF 文件路径
            task_id: 任务ID
            output_dir: 输出目录，如果为 None 则使用默认目录

        Returns:
            包含转换结果的字典
        """
        start_time = time.time()

        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

        # 开始任务
        progress_manager.start_task(task_id, total_stages=3)
        progress_callback = ProgressCallback(task_id, progress_manager)

        try:
            # 阶段1: 初始化转换器
            progress_callback(5)
            await asyncio.sleep(0.1)  # 让出控制权

            # 阶段2: 加载PDF文档
            progress_callback(10)
            await asyncio.sleep(0.1)

            # 阶段3: 执行转换（这是最耗时的部分）
            progress_callback(20)
            rendered = await asyncio.to_thread(self.converter, pdf_path)

            # 阶段4: 提取结果
            progress_callback(60)

            if self.output_format == "markdown":
                text, metadata, images = text_from_rendered(rendered)
                content = text
            else:
                content = rendered
                metadata = getattr(rendered, "metadata", {})
                images = getattr(rendered, "images", {})

            # 阶段5: 设置输出目录
            progress_callback(70)
            if output_dir is None:
                output_dir = FileHandler.ensure_output_directory(task_id)
            else:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)

            # 阶段6: 保存主要内容
            progress_callback(80)
            output_file = self._save_content(content, output_dir, Path(pdf_path).stem)

            # 阶段7: 保存图片
            progress_callback(90)
            image_paths = []
            if self.save_images and images:
                image_paths = self._save_images(images, output_dir)

            # 阶段8: 保存元数据
            progress_callback(95)
            metadata_file = self._save_metadata(metadata, output_dir)

            end_time = time.time()
            processing_time = end_time - start_time

            # 阶段9: 完成任务
            progress_callback(100)
            progress_manager.complete_task(task_id, "转换完成")

            result = {
                "success": True,
                "output_file": str(output_file),
                "metadata_file": str(metadata_file),
                "image_paths": image_paths,
                "processing_time": processing_time,
                "output_format": self.output_format,
                "content": content if self.output_format != "markdown" else None,
                "text": text if self.output_format == "markdown" else None,
            }

            return result

        except Exception as e:
            error_msg = f"转换失败: {str(e)}"
            progress_manager.fail_task(task_id, error_msg)
            return {
                "success": False,
                "error": error_msg,
                "processing_time": time.time() - start_time,
            }

    def _save_content(self, content: Any, output_dir: Path, filename: str) -> Path:
        """保存主要内容"""
        if self.output_format == "markdown":
            output_file = output_dir / f"{filename}.md"

            # 处理markdown内容中的图片引用
            processed_content = self._process_markdown_images(content, output_dir)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(processed_content)
        elif self.output_format == "json":
            output_file = output_dir / f"{filename}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                if hasattr(content, "model_dump"):
                    json.dump(content.model_dump(), f, ensure_ascii=False, indent=2)
                else:
                    json.dump(content, f, ensure_ascii=False, indent=2)
        elif self.output_format == "html":
            output_file = output_dir / f"{filename}.html"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(str(content))
        else:  # chunks
            output_file = output_dir / f"{filename}_chunks.json"
            with open(output_file, "w", encoding="utf-8") as f:
                if hasattr(content, "model_dump"):
                    json.dump(content.model_dump(), f, ensure_ascii=False, indent=2)
                else:
                    json.dump(content, f, ensure_ascii=False, indent=2)

        return output_file

    def _save_images(self, images: Dict, output_dir: Path) -> List[str]:
        """保存提取的图片"""
        image_dir = output_dir / "images"
        image_dir.mkdir(exist_ok=True)

        image_paths = []
        for img_name, img_data in images.items():
            if img_data:
                # 保持原始文件名，不强制添加.png扩展名
                img_path = image_dir / img_name

                # 处理不同的图片数据格式
                if isinstance(img_data, bytes):
                    with open(img_path, "wb") as f:
                        f.write(img_data)
                    image_paths.append(str(img_path))
                elif hasattr(img_data, "save"):  # PIL Image
                    img_data.save(img_path)
                    image_paths.append(str(img_path))

        return image_paths

    def _process_markdown_images(self, content: str, output_dir: Path) -> str:
        """处理markdown内容中的图片引用，替换为API路径"""
        import re

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

        # 创建图片文件名映射
        image_map = {}
        for img_file in image_files:
            # 移除扩展名作为key
            base_name = img_file.stem
            image_map[base_name] = img_file.name

            # 替换markdown中的图片引用

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


async def convert_pdf_task(
    pdf_path: str, task_id: str, config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    执行PDF转换任务

    Args:
        pdf_path: PDF文件路径
        task_id: 任务ID
        config: 转换配置

    Returns:
        转换结果
    """
    converter = MarkerPDFConverter(
        output_format=config.get("output_format", "markdown"),
        use_llm=config.get("use_llm", False),
        force_ocr=config.get("force_ocr", False),
        save_images=config.get("save_images", False),
        format_lines=config.get("format_lines", False),
        disable_image_extraction=config.get("disable_image_extraction", True),
        strip_existing_ocr=config.get("strip_existing_ocr", True),
    )

    output_dir = FileHandler.ensure_output_directory(task_id)
    return await converter.convert_pdf_async(pdf_path, task_id, output_dir)

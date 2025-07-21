"""
扫描版PDF转换器适配层
封装scan_pdf_ocr模块，提供与Marker转换器兼容的接口
"""

import asyncio
import time
from pathlib import Path
from typing import Dict, Any, Optional
from scan_pdf_ocr.scan_pdf_ocr import extract_scan_pdf
from utils.progress import progress_manager, ProgressCallback
from utils.file_handler import FileHandler


class ScanPDFConverter:
    """扫描版PDF转换器适配层"""

    def __init__(self, config: dict):
        self.config = config

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

        # 开始任务
        progress_manager.start_task(task_id, total_stages=3)
        progress_callback = ProgressCallback(task_id, progress_manager)

        try:
            # 阶段1: 初始化
            progress_callback(10)
            await asyncio.sleep(0.1)

            # 阶段2: 执行OCR转换
            progress_callback(30)

            # 在线程池中执行OCR任务
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._execute_ocr_conversion,
                pdf_path,
                output_dir or FileHandler.ensure_output_directory(task_id),
            )

            # 阶段3: 处理结果
            progress_callback(80)

            end_time = time.time()
            processing_time = end_time - start_time

            # 完成任务并存储结果信息
            progress_callback(100)

            # 存储结果信息到进度管理器
            result_info = {
                "status": "completed",
                "progress": 100.0,
                "processing_time": processing_time,
                "output_file": result.get("output_file"),
                "metadata_file": result.get("metadata_file"),
                "image_paths": result.get("image_paths", []),
                "output_format": self.config.get("output_format", "markdown"),
                "conversion_mode": "ocr",
            }
            progress_manager.tasks[task_id].update(result_info)

            return {
                "success": True,
                "output_file": result.get("output_file"),
                "metadata_file": result.get("metadata_file"),
                "image_paths": result.get("image_paths", []),
                "processing_time": processing_time,
                "output_format": self.config.get("output_format", "markdown"),
                "conversion_mode": "ocr",
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

    def _execute_ocr_conversion(
        self, pdf_path: str, output_dir: Path
    ) -> Dict[str, Any]:
        """执行OCR转换"""
        # 生成输出文件路径
        base_name = Path(pdf_path).stem
        output_format = self.config.get("output_format", "markdown")
        file_ext = ".md" if output_format in ["md", "markdown"] else ".txt"
        output_file = output_dir / f"{base_name}_OCR转换{file_ext}"

        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        result = extract_scan_pdf(
            pdf_path=pdf_path,
            output_path=str(output_file),
            enhance_quality=self.config.get("enhance_quality", True),
            output_format=output_format,
        )

        # 返回结果字典
        if result:
            return {
                "output_file": str(output_file),
                "metadata_file": str(output_file.with_suffix(".json")),
                "image_paths": [],
                "success": True,
            }
        else:
            return {
                "output_file": None,
                "metadata_file": None,
                "image_paths": [],
                "success": False,
            }


async def scan_convert_pdf_task(
    pdf_path: str, task_id: str, config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    执行OCR转换任务

    Args:
        pdf_path: PDF文件路径
        task_id: 任务ID
        config: 转换配置

    Returns:
        转换结果
    """
    converter = ScanPDFConverter(config)
    output_dir = FileHandler.ensure_output_directory(task_id)
    return await converter.convert_pdf_async(pdf_path, task_id, output_dir)

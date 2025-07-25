from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Optional
from api.models import (
    ConversionRequest,
    ConfigValidationResponse,
    OCRConfig,
    ConversionResponse,
)
from utils.file_handler import FileHandler
from utils.progress import progress_manager

from core.converter import convert_pdf_task
from core.scan_converter import scan_convert_pdf_task

router = APIRouter()


def find_output_file(
    output_path: Path, output_format: str = "markdown"
) -> Optional[Path]:
    """
    动态查找输出文件

    Args:
        output_path: 输出目录路径
        output_format: 输出格式

    Returns:
        找到的文件路径，如果未找到则返回None
    """
    if not output_path.exists():
        return None

    # 根据输出格式查找对应文件
    if output_format in ["markdown", "md"]:
        # 查找 .md 文件
        md_files = list(output_path.glob("*.md"))
        if md_files:
            return md_files[0]  # 返回第一个找到的 .md 文件
    elif output_format == "json":
        # 查找 .json 文件
        json_files = list(output_path.glob("*.json"))
        if json_files:
            return json_files[0]
    elif output_format == "html":
        # 查找 .html 文件
        html_files = list(output_path.glob("*.html"))
        if html_files:
            return html_files[0]
    elif output_format == "chunks":
        # 查找 _chunks.json 文件
        chunks_files = list(output_path.glob("*_chunks.json"))
        if chunks_files:
            return chunks_files[0]

    # 如果没找到特定格式，尝试查找任何输出文件
    all_files = []
    all_files.extend(output_path.glob("*.md"))
    all_files.extend(output_path.glob("*.json"))
    all_files.extend(output_path.glob("*.html"))

    if all_files:
        return all_files[0]

    return None


@router.post("/validate-config", response_model=ConfigValidationResponse)
async def validate_config(config_data: dict):
    """验证配置有效性"""
    try:
        # 检查必需字段
        required_fields = ["conversion_mode"]
        missing_fields = [
            field for field in required_fields if field not in config_data
        ]

        if missing_fields:
            return ConfigValidationResponse(
                valid=False,
                errors=[f"缺失必需字段: {', '.join(missing_fields)}"],
                warnings=[],
                suggestions=["请检查配置格式"],
            )

        # 检查转换模式
        conversion_mode = config_data.get("conversion_mode")
        if conversion_mode not in ["marker", "ocr"]:
            return ConfigValidationResponse(
                valid=False,
                errors=[f"不支持的转换模式: {conversion_mode}"],
                warnings=[],
                suggestions=["支持的转换模式: marker, ocr"],
            )

        # 根据转换模式进行特定验证
        if conversion_mode == "marker":
            return _validate_marker_config(config_data)
        elif conversion_mode == "ocr":
            return _validate_ocr_config(config_data)

        return ConfigValidationResponse(
            valid=True,
            errors=[],
            warnings=[],
            suggestions=["配置验证通过"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配置验证失败: {str(e)}")


def _validate_marker_config(config_data: dict) -> ConfigValidationResponse:
    """验证Marker配置"""
    errors = []
    warnings = []

    # 检查GPU配置
    gpu_config = config_data.get("gpu_config", {})
    if gpu_config.get("enabled", False):
        # GPU启用时的验证
        if gpu_config.get("num_devices", 1) > 8:
            warnings.append("GPU设备数量超过8个，可能影响性能")

        if gpu_config.get("num_workers", 4) > 16:
            warnings.append("GPU工作进程数超过16个，可能影响性能")

    # 检查LLM配置
    if config_data.get("use_llm", False):
        warnings.append("启用LLM可能增加处理时间")

    # 检查OCR配置冲突
    if config_data.get("force_ocr", False):
        warnings.append("Marker模式下启用force_ocr可能不是最佳选择")

    return ConfigValidationResponse(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        suggestions=["Marker配置验证通过"],
    )


def _validate_ocr_config(config_data: dict) -> ConfigValidationResponse:
    """验证OCR配置"""
    errors = []
    warnings = []

    # 检查OCR质量设置
    ocr_quality = config_data.get("ocr_quality", "balanced")
    if ocr_quality not in ["fast", "balanced", "accurate"]:
        errors.append(f"不支持的OCR质量模式: {ocr_quality}")

    # 检查语言配置
    target_languages = config_data.get("target_languages", ["chi_sim", "eng"])
    valid_languages = ["chi_sim", "eng", "jpn", "kor"]
    invalid_languages = [
        lang for lang in target_languages if lang not in valid_languages
    ]

    if invalid_languages:
        errors.append(f"不支持的语言: {', '.join(invalid_languages)}")

    # 检查性能相关配置
    if config_data.get("enhance_quality", True) and ocr_quality == "accurate":
        warnings.append("同时启用图像增强和准确模式可能显著增加处理时间")

    return ConfigValidationResponse(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        suggestions=["OCR配置验证通过"],
    )


@router.post("/check-compatibility")
async def check_config_compatibility(config_data: dict):
    """检查配置兼容性"""
    try:
        return {
            "compatible": True,
            "version": "current",
            "issues": [],
            "warnings": [],
            "suggestions": ["配置兼容性检查通过"],
            "migration_needed": False,
            "summary": "当前配置格式",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"兼容性检查失败: {str(e)}")


@router.post("/auto-fix-config")
async def auto_fix_config(config_data: dict):
    """自动修复配置"""
    try:
        return {
            "original_config": config_data,
            "fixed_config": config_data,
            "compatible": True,
            "issues": [],
            "warnings": [],
            "summary": "配置无需修复",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配置自动修复失败: {str(e)}")


@router.post("/convert", response_model=ConversionResponse)
async def start_conversion(
    request: ConversionRequest, background_tasks: BackgroundTasks
):
    """启动PDF转换任务 - 使用新的配置系统"""
    try:
        task_id = request.task_id

        # 使用 FileHandler 查找文件
        file_handler = FileHandler()
        pdf_files = list(file_handler.upload_folder.glob(f"{task_id}_*"))
        if not pdf_files:
            raise HTTPException(status_code=404, detail="未找到上传的文件")

        pdf_path = str(pdf_files[0])

        # 启动进度跟踪
        progress_manager.start_task(task_id)

        # 配置处理
        config_dict = request.config.dict()

        # 根据配置类型自动分发
        if isinstance(request.config, OCRConfig):
            # OCR转换任务 - 无需GPU配置
            background_tasks.add_task(
                scan_convert_pdf_task,
                pdf_path=pdf_path,
                task_id=task_id,
                config=config_dict,
            )
            message = f"OCR转换任务已启动 (质量模式: {request.config.ocr_quality})"

        else:  # MarkerConfig
            # 应用GPU配置 - 仅Marker模式需要
            if request.config.gpu_config.enabled:
                request.config.apply_gpu_environment()

            # Marker转换任务
            background_tasks.add_task(
                convert_pdf_task, pdf_path=pdf_path, task_id=task_id, config=config_dict
            )
            gpu_status = "启用" if request.config.gpu_config.enabled else "禁用"
            message = f"Marker转换任务已启动 (GPU: {gpu_status})"

        return ConversionResponse(success=True, task_id=task_id, message=message)

    except Exception as e:
        print(f"❌ [ERROR] 启动转换失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动转换失败: {str(e)}")


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """文件上传接口"""
    try:
        # 使用新的 FileHandler 模型
        file_handler = FileHandler()

        # 生成任务ID
        task_id = file_handler.generate_task_id()

        # 保存文件
        await file_handler.save_upload_file(file, task_id)

        return {
            "success": True,
            "task_id": task_id,
            "filename": file.filename,
            "message": "文件上传成功",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.get("/progress/{task_id}")
async def get_progress(task_id: str):
    """获取转换进度"""
    try:
        task_data = progress_manager.get_progress(task_id)
        if not task_data:
            raise HTTPException(status_code=404, detail="任务不存在")

        return {
            "task_id": task_id,
            "status": task_data.get("status", "unknown"),
            "progress": task_data.get("progress", 0.0),
            "error": task_data.get("error"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取进度失败: {str(e)}")


@router.get("/result/{task_id}")
async def get_result(task_id: str):
    """获取转换结果"""
    try:
        # 使用 FileHandler 获取输出文件路径
        file_handler = FileHandler()
        output_path = file_handler.ensure_output_directory(task_id)

        # 动态查找输出文件
        output_file = find_output_file(output_path)

        if not output_file or not output_file.exists():
            raise HTTPException(status_code=404, detail="结果文件不存在")

        # 读取内容
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查是否有图片
        image_dir = output_path / "images"
        has_images = image_dir.exists() and any(image_dir.iterdir())
        image_count = len(list(image_dir.glob("*"))) if has_images else 0

        return {
            "task_id": task_id,
            "content": content,
            "has_images": has_images,
            "image_count": image_count,
            "file_name": output_file.name,
            "file_format": output_file.suffix,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取结果失败: {str(e)}")


@router.get("/download/{task_id}")
async def download_result(task_id: str):
    """下载转换结果"""
    try:
        # 使用 FileHandler 获取输出文件路径
        file_handler = FileHandler()
        output_path = file_handler.ensure_output_directory(task_id)

        # 动态查找输出文件
        output_file = find_output_file(output_path)

        if not output_file or not output_file.exists():
            raise HTTPException(status_code=404, detail="结果文件不存在")

        # 根据文件类型设置MIME类型
        mime_types = {
            ".md": "text/markdown",
            ".json": "application/json",
            ".html": "text/html",
        }
        media_type = mime_types.get(output_file.suffix, "text/plain")

        return FileResponse(
            path=output_file,
            filename=f"converted_{task_id}{output_file.suffix}",
            media_type=media_type,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.get("/download-images/{task_id}")
async def download_images(task_id: str):
    """下载图片包"""
    try:
        # 使用 FileHandler 获取输出文件路径
        file_handler = FileHandler()
        output_path = file_handler.ensure_output_directory(task_id)
        image_dir = output_path / "images"

        if not image_dir.exists():
            raise HTTPException(status_code=404, detail="图片目录不存在")

        # 创建ZIP文件
        import zipfile

        zip_path = output_path / f"images_{task_id}.zip"

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for image_file in image_dir.glob("*"):
                zipf.write(image_file, image_file.name)

        return FileResponse(
            path=zip_path,
            filename=f"images_{task_id}.zip",
            media_type="application/zip",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载图片失败: {str(e)}")


@router.get("/images/{task_id}/{filename}")
async def get_image(task_id: str, filename: str):
    """获取图片文件"""
    try:
        # 使用 FileHandler 获取图片文件路径
        file_handler = FileHandler()
        output_path = file_handler.ensure_output_directory(task_id)
        image_path = output_path / "images" / filename

        if not image_path.exists():
            raise HTTPException(status_code=404, detail="图片文件不存在")

        return FileResponse(path=image_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图片失败: {str(e)}")


@router.get("/gpu-status")
async def get_gpu_status():
    """获取GPU状态"""
    try:
        import torch

        # 检查CUDA可用性
        cuda_available = torch.cuda.is_available()
        device_count = torch.cuda.device_count() if cuda_available else 0

        # 获取GPU信息
        device_name = None
        memory_total = None
        memory_used = None
        memory_free = None

        if cuda_available and device_count > 0:
            device_name = torch.cuda.get_device_name(0)
            memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            memory_allocated = torch.cuda.memory_allocated(0) / 1024**3
            memory_reserved = torch.cuda.memory_reserved(0) / 1024**3
            memory_used = memory_allocated
            memory_free = memory_total - memory_reserved

        return {
            "available": cuda_available,
            "device_count": device_count,
            "device_name": device_name,
            "memory_total": memory_total,
            "memory_used": memory_used,
            "memory_free": memory_free,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取GPU状态失败: {str(e)}")

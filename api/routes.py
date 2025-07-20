from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, Response
import torch
from api.models import (
    FileUploadResponse,
    ConversionRequest,
    ConversionResponse,
    ConversionResult,
    ProgressData,
    HealthResponse,
    GPUStatus,
    GPUConfig,
)
from utils.file_handler import FileHandler
from utils.progress import progress_manager
from core.converter import convert_pdf_task
from core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    return HealthResponse()


@router.get("/gpu-status", response_model=GPUStatus)
async def get_gpu_status():
    """获取GPU状态接口"""
    try:
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

        # 获取版本信息
        cuda_version = torch.version.cuda if cuda_available else None
        pytorch_version = torch.__version__

        # 获取当前GPU配置
        current_config = GPUConfig(
            enabled=settings.GPU_ENABLED,
            devices=settings.GPU_DEVICES,
            workers=settings.GPU_WORKERS,
            memory_limit=settings.GPU_MEMORY_LIMIT,
        )

        return GPUStatus(
            available=cuda_available,
            device_count=device_count,
            device_name=device_name,
            memory_total=memory_total,
            memory_used=memory_used,
            memory_free=memory_free,
            cuda_version=cuda_version,
            pytorch_version=pytorch_version,
            current_config=current_config,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取GPU状态失败: {str(e)}")


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """文件上传接口"""
    try:
        # 生成任务ID
        task_id = FileHandler.generate_task_id()

        # 保存文件
        success, message, file_path = await FileHandler.save_upload_file(file, task_id)

        if not success:
            raise HTTPException(status_code=400, detail=message)

        # 获取文件信息
        file_info = FileHandler.get_file_info(file_path)

        return FileUploadResponse(
            success=True,
            task_id=task_id,
            filename=file.filename,
            file_size=file_info.get("size"),
            message=message,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.post("/convert", response_model=ConversionResponse)
async def start_conversion(
    request: ConversionRequest, background_tasks: BackgroundTasks
):
    """开始转换接口"""
    try:
        task_id = request.task_id

        # 查找上传的文件
        upload_pattern = f"{task_id}_*"
        pdf_files = list(Path("uploads").glob(upload_pattern))

        if not pdf_files:
            raise HTTPException(
                status_code=404, detail="未找到上传的文件，请先上传PDF文件"
            )

        pdf_path = str(pdf_files[0])

        # 应用GPU配置
        gpu_config = request.config.gpu_config
        if gpu_config.enabled:
            settings.GPU_ENABLED = True
            settings.GPU_DEVICES = gpu_config.devices
            settings.GPU_WORKERS = gpu_config.workers
            settings.GPU_MEMORY_LIMIT = gpu_config.memory_limit
            settings.apply_gpu_environment()
        else:
            settings.GPU_ENABLED = False
            settings.apply_gpu_environment()

        # 添加调试日志
        print(f"🔍 [DEBUG] 转换请求参数:")
        print(f"   - force_ocr: {request.config.force_ocr}")
        print(f"   - strip_existing_ocr: {request.config.strip_existing_ocr}")
        print(f"   - save_images: {request.config.save_images}")
        print(f"   - format_lines: {request.config.format_lines}")
        print(
            f"   - disable_image_extraction: {request.config.disable_image_extraction}"
        )
        print(f"   - gpu_config: {request.config.gpu_config}")

        # 在后台执行转换任务
        background_tasks.add_task(
            convert_pdf_task,
            pdf_path=pdf_path,
            task_id=task_id,
            config=request.config.dict(),
        )

        return ConversionResponse(
            success=True, task_id=task_id, message="转换任务已启动"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动转换失败: {str(e)}")


@router.get("/progress/{task_id}", response_model=ProgressData)
async def get_progress(task_id: str):
    """获取转换进度接口"""
    progress = progress_manager.get_progress(task_id)

    if not progress:
        raise HTTPException(status_code=404, detail="任务不存在")

    return ProgressData(
        task_id=task_id,
        status=progress.get("status", "unknown"),
        progress=progress.get("progress", 0.0),
        error=progress.get("error"),
    )


@router.get("/result/{task_id}", response_model=ConversionResult)
async def get_result(task_id: str):
    """获取转换结果接口"""
    try:
        # 检查任务状态
        progress = progress_manager.get_progress(task_id)
        if not progress:
            raise HTTPException(status_code=404, detail="任务不存在")

        if progress.get("status") == "failed":
            return ConversionResult(
                task_id=task_id, success=False, error=progress.get("error", "转换失败")
            )

        if progress.get("status") != "completed":
            raise HTTPException(status_code=400, detail="转换尚未完成，请稍后再试")

        # 查找输出文件
        output_dir = Path("outputs") / task_id
        if not output_dir.exists():
            raise HTTPException(status_code=404, detail="输出文件不存在")

        # 查找markdown文件
        md_files = list(output_dir.glob("*.md"))
        if not md_files:
            raise HTTPException(status_code=404, detail="未找到转换结果")

        md_file = md_files[0]

        # 读取文件内容预览
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
            text_preview = content[:1000] + "..." if len(content) > 1000 else content

        # 查找图片文件
        image_dir = output_dir / "images"
        image_paths = []
        if image_dir.exists():
            # 查找所有类型的图片文件
            image_paths = []
            for pattern in ["*.png", "*.jpeg", "*.jpg", "*.gif", "*.bmp", "*.tiff"]:
                image_paths.extend([str(p) for p in image_dir.glob(pattern)])

        # 查找元数据文件
        metadata_file = output_dir / "metadata.json"

        return ConversionResult(
            task_id=task_id,
            success=True,
            output_file=str(md_file),
            metadata_file=str(metadata_file) if metadata_file.exists() else None,
            image_paths=image_paths,
            processing_time=progress.get("processing_time"),
            output_format="markdown",
            text_preview=text_preview,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取结果失败: {str(e)}")


@router.get("/download-images/{task_id}")
async def download_images(task_id: str):
    """下载转换结果中的图片压缩包"""
    try:
        import zipfile
        import io

        # 查找输出目录
        output_dir = Path("outputs") / task_id
        if not output_dir.exists():
            raise HTTPException(status_code=404, detail="输出文件不存在")

        # 查找图片目录
        image_dir = output_dir / "images"
        if not image_dir.exists():
            raise HTTPException(status_code=404, detail="图片文件不存在")

        # 获取所有图片文件（现在文件名保持原始格式）
        image_files = []
        # 查找所有可能的图片文件
        for pattern in ["*.png", "*.jpeg", "*.jpg", "*.gif", "*.bmp", "*.tiff"]:
            image_files.extend(list(image_dir.glob(pattern)))

        if not image_files:
            raise HTTPException(status_code=404, detail="没有找到图片文件")

        # 创建内存中的zip文件
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for img_file in image_files:
                # 将图片文件添加到zip中
                zip_file.write(img_file, img_file.name)

        # 重置缓冲区位置
        zip_buffer.seek(0)

        # 返回zip文件
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={task_id}_images.zip"
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载图片压缩包失败: {str(e)}")


@router.get("/download/{task_id}")
async def download_result(task_id: str):
    """下载转换结果接口"""
    try:
        # 查找输出文件
        output_dir = Path("outputs") / task_id
        if not output_dir.exists():
            raise HTTPException(status_code=404, detail="输出文件不存在")

        # 查找markdown文件
        md_files = list(output_dir.glob("*.md"))
        if not md_files:
            raise HTTPException(status_code=404, detail="未找到转换结果")

        md_file = md_files[0]

        return FileResponse(
            path=md_file, filename=md_file.name, media_type="text/markdown"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.get("/images/{task_id}/{filename}")
async def get_image(task_id: str, filename: str):
    """获取转换结果中的图片文件"""
    try:
        # 构建图片文件路径
        image_path = Path("outputs") / task_id / "images" / filename

        # 检查文件是否存在
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="图片文件不存在")

        # 检查文件是否在允许的目录内（安全验证）
        try:
            image_path.resolve().relative_to(Path("outputs").resolve())
        except ValueError:
            raise HTTPException(status_code=403, detail="访问被拒绝")

        # 返回图片文件
        # 根据文件扩展名确定媒体类型
        if filename.endswith(".png"):
            media_type = "image/png"
        elif filename.endswith(".jpeg") or filename.endswith(".jpg"):
            media_type = "image/jpeg"
        elif filename.endswith(".gif"):
            media_type = "image/gif"
        elif filename.endswith(".bmp"):
            media_type = "image/bmp"
        elif filename.endswith(".tiff"):
            media_type = "image/tiff"
        else:
            media_type = "image/png"  # 默认类型

        return FileResponse(
            path=image_path,
            media_type=media_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图片失败: {str(e)}")


@router.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """删除任务接口"""
    try:
        # 删除上传的文件
        upload_pattern = f"{task_id}_*"
        for file_path in Path("uploads").glob(upload_pattern):
            file_path.unlink()

        # 删除输出文件
        output_dir = Path("outputs") / task_id
        if output_dir.exists():
            import shutil

            shutil.rmtree(output_dir)

        # 删除临时文件
        temp_dir = Path("templates") / task_id
        if temp_dir.exists():
            import shutil

            shutil.rmtree(temp_dir)

        # 删除进度信息
        progress_manager.remove_task(task_id)

        return {"success": True, "message": "任务已删除"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")

from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from api.models import (
    FileUploadResponse,
    ConversionRequest,
    ConversionResponse,
    ConversionResult,
    ProgressData,
    HealthResponse,
)
from utils.file_handler import FileHandler
from utils.progress import progress_manager
from core.converter import convert_pdf_task

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    return HealthResponse()


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
        current_stage=progress.get("current_stage"),
        stage_progress=progress.get("stage_progress", 0.0),
        stage_current=progress.get("stage_current", 0),
        stage_total=progress.get("stage_total", 0),
        elapsed_time=progress.get("elapsed_time"),
        estimated_time=progress.get("estimated_time"),
        processing_rate=progress.get("processing_rate"),
        message=progress.get("message"),
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
            image_paths = [str(p) for p in image_dir.glob("*.png")]

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


@router.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """删除任务接口"""
    try:
        # 清理文件
        FileHandler.cleanup_task_files(task_id)

        # 清理进度信息
        progress_manager.remove_task(task_id)

        return {"success": True, "message": "任务已删除"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

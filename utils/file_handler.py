import shutil
import uuid
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile
from core.config import settings


class FileHandler:
    """文件处理类"""

    @staticmethod
    def generate_task_id() -> str:
        """生成任务ID"""
        return str(uuid.uuid4())

    @staticmethod
    def validate_file(file: UploadFile) -> Tuple[bool, str]:
        """验证上传文件"""
        # 检查文件扩展名
        if not settings.is_valid_file(file.filename):
            return False, "不支持的文件格式，仅支持PDF文件"

        # 检查文件大小
        if file.size and file.size > settings.MAX_FILE_SIZE:
            return (
                False,
                f"文件大小超过限制，最大支持{settings.MAX_FILE_SIZE // (1024*1024)}MB",
            )

        return True, "文件验证通过"

    @staticmethod
    async def save_upload_file(
        file: UploadFile, task_id: str
    ) -> Tuple[bool, str, Optional[Path]]:
        """保存上传文件"""
        try:
            # 验证文件
            is_valid, message = FileHandler.validate_file(file)
            if not is_valid:
                return False, message, None

            # 生成文件路径
            filename = file.filename
            file_path = settings.get_file_path(task_id, filename)

            # 保存文件
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            return True, "文件上传成功", file_path

        except Exception as e:
            return False, f"文件保存失败: {str(e)}", None

    @staticmethod
    def cleanup_task_files(task_id: str) -> bool:
        """清理任务相关文件"""
        try:
            # 清理上传文件
            upload_pattern = f"{task_id}_*"
            for file_path in settings.upload_path.glob(upload_pattern):
                file_path.unlink()

            # 清理输出文件
            output_dir = settings.get_output_path(task_id)
            if output_dir.exists():
                shutil.rmtree(output_dir)

            # 清理临时文件
            temp_dir = settings.get_temp_path(task_id)
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

            return True

        except Exception as e:
            print(f"清理文件失败: {str(e)}")
            return False

    @staticmethod
    def get_file_info(file_path: Path) -> dict:
        """获取文件信息"""
        try:
            stat = file_path.stat()
            return {
                "filename": file_path.name,
                "size": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime,
            }
        except Exception as e:
            return {"filename": file_path.name, "error": str(e)}

    @staticmethod
    def ensure_output_directory(task_id: str) -> Path:
        """确保输出目录存在"""
        output_dir = settings.get_output_path(task_id)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    @staticmethod
    def ensure_temp_directory(task_id: str) -> Path:
        """确保临时目录存在"""
        temp_dir = settings.get_temp_path(task_id)
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir

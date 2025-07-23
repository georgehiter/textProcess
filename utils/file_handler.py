import os
import uuid
import shutil
import threading
from pathlib import Path
from typing import Optional, Set
from fastapi import UploadFile


class FileHandler:
    """文件处理单例类 - 解决重复实例化问题"""

    # 单例模式实现
    _instance: Optional["FileHandler"] = None
    _lock = threading.Lock()
    _initialized: bool = False

    def __new__(cls, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, **kwargs):
        if not self._initialized:
            # 设置默认值
            self.max_file_size = 100 * 1024 * 1024
            self.allowed_extensions: Set[str] = {".pdf"}
            self.upload_folder = Path("uploads")
            self.output_folder = Path("outputs")

            # 从环境变量加载配置
            self._load_from_env()

            # 确保目录存在
            self.upload_folder.mkdir(parents=True, exist_ok=True)
            self.output_folder.mkdir(parents=True, exist_ok=True)

            self._initialized = True

        # 总是应用传入的配置参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def _load_from_env(self):
        """从环境变量加载配置"""
        # 设置默认值
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", 100 * 1024 * 1024))
        self.upload_folder = Path(os.getenv("UPLOAD_DIR", "uploads"))
        self.output_folder = Path(os.getenv("OUTPUT_DIR", "outputs"))

        # 处理允许的文件扩展名
        allowed_ext_str = os.getenv("ALLOWED_EXTENSIONS", ".pdf")
        self.allowed_extensions = set(allowed_ext_str.split(","))

    def generate_task_id(self) -> str:
        """生成任务ID"""
        return str(uuid.uuid4())

    def validate_file(self, filename: str, size: Optional[int]) -> None:
        """验证上传文件"""
        if not filename or Path(filename).suffix.lower() not in self.allowed_extensions:
            raise ValueError(
                f"不支持的文件格式，仅支持: " f"{', '.join(self.allowed_extensions)}"
            )

        if size and size > self.max_file_size:
            max_mb = self.max_file_size // (1024 * 1024)
            raise ValueError(f"文件大小超过限制，最大支持{max_mb}MB")

    async def save_upload_file(self, file: UploadFile, task_id: str) -> Path:
        """保存上传文件"""
        self.validate_file(file.filename, file.size)

        file_path = self.upload_folder / f"{task_id}_{file.filename}"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 使用异步方式保存文件
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        return file_path

    def ensure_output_directory(self, task_id: str) -> Path:
        """确保输出目录存在"""
        output_dir = self.output_folder / task_id
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def get_upload_file_path(self, task_id: str, filename: str) -> Path:
        """获取上传文件路径"""
        return self.upload_folder / f"{task_id}_{filename}"

    def get_output_directory(self, task_id: str) -> Path:
        """获取输出目录路径"""
        return self.output_folder / task_id

    def cleanup_task_files(self, task_id: str) -> None:
        """清理任务相关文件"""
        # 清理上传文件
        upload_pattern = f"{task_id}_*"
        for file_path in self.upload_folder.glob(upload_pattern):
            try:
                file_path.unlink()
            except Exception as e:
                print(f"清理上传文件失败: {file_path}, 错误: {e}")

        # 清理输出目录
        output_dir = self.output_folder / task_id
        if output_dir.exists():
            try:
                shutil.rmtree(output_dir)
            except Exception as e:
                print(f"清理输出目录失败: {output_dir}, 错误: {e}")

    def get_file_info(self, task_id: str) -> dict:
        """获取任务文件信息"""
        upload_files = list(self.upload_folder.glob(f"{task_id}_*"))
        output_dir = self.output_folder / task_id

        return {
            "task_id": task_id,
            "upload_files": [str(f) for f in upload_files],
            "output_directory": str(output_dir),
            "output_exists": output_dir.exists(),
            "output_files": (list(output_dir.glob("*")) if output_dir.exists() else []),
        }


def get_file_handler(**kwargs) -> FileHandler:
    """获取 FileHandler 单例实例的便捷函数"""
    return FileHandler(**kwargs)


# 全局实例，用于向后兼容
file_handler = FileHandler()

import os
from typing import Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    """应用程序全局设置"""

    # 基础配置
    APP_NAME: str = "PDF转Markdown工具"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    WORKERS: int = 1

    # CORS配置
    CORS_ORIGINS: list = None

    # 文件上传配置
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: set = None

    # GPU配置 - 使用marker库识别的变量名
    NUM_DEVICES: int = 1  # GPU设备数量
    NUM_WORKERS: int = 4  # GPU工作进程数
    TORCH_DEVICE: str = "cuda"  # PyTorch设备
    CUDA_VISIBLE_DEVICES: str = "0"  # 可见GPU设备

    # 转换配置
    OUTPUT_FORMAT: str = "markdown"
    USE_LLM: bool = False
    FORCE_OCR: bool = False
    STRIP_EXISTING_OCR: bool = True
    SAVE_IMAGES: bool = False
    FORMAT_LINES: bool = False
    DISABLE_IMAGE_EXTRACTION: bool = True

    # 文件路径配置
    UPLOAD_FOLDER: str = "uploads"
    OUTPUT_FOLDER: str = "outputs"

    def __post_init__(self):
        """初始化后处理"""
        if self.CORS_ORIGINS is None:
            self.CORS_ORIGINS = [
                "http://localhost:3000",
                "http://localhost:8001",
                "http://127.0.0.1:8001",
                "http://127.0.0.1:3000",
            ]
        if self.ALLOWED_EXTENSIONS is None:
            self.ALLOWED_EXTENSIONS = {".pdf"}
        self._load_gpu_config()
        self._validate_config()
        self._ensure_directories()

    def _load_gpu_config(self):
        """从环境变量加载GPU配置"""
        # 设备数量
        num_devices = os.getenv("NUM_DEVICES")
        if num_devices is not None:
            self.NUM_DEVICES = int(num_devices)

        # 工作进程数
        num_workers = os.getenv("NUM_WORKERS")
        if num_workers is not None:
            self.NUM_WORKERS = int(num_workers)

        # PyTorch设备
        torch_device = os.getenv("TORCH_DEVICE")
        if torch_device is not None:
            self.TORCH_DEVICE = torch_device

        # CUDA可见设备
        cuda_visible_devices = os.getenv("CUDA_VISIBLE_DEVICES")
        if cuda_visible_devices is not None:
            self.CUDA_VISIBLE_DEVICES = cuda_visible_devices

    def _validate_config(self):
        """验证配置参数"""
        # 验证设备数量
        if self.NUM_DEVICES < 1:
            self.NUM_DEVICES = 1
        elif self.NUM_DEVICES > 8:
            self.NUM_DEVICES = 8

        # 验证工作进程数
        if self.NUM_WORKERS < 1:
            self.NUM_WORKERS = 1
        elif self.NUM_WORKERS > 16:
            self.NUM_WORKERS = 16

    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.UPLOAD_FOLDER,
            self.OUTPUT_FOLDER,
        ]

        for directory in directories:
            Path(directory).mkdir(exist_ok=True)

    @property
    def upload_path(self) -> Path:
        """获取上传目录路径"""
        return Path(self.UPLOAD_FOLDER)

    @property
    def output_path(self) -> Path:
        """获取输出目录路径"""
        return Path(self.OUTPUT_FOLDER)

    def is_valid_file(self, filename: str) -> bool:
        """检查文件是否有效"""
        if not filename:
            return False

        file_ext = Path(filename).suffix.lower()
        return file_ext in self.ALLOWED_EXTENSIONS

    def get_file_path(self, task_id: str, filename: str) -> Path:
        """获取文件完整路径"""
        return self.upload_path / f"{task_id}_{filename}"

    def get_output_path(self, task_id: str) -> Path:
        """获取输出目录路径"""
        return self.output_path / task_id

    def get_temp_path(self, task_id: str) -> Path:
        """获取临时目录路径"""
        return Path(self.OUTPUT_FOLDER) / f"{task_id}_temp"

    def apply_gpu_environment(self):
        """应用GPU环境变量"""
        # 设置marker库识别的环境变量
        os.environ["NUM_DEVICES"] = str(self.NUM_DEVICES)
        os.environ["NUM_WORKERS"] = str(self.NUM_WORKERS)
        os.environ["TORCH_DEVICE"] = self.TORCH_DEVICE
        os.environ["CUDA_VISIBLE_DEVICES"] = self.CUDA_VISIBLE_DEVICES

    def get_gpu_config(self) -> Dict[str, Any]:
        """获取GPU配置字典"""
        return {
            "num_devices": self.NUM_DEVICES,
            "num_workers": self.NUM_WORKERS,
            "torch_device": self.TORCH_DEVICE,
            "cuda_visible_devices": self.CUDA_VISIBLE_DEVICES,
        }

    def get_config_summary(self) -> str:
        """获取配置摘要"""
        return (
            f"GPU设备数={self.NUM_DEVICES}, "
            f"工作进程数={self.NUM_WORKERS}, "
            f"PyTorch设备={self.TORCH_DEVICE}, "
            f"CUDA可见设备={self.CUDA_VISIBLE_DEVICES}"
        )


# 全局设置实例
settings = Settings()

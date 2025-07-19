import os
from pathlib import Path


class Settings:
    """应用配置类"""

    # 基础配置
    APP_NAME: str = "PDF转Markdown工具"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 文件上传配置
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: set = {".pdf"}
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    TEMP_DIR: str = "templates"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    WORKERS: int = 1

    # CORS配置
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
    ]

    # 文件清理配置
    CLEANUP_INTERVAL: int = 3600  # 1小时
    FILE_RETENTION: int = 86400  # 24小时

    # GPU配置
    GPU_ENABLED: bool = True  # 是否启用GPU加速
    GPU_DEVICES: int = 1  # GPU设备数量
    GPU_WORKERS: int = 4  # 每个GPU的工作进程数
    GPU_MEMORY_LIMIT: float = 0.8  # GPU内存使用限制（0.8表示使用80%）

    def __init__(self):
        """初始化配置"""
        self._load_gpu_config()
        self._validate_gpu_config()
        self._ensure_directories()

    def _load_gpu_config(self):
        """从环境变量加载GPU配置"""
        # GPU启用状态
        gpu_enabled = os.getenv("MARKER_GPU_ENABLED")
        if gpu_enabled is not None:
            self.GPU_ENABLED = gpu_enabled.lower() in ("true", "1", "yes", "on")

        # GPU设备数量
        gpu_devices = os.getenv("MARKER_GPU_DEVICES")
        if gpu_devices is not None:
            try:
                self.GPU_DEVICES = int(gpu_devices)
            except ValueError:
                pass

        # GPU工作进程数
        gpu_workers = os.getenv("MARKER_GPU_WORKERS")
        if gpu_workers is not None:
            try:
                self.GPU_WORKERS = int(gpu_workers)
            except ValueError:
                pass

        # GPU内存限制
        gpu_memory_limit = os.getenv("MARKER_GPU_MEMORY_LIMIT")
        if gpu_memory_limit is not None:
            try:
                self.GPU_MEMORY_LIMIT = float(gpu_memory_limit)
            except ValueError:
                pass

    def _validate_gpu_config(self):
        """验证GPU配置的有效性"""
        # 验证GPU设备数量
        if self.GPU_DEVICES < 1:
            self.GPU_DEVICES = 1
            print("⚠️  GPU设备数量不能小于1，已设置为1")

        # 验证GPU工作进程数
        if self.GPU_WORKERS < 1:
            self.GPU_WORKERS = 1
            print("⚠️  GPU工作进程数不能小于1，已设置为1")
        elif self.GPU_WORKERS > 16:
            self.GPU_WORKERS = 16
            print("⚠️  GPU工作进程数不能大于16，已设置为16")

        # 验证GPU内存限制
        if self.GPU_MEMORY_LIMIT < 0.1:
            self.GPU_MEMORY_LIMIT = 0.1
            print("⚠️  GPU内存限制不能小于0.1，已设置为0.1")
        elif self.GPU_MEMORY_LIMIT > 1.0:
            self.GPU_MEMORY_LIMIT = 1.0
            print("⚠️  GPU内存限制不能大于1.0，已设置为1.0")

    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.UPLOAD_DIR,
            self.OUTPUT_DIR,
            self.TEMP_DIR,
        ]

        for directory in directories:
            Path(directory).mkdir(exist_ok=True)

    @property
    def upload_path(self) -> Path:
        """获取上传目录路径"""
        return Path(self.UPLOAD_DIR)

    @property
    def output_path(self) -> Path:
        """获取输出目录路径"""
        return Path(self.OUTPUT_DIR)

    @property
    def temp_path(self) -> Path:
        """获取临时目录路径"""
        return Path(self.TEMP_DIR)

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
        return self.temp_path / task_id

    def get_gpu_config(self) -> dict:
        """获取GPU配置字典"""
        return {
            "enabled": self.GPU_ENABLED,
            "devices": self.GPU_DEVICES,
            "workers": self.GPU_WORKERS,
            "memory_limit": self.GPU_MEMORY_LIMIT,
        }

    def apply_gpu_environment(self):
        """应用GPU配置到环境变量"""
        if self.GPU_ENABLED:
            os.environ["NUM_DEVICES"] = str(self.GPU_DEVICES)
            os.environ["NUM_WORKERS"] = str(self.GPU_WORKERS)
            print(
                f"✅ GPU配置已应用: 设备={self.GPU_DEVICES}, 工作进程={self.GPU_WORKERS}"
            )
        else:
            # 禁用GPU时清除相关环境变量
            os.environ.pop("NUM_DEVICES", None)
            os.environ.pop("NUM_WORKERS", None)
            print("⚠️  GPU加速已禁用")


# 全局配置实例
settings = Settings()

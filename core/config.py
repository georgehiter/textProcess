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

    def __init__(self):
        """初始化配置"""
        self._ensure_directories()

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


# 全局配置实例
settings = Settings()

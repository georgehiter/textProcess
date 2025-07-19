from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class OutputFormat(str, Enum):
    """输出格式枚举"""

    markdown = "markdown"
    json = "json"
    html = "html"
    chunks = "chunks"


class ConversionConfig(BaseModel):
    """转换配置模型"""

    output_format: OutputFormat = Field(
        default=OutputFormat.markdown, description="输出格式"
    )
    use_llm: bool = Field(default=False, description="是否使用LLM提升准确性")
    force_ocr: bool = Field(default=False, description="是否强制使用OCR")
    save_images: bool = Field(default=True, description="是否保存提取的图片")
    format_lines: bool = Field(default=True, description="是否重新格式化行")
    disable_image_extraction: bool = Field(
        default=False, description="是否禁用图片提取"
    )


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""

    success: bool
    task_id: Optional[str] = None
    filename: Optional[str] = None
    file_size: Optional[int] = None
    message: Optional[str] = None


class ConversionRequest(BaseModel):
    """转换请求模型"""

    task_id: str
    config: ConversionConfig


class ConversionResponse(BaseModel):
    """转换响应模型"""

    success: bool
    task_id: Optional[str] = None
    message: Optional[str] = None


class ProgressData(BaseModel):
    """进度数据模型"""

    task_id: str
    status: str  # "uploading", "processing", "completed", "failed"
    progress: float = 0.0  # 0-100
    current_stage: Optional[str] = None
    stage_progress: float = 0.0
    stage_current: int = 0
    stage_total: int = 0
    elapsed_time: Optional[str] = None
    estimated_time: Optional[str] = None
    processing_rate: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class ConversionResult(BaseModel):
    """转换结果模型"""

    task_id: str
    success: bool
    output_file: Optional[str] = None
    metadata_file: Optional[str] = None
    image_paths: List[str] = []
    processing_time: Optional[float] = None
    output_format: Optional[str] = None
    text_preview: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """健康检查响应模型"""

    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"

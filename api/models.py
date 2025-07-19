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


class GPUConfig(BaseModel):
    """GPU配置模型"""

    enabled: bool = Field(default=True, description="是否启用GPU加速")
    devices: int = Field(default=1, ge=1, le=8, description="GPU设备数量")
    workers: int = Field(default=4, ge=1, le=16, description="每个GPU的工作进程数")
    memory_limit: float = Field(
        default=0.8, ge=0.1, le=1.0, description="GPU内存使用限制(0.1-1.0)"
    )


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
    gpu_config: GPUConfig = Field(default_factory=GPUConfig, description="GPU加速配置")


class GPUStatus(BaseModel):
    """GPU状态模型"""

    available: bool = Field(description="GPU是否可用")
    device_count: int = Field(description="GPU设备数量")
    device_name: Optional[str] = Field(description="GPU设备名称")
    memory_total: Optional[float] = Field(description="GPU总内存(GB)")
    memory_used: Optional[float] = Field(description="GPU已用内存(GB)")
    memory_free: Optional[float] = Field(description="GPU可用内存(GB)")
    cuda_version: Optional[str] = Field(description="CUDA版本")
    pytorch_version: Optional[str] = Field(description="PyTorch版本")
    current_config: GPUConfig = Field(description="当前GPU配置")


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

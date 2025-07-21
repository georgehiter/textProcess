from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class OutputFormat(str, Enum):
    """输出格式枚举"""

    markdown = "markdown"
    json = "json"
    html = "html"
    chunks = "chunks"


class GPUConfig(BaseModel):
    """GPU配置模型 - 使用marker库识别的变量名"""

    enabled: bool = Field(default=True, description="是否启用GPU加速")
    num_devices: int = Field(default=1, ge=1, le=8, description="GPU设备数量")
    num_workers: int = Field(default=4, ge=1, le=16, description="GPU工作进程数")
    torch_device: str = Field(default="cuda", description="PyTorch设备")
    cuda_visible_devices: str = Field(default="0", description="可见GPU设备")


class ConversionConfig(BaseModel):
    """转换配置模型 - 扩展版"""

    # 转换方式选择
    conversion_mode: str = Field(
        default="marker", description="转换方式: marker(文本PDF) 或 ocr(扫描PDF)"
    )

    # 现有Marker配置字段保持不变
    output_format: OutputFormat = Field(
        default=OutputFormat.markdown, description="输出格式"
    )
    use_llm: bool = Field(default=False, description="是否使用LLM增强")
    force_ocr: bool = Field(default=False, description="是否强制OCR")
    strip_existing_ocr: bool = Field(default=True, description="是否去除已有OCR文本")
    save_images: bool = Field(default=False, description="是否保存图片")
    format_lines: bool = Field(default=False, description="是否格式化行")
    disable_image_extraction: bool = Field(default=True, description="是否禁用图片提取")
    gpu_config: GPUConfig = Field(default_factory=GPUConfig, description="GPU配置")

    # 新增OCR配置字段
    enhance_quality: bool = Field(default=True, description="是否增强图像质量")
    language_detection: bool = Field(default=True, description="是否启用语言检测")
    document_type_detection: bool = Field(
        default=True, description="是否启用文档类型检测"
    )


class ConversionRequest(BaseModel):
    """转换请求模型"""

    task_id: str = Field(description="任务ID")
    config: ConversionConfig = Field(
        default_factory=ConversionConfig, description="转换配置"
    )


class ConversionResponse(BaseModel):
    """转换响应模型"""

    success: bool = Field(description="是否成功")
    task_id: Optional[str] = Field(default=None, description="任务ID")
    message: Optional[str] = Field(default=None, description="响应消息")


class TaskStatus(BaseModel):
    """任务状态模型"""

    task_id: str = Field(description="任务ID")
    status: str = Field(description="任务状态")
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="进度百分比")
    message: str = Field(description="状态消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class GPUStatus(BaseModel):
    """GPU状态模型"""

    available: bool = Field(description="GPU是否可用")
    device_count: int = Field(default=0, description="GPU设备数量")
    device_name: Optional[str] = Field(default=None, description="GPU设备名称")
    memory_total: Optional[float] = Field(default=None, description="GPU总内存(GB)")
    memory_used: Optional[float] = Field(default=None, description="GPU已用内存(GB)")
    memory_free: Optional[float] = Field(default=None, description="GPU可用内存(GB)")
    cuda_version: Optional[str] = Field(default=None, description="CUDA版本")
    pytorch_version: Optional[str] = Field(default=None, description="PyTorch版本")
    current_config: Optional[GPUConfig] = Field(default=None, description="当前GPU配置")


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""

    success: bool = Field(description="是否成功")
    task_id: Optional[str] = Field(default=None, description="任务ID")
    filename: Optional[str] = Field(default=None, description="文件名")
    file_size: Optional[int] = Field(default=None, description="文件大小")
    message: Optional[str] = Field(default=None, description="响应消息")


class ProgressData(BaseModel):
    """进度数据模型"""

    task_id: str = Field(description="任务ID")
    status: str = Field(description="任务状态")
    progress: float = Field(default=0.0, description="进度百分比")
    error: Optional[str] = Field(default=None, description="错误信息")


class ConversionResult(BaseModel):
    """转换结果模型"""

    task_id: str = Field(description="任务ID")
    success: bool = Field(description="是否成功")
    output_file: Optional[str] = Field(default=None, description="输出文件路径")
    metadata_file: Optional[str] = Field(default=None, description="元数据文件路径")
    image_paths: list = Field(default_factory=list, description="图片路径列表")
    processing_time: Optional[float] = Field(default=None, description="处理时间")
    output_format: Optional[str] = Field(default=None, description="输出格式")
    text_preview: Optional[str] = Field(default=None, description="文本预览")
    error: Optional[str] = Field(default=None, description="错误信息")


class HealthResponse(BaseModel):
    """健康检查响应模型"""

    status: str = Field(default="healthy", description="服务状态")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    version: str = Field(default="1.0.0", description="版本号")


class ErrorResponse(BaseModel):
    """错误响应模型"""

    error: str = Field(description="错误信息")
    details: Optional[str] = Field(default=None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")

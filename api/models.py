from typing import Union, Literal, List
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


class OutputFormat(str, Enum):
    """输出格式枚举"""

    markdown = "markdown"
    json = "json"
    html = "html"
    chunks = "chunks"


class MarkerGPUConfig(BaseModel):
    """Marker专用GPU配置"""

    enabled: bool = Field(default=False, description="是否启用GPU加速")
    num_devices: int = Field(default=1, ge=1, le=8, description="GPU设备数量")
    num_workers: int = Field(default=4, ge=1, le=16, description="GPU工作进程数")
    torch_device: str = Field(default="cuda", description="PyTorch设备")
    cuda_visible_devices: str = Field(default="0", description="可见GPU设备")

    @field_validator("enabled")
    @classmethod
    def validate_gpu_enabled(cls, v, info):
        """验证GPU配置"""
        if v:
            # 如果启用GPU，检查其他配置
            if info.data.get("num_devices", 1) > 1:
                print("⚠️ 多GPU配置可能需要更多内存")
        return v


class BaseConversionConfig(BaseModel):
    """基础转换配置"""

    output_format: OutputFormat = Field(
        default=OutputFormat.markdown, description="输出格式"
    )


class MarkerConfig(BaseConversionConfig):
    """Marker转换配置 - 适用于文本版PDF，包含GPU加速"""

    conversion_mode: Literal["marker"] = "marker"

    # Marker特有配置
    use_llm: bool = Field(default=False, description="是否使用LLM增强准确性")
    force_ocr: bool = Field(default=False, description="是否强制使用OCR（通常不推荐）")
    strip_existing_ocr: bool = Field(
        default=True, description="是否去除已有OCR文本以提升速度"
    )
    save_images: bool = Field(default=False, description="是否保存提取的图片")
    format_lines: bool = Field(default=False, description="是否重新格式化行")
    disable_image_extraction: bool = Field(
        default=True, description="是否禁用图片提取以提升速度"
    )

    # GPU配置 - 仅Marker模式需要
    gpu: MarkerGPUConfig = Field(
        default_factory=MarkerGPUConfig, description="GPU加速配置（Marker模式专用）"
    )

    @model_validator(mode="after")
    def validate_marker_config(self):
        """Marker配置验证"""
        # 检查配置冲突
        if self.force_ocr:
            print("⚠️ 警告: Marker模式下启用force_ocr可能不是最佳选择")

        return self


class OCRConfig(BaseConversionConfig):
    """OCR转换配置 - 适用于扫描版PDF，无需GPU"""

    conversion_mode: Literal["ocr"] = "ocr"

    # OCR特有配置
    enhance_quality: bool = Field(default=True, description="是否增强图像质量")
    language_detection: bool = Field(default=True, description="是否启用智能语言检测")
    document_type_detection: bool = Field(
        default=True, description="是否启用文档类型检测"
    )

    # OCR质量配置
    ocr_quality: Literal["fast", "balanced", "accurate"] = Field(
        default="balanced",
        description="OCR质量模式：fast(快速), balanced(平衡), accurate(准确)",
    )

    # 语言配置
    target_languages: List[str] = Field(
        default=["chi_sim", "eng"], description="目标识别语言列表"
    )

    @field_validator("target_languages")
    @classmethod
    def validate_languages(cls, v):
        """验证语言配置"""
        valid_languages = ["chi_sim", "eng", "jpn", "kor"]
        for lang in v:
            if lang not in valid_languages:
                raise ValueError(f"不支持的语言: {lang}")
        return v


class ConversionRequest(BaseModel):
    """转换请求模型"""

    task_id: str = Field(description="任务ID")
    config: Union[MarkerConfig, OCRConfig] = Field(
        discriminator="conversion_mode", description="转换配置"
    )

    @field_validator("task_id")
    @classmethod
    def validate_task_id(cls, v):
        """验证任务ID格式"""
        if not v or len(v) < 10:
            raise ValueError("任务ID格式无效")
        return v


# 配置预设响应模型
class ConfigPreset(BaseModel):
    """配置预设模型"""

    name: str = Field(description="预设名称")
    description: str = Field(description="预设描述")
    config: Union[MarkerConfig, OCRConfig] = Field(description="配置内容")


class ConfigPresetsResponse(BaseModel):
    """配置预设响应"""

    presets: List[ConfigPreset] = Field(description="预设配置列表")


# 配置验证响应模型
class ConfigValidationResponse(BaseModel):
    """配置验证响应"""

    valid: bool = Field(description="配置是否有效")
    errors: List[str] = Field(default_factory=list, description="错误信息")
    warnings: List[str] = Field(default_factory=list, description="警告信息")
    suggestions: List[str] = Field(default_factory=list, description="建议信息")


class ConversionResponse(BaseModel):
    """转换响应模型"""

    success: bool = Field(description="是否成功")
    task_id: str = Field(description="任务ID")
    message: str = Field(description="响应消息")

"""配置服务模块"""

from typing import Union, Dict, Optional
from api.models import MarkerConfig, OCRConfig

# 类型别名
ConfigType = Union[MarkerConfig, OCRConfig]


class ConfigService:
    """配置服务类，提供配置预设管理和创建功能"""

    @staticmethod
    def get_all_presets() -> Dict[str, ConfigType]:
        """获取所有可用的配置预设

        Returns:
            Dict[str, ConfigType]: 预设名称到配置对象的映射
        """
        return {
            "text_pdf": ConfigService.create_text_pdf_config(),
            "scan_pdf": ConfigService.create_scan_pdf_config(),
        }

    @staticmethod
    def get_preset_by_name(name: str) -> Optional[ConfigType]:
        """根据名称获取特定的配置预设

        Args:
            name (str): 预设名称

        Returns:
            Optional[ConfigType]: 配置对象，如果不存在则返回None
        """
        presets = ConfigService.get_all_presets()
        return presets.get(name)

    @staticmethod
    def create_text_pdf_config() -> MarkerConfig:
        """创建文本型PDF配置（可自定义）

        Returns:
            MarkerConfig: 文本型PDF的默认配置
        """
        from api.models import GPUConfig

        return MarkerConfig(
            output_format="markdown",
            use_llm=False,
            force_ocr=False,
            strip_existing_ocr=True,
            save_images=False,
            format_lines=False,
            disable_image_extraction=True,
            gpu_config=GPUConfig(enabled=False),
        )

    @staticmethod
    def create_scan_pdf_config() -> OCRConfig:
        """创建扫描型PDF配置（固定参数）

        Returns:
            OCRConfig: 扫描型PDF的默认配置
        """
        return OCRConfig(
            output_format="markdown",
            enhance_quality=True,
            save_images=True,
            format_lines=True,
            gpu_enabled=False,
        )

    @staticmethod
    def validate_config(config: ConfigType) -> bool:
        """验证配置对象的有效性

        Args:
            config (ConfigType): 要验证的配置对象

        Returns:
            bool: 配置是否有效
        """
        if isinstance(config, MarkerConfig):
            # 验证MarkerConfig的必要字段
            return (
                config.output_format in ["markdown", "txt", "html"]
                and isinstance(config.use_llm, bool)
                and isinstance(config.force_ocr, bool)
            )
        elif isinstance(config, OCRConfig):
            # 验证OCRConfig的必要字段
            return (
                config.output_format in ["markdown", "txt", "html"]
                and isinstance(config.enhance_quality, bool)
                and isinstance(config.save_images, bool)
            )
        else:
            return False

    @staticmethod
    def get_preset_configs() -> Dict[str, ConfigType]:
        """获取预设配置列表（保持向后兼容）

        Returns:
            Dict[str, ConfigType]: 预设名称到配置对象的映射
        """
        return ConfigService.get_all_presets()

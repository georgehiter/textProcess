from typing import Union, Dict, Any
from api.models import MarkerConfig, OCRConfig, MarkerGPUConfig

# 类型别名
ConfigType = Union[MarkerConfig, OCRConfig]


class ConfigFactory:
    """配置工厂类"""

    @staticmethod
    def create_marker_config(**kwargs) -> MarkerConfig:
        """创建Marker配置"""
        return MarkerConfig(**kwargs)

    @staticmethod
    def create_ocr_config(**kwargs) -> OCRConfig:
        """创建OCR配置"""
        return OCRConfig(**kwargs)

    @staticmethod
    def create_default_config(conversion_mode: str) -> ConfigType:
        """创建默认配置"""
        if conversion_mode == "marker":
            return ConfigFactory.create_marker_config()
        elif conversion_mode == "ocr":
            return ConfigFactory.create_ocr_config()
        else:
            raise ValueError(f"不支持的转换模式: {conversion_mode}")

    @staticmethod
    def create_text_pdf_config() -> MarkerConfig:
        """创建文本型PDF配置（可自定义）"""
        return MarkerConfig(
            output_format="markdown",
            use_llm=False,
            force_ocr=False,
            strip_existing_ocr=True,
            save_images=False,
            format_lines=False,
            disable_image_extraction=True,
            gpu=MarkerGPUConfig(enabled=False),
        )

    @staticmethod
    def create_scan_pdf_config() -> OCRConfig:
        """创建扫描型PDF配置（固定参数）"""
        return OCRConfig(
            output_format="markdown",
            enhance_quality=True,
            language_detection=True,
            document_type_detection=True,
            ocr_quality="balanced",
            target_languages=["chi_sim", "eng"],
        )

    @staticmethod
    def create_fast_marker_config() -> MarkerConfig:
        """创建快速Marker配置"""
        return MarkerConfig(
            disable_image_extraction=True,
            save_images=False,
            format_lines=False,
            gpu=MarkerGPUConfig(enabled=False),
        )

    @staticmethod
    def create_gpu_marker_config() -> MarkerConfig:
        """创建GPU加速Marker配置"""
        return MarkerConfig(
            gpu=MarkerGPUConfig(enabled=True, num_devices=1, num_workers=4)
        )

    @staticmethod
    def create_accurate_ocr_config() -> OCRConfig:
        """创建高精度OCR配置"""
        return OCRConfig(
            enhance_quality=True,
            language_detection=True,
            document_type_detection=True,
            ocr_quality="accurate",
        )

    @staticmethod
    def create_fast_ocr_config() -> OCRConfig:
        """创建快速OCR配置"""
        return OCRConfig(
            enhance_quality=False,
            language_detection=False,
            document_type_detection=False,
            ocr_quality="fast",
        )

    @staticmethod
    def get_preset_configs():
        """获取所有预设配置"""
        from api.models import ConfigPreset

        presets = []
        preset_configs = ConfigPresets.get_preset_configs()

        for key, preset_data in preset_configs.items():
            preset = ConfigPreset(
                name=preset_data["name"],
                description=preset_data["description"],
                config=preset_data["config"],
            )
            presets.append(preset)

        return presets

    @staticmethod
    def get_preset_by_name(name: str) -> ConfigType:
        """根据名称获取预设配置"""
        presets = ConfigPresets.get_preset_configs()
        for preset_data in presets.values():
            if preset_data["name"] == name:
                return preset_data["config"]
        raise ValueError(f"不存在的预设配置: {name}")


class ConfigPresets:
    """配置预设"""

    @staticmethod
    def get_preset_configs() -> Dict[str, Dict[str, Any]]:
        """获取所有预设配置"""
        return {
            "text_pdf": {
                "name": "文本型PDF转换",
                "description": "适用于包含可复制文本的PDF文档，支持自定义参数",
                "config": ConfigFactory.create_text_pdf_config(),
            },
            "scan_pdf": {
                "name": "扫描型PDF转换",
                "description": "适用于扫描版、图片版PDF文档，自动OCR识别",
                "config": ConfigFactory.create_scan_pdf_config(),
            },
        }

    @staticmethod
    def get_preset_by_name(name: str) -> ConfigType:
        """根据名称获取预设配置"""
        presets = ConfigPresets.get_preset_configs()
        if name not in presets:
            raise ValueError(f"不存在的预设配置: {name}")
        return presets[name]["config"]

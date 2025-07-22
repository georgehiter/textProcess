from typing import Union, Dict, Any
from api.new_models import MarkerConfig, OCRConfig, MarkerGPUConfig


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
    def create_default_config(conversion_mode: str) -> Union[MarkerConfig, OCRConfig]:
        """创建默认配置"""
        if conversion_mode == "marker":
            return ConfigFactory.create_marker_config()
        elif conversion_mode == "ocr":
            return ConfigFactory.create_ocr_config()
        else:
            raise ValueError(f"不支持的转换模式: {conversion_mode}")

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
        from api.new_models import ConfigPreset

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
    def get_preset_by_name(name: str) -> Union[MarkerConfig, OCRConfig]:
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
            "fast_marker": {
                "name": "快速Marker转换",
                "description": "适用于文本版PDF的快速转换，禁用GPU和图片提取",
                "config": ConfigFactory.create_fast_marker_config(),
            },
            "gpu_marker": {
                "name": "GPU加速Marker转换",
                "description": "适用于文本版PDF的GPU加速转换",
                "config": ConfigFactory.create_gpu_marker_config(),
            },
            "accurate_ocr": {
                "name": "高精度OCR转换",
                "description": "适用于扫描版PDF的高精度转换，启用所有优化",
                "config": ConfigFactory.create_accurate_ocr_config(),
            },
            "fast_ocr": {
                "name": "快速OCR转换",
                "description": "适用于扫描版PDF的快速转换，禁用优化功能",
                "config": ConfigFactory.create_fast_ocr_config(),
            },
        }

    @staticmethod
    def get_preset_by_name(name: str) -> Union[MarkerConfig, OCRConfig]:
        """根据名称获取预设配置"""
        presets = ConfigPresets.get_preset_configs()
        if name not in presets:
            raise ValueError(f"不存在的预设配置: {name}")
        return presets[name]["config"]

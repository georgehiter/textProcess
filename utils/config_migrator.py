from typing import Dict, Any, Union
from api.new_models import MarkerConfig, OCRConfig


class ConfigMigrator:
    """配置迁移工具"""

    @staticmethod
    def old_to_new_config(old_config: Dict[str, Any]) -> Dict[str, Any]:
        """将旧配置转换为新配置格式"""
        conversion_mode = old_config.get("conversion_mode", "marker")

        if conversion_mode == "marker":
            return ConfigMigrator._convert_to_marker_config_dict(old_config)
        elif conversion_mode == "ocr":
            return ConfigMigrator._convert_to_ocr_config_dict(old_config)
        else:
            raise ValueError(f"不支持的转换模式: {conversion_mode}")

    @staticmethod
    def _convert_to_marker_config_dict(old_config: Dict[str, Any]) -> Dict[str, Any]:
        """转换为Marker配置字典"""
        # 提取GPU配置
        gpu_config = old_config.get("gpu_config", {})

        return {
            "conversion_mode": "marker",
            "output_format": old_config.get("output_format", "markdown"),
            "use_llm": old_config.get("use_llm", False),
            "force_ocr": old_config.get("force_ocr", False),
            "strip_existing_ocr": old_config.get("strip_existing_ocr", True),
            "save_images": old_config.get("save_images", False),
            "format_lines": old_config.get("format_lines", False),
            "disable_image_extraction": old_config.get(
                "disable_image_extraction", True
            ),
            "gpu": {
                "enabled": gpu_config.get("enabled", False),
                "num_devices": gpu_config.get("num_devices", 1),
                "num_workers": gpu_config.get("num_workers", 4),
                "torch_device": gpu_config.get("torch_device", "cuda"),
                "cuda_visible_devices": gpu_config.get("cuda_visible_devices", "0"),
            },
        }

    @staticmethod
    def _convert_to_ocr_config_dict(old_config: Dict[str, Any]) -> Dict[str, Any]:
        """转换为OCR配置字典"""
        return {
            "conversion_mode": "ocr",
            "output_format": old_config.get("output_format", "markdown"),
            "enhance_quality": old_config.get("enhance_quality", True),
            "language_detection": old_config.get("language_detection", True),
            "document_type_detection": old_config.get("document_type_detection", True),
            "ocr_quality": old_config.get("ocr_quality", "balanced"),
            "target_languages": old_config.get("target_languages", ["chi_sim", "eng"]),
        }

    @staticmethod
    def _convert_to_marker_config(old_config: Dict[str, Any]) -> MarkerConfig:
        """转换为Marker配置"""
        # 提取GPU配置
        gpu_config = old_config.get("gpu_config", {})

        return MarkerConfig(
            output_format=old_config.get("output_format", "markdown"),
            use_llm=old_config.get("use_llm", False),
            force_ocr=old_config.get("force_ocr", False),
            strip_existing_ocr=old_config.get("strip_existing_ocr", True),
            save_images=old_config.get("save_images", False),
            format_lines=old_config.get("format_lines", False),
            disable_image_extraction=old_config.get("disable_image_extraction", True),
            gpu={
                "enabled": gpu_config.get("enabled", False),
                "num_devices": gpu_config.get("num_devices", 1),
                "num_workers": gpu_config.get("num_workers", 4),
                "torch_device": gpu_config.get("torch_device", "cuda"),
                "cuda_visible_devices": gpu_config.get("cuda_visible_devices", "0"),
            },
        )

    @staticmethod
    def _convert_to_ocr_config(old_config: Dict[str, Any]) -> OCRConfig:
        """转换为OCR配置"""
        return OCRConfig(
            output_format=old_config.get("output_format", "markdown"),
            enhance_quality=old_config.get("enhance_quality", True),
            language_detection=old_config.get("language_detection", True),
            document_type_detection=old_config.get("document_type_detection", True),
            ocr_quality=old_config.get("ocr_quality", "balanced"),
            target_languages=old_config.get("target_languages", ["chi_sim", "eng"]),
        )

    @staticmethod
    def new_to_old_config(new_config: Dict[str, Any]) -> Dict[str, Any]:
        """将新配置转换为旧配置格式（用于兼容性）"""
        conversion_mode = new_config.get("conversion_mode", "marker")

        if conversion_mode == "marker":
            return ConfigMigrator._marker_dict_to_old_config(new_config)
        elif conversion_mode == "ocr":
            return ConfigMigrator._ocr_dict_to_old_config(new_config)
        else:
            raise ValueError("不支持的配置类型")

    @staticmethod
    def _marker_dict_to_old_config(marker_config: Dict[str, Any]) -> Dict[str, Any]:
        """Marker配置字典转换为旧格式"""
        return {
            "conversion_mode": "marker",
            "output_format": marker_config.get("output_format", "markdown"),
            "use_llm": marker_config.get("use_llm", False),
            "force_ocr": marker_config.get("force_ocr", False),
            "strip_existing_ocr": marker_config.get("strip_existing_ocr", True),
            "save_images": marker_config.get("save_images", False),
            "format_lines": marker_config.get("format_lines", False),
            "disable_image_extraction": marker_config.get(
                "disable_image_extraction", True
            ),
            "gpu_config": marker_config.get(
                "gpu",
                {
                    "enabled": False,
                    "num_devices": 1,
                    "num_workers": 4,
                    "torch_device": "cuda",
                    "cuda_visible_devices": "0",
                },
            ),
        }

    @staticmethod
    def _ocr_dict_to_old_config(ocr_config: Dict[str, Any]) -> Dict[str, Any]:
        """OCR配置字典转换为旧格式"""
        return {
            "conversion_mode": "ocr",
            "output_format": ocr_config.get("output_format", "markdown"),
            "enhance_quality": ocr_config.get("enhance_quality", True),
            "language_detection": ocr_config.get("language_detection", True),
            "document_type_detection": ocr_config.get("document_type_detection", True),
            "ocr_quality": ocr_config.get("ocr_quality", "balanced"),
            "target_languages": ocr_config.get("target_languages", ["chi_sim", "eng"]),
        }

    @staticmethod
    def _marker_to_old_config(marker_config: MarkerConfig) -> Dict[str, Any]:
        """Marker配置转换为旧格式"""
        return {
            "conversion_mode": "marker",
            "output_format": marker_config.output_format,
            "use_llm": marker_config.use_llm,
            "force_ocr": marker_config.force_ocr,
            "strip_existing_ocr": marker_config.strip_existing_ocr,
            "save_images": marker_config.save_images,
            "format_lines": marker_config.format_lines,
            "disable_image_extraction": marker_config.disable_image_extraction,
            "gpu_config": {
                "enabled": marker_config.gpu.enabled,
                "num_devices": marker_config.gpu.num_devices,
                "num_workers": marker_config.gpu.num_workers,
                "torch_device": marker_config.gpu.torch_device,
                "cuda_visible_devices": marker_config.gpu.cuda_visible_devices,
            },
        }

    @staticmethod
    def _ocr_to_old_config(ocr_config: OCRConfig) -> Dict[str, Any]:
        """OCR配置转换为旧格式"""
        return {
            "conversion_mode": "ocr",
            "output_format": ocr_config.output_format,
            "enhance_quality": ocr_config.enhance_quality,
            "language_detection": ocr_config.language_detection,
            "document_type_detection": ocr_config.document_type_detection,
            "ocr_quality": ocr_config.ocr_quality,
            "target_languages": ocr_config.target_languages,
        }

    @staticmethod
    def detect_config_version(config: Dict[str, Any]) -> str:
        """检测配置版本"""
        # 检查是否为新配置格式
        if "conversion_mode" in config:
            if "gpu" in config and isinstance(config["gpu"], dict):
                return "v2"  # 新配置格式
            elif "gpu_config" in config:
                return "v1"  # 旧配置格式

        # 默认认为是旧格式
        return "v1"

    @staticmethod
    def migrate_config(config: Dict[str, Any]) -> Union[MarkerConfig, OCRConfig]:
        """自动迁移配置"""
        version = ConfigMigrator.detect_config_version(config)

        if version == "v2":
            # 已经是新格式，直接创建
            conversion_mode = config.get("conversion_mode", "marker")
            if conversion_mode == "marker":
                return MarkerConfig(**config)
            elif conversion_mode == "ocr":
                return OCRConfig(**config)
            else:
                raise ValueError(f"不支持的转换模式: {conversion_mode}")
        else:
            # 旧格式，需要转换
            return ConfigMigrator.old_to_new_config(config)

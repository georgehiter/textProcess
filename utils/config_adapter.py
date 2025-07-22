from typing import Dict, Any, Union
import os
from api.new_models import MarkerConfig, OCRConfig


class ConfigAdapter:
    """配置适配器 - 处理新旧配置格式的转换"""

    @staticmethod
    def adapt_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        将新配置格式适配为旧格式，用于核心模块处理

        Args:
            config: 新配置字典

        Returns:
            Dict[str, Any]: 适配后的配置字典
        """
        conversion_mode = config.get("conversion_mode", "marker")

        if conversion_mode == "marker":
            return ConfigAdapter._adapt_marker_config_dict(config)
        elif conversion_mode == "ocr":
            return ConfigAdapter._adapt_ocr_config_dict(config)
        else:
            raise ValueError("不支持的配置类型")

    @staticmethod
    def _adapt_marker_config_dict(marker_config: Dict[str, Any]) -> Dict[str, Any]:
        """适配Marker配置字典"""
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
            # GPU配置转换为旧格式
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
    def _adapt_ocr_config_dict(ocr_config: Dict[str, Any]) -> Dict[str, Any]:
        """适配OCR配置字典"""
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
    def _adapt_marker_config(marker_config: MarkerConfig) -> Dict[str, Any]:
        """适配Marker配置"""
        return {
            "output_format": marker_config.output_format,
            "use_llm": marker_config.use_llm,
            "force_ocr": marker_config.force_ocr,
            "strip_existing_ocr": marker_config.strip_existing_ocr,
            "save_images": marker_config.save_images,
            "format_lines": marker_config.format_lines,
            "disable_image_extraction": marker_config.disable_image_extraction,
            # GPU配置转换为旧格式
            "gpu_config": {
                "enabled": marker_config.gpu.enabled,
                "num_devices": marker_config.gpu.num_devices,
                "num_workers": marker_config.gpu.num_workers,
                "torch_device": marker_config.gpu.torch_device,
                "cuda_visible_devices": marker_config.gpu.cuda_visible_devices,
            },
        }

    @staticmethod
    def _adapt_ocr_config(ocr_config: OCRConfig) -> Dict[str, Any]:
        """适配OCR配置"""
        return {
            "output_format": ocr_config.output_format,
            "enhance_quality": ocr_config.enhance_quality,
            "language_detection": ocr_config.language_detection,
            "document_type_detection": ocr_config.document_type_detection,
            "ocr_quality": ocr_config.ocr_quality,
            "target_languages": ocr_config.target_languages,
        }

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """
        验证配置的有效性

        Args:
            config: 配置字典

        Returns:
            bool: 配置是否有效
        """
        try:
            # 检查必要字段
            if "conversion_mode" not in config:
                return False

            # 检查转换模式
            conversion_mode = config.get("conversion_mode", "marker")

            if conversion_mode == "marker":
                # 检查Marker基本字段（允许默认值）
                if "output_format" not in config:
                    return False

                # 检查GPU配置（如果启用）
                gpu_config = config.get("gpu", {})
                if gpu_config.get("enabled", False):
                    gpu_fields = ["num_devices", "num_workers", "torch_device"]
                    for field in gpu_fields:
                        if field not in gpu_config:
                            return False

            elif conversion_mode == "ocr":
                # 检查OCR基本字段（允许默认值）
                if "output_format" not in config:
                    return False

            return True

        except Exception:
            return False

    @staticmethod
    def apply_gpu_config(gpu_config: Dict[str, Any]) -> None:
        """
        应用GPU配置到环境变量

        Args:
            gpu_config: GPU配置字典
        """
        if not gpu_config.get("enabled", False):
            return

        # 设置GPU环境变量
        os.environ["NUM_DEVICES"] = str(gpu_config.get("num_devices", 1))
        os.environ["NUM_WORKERS"] = str(gpu_config.get("num_workers", 4))
        os.environ["TORCH_DEVICE"] = gpu_config.get("torch_device", "cuda")
        os.environ["CUDA_VISIBLE_DEVICES"] = gpu_config.get("cuda_visible_devices", "0")

    @staticmethod
    def get_config_summary(config: Dict[str, Any]) -> str:
        """
        获取配置摘要信息

        Args:
            config: 配置字典

        Returns:
            str: 配置摘要
        """
        try:
            conversion_mode = config.get("conversion_mode", "unknown")

            if conversion_mode == "marker":
                gpu_enabled = config.get("gpu", {}).get("enabled", False)
                gpu_status = "启用" if gpu_enabled else "禁用"
                llm_enabled = config.get("use_llm", False)
                llm_status = "启用" if llm_enabled else "禁用"
                return f"V2 Marker模式 - GPU:{gpu_status}, LLM:{llm_status}"

            elif conversion_mode == "ocr":
                quality = config.get("ocr_quality", "balanced")
                languages = config.get("target_languages", ["chi_sim", "eng"])
                languages_str = ", ".join(languages)
                return f"V2 OCR模式 - 质量:{quality}, 语言:{languages_str}"

            else:
                return f"V2 {conversion_mode}模式"

        except Exception:
            return "配置摘要生成失败"

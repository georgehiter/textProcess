"""
配置兼容性检查工具
确保新旧配置系统的无缝切换
"""

from typing import Dict, Any, List, Tuple, Union
from api.new_models import MarkerConfig, OCRConfig
from utils.config_migrator import ConfigMigrator


class ConfigCompatibilityChecker:
    """配置兼容性检查器"""

    @staticmethod
    def check_config_compatibility(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查配置兼容性并返回兼容性报告

        Args:
            config: 待检查的配置

        Returns:
            兼容性报告
        """
        report = {
            "compatibility": True,
            "version": "unknown",
            "issues": [],
            "warnings": [],
            "suggestions": [],
            "migration_needed": False,
        }

        try:
            # 检测配置版本
            version = ConfigMigrator.detect_config_version(config)
            report["version"] = version

            if version == "v1":
                # 旧配置格式
                report["migration_needed"] = True
                report["suggestions"].append(
                    "建议升级到新的配置格式以获得更好的类型安全"
                )

                # 检查旧配置的完整性
                issues = ConfigCompatibilityChecker._check_v1_completeness(config)
                report["issues"].extend(issues)

                # 检查旧配置的有效性
                warnings = ConfigCompatibilityChecker._check_v1_validity(config)
                report["warnings"].extend(warnings)

            elif version == "v2":
                # 新配置格式
                report["migration_needed"] = False

                # 检查新配置的有效性
                issues = ConfigCompatibilityChecker._check_v2_validity(config)
                report["issues"].extend(issues)

                # 检查新配置的优化建议
                suggestions = ConfigCompatibilityChecker._check_v2_optimization(config)
                report["suggestions"].extend(suggestions)

            # 更新兼容性状态
            report["compatibility"] = len(report["issues"]) == 0

        except Exception as e:
            report["compatibility"] = False
            report["issues"].append(f"配置检查异常: {str(e)}")

        return report

    @staticmethod
    def _check_v1_completeness(config: Dict[str, Any]) -> List[str]:
        """检查V1配置的完整性"""
        issues = []

        # 检查必要字段
        required_fields = ["conversion_mode", "output_format"]
        for field in required_fields:
            if field not in config:
                issues.append(f"缺少必要字段: {field}")

        # 检查转换模式特定字段
        conversion_mode = config.get("conversion_mode", "marker")

        if conversion_mode == "marker":
            marker_fields = [
                "use_llm",
                "force_ocr",
                "strip_existing_ocr",
                "save_images",
                "format_lines",
                "disable_image_extraction",
            ]
            for field in marker_fields:
                if field not in config:
                    issues.append(f"Marker模式缺少字段: {field}")

        elif conversion_mode == "ocr":
            ocr_fields = [
                "enhance_quality",
                "language_detection",
                "document_type_detection",
                "ocr_quality",
                "target_languages",
            ]
            for field in ocr_fields:
                if field not in config:
                    issues.append(f"OCR模式缺少字段: {field}")

        return issues

    @staticmethod
    def _check_v1_validity(config: Dict[str, Any]) -> List[str]:
        """检查V1配置的有效性"""
        warnings = []

        # 检查GPU配置
        gpu_config = config.get("gpu_config", {})
        if gpu_config.get("enabled", False):
            if config.get("conversion_mode") == "ocr":
                warnings.append("OCR模式不需要GPU配置，建议禁用GPU以节省资源")

            # 检查GPU配置的合理性
            num_devices = gpu_config.get("num_devices", 1)
            if num_devices > 4:
                warnings.append("GPU设备数量过多，可能影响性能")

        # 检查配置冲突
        if config.get("force_ocr", False) and config.get("conversion_mode") == "marker":
            warnings.append("Marker模式下启用force_ocr可能不是最佳选择")

        return warnings

    @staticmethod
    def _check_v2_validity(config: Dict[str, Any]) -> List[str]:
        """检查V2配置的有效性"""
        issues = []

        try:
            # 尝试创建配置对象来验证
            conversion_mode = config.get("conversion_mode", "marker")

            if conversion_mode == "marker":
                MarkerConfig(**config)
            elif conversion_mode == "ocr":
                OCRConfig(**config)
            else:
                issues.append(f"不支持的转换模式: {conversion_mode}")

        except Exception as e:
            issues.append(f"配置验证失败: {str(e)}")

        return issues

    @staticmethod
    def _check_v2_optimization(config: Dict[str, Any]) -> List[str]:
        """检查V2配置的优化建议"""
        suggestions = []

        conversion_mode = config.get("conversion_mode", "marker")

        if conversion_mode == "marker":
            # Marker模式优化建议
            if config.get("gpu", {}).get("enabled", False):
                suggestions.append("GPU已启用，确保系统支持CUDA以获得最佳性能")

            if config.get("use_llm", False):
                suggestions.append("LLM已启用，转换时间可能较长但质量更高")

            if not config.get("disable_image_extraction", True):
                suggestions.append("图片提取已启用，可能影响转换速度")

        elif conversion_mode == "ocr":
            # OCR模式优化建议
            ocr_quality = config.get("ocr_quality", "balanced")
            if ocr_quality == "accurate":
                suggestions.append("使用高精度OCR模式，转换时间较长但准确率更高")
            elif ocr_quality == "fast":
                suggestions.append("使用快速OCR模式，转换速度快但准确率可能较低")

            languages = config.get("target_languages", [])
            if len(languages) > 2:
                suggestions.append("目标语言较多，可能影响识别速度")

        return suggestions

    @staticmethod
    def auto_fix_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        自动修复配置中的常见问题

        Args:
            config: 原始配置

        Returns:
            修复后的配置和兼容性信息
        """
        result = {
            "fixed_config": config.copy(),
            "compatibility": True,
            "issues": [],
            "suggestions": [],
        }

        try:
            # 检测配置版本
            version = ConfigMigrator.detect_config_version(config)

            if version == "v1":
                # 修复V1配置
                result["fixed_config"] = ConfigCompatibilityChecker._fix_v1_config(
                    config
                )
                result["suggestions"].append("已从V1格式升级到V2格式")
            elif version == "v2":
                # 修复V2配置
                result["fixed_config"] = ConfigCompatibilityChecker._fix_v2_config(
                    config
                )

        except Exception as e:
            result["compatibility"] = False
            result["issues"].append(f"配置自动修复失败: {str(e)}")

        return result

    @staticmethod
    def _fix_v1_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """修复V1配置"""
        fixed = config.copy()

        # 设置默认值
        conversion_mode = fixed.get("conversion_mode", "marker")

        if conversion_mode == "marker":
            # Marker模式默认值
            defaults = {
                "output_format": "markdown",
                "use_llm": False,
                "force_ocr": False,
                "strip_existing_ocr": True,
                "save_images": False,
                "format_lines": False,
                "disable_image_extraction": True,
                "gpu_config": {
                    "enabled": False,
                    "num_devices": 1,
                    "num_workers": 4,
                    "torch_device": "cuda",
                    "cuda_visible_devices": "0",
                },
            }
        else:
            # OCR模式默认值
            defaults = {
                "output_format": "markdown",
                "enhance_quality": True,
                "language_detection": True,
                "document_type_detection": True,
                "ocr_quality": "balanced",
                "target_languages": ["chi_sim", "eng"],
            }

        # 应用默认值
        for key, value in defaults.items():
            if key not in fixed:
                fixed[key] = value

        return fixed

    @staticmethod
    def _fix_v2_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """修复V2配置"""
        # V2配置通常已经通过Pydantic验证，这里主要处理特殊情况
        fixed = config.copy()

        # 确保conversion_mode存在
        if "conversion_mode" not in fixed:
            fixed["conversion_mode"] = "marker"

        return fixed

    @staticmethod
    def get_config_summary(config: Dict[str, Any]) -> str:
        """
        获取配置摘要

        Args:
            config: 配置字典

        Returns:
            配置摘要字符串
        """
        try:
            version = ConfigMigrator.detect_config_version(config)
            conversion_mode = config.get("conversion_mode", "marker")
            output_format = config.get("output_format", "markdown")

            summary = f"V{version} {conversion_mode.upper()}模式 - 输出:{output_format}"

            if conversion_mode == "marker":
                gpu_enabled = (
                    config.get("gpu_config", {}).get("enabled", False)
                    if version == "v1"
                    else config.get("gpu", {}).get("enabled", False)
                )
                llm_enabled = config.get("use_llm", False)
                summary += f" (GPU:{'启用' if gpu_enabled else '禁用'}, LLM:{'启用' if llm_enabled else '禁用'})"

            elif conversion_mode == "ocr":
                ocr_quality = config.get("ocr_quality", "balanced")
                summary += f" (质量:{ocr_quality})"

            return summary

        except Exception:
            return "配置摘要生成失败"

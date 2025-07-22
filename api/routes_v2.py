from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
from api.new_models import (
    ConversionRequestV2,
    ConfigPresetsResponse,
    ConfigPreset,
    ConfigValidationResponse,
    MarkerConfig,
    OCRConfig,
)
from api.models import ConversionResponse
from utils.file_handler import FileHandler
from utils.progress import progress_manager
from utils.config_factory import ConfigPresets
from utils.config_migrator import ConfigMigrator
from utils.config_compatibility import ConfigCompatibilityChecker
from core.converter import convert_pdf_task
from core.scan_converter import scan_convert_pdf_task
from core.config import settings

router = APIRouter()


@router.get("/config-presets", response_model=ConfigPresetsResponse)
async def get_config_presets():
    """获取配置预设列表"""
    try:
        presets_data = ConfigPresets.get_preset_configs()
        presets = []

        for key, data in presets_data.items():
            preset = ConfigPreset(
                name=data["name"],
                description=data["description"],
                config=data["config"],
            )
            presets.append(preset)

        return ConfigPresetsResponse(presets=presets)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置预设失败: {str(e)}")


@router.post("/validate-config", response_model=ConfigValidationResponse)
async def validate_config(config_data: dict):
    """验证配置有效性 - 增强版，包含兼容性检查"""
    try:
        # 使用兼容性检查器
        compatibility_report = ConfigCompatibilityChecker.check_config_compatibility(
            config_data
        )

        # 构建响应
        response = ConfigValidationResponse(
            valid=compatibility_report["compatible"],
            errors=compatibility_report["issues"],
            warnings=compatibility_report["warnings"],
            suggestions=compatibility_report["suggestions"],
        )

        # 添加版本信息到建议中
        if compatibility_report["version"] == "v1":
            response.suggestions.append(
                "检测到V1配置格式，建议升级到V2格式以获得更好的类型安全"
            )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配置验证失败: {str(e)}")


@router.post("/check-compatibility")
async def check_config_compatibility(config_data: dict):
    """检查配置兼容性"""
    try:
        report = ConfigCompatibilityChecker.check_config_compatibility(config_data)
        return {
            "compatible": report["compatible"],
            "version": report["version"],
            "issues": report["issues"],
            "warnings": report["warnings"],
            "suggestions": report["suggestions"],
            "migration_needed": report["migration_needed"],
            "summary": ConfigCompatibilityChecker.get_config_summary(config_data),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"兼容性检查失败: {str(e)}")


@router.post("/auto-fix-config")
async def auto_fix_config(config_data: dict):
    """自动修复配置"""
    try:
        fixed_config = ConfigCompatibilityChecker.auto_fix_config(config_data)

        # 检查修复后的配置
        compatibility_report = ConfigCompatibilityChecker.check_config_compatibility(
            fixed_config
        )

        return {
            "original_config": config_data,
            "fixed_config": fixed_config,
            "compatible": compatibility_report["compatible"],
            "issues": compatibility_report["issues"],
            "warnings": compatibility_report["warnings"],
            "summary": ConfigCompatibilityChecker.get_config_summary(fixed_config),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配置自动修复失败: {str(e)}")


@router.post("/convert-v2", response_model=ConversionResponse)
async def start_conversion_v2(
    request: ConversionRequestV2, background_tasks: BackgroundTasks
):
    """启动PDF转换任务 V2 - 使用新的配置系统"""
    try:
        task_id = request.task_id

        # 查找文件
        pdf_files = list(settings.upload_path.glob(f"{task_id}_*"))
        if not pdf_files:
            raise HTTPException(status_code=404, detail="未找到上传的文件")

        pdf_path = str(pdf_files[0])

        # 启动进度跟踪
        progress_manager.start_task(task_id)

        # 配置兼容性检查
        config_dict = request.config.dict()
        compatibility_report = ConfigCompatibilityChecker.check_config_compatibility(
            config_dict
        )

        if not compatibility_report["compatible"]:
            print(f"⚠️ 配置兼容性问题: {compatibility_report['issues']}")
            # 尝试自动修复
            fixed_config = ConfigCompatibilityChecker.auto_fix_config(config_dict)
            config_dict = fixed_config
            print("✅ 配置已自动修复")

        # 根据配置类型自动分发
        if isinstance(request.config, OCRConfig):
            # OCR转换任务 - 无需GPU配置
            background_tasks.add_task(
                scan_convert_pdf_task,
                pdf_path=pdf_path,
                task_id=task_id,
                config=config_dict,
            )
            message = f"OCR转换任务已启动 (质量模式: {request.config.ocr_quality})"

        else:  # MarkerConfig
            # 应用GPU配置 - 仅Marker模式需要
            if request.config.gpu.enabled:
                settings.apply_gpu_config(request.config.gpu.dict())

            # Marker转换任务
            background_tasks.add_task(
                convert_pdf_task, pdf_path=pdf_path, task_id=task_id, config=config_dict
            )
            message = f"Marker转换任务已启动 (GPU: {'启用' if request.config.gpu.enabled else '禁用'})"

        return ConversionResponse(success=True, task_id=task_id, message=message)

    except Exception as e:
        print(f"❌ [ERROR] 启动转换失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动转换失败: {str(e)}")


@router.post("/convert-with-preset", response_model=ConversionResponse)
async def start_conversion_with_preset(
    task_id: str, preset_name: str, background_tasks: BackgroundTasks
):
    """使用预设配置启动转换"""
    try:
        # 获取预设配置
        preset_config = ConfigPresets.get_preset_by_name(preset_name)

        # 创建转换请求
        request = ConversionRequestV2(task_id=task_id, config=preset_config)

        # 调用V2转换接口
        return await start_conversion_v2(request, background_tasks)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动转换失败: {str(e)}")

# 配置系统迁移指南

## 概述

本文档介绍如何从V1配置系统迁移到V2配置系统。V2配置系统引入了Pydantic Union类型和discriminator，提供了更好的类型安全和配置验证。

## 主要变化

### 1. 配置结构变化

#### V1配置格式
```python
{
    "conversion_mode": "marker",
    "output_format": "markdown",
    "use_llm": False,
    "force_ocr": False,
    "gpu_config": {
        "enabled": False,
        "num_devices": 1,
        "num_workers": 4
    }
}
```

#### V2配置格式
```python
{
    "conversion_mode": "marker",
    "output_format": "markdown",
    "use_llm": False,
    "force_ocr": False,
    "gpu": {
        "enabled": False,
        "num_devices": 1,
        "num_workers": 4
    }
}
```

### 2. 关键差异

| 特性 | V1 | V2 |
|------|----|----|
| GPU配置字段 | `gpu_config` | `gpu` |
| 类型验证 | 基础验证 | Pydantic强类型验证 |
| 配置预设 | 手动配置 | 内置预设系统 |
| 兼容性检查 | 无 | 自动兼容性检查 |
| 自动修复 | 无 | 智能自动修复 |

## 迁移步骤

### 步骤1: 检测当前配置版本

```python
from utils.config_migrator import ConfigMigrator

migrator = ConfigMigrator()
version = migrator.detect_config_version(your_config)
print(f"当前配置版本: {version}")
```

### 步骤2: 自动迁移配置

```python
# V1到V2迁移
if version == "v1":
    v2_config = migrator.old_to_new_config(your_config)
    print("配置已迁移到V2格式")
```

### 步骤3: 验证新配置

```python
from utils.config_adapter import ConfigAdapter

adapter = ConfigAdapter()
is_valid = adapter.validate_config(v2_config)
if is_valid:
    print("配置验证通过")
else:
    print("配置验证失败")
```

### 步骤4: 检查兼容性

```python
from utils.config_compatibility import ConfigCompatibilityChecker

checker = ConfigCompatibilityChecker()
compatibility = checker.check_config_compatibility(v2_config)
print(f"兼容性报告: {compatibility}")
```

## 配置预设

V2系统提供了4个内置预设配置：

### 1. 快速Marker转换
```python
{
    "conversion_mode": "marker",
    "output_format": "markdown",
    "use_llm": False,
    "force_ocr": False,
    "strip_existing_ocr": True,
    "save_images": False,
    "format_lines": False,
    "disable_image_extraction": True,
    "gpu": {
        "enabled": False,
        "num_devices": 1,
        "num_workers": 4
    }
}
```

### 2. GPU加速Marker转换
```python
{
    "conversion_mode": "marker",
    "output_format": "markdown",
    "use_llm": False,
    "force_ocr": False,
    "strip_existing_ocr": True,
    "save_images": False,
    "format_lines": False,
    "disable_image_extraction": True,
    "gpu": {
        "enabled": True,
        "num_devices": 1,
        "num_workers": 4
    }
}
```

### 3. 高精度OCR转换
```python
{
    "conversion_mode": "ocr",
    "output_format": "markdown",
    "enhance_quality": True,
    "language_detection": True,
    "document_type_detection": True,
    "ocr_quality": "accurate",
    "target_languages": ["chi_sim", "eng"]
}
```

### 4. 快速OCR转换
```python
{
    "conversion_mode": "ocr",
    "output_format": "markdown",
    "enhance_quality": False,
    "language_detection": False,
    "document_type_detection": False,
    "ocr_quality": "fast",
    "target_languages": ["chi_sim", "eng"]
}
```

## API端点变化

### V1端点 (保持兼容)
- `POST /api/convert` - 转换请求
- `GET /api/progress/{task_id}` - 进度查询
- `GET /api/result/{task_id}` - 结果获取

### V2端点 (新增)
- `GET /api/v2/config-presets` - 获取配置预设
- `POST /api/v2/validate-config` - 验证配置
- `POST /api/v2/check-compatibility` - 检查兼容性
- `POST /api/v2/auto-fix-config` - 自动修复配置
- `POST /api/v2/convert-v2` - V2转换请求
- `POST /api/v2/convert-with-preset` - 预设转换

## 前端迁移

### 1. 更新配置管理器
```javascript
// 使用新的配置管理器
const configManager = new ConfigManager();
await configManager.init();

// 应用预设
await configManager.selectPreset('快速Marker转换');
```

### 2. 配置验证
```javascript
// 验证配置
const validation = await configManager.validateConfig(config);
if (validation.valid) {
    console.log('配置有效');
} else {
    console.log('配置错误:', validation.errors);
}
```

### 3. 兼容性检查
```javascript
// 检查兼容性
const compatibility = await configManager.checkCompatibility(config);
console.log('兼容性报告:', compatibility);
```

## 最佳实践

### 1. 渐进式迁移
- 先迁移非关键配置
- 逐步测试新功能
- 保持V1端点可用

### 2. 配置验证
- 始终验证迁移后的配置
- 使用兼容性检查器
- 应用自动修复功能

### 3. 预设使用
- 优先使用内置预设
- 根据需求调整预设
- 保存自定义配置

### 4. 错误处理
- 处理配置验证错误
- 记录兼容性问题
- 提供回退方案

## 常见问题

### Q1: V1配置还能使用吗？
A: 是的，V1配置仍然完全兼容，系统会自动检测并迁移。

### Q2: 如何选择预设配置？
A: 根据文档类型和性能需求选择：
- 文本PDF → 快速Marker转换
- 扫描PDF → 高精度OCR转换
- 需要GPU加速 → GPU加速Marker转换

### Q3: 配置验证失败怎么办？
A: 使用自动修复功能或检查错误信息，确保所有必需字段都存在且值有效。

### Q4: 如何自定义配置？
A: 基于预设配置进行修改，或使用配置工厂创建新配置。

## 技术支持

如果在迁移过程中遇到问题，请：

1. 检查配置格式是否正确
2. 使用配置验证工具
3. 查看错误日志
4. 联系技术支持团队

## 总结

V2配置系统提供了更好的类型安全、配置验证和用户体验。通过渐进式迁移，可以平滑过渡到新系统，同时保持向后兼容性。 
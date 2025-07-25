# DashScope 服务接口文档

## 概述

`DashScopeService` 是一个专门为 marker 库设计的 DashScope LLM 服务适配器，使用 `dashscope.Generation` 原生接口，解决了 marker 库与 DashScope API 的兼容性问题。

## 接口设计

### 类定义

```python
class DashScopeService(BaseService):
    """DashScope LLM 服务类，专门适配 DashScope API"""
```

### 继承关系

- **父类**: `marker.services.BaseService`
- **接口兼容**: 完全兼容 marker 库的 LLM 服务接口

### 核心属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `dashscope_api_key` | `str` | `None` | DashScope API 密钥 |
| `dashscope_model` | `str` | `"qwen-plus"` | 使用的模型名称 |
| `dashscope_image_format` | `str` | `"png"` | 图片格式 |

## 核心方法

### 1. 初始化方法

```python
def __init__(self, config=None):
    """
    初始化 DashScope 服务
    
    Args:
        config: 配置字典，支持以下键：
            - dashscope_api_key: API 密钥
            - dashscope_model: 模型名称
    """
```

**配置优先级**:
1. `config` 字典中的值
2. 环境变量 `DASHSCOPE_API_KEY` 和 `DASHSCOPE_MODEL`
3. 默认值

### 2. 主要调用接口

```python
def __call__(
    self,
    prompt: str,
    image: PIL.Image.Image | List[PIL.Image.Image] | None,
    block: Block | None,
    response_schema: type[BaseModel],
    max_retries: int | None = None,
    timeout: int | None = None,
) -> dict:
    """
    调用 DashScope API
    
    Args:
        prompt: 提示词文本
        image: 图片或图片列表（支持多模态）
        block: marker 块对象（用于元数据更新）
        response_schema: Pydantic 响应模式
        max_retries: 最大重试次数
        timeout: 超时时间（秒）
    
    Returns:
        解析后的响应数据字典
    """
```

### 3. 图片处理方法

#### `process_images()`
```python
def process_images(self, images: List[Image.Image]) -> List[dict]:
    """将 PIL 图片转换为 DashScope 兼容的格式"""
```

#### `img_to_base64()`
```python
def img_to_base64(self, img: PIL.Image.Image) -> str:
    """将图片转换为 base64 编码"""
```

#### `format_image_for_llm()`
```python
def format_image_for_llm(self, image) -> List[dict]:
    """格式化图片用于 LLM 调用"""
```

## 技术特性

### 1. 原生接口集成

使用 `dashscope.Generation.call()` 原生接口：

```python
response = Generation.call(
    model=self.dashscope_model,
    messages=[{"role": "system", "content": system_prompt}, *messages],
    result_format="message",
    enable_thinking=False,  # 关键：禁用 thinking 功能
    timeout=timeout,
    api_key=self.dashscope_api_key,
)
```

### 2. 智能响应处理

#### JSON 解析增强
- 自动清理 Markdown 代码块格式
- 处理 ````json` 和 ```` 标记
- 增强错误日志记录

#### 数据验证
- 使用 Pydantic 进行响应验证
- 为不同 schema 提供合适的默认值
- 支持 `TableSchema` 特殊处理

### 3. 错误处理机制

#### 重试策略
- 指数退避重试
- 可配置最大重试次数
- 详细的错误日志

#### 默认响应
```python
# TableSchema 默认响应
if response_schema.__name__ == "TableSchema":
    return {
        "comparison": "无法处理表格，返回默认响应",
        "corrected_html": "<table><tbody><tr><td>处理失败</td></tr></tbody></table>",
    }
else:
    return {}
```

## 使用方法

### 1. 环境变量配置

```bash
# Windows
set DASHSCOPE_API_KEY=your_api_key
set DASHSCOPE_MODEL=qwen-plus

# Linux/Mac
export DASHSCOPE_API_KEY=your_api_key
export DASHSCOPE_MODEL=qwen-plus
```

### 2. 命令行使用

```bash
# 基本使用
marker_single materials/testpdf.pdf \
  --use_llm \
  --llm_service=marker.services.dashscope.DashScopeService \
  --output_dir outputs \
  --debug

# 指定模型
marker_single materials/testpdf.pdf \
  --use_llm \
  --llm_service=marker.services.dashscope.DashScopeService \
  --output_dir outputs \
  --debug
```

### 3. 编程接口使用

```python
from marker.services.dashscope import DashScopeService
from pydantic import BaseModel

# 定义响应模式
class MySchema(BaseModel):
    result: str
    confidence: float

# 创建服务实例
service = DashScopeService(
    config={
        "dashscope_api_key": "your_api_key",
        "dashscope_model": "qwen-plus"
    }
)

# 调用服务
result = service(
    prompt="分析这个文本",
    image=None,
    block=None,
    response_schema=MySchema
)
```

## 支持的模型

### 文本模型
- `qwen-plus` (默认)
- `qwen-turbo`
- `qwen-max`
- `qwen3-235b-a22b`
- `qwen3-30b-a3b`

### 多模态模型
- `qwen-vl-plus`
- `qwen-vl-max`

## 配置参数

### 基础配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `dashscope_api_key` | `str` | 环境变量 | API 密钥 |
| `dashscope_model` | `str` | `"qwen-plus"` | 模型名称 |
| `dashscope_image_format` | `str` | `"png"` | 图片格式 |

### 高级配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `max_retries` | `int` | `2` | 最大重试次数 |
| `timeout` | `int` | `30` | 超时时间（秒） |
| `retry_wait_time` | `int` | `1` | 重试等待时间（秒） |

## 错误处理

### 常见错误类型

1. **API 密钥错误**
   ```
   AssertionError: In order to use DashScopeService, you must set the configuration values `dashscope_api_key`
   ```

2. **模型不存在**
   ```
   Error: model not found
   ```

3. **JSON 解析错误**
   ```
   JSON 解析错误: Expecting value: line 1 column 1 (char 0)
   ```

4. **数据验证错误**
   ```
   响应验证错误: 2 validation errors for TableSchema
   ```

### 调试技巧

1. **启用调试模式**
   ```bash
   --debug
   ```

2. **查看详细日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **测试简单调用**
   ```python
   # 创建测试实例
   service = DashScopeService()
   result = service("测试", None, None, TestSchema)
   ```

## 性能优化

### 1. 超时设置
```python
service = DashScopeService(
    config={"timeout": 60}  # 增加超时时间
)
```

### 2. 重试策略
```python
service = DashScopeService(
    config={
        "max_retries": 3,
        "retry_wait_time": 2
    }
)
```

### 3. 图片格式优化
```python
service = DashScopeService(
    config={"dashscope_image_format": "webp"}  # 使用更小的图片格式
)
```

## 扩展开发

### 1. 添加新模型支持
```python
class DashScopeService(BaseService):
    SUPPORTED_MODELS = {
        "qwen-plus": "qwen-plus",
        "qwen-turbo": "qwen-turbo",
        "custom-model": "your-custom-model"
    }
```

### 2. 自定义参数
```python
class DashScopeService(BaseService):
    temperature: Annotated[float, "Temperature for generation"] = 0.7
    max_tokens: Annotated[int, "Maximum tokens to generate"] = 2048
```

### 3. 流式支持
```python
def __call__(self, ..., stream: bool = False):
    if stream:
        # 实现流式调用
        pass
```

## 总结

`DashScopeService` 提供了：

- ✅ **完全兼容**: 与 marker 库无缝集成
- ✅ **原生接口**: 使用 `dashscope.Generation` 原生接口
- ✅ **智能处理**: 自动处理 JSON 解析和数据验证
- ✅ **错误恢复**: 完整的重试和默认响应机制
- ✅ **易于使用**: 简单的配置和调用方式
- ✅ **可扩展**: 支持自定义参数和功能扩展

这个服务为 marker 库提供了稳定、高效的 DashScope 集成解决方案。 
# PDF转Markdown工具 - API接口文档

## 1. 概述

### 1.1 基础信息
- **API版本**: v1.0
- **基础URL**: `http://localhost:8001/api`
- **文档地址**: `http://localhost:8001/docs` (Swagger UI)
- **ReDoc地址**: `http://localhost:8001/redoc` (ReDoc文档)
- **内容类型**: `application/json`
- **字符编码**: UTF-8

### 1.2 认证方式
当前版本暂不支持认证，所有接口均为公开访问。

### 1.3 错误处理
所有API接口使用标准HTTP状态码：
- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 数据验证失败
- `500 Internal Server Error`: 服务器内部错误

### 1.4 响应格式
所有API响应均为JSON格式，基本结构如下：
```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 2. 系统状态接口

### 2.1 GPU状态查询

#### 接口信息
- **URL**: `/api/gpu-status`
- **方法**: `GET`
- **描述**: 查询GPU状态和可用性

#### 请求参数
无

#### 响应格式
```json
{
  "available": true,
  "device_count": 1,
  "device_name": "NVIDIA GeForce RTX 3080",
  "memory_total": 10.0,
  "memory_used": 2.0,
  "memory_free": 8.0
}
```

#### 响应字段说明
| 字段 | 类型 | 说明 |
|------|------|------|
| available | boolean | GPU是否可用 |
| device_count | number | GPU数量 |
| device_name | string | GPU名称 |
| memory_total | number | 总显存（GB） |
| memory_used | number | 已用显存（GB） |
| memory_free | number | 可用显存（GB） |

#### 示例
```bash
curl -X GET "http://localhost:8001/api/gpu-status"
```

## 3. 文件管理接口

### 3.1 文件上传

#### 接口信息
- **URL**: `/api/upload`
- **方法**: `POST`
- **描述**: 上传PDF文件
- **内容类型**: `multipart/form-data`

#### 请求参数
| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| file | file | 是 | PDF文件 |

#### 响应格式
```json
{
  "success": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "message": "文件上传成功"
}
```

#### 响应字段说明
| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否成功 |
| task_id | string | 任务唯一标识符 |
| filename | string | 文件名 |
| message | string | 响应消息 |

#### 示例
```bash
curl -X POST "http://localhost:8001/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

### 3.2 文件下载

#### 接口信息
- **URL**: `/api/download/{task_id}`
- **方法**: `GET`
- **描述**: 下载转换后的文件

#### 路径参数
| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| task_id | string | 是 | 任务ID |

#### 响应格式
文件流，根据输出格式设置相应的Content-Type

#### 响应头
```
Content-Type: text/markdown (或 application/json, text/html)
Content-Disposition: attachment; filename="converted_{task_id}.md"
```

#### 示例
```bash
curl -X GET "http://localhost:8001/api/download/550e8400-e29b-41d4-a716-446655440000" \
  -o "document.md"
```

### 3.3 图片下载

#### 接口信息
- **URL**: `/api/download-images/{task_id}`
- **方法**: `GET`
- **描述**: 下载转换过程中提取的图片压缩包

#### 路径参数
| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| task_id | string | 是 | 任务ID |

#### 响应格式
ZIP文件流，Content-Type: `application/zip`

#### 响应头
```
Content-Type: application/zip
Content-Disposition: attachment; filename="images_{task_id}.zip"
```

#### 示例
```bash
curl -X GET "http://localhost:8001/api/download-images/550e8400-e29b-41d4-a716-446655440000" \
  -o "images.zip"
```

### 3.4 图片访问

#### 接口信息
- **URL**: `/api/images/{task_id}/{filename}`
- **方法**: `GET`
- **描述**: 获取转换过程中提取的单个图片

#### 路径参数
| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| task_id | string | 是 | 任务ID |
| filename | string | 是 | 图片文件名 |

#### 响应格式
图片文件流

#### 示例
```bash
curl -X GET "http://localhost:8001/api/images/550e8400-e29b-41d4-a716-446655440000/image1.png"
```

## 4. 转换管理接口

### 4.1 开始转换

#### 接口信息
- **URL**: `/api/convert`
- **方法**: `POST`
- **描述**: 开始PDF转换任务
- **内容类型**: `application/json`

#### 请求体格式
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "config": {
    "conversion_mode": "marker",
    "output_format": "markdown",
    "use_llm": false,
    "force_ocr": false,
    "strip_existing_ocr": true,
    "save_images": false,
    "format_lines": false,
    "disable_image_extraction": true,
    "gpu_config": {
      "enabled": false,
      "num_devices": 1,
      "num_workers": 4,
      "torch_device": "cuda",
      "cuda_visible_devices": "0"
    }
  }
}
```

#### 请求字段说明
| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| task_id | string | 是 | 任务ID |
| config | object | 是 | 转换配置 |

##### config字段说明 (Marker模式)
| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| conversion_mode | string | - | 转换模式：marker |
| output_format | string | markdown | 输出格式：markdown/html/json/chunks |
| use_llm | boolean | false | 是否使用LLM增强 |
| force_ocr | boolean | false | 是否强制OCR |
| strip_existing_ocr | boolean | true | 是否移除已有OCR文本 |
| save_images | boolean | false | 是否保存图片 |
| format_lines | boolean | false | 是否重新格式化行 |
| disable_image_extraction | boolean | true | 是否禁用图片提取 |
| gpu_config | object | - | GPU配置 |

##### config字段说明 (OCR模式)
| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| conversion_mode | string | - | 转换模式：ocr |
| output_format | string | markdown | 输出格式：markdown/html/json/chunks |
| enhance_quality | boolean | true | 是否增强图像质量 |
| language_detection | boolean | true | 是否启用智能语言检测 |
| document_type_detection | boolean | true | 是否启用文档类型检测 |
| ocr_quality | string | balanced | OCR质量模式：fast/balanced/accurate |
| target_languages | array | ["chi_sim", "eng"] | 目标识别语言列表 |

##### gpu_config字段说明
| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| enabled | boolean | false | 是否启用GPU |
| num_devices | number | 1 | GPU设备数量 |
| num_workers | number | 4 | 工作进程数 |
| torch_device | string | cuda | PyTorch设备类型 |
| cuda_visible_devices | string | 0 | 可见GPU设备 |

#### 响应格式
```json
{
  "success": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Marker转换任务已启动 (GPU: 禁用)"
}
```

#### 响应字段说明
| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否成功 |
| task_id | string | 任务ID |
| message | string | 状态消息 |

#### 示例
```bash
curl -X POST "http://localhost:8001/api/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "config": {
      "conversion_mode": "marker",
      "output_format": "markdown",
      "gpu_config": {
        "enabled": true,
        "num_devices": 1
      }
    }
  }'
```

### 4.2 使用预设配置转换

#### 接口信息
- **URL**: `/api/convert-with-preset`
- **方法**: `POST`
- **描述**: 使用预设配置开始PDF转换任务
- **内容类型**: `application/json`

#### 请求体格式
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "preset_name": "text_pdf"
}
```

#### 请求字段说明
| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| task_id | string | 是 | 任务ID |
| preset_name | string | 是 | 预设配置名称 |

#### 响应格式
```json
{
  "success": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Marker转换任务已启动 (GPU: 禁用)"
}
```

#### 示例
```bash
curl -X POST "http://localhost:8001/api/convert-with-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "preset_name": "text_pdf"
  }'
```

### 4.3 查询进度

#### 接口信息
- **URL**: `/api/progress/{task_id}`
- **方法**: `GET`
- **描述**: 查询转换任务进度

#### 路径参数
| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| task_id | string | 是 | 任务ID |

#### 响应格式
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 75.0,
  "error": null
}
```

#### 响应字段说明
| 字段 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务ID |
| status | string | 任务状态：pending/processing/completed/failed |
| progress | number | 进度百分比（0-100） |
| error | string | 错误信息（如果有） |

#### 示例
```bash
curl -X GET "http://localhost:8001/api/progress/550e8400-e29b-41d4-a716-446655440000"
```

### 4.4 获取结果

#### 接口信息
- **URL**: `/api/result/{task_id}`
- **方法**: `GET`
- **描述**: 获取转换结果信息

#### 路径参数
| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| task_id | string | 是 | 任务ID |

#### 响应格式
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "# 转换后的Markdown内容\n\n这里是转换后的文本...",
  "has_images": true,
  "image_count": 5,
  "file_name": "document.md",
  "file_format": ".md"
}
```

#### 响应字段说明
| 字段 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务ID |
| content | string | 转换后的内容 |
| has_images | boolean | 是否包含图片 |
| image_count | number | 图片数量 |
| file_name | string | 文件名 |
| file_format | string | 文件格式 |

#### 示例
```bash
curl -X GET "http://localhost:8001/api/result/550e8400-e29b-41d4-a716-446655440000"
```

## 5. 配置管理接口

### 5.1 获取预设配置

#### 接口信息
- **URL**: `/api/config-presets`
- **方法**: `GET`
- **描述**: 获取所有预设配置

#### 请求参数
无

#### 响应格式
```json
{
  "presets": [
    {
      "name": "text_pdf",
      "description": "文本型PDF配置 - 适用于可搜索的PDF文档，使用Marker引擎",
      "config": {
        "conversion_mode": "marker",
        "output_format": "markdown",
        "use_llm": false,
        "force_ocr": false,
        "strip_existing_ocr": true,
        "save_images": false,
        "format_lines": false,
        "disable_image_extraction": true,
        "gpu_config": {
          "enabled": false,
          "num_devices": 1,
          "num_workers": 4,
          "torch_device": "cuda",
          "cuda_visible_devices": "0"
        }
      }
    },
    {
      "name": "scan_pdf",
      "description": "扫描型PDF配置 - 适用于图片型PDF文档，使用OCR引擎",
      "config": {
        "conversion_mode": "ocr",
        "output_format": "markdown",
        "enhance_quality": true,
        "language_detection": true,
        "document_type_detection": true,
        "ocr_quality": "balanced",
        "target_languages": ["chi_sim", "eng"]
      }
    }
  ]
}
```

#### 响应字段说明
| 字段 | 类型 | 说明 |
|------|------|------|
| presets | array | 预设配置列表 |
| presets[].name | string | 预设名称 |
| presets[].description | string | 预设描述 |
| presets[].config | object | 配置参数 |

#### 示例
```bash
curl -X GET "http://localhost:8001/api/config-presets"
```

### 5.2 验证配置

#### 接口信息
- **URL**: `/api/validate-config`
- **方法**: `POST`
- **描述**: 验证配置有效性
- **内容类型**: `application/json`

#### 请求体格式
```json
{
  "config": {
    "conversion_mode": "marker",
    "output_format": "markdown",
    "gpu_config": {
      "enabled": true,
      "num_devices": 1
    }
  }
}
```

#### 请求字段说明
| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| config | object | 是 | 要验证的配置 |

#### 响应格式
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "GPU配置可能影响性能"
  ],
  "suggestions": [
    "建议启用图像增强以提高质量"
  ]
}
```

#### 响应字段说明
| 字段 | 类型 | 说明 |
|------|------|------|
| valid | boolean | 配置是否有效 |
| errors | array | 错误信息列表 |
| warnings | array | 警告信息列表 |
| suggestions | array | 建议信息列表 |

#### 示例
```bash
curl -X POST "http://localhost:8001/api/validate-config" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "conversion_mode": "marker",
      "output_format": "markdown"
    }
  }'
```

### 5.3 检查配置兼容性

#### 接口信息
- **URL**: `/api/check-compatibility`
- **方法**: `POST`
- **描述**: 检查配置与当前环境的兼容性
- **内容类型**: `application/json`

#### 请求体格式
```json
{
  "config": {
    "conversion_mode": "marker",
    "gpu_config": {
      "enabled": true,
      "num_devices": 1
    }
  }
}
```

#### 响应格式
```json
{
  "compatible": true,
  "issues": [],
  "recommendations": [
    "建议检查GPU驱动版本"
  ]
}
```

### 5.4 自动修复配置

#### 接口信息
- **URL**: `/api/auto-fix-config`
- **方法**: `POST`
- **描述**: 自动修复配置中的问题
- **内容类型**: `application/json`

#### 请求体格式
```json
{
  "config": {
    "conversion_mode": "marker",
    "gpu_config": {
      "enabled": true,
      "num_devices": 2
    }
  }
}
```

#### 响应格式
```json
{
  "fixed": true,
  "original_config": {
    "conversion_mode": "marker",
    "gpu_config": {
      "enabled": true,
      "num_devices": 2
    }
  },
  "fixed_config": {
    "conversion_mode": "marker",
    "gpu_config": {
      "enabled": true,
      "num_devices": 1
    }
  },
  "fixes_applied": [
    "将GPU设备数量从2调整为1"
  ]
}
```

## 6. 错误码说明

### 6.1 通用错误码
| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求参数格式和内容 |
| 404 | 资源不存在 | 确认任务ID或文件路径正确 |
| 422 | 数据验证失败 | 检查请求数据格式和类型 |
| 500 | 服务器内部错误 | 联系管理员或稍后重试 |

### 6.2 业务错误码
| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| FILE_TOO_LARGE | 文件大小超过限制 | 文件大小不能超过限制 |
| INVALID_FILE_TYPE | 不支持的文件类型 | 只支持PDF文件 |
| TASK_NOT_FOUND | 任务不存在 | 任务ID无效或已过期 |
| TASK_ALREADY_RUNNING | 任务正在运行 | 不能重复启动同一任务 |
| GPU_NOT_AVAILABLE | GPU不可用 | 检查GPU配置和环境 |
| CONVERSION_FAILED | 转换失败 | 检查PDF文件是否损坏 |

### 6.3 错误响应格式
```json
{
  "detail": "文件上传失败: 不支持的文件类型"
}
```

## 7. 使用示例

### 7.1 完整转换流程

#### 步骤1：检查GPU状态
```bash
# 检查GPU状态
curl -X GET "http://localhost:8001/api/gpu-status"
```

#### 步骤2：上传文件
```bash
# 上传PDF文件
curl -X POST "http://localhost:8001/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

#### 步骤3：开始转换
```bash
# 使用自定义配置转换
curl -X POST "http://localhost:8001/api/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "config": {
      "conversion_mode": "marker",
      "output_format": "markdown",
      "gpu_config": {
        "enabled": true,
        "num_devices": 1
      }
    }
  }'

# 或使用预设配置转换
curl -X POST "http://localhost:8001/api/convert-with-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "preset_name": "text_pdf"
  }'
```

#### 步骤4：监控进度
```bash
# 查询转换进度
curl -X GET "http://localhost:8001/api/progress/550e8400-e29b-41d4-a716-446655440000"
```

#### 步骤5：获取结果
```bash
# 获取转换结果
curl -X GET "http://localhost:8001/api/result/550e8400-e29b-41d4-a716-446655440000"

# 下载转换后的文件
curl -X GET "http://localhost:8001/api/download/550e8400-e29b-41d4-a716-446655440000" \
  -o "document.md"

# 下载图片压缩包（如果有）
curl -X GET "http://localhost:8001/api/download-images/550e8400-e29b-41d4-a716-446655440000" \
  -o "images.zip"
```

### 7.2 JavaScript示例

#### 文件上传
```javascript
async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}
```

#### 开始转换
```javascript
async function startConversion(taskId, config) {
  const response = await fetch('/api/convert', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      task_id: taskId,
      config: config
    })
  });
  
  return await response.json();
}

// 使用预设配置
async function startConversionWithPreset(taskId, presetName) {
  const response = await fetch('/api/convert-with-preset', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      task_id: taskId,
      preset_name: presetName
    })
  });
  
  return await response.json();
}
```

#### 监控进度
```javascript
async function monitorProgress(taskId) {
  const response = await fetch(`/api/progress/${taskId}`);
  return await response.json();
}

// 定期查询进度
function startProgressMonitoring(taskId) {
  const interval = setInterval(async () => {
    const progress = await monitorProgress(taskId);
    console.log(`进度: ${progress.progress}%`);
    
    if (progress.status === 'completed' || progress.status === 'failed') {
      clearInterval(interval);
      console.log('转换完成');
    }
  }, 2000);
}
```

#### 获取结果
```javascript
async function getResult(taskId) {
  const response = await fetch(`/api/result/${taskId}`);
  return await response.json();
}

async function downloadResult(taskId) {
  const response = await fetch(`/api/download/${taskId}`);
  const blob = await response.blob();
  
  // 创建下载链接
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `converted_${taskId}.md`;
  a.click();
  window.URL.revokeObjectURL(url);
}
```

### 7.3 Python示例

#### 使用requests库
```python
import requests
import time

def convert_pdf(pdf_path, config):
    # 1. 上传文件
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        response = requests.post('http://localhost:8001/api/upload', files=files)
        upload_result = response.json()
        task_id = upload_result['task_id']
    
    # 2. 开始转换
    response = requests.post('http://localhost:8001/api/convert', json={
        'task_id': task_id,
        'config': config
    })
    
    # 3. 监控进度
    while True:
        response = requests.get(f'http://localhost:8001/api/progress/{task_id}')
        progress = response.json()
        
        print(f"进度: {progress['progress']}%")
        
        if progress['status'] in ['completed', 'failed']:
            break
        
        time.sleep(2)
    
    # 4. 获取结果
    response = requests.get(f'http://localhost:8001/api/result/{task_id}')
    result = response.json()
    
    # 5. 下载文件
    response = requests.get(f'http://localhost:8001/api/download/{task_id}')
    with open('output.md', 'wb') as f:
        f.write(response.content)
    
    return result

# 使用示例
config = {
    'conversion_mode': 'marker',
    'output_format': 'markdown',
    'gpu_config': {
        'enabled': True,
        'num_devices': 1
    }
}

result = convert_pdf('document.pdf', config)
print(f"转换完成，包含图片: {result['has_images']}")
```

## 8. 最佳实践

### 8.1 性能优化
1. **使用GPU加速**: 对于文本PDF，启用GPU可显著提升转换速度
2. **合理配置工作进程**: 根据CPU核心数调整num_workers参数
3. **批量处理**: 对于多个文件，使用异步处理避免阻塞

### 8.2 错误处理
1. **检查文件格式**: 确保上传的是有效的PDF文件
2. **监控任务状态**: 定期查询进度，及时处理异常
3. **重试机制**: 对于网络错误，实现适当的重试逻辑

### 8.3 安全考虑
1. **文件大小限制**: 避免上传过大的文件影响系统性能
2. **输入验证**: 验证所有用户输入，防止恶意文件
3. **资源清理**: 及时清理临时文件和过期任务

### 8.4 用户体验
1. **进度反馈**: 实时显示转换进度，提升用户体验
2. **错误提示**: 提供清晰的错误信息和解决建议
3. **结果预览**: 允许用户预览转换结果再决定是否下载

## 9. 实际实现状态

### 9.1 已实现接口
- ✅ **文件上传**: `/api/upload` - 完整的文件上传功能
- ✅ **文件下载**: `/api/download/{task_id}` - 支持多种格式下载
- ✅ **图片下载**: `/api/download-images/{task_id}` - ZIP格式图片包
- ✅ **图片访问**: `/api/images/{task_id}/{filename}` - 单个图片访问
- ✅ **转换控制**: `/api/convert` - 自定义配置转换
- ✅ **预设转换**: `/api/convert-with-preset` - 预设配置转换
- ✅ **进度查询**: `/api/progress/{task_id}` - 实时进度监控
- ✅ **结果获取**: `/api/result/{task_id}` - 转换结果信息
- ✅ **GPU状态**: `/api/gpu-status` - GPU可用性检查
- ✅ **配置管理**: `/api/config-presets` - 预设配置获取
- ✅ **配置验证**: `/api/validate-config` - 配置有效性验证
- ✅ **兼容性检查**: `/api/check-compatibility` - 环境兼容性检查
- ✅ **自动修复**: `/api/auto-fix-config` - 配置自动修复

### 9.2 技术特性
- **异步处理**: 所有转换任务在后台异步执行
- **实时进度**: 支持实时进度查询和状态更新
- **多格式支持**: 支持markdown、json、html、chunks等多种输出格式
- **智能配置**: 基于Pydantic的配置验证和管理
- **错误处理**: 完善的错误处理和异常捕获
- **文件管理**: 完整的文件上传、下载、存储功能

### 9.3 待优化项目
- **健康检查**: 当前缺少`/api/health`接口
- **批量操作**: 支持批量文件上传和转换
- **WebSocket**: 实时进度推送（当前使用轮询）
- **缓存机制**: 结果缓存和重复转换优化
- **限流控制**: API访问频率限制

## 10. 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持Marker和OCR双引擎转换
- 提供完整的RESTful API接口
- 支持GPU加速和并行处理
- 实现实时进度监控
- 提供配置管理和验证功能
- 支持多种输出格式
- 实现图片提取和管理功能 
# 变更日志

本项目遵循[语义化版本](https://semver.org/lang/zh-CN/)规范。

## [未发布]

### 计划中
- 智能路由功能
- 性能监控系统
- 缓存机制
- 批量处理功能
- WebSocket实时通信

## [1.0.0] - 2024-07-24

### 新增
- 🎉 **初始版本发布**
- ✨ **双引擎架构**: Marker引擎和OCR引擎
- 🌐 **Web界面**: 基于Vue.js 3的用户界面
- 🔧 **配置管理系统**: 基于Pydantic的配置验证和管理
- 📁 **文件处理**: 完整的文件上传、下载、存储功能
- 📊 **进度跟踪**: 实时进度监控和状态管理
- 🎛️ **预设配置**: 文本型和扫描型PDF配置预设
- 🔍 **OCR功能**: 支持中英文混合识别
- ⚡ **GPU加速**: Marker引擎支持CUDA GPU加速
- 📝 **API文档**: 完整的RESTful API接口

### 技术特性
- **后端框架**: FastAPI + Uvicorn
- **PDF处理**: Marker PDF库 (marker-pdf[full])
- **OCR引擎**: Tesseract OCR + OpenCV + PIL
- **前端框架**: Vue.js 3 + 原生JavaScript
- **依赖管理**: Poetry
- **类型安全**: Pydantic数据验证

### API接口
- `GET /api/gpu-status` - GPU状态查询
- `POST /api/upload` - 文件上传
- `POST /api/convert` - 开始转换

- `GET /api/progress/{task_id}` - 查询进度
- `GET /api/result/{task_id}` - 获取结果
- `GET /api/download/{task_id}` - 下载转换结果
- `GET /api/download-images/{task_id}` - 下载图片
- `GET /api/images/{task_id}/{filename}` - 获取单个图片

- `POST /api/validate-config` - 验证配置
- `POST /api/check-compatibility` - 检查兼容性
- `POST /api/auto-fix-config` - 自动修复配置

### 配置选项

#### Marker配置
- `conversion_mode`: "marker"
- `output_format`: "markdown" | "json" | "html" | "chunks"
- `use_llm`: 是否使用LLM增强
- `force_ocr`: 是否强制OCR
- `strip_existing_ocr`: 是否去除已有OCR文本
- `save_images`: 是否保存图片
- `format_lines`: 是否重新格式化行
- `disable_image_extraction`: 是否禁用图像提取
- `gpu_config`: GPU配置

#### OCR配置
- `conversion_mode`: "ocr"
- `output_format`: "markdown" | "json" | "html" | "chunks"
- `enhance_quality`: 是否增强图像质量
- `language_detection`: 是否启用语言检测
- `document_type_detection`: 是否启用文档类型检测
- `ocr_quality`: "fast" | "balanced" | "accurate"
- `target_languages`: 目标语言列表

### 项目结构
```
textProcess/
├── api/                    # API接口模块
├── core/                   # 核心功能模块
├── utils/                  # 工具模块
├── static/                 # 前端静态文件
├── docs/                   # 项目文档
├── uploads/                # 上传文件目录
├── outputs/                # 输出文件目录
├── main.py                 # 应用入口
├── pyproject.toml         # 项目配置
└── README.md              # 项目文档
```

### 文档
- 📖 **README.md**: 项目介绍和使用指南
- 📋 **技术文档.md**: 详细的技术实现文档
- 🎨 **设计方案.md**: 系统设计方案
- 🔌 **API接口文档.md**: 完整的API接口文档
- 🚀 **部署指南.md**: 部署和运维指南
- 🤝 **CONTRIBUTING.md**: 贡献指南
- 📜 **CODE_OF_CONDUCT.md**: 行为准则

### 已知问题
- 缺少健康检查接口 (`/api/health`)
- 智能路由功能尚未实现
- 性能监控系统待完善
- 缓存机制待实现

---

## 版本说明

### 版本号格式
- `MAJOR.MINOR.PATCH`
- `MAJOR`: 不兼容的API修改
- `MINOR`: 向下兼容的功能性新增
- `PATCH`: 向下兼容的问题修正

### 变更类型
- 🎉 **重大更新**: 重要功能发布或重大架构变更
- ✨ **新增**: 新功能
- 🔧 **修复**: Bug修复
- 📝 **文档**: 文档更新
- 🎨 **样式**: 代码格式调整
- ♻️ **重构**: 代码重构
- ⚡ **性能**: 性能优化
- 🧪 **测试**: 测试相关
- 🔧 **构建**: 构建过程或辅助工具的变动

### 发布流程
1. 更新版本号 (`pyproject.toml`)
2. 更新CHANGELOG.md
3. 创建Git标签
4. 发布GitHub Release
5. 更新文档

---

## 贡献者

感谢所有为项目做出贡献的开发者！

### 核心维护者
- [GeorgeHit](https://github.com/GeorgeHit) - 项目创建者和主要维护者

### 贡献者
- 欢迎所有贡献者！请查看[CONTRIBUTING.md](CONTRIBUTING.md)了解如何参与项目。

---

## 许可证

本项目采用 [MIT](LICENSE) 许可证。 
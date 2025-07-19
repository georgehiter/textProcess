# PDF转Markdown工具

基于marker库的现代化PDF转Markdown工具，提供友好的Web界面和完整的转换功能。

## 功能特点

- 🚀 **现代化界面** - 响应式设计，支持桌面和移动设备
- 📄 **多格式支持** - 支持Markdown、JSON、HTML、Chunks输出格式
- ⚙️ **灵活配置** - 提供LLM增强、OCR设置、图片提取等选项
- 📊 **实时进度** - 显示详细的转换进度和时间估算
- 🎯 **高质量转换** - 基于marker库，提供准确的PDF解析
- 💾 **文件管理** - 自动文件清理和结果下载

## 技术栈

### 后端
- **FastAPI** - 高性能异步Web框架
- **marker-pdf** - PDF转换核心库
- **uvicorn** - ASGI服务器

### 前端
- **Vue.js 3** - 现代化前端框架
- **Marked.js** - Markdown渲染
- **Highlight.js** - 代码语法高亮

## 快速开始

### 1. 安装依赖

```bash
poetry install
```

### 2. 启动服务

```bash
poetry run python main.py
```

### 3. 访问应用

打开浏览器访问: http://localhost:8000

## 使用说明

### 步骤1: 上传文件
- 拖拽PDF文件到上传区域
- 或点击选择文件按钮
- 支持最大100MB的PDF文件

### 步骤2: 配置选项
- **输出格式**: 选择Markdown、JSON、HTML或Chunks
- **LLM增强**: 启用AI提升转换准确性
- **OCR设置**: 强制使用OCR识别扫描版PDF
- **图片处理**: 提取和保存PDF中的图片
- **格式化**: 重新格式化文本行

### 步骤3: 转换进度
- 实时显示转换进度
- 显示当前处理阶段
- 提供时间估算

### 步骤4: 查看结果
- 预览转换后的Markdown内容
- 下载转换结果文件
- 查看提取的图片

## API接口

### 文件上传
```
POST /api/upload
```

### 开始转换
```
POST /api/convert
```

### 获取进度
```
GET /api/progress/{task_id}
```

### 获取结果
```
GET /api/result/{task_id}
```

### 下载文件
```
GET /api/download/{task_id}
```

## 项目结构

```
textProcess/
├── main.py                 # FastAPI主应用
├── api/                    # API模块
│   ├── __init__.py
│   ├── routes.py           # API路由
│   └── models.py           # 数据模型
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── config.py           # 配置管理
│   └── converter.py        # PDF转换逻辑
├── utils/                  # 工具模块
│   ├── __init__.py
│   ├── file_handler.py     # 文件处理
│   └── progress.py         # 进度监控
├── static/                 # 静态文件
│   ├── index.html          # 主页面
│   ├── app.js              # Vue.js应用
│   └── style.css           # 样式文件
├── uploads/                # 上传文件存储
├── outputs/                # 转换结果存储
├── templates/              # 临时文件存储
├── requirements.txt        # 依赖列表
└── README.md              # 项目文档
```

## 配置选项

### 应用配置 (core/config.py)
- 文件大小限制
- 允许的文件类型
- 服务器端口和主机
- CORS设置

### 转换配置
- 输出格式选择
- LLM增强选项
- OCR设置
- 图片处理选项

## 开发说明

### 本地开发
```bash
# 安装开发依赖
poetry install

# 启动开发服务器
poetry run python main.py
```

### 生产部署
```bash
# 使用poetry和uvicorn启动
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 故障排除

### 常见问题

1. **文件上传失败**
   - 检查文件大小是否超过限制
   - 确认文件格式为PDF

2. **转换失败**
   - 检查PDF文件是否损坏
   - 尝试启用OCR选项

3. **进度不更新**
   - 刷新页面重试
   - 检查网络连接

### 日志查看
应用运行时会输出详细的日志信息，包括：
- 文件上传状态
- 转换进度
- 错误信息

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持PDF转Markdown
- 提供Web界面
- 实时进度监控 
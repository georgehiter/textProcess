# 贡献指南

感谢您对PDF转Markdown工具项目的关注！我们欢迎所有形式的贡献，包括但不限于：

- 🐛 报告Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- 🎨 改进用户界面
- ⚡ 性能优化
- 🧪 编写测试

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [Pull Request流程](#pull-request流程)
- [发布流程](#发布流程)

## 🤝 行为准则

本项目采用[贡献者公约](CODE_OF_CONDUCT.md)。参与即表示您同意遵守其条款。

## 🚀 如何贡献

### 报告Bug

如果您发现了Bug，请通过以下步骤报告：

1. **搜索现有问题**: 在[Issues](https://github.com/your-username/textProcess/issues)中搜索是否已有相关问题
2. **创建新Issue**: 如果没有找到相关问题，请创建新的Issue
3. **提供详细信息**: 包含以下信息：
   - Bug的详细描述
   - 重现步骤
   - 预期行为
   - 实际行为
   - 环境信息（操作系统、Python版本等）
   - 错误日志（如果有）

### 功能建议

如果您有新功能建议：

1. **搜索现有建议**: 在Issues中搜索是否已有类似建议
2. **创建Feature Request**: 使用"Feature Request"模板
3. **详细描述**: 说明功能用途、实现思路、预期效果

### 代码贡献

#### 1. Fork项目

1. 访问项目主页：https://github.com/your-username/textProcess
2. 点击右上角的"Fork"按钮
3. 克隆您的Fork到本地：

```bash
git clone https://github.com/your-username/textProcess.git
cd textProcess
```

#### 2. 创建功能分支

```bash
# 确保在main分支
git checkout main
git pull origin main

# 创建新分支
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

#### 3. 开发环境设置

```bash
# 安装Poetry（如果尚未安装）
curl -sSL https://install.python-poetry.org | python3 -

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell

# 安装开发依赖
poetry install --with dev
```

#### 4. 运行测试

```bash
# 运行所有测试
poetry run pytest

# 运行特定测试
poetry run pytest tests/test_converter.py

# 运行测试并生成覆盖率报告
poetry run pytest --cov=core --cov=api --cov=utils
```

#### 5. 代码检查

```bash
# 代码格式检查
poetry run black --check .

# 代码质量检查
poetry run flake8 .

# 类型检查
poetry run mypy .
```

## 🛠️ 开发环境设置

### 系统要求

- Python 3.11+
- Poetry 1.4.0+
- Git
- Tesseract OCR（用于OCR功能）

### 详细设置步骤

#### 1. 克隆项目

```bash
git clone https://github.com/your-username/textProcess.git
cd textProcess
```

#### 2. 安装依赖

```bash
# 安装Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 配置Poetry
poetry config virtualenvs.in-project true

# 安装项目依赖
poetry install

# 安装开发依赖
poetry install --with dev
```

#### 3. 安装Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
1. 下载安装包：https://github.com/UB-Mannheim/tesseract/wiki
2. 安装时选择中文和英文语言包
3. 将安装路径添加到系统环境变量PATH中

#### 4. 验证安装

```bash
# 验证Python依赖
poetry run python -c "import fastapi, marker, pytesseract, cv2, PIL; print('✅ 依赖安装成功')"

# 验证Tesseract
tesseract --version

# 验证Poetry环境
poetry env info
```

#### 5. 启动开发服务器

```bash
# 启动开发服务器
poetry run python main.py

# 或使用uvicorn
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## 📝 代码规范

### Python代码规范

#### 1. 代码风格

- 遵循[PEP 8](https://www.python.org/dev/peps/pep-0008/)规范
- 使用[Black](https://black.readthedocs.io/)进行代码格式化
- 行长度限制：88字符（Black默认）
- 使用4个空格缩进

#### 2. 类型注解

- 所有函数和类方法都应该有类型注解
- 使用`typing`模块的类型提示
- 复杂类型使用`TypeAlias`定义

```python
from typing import Dict, List, Optional, Union, TypeAlias

ConfigType: TypeAlias = Union[MarkerConfig, OCRConfig]

def process_config(config: ConfigType) -> Dict[str, Any]:
    """处理配置对象"""
    pass
```

#### 3. 文档字符串

- 所有公共函数、类和方法都应该有文档字符串
- 使用Google风格的文档字符串
- 包含参数、返回值和异常说明

```python
def convert_pdf(pdf_path: str, config: Dict[str, Any]) -> str:
    """将PDF文件转换为Markdown格式。
    
    Args:
        pdf_path: PDF文件路径
        config: 转换配置
        
    Returns:
        转换后的Markdown内容
        
    Raises:
        FileNotFoundError: 当PDF文件不存在时
        ConversionError: 当转换失败时
    """
    pass
```

#### 4. 错误处理

- 使用自定义异常类
- 提供有意义的错误消息
- 记录详细的错误日志

```python
class ConversionError(Exception):
    """转换过程中的错误"""
    pass

def safe_convert(pdf_path: str) -> str:
    try:
        return convert_pdf(pdf_path)
    except FileNotFoundError:
        raise ConversionError(f"PDF文件不存在: {pdf_path}")
    except Exception as e:
        logger.error(f"转换失败: {e}")
        raise ConversionError(f"转换过程中发生错误: {e}")
```

### 前端代码规范

#### 1. JavaScript规范

- 使用ES6+语法
- 使用`const`和`let`，避免`var`
- 使用箭头函数
- 使用模板字符串

#### 2. Vue.js规范

- 使用Composition API
- 组件名使用PascalCase
- Props使用camelCase
- 事件名使用kebab-case

```javascript
// 组件定义
const MyComponent = {
    name: 'MyComponent',
    props: {
        configData: {
            type: Object,
            required: true
        }
    },
    emits: ['config-change'],
    setup(props, { emit }) {
        const handleConfigChange = (newConfig) => {
            emit('config-change', newConfig)
        }
        
        return {
            handleConfigChange
        }
    }
}
```

## 📋 提交规范

### 提交消息格式

使用[Conventional Commits](https://www.conventionalcommits.org/)规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### 类型说明

- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

#### 示例

```bash
# 新功能
git commit -m "feat: 添加智能路由功能"

# Bug修复
git commit -m "fix: 修复OCR引擎内存泄漏问题"

# 文档更新
git commit -m "docs: 更新API接口文档"

# 代码重构
git commit -m "refactor: 重构配置管理系统"

# 性能优化
git commit -m "perf: 优化大文件处理性能"
```

### 提交前检查

```bash
# 代码格式化
poetry run black .

# 代码质量检查
poetry run flake8 .

# 运行测试
poetry run pytest

# 类型检查
poetry run mypy .
```

## 🔄 Pull Request流程

### 1. 准备PR

1. **确保代码质量**：
   - 通过所有测试
   - 符合代码规范
   - 添加必要的文档

2. **更新文档**：
   - 更新README.md（如果需要）
   - 更新API文档（如果修改了API）
   - 添加代码注释

3. **提交代码**：
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   git push origin feature/your-feature-name
   ```

### 2. 创建Pull Request

1. 访问您的Fork页面
2. 点击"Compare & pull request"
3. 填写PR描述：
   - 功能描述
   - 解决的问题
   - 测试情况
   - 相关Issue链接

### 3. PR模板

```markdown
## 描述
简要描述此PR的功能或修复的问题

## 类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 代码重构
- [ ] 性能优化
- [ ] 测试相关

## 测试
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动测试完成

## 检查清单
- [ ] 代码符合项目规范
- [ ] 添加了必要的文档
- [ ] 更新了相关文档
- [ ] 没有引入新的警告
- [ ] 测试覆盖率没有降低

## 相关Issue
Closes #123
```

### 4. 代码审查

- 维护者会审查您的代码
- 可能需要修改或改进
- 请及时响应审查意见

## 🚀 发布流程

### 版本号规范

使用[语义化版本](https://semver.org/lang/zh-CN/)：

- `MAJOR.MINOR.PATCH`
- `MAJOR`: 不兼容的API修改
- `MINOR`: 向下兼容的功能性新增
- `PATCH`: 向下兼容的问题修正

### 发布步骤

1. **更新版本号**：
   ```bash
   # 更新pyproject.toml中的版本号
   poetry version patch  # 或 minor, major
   ```

2. **更新CHANGELOG.md**：
   - 记录新功能、修复和改进

3. **创建Release**：
   - 在GitHub上创建新的Release
   - 添加版本说明
   - 上传构建产物

## 📞 获取帮助

如果您在贡献过程中遇到问题：

1. **查看文档**：阅读项目文档和代码注释
2. **搜索Issues**：在Issues中搜索相关问题
3. **创建Issue**：如果问题仍未解决，创建新的Issue
4. **联系维护者**：通过GitHub Discussions或邮件联系

## 🙏 致谢

感谢所有为项目做出贡献的开发者！您的贡献让这个项目变得更好。

---

**注意**：在提交代码之前，请确保您已经阅读并理解了本贡献指南。如有疑问，请随时联系项目维护者。 
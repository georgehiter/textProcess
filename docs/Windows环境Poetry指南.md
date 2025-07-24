# Windows环境Poetry指南

## 📋 目录

- [环境准备](#环境准备)
- [安装Poetry](#安装poetry)
- [配置Poetry](#配置poetry)
- [项目部署](#项目部署)
- [常用命令](#常用命令)
- [故障排除](#故障排除)
- [最佳实践](#最佳实践)

## 🖥️ 环境准备

### 系统要求

- **操作系统**: Windows 10 或更高版本
- **Python**: 3.11 或更高版本
- **内存**: 建议 4GB 以上
- **存储**: 至少 2GB 可用空间
- **网络**: 需要网络连接下载依赖包
- **Git**: 可选，仅在使用Git克隆项目时需要

### 检查Python环境

```cmd
python --version
```
确保输出类似：`Python 3.11.0`

如果提示"python不是内部或外部命令"，请参考下面的Python安装步骤。



## 🐍 安装Python

#### 下载Python
1. 访问Python官网：https://www.python.org/downloads/
2. 点击"Download Python 3.11.x"（选择最新稳定版本）
3. 下载Windows安装包（.exe文件）

#### 安装步骤
1. **运行安装程序**
   - 双击下载的.exe文件
   - 以管理员身份运行（推荐）

2. **重要配置选项**
   - ✅ **Add Python to PATH** - 必须勾选，这样可以在命令行中直接使用python命令
   - ✅ **Install for all users** - 推荐勾选（需要管理员权限）

3. **选择安装类型**
   - **Customize installation** - 推荐选择，可以自定义安装路径
   - 在"Optional Features"中确保以下选项被勾选：
     - ✅ py launcher
     - ✅ Associate files with Python
     - ✅ Create shortcuts for installed applications
     - ✅ Add Python to environment variables
     - ✅ Precompile standard library

4. **高级选项**
   - 在"Advanced Options"中：
     - ✅ Install for all users
     - ✅ Add Python to environment variables
     - ✅ Create shortcuts for installed applications
     - ✅ Add Python to PATH
     - ✅ Precompile standard library
     - ✅ Download debugging symbols
     - ✅ Download debug binaries

5. **选择安装路径**
   - 建议使用默认路径：`C:\Program Files\Python311\`
   - 或自定义路径，但避免包含空格和特殊字符

6. **完成安装**
   - 点击"Install"开始安装
   - 等待安装完成
   - 点击"Close"关闭安装程序

#### 验证安装
```cmd
python --version
pip --version
```



### 安装后配置

#### 1. 升级pip（可选）
```cmd
python -m pip install --upgrade pip
```

#### 2. 配置pip镜像源（可选，提升下载速度）
```cmd
# 配置清华大学镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/

# 或配置阿里云镜像
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

#### 3. 验证完整安装
```cmd
python -c "print('Hello, Python!')"
pip list
```

## 📦 安装Poetry

### 方法1: 官方安装脚本（推荐）

#### 使用PowerShell
```powershell
# 以管理员身份运行PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

#### 使用CMD
```cmd
# 以管理员身份运行CMD
curl -sSL https://install.python-poetry.org | python -
```

### 方法2: pip安装
```cmd
pip install poetry
```

### 方法3: 手动安装
```cmd
# 下载安装脚本
curl -O https://install.python-poetry.org

# 运行安装脚本
python install.python-poetry.org
```

### 验证安装
```cmd
poetry --version
```
应该输出类似：`Poetry (version 1.4.0)`

### 添加到PATH（如果需要）

如果Poetry命令无法识别，需要手动添加到PATH：

1. **找到Poetry安装路径**
   ```cmd
   poetry env info --path
   ```

2. **添加到系统PATH**
   - 右键"此电脑" → "属性" → "高级系统设置" → "环境变量"
   - 在"用户变量"中找到"Path"
   - 添加Poetry安装路径（通常是 `%APPDATA%\Python\Scripts`）

3. **重启命令提示符**
   - 关闭所有命令提示符窗口
   - 重新打开命令提示符
   - 验证：`poetry --version`

## ⚙️ 配置Poetry

### 1. 配置虚拟环境位置
```cmd
# 在项目目录内创建虚拟环境（推荐）
poetry config virtualenvs.in-project true

# 或使用全局虚拟环境
poetry config virtualenvs.in-project false
```

### 2. 配置镜像源（提升下载速度）
```cmd
# 配置PyPI镜像（清华大学镜像）
poetry config repositories.pypi https://pypi.tuna.tsinghua.edu.cn/simple/

# 配置PyTorch镜像
poetry config repositories.pytorch https://download.pytorch.org/whl/cu128
```

### 3. 查看配置
```cmd
poetry config --list
```

### 4. 重置配置（如果需要）
```cmd
# 重置所有配置
poetry config --unset virtualenvs.in-project
poetry config --unset repositories.pypi
```

## 🚀 项目部署

### 步骤1: 获取项目

#### 方法1: 使用Git克隆（推荐）
```cmd
# 克隆项目
git clone https://github.com/your-username/textProcess.git

# 进入项目目录
cd textProcess
```

#### 方法2: 从GitHub下载ZIP包
1. 访问项目GitHub页面：https://github.com/your-username/textProcess
2. 点击绿色的"Code"按钮
3. 选择"Download ZIP"
4. 下载完成后解压到本地目录
5. 进入解压后的项目目录：
```cmd
# 进入项目目录
cd textProcess-master
# 或
cd textProcess-main
```

**注意**: 如果使用ZIP包下载，项目目录名可能是 `textProcess-master` 或 `textProcess-main`，请根据实际解压后的目录名调整。

### 步骤2: 安装依赖

#### 安装所有依赖（包括开发依赖）
```cmd
poetry install
```

#### 仅安装生产依赖
```cmd
poetry install --only main
```

#### 安装特定组依赖
```cmd
# 安装开发依赖
poetry install --with dev

# 安装测试依赖
poetry install --with test
```

### 步骤3: 验证安装
```cmd
# 验证Python依赖
poetry run python -c "import fastapi, marker, pytesseract, cv2, PIL, langdetect; print('✅ 所有依赖安装成功')"

# 查看已安装的依赖
poetry show

# 查看依赖树
poetry show --tree
```

### 步骤4: 安装Tesseract OCR

#### 下载安装包
1. 访问：https://github.com/UB-Mannheim/tesseract/wiki
2. 下载Windows安装包（如：`tesseract-ocr-w64-setup-5.3.1.20230401.exe`）
3. 运行安装程序
4. **重要**: 安装时选择中文和英文语言包

#### 配置环境变量
1. 右键"此电脑" → "属性" → "高级系统设置" → "环境变量"
2. 在"系统变量"中找到"Path"
3. 添加Tesseract安装路径（通常是 `C:\Program Files\Tesseract-OCR`）
4. 重启命令提示符

#### 验证安装
```cmd
tesseract --version
```

### 步骤5: 启动服务

#### 开发环境
```cmd
# 方式1: 使用Poetry运行
poetry run python main.py

# 方式2: 激活虚拟环境后运行
poetry shell
python main.py

# 方式3: 使用uvicorn启动（推荐）
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

#### 生产环境
```cmd
# 使用uvicorn启动
poetry run uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4

# 或使用gunicorn（需要安装）
poetry add gunicorn
poetry run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

## 🔧 常用命令

### 虚拟环境管理
```cmd
# 激活虚拟环境
poetry shell

# 退出虚拟环境
exit

# 在虚拟环境中运行命令
poetry run python main.py

# 查看虚拟环境信息
poetry env info
```

### 依赖管理
```cmd
# 添加生产依赖
poetry add package-name

# 添加开发依赖
poetry add --group dev package-name

# 添加可选依赖
poetry add --optional package-name

# 移除依赖
poetry remove package-name

# 更新依赖
poetry update

# 更新特定依赖
poetry update package-name

# 查看依赖
poetry show

# 查看依赖树
poetry show --tree
```

### 项目配置
```cmd
# 查看项目信息
poetry show

# 查看项目配置
poetry config --list

# 导出依赖到requirements.txt
poetry export -f requirements.txt --output requirements.txt

# 检查依赖冲突
poetry check
```

### 脚本运行
```cmd
# 运行自定义脚本
poetry run script-name

# 查看可用脚本
poetry run --help
```

## 📁 项目结构

安装完成后，项目结构如下：

```
textProcess/
├── .venv/                 # 虚拟环境（如果配置为in-project）
├── api/                   # API模块
├── core/                  # 核心转换模块
├── utils/                 # 工具模块
├── static/                # 前端静态文件
├── uploads/               # 上传文件目录
├── outputs/               # 输出文件目录
├── logs/                  # 日志目录
├── docs/                  # 文档目录
├── pyproject.toml         # Poetry配置文件
├── poetry.lock            # 依赖锁定文件
├── main.py                # 应用入口
├── .env                   # 环境变量（需要创建）
└── README.md              # 项目说明
```

## ⚙️ 环境配置

### 创建环境变量文件
在项目根目录创建 `.env` 文件：

```env
# 应用配置
APP_NAME=PDF转Markdown工具
APP_VERSION=1.0.0
DEBUG=false
HOST=0.0.0.0
PORT=8001
WORKERS=4

# 文件配置
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
MAX_FILE_SIZE=100

# GPU配置
CUDA_VISIBLE_DEVICES=0
NUM_DEVICES=1
NUM_WORKERS=4
TORCH_DEVICE=cuda

# 安全配置
CORS_ORIGINS=http://localhost:3000,http://localhost:8001
RATE_LIMIT=100

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 创建启动脚本

#### 开发环境启动脚本 (`start-dev.bat`)
```batch
@echo off
echo 🚀 启动开发环境...
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8001
pause
```

#### 生产环境启动脚本 (`start-prod.bat`)
```batch
@echo off
echo 🚀 启动生产环境...
poetry run uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
pause
```

## 🔧 故障排除

### 常见问题

#### 1. Python安装问题
```cmd
# 如果提示"python不是内部或外部命令"：
# 1. 检查Python是否已安装
where python

# 2. 检查环境变量
echo %PATH%

# 3. 手动添加Python路径
set PATH=%PATH%;C:\Program Files\Python311\;C:\Program Files\Python311\Scripts\

# 4. 或重新安装Python，确保勾选"Add Python to PATH"
```

#### 2. 项目获取问题
```cmd
# 如果Git克隆失败，可以尝试：
# 1. 检查网络连接
# 2. 使用GitHub下载ZIP包
# 3. 检查Git配置
git config --list

# 如果ZIP包解压后找不到项目文件，检查：
# 1. 解压是否完整
# 2. 目录名是否正确
dir
```

#### 3. Poetry命令无法识别
```cmd
# 检查PATH环境变量
echo %PATH%

# 手动添加Poetry路径
set PATH=%PATH%;%APPDATA%\Python\Scripts

# 或重新安装
pip install poetry
```

#### 4. 依赖安装失败
```cmd
# 清理缓存
poetry cache clear --all

# 更新Poetry
poetry self update

# 重新安装依赖
poetry env remove python
poetry install

# 使用国内镜像
poetry config repositories.pypi https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 5. 虚拟环境问题
```cmd
# 删除虚拟环境
poetry env remove python

# 重新创建虚拟环境
poetry install

# 查看虚拟环境信息
poetry env info
```

#### 6. 权限问题
```cmd
# 以管理员身份运行命令提示符
# 右键命令提示符 → "以管理员身份运行"

# 或修改项目目录权限
icacls . /grant Users:F /T
```

#### 7. 端口占用
```cmd
# 查看端口占用
netstat -ano | findstr :8001

# 结束占用进程
taskkill /PID <进程ID> /F

# 或使用其他端口
poetry run uvicorn main:app --port 8002
```

#### 8. Tesseract问题
```cmd
# 检查Tesseract安装
tesseract --version

# 检查环境变量
echo %PATH%

# 手动设置Tesseract路径
set TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
```

### 调试技巧

#### 1. 启用详细输出
```cmd
# 启用Poetry详细输出
poetry install -vvv

# 启用uvicorn详细输出
poetry run uvicorn main:app --log-level debug
```

#### 2. 检查依赖冲突
```cmd
# 检查依赖冲突
poetry check

# 查看依赖树
poetry show --tree
```

#### 3. 清理和重建
```cmd
# 清理所有缓存
poetry cache clear --all

# 删除虚拟环境
poetry env remove python

# 重新安装
poetry install
```

## 📚 最佳实践

### 1. 开发环境

#### 使用虚拟环境
```cmd
# 始终使用Poetry管理虚拟环境
poetry shell
# 或
poetry run python main.py
```

#### 依赖管理
```cmd
# 定期更新依赖
poetry update

# 检查安全漏洞
poetry run safety check

# 锁定依赖版本
poetry lock
```

### 2. 生产环境

#### 安全配置
```cmd
# 禁用调试模式
set DEBUG=false

# 使用强密码
set SECRET_KEY=your-secret-key

# 限制文件上传
set MAX_FILE_SIZE=100
```

#### 性能优化
```cmd
# 使用多进程
poetry run uvicorn main:app --workers 4

# 启用压缩
poetry run uvicorn main:app --workers 4 --compress

# 使用gunicorn（更稳定）
poetry add gunicorn
poetry run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 3. 项目维护

#### 定期维护
```cmd
# 更新Poetry
poetry self update

# 更新依赖
poetry update

# 清理缓存
poetry cache clear --all

# 检查项目状态
poetry check
```

#### 备份和恢复
```cmd
# 导出依赖
poetry export -f requirements.txt --output requirements.txt

# 备份项目
xcopy /E /I textProcess textProcess_backup

# 恢复项目
poetry install
```

## 🆘 获取帮助

### 官方资源
- **Poetry文档**: https://python-poetry.org/docs/
- **Poetry GitHub**: https://github.com/python-poetry/poetry
- **FastAPI文档**: https://fastapi.tiangolo.com/

### 社区支持
- **Stack Overflow**: 搜索 `poetry windows`
- **GitHub Issues**: 项目仓库的Issues页面
- **Discord**: Python社区Discord服务器

### 本地帮助
```cmd
# Poetry帮助
poetry --help
poetry install --help
poetry add --help

# 查看版本信息
poetry --version
python --version
```

## 🚀 快速开始总结

### 完整安装流程

#### 步骤1: 安装Python
```cmd
# 方法1: 使用winget（推荐）
winget install Python.Python.3.11

# 验证安装
python --version
pip --version
```

#### 步骤2: 安装和配置Poetry
```cmd
# 安装Poetry
pip install poetry

# 配置Poetry
poetry config virtualenvs.in-project true

# 配置镜像源（可选，提升下载速度）
poetry config repositories.pypi https://pypi.tuna.tsinghua.edu.cn/simple/

# 验证Poetry安装
poetry --version
```

### 方式一：Git克隆（推荐）
```cmd
# 1. 克隆项目
git clone https://github.com/your-username/textProcess.git
cd textProcess

# 2. 安装依赖
poetry install --only main

# 3. 启动服务
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 方式二：GitHub下载ZIP包
```cmd
# 1. 下载并解压ZIP包
# 从GitHub页面下载ZIP包并解压

# 2. 进入项目目录
cd textProcess-master  # 或 textProcess-main

# 3. 安装依赖
poetry install --only main

# 4. 启动服务
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 访问应用
- **Web界面**: http://localhost:8001
- **API文档**: http://localhost:8001/docs
- **ReDoc文档**: http://localhost:8001/redoc

---

**注意**: 本指南基于Windows 10/11和Poetry 1.4.0+版本编写。如果使用其他版本，某些命令可能需要调整。 
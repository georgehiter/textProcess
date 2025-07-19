# 启动指南

## 快速启动

### 1. 检查依赖

```bash
poetry run python check_deps.py
```

### 2. 检查端口

```bash
poetry run python test_port.py
```

### 3. 启动服务器

```bash
poetry run python main.py
```

**注意**: 服务器运行在8001端口，访问地址为 http://localhost:8001

## 常见问题

### 问题1: 端口被占用
**症状**: 启动时提示端口被占用
**解决**: 
```bash
# 使用其他端口
poetry run uvicorn main:app --port 8002
```

### 问题2: 依赖缺失
**症状**: ImportError
**解决**:
```bash
poetry install
```

### 问题3: 文件缺失
**症状**: FileNotFoundError
**解决**: 检查项目文件是否完整

## 测试步骤

1. **启动服务器**:
   ```bash
   poetry run python main.py
   ```

2. **访问Web界面**:
   - http://localhost:8001 (Web界面 - 自动重定向)
   - http://localhost:8001/static/index.html (直接访问Web界面)
   - http://localhost:8001/docs (API文档)
   - http://localhost:8001/health (健康检查)

## 调试命令

```bash
# 检查Python进程
tasklist | findstr python

# 检查端口占用
netstat -an | findstr :8001

# 检查依赖
poetry show

# 重新安装依赖
poetry install --sync
``` 
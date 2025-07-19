# .gitignore 配置说明

## 概述

`.gitignore` 文件用于告诉Git哪些文件和目录不应该被跟踪和上传到版本控制系统中。

## 主要配置类别

### 1. Python 相关文件
```
__pycache__/          # Python字节码缓存
*.py[cod]             # 编译的Python文件
*.egg-info/           # Python包信息
dist/                 # 分发目录
build/                # 构建目录
```

### 2. 虚拟环境
```
.env                  # 环境变量文件
.venv/                # 虚拟环境目录
venv/                 # 虚拟环境目录
```

### 3. IDE 和编辑器
```
.idea/                # PyCharm配置
.vscode/              # VS Code配置
*.swp                 # Vim临时文件
```

### 4. 项目特定文件

#### 输入文件
```
input/                # 输入文件目录
*.pdf                 # PDF文件
```

#### 输出文件
```
output/               # 输出文件目录
*.md                  # Markdown文件
*.html                # HTML文件
*.json                # JSON文件
```

#### 临时文件
```
temp/                 # 临时文件目录
*.tmp                 # 临时文件
*.temp                # 临时文件
```

#### 日志文件
```
logs/                 # 日志目录
*.log                 # 日志文件
```

### 5. 系统文件
```
.DS_Store             # macOS系统文件
Thumbs.db             # Windows缩略图文件
```

### 6. 配置文件
```
config.json           # 配置文件（可能包含敏感信息）
.env.local            # 本地环境变量
.env.production       # 生产环境变量
```

## 使用说明

### 添加新的忽略规则

1. **忽略特定文件**：
   ```
   filename.txt
   ```

2. **忽略特定类型文件**：
   ```
   *.log
   *.tmp
   ```

3. **忽略目录**：
   ```
   directory/
   ```

4. **忽略特定路径的文件**：
   ```
   path/to/file.txt
   ```

5. **使用通配符**：
   ```
   *.py[cod]          # 忽略.pyc, .pyo, .pyd文件
   ```

### 强制添加被忽略的文件

如果某个文件被 `.gitignore` 忽略，但你想强制添加它：

```bash
git add -f filename.txt
```

### 检查文件是否被忽略

```bash
git check-ignore filename.txt
```

## 注意事项

1. **已跟踪的文件**：如果文件已经被Git跟踪，添加到 `.gitignore` 不会自动停止跟踪
2. **删除已跟踪的文件**：
   ```bash
   git rm --cached filename.txt
   ```
3. **敏感信息**：确保不要将包含密码、API密钥等敏感信息的文件提交到Git
4. **大文件**：避免提交大文件，考虑使用Git LFS

## 常见问题

### Q: 为什么我的文件还是被提交了？
A: 如果文件已经被Git跟踪，需要先删除跟踪：
```bash
git rm --cached filename.txt
git commit -m "Remove tracked file"
```

### Q: 如何忽略所有PDF文件但保留特定PDF？
A: 使用 `!` 符号：
```
*.pdf                 # 忽略所有PDF
!important.pdf        # 但保留important.pdf
```

### Q: 如何查看当前被忽略的文件？
A: 使用以下命令：
```bash
git status --ignored
``` 
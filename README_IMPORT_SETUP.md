# CoachAI 项目导入路径设置指南

## 问题背景

原始项目结构使用 `coding.` 作为导入前缀：
```python
from coding.config import config
from coding.tornado.core.application import create_application
```

期望的导入方式（无 `coding.` 前缀）：
```python
from config import config
from webapp.core.application import create_application
```

## 解决方案

我们采用了组合方案来解决导入路径问题：

### 1. 重命名冲突目录
将 `coding/tornado/` 重命名为 `coding/webapp/`，避免与 Python 的 `tornado` 包冲突。

### 2. 设置 PYTHONPATH
将 `coding/` 目录添加到 Python 路径中，使其成为根包。

### 3. 修复所有导入语句
更新所有文件中的导入语句，移除 `coding.` 前缀。

## 使用方法

### 方法一：使用环境设置脚本（推荐）

```bash
# 设置环境
cd /path/to/coach-ai
source setup_env.sh

# 现在可以直接运行
python -c "from config import config; print(config.APP_ENV)"
python -m main
```

### 方法二：手动设置 PYTHONPATH

```bash
# 临时设置
export PYTHONPATH=/path/to/coach-ai/coding:$PYTHONPATH

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export PYTHONPATH=/path/to/coach-ai/coding:$PYTHONPATH' >> ~/.bashrc
source ~/.bashrc
```

### 方法三：在代码中设置

在 Python 脚本开头添加：
```python
import sys
import os

# 添加 coding 目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
coding_dir = os.path.join(project_root, "coding")
sys.path.insert(0, coding_dir)

# 现在可以直接导入
from config import config
from webapp.core.application import create_application
```

## 新的导入示例

```python
# 配置模块
from config import config, init_config, get_config

# Web应用框架
from webapp.core.application import create_application
from webapp.core.base_handler import BaseHandler
from webapp.core.middleware import MiddlewareManager

# 数据库
from database.connection import get_db_session
from database.models import User, Tenant

# 业务模块
from webapp.modules.auth.services import auth_service
from webapp.modules.tenant.handlers import CreateTenantHandler

# 工具模块
from webapp.utils.jwt_utils import create_jwt_token, verify_jwt_token
from webapp.utils.password_utils import hash_password, verify_password
```

## 项目结构

```
coach-ai/
├── coding/                    # 源代码根目录（已添加到 PYTHONPATH）
│   ├── config/               # 配置模块
│   │   ├── __init__.py
│   │   └── config.py
│   ├── database/             # 数据库模块
│   │   ├── connection.py
│   │   ├── models/
│   │   └── migrations/
│   ├── webapp/               # Web应用框架（原 tornado）
│   │   ├── core/             # 核心框架
│   │   ├── modules/          # 业务模块
│   │   └── utils/            # 工具函数
│   ├── main.py               # 应用入口
│   └── __init__.py
├── setup_env.sh              # 环境设置脚本
├── setup_pythonpath.py       # Python 环境设置
└── README_IMPORT_SETUP.md    # 本文档
```

## 验证测试

运行测试脚本验证导入是否正常工作：

```bash
# 测试所有导入
cd /path/to/coach-ai
python setup_pythonpath.py

# 测试服务器导入
python -c "
import sys
sys.path.insert(0, 'coding')
from main import main
print('✅ 服务器导入成功')
"
```

## 注意事项

1. **命名冲突**：`webapp` 目录原名 `tornado`，为避免与 Python 的 `tornado` 包冲突而重命名。
2. **相对导入**：在模块内部可以使用相对导入，如 `from .services import auth_service`。
3. **第三方包**：确保已安装所有依赖：`pip install -r requirements.txt`
4. **开发环境**：建议使用虚拟环境管理依赖。

## 故障排除

### 问题：ModuleNotFoundError: No module named 'config'
**解决方案**：确保已正确设置 PYTHONPATH：
```bash
export PYTHONPATH=/path/to/coach-ai/coding:$PYTHONPATH
```

### 问题：ModuleNotFoundError: No module named 'webapp'
**解决方案**：检查目录是否存在，确保 `coding/webapp/` 目录存在。

### 问题：ImportError: cannot import name 'create_application'
**解决方案**：检查导入路径是否正确，应为 `from webapp.core.application import create_application`。

## 更新记录

- **2026-03-27**：完成导入路径重构，移除所有 `coding.` 前缀
- **变更内容**：
  - 重命名 `tornado/` 为 `webapp/` 避免命名冲突
  - 更新 75+ 个文件的导入语句
  - 创建环境设置脚本
  - 更新项目文档

现在项目可以使用简洁的导入路径，无需 `coding.` 前缀。
# CoachAI 部署运维指南

## 📋 文档信息

| 项目 | 内容 |
|------|------|
| **文档名称** | CoachAI 部署运维指南 |
| **文档版本** | 1.0.0 |
| **创建日期** | 2026-03-26 |
| **最后更新** | 2026-03-26 |
| **文档状态** | 正式版 |
| **作者** | CoachAI-RD (后端研发专家) |
| **审核人** | 待定 |
| **关联文档** | [技术架构概要设计.md](./CoachAI技术架构概要设计.md) |
| **目标读者** | 运维工程师、DevOps工程师、系统管理员 |

## 🎯 部署目标

### 1.1 部署环境
1. **开发环境**：本地开发，快速迭代
2. **测试环境**：功能测试，集成测试
3. **预发布环境**：生产环境镜像，最终测试
4. **生产环境**：线上服务，高可用部署

### 1.2 部署原则
1. **自动化**：使用CI/CD流水线自动化部署
2. **可重复**：部署过程可重复，结果一致
3. **可回滚**：支持快速回滚到上一个版本
4. **监控告警**：完善的监控和告警机制
5. **代码规范**：部署脚本遵循编码规范，中文注释
6. **开源合规**：确保部署过程符合GPL V3要求

## 🚀 开发环境部署

### 2.1 本地开发环境

#### 2.1.1 环境要求
- **操作系统**：Linux/macOS/Windows WSL2
- **Python**：3.12.0 或更高
- **MySQL**：8.0 或更高
- **Redis**：7.0 或更高（可选）
- **Node.js**：18.0 或更高（前端）

#### 2.1.2 快速启动脚本
```bash
#!/bin/bash
# scripts/setup_dev.sh

set -e

echo "🚀 开始设置CoachAI开发环境..."

# 检查Python版本
echo "📦 检查Python版本..."
python3 --version | grep "3.12" || {
    echo "❌ 需要Python 3.12，当前版本: $(python3 --version)"
    exit 1
}

# 创建虚拟环境
echo "📦 创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "📦 安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 检查MySQL
echo "📦 检查MySQL服务..."
if ! command -v mysql &> /dev/null; then
    echo "⚠️  MySQL未安装，请先安装MySQL 5.8"
    exit 1
fi

# 创建数据库
echo "📦 创建数据库..."
mysql -u root -p -e "
CREATE DATABASE IF NOT EXISTS coachai_dev 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON coachai_dev.* TO 'coachai'@'localhost' IDENTIFIED BY 'coachai123';
FLUSH PRIVILEGES;
"

# 运行数据库迁移
echo "📦 运行数据库迁移..."
alembic upgrade head

# 初始化测试数据
echo "📦 初始化测试数据..."
python scripts/init_test_data.py

# 启动开发服务器
echo "🚀 启动开发服务器..."
echo "后端API: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "前端应用: http://localhost:3000"

python src/main.py --port=8000 --debug
```

#### 2.1.3 Docker开发环境
```dockerfile
# docker-compose.dev.yml
version: '3.8'

services:
  # MySQL数据库
  mysql:
    image: mysql:5.8
    container_name: coachai-mysql-dev
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: coachai_dev
      MYSQL_USER: coachai
      MYSQL_PASSWORD: coachai123
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./config/mysql/my.cnf:/etc/mysql/conf.d/my.cnf
    command: 
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
      - --default-authentication-plugin=mysql_native_password
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 10

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: coachai-redis-dev
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # 后端应用
  backend:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: coachai-backend-dev
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - ENVIRONMENT=development
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_USERNAME=coachai
      - DB_PASSWORD=coachai123
      - DB_DATABASE=coachai_dev
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src
      - ./config:/app/config
      - ./scripts:/app/scripts
    command: >
      sh -c "
        alembic upgrade head &&
        python src/main.py --port=8000 --debug
      "
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 前端应用
  frontend:
    build:
      context: ../coach-ai-frontend
      dockerfile: Dockerfile.dev
    container_name: coachai-frontend-dev
    depends_on:
      - backend
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api/v1
    ports:
      - "3000:3000"
    volumes:
      - ../coach-ai-frontend/src:/app/src
      - ../coach-ai-frontend/public:/app/public
    command: npm run dev

volumes:
  mysql_data:
  redis_data:
```

### 2.2 开发环境配置

#### 2.2.1 环境变量配置
```bash
# .env.development
# 应用配置
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000
WORKERS=1
API_PREFIX=/api/v1

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USERNAME=coachai
DB_PASSWORD=coachai123
DB_DATABASE=coachai_dev
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=5
DB_POOL_RECYCLE=3600
DB_ECHO=false

# Redis配置（可选）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_MAX_CONNECTIONS=20

# 安全配置
SECRET_KEY=development-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
RATE_LIMIT_ENABLED=false

# 日志配置
LOG_LEVEL=DEBUG
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_FILE_PATH=logs/coachai.log
LOG_MAX_FILE_SIZE=10485760
LOG_BACKUP_COUNT=5

# AI服务配置
AI_OCR_MODEL_PATH=/models/ocr
AI_POSE_MODEL_PATH=/models/pose
AI_SPEECH_MODEL_PATH=/models/speech
AI_GPU_ENABLED=false
AI_BATCH_SIZE=1
AI_CONFIDENCE_THRESHOLD=0.5

# WebRTC配置
WEBRTC_STUN_SERVERS=stun:stun.l.google.com:19302,stun:stun1.l.google.com:19302
WEBRTC_TURN_SERVERS=[]
WEBRTC_VIDEO_BITRATE=2000000
WEBRTC_AUDIO_BITRATE=128000
WEBRTC_MAX_FRAME_RATE=30

# 文件存储配置
STORAGE_TYPE=local
STORAGE_LOCAL_PATH=./uploads
STORAGE_MAX_FILE_SIZE=10485760  # 10MB
STORAGE_ALLOWED_EXTENSIONS=.jpg,.jpeg,.png,.pdf,.mp4,.webm
```

#### 2.2.2 数据库迁移配置
```python
# alembic.ini
# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = src/database/migrations

# template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone = Asia/Shanghai

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses
# os.pathsep. If this key is omitted entirely, it falls back to the legacy
# behavior of splitting on spaces and/or commas.
# Valid values for version_path_separator are:
#
# version_path_separator = :
# version_path_separator = ;
# version_path_separator = space
version_path_separator = os

# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = mysql+pymysql://coachai:coachai123@localhost:3306/coachai_dev

[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the console_scripts runner, against the "ruff" entrypoint
# hooks = ruff
# ruff.type = console_scripts
# ruff.entrypoint = ruff
# ruff.options = --fix REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

## 🏭 生产环境部署

### 3.1 生产环境架构

#### 3.1.1 架构图
```
┌─────────────────────────────────────────────────────────┐
│                   负载均衡层 (Nginx/HAProxy)              │
│                   HTTPS终止，请求分发                     │
└──────────────────────────┬──────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐
│  应用服务器1   │  │  应用服务器2   │  │  应用服务器3   │
│  (Tornado)    │  │  (Tornado)    │  │  (Tornado)    │
└───────┬──────┘  └───────┬──────┘  └───────┬──────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐
│  MySQL主库    │  │  MySQL从库1   │  │  MySQL从库2   │
│  (读写)       │  │  (只读)       │  │  (只读)       │
└───────┬──────┘  └──────────────┘  └──────────────┘
        │
┌───────▼──────┐
│  Redis集群    │
│  (缓存/会话)   │
└──────────────┘
```

#### 3.1.2 服务器规格建议
- **应用服务器**：4核8GB内存，SSD硬盘
- **数据库服务器**：8核16GB内存，SSD硬盘，RAID 10
- **缓存服务器**：4核8GB内存，SSD硬盘
- **负载均衡器**：4核8GB内存

### 3.2 Docker生产部署

#### 3.2.1 Docker生产配置
```dockerfile
# Dockerfile
# 构建阶段
FROM python:3.12-slim as builder

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --user --no-cache-dir -r requirements.txt

# 运行阶段
FROM python:3.12-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libmariadb3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN groupadd -r coachai && useradd -r -g coachai coachai

# 从构建阶段复制Python依赖
COPY --from=builder /root/.local /root/.local

# 复制应用代码
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY alembic.ini .
COPY pyproject.toml .

# 设置权限
RUN chown -R coachai:coachai /app
USER coachai

# 设置环境变量
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app/src:$PYTHONPATH
ENV PYTHONUNBUFFERED=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "src/main.py", "--port=8000"]
```

#### 3.2.2 Docker Compose生产配置
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  # Nginx反向代理
  nginx:
    image: nginx:alpine
    container_name: coachai-nginx-prod
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./config/nginx/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - backend
    networks:
      - coachai-network
    restart: unless-stopped

  # 后端应用
  backend:
    build:
      context: .
      dockerfile: Docker
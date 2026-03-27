# CoachAI 部署指南

## 概述

本文档提供CoachAI项目的完整部署指南，涵盖开发环境、测试环境和生产环境的部署步骤。

## 环境要求

### 系统要求
- **操作系统**: Linux (Ubuntu 20.04+ / CentOS 8+), macOS 10.15+, Windows 10+ (WSL2)
- **内存**: 最低 4GB，推荐 8GB+
- **磁盘空间**: 最低 10GB，推荐 20GB+
- **网络**: 稳定的网络连接

### 软件要求
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+
- **Python**: 3.9+ (仅开发环境需要)

## 快速开始

### 1. 获取代码
```bash
# 克隆项目
git clone https://github.com/baofengbaofeng/coach-ai.git
cd coach-ai

# 切换到稳定分支
git checkout master
```

### 2. 环境配置
```bash
# 复制环境配置文件
cp .env.example .env

# 编辑环境配置
vim .env  # 或使用其他编辑器
```

### 3. 一键部署
```bash
# 开发环境部署
./scripts/deploy.sh dev -b -u

# 或使用完整命令
./scripts/deploy.sh dev --build --up --migrate
```

### 4. 验证部署
```bash
# 检查服务状态
./scripts/deploy.sh -s

# 健康检查
curl http://localhost:8888/api/health

# 查看日志
./scripts/deploy.sh -l
```

## 详细部署步骤

### 开发环境部署

#### 选项1：使用Docker（推荐）
```bash
# 1. 启动所有服务
./scripts/deploy.sh dev -b -u

# 2. 运行数据库迁移
./scripts/deploy.sh dev -m

# 3. 运行测试
./scripts/deploy.sh dev -t

# 4. 查看服务状态
./scripts/deploy.sh dev -s
```

#### 选项2：本地开发环境
```bash
# 1. 设置开发环境
./scripts/setup_environment.sh --all

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 启动开发服务器
./scripts/setup_environment.sh --server

# 4. 运行测试
./scripts/setup_environment.sh --test
```

### 测试环境部署

```bash
# 1. 创建测试环境配置
cp .env.example .env.testing
# 编辑 .env.testing 文件，配置测试环境参数

# 2. 部署测试环境
./scripts/deploy.sh testing -b -u -m

# 3. 运行集成测试
./scripts/deploy.sh testing -t

# 4. 备份数据库
./scripts/deploy.sh testing --backup
```

### 生产环境部署

#### 准备工作
1. **服务器准备**
   - 准备Linux服务器（推荐Ubuntu 22.04 LTS）
   - 配置防火墙（开放80、443、8888端口）
   - 配置域名和SSL证书

2. **环境配置**
   ```bash
   # 创建生产环境配置
   cp .env.example .env.production
   
   # 编辑生产环境配置
   vim .env.production
   
   # 重要：修改所有安全相关配置
   # - APP_SECRET_KEY
   # - JWT_SECRET_KEY
   # - DB_PASSWORD
   # - REDIS_PASSWORD
   # - COOKIE_SECRET
   ```

3. **安全配置**
   ```bash
   # 生成强密码
   openssl rand -base64 32
   
   # 生成JWT密钥
   openssl rand -hex 32
   ```

#### 部署步骤
```bash
# 1. 备份现有数据库（如果有）
./scripts/deploy.sh production --backup

# 2. 构建并启动服务
./scripts/deploy.sh production -b -u -m

# 3. 验证部署
./scripts/deploy.sh production -t

# 4. 监控服务状态
./scripts/deploy.sh production -s
```

#### 生产环境优化
```bash
# 1. 启用HTTPS（配置Nginx）
# 编辑 deploy/nginx/nginx.conf
# 配置SSL证书和反向代理

# 2. 启用监控
./scripts/deploy.sh production --monitor

# 3. 配置日志轮转
# 编辑 deploy/config/logrotate.conf

# 4. 配置备份策略
# 编辑 deploy/scripts/backup.sh
```

## 环境配置详解

### 基础配置
```env
# 应用基础配置
APP_ENV=production                    # 环境: development, testing, production
APP_DEBUG=false                       # 生产环境必须设为false
APP_PORT=8888                         # 应用端口
APP_HOST=0.0.0.0                      # 绑定地址
APP_SECRET_KEY=your-secret-key-here   # 必须修改为强密码
```

### 数据库配置
```env
# MySQL数据库配置
DB_HOST=localhost                     # 数据库主机
DB_PORT=3306                          # 数据库端口
DB_NAME=coach_ai                      # 数据库名称
DB_USER=coach_ai_user                 # 数据库用户
DB_PASSWORD=strong-password-here      # 必须修改为强密码
DB_CHARSET=utf8mb4                    # 字符集

# 连接池配置
DB_POOL_SIZE=20                       # 生产环境建议20-50
DB_MAX_OVERFLOW=40                    # 最大溢出连接数
DB_POOL_RECYCLE=3600                  # 连接回收时间(秒)
DB_POOL_PRE_PING=true                 # 连接预检
```

### Redis配置
```env
# Redis缓存配置
REDIS_HOST=localhost                  # Redis主机
REDIS_PORT=6379                       # Redis端口
REDIS_PASSWORD=redis-password-here    # 必须修改为强密码
REDIS_DB=0                            # Redis数据库
REDIS_MAX_CONNECTIONS=50              # 最大连接数
```

### JWT配置
```env
# JWT认证配置
JWT_SECRET_KEY=jwt-secret-key-here    # 必须修改为强密码
JWT_ALGORITHM=HS256                   # JWT算法
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30    # 访问令牌过期时间
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7       # 刷新令牌过期时间
```

### 安全配置
```env
# 安全配置
CORS_ORIGINS=https://your-domain.com  # 生产环境限制来源
RATE_LIMIT_ENABLED=true               # 启用速率限制
RATE_LIMIT_DEFAULT=100/hour           # 默认速率限制
MAX_REQUEST_BODY_SIZE=10485760        # 最大请求体大小(10MB)
```

## Docker部署详解

### Docker Compose服务

#### 数据库服务 (db)
```yaml
db:
  image: mysql:8.0
  container_name: coach-ai-db
  restart: unless-stopped
  environment:
    MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
    MYSQL_DATABASE: ${DB_NAME}
    MYSQL_USER: ${DB_USER}
    MYSQL_PASSWORD: ${DB_PASSWORD}
  ports:
    - "${DB_PORT}:3306"
  volumes:
    - db_data:/var/lib/mysql
  healthcheck:
    test: ["CMD", "mysqladmin", "ping"]
```

#### Redis服务 (redis)
```yaml
redis:
  image: redis:7-alpine
  container_name: coach-ai-redis
  restart: unless-stopped
  ports:
    - "${REDIS_PORT}:6379"
  volumes:
    - redis_data:/data
  command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
  healthcheck:
    test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
```

#### 应用服务 (app)
```yaml
app:
  build:
    context: .
    dockerfile: Dockerfile
  container_name: coach-ai-app
  restart: unless-stopped
  depends_on:
    db:
      condition: service_healthy
    redis:
      condition: service_healthy
  environment:
    # 所有环境变量
  ports:
    - "${APP_PORT}:8888"
  volumes:
    - app_logs:/var/log/coach-ai
    - app_uploads:/app/uploads
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8888/api/health"]
```

#### Nginx服务 (nginx, 可选)
```yaml
nginx:
  image: nginx:alpine
  container_name: coach-ai-nginx
  restart: unless-stopped
  depends_on:
    - app
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./deploy/nginx/nginx.conf:/etc/nginx/nginx.conf
    - ./deploy/nginx/ssl:/etc/nginx/ssl
```

### Dockerfile详解

```dockerfile
# 构建阶段
FROM python:3.9-slim as builder

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc g++ libmariadb-dev curl

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 运行阶段
FROM python:3.9-slim

# 创建非root用户
RUN groupadd -r coachai && useradd -r -g coachai coachai

# 创建目录并设置权限
RUN mkdir -p /app/uploads /var/log/coach-ai && \
    chown -R coachai:coachai /app /var/log/coach-ai

# 复制应用代码和依赖
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

# 切换到非root用户
USER coachai

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8888/api/health || exit 1

# 启动命令
CMD ["python", "src/main.py"]
```

## 数据库管理

### 初始化数据库
```bash
# 自动初始化（推荐）
./scripts/deploy.sh dev -m

# 手动初始化
docker-compose exec db mysql -u root -p
# 执行SQL脚本
```

### 备份数据库
```bash
# 自动备份
./scripts/deploy.sh production --backup

# 手动备份
docker-compose exec db mysqldump \
  -u ${DB_USER} \
  -p${DB_PASSWORD} \
  ${DB_NAME} > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 恢复数据库
```bash
# 恢复备份
./scripts/deploy.sh production --restore backup_file.sql

# 手动恢复
docker-compose exec -T db mysql \
  -u ${DB_USER} \
  -p${DB_PASSWORD} \
  ${DB_NAME} < backup_file.sql
```

### 数据库迁移
```bash
# 运行迁移
./scripts/deploy.sh production -m

# 查看迁移状态
docker-compose exec app python -c "
from src.infrastructure.db.connection import init_database
from src.infrastructure.db.migrations import get_migration_status

db_manager = init_database()
status = get_migration_status(db_manager)
print(status)
"
```

## 监控和日志

### 服务监控
```bash
# 查看服务状态
./scripts/deploy.sh -s

# 查看容器资源使用
docker stats

# 查看服务日志
./scripts/deploy.sh -l

# 查看特定服务日志
docker-compose logs -f app
docker-compose logs -f db
docker-compose logs -f redis
```

### 启用监控服务
```bash
# 启动Grafana监控
./scripts/deploy.sh production --monitor

# 访问监控面板
# Grafana: http://localhost:3000
# 用户名: admin
# 密码: ${GRAFANA_PASSWORD}
```

### 日志管理
```bash
# 查看应用日志
tail -f /var/log/coach-ai/app.log

# 查看Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 日志轮转配置
# 编辑: deploy/config/logrotate.conf
```

## 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查数据库服务状态
docker-compose ps db

# 检查数据库日志
docker-compose logs db

# 测试数据库连接
docker-compose exec db mysql -u root -p -e "SELECT 1"
```

#### 2. Redis连接失败
```bash
# 检查Redis服务状态
docker-compose ps redis

# 测试Redis连接
docker-compose exec redis redis-cli -a ${REDIS_PASSWORD} ping
```

#### 3. 应用启动失败
```bash
# 查看应用日志
docker-compose logs app

# 检查环境变量
docker-compose exec app env | grep DB_

# 手动启动应用调试
docker-compose exec app python src/main.py
```

#### 4. 端口冲突
```bash
# 检查端口占用
netstat -tulpn | grep :8888

# 修改端口配置
# 编辑 .env 文件，修改 APP_PORT
```

### 性能优化

#### 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_exercises_user_date ON exercise_records(user_id, created_at);

-- 优化查询
EXPLAIN SELECT * FROM tasks WHERE status = 'pending';
```

#### Redis优化
```bash
# 监控Redis性能
docker-compose exec redis redis-cli -a ${REDIS_PASSWORD} info

# 优化内存配置
# 编辑 .env 文件，调整 REDIS_MAX_CONNECTIONS
```

#### 应用优化
```python
# 调整连接池大小
DB_POOL_SIZE = 50
DB_MAX_OVERFLOW = 100

# 启用查询缓存
CACHE_DEFAULT_TIMEOUT = 300
```

## 升级和维护

### 版本升级
```bash
# 1. 备份当前版本
git tag v1.0.0-current
./scripts/deploy.sh production --backup

# 2. 拉取新版本
git pull origin master

# 3. 重建服务
./scripts/deploy.sh production -b -u -m

# 4. 验证升级
./scripts/deploy.sh production -t
```

### 日常维护
```bash
# 清理Docker资源
docker system prune -f
docker volume prune -f

# 更新依赖
pip install -r requirements.txt --upgrade

# 运行测试
./scripts/run_tests.py

# 检查安全更新
docker scan coach-ai-app
```

### 灾难恢复
```bash
# 1. 停止所有服务
./scripts/deploy.sh production --down

# 2. 恢复数据库备份
./scripts/deploy.sh production --restore latest_backup.sql

# 3. 启动服务
./scripts/deploy.sh production -u

# 4. 验证恢复
./scripts/deploy.sh production -t
```

## 安全最佳实践

### 1. 密码安全
- 使用强密码生成器
- 定期更换密码
- 不要将密码提交到版本控制

### 2. 网络安全
- 启用防火墙
- 使用HTTPS
- 限制访问IP

### 3. 容器安全
- 使用非root用户运行容器
- 定期更新基础镜像
- 扫描镜像漏洞

### 4. 数据安全
- 定期备份数据
- 加密敏感数据
- 实施访问控制

## 附录

### 常用命令速查

```bash
# 开发环境
./scripts/setup_environment.sh --all      # 完整设置
./scripts/setup_environment.sh --server   # 启动服务器
./scripts/setup_environment.sh --test     # 运行测试

# 部署命令
./scripts/deploy.sh dev -b -u -m         # 开发环境部署
./scripts/deploy.sh testing -b -u        # 测试环境部署
./scripts/deploy.sh production -b -u -m  # 生产环境部署

# 管理命令
./scripts/deploy.sh -s                   # 查看状态
./scripts/deploy.sh -l                   # 查看日志
./scripts/deploy.sh --backup             # 备份数据库
./scripts/deploy.sh --restore file.sql   # 恢复数据库

# 测试命令
./scripts/run_tests.py                   # 运行所有测试
python -m pytest tests/ -v               # 运行特定测试
```

### 配置文件示例
完整的配置文件示例请参考 `.env.example` 文件。

### 技术支持
- GitHub Issues: https://github.com/baofengbaofeng/coach-ai/issues
- 文档: https://github.com/baofengbaofeng/coach-ai/docs
- 邮件: team@coach-ai.com

---

**最后更新**: 2026-03-27  
**版本**: 1.0.0  
**作者**: CoachAI Team
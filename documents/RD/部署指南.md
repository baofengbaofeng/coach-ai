# CoachAI 部署指南

## 概述

本文档提供CoachAI项目的部署指南，包括开发环境搭建、测试环境配置和生产环境部署。

## 目录结构

```
deploy/
├── docker/                 # Docker配置
│   ├── Dockerfile         # Docker镜像构建文件
│   └── docker-compose.yml # Docker Compose配置
├── scripts/               # 部署脚本
│   └── deploy.sh         # 自动化部署脚本
├── config/                # 环境配置
│   ├── development.env   # 开发环境配置
│   ├── testing.env       # 测试环境配置
│   └── production.env    # 生产环境配置
└── README.md             # 部署文档
```

## 环境要求

### 开发环境
- Docker 20.10+
- Docker Compose 2.0+
- Git
- MySQL 8.0+ (可选，可使用Docker)
- Redis 6.0+ (可选，可使用Docker)
- RabbitMQ 3.8+ (可选，可使用Docker)

### 生产环境
- Linux服务器 (Ubuntu 20.04+ / CentOS 8+)
- Docker 20.10+
- Docker Compose 2.0+
- 至少2GB RAM
- 至少10GB磁盘空间
- 域名和SSL证书（推荐）

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd coach-ai
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑环境变量
vim .env
```

### 3. 使用Docker Compose启动（推荐）

```bash
# 启动所有服务
cd deploy/docker
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app
```

### 4. 使用部署脚本

```bash
# 给予执行权限
chmod +x deploy/scripts/deploy.sh

# 开发环境部署
./deploy/scripts/deploy.sh -e development --build --migrate --seed

# 生产环境部署
./deploy/scripts/deploy.sh -e production --build --migrate
```

## 详细部署步骤

### 开发环境部署

#### 方法一：使用Docker Compose

1. **启动基础服务**：
   ```bash
   # 只启动数据库、Redis和RabbitMQ
   docker-compose up -d db redis rabbitmq
   ```

2. **初始化数据库**：
   ```bash
   # 等待数据库就绪
   sleep 10
   
   # 创建数据库（如果不存在）
   docker-compose exec db mysql -u root -p${DB_ROOT_PASSWORD} -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME};"
   
   # 运行迁移
   docker-compose exec app python -m database.migration_manager upgrade
   
   # 运行种子
   docker-compose exec app python -m database.seeds.initial_data
   ```

3. **启动应用**：
   ```bash
   docker-compose up -d app
   ```

4. **访问应用**：
   - 应用: http://localhost:8888
   - 健康检查: http://localhost:8888/api/health
   - PHPMyAdmin: http://localhost:8080
   - RabbitMQ管理: http://localhost:15672 (guest/guest)

#### 方法二：本地开发

1. **安装Python依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **配置本地服务**：
   - 启动MySQL服务
   - 启动Redis服务
   - 启动RabbitMQ服务

3. **运行应用**：
   ```bash
   python code/main.py
   ```

### 测试环境部署

1. **准备测试环境**：
   ```bash
   # 使用测试配置
   export APP_ENV=testing
   
   # 或复制测试环境配置
   cp deploy/config/testing.env .env.testing
   ```

2. **运行测试**：
   ```bash
   # 运行所有测试
   pytest
   
   # 运行集成测试
   pytest tests/integration/ -v
   
   # 生成测试报告
   pytest --cov=code --cov-report=html
   ```

3. **测试环境验证**：
   ```bash
   # 启动测试环境服务
   ./deploy/scripts/deploy.sh -e testing --build --migrate --seed
   
   # 运行API测试
   python -m pytest tests/integration/test_api_auth.py -v
   ```

### 生产环境部署

#### 服务器准备

1. **系统更新**：
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **安装Docker**：
   ```bash
   # Ubuntu
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # 添加用户到docker组
   sudo usermod -aG docker $USER
   ```

3. **安装Docker Compose**：
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

#### 应用部署

1. **克隆项目**：
   ```bash
   git clone <repository-url> /opt/coach-ai
   cd /opt/coach-ai
   ```

2. **配置生产环境**：
   ```bash
   # 复制生产环境配置
   cp deploy/config/production.env .env
   
   # 编辑配置文件，修改所有密码和密钥
   vim .env
   ```

3. **首次部署**：
   ```bash
   # 备份现有数据（如果有）
   ./deploy/scripts/deploy.sh -e production --stop
   
   # 完整部署
   ./deploy/scripts/deploy.sh -e production --build --migrate --seed
   ```

4. **配置SSL（可选）**：
   ```bash
   # 使用Let's Encrypt获取证书
   sudo apt install certbot python3-certbot-nginx
   sudo certbot certonly --nginx -d yourdomain.com
   
   # 配置Nginx SSL
   # 参考: deploy/docker/nginx/ssl.conf
   ```

#### 监控和维护

1. **查看服务状态**：
   ```bash
   ./deploy/scripts/deploy.sh --status
   ```

2. **查看日志**：
   ```bash
   ./deploy/scripts/deploy.sh --logs
   
   # 或直接查看
   docker-compose logs -f --tail=100
   ```

3. **备份数据库**：
   ```bash
   # 手动备份
   ./deploy/scripts/deploy.sh -e production --backup
   
   # 设置定时备份（crontab）
   0 2 * * * cd /opt/coach-ai && ./deploy/scripts/deploy.sh -e production --backup
   ```

4. **更新应用**：
   ```bash
   # 拉取最新代码
   git pull origin main
   
   # 重新部署
   ./deploy/scripts/deploy.sh -e production --build --migrate --restart
   ```

## 配置说明

### 环境变量

关键环境变量说明：

| 变量 | 说明 | 默认值 | 必需 |
|------|------|--------|------|
| APP_ENV | 应用环境 | development | 是 |
| APP_SECRET_KEY | 应用密钥 | - | 是 |
| JWT_SECRET_KEY | JWT密钥 | - | 是 |
| DB_PASSWORD | 数据库密码 | - | 是 |
| REDIS_PASSWORD | Redis密码 | - | 生产环境必需 |
| RABBITMQ_PASSWORD | RabbitMQ密码 | - | 生产环境必需 |

### 安全配置

1. **密码要求**：
   - 使用强密码（至少12位，包含大小写字母、数字、特殊字符）
   - 不同服务使用不同密码
   - 定期更换密码

2. **密钥管理**：
   ```bash
   # 生成随机密钥
   openssl rand -hex 32
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **防火墙配置**：
   ```bash
   # 只开放必要端口
   sudo ufw allow 22/tcp      # SSH
   sudo ufw allow 80/tcp      # HTTP
   sudo ufw allow 443/tcp     # HTTPS
   sudo ufw allow 8000/tcp    # 应用端口（如果需要）
   sudo ufw enable
   ```

### 性能优化

1. **数据库优化**：
   ```sql
   -- 添加索引
   CREATE INDEX idx_users_email ON users(email);
   CREATE INDEX idx_users_username ON users(username);
   
   -- 定期优化表
   OPTIMIZE TABLE users;
   ```

2. **Redis优化**：
   ```bash
   # 配置Redis内存策略
   maxmemory 1gb
   maxmemory-policy allkeys-lru
   ```

3. **应用优化**：
   ```yaml
   # docker-compose.yml
   app:
     deploy:
       resources:
         limits:
           cpus: '2'
           memory: 2G
   ```

## 故障排除

### 常见问题

#### 1. 数据库连接失败

**症状**：应用启动时提示数据库连接错误

**解决**：
```bash
# 检查数据库服务状态
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 测试数据库连接
docker-compose exec db mysql -u ${DB_USER} -p${DB_PASSWORD} -e "SELECT 1;"
```

#### 2. 端口冲突

**症状**：服务启动失败，提示端口已被占用

**解决**：
```bash
# 查看占用端口的进程
sudo lsof -i :8888

# 修改docker-compose.yml中的端口映射
# 或停止占用端口的服务
```

#### 3. 内存不足

**症状**：容器频繁重启，日志显示内存错误

**解决**：
```bash
# 查看内存使用
docker stats

# 增加内存限制
# 在docker-compose.yml中调整resources.limits.memory
```

#### 4. 迁移失败

**症状**：数据库迁移执行失败

**解决**：
```bash
# 查看迁移状态
docker-compose exec app python -m database.migration_manager status

# 回滚迁移
docker-compose exec app python -m database.migration_manager downgrade -1

# 手动修复后重新迁移
docker-compose exec app python -m database.migration_manager upgrade
```

### 日志分析

日志文件位置：
- 应用日志：`logs/app_YYYY-MM-DD.log`
- Nginx日志：`/var/log/nginx/`（如果使用Nginx）
- Docker日志：`docker-compose logs <service>`

关键日志信息：
- `ERROR`：需要立即处理的错误
- `WARNING`：需要注意的警告信息
- `INFO`：正常操作信息
- `DEBUG`：调试信息（开发环境）

## 监控和告警

### 健康检查

应用提供健康检查端点：
- `GET /api/health` - 应用健康状态
- `GET /api/health/db` - 数据库健康状态
- `GET /api/health/redis` - Redis健康状态

### 监控工具

推荐监控方案：

1. **Docker监控**：
   ```bash
   # 使用cAdvisor
   docker run -d \
     --name=cadvisor \
     --restart=always \
     -p 8080:8080 \
     -v /:/rootfs:ro \
     -v /var/run:/var/run:ro \
     -v /sys:/sys:ro \
     -v /var/lib/docker/:/var/lib/docker:ro \
     google/cadvisor:latest
   ```

2. **应用监控**：
   ```bash
   # 使用Prometheus + Grafana
   # 参考: deploy/monitoring/prometheus.yml
   ```

3. **日志收集**：
   ```bash
   # 使用ELK Stack或Loki
   # 参考: deploy/logging/
   ```

### 告警配置

设置基础告警：
- 服务宕机超过5分钟
- 内存使用超过80%
- 磁盘使用超过85%
- 错误日志频繁出现

## 备份和恢复

### 备份策略

1. **数据库备份**：
   ```bash
   # 每日全量备份
   ./deploy/scripts/deploy.sh --backup
   
   # 保留30天备份
   ```

2. **文件备份**：
   ```bash
   # 备份上传文件
   tar -czf backup_uploads_$(date +%Y%m%d).tar.gz uploads/
   
   # 备份配置文件
   tar -czf backup_config_$(date +%Y%m%d).tar.gz .env deploy/config/
   ```

3. **Docker卷备份**：
   ```bash
   # 备份Docker卷
   docker run --rm -v coachai_db_data:/volume -v $(pwd)/backup:/backup alpine \
     tar -czf /backup/db_data_$(date +%Y%m%d).tar.gz -C /volume ./
   ```

### 恢复步骤

1. **停止服务**：
   ```bash
   ./deploy/scripts/deploy.sh --stop
   ```

2. **恢复数据库**：
   ```bash
   # 解压备份文件
   gunzip backup_20240101.sql.gz
   
   # 恢复数据库
   docker-compose exec -T db mysql -u ${DB_USER} -p${DB_PASSWORD} ${DB_NAME} < backup_20240101.sql
   ```

3. **恢复文件**：
   ```bash
   # 恢复上传文件
   tar -xzf backup_uploads_20240101.tar.gz
   
   # 恢复配置文件
   tar -xzf backup_config_20240101.tar.gz
   ```

4. **启动服务**：
   ```bash
   ./deploy/scripts/deploy.sh --restart
   ```

## 扩展和定制

### 添加新服务

1. **在docker-compose.yml中添加服务**：
   ```yaml
   new-service:
     image: service:latest
     environment:
       KEY: value
     networks:
       - coachai-network
   ```

2. **更新应用配置**：
   ```python
   # 在config.py中添加配置
   NEW_SERVICE_HOST = os.getenv("NEW_SERVICE_HOST", "new-service")
   NEW_SERVICE_PORT = int(os.getenv("NEW_SERVICE_PORT", "8080"))
   ```

### 自定义部署

1. **使用不同数据库**：
   ```yaml
   # 修改docker-compose.yml中的db服务
   db:
     image: postgres:14  # 改为PostgreSQL
     environment:
       POSTGRES_DB: ${DB_NAME}
       POSTGRES_USER: ${DB_USER}
       POSTGRES_PASSWORD: ${DB_PASSWORD}
   ```

2. **添加负载均衡**：
   ```yaml
   # 添加多个应用实例
   app:
     deploy:
       replicas: 3
   
   # 添加负载均衡器
   load-balancer:
     image: nginx:alpine
     ports:
       - "80:80"
     depends_on:
       - app
   ```

## 支持

### 获取帮助

- 查看日志：`./deploy/scripts/deploy.sh --logs`
- 检查状态：`./deploy/scripts/deploy.sh --status`
- 文档：查看项目README.md和本文件

### 报告问题

遇到问题时，请提供：
1. 环境信息（APP_ENV, Docker版本等）
2. 错误日志
3. 复现步骤
4. 期望行为

### 更新文档

本文档随项目更新，请定期查看最新版本。
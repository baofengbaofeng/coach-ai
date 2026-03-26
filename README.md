# CoachAI - AI教练平台

CoachAI是一个基于人工智能的教练平台，提供个性化的教练服务和智能分析。

## 项目架构

### 技术栈
- **后端框架**: Python + Tornado
- **数据库**: MySQL 5.8+（多租户数据隔离）
- **缓存**: Redis
- **消息队列**: RabbitMQ（事件驱动架构）
- **前端**: Vue 3纯脚本（code/web/目录）

### 项目结构
```
coach-ai/
├── code/                     # 源代码目录（按DDD架构）
│   ├── main.py              # 应用入口
│   ├── config.py            # 配置文件
│   ├── tornado/             # Tornado后端核心
│   │   ├── core/           # 核心基础（中间件/异常/认证）
│   │   ├── modules/        # 按业务拆分模块（DDD领域）
│   │   ├── infrastructure/ # 基础设施层
│   │   └── utils/          # 工具类
│   ├── database/           # 数据库相关
│   └── web/                # 前端代码（Vue 3纯脚本）
├── tests/                   # 测试目录
├── deploy/                  # 部署配置
├── docs/                   # 文档目录
├── requirements.txt        # Python依赖
├── .env.example           # 环境变量示例
├── setup.py              # 项目安装配置
└── README.md             # 项目说明
```

## 编码规范

### 语言要求
1. **代码注释**: 必须使用中文
2. **日志输出**: 必须使用英文（禁止中文日志）
3. **异常消息**: 必须使用英文（禁止中文异常）
4. **文档编写**: 技术文档使用中文

### 代码风格
- 遵循PEP 8规范
- 使用类型注解
- 模块化设计，高内聚低耦合
- 统一的错误处理机制

## 快速开始

### 环境要求
- Python 3.8+
- MySQL 5.8+
- Redis 6.0+
- RabbitMQ 3.8+

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd coach-ai
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑.env文件，配置数据库、Redis等连接信息
   ```

5. **初始化数据库**
   ```bash
   # 创建数据库
   mysql -u root -p -e "CREATE DATABASE coach_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   
   # 创建用户（根据.env配置）
   mysql -u root -p -e "CREATE USER 'coach_ai_user'@'localhost' IDENTIFIED BY 'your_password';"
   mysql -u root -p -e "GRANT ALL PRIVILEGES ON coach_ai.* TO 'coach_ai_user'@'localhost';"
   mysql -u root -p -e "FLUSH PRIVILEGES;"
   ```

6. **启动服务**
   ```bash
   python code/main.py
   ```

7. **验证服务**
   ```bash
   curl http://localhost:8888/api/health
   ```

## 开发指南

### 项目结构说明

#### 核心模块 (tornado/core/)
- **base_handler.py**: 基础Handler类，所有Handler的基类
- **exceptions.py**: 自定义异常类
- **error_handler.py**: 统一错误处理器
- **middleware.py**: 中间件（日志、租户、CORS等）
- **application.py**: 应用工厂，创建Tornado应用实例

#### 数据库模块 (database/)
- **connection.py**: 数据库连接管理器，支持多租户
- **redis_client.py**: Redis客户端管理器

#### 工具模块 (tornado/utils/)
- **jwt_utils.py**: JWT令牌工具
- **password_utils.py**: 密码哈希和验证工具

#### 业务模块 (tornado/modules/)
- 按DDD领域划分的业务模块（待实现）

#### 基础设施 (tornado/infrastructure/)
- 外部服务集成、消息队列等（待实现）

### 创建新模块

1. **在modules目录下创建新模块**
   ```bash
   mkdir -p code/tornado/modules/auth
   ```

2. **创建模块文件**
   ```python
   # code/tornado/modules/auth/__init__.py
   from tornado.web import url
   
   def get_routes():
       from .handlers import LoginHandler, RegisterHandler
       
       return [
           url(r"/api/auth/login", LoginHandler, name="auth_login"),
           url(r"/api/auth/register", RegisterHandler, name="auth_register"),
       ]
   ```

3. **注册路由**
   在`code/tornado/modules/__init__.py`中导入新模块的路由

### 测试
项目使用pytest进行测试：
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/unit/

# 生成测试覆盖率报告
pytest --cov=code tests/
```

## 部署

### 生产环境配置
1. 设置`APP_ENV=production`
2. 配置强密码和密钥
3. 启用HTTPS
4. 配置防火墙规则
5. 设置监控和告警

### Docker部署
```dockerfile
# Dockerfile示例
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "code/main.py"]
```

## API文档

### 健康检查
- `GET /api/health` - 服务健康状态
- `GET /api/health/db` - 数据库健康状态
- `GET /api/health/redis` - Redis健康状态

### 响应格式

#### 成功响应
```json
{
  "success": true,
  "message": "Success",
  "data": {...},
  "timestamp": 1234567890.123
}
```

#### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message",
    "details": {...}
  },
  "timestamp": 1234567890.123
}
```

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 查看LICENSE文件了解详情

## 联系方式

- 项目维护: team@coach-ai.com
- 问题反馈: [GitHub Issues](<repository-url>/issues)

## 更新日志

### v1.0.0 (2026-03-27)
- 项目初始化
- 基础框架搭建
- Tornado后端核心
- 数据库连接和多租户支持
- Redis缓存集成
- 统一的错误处理和日志系统
- JWT认证基础
- 健康检查端点
# 数据库模块

## 概述

数据库模块负责管理CoachAI项目的数据库连接、迁移和种子数据。

## 目录结构

```
database/
├── connection.py              # 数据库连接管理器
├── migration_manager.py       # 数据库迁移管理器
├── migrations/                # 数据库迁移脚本
│   ├── alembic.ini           # Alembic配置文件
│   ├── env.py                # Alembic环境配置
│   ├── script.py.mako        # 迁移模板
│   └── versions/             # 迁移版本目录
│       └── 001_initial_tables.py  # 初始表结构迁移
└── seeds/                    # 种子数据
    └── initial_data.py       # 初始数据脚本
```

## 数据库迁移

### 使用Alembic进行数据库迁移

CoachAI使用Alembic进行数据库版本控制。Alembic是一个轻量级的数据库迁移工具，支持SQLAlchemy。

### 迁移命令

#### 1. 初始化数据库

```bash
# 初始化迁移环境并创建所有表
python -m database.migration_manager init
```

#### 2. 创建新的迁移

```bash
# 自动检测模型变化并创建迁移脚本
python -m database.migration_manager create "添加新功能表"

# 手动创建空迁移脚本
python -m database.migration_manager create "手动修改" --no-autogenerate
```

#### 3. 应用迁移

```bash
# 升级到最新版本
python -m database.migration_manager upgrade

# 升级到特定版本
python -m database.migration_manager upgrade 001_initial_tables
```

#### 4. 回滚迁移

```bash
# 回滚一个版本
python -m database.migration_manager downgrade

# 回滚到特定版本
python -m database.migration_manager downgrade base
```

#### 5. 查看状态

```bash
# 查看当前迁移状态
python -m database.migration_manager status

# 查看迁移历史
python -m database.migration_manager history
```

#### 6. 重置数据库（危险！）

```bash
# 重置数据库（删除所有表并重新创建）
python -m database.migration_manager reset --confirm
```

### 迁移工作流程

1. **开发新功能时**：
   ```bash
   # 1. 修改模型文件
   # 2. 创建迁移脚本
   python -m database.migration_manager create "添加新功能"
   # 3. 检查生成的迁移脚本
   # 4. 应用迁移
   python -m database.migration_manager upgrade
   ```

2. **部署到生产环境**：
   ```bash
   # 1. 拉取最新代码
   # 2. 检查待应用的迁移
   python -m database.migration_manager status
   # 3. 应用迁移
   python -m database.migration_manager upgrade
   ```

3. **回滚错误迁移**：
   ```bash
   # 1. 查看迁移历史
   python -m database.migration_manager history
   # 2. 回滚到上一个版本
   python -m database.migration_manager downgrade
   ```

## 种子数据

### 初始数据

系统启动时需要一些初始数据，包括：
- 系统权限定义
- 系统角色定义
- 角色权限分配
- 超级用户账户
- 默认租户
- 测试用户

### 运行种子脚本

```bash
# 运行所有种子
python -m database.seeds.initial_data

# 通过迁移管理器运行
python -m database.migration_manager seed
```

### 种子数据内容

#### 1. 系统权限
系统定义了以下权限模块：
- **用户管理** (user): 用户CRUD操作
- **租户管理** (tenant): 租户CRUD操作
- **角色管理** (role): 角色CRUD操作
- **权限管理** (permission): 权限CRUD操作
- **教练模块** (coach): 教练管理
- **学员模块** (student): 学员管理
- **课程模块** (course): 课程管理
- **系统管理** (system): 系统设置

#### 2. 系统角色
- **超级管理员** (super_admin): 拥有所有权限
- **租户管理员** (tenant_admin): 管理租户内所有资源
- **教练** (coach): 管理学员和课程
- **学员** (student): 查看和参与课程
- **访客** (guest): 只有基本查看权限

#### 3. 初始用户
- **超级用户**: admin@coach-ai.com / Admin@123
- **测试教练**: coach1@coach-ai.com / Coach@123
- **测试学员**: student1@coach-ai.com / Student@123
- **测试访客**: guest1@coach-ai.com / Guest@123

## 多租户支持

### 租户数据隔离

数据库连接管理器支持多租户数据隔离。每个租户使用相同的数据库，但通过`tenant_id`进行数据隔离。

### 使用示例

```python
from database.connection import get_db_session

# 使用默认租户
with get_db_session() as session:
    # 操作默认租户的数据
    pass

# 使用特定租户
with get_db_session(tenant_id="tenant_123") as session:
    # 操作特定租户的数据
    pass
```

### 租户上下文管理

在请求处理中，租户ID通常从JWT令牌或请求头中获取：

```python
class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        # 从JWT令牌获取租户ID
        tenant_id = self.current_user.get("tenant_id")
        self.db_session = get_db_session(tenant_id)
    
    def on_finish(self):
        # 清理数据库会话
        if hasattr(self, "db_session"):
            self.db_session.close()
```

## 数据库连接配置

### 环境变量

数据库连接通过环境变量配置：

```bash
# MySQL数据库连接
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/coach_ai

# 连接池配置
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# 默认租户ID
DEFAULT_TENANT_ID=default
```

### 连接池管理

数据库连接管理器使用SQLAlchemy连接池：
- **pool_size**: 连接池大小（默认：10）
- **max_overflow**: 最大溢出连接数（默认：20）
- **pool_recycle**: 连接回收时间（默认：3600秒）
- **pool_pre_ping**: 连接前ping检查（默认：True）

## 最佳实践

### 1. 迁移脚本编写

- 每个迁移脚本必须可回滚（实现`downgrade`函数）
- 迁移描述要清晰明确
- 复杂的迁移需要手动测试
- 生产环境迁移前备份数据库

### 2. 种子数据管理

- 种子数据只包含系统必需数据
- 测试数据通过单独的脚本管理
- 敏感信息（如密码）使用环境变量
- 种子脚本要幂等（可重复执行）

### 3. 数据库会话管理

- 使用上下文管理器确保会话正确关闭
- 避免长时间持有数据库会话
- 及时提交或回滚事务
- 处理数据库异常

### 4. 性能优化

- 合理设置连接池大小
- 使用索引优化查询性能
- 定期清理无用数据
- 监控数据库性能指标

## 故障排除

### 常见问题

#### 1. 迁移失败

**问题**: Alembic迁移失败，提示表已存在或列不存在

**解决**:
```bash
# 检查当前迁移状态
python -m database.migration_manager status

# 手动修复迁移历史
# 1. 连接到数据库
# 2. 查看alembic_version表
# 3. 更新版本号或删除错误记录
```

#### 2. 连接池耗尽

**问题**: 数据库连接池耗尽，无法获取新连接

**解决**:
- 增加连接池大小
- 检查代码中是否有未关闭的会话
- 减少长时间运行的查询

#### 3. 种子数据重复

**问题**: 重复运行种子脚本导致数据重复

**解决**:
- 种子脚本设计为幂等的
- 使用`ON DUPLICATE KEY UPDATE`或先检查后插入
- 清理重复数据后重新运行

### 日志查看

数据库相关日志输出到控制台和日志文件：

```bash
# 查看数据库日志
tail -f logs/app_$(date +%Y-%m-%d).log | grep -i database

# 查看迁移日志
tail -f logs/app_$(date +%Y-%m-%d).log | grep -i alembic
```

## 相关文档

- [Alembic官方文档](https://alembic.sqlalchemy.org/)
- [SQLAlchemy官方文档](https://docs.sqlalchemy.org/)
- [MySQL官方文档](https://dev.mysql.com/doc/)
- [项目编码规范](../README.md#编码规范)
# CoachAI数据库设计指南

## 📋 概述

本文档是CoachAI项目的数据库设计指南，由RD (研发专家) subagent创建和维护。文档按照项目文档规范要求，使用中文文件名，存储在`docs/技术架构/`目录下。

## 🏗️ 数据库架构设计

### 1. 数据库选型策略
#### 开发环境：
- **数据库**: SQLite 3
- **优势**: 轻量级、零配置、快速开发
- **适用场景**: 开发、测试、原型验证

#### 生产环境：
- **数据库**: PostgreSQL 15+
- **优势**: 高性能、高可靠性、完整功能
- **适用场景**: 生产部署、高并发、数据安全

### 2. 数据库设计原则
#### 核心原则：
1. **规范化设计**: 遵循数据库规范化原则
2. **性能优化**: 考虑查询性能和扩展性
3. **数据安全**: 确保数据完整性和安全性
4. **可维护性**: 设计清晰，易于维护和扩展

#### 命名规范：
- **表名**: 小写字母，下划线分隔，复数形式
  - 示例: `users`, `exercise_records`, `task_assignments`
- **字段名**: 小写字母，下划线分隔
  - 示例: `user_id`, `created_at`, `is_active`
- **索引名**: `idx_表名_字段名`
  - 示例: `idx_users_email`, `idx_exercise_records_user_id`
- **外键名**: `fk_表名_字段名`
  - 示例: `fk_exercise_records_user_id`

## 📊 核心数据模型

### 1. 用户管理模块
#### users表 (用户表)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url VARCHAR(255),
    phone_number VARCHAR(20),
    date_of_birth DATE,
    gender VARCHAR(10),
    height_cm INTEGER,
    weight_kg DECIMAL(5,2),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_is_active ON users(is_active);
```

#### tenants表 (租户表)
```sql
CREATE TABLE tenants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    contact_email VARCHAR(100),
    contact_phone VARCHAR(20),
    max_users INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT TRUE,
    subscription_plan VARCHAR(20) DEFAULT 'free',
    subscription_expires_at TIMESTAMP,
    settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_tenants_tenant_code ON tenants(tenant_code);
CREATE INDEX idx_tenants_is_active ON tenants(is_active);
```

### 2. 运动管理模块
#### exercise_types表 (运动类型表)
```sql
CREATE TABLE exercise_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(50),
    difficulty_level VARCHAR(20),
    calories_per_minute DECIMAL(5,2),
    icon_url VARCHAR(255),
    video_url VARCHAR(255),
    instructions TEXT,
    safety_precautions TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_exercise_types_code ON exercise_types(code);
CREATE INDEX idx_exercise_types_category ON exercise_types(category);
```

#### exercise_records表 (运动记录表)
```sql
CREATE TABLE exercise_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    exercise_type_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    duration_seconds INTEGER NOT NULL,
    calories_burned DECIMAL(8,2),
    heart_rate_avg INTEGER,
    heart_rate_max INTEGER,
    steps_count INTEGER,
    distance_meters DECIMAL(8,2),
    repetitions INTEGER,
    sets INTEGER,
    weight_kg DECIMAL(5,2),
    notes TEXT,
    video_url VARCHAR(255),
    ai_analysis JSON,
    is_completed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_type_id) REFERENCES exercise_types(id) ON DELETE RESTRICT
);

-- 索引
CREATE INDEX idx_exercise_records_user_id ON exercise_records(user_id);
CREATE INDEX idx_exercise_records_exercise_type_id ON exercise_records(exercise_type_id);
CREATE INDEX idx_exercise_records_start_time ON exercise_records(start_time);
CREATE INDEX idx_exercise_records_user_date ON exercise_records(user_id, start_time);
```

### 3. 任务管理模块
#### tasks表 (任务表)
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    task_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    difficulty VARCHAR(20) DEFAULT 'medium',
    estimated_duration_minutes INTEGER,
    due_date TIMESTAMP,
    max_score INTEGER DEFAULT 100,
    passing_score INTEGER DEFAULT 60,
    is_repeatable BOOLEAN DEFAULT FALSE,
    repeat_interval_days INTEGER,
    tags JSON,
    metadata JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_tasks_task_type ON tasks(task_type);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_is_active ON tasks(is_active);
```

#### task_assignments表 (任务分配表)
```sql
CREATE TABLE task_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    assigned_by INTEGER,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'assigned',
    progress_percentage INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    actual_score INTEGER,
    feedback TEXT,
    notes TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_task_assignments_task_id ON task_assignments(task_id);
CREATE INDEX idx_task_assignments_user_id ON task_assignments(user_id);
CREATE INDEX idx_task_assignments_status ON task_assignments(status);
CREATE INDEX idx_task_assignments_due_date ON task_assignments(due_date);
CREATE INDEX idx_task_assignments_user_status ON task_assignments(user_id, status);
```

### 4. 成就系统模块
#### achievements表 (成就表)
```sql
CREATE TABLE achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(50),
    difficulty VARCHAR(20),
    points INTEGER DEFAULT 100,
    icon_url VARCHAR(255),
    trigger_type VARCHAR(50),
    trigger_condition JSON,
    rewards JSON,
    is_secret BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_achievements_code ON achievements(code);
CREATE INDEX idx_achievements_category ON achievements(category);
CREATE INDEX idx_achievements_difficulty ON achievements(difficulty);
CREATE INDEX idx_achievements_is_active ON achievements(is_active);
```

#### user_achievements表 (用户成就表)
```sql
CREATE TABLE user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    progress_current INTEGER DEFAULT 0,
    progress_target INTEGER NOT NULL,
    progress_percentage INTEGER DEFAULT 0,
    is_unlocked BOOLEAN DEFAULT FALSE,
    unlocked_at TIMESTAMP,
    notified BOOLEAN DEFAULT FALSE,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE,
    UNIQUE(user_id, achievement_id)
);

-- 索引
CREATE INDEX idx_user_achievements_user_id ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_achievement_id ON user_achievements(achievement_id);
CREATE INDEX idx_user_achievements_is_unlocked ON user_achievements(is_unlocked);
CREATE INDEX idx_user_achievements_user_unlocked ON user_achievements(user_id, is_unlocked);
```

## 🔧 数据库性能优化

### 1. 索引策略
#### 必须创建的索引：
1. **主键索引**: 所有表自动创建
2. **外键索引**: 所有外键字段创建索引
3. **查询字段索引**: 经常用于查询条件的字段
4. **排序字段索引**: 经常用于排序的字段
5. **联合索引**: 经常一起查询的字段组合

#### 索引创建原则：
1. **选择性原则**: 高选择性的字段优先创建索引
2. **覆盖查询**: 创建覆盖索引减少回表
3. **避免过度索引**: 索引会增加写操作开销
4. **定期维护**: 定期重建索引优化性能

### 2. 查询优化
#### 优化原则：
1. **避免SELECT ***: 只选择需要的字段
2. **使用EXPLAIN**: 分析查询执行计划
3. **避免子查询**: 尽量使用JOIN代替子查询
4. **分页优化**: 使用游标分页代替OFFSET分页
5. **批量操作**: 使用批量插入和更新

#### 示例优化：
```sql
-- 不好的写法
SELECT * FROM users WHERE email LIKE '%@example.com%';

-- 好的写法
SELECT id, username, email FROM users 
WHERE email LIKE 'user%@example.com'
ORDER BY created_at DESC
LIMIT 20;
```

### 3. 事务管理
#### 事务使用原则：
1. **保持简短**: 事务尽可能简短
2. **明确边界**: 明确事务开始和结束
3. **错误处理**: 完善的错误处理和回滚
4. **隔离级别**: 根据业务需求选择隔离级别

#### 示例事务：
```python
# Django示例
from django.db import transaction

@transaction.atomic
def create_user_with_profile(username, email, profile_data):
    user = User.objects.create(username=username, email=email)
    profile = UserProfile.objects.create(user=user, **profile_data)
    return user
```

## 🛡️ 数据安全设计

### 1. 数据加密
#### 敏感数据加密：
1. **密码哈希**: 使用bcrypt或Argon2算法
2. **个人信息**: 加密存储敏感个人信息
3. **API密钥**: 加密存储第三方API密钥
4. **支付信息**: 符合PCI DSS标准加密

#### 加密实现：
```python
from django.contrib.auth.hashers import make_password, check_password

# 密码哈希
hashed_password = make_password('user_password')

# 验证密码
is_valid = check_password('user_password', hashed_password)
```

### 2. 访问控制
#### 数据库访问控制：
1. **最小权限原则**: 应用使用最小必要权限
2. **连接池管理**: 使用连接池管理数据库连接
3. **IP白名单**: 生产环境限制访问IP
4. **审计日志**: 记录数据库访问日志

#### 应用层访问控制：
1. **认证授权**: 用户认证和权限控制
2. **数据隔离**: 多租户数据隔离
3. **输入验证**: 防止SQL注入攻击
4. **输出转义**: 防止XSS攻击

### 3. 备份和恢复
#### 备份策略：
1. **全量备份**: 每日全量备份
2. **增量备份**: 每小时增量备份
3. **异地备份**: 备份到异地存储
4. **备份验证**: 定期验证备份可恢复性

#### 恢复策略：
1. **恢复测试**: 定期测试恢复流程
2. **恢复时间目标**: RTO < 4小时
3. **恢复点目标**: RPO < 15分钟
4. **灾难恢复**: 完整的灾难恢复计划

## 📈 数据迁移管理

### 1. 迁移工具
#### 使用Alembic进行数据库迁移：
```python
# 生成迁移文件
alembic revision --autogenerate -m "Add exercise_records table"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 2. 迁移原则
#### 安全迁移原则：
1. **向后兼容**: 迁移保持向后兼容
2. **小步迁移**: 每次迁移只做一个变更
3. **测试验证**: 迁移前在测试环境验证
4. **回滚计划**: 准备迁移回滚计划

#### 数据迁移原则：
1. **数据验证**: 迁移前后验证数据完整性
2. **性能考虑**: 大数据量迁移考虑性能影响
3. **业务影响**: 评估迁移对业务的影响
4. **监控告警**: 迁移过程监控和告警

### 3. 迁移示例
#### 添加新字段迁移：
```python
# migration script
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users', sa.Column('phone_number', sa.String(20), nullable=True))
    op.create_index('idx_users_phone_number', 'users', ['phone_number'])

def downgrade():
    op.drop_index('idx_users_phone_number', 'users')
    op.drop_column('users', 'phone_number')
```

## 🔍 数据库监控和维护

### 1. 性能监控
#### 监控指标：
1. **连接数**: 当前连接数和最大连接数
2. **查询性能**: 慢查询统计和优化
3. **锁等待**: 锁等待时间和死锁检测
4. **空间使用**: 数据库空间使用情况

#### 监控工具：
1. **pg_stat_statements**: PostgreSQL查询统计
2. **pgBadger**: PostgreSQL日志分析
3. **Prometheus**: 指标收集和告警
4. **Grafana**: 监控仪表板

### 2. 定期维护
#### 维护任务：
1. **索引重建**: 定期重建碎片化索引
2. **统计更新**: 更新数据库统计信息
3. **空间回收**: 回收删除数据的空间
4. **备份清理**: 清理过期备份文件

#### 维护计划：
1. **每日维护**: 备份验证、空间监控
2. **每周维护**: 索引重建、统计更新
3. **每月维护**: 性能分析、容量规划
4. **每季度维护**: 架构评估、优化调整

## 📚 相关文档

### 项目文档：
- [技术架构概要设计](../CoachAI技术架构概要设计.md)
- [技术架构详细设计](../CoachAI技术架构详细设计.md)
- [API接口总览文档](../API文档/CoachAI-API接口总览.md)

### 开发文档：
- [编码规范文档](../开发指南/编码规范.md)
- [开发环境配置指南](../开发指南/开发环境配置指南.md) (待创建)
- [部署运维指南](../部署运维/部署指南.md)

### 外部资源：
- [PostgreSQL官方文档](https://www.postgresql.org/docs/)
- [SQLite官方文档](https://www.sqlite.org/docs.html)
- [Django数据库文档](https://docs.djangoproject.com/en/5.0/topics/db/)

---
**文档信息**:
- **创建时间**: 2026-03-26 23:59
- **创建者**: RD subagent (研发专家)
- **文档状态**: 草案 v1.0
- **存储位置**: `docs/技术架构/CoachAI数据库设计指南.md`
- **文件名规范**: 符合中文文件名要求
- **版本控制**: 已纳入Git版本管理

**更新计划**:
- 2026-03-27: 根据实际开发经验更新内容
- 2026-04-01: 添加性能优化案例
- 2026-04-15: 更新监控和维护指南
- 每月评审: 定期评审和优化指南内容

**使用说明**:
1. 本指南适用于CoachAI项目的数据库设计和开发
2. 开发人员应遵循本指南进行数据库设计
3. DBA应参考本指南进行数据库维护
4. 定期更新本指南以反映最佳实践

**原则遵循**:
- ✅ 产出物存储在项目docs目录
- ✅ 使用中文文件名: `CoachAI数据库设计指南.md`
- ✅ 按功能分类存储: `技术架构/`目录
- ✅ 严格分离记忆和产出物存储
- ✅ 长期遵循文档管理规范
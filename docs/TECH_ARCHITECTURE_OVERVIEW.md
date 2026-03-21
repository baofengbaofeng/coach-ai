# CoachAI 技术架构概要设计 (简化版本 - 无中间件)

## 文档信息

| 项目 | 内容 |
|------|------|
| **文档名称** | CoachAI 技术架构概要设计 |
| **文档版本** | 3.0.0 |
| **创建日期** | 2026-03-21 |
| **最后更新** | 2026-03-21 |
| **文档状态** | 草案 |
| **作者** | baofengbaofeng |
| **审核人** | 待定 |
| **关联文档** | [BRD.md](./BRD.md), [PRD.md](./PRD.md) |

## 修订历史

| 版本 | 日期 | 作者 | 变更描述 |
|------|------|------|----------|
| 1.0.0 | 2026-03-21 | baofengbaofeng | 初始版本创建 (Node.js + PostgreSQL) |
| 2.0.0 | 2026-03-21 | baofengbaofeng | 技术栈变更为 Python + Django + MySQL |
| 3.0.0 | 2026-03-21 | baofengbaofeng | 简化架构，移除 Redis/MQ 中间件 |

## 重要说明

**架构简化原则**：
1. 暂时不引入 Redis、RabbitMQ 等中间件
2. 使用数据库表替代缓存和消息队列功能
3. 简化部署和维护复杂度
4. 未来可根据需要逐步引入中间件

## 目录

1. [架构设计原则](#1-架构设计原则)
2. [整体架构概述](#2-整体架构概述)
3. [技术栈选型](#3-技术栈选型)
4. [系统模块划分](#4-系统模块划分)
5. [数据架构设计](#5-数据架构设计)
6. [部署架构设计](#6-部署架构设计)
7. [性能优化策略](#7-性能优化策略)
8. [扩展性设计](#8-扩展性设计)

---

## 1. 架构设计原则

### 1.1 核心设计原则

#### 1.1.1 简化架构原则
- **最小化依赖**：只使用必要的技术组件
- **数据库中心化**：使用数据库表实现缓存和队列功能
- **渐进式演进**：未来可根据需要引入中间件
- **易于部署**：单数据库架构，部署简单

#### 1.1.2 异步处理原则
- **数据库驱动异步**：使用数据库表管理异步任务
- **定时轮询机制**：通过定时任务处理异步队列
- **最终一致性**：保证数据的最终一致性
- **错误重试机制**：任务失败后自动重试

#### 1.1.3 性能优化原则
- **查询优化**：通过数据库索引和查询优化提升性能
- **连接池管理**：合理配置数据库连接池
- **批量操作**：减少数据库交互次数
- **懒加载策略**：按需加载数据

### 1.2 无中间件架构优势

#### 1.2.1 部署简化
- **组件减少**：只需要 Django + MySQL
- **配置简单**：无需中间件配置和维护
- **故障排查**：系统组件少，故障定位简单
- **资源需求低**：减少服务器资源消耗

#### 1.2.2 开发效率
- **学习成本低**：开发者只需掌握 Django 和 MySQL
- **调试方便**：所有数据都在数据库中，便于调试
- **测试简单**：无需模拟中间件行为
- **代码统一**：所有逻辑都在 Django 应用中

#### 1.2.3 成本控制
- **服务器成本**：减少中间件服务器需求
- **运维成本**：减少中间件维护工作量
- **监控成本**：监控系统更简单
- **备份恢复**：只需备份数据库

## 2. 整体架构概述

### 2.1 架构视图

#### 2.1.1 逻辑架构
```
┌─────────────────────────────────────────┐
│               客户端层                   │
│  ┌──────────┐  ┌──────────┐            │
│  │ Web前端  │  │ 移动端   │            │
│  │(React)   │  │(Flutter) │            │
│  └──────────┘  └──────────┘            │
└─────────────────────────────────────────┘
                    │ HTTP/WebSocket
┌─────────────────────────────────────────┐
│              Django 应用层               │
│  ┌──────────────────────────────────┐   │
│  │        Django 单体应用           │   │
│  │  ┌─────────┐ ┌─────────┐        │   │
│  │  │同步视图 │ │异步视图 │        │   │
│  │  │(REST)   │ │(ASGI)   │        │   │
│  │  └─────────┘ └─────────┘        │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │     后台任务处理器       │    │   │
│  │  │   (定时轮询)            │    │   │
│  │  └─────────────────────────┘    │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│               数据存储层                 │
│  ┌──────────┐  ┌──────────┐            │
│  │ MySQL    │  │ 文件系统 │            │
│  │ (主业务) │  │ (本地)   │            │
│  └──────────┘  └──────────┘            │
└─────────────────────────────────────────┘
```

#### 2.1.2 数据流架构
```
用户请求 → Django视图 → 数据库操作
                    ↓
            异步任务创建 → 任务表
                    ↓
            定时任务轮询 → 处理任务
                    ↓
            更新任务状态 → 通知用户
```

### 2.2 核心组件说明

#### 2.2.1 Django 同步服务
- **RESTful API**：处理 HTTP 请求
- **认证授权**：用户认证和权限控制
- **业务逻辑**：核心业务处理
- **数据验证**：请求数据验证和处理

#### 2.2.2 Django 异步服务
- **ASGI 支持**：处理 WebSocket 和异步请求
- **后台任务**：定时处理异步任务
- **实时通信**：WebSocket 实时数据推送
- **事件处理**：异步事件处理

#### 2.2.3 数据库任务系统
- **任务表**：存储待处理任务
- **状态管理**：任务状态跟踪
- **结果存储**：任务处理结果存储
- **错误处理**：任务失败处理和重试

## 3. 技术栈选型

### 3.1 后端技术栈

#### 3.1.1 Django 框架
| 技术 | 版本 | 用途 | 选择理由 |
|------|------|------|----------|
| **Django** | 5.0+ | Web框架 | 功能完整，内置ORM和Admin |
| **Django REST Framework** | 3.15+ | API框架 | Django生态的REST API支持 |
| **Django Channels** | 4.0+ | WebSocket | 异步和实时通信支持 |
| **Django Q** | 1.3+ | 任务队列 | 基于数据库的任务队列 |

#### 3.1.2 数据库
| 技术 | 版本 | 用途 | 选择理由 |
|------|------|------|----------|
| **MySQL** | 8.0+ | 主数据库 | 成熟稳定，性能优秀 |
| **SQLite** | 3.35+ | 开发数据库 | 开发环境简化部署 |

#### 3.1.3 文件存储
| 技术 | 版本 | 用途 | 选择理由 |
|------|------|------|----------|
| **本地文件系统** | - | 文件存储 | 简化架构，无需对象存储 |
| **Django Storage** | - | 存储抽象 | 支持未来迁移到云存储 |

### 3.2 前端技术栈 (保持不变)

#### 3.2.1 Web前端
| 技术 | 版本 | 用途 | 选择理由 |
|------|------|------|----------|
| **React** | 18+ | UI框架 | 生态丰富，性能优秀 |
| **TypeScript** | 5+ | 开发语言 | 类型安全，提高代码质量 |
| **Vite** | 5+ | 构建工具 | 开发体验优秀，构建速度快 |

#### 3.2.2 移动端
| 技术 | 版本 | 用途 | 选择理由 |
|------|------|------|----------|
| **Flutter** | 3+ | 跨平台框架 | 性能接近原生，开发效率高 |

### 3.3 AI技术栈

#### 3.3.1 OCR识别
| 技术 | 版本 | 用途 | 选择理由 |
|------|------|------|----------|
| **PaddleOCR** | 2.6+ | OCR引擎 | 中文识别优秀，Python原生 |
| **EasyOCR** | 1.7+ | OCR库 | 简单易用，多语言支持 |

#### 3.3.2 计算机视觉
| 技术 | 版本 | 用途 | 选择理由 |
|------|------|------|----------|
| **MediaPipe** | 0.10+ | 姿态识别 | Google出品，Python支持 |
| **OpenCV** | 4.8+ | 图像处理 | 功能强大，Python原生 |

#### 3.3.3 语音处理
| 技术 | 版本 | 用途 | 选择理由 |
|------|------|------|----------|
| **Whisper** | 202309+ | 语音识别 | OpenAI出品，Python原生 |
| **SpeechRecognition** | 3.10+ | 语音识别 | Python语音识别库 |

### 3.4 开发工具

#### 3.4.1 开发环境
| 技术 | 版本 | 用途 | 选择理由 |
|------|------|------|----------|
| **Python** | 3.11+ | 开发语言 | Django官方支持版本 |
| **Poetry** | 1.7+ | 依赖管理 | 现代Python依赖管理 |
| **Black** | 23.0+ | 代码格式化 | 统一的代码风格 |
| **Flake8** | 7.0+ | 代码检查 | 代码质量检查 |

#### 3.4.2 容器化
| 技术 | 版本 | 用途 | 选择理由 |
|------|------|------|----------|
| **Docker** | 24+ | 容器引擎 | 环境一致性 |
| **Docker Compose** | 2.20+ | 容器编排 | 开发环境编排 |

## 4. 系统模块划分

### 4.1 Django 应用模块

#### 4.1.1 用户管理模块 (accounts)
**功能**：
- 用户注册、登录、认证
- 个人资料管理
- 权限和角色管理

**技术实现**：
- Django 内置 User 模型扩展
- Django REST Framework 认证
- JWT 令牌认证
- 数据库会话存储

#### 4.1.2 作业管理模块 (homework)
**功能**：
- 作业上传和管理
- 作业批改状态跟踪
- 学习报告生成
- 错题本管理

**技术实现**：
- Django Models 定义数据模型
- Django REST Framework 提供 API
- 数据库任务表处理异步批改
- 本地文件系统存储作业图片

#### 4.1.3 运动管理模块 (exercise)
**功能**：
- 运动记录管理
- 运动数据统计
- 运动成就计算
- 实时运动计数

**技术实现**：
- Django Channels WebSocket
- 数据库实时状态存储
- 定时任务处理运动数据
- 本地文件存储运动视频

#### 4.1.4 任务管理模块 (tasks)
**功能**：
- 任务创建和管理
- 任务提醒和通知
- 进度跟踪
- 成就计算

**技术实现**：
- Django Models + Django REST Framework
- 数据库定时任务表
- WebSocket 实时通知
- 数据库缓存任务状态

### 4.2 数据库任务系统

#### 4.2.1 任务表设计
```sql
CREATE TABLE async_tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_type VARCHAR(50) NOT NULL,
    payload JSON NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    result JSON,
    error_message TEXT,
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

#### 4.2.2 缓存表设计
```sql
CREATE TABLE database_cache (
    cache_key VARCHAR(255) PRIMARY KEY,
    cache_value JSON NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_expires_at (expires_at)
);
```

#### 4.2.3 事件表设计
```sql
CREATE TABLE system_events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    payload JSON NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_event_type (event_type),
    INDEX idx_processed (processed)
);
```

### 4.3 服务通信设计

#### 4.3.1 同步通信
- **HTTP RESTful API**：客户端与服务器通信
- **WebSocket**：实时数据推送
- **Server-Sent Events**：单向实时数据流

#### 4.3.2 异步通信
- **数据库任务表**：异步任务调度
- **定时轮询**：后台任务处理器轮询任务表
- **事件表**：系统事件驱动

#### 4.3.3 数据一致性
- **数据库事务**：保证数据一致性
- **乐观锁**：防止并发冲突
- **最终一致性**：通过任务表保证最终一致性

## 5. 数据架构设计

### 5.1 数据库设计原则

#### 5.1.1 规范化设计
- **第三范式**：减少数据冗余
- **适当反规范化**：提高查询性能
- **索引优化**：合理创建和使用索引
- **分区策略**：大表按时间分区

#### 5.1.2 性能优化
- **查询优化**：避免 N+1 查询问题
- **连接池**：合理配置数据库连接
- **批量操作**：减少数据库交互
- **读写分离**：未来扩展支持

### 5.2 核心表设计

#### 5.2.1 用户表 (users)
```sql
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(30),
    last_name VARCHAR(150),
    role ENUM('student', 'parent', 'teacher', 'admin') DEFAULT 'student',
    age INT,
    grade VARCHAR(20),
    avatar_url VARCHAR(500),
    settings JSON,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 5.2.2 作业表 (homeworks)
```sql
CREATE TABLE homeworks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    subject VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    image_urls JSON,
    status ENUM('uploaded', 'processing', 'graded', 'error') DEFAULT 'uploaded',
    grade_result JSON,
    total_questions INT,
    correct_questions INT,
    score DECIMAL(5,2),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 5.2.3 运动记录表 (exercise_records)
```sql
CREATE TABLE exercise_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    exercise_type VARCHAR(50) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INT,
    total_count INT,
    average_frequency DECIMAL(5,2),
    posture_score DECIMAL(5,2),
    video_url VARCHAR(500),
    data_points JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_exercise_type (exercise_type),
    INDEX idx_start_time (start_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

####### 5.2.4 任务表 (tasks)
```sql
CREATE TABLE tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    task_type VARCHAR(50) NOT NULL,
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    status ENUM('pending', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    reminder_settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_due_date (due_date),
    INDEX idx_priority (priority)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5.3 文件存储设计

#### 5.3.1 本地文件存储结构
```
media/
├── avatars/              # 用户头像
│   ├── user_1/
│   └── user_2/
├── homeworks/            # 作业图片
│   ├── 2026/
│   │   ├── 03/
│   │   │   ├── 21/
│   │   │   └── 22/
│   │   └── 04/
├── exercises/            # 运动视频
│   ├── jump_rope/
│   ├── push_up/
│   └── sit_up/
└── temp/                 # 临时文件
```

#### 5.3.2 文件管理策略
1. **目录分区**：按日期和类型分区存储
2. **文件命名**：使用UUID避免文件名冲突
3. **权限控制**：文件访问权限控制
4. **清理策略**：定期清理临时文件

#### 5.3.3 Django 文件存储配置
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 文件上传配置
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
```

### 5.4 数据备份策略

#### 5.4.1 备份方案
- **每日全量备份**：凌晨进行数据库全量备份
- **实时增量备份**：MySQL binlog 实时备份
- **文件备份**：重要文件定期备份
- **备份验证**：定期恢复测试验证备份有效性

#### 5.4.2 备份脚本示例
```bash
#!/bin/bash
# 数据库备份脚本
BACKUP_DIR="/backup/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="coachai"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -u root -p$MYSQL_ROOT_PASSWORD $DB_NAME \
  --single-transaction \
  --routines \
  --triggers \
  --events \
  > $BACKUP_DIR/${DB_NAME}_${DATE}.sql

# 压缩备份文件
gzip $BACKUP_DIR/${DB_NAME}_${DATE}.sql

# 保留最近7天备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
```

## 6. 部署架构设计

### 6.1 环境划分

#### 6.1.1 开发环境
- **目的**：开发人员本地开发
- **部署**：Docker Compose
- **数据库**：MySQL 单实例
- **文件存储**：本地文件系统

#### 6.1.2 测试环境
- **目的**：集成测试和系统测试
- **部署**：单服务器部署
- **数据库**：MySQL 单实例
- **监控**：基础监控

#### 6.1.3 生产环境
- **目的**：对外提供服务
- **部署**：单服务器或双服务器
- **数据库**：MySQL 主从（可选）
- **监控**：完整监控告警

### 6.2 单服务器部署方案

#### 6.2.1 服务器配置
```
单服务器配置：
- CPU: 4核
- 内存: 8GB
- 存储: 100GB SSD
- 带宽: 10Mbps
```

#### 6.2.2 服务部署
```
单服务器部署结构：
┌─────────────────────────────────┐
│          Nginx (反向代理)        │
├─────────────────────────────────┤
│        Gunicorn (Django)        │
├─────────────────────────────────┤
│      Daphne (WebSocket)         │
├─────────────────────────────────┤
│      Celery (后台任务)          │
├─────────────────────────────────┤
│         MySQL 8.0               │
└─────────────────────────────────┘
```

#### 6.2.3 Docker Compose 配置
```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: coachai-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: coachai
      MYSQL_USER: coachai
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./config/mysql/my.cnf:/etc/mysql/conf.d/my.cnf
    restart: unless-stopped

  web:
    build: .
    container_name: coachai-web
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn coachai.wsgi:application --bind 0.0.0.0:8000"
    environment:
      DATABASE_URL: mysql://coachai:${MYSQL_PASSWORD}@mysql:3306/coachai
      DJANGO_SETTINGS_MODULE: coachai.settings.production
    ports:
      - "8000:8000"
    volumes:
      - media_volume:/app/media
      - static_volume:/app/staticfiles
    depends_on:
      - mysql
    restart: unless-stopped

  websocket:
    build: .
    container_name: coachai-websocket
    command: daphne -b 0.0.0.0 -p 8001 coachai.asgi:application
    environment:
      DATABASE_URL: mysql://coachai:${MYSQL_PASSWORD}@mysql:3306/coachai
      DJANGO_SETTINGS_MODULE: coachai.settings.production
    ports:
      - "8001:8001"
    volumes:
      - media_volume:/app/media
    depends_on:
      - mysql
    restart: unless-stopped

  worker:
    build: .
    container_name: coachai-worker
    command: celery -A coachai worker --loglevel=info
    environment:
      DATABASE_URL: mysql://coachai:${MYSQL_PASSWORD}@mysql:3306/coachai
      DJANGO_SETTINGS_MODULE: coachai.settings.production
    volumes:
      - media_volume:/app/media
    depends_on:
      - mysql
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: coachai-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./config/nginx/ssl:/etc/nginx/ssl
      - static_volume:/static
      - media_volume:/media
    depends_on:
      - web
      - websocket
    restart: unless-stopped

volumes:
  mysql_data:
  media_volume:
  static_volume:
```

### 6.3 高可用设计（未来扩展）

#### 6.3.1 双服务器部署
```
服务器A (主)                    服务器B (备)
┌─────────────┐                ┌─────────────┐
│ Nginx       │                │ Nginx       │
│ Django      │ ← 负载均衡 →   │ Django      │
│ MySQL主     │                │ MySQL从     │
└─────────────┘                └─────────────┘
```

#### 6.3.2 数据库主从复制
```sql
-- 主服务器配置
[mysqld]
server-id=1
log-bin=mysql-bin
binlog-format=ROW

-- 从服务器配置  
[mysqld]
server-id=2
relay-log=mysql-relay-bin
read-only=1
```

#### 6.3.3 故障转移策略
- **手动切换**：管理员手动切换主从
- **监控告警**：系统监控发现故障
- **数据同步**：保证数据一致性
- **恢复测试**：定期进行故障恢复测试

## 7. 性能优化策略

### 7.1 数据库性能优化

#### 7.1.1 查询优化
```python
# 优化前：N+1查询问题
homeworks = Homework.objects.filter(user=user)
for homework in homeworks:
    print(homework.user.username)  # 每次循环都查询数据库

# 优化后：使用select_related
homeworks = Homework.objects.select_related('user').filter(user=user)
for homework in homeworks:
    print(homework.user.username)  # 一次查询获取所有数据
```

#### 7.1.2 索引优化
```sql
-- 添加复合索引
CREATE INDEX idx_homework_user_status ON homeworks(user_id, status);

-- 添加覆盖索引
CREATE INDEX idx_exercise_user_type_time ON exercise_records(user_id, exercise_type, start_time);
```

#### 7.1.3 连接池配置
```python
# Django数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'coachai',
        'USER': 'coachai',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'connect_timeout': 10,
        },
        'CONN_MAX_AGE': 60,  # 连接池保持时间
        'CONN_HEALTH_CHECKS': True,
    }
}
```

### 7.2 Django 性能优化

#### 7.2.1 缓存优化
```python
# 使用数据库缓存
from django.core.cache import cache

class DatabaseCacheBackend:
    def get(self, key):
        try:
            cache_obj = DatabaseCache.objects.get(
                key=key,
                expires_at__gt=timezone.now()
            )
            return cache_obj.value
        except DatabaseCache.DoesNotExist:
            return None
    
    def set(self, key, value, timeout=300):
        expires_at = timezone.now() + timedelta(seconds=timeout)
        DatabaseCache.objects.update_or_create(
            key=key,
            defaults={'value': value, 'expires_at': expires_at}
        )
```

#### 7.2.2 静态文件优化
```python
# 使用WhiteNoise处理静态文件
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... 其他中间件
]

# 静态文件压缩
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

#### 7.2.3 异步视图优化
```python
# 使用异步视图处理耗时请求
from django.http import JsonResponse
from django.views import View
import asyncio

class AsyncHomeworkView(View):
    async def post(self, request):
        # 异步处理作业上传
        homework_id = await self.process_homework_async(request)
        return JsonResponse({'homework_id': homework_id})
    
    async def process_homework_async(self, request):
        # 模拟异步处理
        await asyncio.sleep(1)
        return 123
```

### 7.3 前端性能优化

#### 7.3.1 代码分割
```javascript
// 动态导入组件
const HomeworkComponent = React.lazy(() => import('./HomeworkComponent'));

function App() {
  return (
    <Suspense fallback={<div>加载中...</div>}>
      <HomeworkComponent />
    </Suspense>
  );
}
```

#### 7.3.2 资源优化
- **图片压缩**：使用WebP格式，适当压缩
- **代码压缩**：生产环境压缩JS和CSS
- **CDN加速**：静态资源使用CDN
- **懒加载**：图片和组件懒加载

## 8. 扩展性设计

### 8.1 水平扩展准备

#### 8.1.1 无状态设计
- **会话外部化**：使用数据库存储会话
- **文件共享**：使用共享文件系统或未来迁移到对象存储
- **配置中心化**：环境变量统一管理
- **服务发现**：为未来微服务做准备

#### 8.1.2 数据库扩展准备
- **读写分离**：代码支持主从读写分离
- **分库分表**：设计支持未来分库分表
- **数据分区**：按时间分区存储历史数据
- **连接池**：支持多数据库连接

### 8.2 垂直扩展策略

#### 8.2.1 硬件升级路径
1. **CPU升级**：从4核升级到8核或更多
2. **内存升级**：从8GB升级到16GB或更多
3. **存储升级**：从HDD升级到SSD，增加容量
4. **网络升级**：增加带宽，优化网络配置

#### 8.2.2 软件优化路径
1. **代码优化**：性能分析和代码优化
2. **配置调优**：系统参数和数据库参数调优
3. **架构调整**：根据业务特点调整架构
4. **缓存引入**：未来引入Redis缓存

### 8.3 功能扩展设计

#### 8.3.1 插件化架构
```python
# 插件系统设计
class Plugin:
    def __init__(self, name):
        self.name = name
    
    def register(self):
        """注册插件"""
        pass
    
    def unregister(self):
        """卸载插件"""
        pass

class PluginManager:
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, plugin):
        self.plugins[plugin.name] = plugin
        plugin.register()
    
    def unregister_plugin(self, name):
        if name in self.plugins:
            self.plugins[name].unregister()
            del self.plugins[name]
```

#### 8.3.2 模块化设计
- **独立应用**：每个功能模块作为独立Django应用
- **清晰接口**：模块间通过定义良好的接口通信
- **松耦合**：模块间依赖最小化
- **可替换**：模块可以独立替换和升级

### 8.4 中间件引入计划

#### 8.4.1 引入时机
1. **用户量增长**：日活跃用户超过1000
2. **性能瓶颈**：数据库成为性能瓶颈
3. **功能需求**：需要实时推送等高级功能
4. **团队规模**：开发团队规模扩大

#### 8.4.2 引入顺序
1. **Redis缓存**：首先引入，解决缓存问题
2. **消息队列**：其次引入，解决异步任务问题
3. **对象存储**：然后引入，解决文件存储问题
4. **监控系统**：最后引入，完善监控体系

#### 8.4.3 平滑迁移方案
- **双写策略**：新旧系统并行运行
- **数据同步**：保证数据一致性
- **流量切换**：逐步切换流量
- **回滚计划**：准备回滚方案

---

## 总结

### 简化架构优势
1. **部署简单**：只需Django + MySQL，部署快速
2. **维护方便**：组件少，故障排查简单
3. **成本可控**：服务器资源需求低
4. **开发高效**：开发者学习成本低

### 未来扩展路径
1. **短期**：优化现有架构，提升性能
2. **中期**：根据需求引入Redis等中间件
3. **长期**：考虑微服务架构改造

### 风险评估
1. **性能风险**：高并发时数据库可能成为瓶颈
2. **扩展风险**：未来架构改造需要成本
3. **技术风险**：依赖单一数据库，故障影响大

### 应对策略
1. **监控预警**：建立完善的监控体系
2. **容量规划**：定期进行容量评估
3. **备份恢复**：完善的备份和恢复机制
4. **渐进演进**：根据实际需求逐步演进架构

---

**文档版本**：3.0.0 (简化版本 - 无中间件)
**最后更新**：2026-03-21
**状态**：草案，待用户审阅
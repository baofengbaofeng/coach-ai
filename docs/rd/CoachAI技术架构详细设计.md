# CoachAI 技术架构详细设计

## 第 1 章 文档概述

### 1.1 文档目的
本文档旨在为CoachAI项目提供全面的技术架构详细设计指导，确保开发团队对系统架构、技术选型、模块设计、接口规范等有统一的理解和遵循。

### 1.2 文档范围
- **技术范围**：Python后端、Vue前端、MySQL数据库、部署运维
- **功能范围**：用户认证、租户管理、作业批改、运动识别等核心功能
- **非功能范围**：性能、安全、高可用、可扩展性设计
- **架构范围**：DDD（领域驱动设计）、EDA（事件驱动架构）

### 1.3 读者对象
- **开发工程师**：了解系统架构、模块设计、编码规范
- **测试工程师**：了解系统功能、接口设计、测试策略
- **运维工程师**：了解部署架构、监控方案、运维流程
- **技术负责人**：了解整体技术架构、技术选型、风险评估
- **产品经理**：了解技术实现约束、功能可行性

### 1.4 术语与缩写解释

| 术语/缩写 | 全称 | 解释 |
|-----------|------|------|
| **SaaS** | Software as a Service | 软件即服务，多租户云服务模式 |
| **OCR** | Optical Character Recognition | 光学字符识别，用于作业批改 |
| **PWA** | Progressive Web App | 渐进式Web应用，支持离线功能 |
| **JWT** | JSON Web Token | JSON Web令牌，用于用户认证 |
| **RESTful** | Representational State Transfer | 表述性状态转移，API设计风格 |
| **ORM** | Object-Relational Mapping | 对象关系映射，数据库操作框架 |
| **DDD** | Domain-Driven Design | 领域驱动设计，软件设计方法 |
| **EDA** | Event-Driven Architecture | 事件驱动架构，系统架构模式 |
| **CI/CD** | Continuous Integration/Deployment | 持续集成/持续部署 |
| **MVP** | Minimum Viable Product | 最小可行产品 |
| **WebRTC** | Web Real-Time Communication | 网页实时通信，用于音视频传输 |
| **AI** | Artificial Intelligence | 人工智能，用于运动识别和作业分析 |

### 1.5 参考资料
1. **产品文档**：
   - `docs/pm/CoachAI业务需求文档（BRD）.md`
   - `docs/pm/CoachAI产品需求文档（PRD）.md`
   - `docs/pm/CoachAI项目产品愿景.md`

2. **技术文档**：
   - `docs/rd/CoachAI技术架构概要设计.md`
   - `docs/rd/CoachAI技术方案实施指南.md`
   - `docs/rd/CoachAI API接口设计.md`
   - `docs/rd/CoachAI部署运维指南.md`

3. **规范文档**：
   - `.rules/coding-style.md` - 项目编码规范
   - `pyproject.toml` - Python项目配置
   - `package.json` - 前端项目配置

4. **外部参考**：
   - Python官方文档：https://docs.python.org/3.12/
   - Tornado文档：https://www.tornadoweb.org/
   - Vue 3文档：https://vuejs.org/
   - MySQL 5.8文档：https://dev.mysql.com/doc/

### 1.6 开发约定

#### 1.6.1 Python版本规范
- **主版本**：Python 3.12.0+
- **虚拟环境**：使用`venv`创建隔离环境
- **依赖管理**：使用`requirements.txt`和`requirements-dev.txt`
- **版本锁定**：生产环境依赖版本需明确指定

#### 1.6.2 编码规范（PEP8扩展）
- **基础规范**：遵循PEP8 Python编码规范
- **项目规范**：严格遵循`.rules/coding-style.md`文件定义
- **注释规范**：所有代码注释必须使用中文编写
- **类型注解**：强制使用类型注解，提高代码可读性
- **文档字符串**：所有函数、类、模块必须有中文文档字符串

#### 1.6.3 接口命名/文件命名规范
- **后端文件**：小写蛇形命名（`user_service.py`, `homework_handler.py`）
- **前端文件**：大驼峰命名（`UserLogin.vue`, `HomeworkList.vue`）
- **数据库表**：统一前缀`coach_ai_` + 小写蛇形命名（`coach_ai_users`）
- **API接口**：RESTful风格，小写蛇形（`/api/v1/users/{id}`）
- **Git分支**：功能分支`feature/功能名`，修复分支`fix/问题描述`

#### 1.6.4 版本管理规范
- **Git工作流**：采用Git Flow工作流
- **提交信息**：遵循Conventional Commits规范
- **版本号**：遵循语义化版本控制（SemVer）
- **代码审查**：所有代码必须经过Code Review才能合并
- **分支保护**：main分支受保护，禁止直接推送

## 第 2 章 项目整体说明

### 2.1 项目业务背景
CoachAI是一个面向中国家庭的智能教育管理SaaS平台，旨在帮助家长轻松管理子女的学习和运动。随着教育信息化和家庭教育需求的增长，家长面临作业批改困难、运动监督不足、时间精力有限等痛点。本项目通过AI技术（OCR识别、动作识别）和硬件外设（摄像头、麦克风）集成，为家长提供一站式的子女教育管理解决方案。

### 2.2 核心功能与业务目标

#### 2.2.1 核心功能
1. **作业批改系统**：
   - 作业图片上传与OCR识别
   - 自动批改与错题分析
   - 知识点总结与学习建议

2. **运动识别系统**：
   - 实时运动计数（跳绳、俯卧撑等）
   - 姿势分析与纠正指导
   - 运动数据统计与报告

3. **家庭管理系统**：
   - 多成员家庭账户管理
   - 学习运动进度跟踪
   - 成就系统与激励体系

#### 2.2.2 业务目标
- **短期目标**（3个月）：完成MVP版本，获取100个种子用户
- **中期目标**（6个月）：功能完善，用户增长至1000个家庭
- **长期目标**（12个月）：平台化运营，建立教育生态

### 2.3 技术选型总原则
1. **成熟稳定**：选择经过生产验证的技术，降低技术风险
2. **开发效率**：选择生态丰富、开发效率高的技术栈
3. **性能优先**：针对实时音视频处理选择高性能框架
4. **成本控制**：MVP阶段简化架构，避免过度设计
5. **扩展性**：设计支持水平扩展的架构，应对用户增长
6. **架构先进**：采用DDD和EDA架构，提高系统可维护性

### 2.4 核心技术栈清单

#### 2.4.1 Web框架
- **主框架**：Tornado 6.4
- **选择理由**：
  - 异步非阻塞，适合高并发实时应用
  - 原生WebSocket支持，适合硬件实时通信
  - 轻量级，启动快速，资源占用少
- **备选方案**：FastAPI（功能丰富）、Django（生态完善）

#### 2.4.2 ASGI/WSGI服务器
- **开发环境**：Tornado内置服务器
- **生产环境**：Gunicorn + Tornado Worker
- **配置示例**：
  ```bash
  gunicorn code.main:app \
    --workers=4 \
    --worker-class=tornado \
    --bind=0.0.0.0:8000 \
    --timeout=120 \
    --access-logfile=-
  ```

#### 2.4.3 ORM框架
- **主框架**：SQLAlchemy 2.0 + Alembic
- **选择理由**：
  - 功能强大，支持复杂查询
  - 异步支持良好
  - 迁移工具完善（Alembic）
  - 支持DDD领域模型设计

#### 2.4.4 数据库
- **主数据库**：MySQL 5.8
- **选择理由**：
  - 成熟稳定，生产验证充分
  - 当前环境支持版本
  - 成本可控，运维简单
- **配置要求**：
  - 字符集：utf8mb4
  - 排序规则：utf8mb4_unicode_ci
  - 存储引擎：InnoDB

#### 2.4.5 前端技术栈
- **核心框架**：Vue 3（纯脚本，无打包编译）
- **UI框架**：Element Plus（移动端适配）
- **HTTP客户端**：Axios
- **状态管理**：Vuex/Pinia（可选）
- **路由管理**：Vue Router（可选）
- **特点**：
  - 无需Node.js编译，直接浏览器运行
  - 与后端代码一起发布，简化部署
  - 支持模块化开发，保持前后端分离

#### 2.4.6 缓存（可选）
- **MVP阶段**：Python内存缓存（`lru_cache`）
- **成长阶段**：Redis 7.0
- **缓存策略**：
  - 用户会话数据
  - 频繁查询结果
  - 配置信息缓存

#### 2.4.7 异步任务
- **MVP阶段**：Tornado异步任务
- **成长阶段**：Celery + Redis
- **任务类型**：
  - OCR识别任务
  - 运动分析任务
  - 报告生成任务

#### 2.4.8 日志/配置/工具库
- **日志系统**：Python logging + structlog
- **配置管理**：Pydantic Settings + 环境变量
- **工具库**：
  - 数据验证：Pydantic
  - HTTP客户端：aiohttp
  - 日期时间：python-dateutil
  - 安全加密：bcrypt, cryptography

#### 2.4.9 测试框架
- **单元测试**：pytest + pytest-asyncio
- **接口测试**：pytest + aiohttp
- **测试覆盖率**：pytest-cov（目标>80%）

#### 2.4.10 部署工具
- **容器化**：Docker + Docker Compose
- **镜像管理**：Docker Hub / 私有仓库
- **编排工具**：Docker Compose（生产考虑K8s）

## 第 3 章 整体技术架构设计

### 3.1 架构设计目标

#### 3.1.1 高可用
- **目标**：系统可用性达到99.9%
- **措施**：
  - 无状态应用设计，支持水平扩展
  - 数据库主从复制，读写分离
  - 负载均衡，故障自动转移
  - 健康检查，自动恢复

#### 3.1.2 可扩展
- **目标**：支持从100到10万用户平滑扩展
- **措施**：
  - 微服务就绪的模块化设计
  - 数据库分片方案设计
  - 缓存层隔离，减少数据库压力
  - 异步处理，提高吞吐量

#### 3.1.3 易维护
- **目标**：新成员1周内可上手开发
- **措施**：
  - 清晰的代码结构和文档
  - 统一的编码规范和工具链
  - 完善的测试覆盖和CI/CD
  - 详细的监控和日志

#### 3.1.4 高性能
- **目标**：API响应时间<100ms，支持1000并发
- **措施**：
  - Tornado异步框架
  - 数据库查询优化
  - 多级缓存策略
  - CDN静态资源加速

### 3.2 系统分层架构（DDD + EDA）

```
┌─────────────────────────────────────────────────────────┐
│                   表现层 (Presentation Layer)            │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│   │   Web前端    │  │ 移动端H5    │  │  管理后台    │    │
│   │  (Vue 3)    │  │ (PWA)       │  │ (Element+)  │    │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│          │                 │                 │          │
└──────────┼─────────────────┼─────────────────┼──────────┘
           │                 │                 │
┌──────────┼─────────────────┼─────────────────┼──────────┐
│                   网关层 (Gateway Layer)                  │
│   ┌──────────────────────────────────────────────┐      │
│   │              Nginx反向代理                    │      │
│   │        • HTTPS终止                           │      │
│   │        • 请求路由                            │      │
│   │        • 负载均衡                            │      │
│   │        • 限流熔断                            │      │
│   └──────────────────────────────────────────────┘      │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────┐
│                   应用层 (Application Layer)              │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│   │  API服务1    │  │  API服务2    │  │  API服务3    │    │
│   │ (Tornado)   │  │ (Tornado)   │  │ (Tornado)   │    │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│          │                 │                 │          │
└──────────┼─────────────────┼─────────────────┼──────────┘
           │                 │                 │
┌──────────┼─────────────────┼─────────────────┼──────────┐
│                   领域层 (Domain Layer)                   │
│   ┌──────────────────────────────────────────────┐      │
│   │           领域模型聚合层                      │      │
│   │  • 用户领域      • 作业领域      • 运动领域     │      │
│   │  • 租户领域      • 成就领域      • 文件领域     │      │
│   │  • 事件发布      • 领域服务      • 仓储接口     │      │
│   └──────────────────────────────────────────────┘      │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────┐
│                   基础设施层 (Infrastructure Layer)       │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│   │   MySQL      │  │   Redis     │  │  对象存储    │    │
│   │  (主从)      │  │  (集群)     │  │  (MinIO)    │    │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│          │                 │                 │          │
└──────────┼─────────────────┼─────────────────┼──────────┘
           │                 │                 │
┌──────────┼─────────────────┼─────────────────┼──────────┐
│                   事件总线层 (Event Bus Layer)           │
│   ┌──────────────────────────────────────────────┐      │
│   │             事件驱动架构                      │      │
│   │  • 事件发布/订阅                            │      │
│   │  • 事件存储                                │      │
│   │  • 事件处理                                │      │
│   │  • Saga模式                                │      │
│   └──────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

### 3.3 整体架构图

```mermaid
graph TB
    subgraph "客户端层"
        A[Web前端 Vue 3] --> G[Nginx网关]
        B[移动端H5 PWA] --> G
        C[管理后台] --> G
    end
    
    subgraph "网关层"
        G --> H[负载均衡]
        H --> I[限流熔断]
        I --> J[请求路由]
    end
    
    subgraph "应用层"
        J --> K1[API服务1]
        J --> K2[API服务2]
        J --> K3[API服务3]
        
        K1 --> L[领域层]
        K2 --> L
        K3 --> L
    end
    
    subgraph "领域层"
        L --> M1[用户领域]
        L --> M2[作业领域]
        L --> M3[运动领域]
        L --> M4[租户领域]
        L --> M5[成就领域]
        
        M1 --> N[基础设施层]
        M2 --> N
        M3 --> N
        M4 --> N
        M5 --> N
        
        M1 --> O[事件总线]
        M2 --> O
        M3 --> O
        M4 --> O
        M5 --> O
    end
    
    subgraph "基础设施层"
        N --> P1[(MySQL主库)]
        N --> P2[(MySQL从库)]
        N --> Q[(Redis缓存)]
        N --> R[(MinIO存储)]
        
        P1 -.-> P2
    end
    
    subgraph "事件总线层"
        O --> S[事件发布]
        O --> T[事件订阅]
        O --> U[事件存储]
        O --> V[Saga协调器]
    end
```

### 3.4 架构核心特点

#### 3.4.1 DDD领域驱动设计
- **领域模型**：用户、租户、作业、运动等核心领域
- **聚合根**：每个领域有明确的聚合根，保证业务一致性
- **领域服务**：封装复杂业务逻辑，保持领域模型纯净
- **仓储模式**：抽象数据访问，支持多种数据源
- **领域事件**：通过事件实现领域间解耦

#### 3.4.2 EDA事件驱动架构
- **事件发布/订阅**：松耦合的组件通信方式
- **事件溯源**：通过事件序列重建系统状态
- **Saga模式**：分布式事务管理
- **CQRS**：命令查询职责分离，优化读写性能
- **最终一致性**：通过事件实现数据最终一致性

#### 3.4.3 前后端分离但统一部署
- **前端架构**：Vue 3纯脚本，无需编译打包
- **后端架构**：Tornado异步Web框架
- **统一部署**：前后端代码一起发布，简化运维
- **API通信**：前端通过Ajax调用后端RESTful API
- **静态资源**：前端资源由Nginx直接提供

#### 3.4.4 SaaS多租户
- **数据隔离**：数据库表级隔离（tenant_id字段）
- **资源配额**：租户级存储、成员、API调用限制
- **配置独立**：每个租户可独立配置功能开关
- **计费灵活**：基于订阅计划的差异化功能

#### 3.4.5 移动端优先
- **PWA支持**：渐进式Web应用，类原生体验
- **离线功能**：Service Worker支持离线数据同步
- **硬件访问**：优化摄像头、麦克风、传感器访问
- **性能优化**：针对移动网络和设备深度优化

### 3.5 系统交互流程

#### 3.5.1 作业批改流程（DDD + EDA）
```
前端 (Vue 3) → 网关 (Nginx) → API服务 (Tornado) → 命令处理器 → 领域层 → 事件发布
     ↑              ↑              ↑              ↑          ↑          ↑
   用户界面        负载均衡       请求处理       命令验证    业务逻辑    事件通知
     ↓              ↓              ↓              ↓          ↓          ↓
1. 拍照上传 → 2. 请求路由 → 3. 参数验证 → 4. 创建命令 → 5. 处理命令 → 6. 发布事件
     ↓              ↓              ↓              ↓          ↓          ↓
7. 显示进度 ← 8. 返回任务ID ← 9. 返回结果 ← 10. 保存聚合 ← 11. 持久化 ← 12. 事件存储
     ↓              ↓              ↓              ↓          ↓          ↓
13.轮询结果 → 14.查询状态 → 15.查询仓储 → 16.获取聚合 → 17.返回数据 → 18.事件处理
```

#### 3.5.2 运动识别流程（实时+EDA）
```
移动端H5 → WebRTC信令 → Tornado服务 → 命令处理器 → 领域层 → 实时事件
    ↑           ↑           ↑           ↑           ↑          ↑
  摄像头       信令交换     连接管理    命令创建    业务逻辑    事件流
    ↓           ↓           ↓           ↓           ↓          ↓
1.开启摄像头 → 2.建立连接 → 3.创建会话 → 4.开始命令 → 5.处理命令 → 6.发布开始事件
    ↓           ↓           ↓           ↓           ↓          ↓
7.实时视频 → 8.传输帧 → 9.接收帧 → 10.分析命令 → 11.分析逻辑 → 12.发布分析事件
    ↓           ↓           ↓           ↓           ↓          ↓
13.显示计数 ← 14.返回结果 ← 15.返回数据 ← 16.更新聚合 ← 17.保存状态 ← 18.事件处理
    ↓           ↓           ↓           ↓           ↓          ↓
19.结束运动 → 20.关闭连接 → 21.结束命令 → 22.结束逻辑 → 23.发布结束事件 → 24.最终处理
```

#### 3.5.3 用户认证流程（DDD）
```
前端应用 → 认证中间件 → 命令处理器 → 用户领域 → 事件发布 → 通知领域
    ↑          ↑          ↑          ↑          ↑          ↑
  登录界面    Token验证   命令验证    业务逻辑    事件通知    通知处理
    ↓          ↓          ↓          ↓          ↓          ↓
1.输入凭证 → 2.提取Token → 3.创建命令 → 4.验证用户 → 5.发布事件 → 6.发送通知
    ↓          ↓          ↓          ↓          ↓          ↓
7.显示错误 ← 8.返回错误 ← 9.验证失败 ← 10.用户无效 ← 11.失败事件 ← 12.错误通知
    ↓          ↓          ↓          ↓          ↓          ↓
13.跳转首页 ← 14.返回用户 ← 15.验证成功 ← 16.用户有效 ← 17.成功事件 ← 18.欢迎通知
```

## 第 4 章 系统分层详细设计

### 4.1 项目目录结构设计

根据要求，项目源代码保存在`code`目录下，具体结构如下：

```
code/
├── main.py                    # 应用入口文件
├── requirements.txt           # Python依赖文件
├── pyproject.toml            # Python项目配置
├── deploy/                   # Docker部署文件
│   ├── Dockerfile           # Docker镜像构建文件
│   ├── docker-compose.yml   # Docker Compose配置
│   ├── nginx/              # Nginx配置
│   │   ├── nginx.conf
│   │   └── ssl/
│   └── scripts/            # 部署脚本
│       ├── start.sh
│       ├── stop.sh
│       └── healthcheck.sh
├── tornado/                  # Tornado后端核心
│   ├── __init__.py
│   ├── settings.py          # 应用配置
│   ├── urls.py              # URL路由配置
│   ├── application.py       # 应用工厂
│   ├── core/                # 核心基础模块
│   │   ├── __init__.py
│   │   ├── middleware.py    # 中间件
│   │   ├── exceptions.py    # 异常处理
│   │   ├── authentication.py # 认证授权
│   │   ├── response.py      # 响应封装
│   │   ├── validator.py     # 参数验证
│   │   └── event_bus.py     # 事件总线
│   ├── modules/             # 按业务拆分模块（DDD领域）
│   │   ├── user/           # 用户领域
│   │   │   ├── __init__.py
│   │   │   ├── commands.py # 命令定义
│   │   │   ├── events.py   # 事件定义
│   │   │   ├── models.py   # 领域模型
│   │   │   ├── services.py # 领域服务
│   │   │   ├── repositories.py # 仓储接口
│   │   │   ├── handlers.py # 命令处理器
│   │   │   └── api.py      # API接口
│   │   ├── tenant/         # 租户领域
│   │   │   ├── __init__.py
│   │   │   ├── commands.py
│   │   │   ├── events.py
│   │   │   ├── models.py
│   │   │   ├── services.py
│   │   │   ├── repositories.py
│   │   │   ├── handlers.py
│   │   │   └── api.py
│   │   ├── homework/       # 作业领域
│   │   │   ├── __init__.py
│   │   │   ├── commands.py
│   │   │   ├── events.py
│   │   │   ├── models.py
│   │   │   ├── services.py
│   │   │   ├── repositories.py
│   │   │   ├── handlers.py
│   │   │   └── api.py
│   │   ├── exercise/       # 运动领域
│   │   │   ├── __init__.py
│   │   │   ├── commands.py
│   │   │   ├── events.py
│   │   │   ├── models.py
│   │   │   ├── services.py
│   │   │   ├── repositories.py
│   │   │   ├── handlers.py
│   │   │   └── api.py
│   │   └── achievement/    # 成就领域
│   │       ├── __init__.py
│   │       ├── commands.py
│   │       ├── events.py
│   │       ├── models.py
│   │       ├── services.py
│   │       ├── repositories.py
│   │       ├── handlers.py
│   │       └── api.py
│   ├── infrastructure/      # 基础设施层
│   │   ├── __init__.py
│   │   ├── database/       # 数据库相关
│   │   │   ├── __init__.py
│   │   │   ├── pool.py     # 数据库连接池
│   │   │   ├── session.py  # 会话管理
│   │   │   └── migrations/ # 数据库迁移
│   │   ├── cache/          # 缓存相关
│   │   │   ├── __init__.py
│   │   │   ├── redis_client.py
│   │   │   └── memory_cache.py
│   │   ├── storage/        # 存储相关
│   │   │   ├── __init__.py
│   │   │   ├── file_storage.py
│   │   │   └── minio_client.py
│   │   └── external/       # 外部服务
│   │       ├── __init__.py
│   │       ├── ocr_service.py
│   │       ├── ai_service.py
│   │       └── webrtc_service.py
│   └── utils/              # 工具类
│       ├── __init__.py
│       ├── datetime_utils.py
│       ├── string_utils.py
│       ├── encryption_utils.py
│       └── file_utils.py
├── database/                # 数据库相关
│   ├── __init__.py
│   ├── pool.py             # MySQL高级连接池
│   ├── models.py           # ORM模型（SQLAlchemy）
│   ├── repositories/       # 仓储实现
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── tenant_repository.py
│   │   ├── homework_repository.py
│   │   ├── exercise_repository.py
│   │   └── achievement_repository.py
│   └── migrations/         # Alembic迁移
│       ├── versions/
│       ├── env.py
│       └── alembic.ini
└── web/                    # 前端代码（Vue 3纯脚本）
    ├── index.html          # 主入口文件
    ├── assets/             # 静态资源
    │   ├── css/
    │   │   ├── app.css
    │   │   ├── components.css
    │   │   └── responsive.css
    │   ├── js/
    │   │   ├── lib/        # 第三方库
    │   │   │   ├── vue.global.js
    │   │   │   ├── element-plus.js
    │   │   │   └── axios.js
    │   │   └── utils/      # 工具函数
    │   │       ├── api.js
    │   │       ├── auth.js
    │   │       └── utils.js
    │   └── images/         # 图片资源
    │       ├── logo.png
    │       ├── icons/
    │       └── avatars/
    ├── components/         # 公共Vue组件
    │   ├── common/         # 通用组件
    │   │   ├── Header.vue
    │   │   ├── Footer.vue
    │   │   ├── Sidebar.vue
    │   │   └── Loading.vue
    │   ├── forms/          # 表单组件
    │   │   ├── InputField.vue
    │   │   ├── SelectField.vue
    │   │   ├── UploadField.vue
    │   │   └── FormValidator.vue
    │   └── ui/             # UI组件
    │       ├── Button.vue
    │       ├── Card.vue
    │       ├── Modal.vue
    │       └── Toast.vue
    ├── pages/              # 按模块对应页面
    │   ├── auth/           # 认证页面
    │   │   ├── Login.vue
    │   │   ├── Register.vue
    │   │   └── ForgotPassword.vue
    │   ├── user/           # 用户页面
    │   │   ├── Profile.vue
    │   │   ├── Settings.vue
    │   │   └── Dashboard.vue
    │   ├── tenant/         # 租户页面
    │   │   ├── CreateTenant.vue
    │   │   ├── TenantList.vue
    │   │   └── TenantDetail.vue
    │   ├── homework/       # 作业页面
    │   │   ├── UploadHomework.vue
    │   │   ├── HomeworkList.vue
    │   │   └── HomeworkDetail.vue
    │   ├── exercise/       # 运动页面
    │   │   ├── StartExercise.vue
    │   │   ├── ExerciseList.vue
    │   │   └── ExerciseDetail.vue
    │   └── achievement/    # 成就页面
    │       ├── AchievementList.vue
    │       └── AchievementDetail.vue
    ├── config.js           # Vue全局配置
    ├── router.js           # 前端路由配置
    ├── store.js            # 状态管理配置
    └── app.js              # Vue应用初始化
```

### 4.2 接入层设计

#### 4.2.1 反向代理（Nginx）
```nginx
# nginx.conf 核心配置
http {
    # 上游服务配置
    upstream coachai_backend {
        least_conn;  # 最少连接负载均衡
        server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
        server 127.0.0.1:8002 max_fails=3 fail_timeout=30s;
        server 127.0.0.1:8003 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }
    
    # WebSocket上游
    upstream coachai_websocket {
        ip_hash;  # WebSocket需要会话保持
        server 127.0.0.1:8001;
        server 127.0.0.1:8002;
        server 127.0.0.1:8003;
    }
    
    server {
        listen 80;
        server_name coachai.example.com;
        
        # HTTPS重定向
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name coachai.example.com;
        
        # SSL配置
        ssl_certificate /etc/nginx/ssl/coachai.crt;
        ssl_certificate_key /etc/nginx/ssl/coachai.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;
        
        # 安全头部
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        
        # 前端静态资源
        location / {
            root /var/www/coachai/web;
            index index.html;
            try_files $uri $uri/ /index.html;
            
            # 缓存策略
            expires 1h;
            add_header Cache-Control "public, max-age=3600";
        }
        
        # 静态资源服务
        location /assets/ {
            root /var/www/coachai/web;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # API路由
        location /api# CoachAI 技术架构详细设计（续写部分）

## 第 7 章 数据存储设计（续）

### 7.4 索引设计与优化

#### 7.4.1 索引设计原则
1. **主键索引**：所有表必须有主键索引
2. **唯一索引**：唯一约束字段建立唯一索引
3. **外键索引**：所有外键字段建立索引
4. **查询索引**：频繁查询条件字段建立索引
5. **组合索引**：多条件查询建立组合索引

#### 7.4.2 核心表索引设计
```sql
-- 用户表索引
CREATE INDEX idx_users_tenant_id ON coach_ai_users(tenant_id);
CREATE INDEX idx_users_created_at ON coach_ai_users(created_at);
CREATE INDEX idx_users_status ON coach_ai_users(is_active, is_verified, is_locked);

-- 作业表索引
CREATE INDEX idx_homeworks_tenant_student ON coach_ai_homeworks(tenant_id, student_id);
CREATE INDEX idx_homeworks_subject_status ON coach_ai_homeworks(subject, status);
CREATE INDEX idx_homeworks_submitted_at ON coach_ai_homeworks(submitted_at);

-- 运动记录表索引
CREATE INDEX idx_exercise_tenant_student ON coach_ai_exercise_records(tenant_id, student_id);
CREATE INDEX idx_exercise_type_date ON coach_ai_exercise_records(exercise_type, started_at);
```

#### 7.4.3 索引优化策略
1. **覆盖索引**：查询只通过索引就能返回所需数据
2. **前缀索引**：对长字符串字段使用前缀索引
3. **索引合并**：MySQL自动合并多个单列索引
4. **索引下推**：在存储引擎层过滤数据

### 7.5 缓存设计（Redis策略）

#### 7.5.1 缓存层级设计
1. **L1缓存**：应用内存缓存（LRU Cache）
2. **L2缓存**：Redis分布式缓存
3. **L3缓存**：数据库查询缓存

#### 7.5.2 Redis缓存策略
```python
# code/tornado/infrastructure/cache/redis_client.py
import redis
import json
from typing import Optional, Any
import asyncio

class RedisCache:
    """Redis缓存客户端"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            value = await asyncio.get_event_loop().run_in_executor(
                None, self.redis.get, key
            )
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            # 缓存失败不影响主流程
            return None
    
    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存"""
        try:
            json_value = json.dumps(value, ensure_ascii=False)
            return await asyncio.get_event_loop().run_in_executor(
                None, self.redis.setex, key, expire, json_value
            )
        except Exception as e:
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            return await asyncio.get_event_loop().run_in_executor(
                None, self.redis.delete, key
            ) > 0
        except Exception as e:
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存"""
        try:
            keys = await asyncio.get_event_loop().run_in_executor(
                None, self.redis.keys, pattern
            )
            if keys:
                return await asyncio.get_event_loop().run_in_executor(
                    None, self.redis.delete, *keys
                )
            return 0
        except Exception as e:
            return 0
```

#### 7.5.3 缓存使用场景
1. **用户会话缓存**：JWT Token、用户信息
2. **配置信息缓存**：系统配置、租户配置
3. **热点数据缓存**：频繁查询的业务数据
4. **计算结果缓存**：OCR结果、运动分析结果
5. **分布式锁**：防止重复操作、并发控制

#### 7.5.4 缓存失效策略
1. **时间失效**：设置合理的过期时间
2. **事件失效**：数据变更时主动清除缓存
3. **版本失效**：缓存键包含数据版本号
4. **容量失效**：LRU算法淘汰旧缓存

### 7.6 数据备份与恢复方案

#### 7.6.1 备份策略
1. **全量备份**：每日凌晨进行全量备份
2. **增量备份**：每小时进行增量备份
3. **日志备份**：实时备份二进制日志
4. **异地备份**：备份数据存储到异地

#### 7.6.2 备份工具
- **mysqldump**：逻辑备份，适合小数据量
- **xtrabackup**：物理备份，适合大数据量
- **MySQL Enterprise Backup**：企业级备份工具

#### 7.6.3 恢复方案
1. **全量恢复**：从全量备份恢复
2. **时间点恢复**：结合全量备份和二进制日志
3. **表级恢复**：恢复单个表或数据库
4. **演练测试**：定期进行恢复演练

### 7.7 数据迁移方案

#### 7.7.1 迁移工具
- **Alembic**：SQLAlchemy数据库迁移工具
- **Flyway**：数据库版本控制工具
- **自定义脚本**：复杂迁移场景

#### 7.7.2 迁移流程
1. **开发环境**：开发人员本地迁移
2. **测试环境**：自动化测试验证
3. **预发布环境**：生产数据验证
4. **生产环境**：低峰期执行迁移

#### 7.7.3 回滚方案
1. **向前兼容**：新版本兼容旧数据
2. **版本回退**：回退到上一个版本
3. **数据回滚**：从备份恢复数据
4. **灰度发布**：逐步验证迁移效果

## 第 8 章 非功能需求设计

### 8.1 性能设计

#### 8.1.1 并发能力
- **目标**：支持1000并发用户
- **措施**：
  - Tornado异步框架，单进程支持数千连接
  - 数据库连接池，减少连接创建开销
  - Redis缓存，减少数据库压力
  - CDN加速，减少网络延迟

#### 8.1.2 接口响应时间
- **目标**：API响应时间<100ms
- **措施**：
  - 数据库查询优化，使用索引
  - 多级缓存策略，减少IO操作
  - 异步处理，非阻塞IO
  - 代码优化，减少计算复杂度

#### 8.1.3 性能优化方案
1. **数据库优化**：
   - 查询优化，避免全表扫描
   - 索引优化，覆盖索引
   - 分库分表，水平扩展
   - 读写分离，负载均衡

2. **缓存优化**：
   - 热点数据缓存
   - 查询结果缓存
   - 页面片段缓存
   - CDN静态资源缓存

3. **代码优化**：
   - 异步编程，避免阻塞
   - 算法优化，减少复杂度
   - 内存管理，避免泄漏
   - 连接复用，减少开销

### 8.2 安全设计

#### 8.2.1 身份认证
- **JWT Token**：无状态认证，支持分布式
- **多因素认证**：短信验证码、邮箱验证
- **会话管理**：Token刷新、超时控制
- **防暴力破解**：登录失败次数限制

#### 8.2.2 接口权限控制
- **RBAC模型**：基于角色的访问控制
- **数据权限**：租户级数据隔离
- **操作权限**：细粒度操作控制
- **API权限**：接口级别权限验证

#### 8.2.3 安全防护
1. **SQL注入防护**：
   - 参数化查询
   - ORM框架防护
   - 输入验证过滤

2. **XSS防护**：
   - 输入输出编码
   - CSP安全策略
   - 内容安全过滤

3. **CSRF防护**：
   - Token验证
   - SameSite Cookie
   - Referer检查

4. **文件上传安全**：
   - 文件类型验证
   - 文件大小限制
   - 病毒扫描
   - 存储隔离

#### 8.2.4 密码加密
- **算法**：bcrypt + salt
- **强度**：最小8位，包含大小写数字
- **策略**：定期更换，历史密码检查
- **存储**：加密存储，不可逆

#### 8.2.5 敏感数据脱敏
- **个人信息**：手机号、邮箱部分隐藏
- **支付信息**：银行卡号加密存储
- **日志脱敏**：敏感信息不记录日志
- **数据传输**：HTTPS加密传输

### 8.3 高可用设计

#### 8.3.1 服务容错
- **健康检查**：定期检查服务状态
- **故障转移**：自动切换到备用节点
- **服务降级**：非核心功能降级处理
- **熔断机制**：防止雪崩效应

#### 8.3.2 重试/降级机制
1. **重试策略**：
   - 指数退避重试
   - 最大重试次数限制
   - 重试条件判断

2. **降级策略**：
   - 功能降级：关闭非核心功能
   - 数据降级：返回缓存数据
   - 服务降级：调用备用服务

#### 8.3.3 单点故障规避
1. **无状态设计**：服务无状态，支持水平扩展
2. **多副本部署**：关键服务多副本部署
3. **负载均衡**：多节点负载均衡
4. **数据冗余**：数据多副本存储

### 8.4 可扩展性设计

#### 8.4.1 模块化设计
- **微服务就绪**：模块可独立部署
- **领域驱动**：按业务领域划分模块
- **接口标准化**：标准化模块间接口
- **依赖管理**：清晰模块依赖关系

#### 8.4.2 水平扩展方案
1. **应用层扩展**：
   - 无状态应用，支持水平扩展
   - 负载均衡，流量分发
   - 服务发现，动态扩缩容

2. **数据层扩展**：
   - 读写分离，主从复制
   - 分库分表，数据分片
   - 缓存集群，分布式缓存

3. **存储层扩展**：
   - 对象存储，无限扩展
   - CDN加速，全球分发
   - 文件分片，并行处理

## 第 9 章 部署与运维设计

### 9.1 环境规划

#### 9.1.1 开发环境
- **目的**：开发人员本地开发调试
- **配置**：本地Docker环境
- **数据库**：本地MySQL实例
- **部署**：Docker Compose一键部署

#### 9.1.2 测试环境
- **目的**：自动化测试、集成测试
- **配置**：与生产环境一致
- **数据**：测试数据，定期清理
- **部署**：CI/CD自动部署

#### 9.1.3 预发布环境
- **目的**：生产前验证
- **配置**：与生产环境完全一致
- **数据**：生产数据副本
- **部署**：手动部署，严格验证

#### 9.1.4 生产环境
- **目的**：线上服务
- **配置**：高可用集群配置
- **数据**：生产真实数据
- **部署**：蓝绿部署，滚动更新

### 9.2 容器化部署（Docker）

#### 9.2.1 Dockerfile
```dockerfile
# 基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 复制前端代码
COPY web/ /app/web/

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "code.main:app", \
     "--workers", "4", \
     "--worker-class", "tornado", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-"]
```

#### 9.2.2 Docker Compose配置
```yaml
version: '3.8'

services:
  # MySQL数据库
  mysql:
    image: mysql:5.8
    container_name: coachai-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: coachai
      MYSQL_USER: coachai
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./deploy/mysql/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "3306:3306"
    networks:
      - coachai-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: coachai-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - coachai-network
    command: redis-server --appendonly yes

  # 应用服务
  app:
    build: .
    container_name: coachai-app
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_started
    environment:
      DATABASE_URL: mysql+pymysql://coachai:${MYSQL_PASSWORD}@mysql:3306/coachai
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    networks:
      - coachai-network
    restart: unless-stopped

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    container_name: coachai-nginx
    depends_on:
      - app
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deploy/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./deploy/nginx/ssl:/etc/nginx/ssl
      - ./web:/var/www/coachai/web
      - ./logs/nginx:/var/log/nginx
    networks:
      - coachai-network

networks:
  coachai-network:
    driver: bridge

volumes:
  mysql_data:
  redis_data:
```

### 9.3 服务编排

#### 9.3.1 开发环境编排
- **单节点部署**：所有服务部署在单台机器
- **本地开发**：支持热重载，快速迭代
- **数据持久化**：数据卷挂载，数据不丢失

#### 9.3.2 生产环境编排
- **多节点集群**：服务分布式部署
- **负载均衡**：Nginx + 应用集群
- **数据高可用**：MySQL主从 + Redis集群
- **监控告警**：Prometheus + Grafana + Alertmanager

### 9.4 CI/CD持续集成流程

#### 9.4.1 流水线设计
1. **代码提交**：触发CI/CD流水线
2. **代码检查**：代码规范、安全扫描
3. **单元测试**：自动化单元测试
4. **构建镜像**：Docker镜像构建
5. **集成测试**：容器化集成测试
6. **部署测试**：部署到测试环境
7. **自动化测试**：接口测试、性能测试
8. **生产部署**：蓝绿部署、滚动更新

#### 9.4.2 GitLab CI配置
```yaml
stages:
  - check
  - test
  - build
  - deploy-test
  - deploy-prod

variables:
  DOCK## 第 10 章 监控与日志设计

### 10.1 日志规范

#### 10.1.1 日志级别
- **DEBUG**：调试信息，开发环境使用
- **INFO**：普通信息，记录正常操作
- **WARNING**：警告信息，需要注意但不影响运行
- **ERROR**：错误信息，影响单个请求
- **CRITICAL**：严重错误，影响系统运行

#### 10.1.2 日志格式
```python
# code/tornado/core/logging.py
import logging
import structlog
from datetime import datetime
import json

def setup_logging():
    """配置结构化日志"""
    
    # 基础日志配置
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 结构化日志配置
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()

# 使用示例
logger = setup_logging()

# 结构化日志记录
logger.info("用户登录成功", 
           user_id=123, 
           ip="192.168.1.100", 
           duration=0.15)

logger.error("数据库连接失败",
            error="Connection refused",
            retry_count=3,
            endpoint="mysql://localhost:3306")
```

#### 10.1.3 日志内容规范
1. **请求日志**：记录所有API请求和响应
2. **业务日志**：记录关键业务操作
3. **错误日志**：记录所有异常和错误
4. **性能日志**：记录接口响应时间、数据库查询时间
5. **审计日志**：记录敏感操作，用于安全审计

### 10.2 日志收集与存储

#### 10.2.1 日志收集方案
- **文件日志**：本地文件存储，按日期分割
- **集中日志**：ELK Stack（Elasticsearch + Logstash + Kibana）
- **云日志**：阿里云SLS、腾讯云CLS
- **实时日志**：WebSocket实时推送

#### 10.2.2 日志存储策略
1. **热数据**：最近7天日志，快速查询
2. **温数据**：7-30天日志，压缩存储
3. **冷数据**：30天以上日志，归档存储
4. **永久存储**：审计日志永久保存

#### 10.2.3 日志轮转配置
```python
# logging配置文件
import logging.handlers

# 文件处理器
file_handler = logging.handlers.RotatingFileHandler(
    filename='logs/app.log',
    maxBytes=10485760,  # 10MB
    backupCount=10,
    encoding='utf-8'
)

# 时间轮转处理器
time_handler = logging.handlers.TimedRotatingFileHandler(
    filename='logs/app.log',
    when='midnight',  # 每天轮转
    interval=1,
    backupCount=30,   # 保留30天
    encoding='utf-8'
)
```

### 10.3 系统监控指标

#### 10.3.1 基础监控
1. **CPU使用率**：系统CPU使用情况
2. **内存使用率**：系统内存使用情况
3. **磁盘使用率**：磁盘空间使用情况
4. **网络流量**：网络流入流出流量
5. **进程状态**：关键进程运行状态

#### 10.3.2 应用监控
1. **接口响应时间**：API接口平均响应时间
2. **接口成功率**：API接口成功调用比例
3. **并发连接数**：当前活跃连接数
4. **请求吞吐量**：单位时间处理请求数
5. **错误率**：错误请求比例

#### 10.3.3 业务监控
1. **用户活跃度**：日活、月活用户数
2. **业务成功率**：核心业务成功率
3. **数据增长**：用户数、作业数、运动记录数
4. **资源使用**：存储空间、API调用次数
5. **收入指标**：订阅收入、付费用户数

#### 10.3.4 监控工具
- **Prometheus**：指标收集和存储
- **Grafana**：数据可视化
- **Node Exporter**：系统指标收集
- **cAdvisor**：容器监控
- **自定义Exporter**：业务指标收集

### 10.4 告警机制

#### 10.4.1 告警级别
- **P0（紧急）**：系统不可用，需要立即处理
- **P1（重要）**：核心功能异常，需要尽快处理
- **P2（警告）**：非核心功能异常，需要关注
- **P3（提示）**：系统指标异常，需要观察

#### 10.4.2 告警规则
```yaml
# Prometheus告警规则
groups:
  - name: coachai_alerts
    rules:
      # 系统告警
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CPU使用率过高"
          description: "实例 {{ $labels.instance }} CPU使用率超过80%"
      
      # 应用告警
      - alert: HighAPIErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "API错误率过高"
          description: "API错误率超过5%"
      
      # 业务告警
      - alert: LowUserActivity
        expr: active_users < 10
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "用户活跃度低"
          description: "活跃用户数低于10"
```

#### 10.4.3 告警通知渠道
1. **即时通讯**：钉钉、企业微信、Slack
2. **短信通知**：重要告警短信通知
3. **邮件通知**：详细告警邮件通知
4. **电话通知**：紧急告警电话通知
5. **值班系统**：告警自动分配值班人员

#### 10.4.4 告警处理流程
1. **告警触发**：监控系统检测到异常
2. **告警通知**：通过多渠道通知相关人员
3. **问题确认**：值班人员确认问题
4. **问题处理**：按照预案处理问题
5. **问题复盘**：问题解决后进行复盘
6. **规则优化**：根据复盘优化告警规则

## 第 11 章 测试设计

### 11.1 测试策略

#### 11.1.1 测试金字塔
```
        E2E测试 (10%)
           ↑
     集成测试 (20%)
           ↑
     单元测试 (70%)
```

#### 11.1.2 测试类型
1. **单元测试**：测试单个函数或类
2. **集成测试**：测试模块间集成
3. **接口测试**：测试API接口
4. **性能测试**：测试系统性能
5. **安全测试**：测试系统安全性
6. **兼容性测试**：测试浏览器兼容性

#### 11.1.3 测试环境
- **开发环境**：开发人员本地测试
- **测试环境**：自动化测试环境
- **预发布环境**：生产前验证环境
- **生产环境**：线上监控和测试

### 11.2 单元测试（pytest）

#### 11.2.1 测试框架
```python
# tests/unit/test_user_service.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from code.tornado.modules.user.services import UserService
from code.tornado.modules.user.models import User

class TestUserService:
    """用户服务单元测试"""
    
    @pytest.fixture
    def mock_repository(self):
        """模拟仓储"""
        repo = Mock()
        repo.get_by_email = AsyncMock(return_value=None)
        repo.create = AsyncMock(return_value=User(id=1, email="test@example.com"))
        return repo
    
    @pytest.fixture
    def user_service(self, mock_repository):
        """用户服务实例"""
        return UserService(repository=mock_repository)
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, mock_repository):
        """测试创建用户成功"""
        # 准备测试数据
        email = "test@example.com"
        password = "Password123"
        
        # 执行测试
        user = await user_service.create_user(email, password)
        
        # 验证结果
        assert user is not None
        assert user.id == 1
        assert user.email == email
        mock_repository.get_by_email.assert_called_once_with(email)
        mock_repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, user_service, mock_repository):
        """测试创建用户邮箱重复"""
        # 模拟邮箱已存在
        mock_repository.get_by_email.return_value = User(id=2, email="test@example.com")
        
        # 执行测试并验证异常
        with pytest.raises(ValueError, match="邮箱已存在"):
            await user_service.create_user("test@example.com", "Password123")
```

#### 11.2.2 测试覆盖率
- **目标**：单元测试覆盖率 > 80%
- **工具**：pytest-cov
- **命令**：`pytest --cov=code --cov-report=html`
- **报告**：生成HTML覆盖率报告

#### 11.2.3 测试最佳实践
1. **测试命名**：test_方法名_场景_预期结果
2. **测试隔离**：每个测试独立，不依赖其他测试
3. **测试数据**：使用fixture管理测试数据
4. **模拟对象**：使用mock模拟外部依赖
5. **断言清晰**：断言信息明确，便于调试

### 11.3 接口自动化测试

#### 11.3.1 测试框架
```python
# tests/integration/test_user_api.py
import pytest
import aiohttp
import asyncio
from aiohttp import web

class TestUserAPI:
    """用户API接口测试"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        from code.main import create_app
        return create_app(testing=True)
    
    @pytest.fixture
    def client(self, aiohttp_client, app):
        """创建测试客户端"""
        return aiohttp_client(app)
    
    @pytest.mark.asyncio
    async def test_user_register_success(self, client):
        """测试用户注册成功"""
        # 准备请求数据
        data = {
            "email": "test@example.com",
            "password": "Password123",
            "nickname": "测试用户"
        }
        
        # 发送请求
        resp = await client.post("/api/v1/auth/register", json=data)
        
        # 验证响应
        assert resp.status == 201
        result = await resp.json()
        assert result["code"] == "SUCCESS"
        assert "data" in result
        assert "user_id" in result["data"]
    
    @pytest.mark.asyncio
    async def test_user_register_invalid_email(self, client):
        """测试用户注册邮箱格式错误"""
        data = {
            "email": "invalid-email",
            "password": "Password123"
        }
        
        resp = await client.post("/api/v1/auth/register", json=data)
        
        assert resp.status == 400
        result = await resp.json()
        assert result["code"] == "VALIDATION_ERROR"
```

#### 11.3.2 测试数据管理
1. **测试数据库**：使用测试专用数据库
2. **数据清理**：每个测试前后清理数据
3. **数据工厂**：使用factory生成测试数据
4. **数据断言**：验证数据库状态变化

#### 11.3.3 测试场景覆盖
1. **正常场景**：正常业务流程测试
2. **异常场景**：错误输入、异常情况测试
3. **边界场景**：边界条件测试
4. **并发场景**：并发操作测试
5. **安全场景**：安全漏洞测试

### 11.4 测试覆盖率要求

#### 11.4.1 覆盖率指标
- **语句覆盖率**：> 80%
- **分支覆盖率**：> 70%
- **函数覆盖率**：> 85%
- **行覆盖率**：> 80%

#### 11.4.2 覆盖率工具
- **pytest-cov**：Python测试覆盖率
- **coverage.py**：覆盖率分析工具
- **SonarQube**：代码质量平台
- **Codecov**：在线覆盖率服务

#### 11.4.3 覆盖率报告
```bash
# 运行测试并生成覆盖率报告
pytest --cov=code --cov-report=html --cov-report=xml

# 查看覆盖率报告
open htmlcov/index.html

# 上传覆盖率到Codecov
codecov -f coverage.xml
```

### 11.5 测试工具

#### 11.5.1 单元测试工具
- **pytest**：测试框架
- **pytest-asyncio**：异步测试支持
- **pytest-mock**：模拟对象支持
- **pytest-cov**：覆盖率工具

#### 11.5.2 接口测试工具
- **aiohttp**：异步HTTP客户端
- **requests**：同步HTTP客户端
- **Postman**：API测试工具
- **Swagger UI**：API文档和测试

#### 11.5.3 性能测试工具
- **locust**：分布式负载测试
- **k6**：现代负载测试工具
- **JMeter**：传统性能测试工具
- **wrk**：HTTP基准测试工具

#### 11.5.4 安全测试工具
- **bandit**：Python安全漏洞扫描
- **safety**：依赖安全扫描
- **OWASP ZAP**：Web应用安全测试
- **sqlmap**：SQL注入测试

## 第 12 章 风险评估与应对方案

### 12.1 技术风险

#### 12.1.1 技术选型风险
1. **风险描述**：选择的技术栈不成熟或社区支持不足
2. **影响程度**：高
3. **发生概率**：中
4. **应对措施**：
   - 选择经过生产验证的技术
   - 评估技术社区活跃度
   - 准备备选技术方案
   - 进行技术原型验证

#### 12.1.2 技术实现风险
1. **风险描述**：技术实现复杂度高，开发进度延迟
2. **影响程度**：中
3. **发生概率**：高
4. **应对措施**：
   - 采用渐进式开发策略
   - 优先实现核心功能
   - 定期进行代码审查
   - 建立技术债务管理机制

#### 12.1.3 技术依赖风险
1. **风险描述**：依赖的第三方服务不稳定或停止服务
2. **影响程度**：高
3. **发生概率**：低
4. **应对措施**：
   - 选择多个供应商备选
   - 建立服务降级机制
   - 定期评估依赖服务状态
   - 准备自研替代方案

### 12.2 性能风险

#### 12.2.1 数据库性能风险
1. **风险描述**：数据库成为性能瓶颈，响应时间变慢
2. **影响程度**：高
3. **发生概率**：中
4. **应对措施**：
   - 数据库查询优化
   - 建立数据库索引
   - 实施读写分离
   - 准备分库分表方案

#### 12.2.2 应用性能风险
1. **风险描述**：应用服务器性能不足，无法支撑高并发
2. **影响程度**：高
3. **发生概率**：中
4. **应对措施**：
   - 代码性能优化
   - 实施缓存策略
   - 支持水平扩展
   - 定期性能测试

#### 12.2.3 网络性能风险
1. **风险描述**：网络延迟高，影响用户体验
2. **影响程度**：中
3. **发生概率**：低
4. **应对措施**：
   - 使用CDN加速
   - 优化资源加载
   - 实施连接复用
   - 监控网络性能

### 12.3 安全风险

#### 12.3.1 数据安全风险
1. **风险描述**：用户数据泄露或被篡改
2. **影响程度**：极高
3. **发生概率**：低
4. **应对措施**：
   - 数据加密存储
   - 访问权限控制
   - 数据备份恢复
   - 安全
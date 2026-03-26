# CoachAI 技术详细设计（Tornado版）

## 📋 文档信息

| 项目 | 内容 |
|------|------|
| **文档名称** | CoachAI 技术详细设计（Tornado版） |
| **文档版本** | 3.0.0 |
| **创建日期** | 2026-03-26 |
| **最后更新** | 2026-03-26 |
| **文档状态** | 正式版 |
| **作者** | CoachAI-RD (后端研发专家) |
| **审核人** | 待定 |
| **关联文档** | [技术架构概要设计.md](./CoachAI技术架构概要设计.md) |
| **目标读者** | 开发团队、测试团队、运维团队 |

## 📝 修订历史

| 版本 | 日期 | 作者 | 变更描述 |
|------|------|------|----------|
| 3.0.0 | 2026-03-26 | CoachAI-RD | 基于Tornado框架的详细技术设计 |

## 🎯 设计目标

### 1.1 核心设计目标
1. **高性能**：利用Tornado异步特性，支持高并发实时处理
2. **可维护**：代码结构清晰，符合编码规范，便于团队协作
3. **可扩展**：模块化设计，支持功能快速迭代和水平扩展
4. **安全可靠**：数据安全、权限控制、错误处理完善

### 1.2 代码规范要求
1. **编码规范**：所有前后端代码必须严格遵循`.rules/coding-style.md`文件定义的规则
2. **注释规范**：所有代码注释必须使用中文编写，确保团队理解一致
3. **命名规范**：遵循统一的命名约定，提高代码可读性
4. **质量检查**：建立代码审查机制，确保代码规范执行
5. **开源协议**：项目使用GPL V3开源协议，所有衍生代码需保持开源

### 1.2 技术约束
1. **Python 3.12**：使用venv虚拟环境，确保环境隔离
2. **Tornado框架**：异步Web框架，适合实时应用
3. **MySQL数据库**：关系型数据库，支持事务和复杂查询
4. **编码规范**：严格遵循项目编码规范，中文注释

## 📁 项目结构设计

### 2.1 项目目录结构
```
coach-ai-backend/
├── README.md                           # 项目说明文档
├── requirements.txt                    # Python依赖包列表
├── requirements-dev.txt                # 开发环境依赖包
├── pyproject.toml                      # 项目配置和构建工具配置
├── .env.example                        # 环境变量示例文件
├── .gitignore                         # Git忽略文件配置
├── .python-version                    # Python版本指定文件
│
├── src/                                # 源代码目录
│   ├── __init__.py                     # 包初始化文件
│   ├── main.py                         # 应用入口文件
│   ├── config/                         # 配置模块
│   │   ├── __init__.py
│   │   ├── settings.py                 # 应用配置
│   │   ├── database.py                 # 数据库配置
│   │   └── logging_config.py           # 日志配置
│   │
│   ├── core/                           # 核心模块
│   │   ├── __init__.py
│   │   ├── exceptions.py               # 自定义异常类
│   │   ├── middleware.py               # 中间件
│   │   ├── authentication.py           # 认证授权
│   │   ├── tenant.py                   # 租户管理
│   │   └── cache.py                    # 缓存管理
│   │
│   ├── api/                            # API接口层
│   │   ├── __init__.py
│   │   ├── v1/                         # API版本1
│   │   │   ├── __init__.py
│   │   │   ├── handlers/               # 请求处理器
│   │   │   │   ├── __init__.py
│   │   │   │   ├── health.py           # 健康检查
│   │   │   │   ├── auth.py             # 认证相关
│   │   │   │   ├── tenant.py           # 租户管理
│   │   │   │   ├── family.py           # 家庭管理
│   │   │   │   ├── exercise.py         # 运动管理
│   │   │   │   ├── homework.py         # 作业管理
│   │   │   │   └── webrtc.py           # WebRTC相关
│   │   │   ├── schemas/                # 请求响应模型
│   │   │   └── routers.py              # 路由配置
│   │   └── docs.py                     # API文档生成
│   │
│   ├── services/                       # 业务服务层
│   │   ├── __init__.py
│   │   ├── tenant_service.py           # 租户服务
│   │   ├── family_service.py           # 家庭服务
│   │   ├── exercise_service.py          # 运动服务
│   │   ├── homework_service.py          # 作业服务
│   │   ├── ai_service.py               # AI服务
│   │   └── webrtc_service.py           # WebRTC服务
│   │
│   ├── models/                         # 数据模型层
│   │   ├── __init__.py
│   │   ├── base.py                     # 基础模型类
│   │   ├── user.py                     # 用户模型
│   │   ├── tenant.py                   # 租户模型
│   │   ├── family.py                   # 家庭模型
│   │   ├── exercise.py                 # 运动模型
│   │   ├── homework.py                 # 作业模型
│   │   └── achievement.py              # 成就模型
│   │
│   ├── database/                       # 数据库层
│   │   ├── __init__.py
│   │   ├── session.py                  # 数据库会话管理
│   │   ├── migrations/                 # 数据库迁移脚本
│   │   │   ├── versions/               # 迁移版本文件
│   │   │   └── env.py                  # 迁移环境配置
│   │   └── repositories/               # 数据仓库
│   │       ├── __init__.py
│   │       ├── base.py                 # 基础仓库类
│   │       ├── user_repo.py            # 用户仓库
│   │       ├── tenant_repo.py          # 租户仓库
│   │       └── exercise_repo.py        # 运动仓库
│   │
│   ├── utils/                          # 工具模块
│   │   ├── __init__.py
│   │   ├── validators.py               # 数据验证器
│   │   ├── security.py                 # 安全工具
│   │   ├── file_utils.py               # 文件处理工具
│   │   ├── date_utils.py               # 日期时间工具
│   │   └── logging_utils.py            # 日志工具
│   │
│   └── tasks/                          # 异步任务模块
│       ├── __init__.py
│       ├── base.py                     # 基础任务类
│       ├── exercise_tasks.py           # 运动相关任务
│       └── homework_tasks.py           # 作业相关任务
│
├── tests/                              # 测试目录
│   ├── __init__.py
│   ├── conftest.py                     # 测试配置
│   ├── unit/                           # 单元测试
│   ├── integration/                    # 集成测试
│   └── e2e/                            # 端到端测试
│
├── scripts/                            # 脚本目录
│   ├── setup_venv.sh                   # 虚拟环境设置脚本
│   ├── start_dev.sh                    # 开发环境启动脚本
│   ├── start_prod.sh                   # 生产环境启动脚本
│   └── db_migrate.sh                   # 数据库迁移脚本
│
├── docs/                               # 项目文档
│   ├── api/                            # API文档
│   ├── deployment/                     # 部署文档
│   └── development/                    # 开发文档
│
└── docker/                             # Docker配置
    ├── Dockerfile                      # Docker构建文件
    ├── docker-compose.yml              # Docker Compose配置
    └── nginx/                          # Nginx配置
        └── nginx.conf
```

### 2.2 模块职责说明

#### 2.2.1 配置模块（config）
- **职责**：管理应用配置，包括数据库、日志、第三方服务等配置
- **关键文件**：`settings.py`、`database.py`、`logging_config.py`
- **设计原则**：配置与代码分离，支持环境变量覆盖

#### 2.2.2 核心模块（core）
- **职责**：提供基础功能，如异常处理、中间件、认证授权、租户管理、缓存等
- **关键文件**：`exceptions.py`、`middleware.py`、`authentication.py`、`tenant.py`
- **设计原则**：可复用、可配置、松耦合

#### 2.2.3 API接口层（api）
- **职责**：处理HTTP请求，参数验证，返回响应，API版本管理
- **关键文件**：`handlers/`目录下的各个处理器，`schemas/`请求响应模型
- **设计原则**：RESTful设计，输入输出验证，错误处理统一

#### 2.2.4 业务服务层（services）
- **职责**：实现业务逻辑，协调多个数据模型操作，事务管理
- **关键文件**：`tenant_service.py`、`family_service.py`、`exercise_service.py`
- **设计原则**：单一职责，依赖注入，易于测试

#### 2.2.5 数据模型层（models）
- **职责**：定义数据模型，数据库表映射，数据验证规则
- **关键文件**：`user.py`、`tenant.py`、`family.py`、`exercise.py`
- **设计原则**：清晰的数据关系，合理的字段设计，适当的索引

#### 2.2.6 数据库层（database）
- **职责**：数据库连接管理，数据访问抽象，迁移脚本管理
- **关键文件**：`session.py`、`repositories/`目录下的各个仓库
- **设计原则**：连接池管理，事务控制，数据访问抽象

#### 2.2.7 工具模块（utils）
- **职责**：提供通用工具函数，如数据验证、安全处理、文件操作等
- **关键文件**：`validators.py`、`security.py`、`file_utils.py`
- **设计原则**：纯函数，无副作用，易于测试

#### 2.2.8 异步任务模块（tasks）
- **职责**：处理异步任务，如文件处理、数据分析、通知发送等
- **关键文件**：`exercise_tasks.py`、`homework_tasks.py`
- **设计原则**：任务队列抽象，错误重试，进度跟踪

## 🔧 核心模块详细设计

### 3.1 配置管理模块

#### 3.1.1 配置类设计
```python
# src/config/settings.py
"""
应用配置管理模块，负责加载和管理所有配置项，支持环境变量覆盖和配置文件加载。
使用Python的dataclasses和pydantic进行配置验证和类型提示，确保配置的正确性和一致性。
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pydantic import BaseSettings, Field, validator
from pathlib import Path


# 日志配置
_LOGGER = logging.getLogger(__name__)


class DatabaseSettings(BaseSettings):
    """数据库配置类，包含MySQL数据库连接和连接池相关配置项。"""
    
    host: str = Field("localhost", env="DB_HOST", description="数据库主机地址")
    port: int = Field(3306, env="DB_PORT", description="数据库端口号")
    username: str = Field("root", env="DB_USERNAME", description="数据库用户名")
    password: str = Field("", env="DB_PASSWORD", description="数据库密码")
    database: str = Field("coachai", env="DB_DATABASE", description="数据库名称")
    pool_size: int = Field(20, env="DB_POOL_SIZE", description="数据库连接池大小")
    max_overflow: int = Field(10, env="DB_MAX_OVERFLOW", description="连接池最大溢出连接数")
    pool_recycle: int = Field(3600, env="DB_POOL_RECYCLE", description="连接回收时间（秒）")
    echo: bool = Field(False, env="DB_ECHO", description="是否输出SQL日志")
    
    @property
    def connection_url(self) -> str:
        """生成数据库连接URL，用于SQLAlchemy连接池初始化。"""
        return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @validator("password")
    def validate_password(cls, v: str) -> str:
        """验证数据库密码，确保生产环境不使用默认密码。"""
        if os.getenv("ENVIRONMENT") == "production" and v == "":
            raise ValueError("生产环境必须设置数据库密码")
        return v


class RedisSettings(BaseSettings):
    """Redis缓存配置类，包含连接信息和缓存相关配置。"""
    
    host: str = Field("localhost", env="REDIS_HOST", description="Redis主机地址")
    port: int = Field(6379, env="REDIS_PORT", description="Redis端口号")
    password: Optional[str] = Field(None, env="REDIS_PASSWORD", description="Redis密码")
    db: int = Field(0, env="REDIS_DB", description="Redis数据库编号")
    max_connections: int = Field(50, env="REDIS_MAX_CONNECTIONS", description="最大连接数")
    
    @property
    def connection_url(self) -> str:
        """生成Redis连接URL，用于Redis连接池初始化。"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class WebRTCSettings(BaseSettings):
    """WebRTC配置类，包含STUN/TURN服务器和媒体流相关配置。"""
    
    stun_servers: List[str] = Field(
        default_factory=lambda: [
            "stun:stun.l.google.com:19302",
            "stun:stun1.l.google.com:19302"
        ],
        env="WEBRTC_STUN_SERVERS",
        description="STUN服务器列表"
    )
    turn_servers: List[Dict[str, Any]] = Field(
        default_factory=list,
        env="WEBRTC_TURN_SERVERS",
        description="TURN服务器配置列表"
    )
    video_bitrate: int = Field(2000000, env="WEBRTC_VIDEO_BITRATE", description="视频码率（bps）")
    audio_bitrate: int = Field(128000, env="WEBRTC_AUDIO_BITRATE", description="音频码率（bps）")
    max_frame_rate: int = Field(30, env="WEBRTC_MAX_FRAME_RATE", description="最大帧率")


class AISettings(BaseSettings):
    """AI服务配置类，包含OCR、动作识别、语音识别等相关配置。"""
    
    ocr_model_path: str = Field(
        "/models/ocr",
        env="AI_OCR_MODEL_PATH",
        description="OCR模型文件路径"
    )
    pose_model_path: str = Field(
        "/models/pose",
        env="AI_POSE_MODEL_PATH",
        description="姿态识别模型文件路径"
    )
    speech_model_path: str = Field(
        "/models/speech",
        env="AI_SPEECH_MODEL_PATH",
        description="语音识别模型文件路径"
    )
    gpu_enabled: bool = Field(False, env="AI_GPU_ENABLED", description="是否启用GPU加速")
    batch_size: int = Field(32, env="AI_BATCH_SIZE", description="批量处理大小")
    confidence_threshold: float = Field(0.7, env="AI_CONFIDENCE_THRESHOLD", description="置信度阈值")


class SecuritySettings(BaseSettings):
    """安全配置类，包含JWT、加密、CORS等相关安全配置。"""
    
    secret_key: str = Field(
        "your-secret-key-change-in-production",
        env="SECRET_KEY",
        description="应用密钥，用于加密和签名"
    )
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM", description="JWT签名算法")
    jwt_expire_minutes: int = Field(1440, env="JWT_EXPIRE_MINUTES", description="JWT过期时间（分钟）")
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        env="CORS_ORIGINS",
        description="允许的CORS源"
    )
    rate_limit_enabled: bool = Field(True, env="RATE_LIMIT_ENABLED", description="是否启用速率限制")
    rate_limit_per_minute: int = Field(60, env="RATE_LIMIT_PER_MINUTE", description="每分钟请求限制")


class LoggingSettings(BaseSettings):
    """日志配置类，包含日志级别、格式、输出路径等相关配置。"""
    
    level: str = Field("INFO", env="LOG_LEVEL", description="日志级别")
    format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT",
        description="日志格式"
    )
    file_path: Optional[str] = Field(None, env="LOG_FILE_PATH", description="日志文件路径")
    max_file_size: int = Field(10485760, env="LOG_MAX_FILE_SIZE", description="日志文件最大大小（字节）")
    backup_count: int = Field(5, env="LOG_BACKUP_COUNT", description="日志备份文件数量")


class ApplicationSettings(BaseSettings):
    """应用基础配置类，包含服务端口、环境、调试模式等基础配置。"""
    
    environment: str = Field("development", env="ENVIRONMENT", description="运行环境")
    debug: bool = Field(False, env="DEBUG", description="是否启用调试模式")
    host: str = Field("0.0.0.0", env="HOST", description="服务监听地址")
    port: int = Field(8000, env="PORT", description="服务监听端口")
    workers: int = Field(4, env="WORKERS", description="工作进程数量")
    api_prefix: str = Field("/api/v1", env="API_PREFIX", description="API前缀")
    
    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """验证环境变量，确保是有效的环境名称。"""
        valid_environments = ["development", "testing", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"环境必须是以下之一: {valid_environments}")
        return v


@dataclass
class Settings:
    """
    应用总配置类，聚合所有子配置类，提供统一的配置访问接口。
    使用单例模式确保配置的一致性，支持配置的热加载和动态更新。
    """
    
    app: ApplicationSettings = field(default_factory=ApplicationSettings)
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    redis: RedisSettings = field(default_factory=RedisSettings)
    webrtc: WebRTCSettings = field(default_factory=WebRTCSettings)
    ai: AISettings = field(default_factory=AISettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    
    # 配置实例（单例模式）
    _instance: Optional["Settings"] = None
    
    def __new__(cls, *args: Any, **kwargs: Any) -> "Settings":
        """实现单例模式，确保全局只有一个配置实例。"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            _LOGGER.info("创建新的配置实例")
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> "Settings":
        """获取配置单例实例，如果不存在则创建新实例。"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def reload(self) -> None:
        """重新加载配置，用于配置热更新场景。"""
        _LOGGER.info("重新加载配置")
        self.__init__()  # type: ignore
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典，用于日志记录和调试。"""
        return {
            "app": self.app.dict(),
            "database": self.database.dict(),
            "redis": self.redis.dict(),
            "webrtc": self.webrtc.dict(),
            "ai": self.ai.dict(),
            "security": self.security.dict(),
            "logging": self.logging.dict(),
        }


# 全局配置实例
settings = Settings.get_instance()


def init_settings() -> Settings:
    """
    初始化配置，加载环境变量和配置文件，返回配置实例。
    此函数应在应用启动时调用，确保配置正确加载。
    """
    _LOGGER.info("开始初始化配置")
    
    # 加载环境变量文件（如果存在）
    env_file = Path(".env")
    if env_file.exists():
        _LOGGER.info(f"加载环境变量文件: {env_file}")
    
    # 创建配置实例
    config = Settings.get_instance()
    
    # 记录配置信息（敏感信息已脱敏）
    config_dict = config.to_dict()
    config_dict["database"]["password"] = "***" if config.database.password else ""
    config_dict["redis"]["password"] = "***" if config.redis.password else ""
    config_dict["security"]["secret_key"] = "***"
    
    _LOGGER.info(f"配置初始化完成: {config_dict}")
    return config
```

#### 3.1.2 数据库配置
```python
# src/config/database.py
"""
数据库配置模块，负责数据库连接池初始化、会话管理和多租户数据隔离配置。
使用SQLAlchemy作为ORM框架，Alembic进行数据库迁移，支持MySQL数据库。
"""

import logging
from typing import Optional, Any, Dict
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import QueuePool
from contextvars import ContextVar

from src.config.settings import settings


# 日志配置
_LOGGER = logging.getLogger(__name__)

# 上下文变量，用于存储当前数据库会话（支持多租户）
_session_context: ContextVar[Optional[Session]] = ContextVar("_session_context", default=None)


class DatabaseManager:
    """
    数据库管理器类，负责数据库连接池的创建、会话管理和多租户支持。
    使用连接池提高性能，支持读写分离和故障转移（后续扩展）。
    """
    
    def __init__(self) -> None:
        """初始化数据库管理器，创建数据库引擎和会话工厂。"""
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._scoped_session_factory: Optional[scoped_session] = None
        
    def init_engine(self) -> Engine:
        """
        初始化数据库引擎，创建连接池，配置连接参数和超时设置。
        使用QueuePool连接池管理数据库连接，提高并发性能。
        """
        if self._engine is not None:
            return self._engine
        
        db_config = settings.database
        
        # 创建数据库引擎，配置连接池参数
        engine = create_engine(
            db_config.connection_url,
            poolclass=QueuePool,
            pool_size=db_config.pool_size,
            max_overflow=db_config.max_overflow,
            pool_recycle=db_config.pool_recycle,
            pool_pre_ping=True,  # 连接前ping检查
            echo=db_config.echo,
            echo_pool=True if db_config.echo else False,
            isolation_level="READ COMMITTED",
            connect_args={
                "charset": "utf8mb4",
                "connect_timeout": 10,
                "read_timeout": 30,
                "write_timeout": 30,
            }
        )
        
        self._engine = engine
        _LOGGER.info(f"数据库引擎初始化完成，连接池大小: {db_config.pool_size}")
        return engine
    
    def init_session_factory(self) -> sessionmaker:
        """
        初始化会话工厂，用于创建数据库会话。
        配置会话自动刷新、自动提交和过期策略。
        """
        if self._session_factory is not None:
            return self._session_factory
        
        engine = self.init_engine()
        
        # 创建会话工厂
        session_factory = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=True,
            class_=Session,
        )
        
        self._session_factory = session_factory
        _LOGGER.info("数据库会话工厂初始化完成")
        return session_factory
    
    def init_scoped_session(self) -> scoped_session:
        """
        初始化作用域会话，支持线程/协程级别的会话隔离。
        用于Web请求处理，确保每个请求有独立的数据库会话。
        """
        if self._scoped_session_factory is not None:
            return self._scoped_session_factory
        
        session_factory = self.init_session_factory()
        
        # 创建作用域会话
        scoped_session_factory = scoped_session(session_factory)
        self._scoped_session_factory = scoped_session_factory
        
        _LOGGER.info("作用域会话工厂初始化完成")
        return scoped_session_factory
    
    def get_session(self) -> Session:
        """
        获取数据库会话，优先使用上下文中的会话，如果没有则创建新会话。
        用于业务逻辑层访问数据库，确保会话的正确管理和释放。
        """
        # 尝试从上下文中获取会话
        current_session = _session_context.get()
        if current_session is not None:
            return current_session
        
        # 创建新会话
        session_factory = self.init_session_factory()
        session = session_factory()
        
        # 设置到上下文中
        _session_context.set(session)
        return session
    
    def close_session(self) -> None:
        """关闭当前上下文中的数据库会话，释放连接资源。"""
        current_session = _session_context.get()
        if current_session is not None:
            current_session.close()
            _session_context.set(None)
            _LOGGER.debug("数据库会话已关闭")
    
    def get_engine(self) -> Engine:
        """获取数据库引擎，用于原始SQL查询或批量操作。"""
        return self.init_engine()
    
    def dispose_pool(self) -> None:
        """释放连接池中的所有连接，用于应用关闭或连接重置。"""
        if self._engine is not None:
            self._engine.dispose()
            _LOGGER.info("数据库连接池已释放")


# 全局数据库管理器实例
db_manager = DatabaseManager()


class DatabaseSession:
    """
    数据库会话上下文管理器，用于自动管理会话的生命周期。
    使用with语句确保会话正确打开和关闭，支持嵌套会话。
    """
    
    def __init__(self) -> None:
        """初始化数据库会话上下文管理器。"""
        self.session: Optional[Session] = None
    
    def __enter__(self) -> Session:
        """
        进入上下文，获取数据库会话，如果已存在则复用，否则创建新会话。
        返回数据库会话对象，用于执行数据库操作。
        """
        # 检查是否已有会话
        existing_session = _session_context.get()
        if existing_session is not None:
            self.session = existing_session
            _LOGGER.debug("复用现有数据库会话")
        else:
            # 创建新会话
            session_factory = db_manager.init_session_factory()
            self.session = session_factory()
            _session_context.set(self.session)
            _LOGGER.debug("创建新的数据库会话")
        
        return self.session
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        退出上下文，根据异常情况决定提交或回滚事务，然后关闭会话。
        如果发生异常则回滚事务，否则提交事务，确保数据一致性。
        """
        if self.session is None:
            return
        
        try:
            if exc_type is not None:
                # 发生异常，回滚事务
                self.session.rollback()
                _LOGGER.warning(f"数据库会话异常回滚: {exc_type.__name__}: {exc_val}")
            else:
                # 正常执行，提交事务
                self.session.commit()
                _LOGGER.debug("数据库会话提交成功")
        except Exception as commit_error:
            # 提交失败，回滚事务
            self.session.rollback()
            _LOGGER.error(f"数据库会话提交失败，已回滚: {commit_error}")
            raise
        finally:
            # 关闭会话
            self.session.close()
            # 从上下文中移除
            if _session_context.get() is self.session:
                _session_context.set(None)
            self.session = None


def get_db_session() -> Session:
    """
    获取数据库会话的快捷函数，用于依赖注入或直接调用。
    返回当前上下文中的数据库会话，如果没有则创建新会话。
    """
    return db_manager.get_session()


def init_database() -> DatabaseManager:
    """
    初始化数据库模块，创建引擎和会话工厂，返回数据库管理器。
    此函数应在应用启动时调用，确保数据库连接正确建立。
    """
    _LOGGER.info("开始初始化数据库模块")
    
    # 初始化数据库管理器
    manager = db_manager
    manager.init_engine()
    manager.init_session_factory()
    manager.init_scoped_session()
    
    # 测试数据库连接
    try:
        with DatabaseSession() as session:
            session.execute("SELECT 1")
        _LOGGER.info("数据库连接测试成功")
    except Exception as e:
        _LOGGER.error(f"数据库连接测试失败: {e}")
        raise
    
    _LOGGER.info("数据库模块初始化完成")
    return manager
```

### 3.2 核心异常处理模块

#### 3.2.1 自定义异常类设计
```python
# src/core/exceptions.py
"""
自定义异常类模块，定义业务异常和系统异常，提供统一的异常处理机制。
所有异常都继承自BaseException，分为业务异常、验证异常、权限异常等类别。
"""

import logging
from typing import Optional, Any, Dict, List
from http import HTTPStatus


# 日志配置
_LOGGER = logging.getLogger(__name__)


class BaseAppException(Exception):
    """
    应用基础异常类，所有自定义异常的基类，包含错误码、错误信息和额外数据。
    提供统一的异常格式和序列化方法，便于API错误响应和日志记录。
    """
    
    def __init__(
        self,
        message: str = "应用内部错误",
        code: str = "INTERNAL_ERROR",
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        """
        初始化基础异常，设置错误信息、错误码、HTTP状态码和额外详情。
        
        Args:
            message: 错误描述信息，用于显示给用户或记录日志
            code: 错误代码，用于程序识别错误类型，大写字母和下划线组成
            status_code: HTTP状态码，用于API响应，默认500内部服务器错误
            details: 错误详情，包含额外的调试信息或错误上下文
            cause: 原始异常，用于异常链追踪，保留完整的错误堆栈
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        self.cause = cause
        
        # 记录异常日志
        _LOGGER.error(
            f"异常发生: code={code}, message={message}, status={status_code}",
            extra={"details": details},
            exc_info=True
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将异常转换为字典格式，用于API错误响应或日志记录。
        
        Returns:
            包含错误信息的字典，包含code、message、details等字段
        """
        result = {
            "code": self.code,
            "message": self.message,
            "status": self.status_code,
        }
        
        if self.details:
            result["details"] = self.details
        
        return result
    
    def __str__(self) -> str:
        """返回异常的字符串表示，包含错误码和错误信息。"""
        return f"{self.code}: {self.message}"


class ValidationException(BaseAppException):
    """
    数据验证异常，用于参数验证失败或数据格式错误场景。
    包含字段级错误信息，便于前端显示具体的验证错误。
    """
    
    def __init__(
        self,
        message: str = "数据验证失败",
        field_errors: Optional[Dict[str, List[str]]] = None,
        **kwargs: Any
    ) -> None:
        """
        初始化验证异常，设置字段级错误信息和验证失败详情。
        
        Args:
            message: 验证失败的整体描述信息
            field_errors: 字段级错误信息，键为字段名，值为错误消息列表
            **kwargs: 其他传递给基类的参数
        """
        details = kwargs.pop("details", {})
        if field_errors:
            details["field_errors"] = field_errors
        
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=HTTPStatus.BAD_REQUEST,
            details=details,
            **kwargs
        )


class AuthenticationException(BaseAppException):
    """
    认证异常，用于用户身份验证失败场景，如Token无效、密码错误等。
    区分不同的认证失败原因，提供具体的错误提示。
    """
    
    def __init__(
        self,
        message: str = "认证失败",
        reason: str = "invalid_credentials",
        **kwargs: Any
    ) -> None:
        """
        初始化认证异常，设置认证失败原因和具体错误信息。
        
        Args:
            message: 认证失败描述信息
            reason: 认证失败原因，如invalid_token、expired_token等
            **kwargs: 其他传递给基类的参数
        """
        details = kwargs.pop("details", {})
        details["reason"] = reason
        
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=HTTPStatus.UNAUTHORIZED,
            details=details,
            **kwargs
        )


class AuthorizationException(BaseAppException):
    """
    授权异常，用于权限检查失败场景，如用户无权访问资源或执行操作。
    包含具体的资源信息和操作类型，便于权限管理和审计。
    """
    
    def __init__(
        self,
        message: str = "权限不足",
        resource: Optional[str] = None,
        action: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        初始化授权异常，设置资源、操作和权限失败详情。
        
        Args:
            message: 授权失败描述信息
            resource: 资源标识，如user、tenant、exercise等
            action: 操作类型，如read、write、delete等
            **kwargs: 其他传递给基类的参数
        """
        details = kwargs.pop("details", {})
        if
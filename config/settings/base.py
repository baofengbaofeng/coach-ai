"""
Django 基础配置设置文件，包含所有环境共享的通用配置，如应用定义、中间件、数据库基础配置等。
按照豆包AI助手提供的Django项目结构最佳实践实现。
"""
import os
import sys
from pathlib import Path
from datetime import timedelta
from typing import Any, Dict, List, Optional


# ==================== 基础路径配置（豆包最佳实践） ====================
# 基础路径：定位到项目根目录的三级父目录（config/settings/../..）
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

# 把 apps 目录加入 Python 路径（直接 import 应用名）- 豆包最佳实践关键步骤
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))


# ==================== 安全配置 ====================
# 安全配置：从环境变量获取密钥，生产环境必须设置，开发环境使用默认值
SECRET_KEY: str = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-change-in-production-for-security")
DEBUG: bool = False
ALLOWED_HOSTS: List[str] = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")


# ==================== 应用定义 ====================
# 应用定义：按标准库、第三方库、项目应用的顺序组织，确保依赖关系正确
INSTALLED_APPS: List[str] = [
    # Django 内置核心应用
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # 第三方应用和扩展
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_yasg",
    "channels",
    "django_filters",
    "django_celery_results",
    "django_celery_beat",
    
    # 项目自定义应用（按功能模块划分）- 豆包最佳实践：apps.xxx
    "accounts",
    "homework",
    "exercise",
    "tasks",
    "achievements",
    "common",
]


# ==================== 中间件配置 ====================
# 中间件配置：按处理顺序排列，确保请求和响应处理链正确
MIDDLEWARE: List[str] = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    
    # 自定义中间件 - 豆包最佳实践：core.middlewares
    "core.middlewares.RequestLoggingMiddleware",
    "core.middlewares.ExceptionHandlingMiddleware",
]


# ==================== 模板和URL配置 ====================
# URL 配置：指向项目的主 URL 路由配置文件
ROOT_URLCONF: str = "config.urls"

# 模板配置：定义模板引擎、目录和上下文处理器
TEMPLATES: List[Dict[str, Any]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]


# ==================== WSGI/ASGI 配置 ====================
# WSGI 应用配置：指向项目的 WSGI 应用入口点
WSGI_APPLICATION: str = "config.wsgi.application"

# ASGI 应用配置：指向项目的 ASGI 应用入口点，支持 WebSocket 和异步请求
ASGI_APPLICATION: str = "config.asgi.application"


# ==================== 数据库配置 ====================
# 数据库配置：使用 MySQL 作为主数据库，配置连接参数和选项
DATABASES: Dict[str, Dict[str, Any]] = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MYSQL_DATABASE", "coachai"),
        "USER": os.environ.get("MYSQL_USER", "coachai"),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD", "password"),
        "HOST": os.environ.get("MYSQL_HOST", "localhost"),
        "PORT": os.environ.get("MYSQL_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "connect_timeout": 10,
        },
        "CONN_MAX_AGE": 300,  # 连接保持 5 分钟，减少连接建立开销
        "CONN_HEALTH_CHECKS": True,
    }
}


# ==================== 密码验证配置 ====================
# 密码验证配置：设置密码强度和验证规则，确保用户密码安全
AUTH_PASSWORD_VALIDATORS: List[Dict[str, str]] = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ==================== 国际化配置 ====================
# 国际化配置：设置语言、时区和本地化支持
LANGUAGE_CODE: str = "zh-hans"
TIME_ZONE: str = "Asia/Shanghai"
USE_I18N: bool = True
USE_TZ: bool = True


# ==================== 静态文件和媒体文件配置 ====================
# 静态文件配置：定义静态文件 URL 和收集目录
STATIC_URL: str = "/static/"
STATIC_ROOT: Path = BASE_DIR / "staticfiles"

# 媒体文件配置：定义媒体文件 URL 和存储目录
MEDIA_URL: str = "/media/"
MEDIA_ROOT: Path = BASE_DIR / "media"


# ==================== 默认主键字段类型 ====================
# 默认主键字段类型：使用 BigAutoField 支持更大的主键范围
DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"


# ==================== 自定义用户模型 ====================
# 自定义用户模型：使用扩展的用户模型替代 Django 默认用户模型
AUTH_USER_MODEL: str = "accounts.User"


# ==================== Django REST Framework 配置 ====================
# Django REST Framework 配置：设置认证、权限、分页和限流策略
REST_FRAMEWORK: Dict[str, Any] = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
    },
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    # 豆包最佳实践：使用统一的异常处理器
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
}


# ==================== JWT 配置 ====================
# JWT 配置：设置访问令牌和刷新令牌的生命周期、算法和签名密钥
SIMPLE_JWT: Dict[str, Any] = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}


# ==================== CORS 配置 ====================
# CORS 配置：设置允许跨域请求的来源、方法和头部，支持凭证传输
CORS_ALLOWED_ORIGINS: List[str] = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
CORS_ALLOW_CREDENTIALS: bool = True
CORS_ALLOW_METHODS: List[str] = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_HEADERS: List[str] = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]


# ==================== 缓存配置 ====================
# 缓存配置：使用 Redis 作为缓存后端，配置连接参数和键前缀
CACHES: Dict[str, Dict[str, Any]] = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PARSER_CLASS": "redis.connection.HiredisParser",
            "CONNECTION_POOL_CLASS": "redis.BlockingConnectionPool",
            "CONNECTION_POOL_CLASS_KWARGS": {
                "max_connections": 50,
                "timeout": 20,
            },
            "MAX_CONNECTIONS": 1000,
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
        },
        "KEY_PREFIX": "coachai",
    }
}


# ==================== Celery 配置 ====================
# Celery 配置：设置消息代理、结果后端和任务序列化格式
CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND: str = "django-db"
CELERY_CACHE_BACKEND: str = "django-cache"
CELERY_ACCEPT_CONTENT: List[str] = ["json"]
CELERY_TASK_SERIALIZER: str = "json"
CELERY_RESULT_SERIALIZER: str = "json"
CELERY_TIMEZONE: str = "Asia/Shanghai"
CELERY_TASK_TRACK_STARTED: bool = True
CELERY_TASK_TIME_LIMIT: int = 30 * 60  # 30 分钟任务超时
CELERY_TASK_SOFT_TIME_LIMIT: int = 25 * 60  # 25 分钟软超时
CELERY_BEAT_SCHEDULER: str = "django_celery_beat.schedulers:DatabaseScheduler"


# ==================== Channels 配置 ====================
# Channels 配置：设置通道层后端，支持 WebSocket 和异步通信
CHANNEL_LAYERS: Dict[str, Dict[str, Any]] = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get("REDIS_URL", "redis://localhost:6379/3")],
            "capacity": 1500,
            "expiry": 10,
        },
    }
}


# ==================== 文件上传配置 ====================
# 文件上传配置：设置最大内存文件大小和最大上传数据大小
FILE_UPLOAD_MAX_MEMORY_SIZE: int = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE: int = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_PERMISSIONS: int = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS: int = 0o755


# ==================== 会话配置 ====================
# 会话配置：设置会话引擎、过期时间和 Cookie 安全选项
SESSION_ENGINE: str = "django.contrib.sessions.backends.cached_db"
SESSION_COOKIE_AGE: int = 1209600  # 2 周，单位秒
SESSION_COOKIE_SECURE: bool = not DEBUG
SESSION_COOKIE_HTTPONLY: bool = True
SESSION_COOKIE_SAMESITE: str = "Lax"


# ==================== CSRF 配置 ====================
# CSRF 配置：设置 CSRF Cookie 安全选项和信任的来源
CSRF_COOKIE_SECURE: bool = not DEBUG
CSRF_COOKIE_HTTPONLY: bool = True
CSRF_TRUSTED_ORIGINS: List[str] = os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")


# ==================== 安全头部配置 ====================
# 安全头部配置：增强应用安全性，防止常见 Web 攻击
SECURE_BROWSER_XSS_FILTER: bool = True
SECURE_CONTENT_TYPE_NOSNIFF: bool = True
X_FRAME_OPTIONS: str = "DENY"


# ==================== 日志配置 ====================
# 日志配置：定义日志格式、处理器和记录器，支持不同级别的日志输出
LOGGING: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "maxBytes": 1024 * 1024 * 100,  # 100MB
            "backupCount": 10,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": True,
        },
        "coachai": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "apps": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}


# ==================== AI 服务配置 ====================
# AI 服务配置：OCR、计算机视觉、语音识别等服务配置
AI_SERVICES: Dict[str, Any] = {
    "ocr": {
        "engine": os.environ.get("OCR_ENGINE", "paddle"),  # paddle 或 easy
        "use_gpu": os.environ.get("USE_GPU", "false").lower() == "true",
        "languages": ["ch", "en"],
    },
    "computer_vision": {
        "pose_estimation_model": "mediapipe",
        "action_recognition_model": "mediapipe",
        "confidence_threshold": 0.7,
    },
    "speech": {
        "engine": os.environ.get("SPEECH_ENGINE", "whisper"),
        "whisper_model_size": os.environ.get("WHISPER_MODEL_SIZE", "base"),
        "language": "zh",
    },
}


# ==================== 任务队列配置 ====================
# 任务队列配置：异步任务处理配置
TASK_QUEUE: Dict[str, Any] = {
    "max_retries": 3,
    "retry_delay": 60,  # 秒
    "timeout": 300,  # 秒
    "concurrency": 4,
}

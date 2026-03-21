"""
Django 生产环境配置设置文件，包含生产环境特有的安全配置、性能优化和监控设置。
按照豆包AI助手提供的Django项目结构最佳实践实现。
"""
from __future__ import annotations

import os
from typing import Any, Dict, List

from .base import *  # noqa: F403


# ==================== 安全配置 ====================
# 安全配置：生产环境禁用调试模式，设置严格的安全头部
DEBUG: bool = False
ALLOWED_HOSTS: List[str] = os.environ.get("ALLOWED_HOSTS", "").split(",")

# 强制 HTTPS 重定向，确保所有流量通过安全连接
SECURE_SSL_REDIRECT: bool = True
SECURE_HSTS_SECONDS: int = 31536000  # 1年
SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = True
SECURE_HSTS_PRELOAD: bool = True

# Cookie 安全设置：生产环境必须启用安全 Cookie
SESSION_COOKIE_SECURE: bool = True
CSRF_COOKIE_SECURE: bool = True
SESSION_COOKIE_HTTPONLY: bool = True
CSRF_COOKIE_HTTPONLY: bool = True

# 安全头部配置：防止点击劫持和内容嗅探
SECURE_BROWSER_XSS_FILTER: bool = True
SECURE_CONTENT_TYPE_NOSNIFF: bool = True
X_FRAME_OPTIONS: str = "DENY"


# ==================== 数据库配置 ====================
# 数据库配置：生产环境使用 MySQL，配置连接池和性能优化
DATABASES: Dict[str, Dict[str, Any]] = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MYSQL_DATABASE", "coachai_prod"),
        "USER": os.environ.get("MYSQL_USER", "coachai_prod"),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD", ""),
        "HOST": os.environ.get("MYSQL_HOST", "localhost"),
        "PORT": os.environ.get("MYSQL_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "connect_timeout": 10,
        },
        "CONN_MAX_AGE": 600,  # 连接保持 10 分钟，减少连接建立开销
        "CONN_HEALTH_CHECKS": True,
    }
}


# ==================== 缓存配置 ====================
# 缓存配置：生产环境使用 Redis 缓存，提升性能
CACHES: Dict[str, Dict[str, Any]] = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PARSER_CLASS": "redis.connection.HiredisParser",
            "CONNECTION_POOL_CLASS": "redis.BlockingConnectionPool",
            "CONNECTION_POOL_CLASS_KWARGS": {
                "max_connections": 100,
                "timeout": 20,
            },
            "MAX_CONNECTIONS": 1000,
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
        },
        "KEY_PREFIX": "coachai_prod",
    }
}


# ==================== 静态文件和媒体文件配置 ====================
# 静态文件配置：生产环境使用 CDN 或专用静态文件服务器
STATIC_URL: str = os.environ.get("STATIC_URL", "/static/")
STATIC_ROOT: str = os.environ.get("STATIC_ROOT", BASE_DIR / "staticfiles")  # noqa: F405

# 媒体文件配置：生产环境使用对象存储服务
MEDIA_URL: str = os.environ.get("MEDIA_URL", "/media/")
MEDIA_ROOT: str = os.environ.get("MEDIA_ROOT", BASE_DIR / "media")  # noqa: F405


# ==================== 日志配置 ====================
# 日志配置：生产环境使用更详细的日志级别，便于监控和问题排查
LOGGING["loggers"]["django"]["level"] = "WARNING"  # noqa: F405
LOGGING["loggers"]["coachai"]["level"] = "INFO"  # noqa: F405
LOGGING["loggers"]["apps"]["level"] = "INFO"  # noqa: F405

# 生产环境添加文件轮转处理器，避免日志文件过大
LOGGING["handlers"]["file"]["maxBytes"] = 1024 * 1024 * 500  # 500MB
LOGGING["handlers"]["file"]["backupCount"] = 20


# ==================== Django REST Framework 配置 ====================
# 生产环境禁用浏览 API 界面，只提供 JSON 响应
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
]

# 生产环境调整限流策略，防止恶意请求
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "anon": "50/day",
    "user": "500/day",
}


# ==================== CORS 配置 ====================
# CORS 配置：生产环境设置严格的白名单，只允许特定来源跨域请求
CORS_ALLOWED_ORIGINS: List[str] = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
CORS_ALLOW_ALL_ORIGINS: bool = False


# ==================== 会话配置 ====================
# 会话配置：生产环境使用缓存数据库后端，提升性能
SESSION_ENGINE: str = "django.contrib.sessions.backends.cached_db"
SESSION_COOKIE_AGE: int = 1209600  # 2 周，单位秒


# ==================== 环境变量验证 ====================
# 生产环境关键环境变量验证，确保配置正确
required_env_vars: List[str] = [
    "DJANGO_SECRET_KEY",
    "MYSQL_DATABASE",
    "MYSQL_USER",
    "MYSQL_PASSWORD",
    "MYSQL_HOST",
    "REDIS_URL",
    "CELERY_BROKER_URL",
]

for env_var in required_env_vars:
    if not os.environ.get(env_var):
        raise ValueError(f"生产环境必须设置环境变量: {env_var}")


# ==================== 监控和性能配置 ====================
# 监控配置：生产环境启用性能监控和错误追踪
if os.environ.get("ENABLE_MONITORING", "false").lower() == "true":
    try:
        import sentry_sdk  # noqa: F401
        from sentry_sdk.integrations.django import DjangoIntegration  # noqa: F401

        sentry_sdk.init(
            dsn=os.environ.get("SENTRY_DSN", ""),
            integrations=[DjangoIntegration()],
            traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            send_default_pii=True,
        )
    except ImportError:
        pass

"""
Django 开发环境配置设置文件，包含开发阶段特有的配置，如调试模式、简化数据库配置和宽松的安全设置。
按照豆包AI助手提供的Django项目结构最佳实践实现。
"""
from __future__ import annotations

import os
from typing import Any, Dict, List

from .base import *  # noqa: F403


# ==================== 安全配置 ====================
# 安全配置：开发环境启用调试模式，允许所有主机访问以便于开发和测试
DEBUG: bool = True
ALLOWED_HOSTS: List[str] = ["*"]


# ==================== 数据库配置 ====================
# 数据库配置：开发环境使用 SQLite 简化部署，避免 MySQL 依赖，便于快速启动和测试
DATABASES: Dict[str, Dict[str, Any]] = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}


# ==================== 缓存配置 ====================
# 缓存配置：开发环境使用虚拟缓存，避免 Redis 依赖，简化开发环境配置
CACHES: Dict[str, Dict[str, Any]] = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}


# ==================== CORS 配置 ====================
# CORS 配置：开发环境允许所有来源跨域请求，便于前端开发调试
CORS_ALLOW_ALL_ORIGINS: bool = True


# ==================== 会话配置 ====================
# 会话配置：开发环境使用数据库后端会话，避免 Redis 依赖，简化配置
SESSION_ENGINE: str = "django.contrib.sessions.backends.db"


# ==================== 日志配置 ====================
# 日志配置：开发环境启用更详细的日志级别，便于调试和问题排查
LOGGING["loggers"]["django"]["level"] = "DEBUG"  # noqa: F405
LOGGING["loggers"]["coachai"]["level"] = "DEBUG"  # noqa: F405
LOGGING["loggers"]["apps"]["level"] = "DEBUG"  # noqa: F405

# 添加控制台 SQL 查询日志，便于开发阶段优化数据库查询性能
LOGGING["loggers"]["django.db.backends"] = {
    "handlers": ["console"],
    "level": "DEBUG",
    "propagate": False,
}


# ==================== Django REST Framework 配置 ====================
# 开发环境启用浏览 API 界面，便于测试和调试
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]


# ==================== 安全设置（开发环境宽松） ====================
# 开发环境禁用 HTTPS 重定向，避免本地开发时的证书问题
SECURE_SSL_REDIRECT: bool = False

# 开发环境允许非安全 Cookie，避免本地开发时的 HTTPS 要求
SESSION_COOKIE_SECURE: bool = False
CSRF_COOKIE_SECURE: bool = False

# 开发环境禁用 HSTS，避免本地开发时的 HTTPS 强制要求
SECURE_HSTS_SECONDS: int = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = False
SECURE_HSTS_PRELOAD: bool = False

# 开发环境允许内联框架，便于使用 Django 管理界面和调试工具
X_FRAME_OPTIONS: str = "SAMEORIGIN"


# ==================== 开发工具配置 ====================
# 开发环境启用 Django 调试工具栏（如果已安装）
try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS.append("debug_toolbar")  # noqa: F405
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
    INTERNAL_IPS: List[str] = ["127.0.0.1"]
except ImportError:
    pass

# 开发环境启用 Django 扩展（如果已安装）
try:
    import django_extensions  # noqa: F401

    INSTALLED_APPS.append("django_extensions")  # noqa: F405
except ImportError:
    pass


# ==================== 环境变量默认值 ====================
# 开发环境配置：设置环境变量默认值，避免未设置环境变量导致的启动失败
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
os.environ.setdefault("DJANGO_SECRET_KEY", "dev-secret-key-change-in-production-for-security")
os.environ.setdefault("MYSQL_DATABASE", "coachai_dev")
os.environ.setdefault("MYSQL_USER", "coachai_dev")
os.environ.setdefault("MYSQL_PASSWORD", "dev_password")
os.environ.setdefault("MYSQL_HOST", "localhost")
os.environ.setdefault("MYSQL_PORT", "3306")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/1")
os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
os.environ.setdefault("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
os.environ.setdefault("OCR_ENGINE", "paddle")
os.environ.setdefault("USE_GPU", "false")
os.environ.setdefault("SPEECH_ENGINE", "whisper")
os.environ.setdefault("WHISPER_MODEL_SIZE", "base")

"""
简化的Django开发设置，用于测试和验证。
"""
import os
import sys
from pathlib import Path
from typing import Any, Dict, List


# ==================== 基础路径配置 ====================
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))


# ==================== 安全配置 ====================
SECRET_KEY: str = "dev-secret-key-for-testing-only"
DEBUG: bool = True
ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]


# ==================== 应用定义 ====================
INSTALLED_APPS: List[str] = [
    # Django 内置核心应用
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # 第三方应用（简化版）
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_yasg",
    "django_filters",
    
    # 项目自定义应用
    "apps.accounts",
    "apps.homework",
    "apps.exercise",
    "apps.tasks",
    "apps.achievements",
    "apps.common",
]


# ==================== 中间件配置 ====================
MIDDLEWARE: List[str] = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ==================== 模板和URL配置 ====================
ROOT_URLCONF: str = "config.urls"
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


# ==================== WSGI配置 ====================
WSGI_APPLICATION: str = "config.wsgi.application"


# ==================== 数据库配置 ====================
DATABASES: Dict[str, Any] = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ==================== 密码验证 ====================
AUTH_PASSWORD_VALIDATORS: List[Dict[str, str]] = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ==================== 国际化配置 ====================
LANGUAGE_CODE: str = "zh-hans"
TIME_ZONE: str = "Asia/Shanghai"
USE_I18N: bool = True
USE_TZ: bool = True


# ==================== 静态文件配置 ====================
STATIC_URL: str = "static/"
STATIC_ROOT: Path = BASE_DIR / "staticfiles"
MEDIA_URL: str = "media/"
MEDIA_ROOT: Path = BASE_DIR / "media"


# ==================== 默认主键字段类型 ====================
DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"


# ==================== REST Framework配置 ====================
REST_FRAMEWORK: Dict[str, Any] = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}


# ==================== CORS配置 ====================
CORS_ALLOW_ALL_ORIGINS: bool = True  # 开发环境允许所有来源
CORS_ALLOW_CREDENTIALS: bool = True


# ==================== 自定义用户模型 ====================
AUTH_USER_MODEL: str = "accounts.User"


# ==================== 日志配置 ====================
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
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
"""
测试环境设置文件。
"""
import os
from pathlib import Path
from .base import *

# 测试环境标识
ENVIRONMENT = "test"

# 调试模式
DEBUG = True

# 测试数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'TEST': {
            'NAME': ':memory:',
        }
    }
}

# 禁用缓存（测试环境）
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# 禁用CSRF保护（测试环境）
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False

# 禁用Session Cookie安全设置
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False

# 测试密钥
SECRET_KEY = 'test-secret-key-for-testing-only-do-not-use-in-production'

# 禁用密码验证（测试环境）
AUTH_PASSWORD_VALIDATORS = []

# 测试日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'test.log'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'coach_ai': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'tests': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# 测试邮件后端
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# 测试存储后端
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media', 'test')
MEDIA_URL = '/media/test/'

# 创建测试媒体目录
os.makedirs(MEDIA_ROOT, exist_ok=True)

# 测试AI服务配置（模拟模式）
AI_SERVICE_CONFIG = {
    'mode': 'mock',  # 测试环境使用模拟模式
    'mock_delay': 0.1,  # 模拟延迟（秒）
    'mock_success_rate': 1.0,  # 模拟成功率
}

# 测试任务队列配置（使用同步模式）
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# 测试安全设置（降低安全要求）
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
X_FRAME_OPTIONS = 'SAMEORIGIN'

# 测试API限制
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # 测试环境允许所有访问
    ],
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {
        'user': None,
        'anon': None,
    },
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# 测试中间件配置
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 禁用不需要的测试应用
INSTALLED_APPS = [
    app for app in INSTALLED_APPS 
    if not any(app.startswith(x) for x in ['debug_toolbar', 'django_celery', 'channels', 'django_nose'])
]

# 测试运行器配置
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# 测试时区
TIME_ZONE = 'UTC'

# 测试语言
LANGUAGE_CODE = 'en-us'

# 测试静态文件
STATIC_ROOT = os.path.join(BASE_DIR, 'static', 'test')
STATIC_URL = '/static/test/'

# 创建测试静态目录
os.makedirs(STATIC_ROOT, exist_ok=True)

# 测试用户模型配置
AUTH_USER_MODEL = 'accounts.User'

# 测试会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# 测试缓存超时（秒）
CACHE_TIMEOUT = 60

# 测试API版本
API_VERSION = 'v1'
API_BASE_PATH = f'/api/{API_VERSION}/'

# 测试环境变量
os.environ['TEST_ENV'] = 'true'
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.test'

print(f"✅ 测试环境配置加载完成: {ENVIRONMENT}")
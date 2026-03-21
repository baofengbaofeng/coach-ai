"""
WSGI 配置文件，用于部署 Django 项目到支持 WSGI 的服务器，如 Gunicorn、uWSGI 等。
"""
import os

from django.core.wsgi import get_wsgi_application


# 设置 Django 环境变量，指定使用的配置模块，确保应用正确初始化
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

# 获取 WSGI 应用实例，这是 Django 应用与 WSGI 服务器之间的接口
application = get_wsgi_application()

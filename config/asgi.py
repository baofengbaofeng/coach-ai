"""
ASGI 配置文件，用于部署 Django 项目到支持 ASGI 的服务器，如 Daphne、Uvicorn 等，支持 WebSocket。
"""
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application


# 设置 Django 环境变量，指定使用的配置模块，确保应用正确初始化
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

# 初始化 Django ASGI 应用，处理 HTTP 和 WebSocket 之外的协议
django_asgi_app = get_asgi_application()

# 导入路由配置，需要在环境变量设置后导入，确保 Django 应用已正确初始化
from exercise import routing as exercise_routing  # noqa: E402


# ASGI 应用路由配置：根据协议类型分发请求到相应的处理器
application = ProtocolTypeRouter(
    {
        # HTTP 请求由 Django ASGI 应用处理
        "http": django_asgi_app,
        # WebSocket 请求经过认证中间件和主机验证后，由运动模块的路由处理
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(exercise_routing.websocket_urlpatterns))
        ),
    }
)

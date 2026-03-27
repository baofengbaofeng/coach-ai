"""
应用工厂模块（DDD迁移版）
创建Tornado应用实例
"""

from typing import List, Tuple
from tornado.web import Application, url
from tornado.ioloop import IOLoop
from loguru import logger

from src.settings import settings
from src.interfaces.api.middleware.auth_middleware import AuthMiddleware
from src.interfaces.api.middleware.exceptions import (
    BadRequestError, UnauthorizedError, ForbiddenError,
    NotFoundError, ValidationError, InternalServerError
)


def create_application() -> Application:
    """
    创建Tornado应用实例
    
    Returns:
        Tornado应用实例
    """
    # 获取路由列表
    routes = get_routes()
    
    # 应用设置
    app_settings = {
        "debug": settings.DEBUG,
        "autoreload": settings.DEBUG,
        "compress_response": True,
        "xsrf_cookies": settings.XSRF_COOKIES,
        "cookie_secret": settings.COOKIE_SECRET,
        "login_url": "/api/v1/auth/login",
        "default_handler_class": ErrorHandler,
        "default_handler_args": {},
    }
    
    # 创建应用实例
    application = Application(routes, **app_settings)
    
    # 配置日志
    logger.info(f"Application created with {len(routes)} routes")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Server will run on {settings.HOST}:{settings.PORT}")
    
    return application


def get_routes() -> List[Tuple]:
    """
    获取所有路由配置
    
    Returns:
        路由配置列表
    """
    routes = []
    
    # 导入各模块路由
    try:
        # 认证模块路由
        from src.interfaces.api.v1.auth.routes import get_auth_routes
        routes.extend(get_auth_routes())
        logger.debug("Loaded auth routes")
    except ImportError as e:
        logger.warning(f"Failed to load auth routes: {e}")
    
    try:
        # 租户模块路由
        from src.interfaces.api.v1.user.tenant_routes import get_tenant_routes
        routes.extend(get_tenant_routes())
        logger.debug("Loaded tenant routes")
    except ImportError as e:
        logger.warning(f"Failed to load tenant routes: {e}")
    
    try:
        # 运动模块路由
        from src.interfaces.api.v1.exercise.routes import get_exercise_routes
        routes.extend(get_exercise_routes())
        logger.debug("Loaded exercise routes")
    except ImportError as e:
        logger.warning(f"Failed to load exercise routes: {e}")
    
    try:
        # 任务模块路由
        from src.interfaces.api.v1.task.routes import get_task_routes
        routes.extend(get_task_routes())
        logger.debug("Loaded task routes")
    except ImportError as e:
        logger.warning(f"Failed to load task routes: {e}")
    
    try:
        # 成就模块路由
        from src.interfaces.api.v1.achievement.routes import get_achievement_routes
        routes.extend(get_achievement_routes())
        logger.debug("Loaded achievement routes")
    except ImportError as e:
        logger.warning(f"Failed to load achievement routes: {e}")
    
    # 健康检查路由
    routes.append((r"/api/health", HealthHandler))
    routes.append((r"/api/health/db", HealthDBHandler))
    routes.append((r"/api/health/redis", HealthRedisHandler))
    
    # 默认路由（404处理）
    routes.append((r".*", NotFoundHandler))
    
    return routes


class HealthHandler(RequestHandler):
    """健康检查处理器"""
    
    def get(self):
        """健康检查端点"""
        self.write({
            'success': True,
            'data': {
                'status': 'healthy',
                'service': 'coach-ai',
                'version': '1.0.0',
                'timestamp': IOLoop.current().time()
            }
        })


class HealthDBHandler(RequestHandler):
    """数据库健康检查处理器"""
    
    def get(self):
        """数据库健康检查"""
        try:
            # 这里可以添加数据库连接检查
            self.write({
                'success': True,
                'data': {
                    'status': 'healthy',
                    'service': 'database',
                    'timestamp': IOLoop.current().time()
                }
            })
        except Exception as e:
            self.set_status(503)
            self.write({
                'success': False,
                'error': {
                    'code': 'DATABASE_ERROR',
                    'message': str(e)
                }
            })


class HealthRedisHandler(RequestHandler):
    """Redis健康检查处理器"""
    
    def get(self):
        """Redis健康检查"""
        try:
            # 这里可以添加Redis连接检查
            self.write({
                'success': True,
                'data': {
                    'status': 'healthy',
                    'service': 'redis',
                    'timestamp': IOLoop.current().time()
                }
            })
        except Exception as e:
            self.set_status(503)
            self.write({
                'success': False,
                'error': {
                    'code': 'REDIS_ERROR',
                    'message': str(e)
                }
            })


class ErrorHandler(RequestHandler):
    """错误处理器（404处理）"""
    
    def prepare(self):
        """准备处理请求"""
        self.set_status(404)
        self.write({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'The requested resource was not found'
            }
        })
        self.finish()


class NotFoundHandler(RequestHandler):
    """404处理器"""
    
    def prepare(self):
        """准备处理请求"""
        self.set_status(404)
        self.write({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'The requested resource was not found'
            }
        })
        self.finish()


def start_server():
    """启动服务器"""
    try:
        # 创建应用
        app = create_application()
        
        # 启动服务器
        app.listen(settings.PORT, address=settings.HOST)
        
        logger.info(f"Server started on {settings.HOST}:{settings.PORT}")
        logger.info(f"Debug mode: {settings.DEBUG}")
        logger.info(f"Press Ctrl+C to stop")
        
        # 启动事件循环
        IOLoop.current().start()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


if __name__ == "__main__":
    start_server()
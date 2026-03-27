"""
应用工厂模块 - 简化版本
创建Tornado应用实例
"""

from typing import List, Tuple
from tornado.web import Application, url
from loguru import logger

from config import get_config
from .base_handler import BaseHandler


def create_application() -> Application:
    """
    创建Tornado应用实例
    
    Returns:
        Tornado应用实例
    """
    # 获取路由列表
    routes = get_routes()
    
    # 获取配置
    config = get_config()
    
    # 应用设置
    settings = {
        "debug": config.APP_DEBUG,
        "autoreload": config.APP_DEBUG,
        "compress_response": True,
        "cookie_secret": config.APP_SECRET_KEY,
        "xsrf_cookies": True,
        "login_url": "/api/auth/login",
        "default_handler_class": NotFoundHandler,
    }
    
    # 创建应用实例
    app = Application(routes, **settings)
    
    logger.info(f"Application created with {len(routes)} routes")
    logger.info(f"Debug mode: {config.APP_DEBUG}")
    
    return app


def get_routes() -> List[Tuple]:
    """
    获取所有路由 - 简化版本
    
    Returns:
        路由列表
    """
    # 只包含基础健康检查路由
    routes = [
        url(r"/api/health", HealthCheckHandler, name="health_check"),
        url(r"/api/health/db", DatabaseHealthHandler, name="db_health"),
        url(r"/api/health/redis", RedisHealthHandler, name="redis_health"),
    ]
    
    return routes


class HealthCheckHandler(BaseHandler):
    """健康检查处理器"""
    
    async def get(self):
        """健康检查端点"""
        from config import get_config
        config = get_config()
        
        self.success({
            "status": "healthy",
            "service": "coach-ai",
            "version": "1.0.0",
            "environment": config.APP_ENV,
            "timestamp": self.request.request_time()
        })


class DatabaseHealthHandler(BaseHandler):
    """数据库健康检查处理器"""
    
    async def get(self):
        """数据库健康检查端点"""
        try:
            # 尝试导入数据库连接
            from database.connection import get_db_session
            with get_db_session() as session:
                # 执行简单查询
                session.execute("SELECT 1")
            
            self.success({
                "status": "healthy",
                "service": "database",
                "timestamp": self.request.request_time()
            })
        except Exception as e:
            self.error(
                error_code="DATABASE_ERROR",
                message=f"Database connection failed: {str(e)}",
                status_code=503
            )


class RedisHealthHandler(BaseHandler):
    """Redis健康检查处理器"""
    
    async def get(self):
        """Redis健康检查端点"""
        try:
            # 尝试导入Redis客户端
            from database.redis_client import redis_client
            
            # 测试Redis连接
            redis_client.ping()
            
            self.success({
                "status": "healthy",
                "service": "redis",
                "timestamp": self.request.request_time()
            })
        except Exception as e:
            self.error(
                error_code="REDIS_ERROR",
                message=f"Redis connection failed: {str(e)}",
                status_code=503
            )


class NotFoundHandler(BaseHandler):
    """404处理器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 确保middlewares属性存在
        if not hasattr(self, 'middlewares'):
            self.middlewares = []
    
    async def prepare(self):
        """处理未找到的路由"""
        self.set_status(404)
        self.error(
            error_code="NOT_FOUND",
            message="The requested resource was not found",
            status_code=404
        )
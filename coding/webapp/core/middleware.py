"""
中间件模块
包含请求处理中间件
"""

import time
import json
from typing import Callable, Any
from loguru import logger
from tornado.web import RequestHandler

from config import config


class RequestLoggingMiddleware:
    """请求日志中间件"""
    
    def __init__(self, handler: RequestHandler):
        """
        初始化中间件
        
        Args:
            handler: RequestHandler实例
        """
        self.handler = handler
    
    async def prepare(self) -> None:
        """在请求处理前执行"""
        # 记录请求开始时间
        self.handler.request._start_time = time.time()
        
        # 记录请求信息（英文日志）
        logger.info(
            f"Request started: {self.handler.request.method} {self.handler.request.uri} "
            f"from {self.handler.request.remote_ip}"
        )
    
    def on_finish(self) -> None:
        """在请求处理后执行"""
        # 计算请求耗时
        duration = time.time() - getattr(self.handler.request, "_start_time", time.time())
        
        # 记录请求完成信息
        status_code = self.handler.get_status()
        logger.info(
            f"Request completed: {self.handler.request.method} {self.handler.request.uri} "
            f"status={status_code} duration={duration:.3f}s"
        )


class TenantMiddleware:
    """多租户中间件"""
    
    def __init__(self, handler: RequestHandler):
        """
        初始化多租户中间件
        
        Args:
            handler: RequestHandler实例
        """
        self.handler = handler
    
    async def prepare(self) -> None:
        """在请求处理前执行，提取租户ID"""
        from config import get_config
        config = get_config()
        
        # 从请求头获取租户ID
        tenant_id = self.handler.request.headers.get(config.TENANT_ID_HEADER, config.DEFAULT_TENANT_ID)
        
        # 验证租户ID格式
        if not tenant_id or not isinstance(tenant_id, str) or len(tenant_id) > 64:
            tenant_id = config.DEFAULT_TENANT_ID
        
        # 设置租户ID到请求对象
        self.handler.request.tenant_id = tenant_id
        
        # 记录租户信息（英文日志）
        logger.debug(f"Tenant context: {tenant_id}")


class JSONMiddleware:
    """JSON处理中间件"""
    
    def __init__(self, handler: RequestHandler):
        """
        初始化JSON中间件
        
        Args:
            handler: RequestHandler实例
        """
        self.handler = handler
    
    async def prepare(self) -> None:
        """在请求处理前执行，解析JSON请求体"""
        content_type = self.handler.request.headers.get("Content-Type", "")
        
        if "application/json" in content_type and self.handler.request.body:
            try:
                # 解析JSON请求体
                json_data = json.loads(self.handler.request.body.decode("utf-8"))
                self.handler.request.json = json_data
            except json.JSONDecodeError:
                # JSON解析失败，设置空字典
                self.handler.request.json = {}
                logger.warning(f"Invalid JSON in request body: {self.handler.request.body[:100]}")
        else:
            self.handler.request.json = {}


class CORSMiddleware:
    """CORS跨域中间件"""
    
    def __init__(self, handler: RequestHandler):
        """
        初始化CORS中间件
        
        Args:
            handler: RequestHandler实例
        """
        self.handler = handler
    
    def set_default_headers(self) -> None:
        """设置默认响应头"""
        # CORS头
        self.handler.set_header("Access-Control-Allow-Origin", "*")
        self.handler.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.handler.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Tenant-ID")
        self.handler.set_header("Access-Control-Allow-Credentials", "true")
        self.handler.set_header("Access-Control-Max-Age", "86400")
        
        # 安全头
        self.handler.set_header("X-Content-Type-Options", "nosniff")
        self.handler.set_header("X-Frame-Options", "DENY")
        self.handler.set_header("X-XSS-Protection", "1; mode=block")
    
    async def options(self, *args, **kwargs) -> None:
        """处理OPTIONS预检请求"""
        self.handler.set_status(204)
        self.handler.finish()


class MiddlewareManager:
    """中间件管理器"""
    
    # 中间件类列表（按执行顺序）
    MIDDLEWARE_CLASSES = [
        RequestLoggingMiddleware,
        TenantMiddleware,
        JSONMiddleware,
        CORSMiddleware
    ]
    
    @classmethod
    def get_middleware_classes(cls):
        """
        获取中间件类列表，动态包含认证中间件
        
        Returns:
            list: 中间件类列表
        """
        try:
            from tornado.core.auth_middleware import (
                JWTAuthMiddleware, 
                PermissionMiddleware, 
                RateLimitMiddleware,
                update_middleware_classes
            )
            return update_middleware_classes()
        except ImportError:
            # 如果认证中间件模块不存在，返回基本中间件
            logger.warning("Auth middleware module not found, using basic middlewares only")
            return cls.MIDDLEWARE_CLASSES
    
    @classmethod
    def wrap_handler(cls, handler_class: type) -> type:
        """
        包装Handler类，添加中间件支持
        
        Args:
            handler_class: 要包装的Handler类
            
        Returns:
            包装后的Handler类
        """
        class WrappedHandler(handler_class):
            """包装后的Handler类"""
            
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.middlewares = []
                
                # 实例化所有中间件
                middleware_classes = cls.get_middleware_classes()
                for middleware_class in middleware_classes:
                    middleware = middleware_class(self)
                    self.middlewares.append(middleware)
            
            async def prepare(self) -> None:
                """执行所有中间件的prepare方法"""
                # 确保middlewares属性存在
                if not hasattr(self, 'middlewares'):
                    self.middlewares = []
                for middleware in self.middlewares:
                    if hasattr(middleware, "prepare"):
                        await middleware.prepare()
                # 调用父类的prepare方法
                super().prepare()
            
            def on_finish(self) -> None:
                """执行所有中间件的on_finish方法"""
                # 确保middlewares属性存在
                if not hasattr(self, 'middlewares'):
                    self.middlewares = []
                for middleware in self.middlewares:
                    if hasattr(middleware, "on_finish"):
                        middleware.on_finish()
                super().on_finish()
            
            def set_default_headers(self) -> None:
                """执行所有中间件的set_default_headers方法"""
                # 确保middlewares属性存在
                if not hasattr(self, 'middlewares'):
                    self.middlewares = []
                for middleware in self.middlewares:
                    if hasattr(middleware, "set_default_headers"):
                        middleware.set_default_headers()
                super().set_default_headers()
            
            async def options(self, *args, **kwargs) -> None:
                """处理OPTIONS请求"""
                for middleware in self.middlewares:
                    if hasattr(middleware, "options"):
                        await middleware.options(*args, **kwargs)
                        return
                await super().options(*args, **kwargs)
        
        return WrappedHandler
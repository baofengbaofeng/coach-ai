"""
中间件管理器模块（DDD迁移版）
中间件管理和请求处理
"""

import time
from typing import Any, Callable, Dict, List, Optional
from tornado.web import RequestHandler
from loguru import logger

from src.settings import settings


class MiddlewareManager:
    """中间件管理器"""
    
    _middlewares: List[Callable] = []
    
    @classmethod
    def register_middleware(cls, middleware: Callable) -> None:
        """
        注册中间件
        
        Args:
            middleware: 中间件函数
        """
        cls._middlewares.append(middleware)
        logger.debug(f"Registered middleware: {middleware.__name__}")
    
    @classmethod
    def get_middlewares(cls) -> List[Callable]:
        """
        获取所有中间件
        
        Returns:
            中间件列表
        """
        return cls._middlewares.copy()
    
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
                self._middleware_chain = None
            
            async def prepare(self) -> None:
                """准备处理请求，执行中间件"""
                await self._execute_middlewares('before')
                await super().prepare()
            
            async def on_finish(self) -> None:
                """请求完成，执行中间件"""
                await super().on_finish()
                await self._execute_middlewares('after')
            
            async def _execute_middlewares(self, phase: str) -> None:
                """执行中间件"""
                for middleware in cls._middlewares:
                    try:
                        if phase == 'before':
                            await middleware.before_request(self)
                        elif phase == 'after':
                            await middleware.after_request(self)
                    except Exception as e:
                        logger.error(f"Middleware error ({middleware.__name__}, {phase}): {e}")
                        # 继续执行其他中间件，不中断请求
        
        return WrappedHandler
    
    @classmethod
    def initialize_default_middlewares(cls) -> None:
        """初始化默认中间件"""
        # 注册日志中间件
        cls.register_middleware(LoggingMiddleware())
        
        # 注册CORS中间件
        cls.register_middleware(CORSMiddleware())
        
        # 注册请求验证中间件
        cls.register_middleware(RequestValidationMiddleware())
        
        # 注册速率限制中间件
        cls.register_middleware(RateLimitMiddleware())
        
        logger.info(f"Initialized {len(cls._middlewares)} default middlewares")


class BaseMiddleware:
    """基础中间件类"""
    
    async def before_request(self, handler: RequestHandler) -> None:
        """请求前处理"""
        pass
    
    async def after_request(self, handler: RequestHandler) -> None:
        """请求后处理"""
        pass


class LoggingMiddleware(BaseMiddleware):
    """日志中间件"""
    
    async def before_request(self, handler: RequestHandler) -> None:
        """请求前记录日志"""
        handler._request_start_time = time.time()
        
        method = handler.request.method
        uri = handler.request.uri
        remote_ip = handler.request.remote_ip
        user_agent = handler.request.headers.get('User-Agent', 'Unknown')
        
        logger.info(f"[{method}] {uri} - IP: {remote_ip} - UA: {user_agent[:50]}")
    
    async def after_request(self, handler: RequestHandler) -> None:
        """请求后记录日志"""
        if hasattr(handler, '_request_start_time'):
            request_time = time.time() - handler._request_start_time
            
            method = handler.request.method
            uri = handler.request.uri
            status = handler.get_status()
            
            if status >= 400:
                logger.warning(f"[{method}] {uri} - Status: {status} - Time: {request_time:.3f}s")
            elif request_time > 1.0:  # 慢请求
                logger.warning(f"Slow request: {method} {uri} took {request_time:.2f}s")
            else:
                logger.debug(f"[{method}] {uri} - Status: {status} - Time: {request_time:.3f}s")


class CORSMiddleware(BaseMiddleware):
    """CORS中间件"""
    
    async def before_request(self, handler: RequestHandler) -> None:
        """设置CORS头"""
        # 已经在BaseHandler中设置了，这里可以添加额外的CORS逻辑
        pass
    
    async def after_request(self, handler: RequestHandler) -> None:
        """请求后处理CORS"""
        pass


class RequestValidationMiddleware(BaseMiddleware):
    """请求验证中间件"""
    
    async def before_request(self, handler: RequestHandler) -> None:
        """验证请求"""
        # 检查请求方法
        if handler.request.method not in ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']:
            from src.interfaces.api.middleware.exceptions import BadRequestError
            raise BadRequestError(f"Unsupported method: {handler.request.method}")
        
        # 检查内容类型（对于POST/PUT请求）
        if handler.request.method in ['POST', 'PUT', 'PATCH']:
            content_type = handler.request.headers.get('Content-Type', '')
            if not content_type.startswith('application/json'):
                from src.interfaces.api.middleware.exceptions import BadRequestError
                raise BadRequestError("Content-Type must be application/json")
        
        # 检查请求体大小限制
        max_body_size = settings.MAX_REQUEST_BODY_SIZE
        if len(handler.request.body) > max_body_size:
            from src.interfaces.api.middleware.exceptions import BadRequestError
            raise BadRequestError(f"Request body too large (max {max_body_size} bytes)")


class RateLimitMiddleware(BaseMiddleware):
    """速率限制中间件"""
    
    _request_counts: Dict[str, List[float]] = {}
    
    async def before_request(self, handler: RequestHandler) -> None:
        """检查速率限制"""
        if not settings.RATE_LIMIT_ENABLED:
            return
        
        client_ip = handler.request.remote_ip
        current_time = time.time()
        
        # 清理旧记录
        self._cleanup_old_records(client_ip, current_time)
        
        # 获取客户端请求记录
        if client_ip not in self._request_counts:
            self._request_counts[client_ip] = []
        
        # 检查速率限制
        request_times = self._request_counts[client_ip]
        window_start = current_time - settings.RATE_LIMIT_WINDOW_SECONDS
        
        # 统计窗口内的请求数
        recent_requests = [t for t in request_times if t > window_start]
        
        if len(recent_requests) >= settings.RATE_LIMIT_MAX_REQUESTS:
            from src.interfaces.api.middleware.exceptions import TooManyRequestsError
            raise TooManyRequestsError(
                f"Rate limit exceeded. Maximum {settings.RATE_LIMIT_MAX_REQUESTS} "
                f"requests per {settings.RATE_LIMIT_WINDOW_SECONDS} seconds"
            )
        
        # 记录本次请求
        request_times.append(current_time)
    
    def _cleanup_old_records(self, client_ip: str, current_time: float) -> None:
        """清理旧的请求记录"""
        if client_ip in self._request_counts:
            window_start = current_time - settings.RATE_LIMIT_WINDOW_SECONDS
            self._request_counts[client_ip] = [
                t for t in self._request_counts[client_ip] 
                if t > window_start
            ]
            
            # 如果记录为空，删除键
            if not self._request_counts[client_ip]:
                del self._request_counts[client_ip]
    
    async def after_request(self, handler: RequestHandler) -> None:
        """请求后处理"""
        pass


# 自定义异常类
class TooManyRequestsError(Exception):
    """请求过多异常"""
    
    def __init__(self, message: str = "Too many requests"):
        super().__init__(message)
        self.code = "TOO_MANY_REQUESTS"
        self.status_code = 429


# 初始化默认中间件
MiddlewareManager.initialize_default_middlewares()
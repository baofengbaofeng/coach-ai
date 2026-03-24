"""
公共中间件模块，提供跨模块使用的自定义中间件。
按照豆包AI助手最佳实践：提供类型安全的中间件。
"""
from __future__ import annotations

import logging
import time
from typing import Any, Callable, Optional
from urllib.parse import urlparse

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from apps.common.utils import Timer


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 请求日志中间件 ====================
class RequestLoggingMiddleware(MiddlewareMixin):
    """
    请求日志中间件，记录所有HTTP请求的详细信息。
    """
    
    def process_request(self, request: HttpRequest) -> None:
        """
        处理请求前。
        
        Args:
            request: HTTP请求对象
        """
        # 记录请求开始时间
        request.start_time = time.time()
        
        # 记录请求信息
        _LOGGER.info(
            "请求开始: %s %s (客户端: %s)",
            request.method,
            request.path,
            request.META.get("REMOTE_ADDR", "未知"),
        )
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        处理响应后。
        
        Args:
            request: HTTP请求对象
            response: HTTP响应对象
            
        Returns:
            HTTP响应对象
        """
        # 计算请求处理时间
        if hasattr(request, "start_time"):
            duration: float = time.time() - request.start_time
        else:
            duration = 0.0
        
        # 记录响应信息
        _LOGGER.info(
            "请求完成: %s %s -> %s (耗时: %.3f秒)",
            request.method,
            request.path,
            response.status_code,
            duration,
        )
        
        return response
    
    def process_exception(self, request: HttpRequest, exception: Exception) -> Optional[HttpResponse]:
        """
        处理异常。
        
        Args:
            request: HTTP请求对象
            exception: 异常对象
            
        Returns:
            HTTP响应对象或None
        """
        # 计算请求处理时间
        if hasattr(request, "start_time"):
            duration: float = time.time() - request.start_time
        else:
            duration = 0.0
        
        # 记录异常信息
        _LOGGER.error(
            "请求异常: %s %s -> %s (耗时: %.3f秒)",
            request.method,
            request.path,
            str(exception),
            duration,
            exc_info=True,
        )
        
        return None


# ==================== CORS中间件 ====================
class CorsMiddleware(MiddlewareMixin):
    """
    CORS中间件，处理跨域请求。
    """
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        处理响应，添加CORS头。
        
        Args:
            request: HTTP请求对象
            response: HTTP响应对象
            
        Returns:
            HTTP响应对象
        """
        # 获取允许的源
        allowed_origins: list = getattr(settings, "CORS_ALLOWED_ORIGINS", [])
        
        # 获取请求源
        origin: Optional[str] = request.META.get("HTTP_ORIGIN")
        
        if origin:
            # 检查是否在允许的源列表中
            if origin in allowed_origins or "*" in allowed_origins:
                response["Access-Control-Allow-Origin"] = origin
                response["Access-Control-Allow-Credentials"] = "true"
        
        # 添加其他CORS头
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-Requested-With, "
            "Accept, Origin, Cache-Control, X-CSRFToken"
        )
        response["Access-Control-Expose-Headers"] = "Content-Length, Content-Range"
        response["Access-Control-Max-Age"] = "86400"  # 24小时
        
        return response


# ==================== 性能监控中间件 ====================
class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    性能监控中间件，监控API性能。
    """
    
    def process_request(self, request: HttpRequest) -> None:
        """
        处理请求前。
        
        Args:
            request: HTTP请求对象
        """
        # 创建计时器
        request.performance_timer = Timer(f"API请求: {request.method} {request.path}")
        request.performance_timer.start()
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        处理响应后。
        
        Args:
            request: HTTP请求对象
            response: HTTP响应对象
            
        Returns:
            HTTP响应对象
        """
        # 停止计时器并记录性能数据
        if hasattr(request, "performance_timer"):
            request.performance_timer.stop()
            
            # 记录慢请求
            if request.performance_timer.elapsed_time > 1.0:  # 超过1秒
                _LOGGER.warning(
                    "慢请求: %s %s (耗时: %.3f秒)",
                    request.method,
                    request.path,
                    request.performance_timer.elapsed_time,
                )
            
            # 添加性能头信息
            response["X-Request-Duration"] = f"{request.performance_timer.elapsed_time:.3f}"
        
        return response


# ==================== 安全中间件 ====================
class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    安全头中间件，添加安全相关的HTTP头。
    """
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        处理响应，添加安全头。
        
        Args:
            request: HTTP请求对象
            response: HTTP响应对象
            
        Returns:
            HTTP响应对象
        """
        # 添加安全头
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # 添加CSP头（内容安全策略）
        csp_policy: str = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response["Content-Security-Policy"] = csp_policy
        
        # 添加HSTS头（仅在HTTPS时）
        if request.is_secure():
            response["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


# ==================== 用户活动中间件 ====================
class UserActivityMiddleware(MiddlewareMixin):
    """
    用户活动中间件，跟踪用户活动。
    """
    
    def process_request(self, request: HttpRequest) -> None:
        """
        处理请求前。
        
        Args:
            request: HTTP请求对象
        """
        # 检查用户是否已认证
        if hasattr(request, "user") and request.user.is_authenticated:
            # 记录用户活动
            user_agent: str = request.META.get("HTTP_USER_AGENT", "未知")
            ip_address: str = request.META.get("REMOTE_ADDR", "未知")
            
            _LOGGER.debug(
                "用户活动: %s (%s) 访问 %s %s (UA: %s, IP: %s)",
                request.user.username,
                request.user.email or "无邮箱",
                request.method,
                request.path,
                user_agent[:50],  # 截断用户代理字符串
                ip_address,
            )
            
            # 更新用户最后活动时间
            try:
                request.user.last_activity = timezone.now()
                request.user.save(update_fields=["last_activity"])
            except Exception as e:
                _LOGGER.warning("更新用户活动时间失败: %s", str(e))


# ==================== API版本中间件 ====================
class ApiVersionMiddleware(MiddlewareMixin):
    """
    API版本中间件，处理API版本控制。
    """
    
    def process_request(self, request: HttpRequest) -> None:
        """
        处理请求前，提取API版本。
        
        Args:
            request: HTTP请求对象
        """
        # 从URL路径中提取版本
        path_parts: list = request.path.split("/")
        
        if len(path_parts) >= 2 and path_parts[1].startswith("v"):
            try:
                version_str: str = path_parts[1][1:]  # 去掉"v"前缀
                request.api_version = float(version_str)
            except (ValueError, IndexError):
                request.api_version = 1.0  # 默认版本
        else:
            request.api_version = 1.0  # 默认版本
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        处理响应，添加API版本头。
        
        Args:
            request: HTTP请求对象
            response: HTTP响应对象
            
        Returns:
            HTTP响应对象
        """
        # 添加API版本头
        if hasattr(request, "api_version"):
            response["X-API-Version"] = str(request.api_version)
        
        return response


# ==================== 请求ID中间件 ====================
class RequestIdMiddleware(MiddlewareMixin):
    """
    请求ID中间件，为每个请求生成唯一ID。
    """
    
    def process_request(self, request: HttpRequest) -> None:
        """
        处理请求前，生成请求ID。
        
        Args:
            request: HTTP请求对象
        """
        # 生成请求ID
        import uuid
        request.request_id = str(uuid.uuid4())
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        处理响应，添加请求ID头。
        
        Args:
            request: HTTP请求对象
            response: HTTP响应对象
            
        Returns:
            HTTP响应对象
        """
        # 添加请求ID头
        if hasattr(request, "request_id"):
            response["X-Request-ID"] = request.request_id
        
        return response


# ==================== 导出列表 ====================
__all__: list = [
    "RequestLoggingMiddleware",
    "CorsMiddleware",
    "PerformanceMonitoringMiddleware",
    "SecurityHeadersMiddleware",
    "UserActivityMiddleware",
    "ApiVersionMiddleware",
    "RequestIdMiddleware",
]
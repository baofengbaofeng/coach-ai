"""
自定义中间件模块，提供项目级别的请求处理、响应处理和性能监控功能。
按照豆包AI助手最佳实践和coding-style.md规范实现。
"""
from __future__ import annotations

import logging
import time
from typing import Any, Callable, Optional, Tuple
from uuid import uuid4

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from core.constants import HttpStatus


# ==================== 日志记录器 ====================
# 模块级别的日志记录器，用于记录请求处理信息和调试信息，遵循coding-style.md规范
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 请求日志中间件 ====================
class RequestLoggingMiddleware(MiddlewareMixin):
    """
    请求日志中间件，记录所有HTTP请求的详细信息，包括请求路径、方法、处理时间和响应状态。
    
    Attributes:
        get_response (Callable): Django 请求处理链中的下一个处理函数
    """
    
    def __init__(self, get_response: Callable) -> None:
        """
        初始化请求日志中间件实例，设置请求处理函数和中间件配置。
        
        Args:
            get_response (Callable): Django 请求处理链中的下一个处理函数
            
        Returns:
            None: 此方法不返回值，但会初始化中间件实例的各种属性
        """
        self.get_response: Callable = get_response
        super().__init__(get_response)
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        处理HTTP请求，记录请求开始和结束的详细信息，计算请求处理时间。
        
        Args:
            request (HttpRequest): Django HTTP 请求对象，包含请求的所有信息
            
        Returns:
            HttpResponse: 处理后的 HTTP 响应对象
            
        Raises:
            此方法不直接抛出异常，但会记录处理过程中发生的任何异常
        """
        # 生成唯一的请求ID，用于追踪请求处理链路
        request_id: str = str(uuid4())[:8]
        request.request_id = request_id
        
        # 记录请求开始信息
        start_time: float = time.time()
        _LOGGER.info(
            "请求开始 - ID: %s, 路径: %s, 方法: %s, IP: %s, 用户: %s",
            request_id,
            request.path,
            request.method,
            self._get_client_ip(request),
            self._get_user_info(request),
        )
        
        try:
            # 调用下一个中间件或视图函数处理请求
            response: HttpResponse = self.get_response(request)
            
            # 计算请求处理时间
            process_time: float = time.time() - start_time
            
            # 记录请求完成信息
            _LOGGER.info(
                "请求完成 - ID: %s, 状态: %d, 时间: %.3f秒, 路径: %s",
                request_id,
                response.status_code,
                process_time,
                request.path,
            )
            
            # 添加自定义响应头
            response["X-Request-ID"] = request_id
            response["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
            
        except Exception as exc:
            # 记录请求处理异常信息
            process_time = time.time() - start_time
            _LOGGER.error(
                "请求异常 - ID: %s, 错误: %s, 时间: %.3f秒, 路径: %s",
                request_id,
                str(exc),
                process_time,
                request.path,
                exc_info=True,
            )
            raise
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """
        获取客户端真实IP地址，处理代理服务器和负载均衡器的情况。
        
        Args:
            request (HttpRequest): Django HTTP 请求对象
            
        Returns:
            str: 客户端IP地址字符串，如果无法获取则返回 "unknown"
        """
        x_forwarded_for: Optional[str] = request.META.get("HTTP_X_FORWARDED_FOR")
        
        if x_forwarded_for:
            # 处理多个代理的情况，取第一个IP地址
            ip: str = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "unknown")
        
        return ip
    
    def _get_user_info(self, request: HttpRequest) -> str:
        """
        获取用户信息，包括用户ID和用户名，用于日志记录和审计。
        
        Args:
            request (HttpRequest): Django HTTP 请求对象
            
        Returns:
            str: 用户信息字符串，格式为 "用户ID:用户名" 或 "anonymous"
        """
        if hasattr(request, "user") and request.user.is_authenticated:
            return f"{request.user.id}:{request.user.username}"
        return "anonymous"


# ==================== 异常处理中间件 ====================
class ExceptionHandlingMiddleware(MiddlewareMixin):
    """
    异常处理中间件，捕获请求处理过程中的异常，提供统一的异常响应格式。
    
    Attributes:
        get_response (Callable): Django 请求处理链中的下一个处理函数
    """
    
    def __init__(self, get_response: Callable) -> None:
        """
        初始化异常处理中间件实例，设置请求处理函数和异常处理配置。
        
        Args:
            get_response (Callable): Django 请求处理链中的下一个处理函数
            
        Returns:
            None: 此方法不返回值，但会初始化中间件实例的各种属性
        """
        self.get_response: Callable = get_response
        super().__init__(get_response)
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        处理HTTP请求，捕获处理过程中的异常并提供统一的错误响应。
        
        Args:
            request (HttpRequest): Django HTTP 请求对象
            
        Returns:
            HttpResponse: 处理后的 HTTP 响应对象，如果发生异常则返回错误响应
            
        Raises:
            此方法会捕获所有异常并转换为统一的错误响应，不会向上抛出异常
        """
        try:
            response: HttpResponse = self.get_response(request)
            return response
            
        except Exception as exc:
            return self._handle_exception(exc, request)
    
    def _handle_exception(self, exc: Exception, request: HttpRequest) -> HttpResponse:
        """
        处理捕获的异常，根据异常类型生成统一的错误响应。
        
        Args:
            exc (Exception): 捕获的异常对象
            request (HttpRequest): 发生异常的 HTTP 请求对象
            
        Returns:
            HttpResponse: 统一的错误响应对象，包含错误代码、描述和详细信息
        """
        from core.exceptions import (
            BusinessValidationError,
            ResourceNotFoundException,
            AuthenticationFailedException,
            PermissionDeniedException,
            ServiceUnavailableException,
            RateLimitExceededException,
            CoachAIBaseException,
        )
        
        # 根据异常类型确定状态码和错误信息
        if isinstance(exc, BusinessValidationError):
            status_code: int = HttpStatus.BAD_REQUEST
            error_message: str = str(exc)
            error_code: str = "VALIDATION_ERROR"
        elif isinstance(exc, ResourceNotFoundException):
            status_code = HttpStatus.NOT_FOUND
            error_message = str(exc)
            error_code = "RESOURCE_NOT_FOUND"
        elif isinstance(exc, AuthenticationFailedException):
            status_code = HttpStatus.UNAUTHORIZED
            error_message = str(exc)
            error_code = "AUTHENTICATION_FAILED"
        elif isinstance(exc, PermissionDeniedException):
            status_code = HttpStatus.FORBIDDEN
            error_message = str(exc)
            error_code = "PERMISSION_DENIED"
        elif isinstance(exc, ServiceUnavailableException):
            status_code = HttpStatus.SERVICE_UNAVAILABLE
            error_message = str(exc)
            error_code = "SERVICE_UNAVAILABLE"
        elif isinstance(exc, RateLimitExceededException):
            status_code = HttpStatus.TOO_MANY_REQUESTS
            error_message = str(exc)
            error_code = "RATE_LIMIT_EXCEEDED"
        elif isinstance(exc, CoachAIBaseException):
            status_code = exc.status_code
            error_message = str(exc)
            error_code = exc.default_code
        else:
            # 未知异常，记录详细信息并返回通用错误响应
            _LOGGER.exception("未处理的异常: %s, 路径: %s", str(exc), request.path)
            status_code = HttpStatus.INTERNAL_SERVER_ERROR
            error_message = "服务器内部错误，请稍后重试"
            error_code = "INTERNAL_SERVER_ERROR"
        
        # 构建错误响应数据
        response_data: dict[str, Any] = {
            "success": False,
            "error": {
                "code": error_code,
                "message": error_message,
                "details": getattr(exc, "extra_data", {}),
            },
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "path": request.path,
            "request_id": getattr(request, "request_id", "unknown"),
        }
        
        # 创建并返回错误响应
        from django.http import JsonResponse
        return JsonResponse(response_data, status=status_code)


# ==================== CORS 中间件扩展 ====================
class CorsMiddleware(MiddlewareMixin):
    """
    CORS 中间件扩展，处理跨域请求的预检请求和响应头设置。
    
    Attributes:
        get_response (Callable): Django 请求处理链中的下一个处理函数
    """
    
    def __init__(self, get_response: Callable) -> None:
        """
        初始化 CORS 中间件实例，设置请求处理函数和 CORS 配置。
        
        Args:
            get_response (Callable): Django 请求处理链中的下一个处理函数
            
        Returns:
            None: 此方法不返回值，但会初始化中间件实例的各种属性
        """
        self.get_response: Callable = get_response
        super().__init__(get_response)
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        处理HTTP请求，添加CORS相关响应头，处理OPTIONS预检请求。
        
        Args:
            request (HttpRequest): Django HTTP 请求对象
            
        Returns:
            HttpResponse: 处理后的 HTTP 响应对象，包含 CORS 相关响应头
        """
        # 处理 OPTIONS 预检请求
        if request.method == "OPTIONS":
            response: HttpResponse = HttpResponse()
            response["Content-Length"] = "0"
        else:
            response = self.get_response(request)
        
        # 添加 CORS 响应头
        self._add_cors_headers(request, response)
        
        return response
    
    def _add_cors_headers(self, request: HttpRequest, response: HttpResponse) -> None:
        """
        添加 CORS 相关响应头到 HTTP 响应对象。
        
        Args:
            request (HttpRequest): Django HTTP 请求对象
            response (HttpResponse): Django HTTP 响应对象
            
        Returns:
            None: 此方法不返回值，但会修改响应对象的头部信息
        """
        # 允许的源，可以从配置中获取
        allowed_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
        
        # 获取请求来源
        origin: Optional[str] = request.META.get("HTTP_ORIGIN")
        
        if origin and origin in allowed_origins:
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
        
        # 添加其他 CORS 头部
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-Requested-With, X-CSRFToken"
        )
        response["Access-Control-Max-Age"] = "86400"  # 24小时


# ==================== 性能监控中间件 ====================
class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    性能监控中间件，监控请求处理性能，记录慢请求和性能指标。
    
    Attributes:
        get_response (Callable): Django 请求处理链中的下一个处理函数
        slow_request_threshold (float): 慢请求阈值（秒），超过此时间的请求会被记录
    """
    
    def __init__(self, get_response: Callable) -> None:
        """
        初始化性能监控中间件实例，设置请求处理函数和性能监控配置。
        
        Args:
            get_response (Callable): Django 请求处理链中的下一个处理函数
            
        Returns:
            None: 此方法不返回值，但会初始化中间件实例的各种属性
        """
        self.get_response: Callable = get_response
        self.slow_request_threshold: float = 1.0  # 1秒
        super().__init__(get_response)
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        处理HTTP请求，监控请求处理性能，记录慢请求信息。
        
        Args:
            request (HttpRequest): Django HTTP 请求对象
            
        Returns:
            HttpResponse: 处理后的 HTTP 响应对象
        """
        start_time: float = time.time()
        
        response: HttpResponse = self.get_response(request)
        
        process_time: float = time.time() - start_time
        
        # 记录慢请求
        if process_time > self.slow_request_threshold:
            _LOGGER.warning(
                "慢请求警告 - 路径: %s, 方法: %s, 时间: %.3f秒, 阈值: %.1f秒",
                request.path,
                request.method,
                process_time,
                self.slow_request_threshold,
            )
        
        # 添加性能监控头部
        response["X-Process-Time"] = f"{process_time:.3f}"
        
        return response


# ==================== 请求ID中间件 ====================
class RequestIdMiddleware(MiddlewareMixin):
    """
    请求ID中间件，为每个请求生成唯一的请求ID，便于请求追踪和日志关联。
    
    Attributes:
        get_response (Callable): Django 请求处理链中的下一个处理函数
    """
    
    def __init__(self, get_response: Callable) -> None:
        """
        初始化请求ID中间件实例，设置请求处理函数和请求ID生成配置。
        
        Args:
            get_response (Callable): Django 请求处理链中的下一个处理函数
            
        Returns:
            None: 此方法不返回值，但会初始化中间件实例的各种属性
        """
        self.get_response: Callable = get_response
        super().__init__(get_response)
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        处理HTTP请求，生成唯一的请求ID并添加到请求和响应中。
        
        Args:
            request (HttpRequest): Django HTTP 请求对象
            
        Returns:
            HttpResponse: 处理后的 HTTP 响应对象，包含请求ID头部
        """
        # 生成唯一的请求ID
        request_id: str = str(uuid4())
        
        # 将请求ID添加到请求对象中
        request.request_id = request_id
        
        response: HttpResponse = self.get_response(request)
        
        # 将请求ID添加到响应头部
        response["X-Request-ID"] = request_id
        
        return response


# ==================== 导出定义 ====================
__all__: list[str] = [
    "RequestLoggingMiddleware",
    "ExceptionHandlingMiddleware",
    "CorsMiddleware",
    "PerformanceMonitoringMiddleware",
    "RequestIdMiddleware",
]

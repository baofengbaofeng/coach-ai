"""
异常处理模块
定义应用级别的异常类
"""

from typing import Any, Dict
from tornado.web import HTTPError


class BaseAPIError(HTTPError):
    """基础API异常类"""
    
    def __init__(self, status_code: int, error_code: str, message: str, details: Dict[str, Any] = None):
        """
        初始化异常
        
        Args:
            status_code: HTTP状态码
            error_code: 错误代码
            message: 错误消息（英文）
            details: 错误详情
        """
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(status_code, reason=message)


class ValidationError(BaseAPIError):
    """数据验证错误"""
    
    def __init__(self, message: str = "Validation failed", details: Dict[str, Any] = None):
        super().__init__(400, "VALIDATION_ERROR", message, details)


class AuthenticationError(BaseAPIError):
    """认证错误"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(401, "AUTHENTICATION_ERROR", message)


class AuthorizationError(BaseAPIError):
    """授权错误"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(403, "AUTHORIZATION_ERROR", message)


class NotFoundError(BaseAPIError):
    """资源未找到错误"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(404, "NOT_FOUND", message)


class ConflictError(BaseAPIError):
    """资源冲突错误"""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(409, "CONFLICT", message)


class RateLimitError(BaseAPIError):
    """速率限制错误"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(429, "RATE_LIMIT", message)


class InternalServerError(BaseAPIError):
    """内部服务器错误"""
    
    def __init__(self, message: str = "Internal server error"):
        super().__init__(500, "INTERNAL_ERROR", message)


class DatabaseError(BaseAPIError):
    """数据库错误"""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(500, "DATABASE_ERROR", message)


class ExternalServiceError(BaseAPIError):
    """外部服务错误"""
    
    def __init__(self, message: str = "External service error"):
        super().__init__(502, "EXTERNAL_SERVICE_ERROR", message)
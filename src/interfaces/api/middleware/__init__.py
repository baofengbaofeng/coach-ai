"""
API中间件模块
包含认证、授权、错误处理等中间件
"""

from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    RateLimitError,
    MaintenanceError
)
from .auth_middleware import (
    JWTAuthMiddleware,
    auth_required,
    permission_required,
    role_required
)

__all__ = [
    # 异常类
    'AuthenticationError',
    'AuthorizationError',
    'ValidationError',
    'RateLimitError',
    'MaintenanceError',
    
    # 认证中间件
    'JWTAuthMiddleware',
    'auth_required',
    'permission_required',
    'role_required',
]
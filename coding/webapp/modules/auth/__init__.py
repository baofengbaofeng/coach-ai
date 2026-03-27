"""
认证模块
处理用户认证、授权和会话管理
"""

from .handlers import (
    RegisterHandler,
    LoginHandler,
    LogoutHandler,
    RefreshTokenHandler,
    VerifyTokenHandler,
    RequestPasswordResetHandler,
    ResetPasswordHandler,
    VerifyEmailHandler,
    ProfileHandler
)

from .services import auth_service
from .models import (
    RegisterRequest,
    LoginRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
    ProfileUpdateRequest,
    UserResponse,
    TenantInfoResponse,
    LoginResponse,
    RegisterResponse,
    ProfileResponse,
    TokenVerifyResponse,
    TokenRefreshResponse,
    MessageResponse,
    ErrorResponse,
    AUTH_TAGS,
    AUTH_DESCRIPTION
)

__all__ = [
    # 处理器
    'RegisterHandler',
    'LoginHandler',
    'LogoutHandler',
    'RefreshTokenHandler',
    'VerifyTokenHandler',
    'RequestPasswordResetHandler',
    'ResetPasswordHandler',
    'VerifyEmailHandler',
    'ProfileHandler',
    
    # 服务
    'auth_service',
    
    # 模型
    'RegisterRequest',
    'LoginRequest',
    'PasswordResetRequest',
    'PasswordResetConfirmRequest',
    'ProfileUpdateRequest',
    'UserResponse',
    'TenantInfoResponse',
    'LoginResponse',
    'RegisterResponse',
    'ProfileResponse',
    'TokenVerifyResponse',
    'TokenRefreshResponse',
    'MessageResponse',
    'ErrorResponse',
    
    # API文档
    'AUTH_TAGS',
    'AUTH_DESCRIPTION'
]
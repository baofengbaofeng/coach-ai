"""
认证API模块
包含用户认证相关的HTTP处理器和路由
"""

from .handlers import (
    BaseHandler,
    RegisterHandler,
    LoginHandler,
    LogoutHandler,
    RefreshTokenHandler,
    VerifyEmailHandler,
    ForgotPasswordHandler,
    ResetPasswordHandler,
    ProfileHandler
)
from .routes import get_auth_routes

__all__ = [
    # 处理器
    'BaseHandler',
    'RegisterHandler',
    'LoginHandler',
    'LogoutHandler',
    'RefreshTokenHandler',
    'VerifyEmailHandler',
    'ForgotPasswordHandler',
    'ResetPasswordHandler',
    'ProfileHandler',
    
    # 路由
    'get_auth_routes',
]
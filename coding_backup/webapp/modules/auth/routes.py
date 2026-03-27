"""
认证模块路由配置
"""

from typing import List, Tuple
from tornado.web import url
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


def get_auth_routes() -> List[Tuple]:
    """
    获取认证模块路由
    
    Returns:
        路由列表
    """
    return [
        url(r"/api/auth/register", RegisterHandler, name="register"),
        url(r"/api/auth/login", LoginHandler, name="login"),
        url(r"/api/auth/logout", LogoutHandler, name="logout"),
        url(r"/api/auth/refresh", RefreshTokenHandler, name="refresh_token"),
        url(r"/api/auth/verify", VerifyTokenHandler, name="verify_token"),
        url(r"/api/auth/password/reset/request", RequestPasswordResetHandler, name="request_password_reset"),
        url(r"/api/auth/password/reset", ResetPasswordHandler, name="reset_password"),
        url(r"/api/auth/email/verify", VerifyEmailHandler, name="verify_email"),
        url(r"/api/auth/profile", ProfileHandler, name="profile"),
    ]
"""
认证路由配置
"""

from .handlers import (
    RegisterHandler,
    LoginHandler,
    LogoutHandler,
    RefreshTokenHandler,
    VerifyEmailHandler,
    ForgotPasswordHandler,
    ResetPasswordHandler,
    ProfileHandler
)


def get_auth_routes():
    """获取认证路由配置"""
    return [
        (r"/api/auth/register", RegisterHandler),
        (r"/api/auth/login", LoginHandler),
        (r"/api/auth/logout", LogoutHandler),
        (r"/api/auth/refresh", RefreshTokenHandler),
        (r"/api/auth/verify-email", VerifyEmailHandler),
        (r"/api/auth/forgot-password", ForgotPasswordHandler),
        (r"/api/auth/reset-password", ResetPasswordHandler),
        (r"/api/auth/profile", ProfileHandler),
    ]
"""
认证处理器（简化迁移版）
处理用户认证相关的HTTP请求
"""

import logging
from typing import Dict, Any

from tornado.web import RequestHandler
from src.interfaces.api.middleware.exceptions import ValidationError, AuthenticationError
from src.interfaces.api.middleware.auth_middleware import auth_required
from src.application.services.auth_service import AuthService

logger = logging.getLogger(__name__)


class BaseHandler(RequestHandler):
    """基础处理器"""
    
    def get_json_body(self) -> Dict[str, Any]:
        """获取JSON请求体"""
        try:
            import json
            return json.loads(self.request.body.decode('utf-8'))
        except Exception as e:
            raise ValidationError(f"Invalid JSON: {str(e)}")
    
    def write_success(self, data: Dict[str, Any] = None, message: str = "Success"):
        """写入成功响应"""
        response = {
            "success": True,
            "message": message,
            "data": data or {}
        }
        self.write(response)
    
    def write_error(self, status_code: int, message: str = None, error_code: str = None):
        """写入错误响应"""
        response = {
            "success": False,
            "error": {
                "code": error_code or f"HTTP_{status_code}",
                "message": message or self._reason
            }
        }
        self.set_status(status_code)
        self.write(response)


class RegisterHandler(BaseHandler):
    """
    用户注册处理器
    """
    
    async def post(self):
        """
        注册新用户
        POST /api/auth/register
        """
        try:
            # 验证请求数据
            data = self.get_json_body()
            required_fields = ['username', 'email', 'password']
            
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValidationError(f"Field '{field}' is required")
            
            # 验证邮箱格式
            if '@' not in data['email']:
                raise ValidationError("Invalid email format")
            
            # 验证密码强度
            if len(data['password']) < 8:
                raise ValidationError("Password must be at least 8 characters")
            
            # 调用应用服务注册用户
            auth_service = AuthService()
            result = await auth_service.register_user(data)
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Registration failed'))
            
            self.write_success(result.get('data'), "Registration successful")
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            self.write_error(400, str(e))


class LoginHandler(BaseHandler):
    """
    用户登录处理器
    """
    
    async def post(self):
        """
        用户登录
        POST /api/auth/login
        """
        try:
            data = self.get_json_body()
            
            if 'identifier' not in data or not data['identifier']:
                raise ValidationError("Identifier (username or email) is required")
            
            if 'password' not in data or not data['password']:
                raise ValidationError("Password is required")
            
            # 调用应用服务登录
            auth_service = AuthService()
            result = await auth_service.login_user(
                identifier=data['identifier'],
                password=data['password']
            )
            
            if not result.get('success'):
                raise AuthenticationError(result.get('error', 'Login failed'))
            
            self.write_success(result.get('data'), "Login successful")
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            self.write_error(401, str(e))


class LogoutHandler(BaseHandler):
    """
    用户登出处理器
    """
    
    @auth_required
    async def post(self):
        """
        用户登出
        POST /api/auth/logout
        """
        try:
            # 获取当前用户的令牌
            token_payload = getattr(self, 'token_payload', None)
            if not token_payload:
                raise AuthenticationError("Not authenticated")
            
            # 调用应用服务登出
            auth_service = AuthService()
            result = await auth_service.logout_user(token_payload)
            
            self.write_success(result.get('data'), "Logout successful")
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            self.write_error(400, str(e))


class RefreshTokenHandler(BaseHandler):
    """
    刷新令牌处理器
    """
    
    async def post(self):
        """
        刷新访问令牌
        POST /api/auth/refresh
        """
        try:
            data = self.get_json_body()
            
            if 'refresh_token' not in data or not data['refresh_token']:
                raise ValidationError("Refresh token is required")
            
            # 调用应用服务刷新令牌
            auth_service = AuthService()
            result = await auth_service.refresh_token(data['refresh_token'])
            
            if not result.get('success'):
                raise AuthenticationError(result.get('error', 'Token refresh failed'))
            
            self.write_success(result.get('data'), "Token refreshed")
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            self.write_error(401, str(e))


class VerifyEmailHandler(BaseHandler):
    """
    邮箱验证处理器
    """
    
    async def get(self):
        """
        验证邮箱
        GET /api/auth/verify-email?token=<verification_token>
        """
        try:
            token = self.get_argument('token', None)
            if not token:
                raise ValidationError("Verification token is required")
            
            # 调用应用服务验证邮箱
            auth_service = AuthService()
            result = await auth_service.verify_email(token)
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Email verification failed'))
            
            self.write_success(result.get('data'), "Email verified successfully")
            
        except Exception as e:
            logger.error(f"Email verification error: {e}")
            self.write_error(400, str(e))


class ForgotPasswordHandler(BaseHandler):
    """
    忘记密码处理器
    """
    
    async def post(self):
        """
        请求密码重置
        POST /api/auth/forgot-password
        """
        try:
            data = self.get_json_body()
            
            if 'email' not in data or not data['email']:
                raise ValidationError("Email is required")
            
            # 调用应用服务发送重置邮件
            auth_service = AuthService()
            result = await auth_service.forgot_password(data['email'])
            
            self.write_success(result.get('data'), "Password reset email sent")
            
        except Exception as e:
            logger.error(f"Forgot password error: {e}")
            self.write_error(400, str(e))


class ResetPasswordHandler(BaseHandler):
    """
    重置密码处理器
    """
    
    async def post(self):
        """
        重置密码
        POST /api/auth/reset-password
        """
        try:
            data = self.get_json_body()
            
            required_fields = ['token', 'new_password']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValidationError(f"Field '{field}' is required")
            
            # 验证密码强度
            if len(data['new_password']) < 8:
                raise ValidationError("Password must be at least 8 characters")
            
            # 调用应用服务重置密码
            auth_service = AuthService()
            result = await auth_service.reset_password(
                token=data['token'],
                new_password=data['new_password']
            )
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Password reset failed'))
            
            self.write_success(result.get('data'), "Password reset successful")
            
        except Exception as e:
            logger.error(f"Reset password error: {e}")
            self.write_error(400, str(e))


class ProfileHandler(BaseHandler):
    """
    用户资料处理器
    """
    
    @auth_required
    async def get(self):
        """
        获取用户资料
        GET /api/auth/profile
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            if not user_id:
                raise AuthenticationError("Not authenticated")
            
            # 调用应用服务获取用户资料
            auth_service = AuthService()
            result = await auth_service.get_user_profile(user_id)
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to get profile'))
            
            self.write_success(result.get('data'), "Profile retrieved")
            
        except Exception as e:
            logger.error(f"Get profile error: {e}")
            self.write_error(400, str(e))
    
    @auth_required
    async def put(self):
        """
        更新用户资料
        PUT /api/auth/profile
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            if not user_id:
                raise AuthenticationError("Not authenticated")
            
            data = self.get_json_body()
            
            # 调用应用服务更新用户资料
            auth_service = AuthService()
            result = await auth_service.update_user_profile(user_id, data)
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to update profile'))
            
            self.write_success(result.get('data'), "Profile updated")
            
        except Exception as e:
            logger.error(f"Update profile error: {e}")
            self.write_error(400, str(e))
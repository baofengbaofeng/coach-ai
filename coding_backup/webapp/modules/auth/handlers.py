"""
认证处理器
处理用户认证相关的HTTP请求
"""

import logging
from typing import Dict, Any

from tornado.web import RequestHandler
from coding.tornado.core.base_handler import BaseHandler
from coding.tornado.core.exceptions import ValidationError, AuthenticationError
from coding.tornado.core.error_handler import handle_error

from .services import auth_service

logger = logging.getLogger(__name__)


class RegisterHandler(BaseHandler):
    """
    用户注册处理器
    """
    
    async def post(self):
        """
        注册新用户
        POST /api/auth/register
        
        Request Body:
        {
            "username": "string",      # 用户名
            "email": "string",         # 邮箱
            "password": "string",      # 密码
            "display_name": "string",  # 显示名称（可选）
            "phone": "string"          # 手机号（可选）
        }
        
        Response:
        {
            "success": true,
            "data": {
                "user": {
                    "id": "string",
                    "username": "string",
                    "email": "string",
                    "display_name": "string",
                    "status": "string"
                },
                "message": "Registration successful. Please verify your email."
            }
        }
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
            
            # 调用服务注册用户
            success, user, error = await auth_service.register_user(data)
            
            if not success:
                raise ValidationError(error)
            
            # 准备响应数据
            response_data = {
                'user': user.to_public_dict(),
                'message': 'Registration successful. Please check your email for verification.'
            }
            
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class LoginHandler(BaseHandler):
    """
    用户登录处理器
    """
    
    async def post(self):
        """
        用户登录
        POST /api/auth/login
        
        Request Body:
        {
            "identifier": "string",  # 用户名或邮箱
            "password": "string"     # 密码
        }
        
        Response:
        {
            "success": true,
            "data": {
                "token": "string",
                "user": {
                    "id": "string",
                    "username": "string",
                    "email": "string",
                    "display_name": "string"
                },
                "tenants": [
                    {
                        "id": "string",
                        "name": "string",
                        "code": "string",
                        "role": "string"
                    }
                ],
                "expires_in": 86400
            }
        }
        """
        try:
            # 验证请求数据
            data = self.get_json_body()
            required_fields = ['identifier', 'password']
            
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValidationError(f"Field '{field}' is required")
            
            # 获取客户端IP
            ip_address = self.request.remote_ip
            
            # 调用服务登录用户
            success, auth_data, error = await auth_service.login_user(
                data['identifier'], 
                data['password'], 
                ip_address
            )
            
            if not success:
                raise AuthenticationError(error)
            
            self.write_success(auth_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class LogoutHandler(BaseHandler):
    """
    用户登出处理器
    """
    
    async def post(self):
        """
        用户登出
        POST /api/auth/logout
        
        Headers:
        Authorization: Bearer <token>
        
        Response:
        {
            "success": true,
            "data": {
                "message": "Logged out successfully"
            }
        }
        """
        try:
            # 获取令牌
            token = self.get_bearer_token()
            if not token:
                raise AuthenticationError("No authentication token provided")
            
            # 调用服务登出用户
            success = await auth_service.logout_user(token)
            
            if not success:
                raise ValidationError("Logout failed")
            
            response_data = {'message': 'Logged out successfully'}
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class RefreshTokenHandler(BaseHandler):
    """
    令牌刷新处理器
    """
    
    async def post(self):
        """
        刷新JWT令牌
        POST /api/auth/refresh
        
        Headers:
        Authorization: Bearer <old_token>
        
        Response:
        {
            "success": true,
            "data": {
                "token": "string",
                "expires_in": 86400
            }
        }
        """
        try:
            # 获取旧令牌
            token = self.get_bearer_token()
            if not token:
                raise AuthenticationError("No authentication token provided")
            
            # 调用服务刷新令牌
            success, new_token, error = await auth_service.refresh_token(token)
            
            if not success:
                raise AuthenticationError(error)
            
            response_data = {
                'token': new_token,
                'expires_in': auth_service.jwt_expire_hours * 3600
            }
            
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class VerifyTokenHandler(BaseHandler):
    """
    令牌验证处理器
    """
    
    async def post(self):
        """
        验证JWT令牌
        POST /api/auth/verify
        
        Headers:
        Authorization: Bearer <token>
        
        Response:
        {
            "success": true,
            "data": {
                "valid": true,
                "user": {
                    "id": "string",
                    "username": "string",
                    "email": "string"
                }
            }
        }
        """
        try:
            # 获取令牌
            token = self.get_bearer_token()
            if not token:
                raise AuthenticationError("No authentication token provided")
            
            # 调用服务验证令牌
            valid, payload, error = await auth_service.verify_token(token)
            
            if not valid:
                raise AuthenticationError(error)
            
            # 获取用户信息
            session = get_db_session()
            user = session.query(User).filter_by(id=payload['user_id']).first()
            
            response_data = {
                'valid': True,
                'user': user.to_public_dict() if user else None
            }
            
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class RequestPasswordResetHandler(BaseHandler):
    """
    请求密码重置处理器
    """
    
    async def post(self):
        """
        请求密码重置
        POST /api/auth/password/reset/request
        
        Request Body:
        {
            "email": "string"  # 用户邮箱
        }
        
        Response:
        {
            "success": true,
            "data": {
                "message": "If the email exists, a reset link will be sent"
            }
        }
        """
        try:
            # 验证请求数据
            data = self.get_json_body()
            if 'email' not in data or not data['email']:
                raise ValidationError("Email is required")
            
            # 验证邮箱格式
            if '@' not in data['email']:
                raise ValidationError("Invalid email format")
            
            # 调用服务请求密码重置
            success, reset_token, error = await auth_service.request_password_reset(data['email'])
            
            if not success:
                raise ValidationError(error)
            
            # 注意：出于安全考虑，我们不会在响应中返回重置令牌
            # 实际应用中应该发送邮件
            response_data = {
                'message': 'If the email exists, a reset link will be sent'
            }
            
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class ResetPasswordHandler(BaseHandler):
    """
    重置密码处理器
    """
    
    async def post(self):
        """
        重置密码
        POST /api/auth/password/reset
        
        Request Body:
        {
            "token": "string",      # 密码重置令牌
            "password": "string"    # 新密码
        }
        
        Response:
        {
            "success": true,
            "data": {
                "message": "Password reset successfully"
            }
        }
        """
        try:
            # 验证请求数据
            data = self.get_json_body()
            required_fields = ['token', 'password']
            
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValidationError(f"Field '{field}' is required")
            
            # 验证密码强度
            if len(data['password']) < 8:
                raise ValidationError("Password must be at least 8 characters")
            
            # 调用服务重置密码
            success, error = await auth_service.reset_password(data['token'], data['password'])
            
            if not success:
                raise ValidationError(error)
            
            response_data = {'message': 'Password reset successfully'}
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class VerifyEmailHandler(BaseHandler):
    """
    验证邮箱处理器
    """
    
    async def get(self):
        """
        验证邮箱
        GET /api/auth/email/verify?token=<verification_token>
        
        Response:
        {
            "success": true,
            "data": {
                "message": "Email verified successfully"
            }
        }
        """
        try:
            # 获取验证令牌
            token = self.get_argument('token', '')
            if not token:
                raise ValidationError("Verification token is required")
            
            # 调用服务验证邮箱
            success, error = await auth_service.verify_email(token)
            
            if not success:
                raise ValidationError(error)
            
            response_data = {'message': 'Email verified successfully'}
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class ProfileHandler(BaseHandler):
    """
    用户资料处理器
    """
    
    async def get(self):
        """
        获取用户资料
        GET /api/auth/profile
        
        Headers:
        Authorization: Bearer <token>
        
        Response:
        {
            "success": true,
            "data": {
                "user": {
                    "id": "string",
                    "username": "string",
                    "email": "string",
                    "display_name": "string",
                    "avatar_url": "string",
                    "phone": "string",
                    "email_verified": true,
                    "phone_verified": false,
                    "status": "string",
                    "created_at": "string"
                },
                "tenants": [
                    {
                        "id": "string",
                        "name": "string",
                        "code": "string",
                        "role": "string",
                        "joined_at": "string"
                    }
                ]
            }
        }
        """
        try:
            # 验证用户身份
            user_id = self.get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            # 调用服务获取用户资料
            success, profile, error = await auth_service.get_user_profile(user_id)
            
            if not success:
                raise ValidationError(error)
            
            self.write_success(profile)
            
        except Exception as e:
            handle_error(self, e, logger)
    
    async def put(self):
        """
        更新用户资料
        PUT /api/auth/profile
        
        Headers:
        Authorization: Bearer <token>
        
        Request Body:
        {
            "display_name": "string",  # 显示名称（可选）
            "avatar_url": "string",    # 头像URL（可选）
            "phone": "string"          # 手机号（可选）
        }
        
        Response:
        {
            "success": true,
            "data": {
                "user": {
                    // 更新后的用户资料
                },
                "message": "Profile updated successfully"
            }
        }
        """
        try:
            # 验证用户身份
            user_id = self.get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            # 获取更新数据
            data = self.get_json_body()
            if not data:
                raise ValidationError("No data provided for update")
            
            # 调用服务更新用户资料
            success, updated_profile, error = await auth_service.update_user_profile(user_id, data)
            
            if not success:
                raise ValidationError(error)
            
            response_data = {
                'user': updated_profile,
                'message': 'Profile updated successfully'
            }
            
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)


# 导入需要的模块
from database.connection import get_db_session
from database.models.user import User
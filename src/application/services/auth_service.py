"""
认证应用服务
处理用户认证相关的业务逻辑
"""

import asyncio
from typing import Dict, Any, Optional
from loguru import logger

from src.domain.user.services import UserService
from src.domain.user.entities import User
from src.infrastructure.security.jwt_utils import JWTUtils
from src.infrastructure.security.password_utils import PasswordUtils


class AuthService:
    """认证应用服务"""
    
    def __init__(self):
        self.user_service = UserService()
        self.password_utils = PasswordUtils()
    
    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """注册新用户"""
        try:
            # 验证用户数据
            validation_result = self._validate_registration_data(user_data)
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'error': '; '.join(validation_result['errors'])
                }
            
            # 检查用户名和邮箱是否已存在
            username_exists = await self.user_service.check_username_exists(user_data['username'])
            if username_exists:
                return {
                    'success': False,
                    'error': 'Username already exists'
                }
            
            email_exists = await self.user_service.check_email_exists(user_data['email'])
            if email_exists:
                return {
                    'success': False,
                    'error': 'Email already exists'
                }
            
            # 哈希密码
            hashed_password = self.password_utils.hash_password(user_data['password'])
            
            # 创建用户实体
            user = self.user_service.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=hashed_password,
                display_name=user_data.get('display_name'),
                phone=user_data.get('phone')
            )
            
            # 保存用户（这里需要实现持久化）
            # user_repository.save(user)
            
            # 创建验证令牌
            verification_token = self.password_utils.generate_password_reset_token()
            
            # 发送验证邮件（异步）
            asyncio.create_task(self._send_verification_email(user.email, verification_token))
            
            return {
                'success': True,
                'data': {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'display_name': user.display_name,
                        'status': str(user.status)
                    },
                    'message': 'Registration successful. Please verify your email.'
                }
            }
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def login_user(self, identifier: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        try:
            # 根据用户名或邮箱查找用户
            user = await self.user_service.find_user_by_identifier(identifier)
            if not user:
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            # 验证密码
            if not self.password_utils.verify_password(password, user.password_hash):
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            # 检查用户状态
            if not user.status.is_active():
                return {
                    'success': False,
                    'error': 'Account is not active'
                }
            
            # 检查邮箱是否已验证
            if not user.verification_status.is_verified():
                return {
                    'success': False,
                    'error': 'Email not verified'
                }
            
            # 创建JWT令牌
            user_data = {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'tenant_id': user.tenant_id
            }
            
            tokens = JWTUtils.create_tokens_pair(user_data)
            
            # 更新最后登录时间
            user.update_last_login()
            # user_repository.save(user)
            
            return {
                'success': True,
                'data': {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'display_name': user.display_name
                    },
                    'tokens': tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def logout_user(self, token_payload: Dict[str, Any]) -> Dict[str, Any]:
        """用户登出"""
        try:
            # 这里可以添加令牌到黑名单的逻辑
            # 需要Redis客户端支持
            
            return {
                'success': True,
                'data': {
                    'message': 'Logged out successfully'
                }
            }
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """刷新访问令牌"""
        try:
            # 验证刷新令牌
            new_access_token = JWTUtils.refresh_access_token(refresh_token)
            if not new_access_token:
                return {
                    'success': False,
                    'error': 'Invalid refresh token'
                }
            
            return {
                'success': True,
                'data': {
                    'access_token': new_access_token,
                    'token_type': 'bearer'
                }
            }
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def verify_email(self, verification_token: str) -> Dict[str, Any]:
        """验证邮箱"""
        try:
            # 这里需要实现令牌验证逻辑
            # 暂时返回成功
            return {
                'success': True,
                'data': {
                    'message': 'Email verified successfully'
                }
            }
            
        except Exception as e:
            logger.error(f"Email verification error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def forgot_password(self, email: str) -> Dict[str, Any]:
        """忘记密码"""
        try:
            # 查找用户
            user = await self.user_service.find_user_by_email(email)
            if not user:
                # 出于安全考虑，即使用户不存在也返回成功
                return {
                    'success': True,
                    'data': {
                        'message': 'If the email exists, a reset link has been sent'
                    }
                }
            
            # 生成重置令牌
            reset_token = self.password_utils.generate_password_reset_token()
            
            # 保存重置令牌（需要持久化）
            # reset_token_repository.save(user.id, reset_token)
            
            # 发送重置邮件（异步）
            asyncio.create_task(self._send_password_reset_email(email, reset_token))
            
            return {
                'success': True,
                'data': {
                    'message': 'Password reset email sent'
                }
            }
            
        except Exception as e:
            logger.error(f"Forgot password error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def reset_password(self, token: str, new_password: str) -> Dict[str, Any]:
        """重置密码"""
        try:
            # 验证密码强度
            validation_result = self.password_utils.validate_password_strength(new_password)
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'error': '; '.join(validation_result['errors'])
                }
            
            # 验证重置令牌（需要持久化支持）
            # user_id = reset_token_repository.validate_token(token)
            # if not user_id:
            #     return {
            #         'success': False,
            #         'error': 'Invalid or expired reset token'
            #     }
            
            # 查找用户
            # user = user_repository.find_by_id(user_id)
            # if not user:
            #     return {
            #         'success': False,
            #         'error': 'User not found'
            #     }
            
            # 哈希新密码
            hashed_password = self.password_utils.hash_password(new_password)
            
            # 更新用户密码
            # user.update_password(hashed_password)
            # user_repository.save(user)
            
            # 删除重置令牌
            # reset_token_repository.delete_token(token)
            
            return {
                'success': True,
                'data': {
                    'message': 'Password reset successful'
                }
            }
            
        except Exception as e:
            logger.error(f"Reset password error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """获取用户资料"""
        try:
            # 查找用户
            # user = user_repository.find_by_id(user_id)
            # if not user:
            #     return {
            #         'success': False,
            #         'error': 'User not found'
            #     }
            
            # 暂时返回模拟数据
            return {
                'success': True,
                'data': {
                    'user': {
                        'id': user_id,
                        'username': 'testuser',
                        'email': 'test@example.com',
                        'display_name': 'Test User'
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Get profile error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def update_user_profile(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新用户资料"""
        try:
            # 查找用户
            # user = user_repository.find_by_id(user_id)
            # if not user:
            #     return {
            #         'success': False,
            #         'error': 'User not found'
            #     }
            
            # 更新用户信息
            # if 'display_name' in update_data:
            #     user.update_display_name(update_data['display_name'])
            # if 'phone' in update_data:
            #     user.update_phone(update_data['phone'])
            
            # user_repository.save(user)
            
            return {
                'success': True,
                'data': {
                    'message': 'Profile updated successfully'
                }
            }
            
        except Exception as e:
            logger.error(f"Update profile error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_registration_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证注册数据"""
        result = {
            'is_valid': True,
            'errors': []
        }
        
        # 检查必填字段
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                result['is_valid'] = False
                result['errors'].append(f"{field} is required")
        
        # 验证邮箱格式
        if 'email' in data and data['email']:
            if '@' not in data['email']:
                result['is_valid'] = False
                result['errors'].append("Invalid email format")
        
        # 验证密码强度
        if 'password' in data and data['password']:
            validation = self.password_utils.validate_password_strength(data['password'])
            if not validation['is_valid']:
                result['is_valid'] = False
                result['errors'].extend(validation['errors'])
        
        # 验证用户名格式
        if 'username' in data and data['username']:
            if len(data['username']) < 3:
                result['is_valid'] = False
                result['errors'].append("Username must be at least 3 characters")
            if not data['username'].replace('_', '').isalnum():
                result['is_valid'] = False
                result['errors'].append("Username can only contain letters, numbers and underscores")
        
        return result
    
    async def _send_verification_email(self, email: str, token: str):
        """发送验证邮件（异步）"""
        try:
            # 这里实现邮件发送逻辑
            logger.info(f"Verification email would be sent to {email} with token {token}")
            await asyncio.sleep(0.1)  # 模拟异步操作
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
    
    async def _send_password_reset_email(self, email: str, token: str):
        """发送密码重置邮件（异步）"""
        try:
            # 这里实现邮件发送逻辑
            logger.info(f"Password reset email would be sent to {email} with token {token}")
            await asyncio.sleep(0.1)  # 模拟异步操作
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
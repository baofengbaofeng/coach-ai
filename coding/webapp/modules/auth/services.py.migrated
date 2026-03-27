"""
认证服务
处理用户认证相关的业务逻辑
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

from coding.tornado.utils.jwt_utils import create_jwt_token, verify_jwt_token
from coding.tornado.utils.password_utils import hash_password, verify_password
from database.connection import get_db_session
from database.models.user import User
from database.models.tenant import Tenant, TenantMember

logger = logging.getLogger(__name__)


class AuthService:
    """
    认证服务类
    处理用户注册、登录、令牌管理等业务逻辑
    """
    
    def __init__(self):
        self.jwt_secret = "your-secret-key-change-in-production"  # TODO: 从配置读取
        self.jwt_expire_hours = 24
        self.password_reset_expire_hours = 1
    
    async def register_user(self, user_data: Dict[str, Any]) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        注册新用户
        
        Args:
            user_data: 用户数据，包含username, email, password等
            
        Returns:
            (success, user, error_message)
        """
        try:
            session = get_db_session()
            
            # 检查用户名是否已存在
            existing_user = session.query(User).filter(
                (User.username == user_data['username']) | 
                (User.email == user_data['email'])
            ).first()
            
            if existing_user:
                if existing_user.username == user_data['username']:
                    return False, None, "Username already exists"
                else:
                    return False, None, "Email already exists"
            
            # 创建用户
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=hash_password(user_data['password']),
                display_name=user_data.get('display_name', user_data['username']),
                phone=user_data.get('phone'),
                status='pending',  # 需要邮箱验证
                email_verified=False,
                phone_verified=False
            )
            
            session.add(user)
            session.commit()
            
            # 生成邮箱验证令牌
            verify_token = create_jwt_token(
                payload={'user_id': user.id, 'type': 'email_verify'},
                secret=self.jwt_secret,
                expires_hours=24
            )
            
            user.email_verify_token = verify_token
            user.email_verify_expires = datetime.utcnow() + timedelta(hours=24)
            session.commit()
            
            logger.info(f"User registered: {user.username} ({user.email})")
            return True, user, None
            
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return False, None, "Registration failed"
    
    async def login_user(self, identifier: str, password: str, ip_address: str = None) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        用户登录
        
        Args:
            identifier: 用户名或邮箱
            password: 密码
            ip_address: 客户端IP地址
            
        Returns:
            (success, auth_data, error_message)
        """
        try:
            session = get_db_session()
            
            # 查找用户（支持用户名或邮箱登录）
            user = session.query(User).filter(
                (User.username == identifier) | (User.email == identifier)
            ).first()
            
            if not user:
                logger.warning(f"Login attempt with unknown identifier: {identifier}")
                return False, None, "Invalid credentials"
            
            # 检查账户状态
            if user.is_deleted:
                return False, None, "Account deleted"
            
            if user.status == 'blocked':
                return False, None, "Account blocked"
            
            if user.locked_until and user.locked_until > datetime.utcnow():
                return False, None, f"Account locked until {user.locked_until}"
            
            # 验证密码
            if not verify_password(password, user.password_hash):
                user.increment_failed_attempts()
                session.commit()
                logger.warning(f"Failed login attempt for user: {user.username}")
                return False, None, "Invalid credentials"
            
            # 重置失败尝试次数
            user.reset_failed_attempts()
            user.update_last_login(ip_address)
            user.status = 'active'  # 激活用户
            session.commit()
            
            # 生成JWT令牌
            token = create_jwt_token(
                payload={
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                secret=self.jwt_secret,
                expires_hours=self.jwt_expire_hours
            )
            
            # 获取用户的基本租户信息
            tenants = []
            for tenant_member in session.query(TenantMember).filter_by(user_id=user.id, status='active').all():
                tenant = session.query(Tenant).filter_by(id=tenant_member.tenant_id).first()
                if tenant and tenant.is_active():
                    tenants.append({
                        'id': tenant.id,
                        'name': tenant.name,
                        'code': tenant.code,
                        'role': tenant_member.role
                    })
            
            auth_data = {
                'token': token,
                'user': user.to_public_dict(),
                'tenants': tenants,
                'expires_in': self.jwt_expire_hours * 3600
            }
            
            logger.info(f"User logged in: {user.username}")
            return True, auth_data, None
            
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return False, None, "Login failed"
    
    async def verify_token(self, token: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        验证JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            (valid, payload, error_message)
        """
        try:
            payload = verify_jwt_token(token, self.jwt_secret)
            if not payload:
                return False, None, "Invalid token"
            
            # 检查用户是否存在且活跃
            session = get_db_session()
            user = session.query(User).filter_by(id=payload.get('user_id')).first()
            
            if not user or not user.is_active() or user.is_blocked():
                return False, None, "User not found or inactive"
            
            return True, payload, None
            
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return False, None, "Token verification failed"
    
    async def logout_user(self, token: str) -> bool:
        """
        用户登出
        注意：JWT是无状态的，这里主要处理令牌黑名单（如果需要）
        
        Args:
            token: 要失效的令牌
            
        Returns:
            是否成功
        """
        # TODO: 实现令牌黑名单（如果需要立即失效令牌）
        # 当前实现中，JWT令牌在过期前一直有效
        logger.info(f"User logged out, token will expire naturally")
        return True
    
    async def refresh_token(self, token: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        刷新JWT令牌
        
        Args:
            token: 旧令牌
            
        Returns:
            (success, new_token, error_message)
        """
        try:
            # 验证旧令牌
            valid, payload, error = await self.verify_token(token)
            if not valid:
                return False, None, error
            
            # 生成新令牌
            new_token = create_jwt_token(
                payload={
                    'user_id': payload['user_id'],
                    'username': payload['username'],
                    'email': payload['email']
                },
                secret=self.jwt_secret,
                expires_hours=self.jwt_expire_hours
            )
            
            logger.info(f"Token refreshed for user: {payload['username']}")
            return True, new_token, None
            
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return False, None, "Token refresh failed"
    
    async def request_password_reset(self, email: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        请求密码重置
        
        Args:
            email: 用户邮箱
            
        Returns:
            (success, reset_token, error_message)
        """
        try:
            session = get_db_session()
            user = session.query(User).filter_by(email=email).first()
            
            if not user or not user.is_active():
                # 出于安全考虑，不透露用户是否存在
                return True, None, "If the email exists, a reset link will be sent"
            
            # 生成密码重置令牌
            reset_token = create_jwt_token(
                payload={'user_id': user.id, 'type': 'password_reset'},
                secret=self.jwt_secret,
                expires_hours=self.password_reset_expire_hours
            )
            
            user.password_reset_token = reset_token
            user.password_reset_expires = datetime.utcnow() + timedelta(hours=self.password_reset_expire_hours)
            session.commit()
            
            logger.info(f"Password reset requested for user: {user.username}")
            return True, reset_token, None
            
        except Exception as e:
            logger.error(f"Error requesting password reset: {str(e)}")
            return False, None, "Password reset request failed"
    
    async def reset_password(self, reset_token: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        重置密码
        
        Args:
            reset_token: 密码重置令牌
            new_password: 新密码
            
        Returns:
            (success, error_message)
        """
        try:
            session = get_db_session()
            
            # 查找有有效重置令牌的用户
            user = session.query(User).filter(
                User.password_reset_token == reset_token,
                User.password_reset_expires > datetime.utcnow()
            ).first()
            
            if not user:
                return False, "Invalid or expired reset token"
            
            # 更新密码
            user.password_hash = hash_password(new_password)
            user.password_reset_token = None
            user.password_reset_expires = None
            user.reset_failed_attempts()  # 重置失败尝试
            session.commit()
            
            logger.info(f"Password reset for user: {user.username}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error resetting password: {str(e)}")
            return False, "Password reset failed"
    
    async def verify_email(self, verify_token: str) -> Tuple[bool, Optional[str]]:
        """
        验证邮箱
        
        Args:
            verify_token: 邮箱验证令牌
            
        Returns:
            (success, error_message)
        """
        try:
            session = get_db_session()
            
            # 查找有有效验证令牌的用户
            user = session.query(User).filter(
                User.email_verify_token == verify_token,
                User.email_verify_expires > datetime.utcnow()
            ).first()
            
            if not user:
                return False, "Invalid or expired verification token"
            
            # 验证邮箱
            user.email_verified = True
            user.email_verify_token = None
            user.email_verify_expires = None
            
            # 如果用户状态是pending，激活用户
            if user.status == 'pending':
                user.status = 'active'
            
            session.commit()
            
            logger.info(f"Email verified for user: {user.username}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error verifying email: {str(e)}")
            return False, "Email verification failed"
    
    async def get_user_profile(self, user_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        获取用户资料
        
        Args:
            user_id: 用户ID
            
        Returns:
            (success, user_profile, error_message)
        """
        try:
            session = get_db_session()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user or not user.is_active():
                return False, None, "User not found"
            
            # 获取用户的租户信息
            tenants = []
            for tenant_member in session.query(TenantMember).filter_by(user_id=user.id, status='active').all():
                tenant = session.query(Tenant).filter_by(id=tenant_member.tenant_id).first()
                if tenant and tenant.is_active():
                    tenants.append({
                        'id': tenant.id,
                        'name': tenant.name,
                        'code': tenant.code,
                        'role': tenant_member.role,
                        'joined_at': tenant_member.joined_at.isoformat() if tenant_member.joined_at else None
                    })
            
            profile = user.to_public_dict()
            profile['tenants'] = tenants
            
            return True, profile, None
            
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return False, None, "Failed to get user profile"
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        更新用户资料
        
        Args:
            user_id: 用户ID
            profile_data: 要更新的资料
            
        Returns:
            (success, updated_profile, error_message)
        """
        try:
            session = get_db_session()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user or not user.is_active():
                return False, None, "User not found"
            
            # 允许更新的字段
            allowed_fields = ['display_name', 'avatar_url', 'phone']
            
            for field in allowed_fields:
                if field in profile_data:
                    setattr(user, field, profile_data[field])
            
            # 如果更新了手机号，需要重新验证
            if 'phone' in profile_data and profile_data['phone'] != user.phone:
                user.phone_verified = False
            
            session.commit()
            
            # 返回更新后的资料
            return await self.get_user_profile(user_id)
            
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return False, None, "Failed to update user profile"


# 全局认证服务实例
auth_service = AuthService()
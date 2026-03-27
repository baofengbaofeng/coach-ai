"""
简化的用户领域实体
避免dataclass继承问题
"""

from datetime import datetime, timedelta
from typing import Optional, Set
import re

from ..base_simple import AggregateRoot
from .value_objects_simple import Email, Password, PhoneNumber, UserStatus, VerificationStatus


class User(AggregateRoot):
    """用户实体（聚合根）"""
    
    def __init__(
        self,
        username: str,
        email: Email,
        password: Password,
        phone: Optional[PhoneNumber] = None,
        display_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        status: Optional[UserStatus] = None,
        verification: Optional[VerificationStatus] = None,
        last_login_at: Optional[datetime] = None,
        last_login_ip: Optional[str] = None,
        failed_login_attempts: int = 0,
        locked_until: Optional[datetime] = None,
        mfa_enabled: bool = False,
        mfa_secret: Optional[str] = None,
        tenant_ids: Optional[Set[str]] = None,
        owned_tenant_ids: Optional[Set[str]] = None,
        **kwargs  # 用于父类的参数
    ):
        # 调用父类初始化
        super().__init__(**kwargs)
        
        # 基本身份信息
        self.username = username
        self.email = email
        self.password = password
        
        # 可选信息
        self.phone = phone
        self.display_name = display_name or username
        self.avatar_url = avatar_url
        
        # 状态信息
        self.status = status or UserStatus("pending")
        self.verification = verification or VerificationStatus()
        
        # 安全信息
        self.last_login_at = last_login_at
        self.last_login_ip = last_login_ip
        self.failed_login_attempts = failed_login_attempts
        self.locked_until = locked_until
        
        # MFA信息
        self.mfa_enabled = mfa_enabled
        self.mfa_secret = mfa_secret
        
        # 关系
        self.tenant_ids = tenant_ids or set()
        self.owned_tenant_ids = owned_tenant_ids or set()
        
        # 验证
        self._validate()
    
    def _validate(self):
        """验证用户数据"""
        if not self.username or len(self.username) < 3:
            raise ValueError("用户名长度必须至少3个字符")
        if not re.match(r'^[a-zA-Z0-9_]+$', self.username):
            raise ValueError("用户名只能包含字母、数字和下划线")
    
    def activate(self) -> None:
        """激活用户"""
        if self.status.is_blocked():
            raise ValueError("被锁定的用户无法激活")
        
        self.status = UserStatus("active")
        self.mark_updated()
    
    def deactivate(self) -> None:
        """停用用户"""
        self.status = UserStatus("inactive")
        self.mark_updated()
    
    def block(self, reason: Optional[str] = None) -> None:
        """锁定用户"""
        self.status = UserStatus("blocked")
        self.mark_updated()
    
    def verify_email(self) -> None:
        """验证邮箱"""
        self.verification = self.verification.verify_email()
        self.mark_updated()
    
    def verify_phone(self) -> None:
        """验证手机"""
        self.verification = self.verification.verify_phone()
        self.mark_updated()
    
    def update_password(self, new_password: str, old_password: Optional[str] = None) -> bool:
        """
        更新密码
        
        Args:
            new_password: 新密码
            old_password: 旧密码（用于验证）
            
        Returns:
            是否成功
        """
        if old_password and not self.password.verify(old_password):
            return False
        
        self.password = Password.create(new_password)
        self.mark_updated()
        return True
    
    def attempt_login(self, password: str, ip_address: Optional[str] = None) -> bool:
        """
        尝试登录
        
        Args:
            password: 密码
            ip_address: IP地址
            
        Returns:
            是否登录成功
        """
        if not self.status.can_login():
            return False
        
        if self.locked_until and self.locked_until > datetime.now():
            return False
        
        if self.password.verify(password):
            # 登录成功
            self.last_login_at = datetime.now()
            self.last_login_ip = ip_address
            self.failed_login_attempts = 0
            self.locked_until = None
            self.mark_updated()
            return True
        else:
            # 登录失败
            self.failed_login_attempts += 1
            
            if self.failed_login_attempts >= 5:
                self.locked_until = datetime.now() + timedelta(minutes=30)
                self.status = UserStatus("blocked")
            
            self.mark_updated()
            return False
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': str(self.email),
            'phone': str(self.phone) if self.phone else None,
            'display_name': self.display_name,
            'avatar_url': self.avatar_url,
            'status': str(self.status),
            'verification': str(self.verification),
            'mfa_enabled': self.mfa_enabled,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def create(
        cls,
        username: str,
        email: str,
        password: str,
        phone: Optional[str] = None,
        display_name: Optional[str] = None
    ) -> 'User':
        """
        创建新用户
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            phone: 手机号
            display_name: 显示名称
            
        Returns:
            用户实体
        """
        # 创建值对象
        email_obj = Email(email)
        password_obj = Password.create(password)
        phone_obj = PhoneNumber(phone) if phone else None
        
        # 创建用户
        user = cls(
            username=username,
            email=email_obj,
            password=password_obj,
            phone=phone_obj,
            display_name=display_name
        )
        
        return user
    
    def __repr__(self) -> str:
        return f"<User(id='{self.id}', username='{self.username}', email='{self.email}')>"


class Tenant(AggregateRoot):
    """租户实体（聚合根）"""
    
    def __init__(
        self,
        name: str,
        owner_id: str,
        description: Optional[str] = None,
        type: str = "family",
        status: str = "active",
        settings: Optional[dict] = None,
        member_ids: Optional[Set[str]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.name = name
        self.owner_id = owner_id
        self.description = description
        self.type = type
        self.status = status
        self.settings = settings or {}
        self.member_ids = member_ids or set()
        
        # 自动添加拥有者为成员
        self.member_ids.add(self.owner_id)
        
        self._validate()
    
    def _validate(self):
        """验证租户数据"""
        if not self.name or len(self.name) < 2:
            raise ValueError("租户名称长度必须至少2个字符")
    
    def add_member(self, user_id: str) -> bool:
        """添加成员"""
        if user_id in self.member_ids:
            return False
        
        self.member_ids.add(user_id)
        self.mark_updated()
        return True
    
    def remove_member(self, user_id: str) -> bool:
        """移除成员"""
        if user_id == self.owner_id:
            raise ValueError("不能移除租户拥有者")
        
        if user_id not in self.member_ids:
            return False
        
        self.member_ids.remove(user_id)
        self.mark_updated()
        return True
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'type': self.type,
            'status': self.status,
            'member_count': len(self.member_ids),
            'settings': self.settings,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<Tenant(id='{self.id}', name='{self.name}', owner='{self.owner_id}')>"


class Permission(AggregateRoot):
    """权限实体"""
    
    def __init__(
        self,
        name: str,
        resource: str,
        action: str,
        description: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.name = name
        self.resource = resource
        self.action = action
        self.description = description
        
        self._validate()
    
    def _validate(self):
        """验证权限数据"""
        if not self.name:
            raise ValueError("权限名称不能为空")
        if not self.resource:
            raise ValueError("资源类型不能为空")
        if not self.action:
            raise ValueError("操作类型不能为空")
    
    def get_permission_string(self) -> str:
        """获取权限字符串（resource:action格式）"""
        return f"{self.resource}:{self.action}"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'resource': self.resource,
            'action': self.action,
            'permission_string': self.get_permission_string(),
            'created_at': self.created_at.isoformat(),
        }
    
    def __repr__(self) -> str:
        return f"<Permission(id='{self.id}', name='{self.name}', resource='{self.resource}:{self.action}')>"
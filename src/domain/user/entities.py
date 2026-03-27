"""
用户领域实体
包含User、Tenant、Permission等核心实体
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Set
import re

from ..base import AggregateRoot
from .value_objects import Email, Password, PhoneNumber, UserStatus, VerificationStatus


@dataclass
class User(AggregateRoot):
    """用户实体（聚合根）"""
    
    # 基本身份信息（必须参数）
    username: str
    email: Email
    password: Password
    
    # 可选信息
    phone: Optional[PhoneNumber] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # 状态信息
    status: UserStatus = field(default_factory=lambda: UserStatus("pending"))
    verification: VerificationStatus = field(default_factory=VerificationStatus)
    
    # 安全信息
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    # MFA信息
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    
    # 关系
    tenant_ids: Set[str] = field(default_factory=set)  # 用户所属的租户ID
    owned_tenant_ids: Set[str] = field(default_factory=set)  # 用户拥有的租户ID
    
    def __post_init__(self):
        """初始化后验证"""
        super().__post_init__()
        
        # 验证用户名
        if not self.username or len(self.username) < 3:
            raise ValueError("用户名长度必须至少3个字符")
        if not re.match(r'^[a-zA-Z0-9_]+$', self.username):
            raise ValueError("用户名只能包含字母、数字和下划线")
        
        # 设置默认显示名称
        if not self.display_name:
            self.display_name = self.username
    
    def activate(self) -> None:
        """激活用户"""
        if self.status.is_blocked():
            raise ValueError("被锁定的用户无法激活")
        
        self.status = UserStatus("active")
        self.mark_updated()
        
        # 可以在这里添加领域事件
        # self.add_domain_event(UserActivatedEvent(user_id=self.id))
    
    def deactivate(self) -> None:
        """停用用户"""
        self.status = UserStatus("inactive")
        self.mark_updated()
    
    def block(self, reason: Optional[str] = None) -> None:
        """锁定用户"""
        self.status = UserStatus("blocked")
        self.mark_updated()
        
        # 可以在这里添加领域事件
        # self.add_domain_event(UserBlockedEvent(user_id=self.id, reason=reason))
    
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
        # 如果提供了旧密码，需要验证
        if old_password and not self.password.verify(old_password):
            return False
        
        self.password = Password.create(new_password)
        self.mark_updated()
        return True
    
    def reset_password(self, reset_token: str, new_password: str) -> bool:
        """
        重置密码（使用重置令牌）
        
        Args:
            reset_token: 重置令牌
            new_password: 新密码
            
        Returns:
            是否成功
        """
        # 这里应该验证重置令牌的有效性
        # 简化实现：假设令牌验证通过
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
        # 检查用户状态
        if not self.status.can_login():
            return False
        
        # 检查账户是否被锁定
        if self.locked_until and self.locked_until > datetime.now():
            return False
        
        # 验证密码
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
            
            # 如果失败次数过多，锁定账户
            if self.failed_login_attempts >= 5:
                self.locked_until = datetime.now() + timedelta(minutes=30)
                self.status = UserStatus("blocked")
            
            self.mark_updated()
            return False
    
    def enable_mfa(self, secret: str) -> None:
        """启用多因素认证"""
        self.mfa_enabled = True
        self.mfa_secret = secret
        self.mark_updated()
    
    def disable_mfa(self) -> None:
        """禁用多因素认证"""
        self.mfa_enabled = False
        self.mfa_secret = None
        self.mark_updated()
    
    def add_to_tenant(self, tenant_id: str) -> None:
        """添加到租户"""
        self.tenant_ids.add(tenant_id)
        self.mark_updated()
    
    def remove_from_tenant(self, tenant_id: str) -> None:
        """从租户移除"""
        self.tenant_ids.discard(tenant_id)
        self.mark_updated()
    
    def owns_tenant(self, tenant_id: str) -> bool:
        """是否拥有租户"""
        return tenant_id in self.owned_tenant_ids
    
    def is_in_tenant(self, tenant_id: str) -> bool:
        """是否在租户中"""
        return tenant_id in self.tenant_ids
    
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
        
        # 添加领域事件
        from .events import UserRegisteredEvent
        user.add_domain_event(UserRegisteredEvent(
            aggregate_id=user.id,
            user_id=user.id,
            username=username,
            email=str(email)
        ))
        
        return user


@dataclass
class Tenant(AggregateRoot):
    """租户实体（聚合根）"""
    
    name: str
    description: Optional[str] = None
    owner_id: str  # 拥有者用户ID
    
    # 租户类型：family, team, organization, etc.
    type: str = "family"
    
    # 租户状态：active, inactive, suspended
    status: str = "active"
    
    # 配置
    settings: dict = field(default_factory=dict)
    
    # 关系
    member_ids: Set[str] = field(default_factory=set)  # 成员用户ID
    
    def __post_init__(self):
        """初始化后验证"""
        super().__post_init__()
        
        if not self.name or len(self.name) < 2:
            raise ValueError("租户名称长度必须至少2个字符")
        
        # 自动添加拥有者为成员
        self.member_ids.add(self.owner_id)
    
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
    
    def update_settings(self, settings: dict) -> None:
        """更新设置"""
        self.settings.update(settings)
        self.mark_updated()
    
    def is_member(self, user_id: str) -> bool:
        """是否为成员"""
        return user_id in self.member_ids
    
    def is_owner(self, user_id: str) -> bool:
        """是否为拥有者"""
        return user_id == self.owner_id
    
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


@dataclass
class Permission(Entity):
    """权限实体"""
    
    name: str
    description: Optional[str] = None
    resource: str  # 资源类型
    action: str    # 操作类型
    
    def __post_init__(self):
        """初始化后验证"""
        super().__post_init__()
        
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
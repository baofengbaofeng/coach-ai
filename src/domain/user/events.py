"""
用户领域事件
定义用户相关的领域事件
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..base import DomainEvent


@dataclass
class UserRegisteredEvent(DomainEvent):
    """用户注册事件"""
    
    user_id: str
    username: str
    email: str
    registration_source: str = "web"
    metadata: dict = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class UserActivatedEvent(DomainEvent):
    """用户激活事件"""
    
    user_id: str
    activated_by: Optional[str] = None  # 谁激活的（用户ID或系统）
    activation_method: str = "email"  # email, admin, auto


@dataclass
class UserUpdatedEvent(DomainEvent):
    """用户更新事件"""
    
    user_id: str
    updated_fields: dict  # 更新的字段和旧值
    updated_by: Optional[str] = None


@dataclass
class UserPasswordChangedEvent(DomainEvent):
    """用户密码更改事件"""
    
    user_id: str
    changed_by: Optional[str] = None  # 谁更改的（用户自己或管理员）
    change_type: str = "self"  # self, admin, reset


@dataclass
class UserLoggedInEvent(DomainEvent):
    """用户登录事件"""
    
    user_id: str
    login_method: str = "password"  # password, token, social
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class UserLoggedOutEvent(DomainEvent):
    """用户登出事件"""
    
    user_id: str
    session_id: Optional[str] = None
    logout_reason: str = "user"  # user, timeout, admin


@dataclass
class UserBlockedEvent(DomainEvent):
    """用户被锁定事件"""
    
    user_id: str
    blocked_by: Optional[str] = None  # 谁锁定的
    reason: Optional[str] = None
    duration_minutes: Optional[int] = None  # 锁定时长（分钟）


@dataclass
class UserUnblockedEvent(DomainEvent):
    """用户解锁事件"""
    
    user_id: str
    unblocked_by: Optional[str] = None  # 谁解锁的
    reason: Optional[str] = None


@dataclass
class UserEmailVerifiedEvent(DomainEvent):
    """用户邮箱验证事件"""
    
    user_id: str
    verified_at: datetime
    verification_method: str = "email"  # email, admin


@dataclass
class UserPhoneVerifiedEvent(DomainEvent):
    """用户手机验证事件"""
    
    user_id: str
    verified_at: datetime
    verification_method: str = "sms"  # sms, call


@dataclass
class UserMFAEnabledEvent(DomainEvent):
    """用户启用MFA事件"""
    
    user_id: str
    mfa_type: str = "totp"  # totp, sms, email


@dataclass
class UserMFADisabledEvent(DomainEvent):
    """用户禁用MFA事件"""
    
    user_id: str
    disabled_by: Optional[str] = None  # 谁禁用的


@dataclass
class TenantCreatedEvent(DomainEvent):
    """租户创建事件"""
    
    tenant_id: str
    tenant_name: str
    owner_id: str
    tenant_type: str = "family"


@dataclass
class TenantUpdatedEvent(DomainEvent):
    """租户更新事件"""
    
    tenant_id: str
    updated_fields: dict
    updated_by: str


@dataclass
class TenantMemberAddedEvent(DomainEvent):
    """租户添加成员事件"""
    
    tenant_id: str
    user_id: str
    added_by: str  # 谁添加的
    role: Optional[str] = "member"


@dataclass
class TenantMemberRemovedEvent(DomainEvent):
    """租户移除成员事件"""
    
    tenant_id: str
    user_id: str
    removed_by: str  # 谁移除的
    reason: Optional[str] = None


@dataclass
class TenantDeletedEvent(DomainEvent):
    """租户删除事件"""
    
    tenant_id: str
    deleted_by: str
    reason: Optional[str] = None
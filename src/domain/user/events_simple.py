"""
简化的用户领域事件
避免dataclass继承问题
"""

from datetime import datetime
from typing import Optional
from ..base_simple import DomainEvent


class UserRegisteredEvent(DomainEvent):
    """用户注册事件"""
    
    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        registration_source: str = "web",
        metadata: Optional[dict] = None,
        **kwargs
    ):
        super().__init__(aggregate_id=user_id, **kwargs)
        self.user_id = user_id
        self.username = username
        self.email = email
        self.registration_source = registration_source
        self.metadata = metadata or {}


class UserActivatedEvent(DomainEvent):
    """用户激活事件"""
    
    def __init__(
        self,
        user_id: str,
        activated_by: Optional[str] = None,
        activation_method: str = "email",
        **kwargs
    ):
        super().__init__(aggregate_id=user_id, **kwargs)
        self.user_id = user_id
        self.activated_by = activated_by
        self.activation_method = activation_method


class UserUpdatedEvent(DomainEvent):
    """用户更新事件"""
    
    def __init__(
        self,
        user_id: str,
        updated_fields: dict,
        updated_by: Optional[str] = None,
        **kwargs
    ):
        super().__init__(aggregate_id=user_id, **kwargs)
        self.user_id = user_id
        self.updated_fields = updated_fields
        self.updated_by = updated_by


class UserPasswordChangedEvent(DomainEvent):
    """用户密码更改事件"""
    
    def __init__(
        self,
        user_id: str,
        changed_by: Optional[str] = None,
        change_type: str = "self",
        **kwargs
    ):
        super().__init__(aggregate_id=user_id, **kwargs)
        self.user_id = user_id
        self.changed_by = changed_by
        self.change_type = change_type


class UserLoggedInEvent(DomainEvent):
    """用户登录事件"""
    
    def __init__(
        self,
        user_id: str,
        login_method: str = "password",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        **kwargs
    ):
        super().__init__(aggregate_id=user_id, **kwargs)
        self.user_id = user_id
        self.login_method = login_method
        self.ip_address = ip_address
        self.user_agent = user_agent


class UserLoggedOutEvent(DomainEvent):
    """用户登出事件"""
    
    def __init__(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        logout_reason: str = "user",
        **kwargs
    ):
        super().__init__(aggregate_id=user_id, **kwargs)
        self.user_id = user_id
        self.session_id = session_id
        self.logout_reason = logout_reason


class UserBlockedEvent(DomainEvent):
    """用户被锁定事件"""
    
    def __init__(
        self,
        user_id: str,
        blocked_by: Optional[str] = None,
        reason: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        **kwargs
    ):
        super().__init__(aggregate_id=user_id, **kwargs)
        self.user_id = user_id
        self.blocked_by = blocked_by
        self.reason = reason
        self.duration_minutes = duration_minutes


class UserUnblockedEvent(DomainEvent):
    """用户解锁事件"""
    
    def __init__(
        self,
        user_id: str,
        unblocked_by: Optional[str] = None,
        reason: Optional[str] = None,
        **kwargs
    ):
        super().__init__(aggregate_id=user_id, **kwargs)
        self.user_id = user_id
        self.unblocked_by = unblocked_by
        self.reason = reason


class UserEmailVerifiedEvent(DomainEvent):
    """用户邮箱验证事件"""
    
    def __init__(
        self,
        user_id: str,
        verified_at: datetime,
        verification_method: str = "email",
        **kwargs
    ):
        super().__init__(aggregate_id=user_id, **kwargs)
        self.user_id = user_id
        self.verified_at = verified_at
        self.verification_method = verification_method


class UserPhoneVerifiedEvent(DomainEvent):
    """用户手机验证事件"""
    
    def __init__(
        self,
        user_id: str,
        verified_at: datetime,
        verification_method: str = "sms",
        **kwargs
    ):
        super().__init__(aggregate_id=user_id, **kwargs)
        self.user_id = user_id
        self.verified_at = verified_at
        self.verification_method = verification_method


class UserMFAEnabledEvent(DomainEvent):
    """用户启用MFA事件"""
    
    def __init__(
        self,
        user_id: str,
        mfa_type: str = "totp",
        **kwargs
    ):
        super().__init__(aggregate_id=user_id, **kwargs)
        self.user_id = user_id
        self.mfa_type = mfa_type


class UserMFADisabledEvent(DomainEvent):
    """用户禁用MFA事件"""
    
    def __init__(
        self,
        user_id: str,
        disabled_by: Optional[str] = None,
        **kwargs
    ):
        super().__init__(aggregate_id=user_id, **kwargs)
        self.user_id = user_id
        self.disabled_by = disabled_by


class TenantCreatedEvent(DomainEvent):
    """租户创建事件"""
    
    def __init__(
        self,
        tenant_id: str,
        tenant_name: str,
        owner_id: str,
        tenant_type: str = "family",
        **kwargs
    ):
        super().__init__(aggregate_id=tenant_id, **kwargs)
        self.tenant_id = tenant_id
        self.tenant_name = tenant_name
        self.owner_id = owner_id
        self.tenant_type = tenant_type


class TenantUpdatedEvent(DomainEvent):
    """租户更新事件"""
    
    def __init__(
        self,
        tenant_id: str,
        updated_fields: dict,
        updated_by: str,
        **kwargs
    ):
        super().__init__(aggregate_id=tenant_id, **kwargs)
        self.tenant_id = tenant_id
        self.updated_fields = updated_fields
        self.updated_by = updated_by


class TenantMemberAddedEvent(DomainEvent):
    """租户添加成员事件"""
    
    def __init__(
        self,
        tenant_id: str,
        user_id: str,
        added_by: str,
        role: Optional[str] = "member",
        **kwargs
    ):
        super().__init__(aggregate_id=tenant_id, **kwargs)
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.added_by = added_by
        self.role = role


class TenantMemberRemovedEvent(DomainEvent):
    """租户移除成员事件"""
    
    def __init__(
        self,
        tenant_id: str,
        user_id: str,
        removed_by: str,
        reason: Optional[str] = None,
        **kwargs
    ):
        super().__init__(aggregate_id=tenant_id, **kwargs)
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.removed_by = removed_by
        self.reason = reason


class TenantDeletedEvent(DomainEvent):
    """租户删除事件"""
    
    def __init__(
        self,
        tenant_id: str,
        deleted_by: str,
        reason: Optional[str] = None,
        **kwargs
    ):
        super().__init__(aggregate_id=tenant_id, **kwargs)
        self.tenant_id = tenant_id
        self.deleted_by = deleted_by
        self.reason = reason
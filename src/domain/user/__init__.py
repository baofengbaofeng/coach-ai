"""
用户领域模块
包含用户、租户、权限等核心业务概念
"""

from .value_objects_simple import Email, Password, PhoneNumber, UserStatus, VerificationStatus
from .entities_simple import User, Tenant, Permission
from .services import UserService, TenantService, PermissionService
from .events_simple import (
    UserRegisteredEvent,
    UserActivatedEvent,
    UserUpdatedEvent,
    UserPasswordChangedEvent,
    UserLoggedInEvent,
    UserLoggedOutEvent,
    UserBlockedEvent,
    UserUnblockedEvent,
    UserEmailVerifiedEvent,
    UserPhoneVerifiedEvent,
    UserMFAEnabledEvent,
    UserMFADisabledEvent,
    TenantCreatedEvent,
    TenantUpdatedEvent,
    TenantMemberAddedEvent,
    TenantMemberRemovedEvent,
    TenantDeletedEvent
)

__all__ = [
    # 值对象
    'Email',
    'Password',
    'PhoneNumber',
    'UserStatus',
    'VerificationStatus',
    
    # 实体
    'User',
    'Tenant',
    'Permission',
    
    # 领域服务
    'UserService',
    'TenantService',
    'PermissionService',
    
    # 领域事件
    'UserRegisteredEvent',
    'UserActivatedEvent',
    'UserUpdatedEvent',
    'UserPasswordChangedEvent',
    'UserLoggedInEvent',
    'UserLoggedOutEvent',
    'UserBlockedEvent',
    'UserUnblockedEvent',
    'UserEmailVerifiedEvent',
    'UserPhoneVerifiedEvent',
    'UserMFAEnabledEvent',
    'UserMFADisabledEvent',
    'TenantCreatedEvent',
    'TenantUpdatedEvent',
    'TenantMemberAddedEvent',
    'TenantMemberRemovedEvent',
    'TenantDeletedEvent',
]
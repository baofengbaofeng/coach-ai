"""
租户模块
处理多租户架构中的租户管理和成员管理
"""

from .handlers import (
    CreateTenantHandler,
    GetTenantHandler,
    UpdateTenantHandler,
    DeleteTenantHandler,
    GetTenantMembersHandler,
    InviteMemberHandler,
    AcceptInvitationHandler,
    UpdateMemberRoleHandler,
    RemoveMemberHandler,
    GetUserTenantsHandler,
    SearchTenantsHandler
)

from .services import tenant_service
from .models import (
    CreateTenantRequest,
    UpdateTenantRequest,
    InviteMemberRequest,
    UpdateMemberRoleRequest,
    AcceptInvitationRequest,
    TenantResponse,
    TenantMemberResponse,
    UserTenantResponse,
    CreateTenantResponse,
    UpdateTenantResponse,
    GetTenantMembersResponse,
    InviteMemberResponse,
    GetUserTenantsResponse,
    SearchTenantsResponse,
    MessageResponse,
    TENANT_TAGS,
    TENANT_DESCRIPTION
)

__all__ = [
    # 处理器
    'CreateTenantHandler',
    'GetTenantHandler',
    'UpdateTenantHandler',
    'DeleteTenantHandler',
    'GetTenantMembersHandler',
    'InviteMemberHandler',
    'AcceptInvitationHandler',
    'UpdateMemberRoleHandler',
    'RemoveMemberHandler',
    'GetUserTenantsHandler',
    'SearchTenantsHandler',
    
    # 服务
    'tenant_service',
    
    # 模型
    'CreateTenantRequest',
    'UpdateTenantRequest',
    'InviteMemberRequest',
    'UpdateMemberRoleRequest',
    'AcceptInvitationRequest',
    'TenantResponse',
    'TenantMemberResponse',
    'UserTenantResponse',
    'CreateTenantResponse',
    'UpdateTenantResponse',
    'GetTenantMembersResponse',
    'InviteMemberResponse',
    'GetUserTenantsResponse',
    'SearchTenantsResponse',
    'MessageResponse',
    
    # API文档
    'TENANT_TAGS',
    'TENANT_DESCRIPTION'
]
"""
租户模型
定义租户管理相关的数据模型和验证规则
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class CreateTenantRequest(BaseModel):
    """
    创建租户请求模型
    """
    name: str 
    code: str 
    description: Optional[str] = None
    type: str = Field('family', description="租户类型")
    domain: Optional[str] = None
    logo_url: Optional[str] = None
    cover_url: Optional[str] = None
    config: Optional[Dict[str, Any]] 
    metadata: Optional[Dict[str, Any]] 
    max_members: int = Field(10, ge=1, le=1000, description="最大成员数")
    storage_limit_mb: int = Field(1024, ge=10, le=1048576, description="存储空间限制(MB)")
    subscription_plan: str = Field('free', description="订阅计划")
    
    @validator('code')
    def validate_code(cls, v):
        """验证租户代码格式"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Tenant code can only contain letters, numbers, underscores and hyphens')
        return v.lower()  # 转换为小写
    
    @validator('type')
    def validate_type(cls, v):
        """验证租户类型"""
        valid_types = ['family', 'organization', 'team', 'individual']
        if v not in valid_types:
            raise ValueError(f'Type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('domain')
    def validate_domain(cls, v):
        """验证域名格式"""
        if v is not None:
            # 简单的域名验证
            if len(v) < 3 or len(v) > 255:
                raise ValueError('Domain must be between 3 and 255 characters')
            if ' ' in v:
                raise ValueError('Domain cannot contain spaces')
            if not any(c in v for c in ['.', 'localhost']):
                raise ValueError('Invalid domain format')
        return v


class UpdateTenantRequest(BaseModel):
    """
    更新租户请求模型
    """
    name: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    logo_url: Optional[str] = None
    cover_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    max_members: Optional[int] = None
    storage_limit_mb: Optional[int] = None")
    
    @validator('domain')
    def validate_domain(cls, v):
        """验证域名格式"""
        if v is not None:
            if len(v) < 3 or len(v) > 255:
                raise ValueError('Domain must be between 3 and 255 characters')
            if ' ' in v:
                raise ValueError('Domain cannot contain spaces')
            if not any(c in v for c in ['.', 'localhost']):
                raise ValueError('Invalid domain format')
        return v


class InviteMemberRequest(BaseModel):
    """
    邀请成员请求模型
    """
    email: str 
    role: str = Field('member', description="成员角色")
    permissions: Optional[Dict[str, Any]] 
    config: Optional[Dict[str, Any]] 
    
    @validator('role')
    def validate_role(cls, v):
        """验证角色"""
        valid_roles = ['owner', 'admin', 'member', 'guest']
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v


class UpdateMemberRoleRequest(BaseModel):
    """
    更新成员角色请求模型
    """
    role: str 
    
    @validator('role')
    def validate_role(cls, v):
        """验证角色"""
        valid_roles = ['owner', 'admin', 'member', 'guest']
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v


class AcceptInvitationRequest(BaseModel):
    """
    接受邀请请求模型
    """
    invite_token: str 


class TenantResponse(BaseModel):
    """
    租户响应模型
    """
    id: str 
    name: str 
    code: str 
    description: Optional[str] = None
    type: str 
    status: str 
    owner_id: str 
    domain: Optional[str] = None
    logo_url: Optional[str] = None
    cover_url: Optional[str] = None
    max_members: int 
    storage_limit_mb: int ")
    subscription_plan: str 
    subscription_expires_at: Optional[datetime] = None
    member_count: int 
    can_add_member: bool 
    created_at: datetime 
    updated_at: datetime 


class TenantMemberResponse(BaseModel):
    """
    租户成员响应模型
    """
    id: str 
    user_id: str 
    username: str 
    email: str 
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str 
    status: str 
    joined_at: Optional[datetime] = None
    permissions: Dict[str, Any] 
    created_at: datetime 


class UserTenantResponse(BaseModel):
    """
    用户租户响应模型
    """
    id: str 
    name: str 
    code: str 
    type: str 
    status: str 
    role: str 
    member_count: int 
    joined_at: Optional[datetime] = None
    created_at: datetime 


class CreateTenantResponse(BaseModel):
    """
    创建租户响应模型
    """
    tenant: TenantResponse 
    message: str 


class UpdateTenantResponse(BaseModel):
    """
    更新租户响应模型
    """
    tenant: TenantResponse 
    message: str 


class GetTenantMembersResponse(BaseModel):
    """
    获取租户成员响应模型
    """
    members: List[TenantMemberResponse] 
    total: int 


class InviteMemberResponse(BaseModel):
    """
    邀请成员响应模型
    """
    invite_token: str 
    message: str 


class GetUserTenantsResponse(BaseModel):
    """
    获取用户租户响应模型
    """
    tenants: List[UserTenantResponse] 
    total: int 


class SearchTenantsResponse(BaseModel):
    """
    搜索租户响应模型
    """
    tenants: List[TenantResponse] 
    total: int 


class MessageResponse(BaseModel):
    """
    通用消息响应模型
    """
    message: str 


# API文档标签和描述
TENANT_TAGS = ["Tenant Management"]
TENANT_DESCRIPTION = """
租户管理相关API，用于创建、管理租户（家庭/组织）和成员。

## 租户概念
- **租户**: 代表一个独立的数据隔离单元，可以是家庭、组织、团队或个人
- **成员**: 属于租户的用户，具有不同的角色和权限
- **角色**: 定义成员在租户中的权限级别（owner, admin, member, guest）

## 主要功能
1. **租户管理**: 创建、查看、更新、删除租户
2. **成员管理**: 邀请、接受邀请、更新角色、移除成员
3. **权限控制**: 基于角色的访问控制
4. **数据隔离**: 每个租户的数据完全隔离

## 权限规则
- **所有者 (owner)**: 拥有所有权限，可以管理租户和所有成员
- **管理员 (admin)**: 可以管理普通成员，但不能管理所有者
- **成员 (member)**: 可以访问租户资源，但不能管理其他成员
- **访客 (guest)**: 只读访问权限

## 使用流程
1. 用户创建租户（自动成为所有者）
2. 所有者邀请其他用户加入
3. 被邀请用户接受邀请
4. 所有者/管理员管理成员角色和权限
"""
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
    name: str = Field(..., min_length=1, max_length=100, description="租户名称")
    code: str = Field(..., min_length=3, max_length=50, description="租户代码")
    description: Optional[str] = Field(None, description="租户描述")
    type: str = Field('family', description="租户类型")
    domain: Optional[str] = Field(None, max_length=255, description="域名")
    logo_url: Optional[str] = Field(None, description="Logo URL")
    cover_url: Optional[str] = Field(None, description="封面图片URL")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="租户配置")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="租户元数据")
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
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="租户名称")
    description: Optional[str] = Field(None, description="租户描述")
    domain: Optional[str] = Field(None, max_length=255, description="域名")
    logo_url: Optional[str] = Field(None, description="Logo URL")
    cover_url: Optional[str] = Field(None, description="封面图片URL")
    config: Optional[Dict[str, Any]] = Field(None, description="租户配置")
    metadata: Optional[Dict[str, Any]] = Field(None, description="租户元数据")
    max_members: Optional[int] = Field(None, ge=1, le=1000, description="最大成员数")
    storage_limit_mb: Optional[int] = Field(None, ge=10, le=1048576, description="存储空间限制(MB)")
    
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
    email: str = Field(..., description="被邀请用户邮箱")
    role: str = Field('member', description="成员角色")
    permissions: Optional[Dict[str, Any]] = Field(default_factory=dict, description="权限配置")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="成员配置")
    
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
    role: str = Field(..., description="新角色")
    
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
    invite_token: str = Field(..., description="邀请令牌")


class TenantResponse(BaseModel):
    """
    租户响应模型
    """
    id: str = Field(..., description="租户ID")
    name: str = Field(..., description="租户名称")
    code: str = Field(..., description="租户代码")
    description: Optional[str] = Field(None, description="租户描述")
    type: str = Field(..., description="租户类型")
    status: str = Field(..., description="租户状态")
    owner_id: str = Field(..., description="所有者ID")
    domain: Optional[str] = Field(None, description="域名")
    logo_url: Optional[str] = Field(None, description="Logo URL")
    cover_url: Optional[str] = Field(None, description="封面图片URL")
    max_members: int = Field(..., description="最大成员数")
    storage_limit_mb: int = Field(..., description="存储空间限制(MB)")
    subscription_plan: str = Field(..., description="订阅计划")
    subscription_expires_at: Optional[datetime] = Field(None, description="订阅过期时间")
    member_count: int = Field(..., description="当前成员数量")
    can_add_member: bool = Field(..., description="是否可以添加新成员")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class TenantMemberResponse(BaseModel):
    """
    租户成员响应模型
    """
    id: str = Field(..., description="成员记录ID")
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    display_name: Optional[str] = Field(None, description="显示名称")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    role: str = Field(..., description="成员角色")
    status: str = Field(..., description="成员状态")
    joined_at: Optional[datetime] = Field(None, description="加入时间")
    permissions: Dict[str, Any] = Field(default_factory=dict, description="权限配置")
    created_at: datetime = Field(..., description="创建时间")


class UserTenantResponse(BaseModel):
    """
    用户租户响应模型
    """
    id: str = Field(..., description="租户ID")
    name: str = Field(..., description="租户名称")
    code: str = Field(..., description="租户代码")
    type: str = Field(..., description="租户类型")
    status: str = Field(..., description="租户状态")
    role: str = Field(..., description="用户角色")
    member_count: int = Field(..., description="成员数量")
    joined_at: Optional[datetime] = Field(None, description="加入时间")
    created_at: datetime = Field(..., description="创建时间")


class CreateTenantResponse(BaseModel):
    """
    创建租户响应模型
    """
    tenant: TenantResponse = Field(..., description="租户信息")
    message: str = Field(..., description="提示消息")


class UpdateTenantResponse(BaseModel):
    """
    更新租户响应模型
    """
    tenant: TenantResponse = Field(..., description="租户信息")
    message: str = Field(..., description="提示消息")


class GetTenantMembersResponse(BaseModel):
    """
    获取租户成员响应模型
    """
    members: List[TenantMemberResponse] = Field(default_factory=list, description="成员列表")
    total: int = Field(..., description="成员总数")


class InviteMemberResponse(BaseModel):
    """
    邀请成员响应模型
    """
    invite_token: str = Field(..., description="邀请令牌")
    message: str = Field(..., description="提示消息")


class GetUserTenantsResponse(BaseModel):
    """
    获取用户租户响应模型
    """
    tenants: List[UserTenantResponse] = Field(default_factory=list, description="租户列表")
    total: int = Field(..., description="租户总数")


class SearchTenantsResponse(BaseModel):
    """
    搜索租户响应模型
    """
    tenants: List[TenantResponse] = Field(default_factory=list, description="租户列表")
    total: int = Field(..., description="租户总数")


class MessageResponse(BaseModel):
    """
    通用消息响应模型
    """
    message: str = Field(..., description="消息内容")


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
"""
租户模型
管理多租户架构中的租户（家庭）信息
"""

from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Index, JSON, Integer
from datetime import datetime
from sqlalchemy.dialects.mysql import CHAR, VARCHAR
from sqlalchemy.orm import relationship

from .base import BaseModel


class Tenant(BaseModel):
    """
    租户模型
    代表一个家庭或组织，用于数据隔离
    """
    __tablename__ = 'tenants'
    
    # 租户名称
    name = Column(VARCHAR(100), nullable=False, index=True)
    
    # 租户代码（唯一标识符）
    code = Column(VARCHAR(50), unique=True, nullable=False, index=True)
    
    # 租户描述
    description = Column(Text, nullable=True)
    
    # 租户类型：family, organization, team, individual
    type = Column(
        Enum('family', 'organization', 'team', 'individual', name='tenant_type'),
        default='family',
        nullable=False
    )
    
    # 租户状态：active, inactive, suspended, pending
    status = Column(
        Enum('active', 'inactive', 'suspended', 'pending', name='tenant_status'),
        default='pending',
        nullable=False
    )
    
    # 租户配置（JSON格式）
    config = Column(JSON, nullable=True, default=dict)
    
    # 租户元数据（JSON格式）
    tenant_metadata = Column('metadata', JSON, nullable=True, default=dict)
    
    # 所有者ID
    owner_id = Column(CHAR(36), nullable=False, index=True)
    
    # 最大成员数
    max_members = Column(Integer, default=10, nullable=False)
    
    # 存储空间限制（MB）
    storage_limit_mb = Column(Integer, default=1024, nullable=False)
    
    # 订阅计划
    subscription_plan = Column(VARCHAR(50), default='free', nullable=False)
    
    # 订阅过期时间
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # 租户域名（可选）
    domain = Column(VARCHAR(255), nullable=True, unique=True, index=True)
    
    # 租户logo URL
    logo_url = Column(Text, nullable=True)
    
    # 租户封面图片URL
    cover_url = Column(Text, nullable=True)
    
    # 关系
    owner = relationship('User', back_populates='owned_tenants', foreign_keys=[owner_id])
    members = relationship('User', secondary='tenant_members', back_populates='tenants')
    member_details = relationship('TenantMember', back_populates='tenant')
    
    # 索引
    __table_args__ = (
        Index('idx_tenant_status', 'status'),
        Index('idx_tenant_type', 'type'),
        Index('idx_tenant_owner', 'owner_id'),
        Index('idx_tenant_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Tenant(id='{self.id}', name='{self.name}', code='{self.code}')>"
    
    def is_active(self):
        """
        检查租户是否活跃
        """
        return self.status == 'active' and not self.is_deleted
    
    def can_add_member(self):
        """
        检查是否可以添加新成员
        """
        from sqlalchemy import func
        # 这里需要在实际查询时实现
        # current_count = session.query(func.count(TenantMember.id)).filter_by(tenant_id=self.id, is_deleted=False).scalar()
        # return current_count < self.max_members
        return True
    
    def get_config_value(self, key, default=None):
        """
        获取租户配置值
        """
        if self.config and key in self.config:
            return self.config[key]
        return default
    
    def set_config_value(self, key, value):
        """
        设置租户配置值
        """
        if self.config is None:
            self.config = {}
        self.config[key] = value
    
    def to_public_dict(self):
        """
        转换为公开的租户信息
        """
        data = self.to_dict()
        # 移除内部字段
        internal_fields = ['config', 'metadata']
        for field in internal_fields:
            data.pop(field, None)
        return data


class TenantMember(BaseModel):
    """
    租户成员模型
    管理用户与租户的关联关系
    """
    __tablename__ = 'tenant_members'
    
    # 租户ID
    tenant_id = Column(CHAR(36), nullable=False, index=True)
    
    # 用户ID
    user_id = Column(CHAR(36), nullable=False, index=True)
    
    # 成员角色：owner, admin, member, guest
    role = Column(
        Enum('owner', 'admin', 'member', 'guest', name='member_role'),
        default='member',
        nullable=False
    )
    
    # 成员状态：active, inactive, pending, rejected
    status = Column(
        Enum('active', 'inactive', 'pending', 'rejected', name='member_status'),
        default='pending',
        nullable=False
    )
    
    # 加入时间
    joined_at = Column(DateTime, nullable=True)
    
    # 邀请令牌
    invite_token = Column(String(255), nullable=True, unique=True, index=True)
    
    # 邀请令牌过期时间
    invite_expires_at = Column(DateTime, nullable=True)
    
    # 邀请人ID
    invited_by = Column(CHAR(36), nullable=True)
    
    # 成员权限（JSON格式）
    permissions = Column(JSON, nullable=True, default=dict)
    
    # 成员配置（JSON格式）
    config = Column(JSON, nullable=True, default=dict)
    
    # 关系
    tenant = relationship('Tenant', back_populates='member_details')
    user = relationship('User')
    
    # 唯一约束：一个用户在同一个租户中只能有一条记录
    __table_args__ = (
        Index('idx_tenant_member_unique', 'tenant_id', 'user_id', unique=True),
        Index('idx_tenant_member_role', 'tenant_id', 'role'),
        Index('idx_tenant_member_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<TenantMember(tenant_id='{self.tenant_id}', user_id='{self.user_id}', role='{self.role}')>"
    
    def is_active(self):
        """
        检查成员是否活跃
        """
        return self.status == 'active' and not self.is_deleted
    
    def has_permission(self, permission):
        """
        检查成员是否具有特定权限
        """
        if self.role == 'owner':
            return True
        if self.permissions and permission in self.permissions:
            return self.permissions[permission]
        return False
    
    def grant_permission(self, permission, value=True):
        """
        授予权限
        """
        if self.permissions is None:
            self.permissions = {}
        self.permissions[permission] = value
    
    def revoke_permission(self, permission):
        """
        撤销权限
        """
        if self.permissions and permission in self.permissions:
            del self.permissions[permission]
    
    def accept_invitation(self):
        """
        接受邀请
        """
        if self.status == 'pending':
            self.status = 'active'
            self.joined_at = datetime.utcnow()
            self.invite_token = None
            self.invite_expires_at = None
            return True
        return False
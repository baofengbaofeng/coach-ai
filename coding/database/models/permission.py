"""
权限模型
管理系统权限和角色管理
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Index, Integer, Enum, JSON
from sqlalchemy.dialects.mysql import CHAR, VARCHAR
from sqlalchemy.orm import relationship

from .base import BaseModel


class Permission(BaseModel):
    """
    权限定义模型
    定义系统中的所有权限
    """
    __tablename__ = 'permissions'
    
    # 权限代码（唯一标识符）
    code = Column(VARCHAR(100), unique=True, nullable=False, index=True)
    
    # 权限名称
    name = Column(VARCHAR(100), nullable=False)
    
    # 权限描述
    description = Column(Text, nullable=True)
    
    # 权限分类
    category = Column(VARCHAR(50), nullable=False, index=True)
    
    # 权限作用域：system, tenant, user
    scope = Column(
        Enum('system', 'tenant', 'user', name='permission_scope'),
        default='tenant',
        nullable=False
    )
    
    # 是否默认授予所有用户
    is_default = Column(Boolean, default=False, nullable=False)
    
    # 依赖权限（JSON数组）
    dependencies = Column(JSON, nullable=True, default=list)
    
    # 权限元数据（JSON格式）
    permission_metadata = Column('metadata', JSON, nullable=True, default=dict)
    
    # 关系
    roles = relationship('Role', secondary='role_permissions', back_populates='permissions')
    
    # 索引
    __table_args__ = (
        Index('idx_permission_category', 'category'),
        Index('idx_permission_scope', 'scope'),
        Index('idx_permission_is_default', 'is_default'),
    )
    
    def __repr__(self):
        return f"<Permission(id='{self.id}', code='{self.code}', name='{self.name}')>"
    
    def has_dependency(self, permission_code):
        """
        检查是否依赖特定权限
        """
        return self.dependencies and permission_code in self.dependencies


class Role(BaseModel):
    """
    角色模型
    定义用户角色和权限组
    """
    __tablename__ = 'roles'
    
    # 角色代码（唯一标识符）
    code = Column(VARCHAR(50), unique=True, nullable=False, index=True)
    
    # 角色名称
    name = Column(VARCHAR(100), nullable=False)
    
    # 角色描述
    description = Column(Text, nullable=True)
    
    # 角色类型：system, tenant, custom
    type = Column(
        Enum('system', 'tenant', 'custom', name='role_type'),
        default='custom',
        nullable=False
    )
    
    # 角色级别（用于排序和继承）
    level = Column(Integer, default=0, nullable=False)
    
    # 是否系统内置角色
    is_system = Column(Boolean, default=False, nullable=False)
    
    # 是否默认角色
    is_default = Column(Boolean, default=False, nullable=False)
    
    # 角色配置（JSON格式）
    config = Column(JSON, nullable=True, default=dict)
    
    # 角色元数据（JSON格式）
    role_metadata = Column('metadata', JSON, nullable=True, default=dict)
    
    # 关系
    permissions = relationship('Permission', secondary='role_permissions', back_populates='roles')
    users = relationship('User', secondary='user_roles', back_populates='roles')
    
    # 索引
    __table_args__ = (
        Index('idx_role_type', 'type'),
        Index('idx_role_level', 'level'),
        Index('idx_role_is_system', 'is_system'),
        Index('idx_role_is_default', 'is_default'),
    )
    
    def __repr__(self):
        return f"<Role(id='{self.id}', code='{self.code}', name='{self.name}')>"
    
    def has_permission(self, permission_code):
        """
        检查角色是否具有特定权限
        """
        for permission in self.permissions:
            if permission.code == permission_code:
                return True
        return False
    
    def add_permission(self, permission):
        """
        添加权限到角色
        """
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission):
        """
        从角色移除权限
        """
        if permission in self.permissions:
            self.permissions.remove(permission)


class RolePermission(BaseModel):
    """
    角色权限关联模型
    管理角色和权限的多对多关系
    """
    __tablename__ = 'role_permissions'
    
    # 角色ID
    role_id = Column(CHAR(36), nullable=False, index=True)
    
    # 权限ID
    permission_id = Column(CHAR(36), nullable=False, index=True)
    
    # 是否继承（用于角色继承）
    is_inherited = Column(Boolean, default=False, nullable=False)
    
    # 继承来源角色ID
    inherited_from = Column(CHAR(36), nullable=True)
    
    # 权限配置覆盖（JSON格式）
    config_override = Column(JSON, nullable=True)
    
    # 唯一约束
    __table_args__ = (
        Index('idx_role_permission_unique', 'role_id', 'permission_id', unique=True),
    )
    
    def __repr__(self):
        return f"<RolePermission(role_id='{self.role_id}', permission_id='{self.permission_id}')>"


class UserRole(BaseModel):
    """
    用户角色关联模型
    管理用户和角色的多对多关系
    """
    __tablename__ = 'user_roles'
    
    # 用户ID
    user_id = Column(CHAR(36), nullable=False, index=True)
    
    # 角色ID
    role_id = Column(CHAR(36), nullable=False, index=True)
    
    # 租户ID（对于租户级角色）
    tenant_id = Column(CHAR(36), nullable=True, index=True)
    
    # 是否默认角色
    is_default = Column(Boolean, default=False, nullable=False)
    
    # 角色配置（JSON格式）
    config = Column(JSON, nullable=True, default=dict)
    
    # 唯一约束：一个用户在同一个租户中不能重复分配同一个角色
    __table_args__ = (
        Index('idx_user_role_unique', 'user_id', 'role_id', 'tenant_id', unique=True),
        Index('idx_user_role_tenant', 'tenant_id', 'user_id'),
    )
    
    def __repr__(self):
        return f"<UserRole(user_id='{self.user_id}', role_id='{self.role_id}', tenant_id='{self.tenant_id}')>"
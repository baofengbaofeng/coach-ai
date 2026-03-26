"""
用户模型
存储用户基本信息、认证信息和状态
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Index, Integer
from sqlalchemy.dialects.mysql import CHAR, VARCHAR
from sqlalchemy.orm import relationship

from .base import BaseModel


class User(BaseModel):
    """
    用户模型
    管理用户账户信息
    """
    __tablename__ = 'users'
    
    # 用户名，唯一标识
    username = Column(VARCHAR(50), unique=True, nullable=False, index=True)
    
    # 邮箱，唯一标识
    email = Column(VARCHAR(255), unique=True, nullable=False, index=True)
    
    # 手机号，唯一标识
    phone = Column(VARCHAR(20), unique=True, nullable=True, index=True)
    
    # 密码哈希
    password_hash = Column(String(255), nullable=False)
    
    # 用户显示名称
    display_name = Column(VARCHAR(100), nullable=True)
    
    # 头像URL
    avatar_url = Column(Text, nullable=True)
    
    # 用户状态：active, inactive, blocked, pending
    status = Column(
        Enum('active', 'inactive', 'blocked', 'pending', name='user_status'),
        default='pending',
        nullable=False
    )
    
    # 邮箱验证状态
    email_verified = Column(Boolean, default=False, nullable=False)
    
    # 手机验证状态
    phone_verified = Column(Boolean, default=False, nullable=False)
    
    # 最后登录时间
    last_login_at = Column(DateTime, nullable=True)
    
    # 最后登录IP
    last_login_ip = Column(VARCHAR(45), nullable=True)
    
    # 登录失败次数
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    
    # 账户锁定时间
    locked_until = Column(DateTime, nullable=True)
    
    # 多因素认证启用状态
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    
    # 多因素认证密钥
    mfa_secret = Column(String(255), nullable=True)
    
    # 密码重置令牌
    password_reset_token = Column(String(255), nullable=True)
    
    # 密码重置令牌过期时间
    password_reset_expires = Column(DateTime, nullable=True)
    
    # 邮箱验证令牌
    email_verify_token = Column(String(255), nullable=True)
    
    # 邮箱验证令牌过期时间
    email_verify_expires = Column(DateTime, nullable=True)
    
    # 租户关系（一个用户可以属于多个租户）
    tenants = relationship('Tenant', secondary='tenant_members', back_populates='members')
    
    # 创建的家庭/租户
    owned_tenants = relationship('Tenant', back_populates='owner')
    
    # 成就系统关系
    user_achievements = relationship('UserAchievement', back_populates='user', cascade='all, delete-orphan')
    user_badges = relationship('UserBadge', back_populates='user', cascade='all, delete-orphan')
    user_rewards = relationship('UserReward', back_populates='user', cascade='all, delete-orphan')
    
    # 索引
    __table_args__ = (
        Index('idx_user_status', 'status'),
        Index('idx_user_email_verified', 'email_verified'),
        Index('idx_user_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}', email='{self.email}')>"
    
    def is_active(self):
        """
        检查用户是否活跃
        """
        return self.status == 'active' and not self.is_deleted
    
    def is_blocked(self):
        """
        检查用户是否被锁定
        """
        return self.status == 'blocked' or self.locked_until and self.locked_until > datetime.utcnow()
    
    def increment_failed_attempts(self, max_attempts=5, lock_minutes=30):
        """
        增加登录失败次数，如果超过阈值则锁定账户
        """
        self.failed_login_attempts += 1
        
        if self.failed_login_attempts >= max_attempts:
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=lock_minutes)
            self.status = 'blocked'
    
    def reset_failed_attempts(self):
        """
        重置登录失败次数
        """
        self.failed_login_attempts = 0
        self.locked_until = None
        if self.status == 'blocked':
            self.status = 'active'
    
    def update_last_login(self, ip_address=None):
        """
        更新最后登录信息
        """
        self.last_login_at = datetime.utcnow()
        if ip_address:
            self.last_login_ip = ip_address
        self.reset_failed_attempts()
    
    def to_public_dict(self):
        """
        转换为公开的用户信息（不包含敏感信息）
        """
        data = self.to_dict()
        # 移除敏感字段
        sensitive_fields = [
            'password_hash', 'mfa_secret', 'password_reset_token',
            'password_reset_expires', 'email_verify_token', 'email_verify_expires'
        ]
        for field in sensitive_fields:
            data.pop(field, None)
        return data
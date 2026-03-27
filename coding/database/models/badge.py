"""
徽章模型定义

徽章系统核心模型，用于定义徽章的基本信息和授予规则
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import BaseModel


class BadgeRarity(enum.Enum):
    """徽章稀有度枚举"""
    COMMON = "common"      # 普通
    UNCOMMON = "uncommon"  # 稀有
    RARE = "rare"          # 罕见
    EPIC = "epic"          # 史诗
    LEGENDARY = "legendary"  # 传奇


class BadgeType(enum.Enum):
    """徽章类型枚举"""
    ACHIEVEMENT = "achievement"  # 成就徽章
    MILESTONE = "milestone"      # 里程碑徽章
    SPECIAL = "special"          # 特殊徽章
    EVENT = "event"              # 活动徽章
    SEASONAL = "seasonal"        # 季节徽章


class BadgeStatus(enum.Enum):
    """徽章状态枚举"""
    ACTIVE = "active"      # 活跃
    INACTIVE = "inactive"  # 未激活
    ARCHIVED = "archived"  # 已归档


class Badge(BaseModel):
    """
    徽章模型

    定义徽章的基本信息和授予规则
    """
    __tablename__ = "badges"

    # 基础信息
    name = Column(String(255), nullable=False, comment="徽章名称")
    description = Column(Text, nullable=False, comment="徽章描述")
    icon_url = Column(String(500), nullable=False, comment="徽章图标URL")
    banner_url = Column(String(500), comment="徽章横幅URL")

    # 徽章类型和稀有度
    badge_type = Column(
        Enum(BadgeType),
        nullable=False,
        default=BadgeType.ACHIEVEMENT,
        comment="徽章类型"
    )
    rarity = Column(
        Enum(BadgeRarity),
        nullable=False,
        default=BadgeRarity.COMMON,
        comment="徽章稀有度"
    )
    category = Column(String(100), comment="徽章分类")
    tags = Column(JSON, default=list, comment="徽章标签")

    # 授予条件
    grant_condition = Column(Text, comment="授予条件描述")
    grant_config = Column(JSON, comment="授予条件配置")
    is_auto_grant = Column(Boolean, default=True, comment="是否自动授予")

    # 显示和排序
    display_order = Column(Integer, default=0, comment="显示顺序")
    is_hidden = Column(Boolean, default=False, comment="是否隐藏徽章")
    is_secret = Column(Boolean, default=False, comment="是否秘密徽章")

    # 统计信息
    grant_count = Column(Integer, default=0, comment="授予次数统计")
    first_grant_at = Column(DateTime, comment="首次授予时间")
    last_grant_at = Column(DateTime, comment="最近授予时间")

    # 状态
    status = Column(
        Enum(BadgeStatus),
        nullable=False,
        default=BadgeStatus.ACTIVE,
        comment="徽章状态"
    )

    # 关系
    achievements = relationship("Achievement", back_populates="badge")
    user_badges = relationship("UserBadge", back_populates="badge", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Badge(id={self.id}, name='{self.name}', rarity='{self.rarity}')>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon_url": self.icon_url,
            "banner_url": self.banner_url,
            "badge_type": self.badge_type.value,
            "rarity": self.rarity.value,
            "category": self.category,
            "tags": self.tags,
            "grant_condition": self.grant_condition,
            "grant_config": self.grant_config,
            "is_auto_grant": self.is_auto_grant,
            "display_order": self.display_order,
            "is_hidden": self.is_hidden,
            "is_secret": self.is_secret,
            "grant_count": self.grant_count,
            "first_grant_at": self.first_grant_at.isoformat() if self.first_grant_at else None,
            "last_grant_at": self.last_grant_at.isoformat() if self.last_grant_at else None,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
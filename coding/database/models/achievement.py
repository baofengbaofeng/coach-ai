"""
成就模型定义

成就系统核心模型，用于定义成就的基本信息、触发条件和奖励规则
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import BaseModel


class AchievementType(enum.Enum):
    """成就类型枚举"""
    EXERCISE = "exercise"  # 运动相关成就
    TASK = "task"          # 任务相关成就
    STREAK = "streak"      # 连续打卡成就
    MILESTONE = "milestone"  # 里程碑成就
    SPECIAL = "special"    # 特殊成就
    COLLECTION = "collection"  # 收集类成就


class AchievementDifficulty(enum.Enum):
    """成就难度枚举"""
    EASY = "easy"          # 简单
    MEDIUM = "medium"      # 中等
    HARD = "hard"          # 困难
    LEGENDARY = "legendary"  # 传奇


class AchievementStatus(enum.Enum):
    """成就状态枚举"""
    ACTIVE = "active"      # 活跃
    INACTIVE = "inactive"  # 未激活
    ARCHIVED = "archived"  # 已归档


class Achievement(BaseModel):
    """
    成就模型

    定义成就的基本信息、触发条件和奖励规则
    """
    __tablename__ = "achievements"

    # 基础信息
    name = Column(String(255), nullable=False, comment="成就名称")
    description = Column(Text, nullable=False, comment="成就描述")
    icon_url = Column(String(500), comment="成就图标URL")
    banner_url = Column(String(500), comment="成就横幅URL")

    # 成就类型和难度
    achievement_type = Column(
        Enum(AchievementType),
        nullable=False,
        default=AchievementType.EXERCISE,
        comment="成就类型"
    )
    difficulty = Column(
        Enum(AchievementDifficulty),
        nullable=False,
        default=AchievementDifficulty.EASY,
        comment="成就难度"
    )
    category = Column(String(100), comment="成就分类")
    tags = Column(JSON, default=list, comment="成就标签")

    # 触发条件
    trigger_type = Column(String(100), nullable=False, comment="触发类型")
    trigger_config = Column(JSON, nullable=False, comment="触发条件配置")
    target_value = Column(Integer, nullable=False, comment="目标值")
    current_value = Column(Integer, default=0, comment="当前值（用于进度计算）")

    # 奖励配置
    reward_points = Column(Integer, default=0, comment="奖励积分")
    reward_badge_id = Column(Integer, ForeignKey("badges.id"), comment="奖励徽章ID")
    reward_items = Column(JSON, default=list, comment="奖励物品列表")

    # 状态和时间
    status = Column(
        Enum(AchievementStatus),
        nullable=False,
        default=AchievementStatus.ACTIVE,
        comment="成就状态"
    )
    unlock_count = Column(Integer, default=0, comment="解锁次数统计")
    first_unlock_at = Column(DateTime, comment="首次解锁时间")
    last_unlock_at = Column(DateTime, comment="最近解锁时间")

    # 排序和显示
    display_order = Column(Integer, default=0, comment="显示顺序")
    is_hidden = Column(Boolean, default=False, comment="是否隐藏成就")
    is_secret = Column(Boolean, default=False, comment="是否秘密成就")

    # 关系
    badge = relationship("Badge", back_populates="achievements")
    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Achievement(id={self.id}, name='{self.name}', type='{self.achievement_type}')>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon_url": self.icon_url,
            "banner_url": self.banner_url,
            "achievement_type": self.achievement_type.value,
            "difficulty": self.difficulty.value,
            "category": self.category,
            "tags": self.tags,
            "trigger_type": self.trigger_type,
            "trigger_config": self.trigger_config,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "reward_points": self.reward_points,
            "reward_badge_id": self.reward_badge_id,
            "reward_items": self.reward_items,
            "status": self.status.value,
            "unlock_count": self.unlock_count,
            "first_unlock_at": self.first_unlock_at.isoformat() if self.first_unlock_at else None,
            "last_unlock_at": self.last_unlock_at.isoformat() if self.last_unlock_at else None,
            "display_order": self.display_order,
            "is_hidden": self.is_hidden,
            "is_secret": self.is_secret,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
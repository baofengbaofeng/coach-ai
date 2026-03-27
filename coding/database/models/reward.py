"""
奖励模型定义

奖励系统核心模型，用于定义奖励的基本信息和发放规则
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import BaseModel


class RewardType(enum.Enum):
    """奖励类型枚举"""
    POINTS = "points"          # 积分奖励
    BADGE = "badge"           # 徽章奖励
    ITEM = "item"             # 物品奖励
    DISCOUNT = "discount"     # 折扣奖励
    ACCESS = "access"         # 权限奖励
    CUSTOM = "custom"         # 自定义奖励


class RewardStatus(enum.Enum):
    """奖励状态枚举"""
    ACTIVE = "active"         # 活跃
    INACTIVE = "inactive"     # 未激活
    ARCHIVED = "archived"     # 已归档
    EXPIRED = "expired"       # 已过期


class Reward(BaseModel):
    """
    奖励模型

    定义奖励的基本信息和发放规则
    """
    __tablename__ = "rewards"

    # 基础信息
    name = Column(String(255), nullable=False, comment="奖励名称")
    description = Column(Text, nullable=False, comment="奖励描述")
    icon_url = Column(String(500), comment="奖励图标URL")
    banner_url = Column(String(500), comment="奖励横幅URL")

    # 奖励类型和配置
    reward_type = Column(
        Enum(RewardType),
        nullable=False,
        default=RewardType.POINTS,
        comment="奖励类型"
    )
    reward_config = Column(JSON, nullable=False, comment="奖励配置")
    value = Column(Integer, default=0, comment="奖励价值")

    # 发放规则
    grant_condition = Column(Text, comment="发放条件描述")
    grant_config = Column(JSON, comment="发放条件配置")
    is_auto_grant = Column(Boolean, default=True, comment="是否自动发放")

    # 限制条件
    max_claims = Column(Integer, default=-1, comment="最大领取次数（-1表示无限制）")
    claim_count = Column(Integer, default=0, comment="已领取次数")
    per_user_limit = Column(Integer, default=1, comment="每用户限制次数")
    require_achievement_id = Column(Integer, ForeignKey("achievements.id"), comment="需要成就ID")

    # 时间限制
    available_from = Column(DateTime, comment="可用开始时间")
    available_until = Column(DateTime, comment="可用结束时间")
    claim_deadline = Column(DateTime, comment="领取截止时间")

    # 状态
    status = Column(
        Enum(RewardStatus),
        nullable=False,
        default=RewardStatus.ACTIVE,
        comment="奖励状态"
    )

    # 显示和排序
    display_order = Column(Integer, default=0, comment="显示顺序")
    is_hidden = Column(Boolean, default=False, comment="是否隐藏奖励")
    is_secret = Column(Boolean, default=False, comment="是否秘密奖励")

    # 关系
    achievement = relationship("Achievement", foreign_keys=[require_achievement_id])
    user_rewards = relationship("UserReward", back_populates="reward", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Reward(id={self.id}, name='{self.name}', type='{self.reward_type}')>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon_url": self.icon_url,
            "banner_url": self.banner_url,
            "reward_type": self.reward_type.value,
            "reward_config": self.reward_config,
            "value": self.value,
            "grant_condition": self.grant_condition,
            "grant_config": self.grant_config,
            "is_auto_grant": self.is_auto_grant,
            "max_claims": self.max_claims,
            "claim_count": self.claim_count,
            "per_user_limit": self.per_user_limit,
            "require_achievement_id": self.require_achievement_id,
            "available_from": self.available_from.isoformat() if self.available_from else None,
            "available_until": self.available_until.isoformat() if self.available_until else None,
            "claim_deadline": self.claim_deadline.isoformat() if self.claim_deadline else None,
            "status": self.status.value,
            "display_order": self.display_order,
            "is_hidden": self.is_hidden,
            "is_secret": self.is_secret,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def is_available(self):
        """检查奖励是否可用"""
        from datetime import datetime
        
        if self.status != RewardStatus.ACTIVE:
            return False
        
        now = datetime.now()
        
        if self.available_from and now < self.available_from:
            return False
        
        if self.available_until and now > self.available_until:
            return False
        
        if self.max_claims != -1 and self.claim_count >= self.max_claims:
            return False
        
        return True
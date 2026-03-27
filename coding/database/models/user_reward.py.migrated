"""
用户奖励模型定义

记录用户与奖励的关系，包括奖励领取和使用信息
"""

from sqlalchemy import Column, Integer, DateTime, Boolean, Text, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import BaseModel


class UserRewardStatus(enum.Enum):
    """用户奖励状态枚举"""
    CLAIMED = "claimed"        # 已领取
    USED = "used"             # 已使用
    EXPIRED = "expired"       # 已过期
    REVOKED = "revoked"       # 已撤销


class UserReward(BaseModel):
    """
    用户奖励模型

    记录用户与奖励的关系，包括奖励领取和使用信息
    """
    __tablename__ = "user_rewards"

    # 外键关系
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=False, comment="奖励ID")
    achievement_id = Column(Integer, ForeignKey("achievements.id"), comment="关联成就ID")

    # 领取信息
    claimed_at = Column(DateTime, nullable=False, default=func.now(), comment="领取时间")
    claimed_by = Column(Integer, ForeignKey("users.id"), comment="领取者ID（如果是代领）")
    claim_reason = Column(Text, comment="领取原因")

    # 奖励详情
    reward_data = Column(JSON, nullable=False, comment="奖励数据")
    reward_value = Column(Integer, default=0, comment="奖励价值")

    # 使用信息
    status = Column(
        Enum(UserRewardStatus),
        nullable=False,
        default=UserRewardStatus.CLAIMED,
        comment="奖励状态"
    )
    used_at = Column(DateTime, comment="使用时间")
    used_for = Column(Text, comment="使用用途")
    used_data = Column(JSON, comment="使用数据")

    # 过期信息
    expires_at = Column(DateTime, comment="过期时间")
    expired_at = Column(DateTime, comment="实际过期时间")

    # 撤销信息
    revoked_at = Column(DateTime, comment="撤销时间")
    revoked_by = Column(Integer, ForeignKey("users.id"), comment="撤销者ID")
    revoke_reason = Column(Text, comment="撤销原因")

    # 关系
    user = relationship("User", foreign_keys=[user_id], back_populates="user_rewards")
    reward = relationship("Reward", back_populates="user_rewards")
    achievement = relationship("Achievement", foreign_keys=[achievement_id])
    claimer = relationship("User", foreign_keys=[claimed_by])
    revoker = relationship("User", foreign_keys=[revoked_by])

    # 唯一约束
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

    def __repr__(self):
        return f"<UserReward(id={self.id}, user_id={self.user_id}, reward_id={self.reward_id}, status='{self.status}')>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "reward_id": self.reward_id,
            "achievement_id": self.achievement_id,
            "claimed_at": self.claimed_at.isoformat() if self.claimed_at else None,
            "claimed_by": self.claimed_by,
            "claim_reason": self.claim_reason,
            "reward_data": self.reward_data,
            "reward_value": self.reward_value,
            "status": self.status.value,
            "used_at": self.used_at.isoformat() if self.used_at else None,
            "used_for": self.used_for,
            "used_data": self.used_data,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "expired_at": self.expired_at.isoformat() if self.expired_at else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "revoked_by": self.revoked_by,
            "revoke_reason": self.revoke_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def is_expired(self):
        """检查奖励是否过期"""
        from datetime import datetime
        
        if self.status == UserRewardStatus.EXPIRED:
            return True
        
        if self.expires_at and datetime.now() > self.expires_at:
            return True
        
        return False
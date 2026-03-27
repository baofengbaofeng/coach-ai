"""
用户成就模型定义

记录用户与成就的关系，包括成就进度和状态
"""

from sqlalchemy import Column, Integer, DateTime, Boolean, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import BaseModel


class UserAchievementStatus(enum.Enum):
    """用户成就状态枚举"""
    LOCKED = "locked"          # 未解锁
    IN_PROGRESS = "in_progress"  # 进行中
    UNLOCKED = "unlocked"      # 已解锁
    COMPLETED = "completed"    # 已完成


class UserAchievement(BaseModel):
    """
    用户成就模型

    记录用户与成就的关系，包括成就进度和状态
    """
    __tablename__ = "user_achievements"

    # 外键关系
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False, comment="成就ID")

    # 进度信息
    status = Column(
        Enum(UserAchievementStatus),
        nullable=False,
        default=UserAchievementStatus.LOCKED,
        comment="成就状态"
    )
    progress = Column(Integer, default=0, comment="当前进度")
    target_value = Column(Integer, nullable=False, comment="目标值")
    progress_percentage = Column(Integer, default=0, comment="进度百分比")

    # 解锁信息
    unlocked_at = Column(DateTime, comment="解锁时间")
    completed_at = Column(DateTime, comment="完成时间")
    is_new = Column(Boolean, default=True, comment="是否为新解锁成就")

    # 奖励信息
    reward_received = Column(Boolean, default=False, comment="是否已领取奖励")
    reward_received_at = Column(DateTime, comment="奖励领取时间")
    reward_data = Column(JSON, comment="奖励数据")

    # 进度详情
    progress_details = Column(JSON, comment="进度详情")
    last_updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="最后更新时间")

    # 关系
    user = relationship("User", back_populates="user_achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

    # 唯一约束
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

    def __repr__(self):
        return f"<UserAchievement(id={self.id}, user_id={self.user_id}, achievement_id={self.achievement_id}, status='{self.status}')>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "achievement_id": self.achievement_id,
            "status": self.status.value,
            "progress": self.progress,
            "target_value": self.target_value,
            "progress_percentage": self.progress_percentage,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_new": self.is_new,
            "reward_received": self.reward_received,
            "reward_received_at": self.reward_received_at.isoformat() if self.reward_received_at else None,
            "reward_data": self.reward_data,
            "progress_details": self.progress_details,
            "last_updated_at": self.last_updated_at.isoformat() if self.last_updated_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def update_progress(self, new_progress):
        """更新进度"""
        self.progress = new_progress
        if self.target_value > 0:
            self.progress_percentage = min(100, int((new_progress / self.target_value) * 100))
        
        # 检查是否解锁
        if self.status == UserAchievementStatus.LOCKED and new_progress > 0:
            self.status = UserAchievementStatus.IN_PROGRESS
        
        # 检查是否完成
        if new_progress >= self.target_value and self.status != UserAchievementStatus.COMPLETED:
            self.status = UserAchievementStatus.COMPLETED
            self.completed_at = func.now()
        
        self.last_updated_at = func.now()
"""
用户徽章模型定义

记录用户与徽章的关系，包括徽章授予信息
"""

from sqlalchemy import Column, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel


class UserBadge(BaseModel):
    """
    用户徽章模型

    记录用户与徽章的关系，包括徽章授予信息
    """
    __tablename__ = "user_badges"

    # 外键关系
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False, comment="徽章ID")

    # 授予信息
    granted_at = Column(DateTime, nullable=False, default=func.now(), comment="授予时间")
    granted_by = Column(Integer, ForeignKey("users.id"), comment="授予者ID")
    grant_reason = Column(Text, comment="授予原因")

    # 显示信息
    is_equipped = Column(Boolean, default=False, comment="是否装备")
    is_favorite = Column(Boolean, default=False, comment="是否收藏")
    display_order = Column(Integer, default=0, comment="显示顺序")

    # 状态
    is_new = Column(Boolean, default=True, comment="是否为新徽章")
    is_hidden = Column(Boolean, default=False, comment="是否隐藏")

    # 关系
    user = relationship("User", foreign_keys=[user_id], back_populates="user_badges")
    badge = relationship("Badge", back_populates="user_badges")
    granter = relationship("User", foreign_keys=[granted_by])

    # 唯一约束
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

    def __repr__(self):
        return f"<UserBadge(id={self.id}, user_id={self.user_id}, badge_id={self.badge_id})>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "badge_id": self.badge_id,
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
            "granted_by": self.granted_by,
            "grant_reason": self.grant_reason,
            "is_equipped": self.is_equipped,
            "is_favorite": self.is_favorite,
            "display_order": self.display_order,
            "is_new": self.is_new,
            "is_hidden": self.is_hidden,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
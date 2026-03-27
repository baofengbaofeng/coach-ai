"""
成就系统模块模型

定义成就系统的数据模型和业务逻辑
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json

from coding.database.models import (
    Achievement, AchievementType, AchievementDifficulty, AchievementStatus,
    UserAchievement, UserAchievementStatus,
    Badge, BadgeRarity, BadgeType, BadgeStatus,
    UserBadge,
    Reward, RewardType, RewardStatus,
    UserReward, UserRewardStatus
)


class TriggerEventType(Enum):
    """触发事件类型枚举"""
    EXERCISE_COMPLETED = "exercise_completed"  # 运动完成
    TASK_COMPLETED = "task_completed"          # 任务完成
    STREAK_UPDATED = "streak_updated"          # 连续打卡更新
    LEVEL_UP = "level_up"                      # 等级提升
    SOCIAL_INTERACTION = "social_interaction"  # 社交互动
    SYSTEM_EVENT = "system_event"              # 系统事件


class AchievementProgressUpdate:
    """成就进度更新数据类"""
    
    def __init__(
        self,
        user_id: int,
        achievement_id: int,
        progress_delta: int = 1,
        event_type: str = None,
        event_data: Dict[str, Any] = None
    ):
        self.user_id = user_id
        self.achievement_id = achievement_id
        self.progress_delta = progress_delta
        self.event_type = event_type
        self.event_data = event_data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "achievement_id": self.achievement_id,
            "progress_delta": self.progress_delta,
            "event_type": self.event_type,
            "event_data": self.event_data
        }


class AchievementUnlockNotification:
    """成就解锁通知数据类"""
    
    def __init__(
        self,
        user_id: int,
        achievement: Achievement,
        user_achievement: UserAchievement,
        timestamp: datetime = None
    ):
        self.user_id = user_id
        self.achievement = achievement
        self.user_achievement = user_achievement
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "achievement": self.achievement.to_dict(),
            "user_achievement": self.user_achievement.to_dict(),
            "timestamp": self.timestamp.isoformat()
        }


class BadgeGrantNotification:
    """徽章授予通知数据类"""
    
    def __init__(
        self,
        user_id: int,
        badge: Badge,
        user_badge: UserBadge,
        timestamp: datetime = None
    ):
        self.user_id = user_id
        self.badge = badge
        self.user_badge = user_badge
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "badge": self.badge.to_dict(),
            "user_badge": self.user_badge.to_dict(),
            "timestamp": self.timestamp.isoformat()
        }


class RewardClaimNotification:
    """奖励领取通知数据类"""
    
    def __init__(
        self,
        user_id: int,
        reward: Reward,
        user_reward: UserReward,
        timestamp: datetime = None
    ):
        self.user_id = user_id
        self.reward = reward
        self.user_reward = user_reward
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "reward": self.reward.to_dict(),
            "user_reward": self.user_reward.to_dict(),
            "timestamp": self.timestamp.isoformat()
        }


class AchievementStats:
    """成就统计数据类"""
    
    def __init__(
        self,
        total_achievements: int = 0,
        unlocked_achievements: int = 0,
        in_progress_achievements: int = 0,
        locked_achievements: int = 0,
        total_points: int = 0,
        total_badges: int = 0,
        completion_rate: float = 0.0
    ):
        self.total_achievements = total_achievements
        self.unlocked_achievements = unlocked_achievements
        self.in_progress_achievements = in_progress_achievements
        self.locked_achievements = locked_achievements
        self.total_points = total_points
        self.total_badges = total_badges
        self.completion_rate = completion_rate
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_achievements": self.total_achievements,
            "unlocked_achievements": self.unlocked_achievements,
            "in_progress_achievements": self.in_progress_achievements,
            "locked_achievements": self.locked_achievements,
            "total_points": self.total_points,
            "total_badges": self.total_badges,
            "completion_rate": self.completion_rate
        }


class UserAchievementSummary:
    """用户成就摘要数据类"""
    
    def __init__(
        self,
        user_id: int,
        stats: AchievementStats,
        recent_achievements: List[Dict[str, Any]] = None,
        top_achievements: List[Dict[str, Any]] = None,
        badges: List[Dict[str, Any]] = None
    ):
        self.user_id = user_id
        self.stats = stats
        self.recent_achievements = recent_achievements or []
        self.top_achievements = top_achievements or []
        self.badges = badges or []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "stats": self.stats.to_dict(),
            "recent_achievements": self.recent_achievements,
            "top_achievements": self.top_achievements,
            "badges": self.badges
        }
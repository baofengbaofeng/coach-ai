"""
成就领域模块
包含成就、徽章、奖励等核心业务概念
"""

from .value_objects import (
    AchievementType, AchievementDifficulty, AchievementStatus,
    BadgeType, BadgeRarity, RewardType
)
from .entities import Achievement, Badge, Reward, UserAchievement, UserBadge
from .services import AchievementService, BadgeService, RewardService
from .events import (
    AchievementCreatedEvent,
    AchievementUnlockedEvent,
    BadgeEarnedEvent,
    RewardClaimedEvent,
    ProgressUpdatedEvent
)

__all__ = [
    # 值对象
    'AchievementType',
    'AchievementDifficulty',
    'AchievementStatus',
    'BadgeType',
    'BadgeRarity',
    'RewardType',
    
    # 实体
    'Achievement',
    'Badge',
    'Reward',
    'UserAchievement',
    'UserBadge',
    
    # 领域服务
    'AchievementService',
    'BadgeService',
    'RewardService',
    
    # 领域事件
    'AchievementCreatedEvent',
    'AchievementUnlockedEvent',
    'BadgeEarnedEvent',
    'RewardClaimedEvent',
    'ProgressUpdatedEvent',
]
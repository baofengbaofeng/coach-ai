"""
成就系统模块

提供成就、徽章和奖励系统的完整功能
"""

from .handlers import (
    AchievementListHandler,
    AchievementDetailHandler,
    UserAchievementListHandler,
    UserAchievementDetailHandler,
    AchievementProgressHandler,
    UserAchievementStatsHandler,
    AchievementTriggerHandler,
    BadgeGrantHandler,
    RewardClaimHandler,
    UserBadgeListHandler
)
from .analytics_handlers import (
    UserAchievementAnalyticsHandler,
    SystemAchievementAnalyticsHandler,
    AchievementPerformanceMetricsHandler,
    AchievementRecommendationsHandler,
    AchievementTrendAnalysisHandler,
    PopularAchievementsHandler,
    DifficultAchievementsHandler,
    AchievementComparisonHandler
)

__all__ = [
    'AchievementListHandler',
    'AchievementDetailHandler',
    'UserAchievementListHandler',
    'UserAchievementDetailHandler',
    'AchievementProgressHandler',
    'UserAchievementStatsHandler',
    'AchievementTriggerHandler',
    'BadgeGrantHandler',
    'RewardClaimHandler',
    'UserBadgeListHandler',
    'UserAchievementAnalyticsHandler',
    'SystemAchievementAnalyticsHandler',
    'AchievementPerformanceMetricsHandler',
    'AchievementRecommendationsHandler',
    'AchievementTrendAnalysisHandler',
    'PopularAchievementsHandler',
    'DifficultAchievementsHandler',
    'AchievementComparisonHandler'
]
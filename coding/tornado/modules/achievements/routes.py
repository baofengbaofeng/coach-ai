"""
成就系统模块 - 路由配置
定义成就系统相关的API路由
"""

from .handlers import (
    AchievementListHandler, AchievementDetailHandler,
    UserAchievementListHandler, UserAchievementDetailHandler,
    AchievementProgressHandler, UserAchievementStatsHandler,
    AchievementTriggerHandler, BadgeGrantHandler,
    RewardClaimHandler, UserBadgeListHandler
)
from .analytics_handlers import (
    UserAchievementAnalyticsHandler, SystemAchievementAnalyticsHandler,
    AchievementPerformanceMetricsHandler, AchievementRecommendationsHandler,
    AchievementTrendAnalysisHandler, PopularAchievementsHandler,
    DifficultAchievementsHandler, AchievementComparisonHandler
)


def get_achievement_routes():
    """
    获取成就系统模块的路由配置
    
    Returns:
        list: 路由配置列表
    """
    return [
        # 成就管理
        (r"/api/v1/achievements", AchievementListHandler),
        (r"/api/v1/achievements/([^/]+)", AchievementDetailHandler),
        
        # 用户成就
        (r"/api/v1/user-achievements", UserAchievementListHandler),
        (r"/api/v1/user-achievements/([^/]+)", UserAchievementListHandler),
        (r"/api/v1/users/([^/]+)/achievements/([^/]+)", UserAchievementDetailHandler),
        
        # 成就进度
        (r"/api/v1/achievement-progress", AchievementProgressHandler),
        
        # 成就统计
        (r"/api/v1/achievement-stats", UserAchievementStatsHandler),
        (r"/api/v1/users/([^/]+)/achievement-stats", UserAchievementStatsHandler),
        
        # 成就触发
        (r"/api/v1/achievement-trigger", AchievementTriggerHandler),
        
        # 徽章授予
        (r"/api/v1/badge-grant", BadgeGrantHandler),
        
        # 用户徽章
        (r"/api/v1/user-badges", UserBadgeListHandler),
        (r"/api/v1/users/([^/]+)/badges", UserBadgeListHandler),
        
        # 奖励领取
        (r"/api/v1/reward-claim", RewardClaimHandler),
        
        # 成就数据分析
        (r"/api/v1/achievement-analytics/user", UserAchievementAnalyticsHandler),
        (r"/api/v1/achievement-analytics/user/([^/]+)", UserAchievementAnalyticsHandler),
        (r"/api/v1/achievement-analytics/system", SystemAchievementAnalyticsHandler),
        (r"/api/v1/achievement-analytics/performance", AchievementPerformanceMetricsHandler),
        (r"/api/v1/achievement-analytics/recommendations", AchievementRecommendationsHandler),
        (r"/api/v1/achievement-analytics/recommendations/([^/]+)", AchievementRecommendationsHandler),
        (r"/api/v1/achievement-analytics/trend", AchievementTrendAnalysisHandler),
        (r"/api/v1/achievement-analytics/popular", PopularAchievementsHandler),
        (r"/api/v1/achievement-analytics/difficult", DifficultAchievementsHandler),
        (r"/api/v1/achievement-analytics/compare", AchievementComparisonHandler),
    ]
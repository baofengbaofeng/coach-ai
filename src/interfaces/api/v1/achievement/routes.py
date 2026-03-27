"""
成就路由配置
"""

from .handlers import (
    AchievementHandler,
    UserAchievementHandler,
    AchievementProgressHandler,
    UserAchievementStatsHandler,
    AchievementTriggerHandler,
    BadgeHandler,
    UserBadgeHandler,
    RewardHandler
)


def get_achievement_routes():
    """获取成就路由配置"""
    return [
        # 成就管理路由
        (r"/api/v1/achievements", AchievementHandler),
        (r"/api/v1/achievements/([^/]+)", AchievementHandler),
        
        # 用户成就路由
        (r"/api/v1/achievements/user", UserAchievementHandler),
        (r"/api/v1/achievements/user/([^/]+)", UserAchievementHandler),
        
        # 成就进度路由
        (r"/api/v1/achievements/progress", AchievementProgressHandler),
        
        # 用户成就统计路由
        (r"/api/v1/achievements/stats", UserAchievementStatsHandler),
        
        # 成就触发路由
        (r"/api/v1/achievements/trigger", AchievementTriggerHandler),
        
        # 徽章路由
        (r"/api/v1/achievements/badges", BadgeHandler),
        (r"/api/v1/achievements/badges/([^/]+)", BadgeHandler),
        
        # 用户徽章路由
        (r"/api/v1/achievements/user/badges", UserBadgeHandler),
        
        # 奖励路由
        (r"/api/v1/achievements/rewards/claim", RewardHandler),
        (r"/api/v1/achievements/user/rewards", RewardHandler),
    ]
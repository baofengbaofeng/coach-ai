"""
API视图包。
按照豆包AI助手最佳实践：提供类型安全的API视图。
"""

from .ai_views import (
    AIRecommendationView,
    AIAnalysisView,
    AIPredictionView,
    AIAdviceView,
    AIServiceStatusView,
)

from .user_views import (
    UserProfileView,
    UserStatsView,
    UserPreferencesView,
)

from .exercise_views import (
    ExerciseRecordViewSet,
    ExercisePlanViewSet,
    ExerciseAnalysisViewSet,
    ExerciseStatsView,
)

from .task_views import (
    TaskViewSet,
    TaskCategoryViewSet,
    TaskStatsView,
    TaskDashboardView,
)

from .achievement_views import (
    AchievementViewSet,
    UserAchievementViewSet,
    AchievementStatsView,
    AchievementDashboardView,
)

from .common_views import (
    HealthCheckView,
    SystemStatusView,
    APIInfoView,
)


__all__: list[str] = [
    # AI视图
    "AIRecommendationView",
    "AIAnalysisView",
    "AIPredictionView",
    "AIAdviceView",
    "AIServiceStatusView",
    
    # 用户视图
    "UserProfileView",
    "UserStatsView",
    "UserPreferencesView",
    
    # 运动视图
    "ExerciseRecordViewSet",
    "ExercisePlanViewSet",
    "ExerciseAnalysisViewSet",
    "ExerciseStatsView",
    
    # 任务视图
    "TaskViewSet",
    "TaskCategoryViewSet",
    "TaskStatsView",
    "TaskDashboardView",
    
    # 成就视图
    "AchievementViewSet",
    "UserAchievementViewSet",
    "AchievementStatsView",
    "AchievementDashboardView",
    
    # 通用视图
    "HealthCheckView",
    "SystemStatusView",
    "APIInfoView",
]
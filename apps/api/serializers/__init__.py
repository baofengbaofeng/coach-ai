"""
API序列化器包。
按照豆包AI助手最佳实践：提供类型安全的API序列化器。
"""

from .ai_serializers import (
    AIRecommendationRequestSerializer,
    AIRecommendationResponseSerializer,
    AIAnalysisRequestSerializer,
    AIAnalysisResponseSerializer,
    AIPredictionRequestSerializer,
    AIPredictionResponseSerializer,
    AIAdviceRequestSerializer,
    AIAdviceResponseSerializer,
)

from .common_serializers import (
    SuccessResponseSerializer,
    ErrorResponseSerializer,
    PaginationRequestSerializer,
    PaginationResponseSerializer,
    FilterRequestSerializer,
    SortRequestSerializer,
)

from .user_serializers import (
    UserProfileSerializer,
    UserStatsSerializer,
    UserPreferencesSerializer,
)

from .exercise_serializers import (
    ExerciseRecordSerializer,
    ExercisePlanSerializer,
    ExerciseAnalysisSerializer,
    ExerciseStatsSerializer,
)

from .task_serializers import (
    TaskSerializer,
    TaskCategorySerializer,
    TaskStatsSerializer,
    TaskDashboardSerializer,
)

from .achievement_serializers import (
    AchievementSerializer,
    UserAchievementSerializer,
    AchievementStatsSerializer,
    AchievementDashboardSerializer,
)


__all__: list[str] = [
    # AI序列化器
    "AIRecommendationRequestSerializer",
    "AIRecommendationResponseSerializer",
    "AIAnalysisRequestSerializer",
    "AIAnalysisResponseSerializer",
    "AIPredictionRequestSerializer",
    "AIPredictionResponseSerializer",
    "AIAdviceRequestSerializer",
    "AIAdviceResponseSerializer",
    
    # 通用序列化器
    "SuccessResponseSerializer",
    "ErrorResponseSerializer",
    "PaginationRequestSerializer",
    "PaginationResponseSerializer",
    "FilterRequestSerializer",
    "SortRequestSerializer",
    
    # 用户序列化器
    "UserProfileSerializer",
    "UserStatsSerializer",
    "UserPreferencesSerializer",
    
    # 运动序列化器
    "ExerciseRecordSerializer",
    "ExercisePlanSerializer",
    "ExerciseAnalysisSerializer",
    "ExerciseStatsSerializer",
    
    # 任务序列化器
    "TaskSerializer",
    "TaskCategorySerializer",
    "TaskStatsSerializer",
    "TaskDashboardSerializer",
    
    # 成就序列化器
    "AchievementSerializer",
    "UserAchievementSerializer",
    "AchievementStatsSerializer",
    "AchievementDashboardSerializer",
]
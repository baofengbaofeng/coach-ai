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
    
    # 通用视图
    "HealthCheckView",
    "SystemStatusView",
    "APIInfoView",
]
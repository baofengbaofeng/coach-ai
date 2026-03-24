"""
AI服务URL路由配置。
按照豆包AI助手最佳实践：提供类型安全的AI API路由。
"""
from django.urls import path

from apps.api.views.ai_views import (
    AIRecommendationView,
    AIAnalysisView,
    AIPredictionView,
    AIAdviceView,
    AIServiceStatusView,
)


# ==================== AI服务URL模式 ====================
ai_urlpatterns = [
    # AI推荐
    path(
        "ai/recommendation/",
        AIRecommendationView.as_view(),
        name="ai_recommendation",
    ),
    
    # AI分析
    path(
        "ai/analysis/",
        AIAnalysisView.as_view(),
        name="ai_analysis",
    ),
    
    # AI预测
    path(
        "ai/prediction/",
        AIPredictionView.as_view(),
        name="ai_prediction",
    ),
    
    # AI建议
    path(
        "ai/advice/",
        AIAdviceView.as_view(),
        name="ai_advice",
    ),
    
    # AI服务状态
    path(
        "ai/status/",
        AIServiceStatusView.as_view(),
        name="ai_service_status",
    ),
]


__all__: list[str] = [
    "ai_urlpatterns",
]
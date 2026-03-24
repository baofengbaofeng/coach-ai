"""
通用URL路由配置。
按照豆包AI助手最佳实践：提供类型安全的通用API路由。
"""
from django.urls import path

from apps.api.views.common_views import (
    HealthCheckView,
    SystemStatusView,
    APIInfoView,
)


# ==================== 通用URL模式 ====================
common_urlpatterns = [
    # 健康检查
    path(
        "health/",
        HealthCheckView.as_view(),
        name="health_check",
    ),
    
    # 系统状态
    path(
        "status/",
        SystemStatusView.as_view(),
        name="system_status",
    ),
    
    # API信息
    path(
        "info/",
        APIInfoView.as_view(),
        name="api_info",
    ),
]


__all__: list[str] = [
    "common_urlpatterns",
]
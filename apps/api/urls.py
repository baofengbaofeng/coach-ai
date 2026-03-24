"""
API主URL配置。
按照豆包AI助手最佳实践：提供类型安全的API URL配置。
"""
from django.urls import include, path

from apps.api.urls import urlpatterns as api_urlpatterns


# ==================== API URL模式 ====================
urlpatterns = [
    # API v1
    path("api/v1/", include(api_urlpatterns)),
    
    # API文档（未来添加）
    # path("api/docs/", include_docs_urls(title="CoachAI API文档")),
    
    # API信息
    # path("api/info/", APIInfoView.as_view(), name="api_info"),
]


# ==================== 错误处理 ====================
handler400 = "apps.api.views.common_views.bad_request"
handler403 = "apps.api.views.common_views.permission_denied"
handler404 = "apps.api.views.common_views.page_not_found"
handler500 = "apps.api.views.common_views.server_error"


__all__: list[str] = [
    "urlpatterns",
    "handler400",
    "handler403",
    "handler404",
    "handler500",
]
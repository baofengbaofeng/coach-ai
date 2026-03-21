"""
CoachAI 项目 URL 配置主文件，定义项目的所有 URL 路由。
按照豆包AI助手最佳实践：根路由只做分发，不写业务路由。
"""
from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


# ==================== API 文档配置 ====================
# API 文档视图配置：使用 drf-yasg 生成 OpenAPI 规范文档
schema_view = get_schema_view(
    openapi.Info(
        title="CoachAI API",
        default_version="v1",
        description="CoachAI 智能伴读AI系统 API 文档，提供完整的接口说明和测试功能。",
        terms_of_service="https://www.coachai.com/terms/",
        contact=openapi.Contact(email="contact@coachai.com"),
        license=openapi.License(name="GPL v3 License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


# ==================== URL 模式定义 ====================
# URL 模式定义：按功能模块组织路由，确保路由清晰和可维护性
# 豆包最佳实践：根路由只做分发，业务路由写在各自 app 内
urlpatterns = [
    # 根路径重定向：将根路径重定向到 API 文档页面，便于用户快速访问文档
    path("", RedirectView.as_view(url="/swagger/", permanent=False)),
    
    # Django 管理界面：提供后台管理功能，仅限管理员访问
    path("admin/", admin.site.urls),
    
    # API 文档页面：提供 Swagger UI 和 ReDoc 两种文档界面
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    
    # 认证相关 API：处理用户注册、登录、登出和令牌刷新等认证功能
    path("api/v1/auth/", include("accounts.urls")),
    
    # 作业管理 API：处理作业上传、批改、查询和统计等作业相关功能
    path("api/v1/homework/", include("homework.urls")),
    
    # 运动管理 API：处理运动记录、实时计数、数据统计和姿势评估等运动相关功能
    path("api/v1/exercise/", include("exercise.urls")),
    
    # 任务管理 API：处理任务创建、提醒、进度跟踪和成就计算等任务相关功能
    path("api/v1/tasks/", include("tasks.urls")),
    
    # 成就系统 API：处理成就解锁、进度跟踪和奖励发放等功能
    path("api/v1/achievements/", include("achievements.urls")),
    
    # 公共 API：处理文件上传、系统状态检查和公共配置等通用功能
    path("api/v1/common/", include("common.urls")),
    
    # 健康检查端点：用于监控系统健康状态
    path("health/", include("health_check.urls")),
]


# ==================== 开发环境特殊配置 ====================
# 开发环境特殊配置：启用静态文件和媒体文件服务，便于开发调试
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # 开发环境添加调试工具栏路由，提供详细的请求分析和性能监控
    try:
        import debug_toolbar  # noqa: F401

        urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
    except ImportError:
        pass

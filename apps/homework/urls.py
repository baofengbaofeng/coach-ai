"""
作业管理URL配置模块，定义作业相关API的路由规则。
按照豆包AI助手最佳实践：每个应用有自己的URL配置。
"""
from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.homework.views import HomeworkViewSet, KnowledgePointViewSet, QuestionViewSet


# ==================== 路由器配置 ====================
router: DefaultRouter = DefaultRouter()

# 注册知识点视图集
router.register(r"knowledge-points", KnowledgePointViewSet, basename="knowledge-point")

# 注册题目视图集
router.register(r"questions", QuestionViewSet, basename="question")

# 注册作业视图集
router.register(r"homeworks", HomeworkViewSet, basename="homework")


# ==================== URL模式 ====================
urlpatterns: list = [
    # API路由
    path("api/", include(router.urls)),
    
    # 作业统计API（独立端点）
    path(
        "api/homeworks/statistics/",
        HomeworkViewSet.as_view({"get": "statistics"}),
        name="homework-statistics",
    ),
    
    # 题目统计API（独立端点）
    path(
        "api/questions/statistics/",
        QuestionViewSet.as_view({"get": "statistics"}),
        name="question-statistics",
    ),
]

# ==================== 应用命名空间 ====================
app_name: str = "homework"
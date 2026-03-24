"""
运动管理URL配置模块，定义运动相关的API路由。
按照豆包AI助手最佳实践：使用Django REST Framework路由配置。
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.exercise.views import (
    ExerciseAnalysisViewSet,
    ExercisePlanViewSet,
    ExerciseRecordViewSet,
)


# ==================== 路由器配置 ====================
router = DefaultRouter()
router.register(r"records", ExerciseRecordViewSet, basename="exercise-record")
router.register(r"plans", ExercisePlanViewSet, basename="exercise-plan")
router.register(r"analyses", ExerciseAnalysisViewSet, basename="exercise-analysis")

app_name = "exercise"

urlpatterns = [
    path("", include(router.urls)),
]
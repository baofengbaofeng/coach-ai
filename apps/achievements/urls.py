"""
成就系统URL配置模块。
按照豆包AI助手最佳实践：使用Django URL配置。
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.achievements.views import (
    AchievementCategoryViewSet,
    AchievementRewardViewSet,
    AchievementStatisticViewSet,
    AchievementViewSet,
    UserAchievementViewSet,
)


# ==================== REST Framework 路由器 ====================
router = DefaultRouter()
router.register(r"categories", AchievementCategoryViewSet, basename="achievementcategory")
router.register(r"achievements", AchievementViewSet, basename="achievement")
router.register(r"user-achievements", UserAchievementViewSet, basename="userachievement")
router.register(r"rewards", AchievementRewardViewSet, basename="achievementreward")
router.register(r"statistics", AchievementStatisticViewSet, basename="achievementstatistic")

app_name = "achievements"

urlpatterns = [
    path("api/", include(router.urls)),
]
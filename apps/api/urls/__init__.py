"""
API URL路由包。
按照豆包AI助手最佳实践：提供类型安全的URL路由配置。
"""

from .ai_urls import ai_urlpatterns
from .user_urls import user_urlpatterns
from .exercise_urls import exercise_urlpatterns
from .task_urls import task_urlpatterns
from .achievement_urls import achievement_urlpatterns
from .common_urls import common_urlpatterns


# ==================== 合并所有URL模式 ====================
urlpatterns = (
    ai_urlpatterns +
    user_urlpatterns +
    exercise_urlpatterns +
    task_urlpatterns +
    achievement_urlpatterns +
    common_urlpatterns
)


__all__: list[str] = [
    "urlpatterns",
    "ai_urlpatterns",
    "user_urlpatterns",
    "exercise_urlpatterns",
    "task_urlpatterns",
    "achievement_urlpatterns",
    "common_urlpatterns",
]
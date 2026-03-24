"""
API应用配置。
按照豆包AI助手最佳实践：提供类型安全的API应用配置。
"""
from __future__ import annotations

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    API应用配置类。
    """
    
    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "apps.api"
    verbose_name: str = "API接口层"
    
    def ready(self) -> None:
        """
        应用就绪时调用，用于信号注册等初始化操作。
        """
        # 导入信号处理器
        try:
            from apps.api import signals  # noqa: F401
        except ImportError:
            pass
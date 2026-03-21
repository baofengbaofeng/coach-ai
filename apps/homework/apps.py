"""
作业管理应用配置模块，定义Django应用的配置参数和初始化逻辑。
"""
from __future__ import annotations

from django.apps import AppConfig


class HomeworkConfig(AppConfig):
    """
    作业管理应用配置类。
    """
    
    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "homework"
    verbose_name: str = "作业管理"
    
    def ready(self) -> None:
        """
        应用就绪回调函数。
        """
        pass
"""
任务管理应用配置模块，定义Django应用的配置参数和初始化逻辑。
"""
from __future__ import annotations

from django.apps import AppConfig


class TasksConfig(AppConfig):
    """
    任务管理应用配置类。
    """
    
    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "tasks"
    verbose_name: str = "任务管理"
    
    def ready(self) -> None:
        """
        应用就绪回调函数。
        """
        pass
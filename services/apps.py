"""
AI服务层应用配置模块，定义Django应用的配置参数和初始化逻辑。
按照豆包AI助手最佳实践：提供类型安全的AI服务配置。
"""
from __future__ import annotations

import logging

from django.apps import AppConfig


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


class ServicesConfig(AppConfig):
    """
    AI服务层应用配置类。
    """
    
    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "services"
    verbose_name: str = "AI服务层"
    
    def ready(self) -> None:
        """
        应用就绪回调函数，初始化AI服务。
        """
        _LOGGER.info("AI服务层初始化完成")
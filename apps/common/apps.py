"""
公共应用配置模块，定义Django应用的配置参数和初始化逻辑。
"""
from __future__ import annotations

import logging

from django.apps import AppConfig


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


class CommonConfig(AppConfig):
    """
    公共应用配置类。
    """
    
    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "apps.common"
    verbose_name: str = "公共模块"
    
    def ready(self) -> None:
        """
        应用就绪回调函数，注册信号处理器。
        """
        # 导入信号处理器
        try:
            from apps.common import signals
            
            _LOGGER.info("公共模块信号处理器已注册")
        except ImportError as e:
            _LOGGER.warning("导入信号处理器失败: %s", str(e))
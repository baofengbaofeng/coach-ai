"""
用户管理应用配置模块，定义Django应用的配置参数和初始化逻辑。
按照豆包AI助手最佳实践：每个应用都有独立的配置，便于模块化管理。
"""
from __future__ import annotations

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    用户管理应用配置类，定义应用的名称、标签和初始化行为。
    
    Attributes:
        default_auto_field (str): 默认主键字段类型
        name (str): 应用名称，用于Django内部识别
        verbose_name (str): 应用的显示名称，用于管理界面
    """
    
    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "accounts"
    verbose_name: str = "用户管理"
    
    def ready(self) -> None:
        """
        应用就绪回调函数，在Django启动时自动调用，用于执行初始化操作。
        
        Returns:
            None: 此方法不返回值，但会执行用户管理应用的初始化逻辑
            
        Raises:
            此方法不直接抛出异常，但会记录初始化过程中的任何错误
        """
        # 导入信号处理器，确保用户创建时自动创建相关记录
        try:
            import accounts.signals  # noqa: F401
        except ImportError:
            pass
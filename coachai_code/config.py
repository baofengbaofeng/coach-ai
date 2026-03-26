"""
配置文件模块 - 向后兼容层
使用新的配置管理系统
"""

import warnings
from config import init_config, get_config

# 初始化配置
config = init_config()

# 发出弃用警告
warnings.warn(
    "直接导入config模块已弃用，请使用from config import get_config",
    DeprecationWarning,
    stacklevel=2
)

# 导出所有配置属性以便向后兼容
__all__ = ['config']
"""
任务管理应用包初始化文件，提供任务创建、提醒、进度跟踪和完成统计功能。
按照豆包AI助手最佳实践：业务逻辑写在 services.py，视图层只做参数接收和响应返回。
"""
from __future__ import annotations


__version__: str = "0.1.0"
__description__: str = "CoachAI 任务管理模块，处理任务创建、提醒设置、进度跟踪和完成统计"
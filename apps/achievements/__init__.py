"""
成就系统应用包初始化文件，提供成就定义、解锁条件、进度跟踪和奖励发放功能。
按照豆包AI助手最佳实践：业务逻辑写在 services.py，视图层只做参数接收和响应返回。
"""
from __future__ import annotations


__version__: str = "0.1.0"
__description__: str = "CoachAI 成就系统模块，处理成就定义、解锁条件、进度跟踪和奖励发放"
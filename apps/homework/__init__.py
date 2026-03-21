"""
作业管理应用包初始化文件，提供作业上传、批改、查询和统计功能。
按照豆包AI助手最佳实践：业务逻辑写在 services.py，视图层只做参数接收和响应返回。
"""
from __future__ import annotations


__version__: str = "0.1.0"
__description__: str = "CoachAI 作业管理模块，处理作业上传、OCR识别、智能批改和结果分析"
"""
用户管理应用包初始化文件，提供用户注册、登录、认证、个人资料管理和权限控制功能。
按照豆包AI助手最佳实践：业务逻辑写在 services.py，视图层只做参数接收和响应返回。
"""
from __future__ import annotations


__version__: str = "0.1.0"
__description__: str = "CoachAI 用户管理模块，处理用户认证、授权和个人资料管理"
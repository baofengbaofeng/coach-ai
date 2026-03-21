"""
Django 设置包初始化文件，用于管理不同环境下的配置设置，包括开发、测试和生产环境配置。
"""
from __future__ import annotations


__all__: list[str] = ["base", "dev", "prod", "testing"]

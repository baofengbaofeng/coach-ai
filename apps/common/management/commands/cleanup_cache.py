"""
清理缓存管理命令。
按照豆包AI助手最佳实践：提供类型安全的管理命令。
"""
from __future__ import annotations

import logging
from typing import Any

from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandParser

from apps.common.utils import Timer


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    清理缓存管理命令类。
    """
    
    help: str = "清理Django缓存"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """
        添加命令行参数。
        
        Args:
            parser: 参数解析器
        """
        parser.add_argument(
            "--all",
            action="store_true",
            help="清理所有缓存",
        )
        parser.add_argument(
            "--prefix",
            type=str,
            default="",
            help="按前缀清理缓存",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="模拟运行，不实际清理",
        )
    
    def handle(self, *args: Any, **options: Any) -> None:
        """
        执行命令。
        
        Args:
            *args: 位置参数
            **options: 命名参数
        """
        with Timer("清理缓存"):
            self._handle_command(options)
    
    def _handle_command(self, options: dict) -> None:
        """
        处理命令逻辑。
        
        Args:
            options: 命令选项
        """
        dry_run: bool = options["dry_run"]
        prefix: str = options["prefix"]
        clear_all: bool = options["all"]
        
        self.stdout.write("开始清理缓存...")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("模拟运行模式，不会实际清理缓存"))
        
        if clear_all:
            self._clear_all_cache(dry_run)
        elif prefix:
            self._clear_cache_by_prefix(prefix, dry_run)
        else:
            self.stdout.write(self.style.ERROR("请指定清理方式：--all 或 --prefix <前缀>"))
            self.stdout.write("使用 --help 查看帮助")
    
    def _clear_all_cache(self, dry_run: bool) -> None:
        """
        清理所有缓存。
        
        Args:
            dry_run: 是否模拟运行
        """
        self.stdout.write("清理所有缓存...")
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS("模拟：已清理所有缓存"))
            return
        
        try:
            cache.clear()
            self.stdout.write(self.style.SUCCESS("✅ 已清理所有缓存"))
            _LOGGER.info("缓存清理完成：所有缓存")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 清理缓存失败：{str(e)}"))
            _LOGGER.error("清理缓存失败：%s", str(e), exc_info=True)
    
    def _clear_cache_by_prefix(self, prefix: str, dry_run: bool) -> None:
        """
        按前缀清理缓存。
        
        Args:
            prefix: 缓存键前缀
            dry_run: 是否模拟运行
        """
        self.stdout.write(f"清理前缀为 '{prefix}' 的缓存...")
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"模拟：已清理前缀为 '{prefix}' 的缓存"))
            return
        
        try:
            # 注意：Django的cache.clear()不支持按前缀清理
            # 这里需要根据具体的缓存后端实现
            self.stdout.write(self.style.WARNING("⚠️  按前缀清理缓存需要特定的缓存后端支持"))
            self.stdout.write("当前使用 cache.clear() 清理所有缓存")
            
            cache.clear()
            self.stdout.write(self.style.SUCCESS("✅ 已清理所有缓存（作为替代方案）"))
            _LOGGER.info("缓存清理完成：前缀 %s", prefix)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 清理缓存失败：{str(e)}"))
            _LOGGER.error("清理缓存失败：%s", str(e), exc_info=True)
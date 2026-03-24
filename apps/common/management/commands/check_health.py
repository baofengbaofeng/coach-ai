"""
检查系统健康状态管理命令。
按照豆包AI助手最佳实践：提供类型安全的管理命令。
"""
from __future__ import annotations

import logging
import os
import platform
import sys
from datetime import datetime
from typing import Any, Dict, List

import django
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.db import connection, connections
from django.db.utils import OperationalError

from apps.common.utils import Timer


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    检查系统健康状态管理命令类。
    """
    
    help: str = "检查系统健康状态"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """
        添加命令行参数。
        
        Args:
            parser: 参数解析器
        """
        parser.add_argument(
            "--detailed",
            action="store_true",
            help="显示详细健康信息",
        )
        parser.add_argument(
            "--check",
            type=str,
            choices=["all", "database", "cache", "storage", "dependencies"],
            default="all",
            help="指定检查项目",
        )
    
    def handle(self, *args: Any, **options: Any) -> None:
        """
        执行命令。
        
        Args:
            *args: 位置参数
            **options: 命名参数
        """
        with Timer("健康检查"):
            self._handle_command(options)
    
    def _handle_command(self, options: dict) -> None:
        """
        处理命令逻辑。
        
        Args:
            options: 命令选项
        """
        detailed: bool = options["detailed"]
        check_type: str = options["check"]
        
        self.stdout.write("开始系统健康检查...")
        self.stdout.write("=" * 50)
        
        # 收集健康信息
        health_info: Dict[str, Any] = self._collect_health_info(check_type, detailed)
        
        # 显示健康信息
        self._display_health_info(health_info, detailed)
        
        # 总结
        self.stdout.write("=" * 50)
        self._display_summary(health_info)
    
    def _collect_health_info(self, check_type: str, detailed: bool) -> Dict[str, Any]:
        """
        收集健康信息。
        
        Args:
            check_type: 检查类型
            detailed: 是否详细
            
        Returns:
            健康信息字典
        """
        health_info: Dict[str, Any] = {
            "timestamp": datetime.now(),
            "system": {},
            "django": {},
            "checks": {},
        }
        
        # 系统信息
        if check_type in ["all", "dependencies"]:
            health_info["system"] = self._get_system_info(detailed)
        
        # Django信息
        if check_type in ["all", "dependencies"]:
            health_info["django"] = self._get_django_info(detailed)
        
        # 数据库检查
        if check_type in ["all", "database"]:
            health_info["checks"]["database"] = self._check_database(detailed)
        
        # 缓存检查
        if check_type in ["all", "cache"]:
            health_info["checks"]["cache"] = self._check_cache(detailed)
        
        # 存储检查
        if check_type in ["all", "storage"]:
            health_info["checks"]["storage"] = self._check_storage(detailed)
        
        return health_info
    
    def _get_system_info(self, detailed: bool) -> Dict[str, Any]:
        """
        获取系统信息。
        
        Args:
            detailed: 是否详细
            
        Returns:
            系统信息字典
        """
        system_info: Dict[str, Any] = {
            "platform": platform.platform(),
            "python_version": sys.version,
            "python_path": sys.executable,
        }
        
        if detailed:
            system_info.update({
                "processor": platform.processor(),
                "machine": platform.machine(),
                "node": platform.node(),
                "cwd": os.getcwd(),
            })
        
        return system_info
    
    def _get_django_info(self, detailed: bool) -> Dict[str, Any]:
        """
        获取Django信息。
        
        Args:
            detailed: 是否详细
            
        Returns:
            Django信息字典
        """
        django_info: Dict[str, Any] = {
            "version": django.get_version(),
            "settings_module": settings.SETTINGS_MODULE,
            "debug": settings.DEBUG,
            "installed_apps_count": len(settings.INSTALLED_APPS),
        }
        
        if detailed:
            django_info.update({
                "database_engine": settings.DATABASES["default"]["ENGINE"],
                "time_zone": settings.TIME_ZONE,
                "language_code": settings.LANGUAGE_CODE,
                "static_root": settings.STATIC_ROOT,
                "media_root": settings.MEDIA_ROOT,
            })
        
        return django_info
    
    def _check_database(self, detailed: bool) -> Dict[str, Any]:
        """
        检查数据库。
        
        Args:
            detailed: 是否详细
            
        Returns:
            数据库检查结果
        """
        result: Dict[str, Any] = {
            "status": "unknown",
            "message": "",
            "details": {},
        }
        
        try:
            # 测试默认数据库连接
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                row = cursor.fetchone()
                
                if row and row[0] == 1:
                    result["status"] = "healthy"
                    result["message"] = "数据库连接正常"
                else:
                    result["status"] = "unhealthy"
                    result["message"] = "数据库查询异常"
            
            # 获取数据库信息
            if detailed:
                with connection.cursor() as cursor:
                    # 获取数据库版本
                    cursor.execute("SELECT sqlite_version()")
                    db_version = cursor.fetchone()
                    
                    # 获取表数量
                    cursor.execute("""
                        SELECT COUNT(*) FROM sqlite_master 
                        WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    """)
                    table_count = cursor.fetchone()
                    
                    result["details"] = {
                        "database_version": db_version[0] if db_version else "unknown",
                        "table_count": table_count[0] if table_count else 0,
                    }
        
        except OperationalError as e:
            result["status"] = "unhealthy"
            result["message"] = f"数据库连接失败：{str(e)}"
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"数据库检查异常：{str(e)}"
        
        return result
    
    def _check_cache(self, detailed: bool) -> Dict[str, Any]:
        """
        检查缓存。
        
        Args:
            detailed: 是否详细
            
        Returns:
            缓存检查结果
        """
        result: Dict[str, Any] = {
            "status": "unknown",
            "message": "",
            "details": {},
        }
        
        try:
            from django.core.cache import cache
            
            # 测试缓存
            test_key = "health_check_test"
            test_value = "test_value"
            
            # 设置缓存
            cache.set(test_key, test_value, 10)
            
            # 获取缓存
            retrieved_value = cache.get(test_key)
            
            if retrieved_value == test_value:
                result["status"] = "healthy"
                result["message"] = "缓存功能正常"
            else:
                result["status"] = "unhealthy"
                result["message"] = "缓存功能异常"
            
            # 清理测试缓存
            cache.delete(test_key)
            
            if detailed:
                result["details"] = {
                    "cache_backend": settings.CACHES["default"]["BACKEND"],
                }
        
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"缓存检查异常：{str(e)}"
        
        return result
    
    def _check_storage(self, detailed: bool) -> Dict[str, Any]:
        """
        检查存储。
        
        Args:
            detailed: 是否详细
            
        Returns:
            存储检查结果
        """
        result: Dict[str, Any] = {
            "status": "unknown",
            "message": "",
            "details": {},
        }
        
        try:
            # 检查静态文件目录
            static_root = settings.STATIC_ROOT
            media_root = settings.MEDIA_ROOT
            
            checks: List[Dict[str, Any]] = []
            
            # 检查静态文件目录
            if static_root:
                static_exists = os.path.exists(static_root)
                static_writable = os.access(static_root, os.W_OK) if static_exists else False
                
                checks.append({
                    "name": "静态文件目录",
                    "path": static_root,
                    "exists": static_exists,
                    "writable": static_writable,
                })
            
            # 检查媒体文件目录
            if media_root:
                media_exists = os.path.exists(media_root)
                media_writable = os.access(media_root, os.W_OK) if media_exists else False
                
                checks.append({
                    "name": "媒体文件目录",
                    "path": media_root,
                    "exists": media_exists,
                    "writable": media_writable,
                })
            
            # 评估状态
            all_healthy = all(check["exists"] and check["writable"] for check in checks)
            
            if all_healthy:
                result["status"] = "healthy"
                result["message"] = "存储目录正常"
            else:
                result["status"] = "unhealthy"
                result["message"] = "存储目录存在问题"
            
            if detailed:
                result["details"]["checks"] = checks
        
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"存储检查异常：{str(e)}"
        
        return result
    
    def _display_health_info(self, health_info: Dict[str, Any], detailed: bool) -> None:
        """
        显示健康信息。
        
        Args:
            health_info: 健康信息字典
            detailed: 是否详细
        """
        # 显示时间戳
        timestamp = health_info["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        self.stdout.write(f"检查时间: {timestamp}")
        self.stdout.write("")
        
        # 显示系统信息
        if health_info["system"]:
            self.stdout.write(self.style.MIGRATE_HEADING("系统信息:"))
            for key, value in health_info["system"].items():
                self.stdout.write(f"  {key}: {value}")
            self.stdout.write("")
        
        # 显示Django信息
        if health_info["django"]:
            self.stdout.write(self.style.MIGRATE_HEADING("Django信息:"))
            for key, value in health_info["django"].items():
                self.stdout.write(f"  {key}: {value}")
            self.stdout.write("")
        
        # 显示检查结果
        if health_info["checks"]:
            self.stdout.write(self.style.MIGRATE_HEADING("检查结果:"))
            
            for check_name, check_result in health_info["checks"].items():
                status = check_result["status"]
                message = check_result["message"]
                
                if status == "healthy":
                    status_display = self.style.SUCCESS("✅ 健康")
                elif status == "unhealthy":
                    status_display = self.style.ERROR("❌ 不健康")
                elif status == "error":
                    status_display = self.style.WARNING("⚠️  错误")
                else:
                    status_display = self.style.NOTICE("❓ 未知")
                
                self.stdout.write(f"  {check_name.capitalize()}: {status_display}")
                self.stdout.write(f"    消息: {message}")
                
                if detailed and check_result.get("details"):
                    self.stdout.write("    详情:")
                    for detail_key, detail_value in check_result["details"].items():
                        self.stdout.write(f"      {detail_key}: {detail_value}")
                
                self.stdout.write("")
    
    def _display_summary(self, health_info: Dict[str, Any]) -> None:
        """
        显示总结。
        
        Args:
            health_info: 健康信息字典
        """
        # 统计状态
        check_results = health_info.get("checks", {})
        
        if not check_results:
            self.stdout.write(self.style.WARNING("⚠️  未执行任何检查"))
            return
        
        healthy_count = 0
        unhealthy_count = 0
        error_count = 0
        
        for check_result in check_results.values():
            status = check_result["status"]
            
            if status == "healthy":
                healthy_count += 1
            elif status == "unhealthy":
                unhealthy_count += 1
            elif status == "error":
                error_count += 1
        
        total_count = len(check_results)
        
        # 显示统计
        self.stdout.write(self.style.MIGRATE_HEADING("检查统计:"))
        self.stdout.write(f"  总计: {total_count}")
        self.stdout.write(f"  健康: {healthy_count}")
        self.stdout.write(f"  不健康: {unhealthy_count}")
        self.stdout.write(f"  错误: {error_count}")
        
        # 显示总体状态
        if unhealthy_count == 0 and error_count == 0:
            self.stdout.write(self.style.SUCCESS("\n🎉 所有检查项目健康！"))
        elif unhealthy_count > 0:
            self.stdout.write(self.style.ERROR(f"\n⚠️  发现 {unhealthy_count} 个不健康项目"))
        elif error_count > 0:
            self.stdout.write(self.style.WARNING(f"\n⚠️  发现 {error_count} 个错误"))
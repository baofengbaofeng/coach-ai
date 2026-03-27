"""
数据库迁移管理器
提供数据库迁移、回滚、状态检查等功能
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from loguru import logger

from coding.config import config


class MigrationManager:
    """数据库迁移管理器"""
    
    def __init__(self):
        """初始化迁移管理器"""
        self.project_root = Path(__file__).parent.parent.parent
        self.migration_dir = self.project_root / "code" / "database" / "migrations"
        self.alembic_ini = self.migration_dir / "alembic.ini"
        
        # 设置环境变量
        os.environ["DATABASE_URL"] = config.DATABASE_URL
        
    def _run_alembic_command(self, command: str, args: Optional[List[str]] = None) -> bool:
        """运行Alembic命令
        
        Args:
            command: Alembic命令（如：upgrade, downgrade, revision等）
            args: 额外参数
            
        Returns:
            bool: 命令是否成功执行
        """
        try:
            cmd = [
                sys.executable, "-m", "alembic",
                "-c", str(self.alembic_ini),
                command
            ]
            
            if args:
                cmd.extend(args)
            
            logger.info(f"Running Alembic command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout:
                logger.info(f"Alembic output:\n{result.stdout}")
            if result.stderr:
                logger.warning(f"Alembic stderr:\n{result.stderr}")
                
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Alembic command failed: {e}")
            if e.stdout:
                logger.error(f"Stdout:\n{e.stdout}")
            if e.stderr:
                logger.error(f"Stderr:\n{e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Failed to run Alembic command: {e}")
            return False
    
    def init_migration(self) -> bool:
        """初始化迁移环境（如果尚未初始化）
        
        Returns:
            bool: 是否成功
        """
        try:
            # 检查是否已初始化
            if self.alembic_ini.exists():
                logger.info("Migration environment already initialized")
                return True
                
            # 创建迁移目录
            self.migration_dir.mkdir(parents=True, exist_ok=True)
            
            # 使用Alembic初始化
            cmd = [
                sys.executable, "-m", "alembic",
                "init",
                "-t", "generic",
                str(self.migration_dir)
            ]
            
            logger.info(f"Initializing migration environment: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout:
                logger.info(f"Init output:\n{result.stdout}")
                
            # 替换env.py文件
            env_file = self.migration_dir / "env.py"
            if env_file.exists():
                env_file.unlink()
                
            # 复制我们自定义的env.py
            source_env = Path(__file__).parent / "migrations" / "env.py"
            if source_env.exists():
                import shutil
                shutil.copy2(source_env, env_file)
                logger.info("Custom env.py copied")
                
            logger.info("Migration environment initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize migration environment: {e}")
            return False
    
    def create_migration(self, message: str, autogenerate: bool = True) -> bool:
        """创建新的迁移脚本
        
        Args:
            message: 迁移描述
            autogenerate: 是否自动检测模型变化
            
        Returns:
            bool: 是否成功
        """
        args = ["-m", message]
        
        if autogenerate:
            args.append("--autogenerate")
            
        return self._run_alembic_command("revision", args)
    
    def upgrade(self, revision: str = "head") -> bool:
        """升级数据库到指定版本
        
        Args:
            revision: 目标版本（默认为最新版本）
            
        Returns:
            bool: 是否成功
        """
        return self._run_alembic_command("upgrade", [revision])
    
    def downgrade(self, revision: str = "-1") -> bool:
        """降级数据库到指定版本
        
        Args:
            revision: 目标版本（默认为上一个版本）
            
        Returns:
            bool: 是否成功
        """
        return self._run_alembic_command("downgrade", [revision])
    
    def current(self) -> Optional[str]:
        """获取当前数据库版本
        
        Returns:
            Optional[str]: 当前版本号，失败返回None
        """
        try:
            cmd = [
                sys.executable, "-m", "alembic",
                "-c", str(self.alembic_ini),
                "current"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                if lines:
                    # 提取版本号（格式：版本号 (revision)）
                    for line in lines:
                        if line.strip():
                            parts = line.split()
                            if parts:
                                return parts[0]
            return None
            
        except Exception as e:
            logger.error(f"Failed to get current version: {e}")
            return None
    
    def history(self) -> Optional[List[Dict[str, Any]]]:
        """获取迁移历史
        
        Returns:
            Optional[List[Dict[str, Any]]]: 迁移历史列表，失败返回None
        """
        try:
            cmd = [
                sys.executable, "-m", "alembic",
                "-c", str(self.alembic_ini),
                "history"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout:
                history = []
                lines = result.stdout.strip().split('\n')
                
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('Rev:'):
                        # 解析格式：版本号 -> 版本号 (head), 2026-03-29 09:00:00, 创建初始表结构
                        parts = line.split(',', 2)
                        if len(parts) >= 3:
                            rev_part = parts[0].strip()
                            date_part = parts[1].strip()
                            desc_part = parts[2].strip()
                            
                            # 提取版本号
                            rev = rev_part.split('->')[0].strip().split()[0]
                            
                            history.append({
                                'revision': rev,
                                'date': date_part,
                                'description': desc_part
                            })
                
                return history
            return None
            
        except Exception as e:
            logger.error(f"Failed to get migration history: {e}")
            return None
    
    def check_pending(self) -> bool:
        """检查是否有待应用的迁移
        
        Returns:
            bool: 是否有待应用的迁移
        """
        current = self.current()
        history = self.history()
        
        if not history:
            return False
            
        # 获取最新版本
        latest = history[0]['revision'] if history else None
        
        return current != latest
    
    def reset(self, confirm: bool = False) -> bool:
        """重置数据库（删除所有表并重新迁移）
        
        Args:
            confirm: 需要确认
            
        Returns:
            bool: 是否成功
        """
        if not confirm:
            logger.warning("Reset requires confirmation. Use confirm=True to proceed.")
            return False
            
        try:
            # 降级到基础版本
            logger.warning("Dropping all tables...")
            if not self._run_alembic_command("downgrade", ["base"]):
                return False
                
            # 重新升级到最新版本
            logger.info("Recreating all tables...")
            return self.upgrade("head")
            
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            return False
    
    def seed_database(self) -> bool:
        """运行数据库种子脚本
        
        Returns:
            bool: 是否成功
        """
        try:
            from database.seeds.initial_data import run_seeds
            return run_seeds()
        except ImportError as e:
            logger.error(f"Failed to import seed module: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to seed database: {e}")
            return False


# 创建全局实例
migration_manager = MigrationManager()


def init_database() -> bool:
    """初始化数据库（创建表并插入初始数据）
    
    Returns:
        bool: 是否成功
    """
    logger.info("Initializing database...")
    
    # 初始化迁移环境
    if not migration_manager.init_migration():
        logger.error("Failed to initialize migration environment")
        return False
    
    # 升级到最新版本
    if not migration_manager.upgrade("head"):
        logger.error("Failed to upgrade database")
        return False
    
    # 运行种子脚本
    if not migration_manager.seed_database():
        logger.error("Failed to seed database")
        return False
    
    logger.info("Database initialized successfully")
    return True


def check_database_status() -> Dict[str, Any]:
    """检查数据库状态
    
    Returns:
        Dict[str, Any]: 状态信息
    """
    status = {
        'initialized': migration_manager.alembic_ini.exists(),
        'current_version': migration_manager.current(),
        'has_pending_migrations': False,
        'migration_history': [],
        'database_url': config.DATABASE_URL
    }
    
    if status['initialized']:
        status['has_pending_migrations'] = migration_manager.check_pending()
        status['migration_history'] = migration_manager.history() or []
    
    return status


if __name__ == "__main__":
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Migration Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # init命令
    init_parser = subparsers.add_parser("init", help="Initialize database")
    
    # upgrade命令
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database")
    upgrade_parser.add_argument("revision", nargs="?", default="head", help="Target revision")
    
    # downgrade命令
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database")
    downgrade_parser.add_argument("revision", nargs="?", default="-1", help="Target revision")
    
    # create命令
    create_parser = subparsers.add_parser("create", help="Create migration")
    create_parser.add_argument("message", help="Migration message")
    
    # status命令
    status_parser = subparsers.add_parser("status", help="Check database status")
    
    # history命令
    history_parser = subparsers.add_parser("history", help="Show migration history")
    
    # seed命令
    seed_parser = subparsers.add_parser("seed", help="Seed database with initial data")
    
    # reset命令（需要确认）
    reset_parser = subparsers.add_parser("reset", help="Reset database (DANGEROUS)")
    reset_parser.add_argument("--confirm", action="store_true", help="Confirm reset")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 执行命令
    if args.command == "init":
        success = init_database()
    elif args.command == "upgrade":
        success = migration_manager.upgrade(args.revision)
    elif args.command == "downgrade":
        success = migration_manager.downgrade(args.revision)
    elif args.command == "create":
        success = migration_manager.create_migration(args.message)
    elif args.command == "status":
        status = check_database_status()
        print("Database Status:")
        print(f"  Initialized: {status['initialized']}")
        print(f"  Current Version: {status['current_version']}")
        print(f"  Pending Migrations: {status['has_pending_migrations']}")
        print(f"  Database URL: {status['database_url']}")
        if status['migration_history']:
            print("\nMigration History:")
            for item in status['migration_history']:
                print(f"  {item['revision']}: {item['description']} ({item['date']})")
        success = True
    elif args.command == "history":
        history = migration_manager.history()
        if history:
            print("Migration History:")
            for item in history:
                print(f"  {item['revision']}: {item['description']} ({item['date']})")
        else:
            print("No migration history found")
        success = True
    elif args.command == "seed":
        success = migration_manager.seed_database()
    elif args.command == "reset":
        success = migration_manager.reset(args.confirm)
    else:
        print(f"Unknown command: {args.command}")
        success = False
    
    sys.exit(0 if success else 1)
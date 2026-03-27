"""
数据库迁移包
管理数据库表结构的创建和更新
"""

import logging
from alembic import command
from alembic.config import Config
from pathlib import Path

logger = logging.getLogger(__name__)


def init_migrations():
    """
    初始化数据库迁移配置
    """
    try:
        # 创建alembic.ini配置文件
        alembic_cfg = Config()
        alembic_cfg.set_main_option("script_location", "database/migrations")
        alembic_cfg.set_main_option("sqlalchemy.url", "mysql://user:password@localhost/coach_ai")
        alembic_cfg.set_main_option("version_locations", "database/migrations/versions")
        
        # 创建版本目录
        versions_dir = Path(__file__).parent / "versions"
        versions_dir.mkdir(exist_ok=True)
        
        logger.info("Database migrations initialized")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize migrations: {e}")
        return False


def create_tables():
    """
    创建所有数据库表
    """
    try:
        from database.connection import engine
        from database.models import Base
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        logger.info("All database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        return False


def drop_tables():
    """
    删除所有数据库表（谨慎使用！）
    """
    try:
        from database.connection import engine
        from database.models import Base
        
        # 删除所有表
        Base.metadata.drop_all(bind=engine)
        
        logger.warning("All database tables dropped")
        return True
    except Exception as e:
        logger.error(f"Failed to drop tables: {e}")
        return False


def check_tables():
    """
    检查数据库表是否存在
    """
    try:
        from sqlalchemy import inspect
        from database.connection import engine
        from database.models import Base
        
        # 检查表是否存在
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        required_tables = Base.metadata.tables.keys()
        
        missing_tables = []
        for table in required_tables:
            if table not in existing_tables:
                missing_tables.append(table)
        
        if missing_tables:
            logger.warning(f"Missing tables: {missing_tables}")
            return False, missing_tables
        else:
            logger.info("All required tables exist")
            return True, []
            
    except Exception as e:
        logger.error(f"Failed to check tables: {e}")
        return False, [str(e)]
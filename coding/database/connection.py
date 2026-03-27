"""
数据库连接管理器
管理MySQL数据库连接池和多租户连接
"""

import threading
from contextlib import contextmanager
from typing import Dict, Optional, Generator
from loguru import logger
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session

from config import config


class DatabaseConnectionManager:
    """数据库连接管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._engines: Dict[str, Engine] = {}
                    cls._instance._session_factories: Dict[str, scoped_session] = {}
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化连接管理器"""
        if not hasattr(self, "_initialized") or not self._initialized:
            self._engines = {}
            self._session_factories = {}
            self._initialized = True
    
    def get_engine(self, tenant_id: Optional[str] = None) -> Engine:
        """
        获取数据库引擎
        
        Args:
            tenant_id: 租户ID，为None时使用默认租户
            
        Returns:
            SQLAlchemy引擎实例
        """
        tenant_key = tenant_id or config.DEFAULT_TENANT_ID
        
        if tenant_key not in self._engines:
            with self._lock:
                if tenant_key not in self._engines:
                    # 创建数据库引擎
                    engine = create_engine(
                        config.DATABASE_URL,
                        pool_size=config.DB_POOL_SIZE,
                        max_overflow=config.DB_MAX_OVERFLOW,
                        pool_pre_ping=True,  # 连接前ping检查
                        pool_recycle=3600,  # 连接回收时间（秒）
                        echo=config.APP_DEBUG,  # 调试模式下输出SQL
                        future=True  # 使用SQLAlchemy 2.0风格
                    )
                    self._engines[tenant_key] = engine
                    logger.info(f"Database engine created for tenant: {tenant_key}")
        
        return self._engines[tenant_key]
    
    def get_session_factory(self, tenant_id: Optional[str] = None) -> scoped_session:
        """
        获取会话工厂
        
        Args:
            tenant_id: 租户ID，为None时使用默认租户
            
        Returns:
            scoped_session工厂
        """
        tenant_key = tenant_id or config.DEFAULT_TENANT_ID
        
        if tenant_key not in self._session_factories:
            with self._lock:
                if tenant_key not in self._session_factories:
                    engine = self.get_engine(tenant_key)
                    session_factory = sessionmaker(
                        bind=engine,
                        autocommit=False,
                        autoflush=False,
                        expire_on_commit=False,
                        class_=Session,
                        future=True
                    )
                    # 使用scoped_session确保线程安全
                    scoped_session_factory = scoped_session(session_factory)
                    self._session_factories[tenant_key] = scoped_session_factory
                    logger.info(f"Session factory created for tenant: {tenant_key}")
        
        return self._session_factories[tenant_key]
    
    @contextmanager
    def get_session(self, tenant_id: Optional[str] = None) -> Generator[Session, None, None]:
        """
        获取数据库会话（上下文管理器）
        
        Args:
            tenant_id: 租户ID，为None时使用默认租户
            
        Yields:
            SQLAlchemy会话实例
        """
        session_factory = self.get_session_factory(tenant_id)
        session = session_factory()
        
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            # 记录错误日志（英文）
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
            session_factory.remove()
    
    def close_all(self) -> None:
        """关闭所有数据库连接"""
        with self._lock:
            for tenant_key, engine in self._engines.items():
                try:
                    engine.dispose()
                    logger.info(f"Database engine disposed for tenant: {tenant_key}")
                except Exception as e:
                    logger.error(f"Error disposing engine for tenant {tenant_key}: {e}")
            
            self._engines.clear()
            self._session_factories.clear()
            logger.info("All database connections closed")


# 全局数据库连接管理器实例
db_manager = DatabaseConnectionManager()


def get_db_session(tenant_id: Optional[str] = None) -> Generator[Session, None, None]:
    """
    获取数据库会话的便捷函数
    
    Args:
        tenant_id: 租户ID，为None时使用默认租户
        
    Yields:
        SQLAlchemy会话实例
    """
    with db_manager.get_session(tenant_id) as session:
        yield session


def init_database() -> None:
    """初始化数据库连接"""
    # 测试数据库连接
    try:
        with db_manager.get_session() as session:
            # 执行简单的查询测试连接
            session.execute("SELECT 1")
        logger.info("Database connection test successful")
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        raise


def close_database() -> None:
    """关闭数据库连接"""
    db_manager.close_all()
    logger.info("Database connections closed")
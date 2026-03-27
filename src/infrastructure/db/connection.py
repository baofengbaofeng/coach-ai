"""
数据库连接管理器（DDD迁移版）
管理MySQL数据库连接池和多租户连接
"""

import threading
from contextlib import contextmanager
from typing import Dict, Optional, Generator
from loguru import logger
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session

from src.settings import settings


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
        if not self._initialized:
            self._initialized = True
            self._init_connections()
    
    def _init_connections(self) -> None:
        """初始化数据库连接"""
        try:
            # 主数据库连接
            main_engine = self._create_engine(settings.DATABASE_URL)
            self._engines['main'] = main_engine
            self._session_factories['main'] = scoped_session(
                sessionmaker(bind=main_engine, autocommit=False, autoflush=False)
            )
            
            logger.info("Database connection manager initialized")
            logger.info(f"Database URL: {settings.DATABASE_URL}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connections: {e}")
            raise
    
    def _create_engine(self, database_url: str) -> Engine:
        """
        创建数据库引擎
        
        Args:
            database_url: 数据库连接URL
            
        Returns:
            数据库引擎
        """
        return create_engine(
            database_url,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_pre_ping=settings.DB_POOL_PRE_PING,
            echo=settings.APP_DEBUG,  # 调试模式下输出SQL
            echo_pool=settings.APP_DEBUG,
            future=True
        )
    
    def get_engine(self, tenant_id: Optional[str] = None) -> Engine:
        """
        获取数据库引擎
        
        Args:
            tenant_id: 租户ID，如果为None则返回主引擎
            
        Returns:
            数据库引擎
        """
        key = tenant_id or 'main'
        
        if key not in self._engines:
            # 这里可以实现多租户数据库连接
            # 暂时返回主引擎
            return self._engines['main']
        
        return self._engines[key]
    
    def get_session(self, tenant_id: Optional[str] = None) -> Session:
        """
        获取数据库会话
        
        Args:
            tenant_id: 租户ID，如果为None则返回主会话
            
        Returns:
            数据库会话
        """
        key = tenant_id or 'main'
        
        if key not in self._session_factories:
            # 这里可以实现多租户会话工厂
            # 暂时返回主会话工厂
            factory = self._session_factories['main']
        else:
            factory = self._session_factories[key]
        
        return factory()
    
    @contextmanager
    def get_db_session(self, tenant_id: Optional[str] = None) -> Generator[Session, None, None]:
        """
        获取数据库会话上下文管理器
        
        Args:
            tenant_id: 租户ID
            
        Yields:
            数据库会话
            
        Example:
            with db_manager.get_db_session() as session:
                # 使用session进行数据库操作
                pass
        """
        session = self.get_session(tenant_id)
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def close_all(self) -> None:
        """关闭所有数据库连接"""
        for key, engine in self._engines.items():
            try:
                engine.dispose()
                logger.debug(f"Closed database engine: {key}")
            except Exception as e:
                logger.error(f"Failed to close database engine {key}: {e}")
        
        self._engines.clear()
        self._session_factories.clear()
        self._initialized = False
        logger.info("All database connections closed")
    
    def health_check(self) -> Dict[str, Any]:
        """
        数据库健康检查
        
        Returns:
            健康状态信息
        """
        try:
            with self.get_db_session() as session:
                # 执行简单查询检查连接
                result = session.execute("SELECT 1").scalar()
                
                return {
                    'status': 'healthy' if result == 1 else 'unhealthy',
                    'message': 'Database connection is working',
                    'engines_count': len(self._engines),
                    'session_factories_count': len(self._session_factories)
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': str(e),
                'engines_count': len(self._engines),
                'session_factories_count': len(self._session_factories)
            }


# 全局数据库连接管理器实例
db_manager = DatabaseConnectionManager()


def get_db_session(tenant_id: Optional[str] = None) -> Generator[Session, None, None]:
    """
    获取数据库会话的便捷函数
    
    Args:
        tenant_id: 租户ID
        
    Yields:
        数据库会话
    """
    return db_manager.get_db_session(tenant_id)


def init_database() -> DatabaseConnectionManager:
    """
    初始化数据库连接
    
    Returns:
        数据库连接管理器实例
    """
    return db_manager


def close_database() -> None:
    """关闭数据库连接"""
    db_manager.close_all()


# 导出
__all__ = [
    'DatabaseConnectionManager',
    'db_manager',
    'get_db_session',
    'init_database',
    'close_database'
]


if __name__ == "__main__":
    # 测试数据库连接
    try:
        manager = init_database()
        print("Database connection manager initialized")
        
        # 测试健康检查
        health = manager.health_check()
        print(f"Database health: {health}")
        
        # 测试会话
        with manager.get_db_session() as session:
            result = session.execute("SELECT 1").scalar()
            print(f"Test query result: {result}")
        
        close_database()
        print("Database connections closed")
        
    except Exception as e:
        print(f"Database test failed: {e}")
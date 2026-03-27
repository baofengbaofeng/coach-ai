"""
数据库连接模块
提供MySQL数据库连接池和会话管理
"""

import contextlib
from typing import Generator, Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import QueuePool
from loguru import logger

from ..settings import config


class DatabaseManager:
    """数据库管理器"""
    
    _engine: Optional[Engine] = None
    _session_factory: Optional[sessionmaker] = None
    
    @classmethod
    def init_db(cls) -> None:
        """初始化数据库连接"""
        if cls._engine is not None:
            logger.warning("数据库已经初始化")
            return
        
        try:
            # 创建数据库引擎
            cls._engine = create_engine(
                config.DATABASE_URL,
                poolclass=QueuePool,
                pool_size=config.DB_POOL_SIZE,
                max_overflow=config.DB_MAX_OVERFLOW,
                pool_recycle=config.DB_POOL_RECYCLE,
                pool_pre_ping=config.DB_POOL_PRE_PING,
                echo=config.APP_DEBUG,  # 调试模式下输出SQL
                future=True,
            )
            
            # 创建会话工厂
            cls._session_factory = sessionmaker(
                bind=cls._engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
                class_=Session,
            )
            
            logger.info(f"数据库连接初始化成功: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
            
        except Exception as e:
            logger.error(f"数据库连接初始化失败: {e}")
            raise
    
    @classmethod
    def get_engine(cls) -> Engine:
        """获取数据库引擎"""
        if cls._engine is None:
            cls.init_db()
        return cls._engine
    
    @classmethod
    def get_session_factory(cls) -> sessionmaker:
        """获取会话工厂"""
        if cls._session_factory is None:
            cls.init_db()
        return cls._session_factory
    
    @classmethod
    @contextlib.contextmanager
    def get_db_session(cls) -> Generator[Session, None, None]:
        """
        获取数据库会话上下文管理器
        
        Yields:
            数据库会话实例
        """
        session_factory = cls.get_session_factory()
        session = session_factory()
        
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库会话异常: {e}")
            raise
        finally:
            session.close()
    
    @classmethod
    def create_scoped_session(cls) -> scoped_session:
        """
        创建作用域会话（用于Web请求）
        
        Returns:
            作用域会话
        """
        session_factory = cls.get_session_factory()
        return scoped_session(session_factory)
    
    @classmethod
    def close_all_sessions(cls) -> None:
        """关闭所有数据库会话"""
        if cls._engine:
            cls._engine.dispose()
            logger.info("数据库连接已关闭")
    
    @classmethod
    def health_check(cls) -> bool:
        """
        数据库健康检查
        
        Returns:
            是否健康
        """
        try:
            with cls.get_db_session() as session:
                # 执行简单查询测试连接
                session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False
    
    @classmethod
    def get_stats(cls) -> dict:
        """
        获取数据库统计信息
        
        Returns:
            统计信息字典
        """
        if cls._engine is None:
            return {"status": "not_initialized"}
        
        try:
            pool = cls._engine.pool
            return {
                "status": "healthy",
                "pool_size": pool.size(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "checkedin": pool.checkedin(),
                "connections": pool.checkedout() + pool.checkedin(),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }


# 全局数据库管理器实例
db_manager = DatabaseManager()


def init_database() -> None:
    """初始化数据库（应用启动时调用）"""
    db_manager.init_db()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话（简化版）
    
    Yields:
        数据库会话实例
    """
    with db_manager.get_db_session() as session:
        yield session


def get_db_session() -> Session:
    """
    获取数据库会话（非上下文管理器版）
    
    Returns:
        数据库会话实例
    """
    return db_manager.get_session_factory()()


if __name__ == "__main__":
    # 测试数据库连接
    init_database()
    
    # 健康检查
    if db_manager.health_check():
        print("✅ 数据库连接正常")
        
        # 获取统计信息
        stats = db_manager.get_stats()
        print(f"数据库统计: {stats}")
    else:
        print("❌ 数据库连接失败")
    
    # 关闭连接
    db_manager.close_all_sessions()
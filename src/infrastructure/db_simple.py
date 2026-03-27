"""
简化数据库连接模块
避免SQLAlchemy兼容性问题
"""

import contextlib
from typing import Generator, Optional, Any, Dict
import mysql.connector
from mysql.connector import pooling
from mysql.connector.errors import Error as MySQLError
from loguru import logger

import sys
import os

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import settings

config = settings.config


class SimpleDatabaseManager:
    """简化数据库管理器（使用mysql-connector-python）"""
    
    _pool: Optional[pooling.MySQLConnectionPool] = None
    
    @classmethod
    def init_db(cls) -> None:
        """初始化数据库连接池"""
        if cls._pool is not None:
            logger.warning("数据库已经初始化")
            return
        
        try:
            # 创建连接池配置
            pool_config = {
                "pool_name": "coach_ai_pool",
                "pool_size": config.DB_POOL_SIZE,
                "pool_reset_session": True,
                "host": config.DB_HOST,
                "port": config.DB_PORT,
                "database": config.DB_NAME,
                "user": config.DB_USER,
                "password": config.DB_PASSWORD,
                "charset": config.DB_CHARSET,
                "autocommit": False,
            }
            
            # 创建连接池
            cls._pool = pooling.MySQLConnectionPool(**pool_config)
            
            logger.info(f"数据库连接池初始化成功: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
            
        except MySQLError as e:
            logger.error(f"数据库连接池初始化失败: {e}")
            raise
    
    @classmethod
    def get_pool(cls) -> pooling.MySQLConnectionPool:
        """获取连接池"""
        if cls._pool is None:
            cls.init_db()
        return cls._pool
    
    @classmethod
    @contextlib.contextmanager
    def get_connection(cls) -> Generator[mysql.connector.MySQLConnection, None, None]:
        """
        获取数据库连接上下文管理器
        
        Yields:
            数据库连接
        """
        pool = cls.get_pool()
        connection = pool.get_connection()
        
        try:
            yield connection
            connection.commit()
        except MySQLError as e:
            connection.rollback()
            logger.error(f"数据库操作异常: {e}")
            raise
        finally:
            connection.close()
    
    @classmethod
    @contextlib.contextmanager
    def get_cursor(cls, dictionary: bool = True) -> Generator[mysql.connector.cursor.MySQLCursor, None, None]:
        """
        获取数据库游标上下文管理器
        
        Args:
            dictionary: 是否返回字典格式结果
            
        Yields:
            数据库游标
        """
        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=dictionary)
            
            try:
                yield cursor
            finally:
                cursor.close()
    
    @classmethod
    def execute_query(cls, query: str, params: Optional[tuple] = None) -> list:
        """
        执行查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        with cls.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    @classmethod
    def execute_update(cls, query: str, params: Optional[tuple] = None) -> int:
        """
        执行更新
        
        Args:
            query: SQL更新语句
            params: 更新参数
            
        Returns:
            影响的行数
        """
        with cls.get_cursor(dictionary=False) as cursor:
            cursor.execute(query, params or ())
            return cursor.rowcount
    
    @classmethod
    def execute_many(cls, query: str, params_list: list) -> int:
        """
        批量执行
        
        Args:
            query: SQL语句
            params_list: 参数列表
            
        Returns:
            影响的总行数
        """
        with cls.get_cursor(dictionary=False) as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    @classmethod
    def health_check(cls) -> bool:
        """
        数据库健康检查
        
        Returns:
            是否健康
        """
        try:
            with cls.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None and result.get("1") == 1
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """
        获取数据库统计信息
        
        Returns:
            统计信息字典
        """
        if cls._pool is None:
            return {"status": "not_initialized"}
        
        try:
            return {
                "status": "healthy",
                "pool_name": cls._pool.pool_name,
                "pool_size": cls._pool.pool_size,
                "connections": len(cls._pool._cnx_queue) if hasattr(cls._pool, '_cnx_queue') else 0,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    @classmethod
    def close_all_connections(cls) -> None:
        """关闭所有数据库连接"""
        if cls._pool:
            # mysql-connector-python的连接池会自动管理
            logger.info("数据库连接池已标记为关闭")
            cls._pool = None


# 全局数据库管理器实例
db_manager = SimpleDatabaseManager()


def init_database() -> None:
    """初始化数据库（应用启动时调用）"""
    db_manager.init_db()


def get_db() -> Generator[mysql.connector.MySQLConnection, None, None]:
    """
    获取数据库连接（简化版）
    
    Yields:
        数据库连接
    """
    with db_manager.get_connection() as connection:
        yield connection


if __name__ == "__main__":
    # 测试数据库连接
    init_database()
    
    # 健康检查
    if db_manager.health_check():
        print("✅ 数据库连接正常")
        
        # 获取统计信息
        stats = db_manager.get_stats()
        print(f"数据库统计: {stats}")
        
        # 测试查询
        try:
            results = db_manager.execute_query("SELECT VERSION() as version")
            print(f"MySQL版本: {results[0]['version']}")
        except Exception as e:
            print(f"查询测试失败: {e}")
    else:
        print("❌ 数据库连接失败")
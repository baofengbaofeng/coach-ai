"""
Redis客户端管理器
管理Redis连接池
"""

import threading
from typing import Optional
from loguru import logger
import redis

from coding.config import config


class RedisClientManager:
    """Redis客户端管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._clients = {}
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化Redis客户端管理器"""
        if not hasattr(self, "_initialized") or not self._initialized:
            self._clients = {}
            self._initialized = True
    
    def get_client(self, db: Optional[int] = None) -> redis.Redis:
        """
        获取Redis客户端
        
        Args:
            db: Redis数据库编号，为None时使用配置中的DB
            
        Returns:
            Redis客户端实例
        """
        db_key = db if db is not None else config.REDIS_DB
        
        if db_key not in self._clients:
            with self._lock:
                if db_key not in self._clients:
                    # 创建Redis连接池
                    connection_pool = redis.ConnectionPool(
                        host=config.REDIS_HOST,
                        port=config.REDIS_PORT,
                        password=config.REDIS_PASSWORD,
                        db=db_key,
                        decode_responses=True,  # 自动解码响应
                        max_connections=20,  # 最大连接数
                        socket_connect_timeout=5,  # 连接超时
                        socket_timeout=5,  # 读写超时
                        retry_on_timeout=True  # 超时重试
                    )
                    
                    # 创建Redis客户端
                    client = redis.Redis(connection_pool=connection_pool)
                    self._clients[db_key] = client
                    logger.info(f"Redis client created for DB: {db_key}")
        
        return self._clients[db_key]
    
    def test_connection(self, db: Optional[int] = None) -> bool:
        """
        测试Redis连接
        
        Args:
            db: Redis数据库编号
            
        Returns:
            连接是否成功
        """
        try:
            client = self.get_client(db)
            # 执行PING命令测试连接
            result = client.ping()
            if result:
                logger.info(f"Redis connection test successful for DB: {db or config.REDIS_DB}")
                return True
            else:
                logger.error(f"Redis PING failed for DB: {db or config.REDIS_DB}")
                return False
        except Exception as e:
            logger.error(f"Redis connection test failed: {e}")
            return False
    
    def close_all(self) -> None:
        """关闭所有Redis连接"""
        with self._lock:
            for db_key, client in self._clients.items():
                try:
                    client.connection_pool.disconnect()
                    logger.info(f"Redis connection closed for DB: {db_key}")
                except Exception as e:
                    logger.error(f"Error closing Redis connection for DB {db_key}: {e}")
            
            self._clients.clear()
            logger.info("All Redis connections closed")


# 全局Redis客户端管理器实例
redis_manager = RedisClientManager()


def get_redis_client(db: Optional[int] = None) -> redis.Redis:
    """
    获取Redis客户端的便捷函数
    
    Args:
        db: Redis数据库编号
        
    Returns:
        Redis客户端实例
    """
    return redis_manager.get_client(db)


def init_redis() -> bool:
    """
    初始化Redis连接
    
    Returns:
        初始化是否成功
    """
    try:
        if redis_manager.test_connection():
            logger.info("Redis connection initialized successfully")
            return True
        else:
            logger.error("Redis connection test failed")
            return False
    except Exception as e:
        logger.error(f"Redis initialization failed: {e}")
        return False


def close_redis() -> None:
    """关闭Redis连接"""
    redis_manager.close_all()
    logger.info("Redis connections closed")


# Redis工具函数
class RedisTools:
    """Redis工具类"""
    
    @staticmethod
    def set_with_expire(client: redis.Redis, key: str, value: str, expire_seconds: int = 3600) -> bool:
        """
        设置键值对并设置过期时间
        
        Args:
            client: Redis客户端
            key: 键名
            value: 值
            expire_seconds: 过期时间（秒）
            
        Returns:
            操作是否成功
        """
        try:
            result = client.setex(key, expire_seconds, value)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis setex error: {e}")
            return False
    
    @staticmethod
    def get_json(client: redis.Redis, key: str) -> Optional[dict]:
        """
        获取JSON格式的值
        
        Args:
            client: Redis客户端
            key: 键名
            
        Returns:
            JSON字典或None
        """
        try:
            value = client.get(key)
            if value:
                import json
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get JSON error: {e}")
            return None
    
    @staticmethod
    def set_json(client: redis.Redis, key: str, value: dict, expire_seconds: int = 3600) -> bool:
        """
        设置JSON格式的值
        
        Args:
            client: Redis客户端
            key: 键名
            value: JSON字典
            expire_seconds: 过期时间（秒）
            
        Returns:
            操作是否成功
        """
        try:
            import json
            json_str = json.dumps(value)
            return RedisTools.set_with_expire(client, key, json_str, expire_seconds)
        except Exception as e:
            logger.error(f"Redis set JSON error: {e}")
            return False
    
    @staticmethod
    def delete_pattern(client: redis.Redis, pattern: str) -> int:
        """
        删除匹配模式的所有键
        
        Args:
            client: Redis客户端
            pattern: 键名模式
            
        Returns:
            删除的键数量
        """
        try:
            keys = client.keys(pattern)
            if keys:
                return client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis delete pattern error: {e}")
            return 0
    
    @staticmethod
    def increment_with_limit(client: redis.Redis, key: str, limit: int, expire_seconds: int = 3600) -> Optional[int]:
        """
        递增计数器，但不超过限制
        
        Args:
            client: Redis客户端
            key: 键名
            limit: 最大值限制
            expire_seconds: 过期时间（秒）
            
        Returns:
            递增后的值或None（如果超过限制）
        """
        try:
            # 使用Lua脚本保证原子性
            lua_script = """
            local current = redis.call('GET', KEYS[1])
            if current and tonumber(current) >= tonumber(ARGV[1]) then
                return nil
            end
            
            local new_value = redis.call('INCR', KEYS[1])
            if new_value == 1 then
                redis.call('EXPIRE', KEYS[1], ARGV[2])
            end
            
            return new_value
            """
            
            result = client.eval(lua_script, 1, key, limit, expire_seconds)
            return result if result is not None else None
        except Exception as e:
            logger.error(f"Redis increment with limit error: {e}")
            return None
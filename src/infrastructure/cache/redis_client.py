"""
Redis客户端管理器（DDD迁移版）
管理Redis连接池和缓存操作
"""

import threading
import json
from typing import Any, Optional, Dict, List, Union
from datetime import timedelta
from loguru import logger
import redis

from src.settings import settings


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
                    cls._instance._clients: Dict[str, redis.Redis] = {}
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化Redis客户端管理器"""
        if not self._initialized:
            self._initialized = True
            self._init_clients()
    
    def _init_clients(self) -> None:
        """初始化Redis客户端"""
        try:
            # 主Redis客户端
            main_client = self._create_client(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB
            )
            self._clients['main'] = main_client
            
            # 测试连接
            main_client.ping()
            
            logger.info("Redis client manager initialized")
            logger.info(f"Redis connection: {settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis clients: {e}")
            raise
    
    def _create_client(self, host: str, port: int, password: Optional[str] = None, db: int = 0) -> redis.Redis:
        """
        创建Redis客户端
        
        Args:
            host: Redis主机
            port: Redis端口
            password: Redis密码
            db: Redis数据库
            
        Returns:
            Redis客户端
        """
        return redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=True,  # 自动解码响应
            socket_connect_timeout=5,  # 连接超时
            socket_timeout=5,  # 读写超时
            retry_on_timeout=True,  # 超时重试
            max_connections=settings.REDIS_MAX_CONNECTIONS
        )
    
    def get_client(self, name: str = 'main') -> redis.Redis:
        """
        获取Redis客户端
        
        Args:
            name: 客户端名称
            
        Returns:
            Redis客户端
        """
        if name not in self._clients:
            raise ValueError(f"Redis client '{name}' not found")
        
        return self._clients[name]
    
    def set(self, key: str, value: Any, expire: Optional[int] = None, prefix: str = '') -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒）
            prefix: 键前缀
            
        Returns:
            是否设置成功
        """
        try:
            full_key = f"{settings.CACHE_KEY_PREFIX}:{prefix}:{key}" if prefix else f"{settings.CACHE_KEY_PREFIX}:{key}"
            
            # 序列化值
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value)
            else:
                value_str = str(value)
            
            client = self.get_client()
            if expire:
                return client.setex(full_key, expire, value_str)
            else:
                return client.set(full_key, value_str)
                
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False
    
    def get(self, key: str, default: Any = None, prefix: str = '') -> Any:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            default: 默认值
            prefix: 键前缀
            
        Returns:
            缓存值或默认值
        """
        try:
            full_key = f"{settings.CACHE_KEY_PREFIX}:{prefix}:{key}" if prefix else f"{settings.CACHE_KEY_PREFIX}:{key}"
            
            client = self.get_client()
            value = client.get(full_key)
            
            if value is None:
                return default
            
            # 尝试反序列化JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
                
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return default
    
    def delete(self, key: str, prefix: str = '') -> bool:
        """
        删除缓存键
        
        Args:
            key: 缓存键
            prefix: 键前缀
            
        Returns:
            是否删除成功
        """
        try:
            full_key = f"{settings.CACHE_KEY_PREFIX}:{prefix}:{key}" if prefix else f"{settings.CACHE_KEY_PREFIX}:{key}"
            
            client = self.get_client()
            return client.delete(full_key) > 0
                
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False
    
    def exists(self, key: str, prefix: str = '') -> bool:
        """
        检查缓存键是否存在
        
        Args:
            key: 缓存键
            prefix: 键前缀
            
        Returns:
            是否存在
        """
        try:
            full_key = f"{settings.CACHE_KEY_PREFIX}:{prefix}:{key}" if prefix else f"{settings.CACHE_KEY_PREFIX}:{key}"
            
            client = self.get_client()
            return client.exists(full_key) > 0
                
        except Exception as e:
            logger.error(f"Failed to check cache key {key}: {e}")
            return False
    
    def expire(self, key: str, seconds: int, prefix: str = '') -> bool:
        """
        设置缓存过期时间
        
        Args:
            key: 缓存键
            seconds: 过期时间（秒）
            prefix: 键前缀
            
        Returns:
            是否设置成功
        """
        try:
            full_key = f"{settings.CACHE_KEY_PREFIX}:{prefix}:{key}" if prefix else f"{settings.CACHE_KEY_PREFIX}:{key}"
            
            client = self.get_client()
            return client.expire(full_key, seconds)
                
        except Exception as e:
            logger.error(f"Failed to expire cache key {key}: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1, prefix: str = '') -> Optional[int]:
        """
        递增缓存值
        
        Args:
            key: 缓存键
            amount: 递增数量
            prefix: 键前缀
            
        Returns:
            递增后的值，失败返回None
        """
        try:
            full_key = f"{settings.CACHE_KEY_PREFIX}:{prefix}:{key}" if prefix else f"{settings.CACHE_KEY_PREFIX}:{key}"
            
            client = self.get_client()
            return client.incrby(full_key, amount)
                
        except Exception as e:
            logger.error(f"Failed to increment cache key {key}: {e}")
            return None
    
    def decrement(self, key: str, amount: int = 1, prefix: str = '') -> Optional[int]:
        """
        递减缓存值
        
        Args:
            key: 缓存键
            amount: 递减数量
            prefix: 键前缀
            
        Returns:
            递减后的值，失败返回None
        """
        try:
            full_key = f"{settings.CACHE_KEY_PREFIX}:{prefix}:{key}" if prefix else f"{settings.CACHE_KEY_PREFIX}:{key}"
            
            client = self.get_client()
            return client.decrby(full_key, amount)
                
        except Exception as e:
            logger.error(f"Failed to decrement cache key {key}: {e}")
            return None
    
    def keys(self, pattern: str = '*') -> List[str]:
        """
        获取匹配模式的键列表
        
        Args:
            pattern: 匹配模式
            
        Returns:
            键列表
        """
        try:
            full_pattern = f"{settings.CACHE_KEY_PREFIX}:{pattern}"
            
            client = self.get_client()
            return client.keys(full_pattern)
                
        except Exception as e:
            logger.error(f"Failed to get keys with pattern {pattern}: {e}")
            return []
    
    def flush_db(self) -> bool:
        """
        清空当前数据库
        
        Returns:
            是否清空成功
        """
        try:
            client = self.get_client()
            client.flushdb()
            logger.info("Redis database flushed")
            return True
                
        except Exception as e:
            logger.error(f"Failed to flush Redis database: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Redis健康检查
        
        Returns:
            健康状态信息
        """
        try:
            client = self.get_client()
            client.ping()
            
            info = client.info()
            
            return {
                'status': 'healthy',
                'message': 'Redis connection is working',
                'version': info.get('redis_version'),
                'used_memory': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'clients_count': len(self._clients)
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': str(e),
                'clients_count': len(self._clients)
            }
    
    def close_all(self) -> None:
        """关闭所有Redis连接"""
        for name, client in self._clients.items():
            try:
                client.close()
                logger.debug(f"Closed Redis client: {name}")
            except Exception as e:
                logger.error(f"Failed to close Redis client {name}: {e}")
        
        self._clients.clear()
        self._initialized = False
        logger.info("All Redis connections closed")


# 全局Redis客户端管理器实例
redis_manager = RedisClientManager()


def get_redis_client(name: str = 'main') -> redis.Redis:
    """
    获取Redis客户端的便捷函数
    
    Args:
        name: 客户端名称
        
    Returns:
        Redis客户端
    """
    return redis_manager.get_client(name)


def init_redis() -> RedisClientManager:
    """
    初始化Redis连接
    
    Returns:
        Redis客户端管理器实例
    """
    return redis_manager


def close_redis() -> None:
    """关闭Redis连接"""
    redis_manager.close_all()


# 导出
__all__ = [
    'RedisClientManager',
    'redis_manager',
    'get_redis_client',
    'init_redis',
    'close_redis'
]


if __name__ == "__main__":
    # 测试Redis连接
    try:
        manager = init_redis()
        print("Redis client manager initialized")
        
        # 测试健康检查
        health = manager.health_check()
        print(f"Redis health: {health}")
        
        # 测试基本操作
        manager.set('test_key', 'test_value', expire=10)
        value = manager.get('test_key')
        print(f"Test get value: {value}")
        
        exists = manager.exists('test_key')
        print(f"Test key exists: {exists}")
        
        manager.delete('test_key')
        print("Test key deleted")
        
        close_redis()
        print("Redis connections closed")
        
    except Exception as e:
        print(f"Redis test failed: {e}")
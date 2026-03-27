"""
Redis客户端模块
提供Redis连接池和缓存操作
"""

import json
import pickle
from typing import Any, Optional, Union, List, Dict
from redis import Redis, ConnectionPool
from redis.exceptions import RedisError
from loguru import logger

from ..settings import config


class RedisClient:
    """Redis客户端"""
    
    _pool: Optional[ConnectionPool] = None
    _client: Optional[Redis] = None
    
    def __init__(self):
        self._init_pool()
    
    def _init_pool(self) -> None:
        """初始化连接池"""
        if self._pool is not None:
            return
        
        try:
            self._pool = ConnectionPool(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                password=config.REDIS_PASSWORD,
                db=config.REDIS_DB,
                max_connections=config.REDIS_MAX_CONNECTIONS,
                decode_responses=True,  # 自动解码为字符串
                health_check_interval=30,  # 健康检查间隔
            )
            
            logger.info(f"Redis连接池初始化成功: {config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_DB}")
            
        except Exception as e:
            logger.error(f"Redis连接池初始化失败: {e}")
            raise
    
    @property
    def client(self) -> Redis:
        """获取Redis客户端实例"""
        if self._client is None:
            if self._pool is None:
                self._init_pool()
            self._client = Redis(connection_pool=self._pool)
        return self._client
    
    def ping(self) -> bool:
        """
        Ping Redis服务器
        
        Returns:
            是否连接正常
        """
        try:
            return self.client.ping()
        except RedisError as e:
            logger.error(f"Redis Ping失败: {e}")
            return False
    
    # ====================== 字符串操作 ======================
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """
        设置键值
        
        Args:
            key: 键名
            value: 值（自动序列化）
            ex: 过期时间（秒）
            
        Returns:
            是否成功
        """
        try:
            # 自动序列化
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            elif not isinstance(value, str):
                serialized_value = str(value)
            else:
                serialized_value = value
            
            if ex:
                return self.client.set(key, serialized_value, ex=ex)
            else:
                return self.client.set(key, serialized_value)
                
        except RedisError as e:
            logger.error(f"Redis SET失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取键值
        
        Args:
            key: 键名
            default: 默认值
            
        Returns:
            值（自动反序列化）
        """
        try:
            value = self.client.get(key)
            if value is None:
                return default
            
            # 尝试JSON反序列化
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # 如果不是JSON，返回原始字符串
                return value
                
        except RedisError as e:
            logger.error(f"Redis GET失败: {e}")
            return default
    
    def delete(self, *keys: str) -> int:
        """
        删除键
        
        Args:
            *keys: 要删除的键名
            
        Returns:
            删除的键数量
        """
        try:
            return self.client.delete(*keys)
        except RedisError as e:
            logger.error(f"Redis DELETE失败: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 键名
            
        Returns:
            是否存在
        """
        try:
            return self.client.exists(key) == 1
        except RedisError as e:
            logger.error(f"Redis EXISTS失败: {e}")
            return False
    
    def expire(self, key: str, time: int) -> bool:
        """
        设置键过期时间
        
        Args:
            key: 键名
            time: 过期时间（秒）
            
        Returns:
            是否成功
        """
        try:
            return self.client.expire(key, time)
        except RedisError as e:
            logger.error(f"Redis EXPIRE失败: {e}")
            return False
    
    # ====================== 哈希操作 ======================
    
    def hset(self, name: str, key: str, value: Any) -> bool:
        """
        设置哈希字段
        
        Args:
            name: 哈希名
            key: 字段名
            value: 字段值
            
        Returns:
            是否成功
        """
        try:
            # 自动序列化
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            elif not isinstance(value, str):
                serialized_value = str(value)
            else:
                serialized_value = value
            
            return self.client.hset(name, key, serialized_value) == 1
            
        except RedisError as e:
            logger.error(f"Redis HSET失败: {e}")
            return False
    
    def hget(self, name: str, key: str, default: Any = None) -> Any:
        """
        获取哈希字段
        
        Args:
            name: 哈希名
            key: 字段名
            default: 默认值
            
        Returns:
            字段值
        """
        try:
            value = self.client.hget(name, key)
            if value is None:
                return default
            
            # 尝试JSON反序列化
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
                
        except RedisError as e:
            logger.error(f"Redis HGET失败: {e}")
            return default
    
    def hgetall(self, name: str) -> Dict[str, Any]:
        """
        获取所有哈希字段
        
        Args:
            name: 哈希名
            
        Returns:
            所有字段的字典
        """
        try:
            result = self.client.hgetall(name)
            decoded_result = {}
            
            for key, value in result.items():
                # 尝试JSON反序列化
                try:
                    decoded_result[key] = json.loads(value)
                except json.JSONDecodeError:
                    decoded_result[key] = value
            
            return decoded_result
            
        except RedisError as e:
            logger.error(f"Redis HGETALL失败: {e}")
            return {}
    
    # ====================== 列表操作 ======================
    
    def lpush(self, name: str, *values: Any) -> int:
        """
        从左侧推入列表
        
        Args:
            name: 列表名
            *values: 要推入的值
            
        Returns:
            列表长度
        """
        try:
            # 序列化所有值
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value))
                elif not isinstance(value, str):
                    serialized_values.append(str(value))
                else:
                    serialized_values.append(value)
            
            return self.client.lpush(name, *serialized_values)
            
        except RedisError as e:
            logger.error(f"Redis LPUSH失败: {e}")
            return 0
    
    def rpop(self, name: str, default: Any = None) -> Any:
        """
        从右侧弹出列表
        
        Args:
            name: 列表名
            default: 默认值
            
        Returns:
            弹出的值
        """
        try:
            value = self.client.rpop(name)
            if value is None:
                return default
            
            # 尝试JSON反序列化
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
                
        except RedisError as e:
            logger.error(f"Redis RPOP失败: {e}")
            return default
    
    # ====================== 集合操作 ======================
    
    def sadd(self, name: str, *values: Any) -> int:
        """
        添加集合元素
        
        Args:
            name: 集合名
            *values: 要添加的值
            
        Returns:
            添加的元素数量
        """
        try:
            # 序列化所有值
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value))
                elif not isinstance(value, str):
                    serialized_values.append(str(value))
                else:
                    serialized_values.append(value)
            
            return self.client.sadd(name, *serialized_values)
            
        except RedisError as e:
            logger.error(f"Redis SADD失败: {e}")
            return 0
    
    def smembers(self, name: str) -> List[Any]:
        """
        获取集合所有元素
        
        Args:
            name: 集合名
            
        Returns:
            所有元素的列表
        """
        try:
            values = self.client.smembers(name)
            decoded_values = []
            
            for value in values:
                # 尝试JSON反序列化
                try:
                    decoded_values.append(json.loads(value))
                except json.JSONDecodeError:
                    decoded_values.append(value)
            
            return decoded_values
            
        except RedisError as e:
            logger.error(f"Redis SMEMBERS失败: {e}")
            return []
    
    # ====================== 高级操作 ======================
    
    def cache_get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存（带前缀）
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            缓存值
        """
        cache_key = f"{config.CACHE_KEY_PREFIX}:{key}"
        return self.get(cache_key, default)
    
    def cache_set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        设置缓存（带前缀）
        
        Args:
            key: 缓存键
            value: 缓存值
            timeout: 超时时间（秒），None表示使用默认值
            
        Returns:
            是否成功
        """
        cache_key = f"{config.CACHE_KEY_PREFIX}:{key}"
        if timeout is None:
            timeout = config.CACHE_DEFAULT_TIMEOUT
        
        return self.set(cache_key, value, ex=timeout)
    
    def cache_delete(self, *keys: str) -> int:
        """
        删除缓存（带前缀）
        
        Args:
            *keys: 缓存键
            
        Returns:
            删除的键数量
        """
        cache_keys = [f"{config.CACHE_KEY_PREFIX}:{key}" for key in keys]
        return self.delete(*cache_keys)
    
    def health_check(self) -> bool:
        """
        Redis健康检查
        
        Returns:
            是否健康
        """
        return self.ping()
    
    def get_stats(self) -> dict:
        """
        获取Redis统计信息
        
        Returns:
            统计信息字典
        """
        try:
            info = self.client.info()
            return {
                "status": "healthy",
                "version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_connections_received": info.get("total_connections_received"),
                "total_commands_processed": info.get("total_commands_processed"),
            }
        except RedisError as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    def close(self) -> None:
        """关闭Redis连接"""
        if self._client:
            self._client.close()
        if self._pool:
            self._pool.disconnect()
            logger.info("Redis连接已关闭")


# 全局Redis客户端实例
redis_client = RedisClient()


def get_redis() -> RedisClient:
    """
    获取Redis客户端
    
    Returns:
        Redis客户端实例
    """
    return redis_client


def init_redis() -> None:
    """初始化Redis（应用启动时调用）"""
    # 这里只是确保Redis客户端已初始化
    redis_client.ping()


if __name__ == "__main__":
    # 测试Redis连接
    init_redis()
    
    # 健康检查
    if redis_client.health_check():
        print("✅ Redis连接正常")
        
        # 获取统计信息
        stats = redis_client.get_stats()
        print(f"Redis统计: {stats}")
        
        # 测试基本操作
        redis_client.set("test_key", {"name": "test", "value": 123})
        value = redis_client.get("test_key")
        print(f"测试值: {value}")
        
        redis_client.delete("test_key")
    else:
        print("❌ Redis连接失败")
    
    # 关闭连接
    redis_client.close()
"""
基础设施层
提供技术实现：数据库、缓存、安全等
"""

from .db_simple import (
    SimpleDatabaseManager,
    db_manager,
    init_database,
    get_db,
    # 注意：health_check和get_stats是类方法，不是函数
)

from .redis import (
    RedisClient,
    redis_client,
    get_redis,
    init_redis,
    health_check as redis_health_check,
    get_stats as redis_get_stats,
)

__all__ = [
    # 数据库
    'SimpleDatabaseManager',
    'db_manager',
    'init_database',
    'get_db',
    'execute_query',
    'execute_update',
    'execute_many',
    'db_health_check',
    'db_get_stats',
    
    # Redis
    'RedisClient',
    'redis_client',
    'get_redis',
    'init_redis',
    'redis_health_check',
    'redis_get_stats',
]
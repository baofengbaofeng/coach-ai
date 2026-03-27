"""
基础设施层
提供技术实现：数据库、缓存、安全等
"""

from .db_simple import (
    SimpleDatabaseManager,
    db_manager,
    init_database,
    get_db,
)

from .redis import (
    RedisClient,
    redis_client,
    get_redis,
    init_redis,
)

from .persistence.base import Repository, UnitOfWork, DatabaseUnitOfWork
from .persistence.user_repository import UserRepository, TenantRepository, PermissionRepository

__all__ = [
    # 数据库
    'SimpleDatabaseManager',
    'db_manager',
    'init_database',
    'get_db',
    
    # Redis
    'RedisClient',
    'redis_client',
    'get_redis',
    'init_redis',
    
    # 持久化
    'Repository',
    'UnitOfWork',
    'DatabaseUnitOfWork',
    'UserRepository',
    'TenantRepository',
    'PermissionRepository',
]
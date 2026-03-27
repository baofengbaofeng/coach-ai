"""
基础设施层 - 持久化基础类
提供仓库模式的基础实现
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Dict, Any
from datetime import datetime
from loguru import logger

from domain.base import Entity

T = TypeVar('T', bound=Entity)


class Repository(Generic[T], ABC):
    """仓库基类"""
    
    def __init__(self, db_manager, table_name: str):
        """
        初始化仓库
        
        Args:
            db_manager: 数据库管理器
            table_name: 表名
        """
        self.db_manager = db_manager
        self.table_name = table_name
    
    @abstractmethod
    def _entity_to_dict(self, entity: T) -> Dict[str, Any]:
        """将实体转换为字典"""
        pass
    
    @abstractmethod
    def _dict_to_entity(self, data: Dict[str, Any]) -> T:
        """将字典转换为实体"""
        pass
    
    async def save(self, entity: T) -> bool:
        """
        保存实体
        
        Args:
            entity: 要保存的实体
            
        Returns:
            是否成功
        """
        try:
            # 转换为字典
            data = self._entity_to_dict(entity)
            
            # 检查是否已存在
            existing = await self.find_by_id(entity.id)
            
            if existing:
                # 更新
                return await self._update(entity.id, data)
            else:
                # 插入
                return await self._insert(data)
                
        except Exception as e:
            logger.error(f"保存实体失败: {e}")
            return False
    
    async def _insert(self, data: Dict[str, Any]) -> bool:
        """插入新记录"""
        try:
            # 构建SQL
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            
            # 执行插入
            affected = await self.db_manager.execute_update(query, tuple(data.values()))
            return affected > 0
            
        except Exception as e:
            logger.error(f"插入记录失败: {e}")
            return False
    
    async def _update(self, entity_id: str, data: Dict[str, Any]) -> bool:
        """更新记录"""
        try:
            # 移除ID字段（不更新ID）
            update_data = {k: v for k, v in data.items() if k != 'id'}
            
            # 构建SET子句
            set_clause = ', '.join([f"{k} = %s" for k in update_data.keys()])
            
            # 添加版本检查（乐观锁）
            if 'version' in update_data:
                set_clause += f", version = version + 1"
                version = update_data.pop('version')
                query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = %s AND version = %s"
                params = tuple(update_data.values()) + (entity_id, version)
            else:
                query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = %s"
                params = tuple(update_data.values()) + (entity_id,)
            
            # 执行更新
            affected = await self.db_manager.execute_update(query, params)
            return affected > 0
            
        except Exception as e:
            logger.error(f"更新记录失败: {e}")
            return False
    
    async def find_by_id(self, entity_id: str) -> Optional[T]:
        """
        根据ID查找实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            实体或None
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE id = %s AND is_deleted = 0"
            result = await self.db_manager.execute_query(query, (entity_id,))
            
            if result:
                return self._dict_to_entity(result[0])
            return None
            
        except Exception as e:
            logger.error(f"根据ID查找实体失败: {e}")
            return None
    
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """
        查找所有实体
        
        Args:
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            实体列表
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE is_deleted = 0
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            results = await self.db_manager.execute_query(query, (limit, offset))
            
            return [self._dict_to_entity(row) for row in results]
            
        except Exception as e:
            logger.error(f"查找所有实体失败: {e}")
            return []
    
    async def delete(self, entity_id: str, soft_delete: bool = True) -> bool:
        """
        删除实体
        
        Args:
            entity_id: 实体ID
            soft_delete: 是否软删除
            
        Returns:
            是否成功
        """
        try:
            if soft_delete:
                # 软删除
                query = f"""
                    UPDATE {self.table_name} 
                    SET is_deleted = 1, deleted_at = %s, updated_at = %s
                    WHERE id = %s
                """
                now = datetime.now()
                params = (now, now, entity_id)
            else:
                # 硬删除
                query = f"DELETE FROM {self.table_name} WHERE id = %s"
                params = (entity_id,)
            
            affected = await self.db_manager.execute_update(query, params)
            return affected > 0
            
        except Exception as e:
            logger.error(f"删除实体失败: {e}")
            return False
    
    async def count(self) -> int:
        """
        统计实体数量
        
        Returns:
            实体数量
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE is_deleted = 0"
            result = await self.db_manager.execute_query(query)
            
            if result:
                return result[0].get('count', 0)
            return 0
            
        except Exception as e:
            logger.error(f"统计实体数量失败: {e}")
            return 0
    
    async def exists(self, entity_id: str) -> bool:
        """
        检查实体是否存在
        
        Args:
            entity_id: 实体ID
            
        Returns:
            是否存在
        """
        try:
            query = f"SELECT 1 FROM {self.table_name} WHERE id = %s AND is_deleted = 0"
            result = await self.db_manager.execute_query(query, (entity_id,))
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"检查实体是否存在失败: {e}")
            return False


class UnitOfWork(ABC):
    """工作单元基类"""
    
    def __init__(self):
        self._repositories = {}
    
    def __enter__(self):
        """进入上下文"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
    
    @abstractmethod
    async def commit(self):
        """提交所有更改"""
        pass
    
    @abstractmethod
    async def rollback(self):
        """回滚所有更改"""
        pass
    
    def get_repository(self, entity_class) -> Repository:
        """获取仓库"""
        if entity_class not in self._repositories:
            self._repositories[entity_class] = self._create_repository(entity_class)
        return self._repositories[entity_class]
    
    @abstractmethod
    def _create_repository(self, entity_class) -> Repository:
        """创建仓库"""
        pass


class DatabaseUnitOfWork(UnitOfWork):
    """数据库工作单元"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.connection = None
        self.transaction_started = False
    
    async def __aenter__(self):
        """异步进入上下文"""
        self.connection = await self.db_manager.get_connection()
        await self.connection.start_transaction()
        self.transaction_started = True
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步退出上下文"""
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        
        if self.connection:
            await self.connection.close()
    
    async def commit(self):
        """提交事务"""
        if self.connection and self.transaction_started:
            await self.connection.commit()
            self.transaction_started = False
    
    async def rollback(self):
        """回滚事务"""
        if self.connection and self.transaction_started:
            await self.connection.rollback()
            self.transaction_started = False
    
    def _create_repository(self, entity_class) -> Repository:
        """根据实体类创建仓库"""
        # 这里可以根据实体类名动态创建仓库
        # 简化实现：返回None，由子类重写
        return None
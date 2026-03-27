"""
数据库基础模型
提供所有模型共享的基础字段和功能
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import CHAR

# 声明性基类
Base = declarative_base()


class BaseModel(Base):
    """
    基础模型类
    所有数据库模型都继承此类，包含通用字段
    """
    __abstract__ = True
    
    # 主键ID，使用UUID格式
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 是否删除（软删除）
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # 删除时间
    deleted_at = Column(DateTime, nullable=True)
    
    # 创建者ID
    created_by = Column(CHAR(36), nullable=True)
    
    # 更新者ID
    updated_by = Column(CHAR(36), nullable=True)
    
    def to_dict(self):
        """
        将模型转换为字典
        排除敏感字段和内部字段
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # 处理特殊类型
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, uuid.UUID):
                value = str(value)
            result[column.name] = value
        return result
    
    def soft_delete(self, user_id=None):
        """
        软删除方法
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        if user_id:
            self.updated_by = user_id
    
    def restore(self, user_id=None):
        """
        恢复软删除
        """
        self.is_deleted = False
        self.deleted_at = None
        if user_id:
            self.updated_by = user_id
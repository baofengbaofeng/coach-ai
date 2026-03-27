"""
简化的领域基础类
避免dataclass继承问题
"""

import uuid
from datetime import datetime
from typing import Optional, List, Any
from abc import ABC


class DomainObject(ABC):
    """领域对象基类"""
    pass


class Entity(DomainObject):
    """实体基类（有唯一标识）"""
    
    def __init__(
        self,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        version: int = 0
    ):
        self.id = id or str(uuid.uuid4())
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or self.created_at
        self.version = version
    
    def mark_updated(self):
        """标记为已更新"""
        self.updated_at = datetime.now()
        self.version += 1
    
    def __eq__(self, other: Any) -> bool:
        """实体相等性比较（基于ID）"""
        if not isinstance(other, Entity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """实体哈希（基于ID）"""
        return hash(self.id)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id='{self.id}')>"


class ValueObject(DomainObject):
    """值对象基类（不可变，无标识）"""
    
    def __eq__(self, other: Any) -> bool:
        """值对象相等性比较（基于所有属性）"""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self) -> int:
        """值对象哈希（基于所有属性）"""
        return hash(tuple(sorted(self.__dict__.items())))
    
    def __repr__(self) -> str:
        attrs = ', '.join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"


class AggregateRoot(Entity):
    """聚合根基类"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._domain_events: List['DomainEvent'] = []
    
    def add_domain_event(self, event: 'DomainEvent'):
        """添加领域事件"""
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> List['DomainEvent']:
        """清除并返回所有领域事件"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    def get_domain_events(self) -> List['DomainEvent']:
        """获取所有领域事件"""
        return self._domain_events.copy()


class DomainEvent:
    """领域事件基类"""
    
    def __init__(
        self,
        event_id: Optional[str] = None,
        occurred_at: Optional[datetime] = None,
        aggregate_id: Optional[str] = None,
        aggregate_type: Optional[str] = None
    ):
        self.event_id = event_id or str(uuid.uuid4())
        self.occurred_at = occurred_at or datetime.now()
        self.aggregate_id = aggregate_id
        self.aggregate_type = aggregate_type or self.__class__.__name__.replace('Event', '')
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id='{self.event_id}', aggregate='{self.aggregate_id}')>"


class DomainException(Exception):
    """领域异常基类"""
    
    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        super().__init__(message)
        self.code = code
        self.message = message
    
    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class BusinessRule:
    """业务规则基类"""
    
    def __init__(self, message: str):
        self.message = message
    
    def is_broken(self) -> bool:
        """规则是否被违反"""
        raise NotImplementedError
    
    def __str__(self) -> str:
        return self.message
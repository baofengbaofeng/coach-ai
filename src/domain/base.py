"""
领域基础类
提供实体、值对象、领域事件等基础类
"""

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Any
import uuid


class DomainObject(ABC):
    """领域对象基类"""
    pass


@dataclass
class Entity(DomainObject):
    """实体基类（有唯一标识）"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    version: int = field(default=0)
    
    def __post_init__(self):
        """初始化后处理"""
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    def __post_init__(self):
        """初始化后处理"""
        if self.updated_at is None:
            self.updated_at = self.created_at
    
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


@dataclass(frozen=True)
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


@dataclass
class AggregateRoot(Entity):
    """聚合根基类"""
    
    _domain_events: List['DomainEvent'] = field(default_factory=list, init=False, repr=False)
    
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


@dataclass
class DomainEvent:
    """领域事件基类"""
    
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)
    aggregate_id: Optional[str] = None
    aggregate_type: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.aggregate_type:
            self.aggregate_type = self.__class__.__name__.replace('Event', '')


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
"""
事件总线模块
EDA（事件驱动架构）核心，提供事件发布/订阅机制
"""

import asyncio
import inspect
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
from loguru import logger

from ....settings import config


class EventStatus(Enum):
    """事件状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class DomainEvent:
    """领域事件基类"""
    
    # 事件标识
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = field(default="")
    event_version: str = field(default="1.0")
    
    # 事件元数据
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # 事件源
    source: str = field(default="")
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    
    # 事件数据
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # 处理状态
    status: EventStatus = field(default=EventStatus.PENDING)
    retry_count: int = field(default=0)
    error_message: Optional[str] = None
    processed_at: Optional[datetime] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.event_type:
            self.event_type = self.__class__.__name__
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "event_version": self.event_version,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "source": self.source,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "payload": self.payload,
            "status": self.status.value,
            "retry_count": self.retry_count,
            "error_message": self.error_message,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DomainEvent':
        """从字典创建"""
        # 处理时间字段
        timestamp = datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now()
        processed_at = datetime.fromisoformat(data["processed_at"]) if data.get("processed_at") else None
        
        # 处理状态字段
        status = EventStatus(data.get("status", "pending"))
        
        return cls(
            event_id=data.get("event_id", str(uuid.uuid4())),
            event_type=data.get("event_type", ""),
            event_version=data.get("event_version", "1.0"),
            timestamp=timestamp,
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id"),
            source=data.get("source", ""),
            user_id=data.get("user_id"),
            tenant_id=data.get("tenant_id"),
            payload=data.get("payload", {}),
            status=status,
            retry_count=data.get("retry_count", 0),
            error_message=data.get("error_message"),
            processed_at=processed_at,
        )


# 事件处理器类型
EventHandler = Callable[[DomainEvent], Any]
AsyncEventHandler = Callable[[DomainEvent], Any]


class EventBus(ABC):
    """事件总线抽象基类"""
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> bool:
        """发布事件"""
        pass
    
    @abstractmethod
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """订阅事件"""
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """取消订阅"""
        pass
    
    @abstractmethod
    async def process_event(self, event: DomainEvent) -> bool:
        """处理事件"""
        pass


class MemoryEventBus(EventBus):
    """内存事件总线（开发环境使用）"""
    
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._processing_tasks: Set[asyncio.Task] = set()
        self._is_running = False
    
    async def start(self) -> None:
        """启动事件总线"""
        if self._is_running:
            return
        
        self._is_running = True
        # 启动事件处理循环
        asyncio.create_task(self._process_events())
        logger.info("内存事件总线已启动")
    
    async def stop(self) -> None:
        """停止事件总线"""
        self._is_running = False
        
        # 等待所有处理任务完成
        if self._processing_tasks:
            await asyncio.gather(*self._processing_tasks, return_exceptions=True)
        
        logger.info("内存事件总线已停止")
    
    async def publish(self, event: DomainEvent) -> bool:
        """发布事件到队列"""
        try:
            await self._event_queue.put(event)
            logger.debug(f"事件已发布: {event.event_type} ({event.event_id})")
            return True
        except Exception as e:
            logger.error(f"发布事件失败: {e}")
            return False
    
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """订阅事件"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            logger.debug(f"事件处理器已订阅: {event_type} -> {handler.__name__}")
    
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """取消订阅"""
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            logger.debug(f"事件处理器已取消订阅: {event_type} -> {handler.__name__}")
    
    async def _process_events(self) -> None:
        """处理事件队列"""
        while self._is_running:
            try:
                # 从队列获取事件
                event = await self._event_queue.get()
                
                # 创建处理任务
                task = asyncio.create_task(self._handle_event(event))
                self._processing_tasks.add(task)
                task.add_done_callback(self._processing_tasks.discard)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"事件处理循环异常: {e}")
    
    async def _handle_event(self, event: DomainEvent) -> None:
        """处理单个事件"""
        event.status = EventStatus.PROCESSING
        
        try:
            # 获取事件处理器
            handlers = self._handlers.get(event.event_type, [])
            
            if not handlers:
                logger.warning(f"没有找到事件处理器: {event.event_type}")
                event.status = EventStatus.SUCCESS
                event.processed_at = datetime.now()
                return
            
            # 执行所有处理器
            for handler in handlers:
                try:
                    # 检查是否是异步函数
                    if inspect.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                    
                    logger.debug(f"事件处理成功: {event.event_type} -> {handler.__name__}")
                    
                except Exception as e:
                    logger.error(f"事件处理器执行失败: {event.event_type} -> {handler.__name__}: {e}")
                    
                    # 重试逻辑
                    if event.retry_count < config.EVENT_RETRY_ATTEMPTS:
                        event.retry_count += 1
                        event.status = EventStatus.RETRYING
                        event.error_message = str(e)
                        
                        # 延迟重试
                        await asyncio.sleep(config.EVENT_RETRY_DELAY * event.retry_count)
                        
                        # 重新发布事件
                        await self.publish(event)
                        return
                    else:
                        event.status = EventStatus.FAILED
                        event.error_message = f"重试{config.EVENT_RETRY_ATTEMPTS}次后仍然失败: {e}"
                        raise
            
            # 处理成功
            event.status = EventStatus.SUCCESS
            event.processed_at = datetime.now()
            
        except Exception as e:
            event.status = EventStatus.FAILED
            event.error_message = str(e)
            logger.error(f"事件处理失败: {event.event_type} ({event.event_id}): {e}")
    
    async def process_event(self, event: DomainEvent) -> bool:
        """直接处理事件（同步接口）"""
        return await self._handle_event(event)


class EventBusFactory:
    """事件总线工厂"""
    
    _instance: Optional[EventBus] = None
    
    @classmethod
    def get_event_bus(cls) -> EventBus:
        """获取事件总线实例"""
        if cls._instance is None:
            cls._instance = cls._create_event_bus()
        return cls._instance
    
    @classmethod
    def _create_event_bus(cls) -> EventBus:
        """创建事件总线实例"""
        bus_type = config.EVENT_BUS_TYPE.lower()
        
        if bus_type == "memory":
            bus = MemoryEventBus()
            logger.info(f"创建内存事件总线")
            return bus
        elif bus_type == "redis":
            # 这里可以扩展Redis事件总线
            logger.warning("Redis事件总线尚未实现，使用内存事件总线")
            return MemoryEventBus()
        elif bus_type == "rabbitmq":
            # 这里可以扩展RabbitMQ事件总线
            logger.warning("RabbitMQ事件总线尚未实现，使用内存事件总线")
            return MemoryEventBus()
        else:
            logger.warning(f"未知的事件总线类型: {bus_type}，使用内存事件总线")
            return MemoryEventBus()
    
    @classmethod
    async def start_event_bus(cls) -> None:
        """启动事件总线"""
        bus = cls.get_event_bus()
        if isinstance(bus, MemoryEventBus):
            await bus.start()
    
    @classmethod
    async def stop_event_bus(cls) -> None:
        """停止事件总线"""
        bus = cls.get_event_bus()
        if isinstance(bus, MemoryEventBus):
            await bus.stop()


# 全局事件总线实例
event_bus = EventBusFactory.get_event_bus()


async def publish_event(event: DomainEvent) -> bool:
    """
    发布事件（简化接口）
    
    Args:
        event: 领域事件
        
    Returns:
        是否成功
    """
    return await event_bus.publish(event)


def subscribe_event(event_type: str, handler: EventHandler) -> None:
    """
    订阅事件（简化接口）
    
    Args:
        event_type: 事件类型
        handler: 事件处理器
    """
    event_bus.subscribe(event_type, handler)


def unsubscribe_event(event_type: str, handler: EventHandler) -> None:
    """
    取消订阅事件（简化接口）
    
    Args:
        event_type: 事件类型
        handler: 事件处理器
    """
    event_bus.unsubscribe(event_type, handler)


# ====================== 示例事件定义 ======================

@dataclass
class UserRegisteredEvent(DomainEvent):
    """用户注册事件"""
    
    def __post_init__(self):
        super().__post_init__()
        if not self.event_type:
            self.event_type = "UserRegisteredEvent"
        
        # 确保必要的payload字段
        if "user_id" not in self.payload:
            raise ValueError("UserRegisteredEvent必须包含user_id")


@dataclass
class AchievementUnlockedEvent(DomainEvent):
    """成就解锁事件"""
    
    def __post_init__(self):
        super().__post_init__()
        if not self.event_type:
            self.event_type = "AchievementUnlockedEvent"
        
        # 确保必要的payload字段
        if "achievement_id" not in self.payload:
            raise ValueError("AchievementUnlockedEvent必须包含achievement_id")
        if "user_id" not in self.payload:
            raise ValueError("AchievementUnlockedEvent必须包含user_id")


@dataclass
class TaskCompletedEvent(DomainEvent):
    """任务完成事件"""
    
    def __post_init__(self):
        super().__post_init__()
        if not self.event_type:
            self.event_type = "TaskCompletedEvent"
        
        # 确保必要的payload字段
        if "task_id" not in self.payload:
            raise ValueError("TaskCompletedEvent必须包含task_id")
        if "user_id" not in self.payload:
            raise ValueError("TaskCompletedEvent必须包含user_id")


if __name__ == "__main__":
    # 测试事件总线
    import asyncio
    
    async def test_event_bus():
        """测试事件总线"""
        
        # 定义事件处理器
        def handle_user_registered(event: UserRegisteredEvent):
            print(f"处理用户注册事件: {event.payload}")
        
        async def handle_achievement_unlocked(event: AchievementUnlockedEvent):
            print(f"处理成就解锁事件: {event.payload}")
            await asyncio.sleep(0.1)  # 模拟异步处理
        
        # 获取事件总线
        bus = EventBusFactory.get_event_bus()
        
        # 启动事件总线
        if isinstance(bus, MemoryEventBus):
            await bus.start()
        
        # 订阅事件
        subscribe_event("UserRegisteredEvent", handle_user_registered)
        subscribe_event("AchievementUnlockedEvent", handle_achievement_unlocked)
        
        # 发布事件
        user_event = UserRegisteredEvent(
            source="auth_service",
            user_id="user_123",
            payload={"user_id": "user_123", "email": "test@example.com"}
        )
        
        achievement_event = AchievementUnlockedEvent(
            source="achievement_service",
            user_id="user_123",
            payload={"user_id": "user_123", "achievement_id": "first_login"}
        )
        
        await publish_event(user_event)
        await publish_event(achievement_event)
        
        # 等待事件处理完成
        await asyncio.sleep(1)
        
        # 停止事件总线
        if isinstance(bus, MemoryEventBus):
            await bus.stop()
        
        print("✅ 事件总线测试完成")
    
    # 运行测试
    asyncio.run(test_event_bus())
"""
应用层
协调领域对象，处理用例，事件处理
"""

from .event.bus import (
    DomainEvent,
    UserRegisteredEvent,
    AchievementUnlockedEvent,
    TaskCompletedEvent,
    EventBus,
    MemoryEventBus,
    EventBusFactory,
    event_bus,
    publish_event,
    subscribe_event,
    unsubscribe_event,
)

__all__ = [
    # 事件总线
    'DomainEvent',
    'UserRegisteredEvent',
    'AchievementUnlockedEvent',
    'TaskCompletedEvent',
    'EventBus',
    'MemoryEventBus',
    'EventBusFactory',
    'event_bus',
    'publish_event',
    'subscribe_event',
    'unsubscribe_event',
]
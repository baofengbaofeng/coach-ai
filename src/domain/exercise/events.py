"""
运动领域事件
"""

from datetime import datetime
from typing import Optional
from domain.base_simple import DomainEvent


class ExerciseTypeCreatedEvent(DomainEvent):
    """运动类型创建事件"""
    
    def __init__(self, exercise_type_id: str, name_zh: str, code: str, **kwargs):
        super().__init__(**kwargs)
        self.exercise_type_id = exercise_type_id
        self.name_zh = name_zh
        self.code = code
    
    def to_dict(self):
        return {
            'event_type': 'exercise_type_created',
            'exercise_type_id': self.exercise_type_id,
            'name_zh': self.name_zh,
            'code': self.code,
            'occurred_at': self.occurred_at.isoformat(),
        }


class ExerciseRecordCreatedEvent(DomainEvent):
    """运动记录创建事件"""
    
    def __init__(self, record_id: str, user_id: str, exercise_type_id: str, **kwargs):
        super().__init__(**kwargs)
        self.record_id = record_id
        self.user_id = user_id
        self.exercise_type_id = exercise_type_id
    
    def to_dict(self):
        return {
            'event_type': 'exercise_record_created',
            'record_id': self.record_id,
            'user_id': self.user_id,
            'exercise_type_id': self.exercise_type_id,
            'occurred_at': self.occurred_at.isoformat(),
        }


class ExerciseStartedEvent(DomainEvent):
    """运动开始事件"""
    
    def __init__(self, record_id: str, user_id: str, started_at: datetime, **kwargs):
        super().__init__(**kwargs)
        self.record_id = record_id
        self.user_id = user_id
        self.started_at = started_at
    
    def to_dict(self):
        return {
            'event_type': 'exercise_started',
            'record_id': self.record_id,
            'user_id': self.user_id,
            'started_at': self.started_at.isoformat(),
            'occurred_at': self.occurred_at.isoformat(),
        }


class ExerciseCompletedEvent(DomainEvent):
    """运动完成事件"""
    
    def __init__(
        self,
        record_id: str,
        user_id: str,
        completed_at: datetime,
        duration_seconds: Optional[int] = None,
        calories: Optional[float] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.record_id = record_id
        self.user_id = user_id
        self.completed_at = completed_at
        self.duration_seconds = duration_seconds
        self.calories = calories
    
    def to_dict(self):
        return {
            'event_type': 'exercise_completed',
            'record_id': self.record_id,
            'user_id': self.user_id,
            'completed_at': self.completed_at.isoformat(),
            'duration_seconds': self.duration_seconds,
            'calories': self.calories,
            'occurred_at': self.occurred_at.isoformat(),
        }


class ExercisePlanCreatedEvent(DomainEvent):
    """运动计划创建事件"""
    
    def __init__(self, plan_id: str, user_id: str, plan_name: str, **kwargs):
        super().__init__(**kwargs)
        self.plan_id = plan_id
        self.user_id = user_id
        self.plan_name = plan_name
    
    def to_dict(self):
        return {
            'event_type': 'exercise_plan_created',
            'plan_id': self.plan_id,
            'user_id': self.user_id,
            'plan_name': self.plan_name,
            'occurred_at': self.occurred_at.isoformat(),
        }


class ExercisePlanUpdatedEvent(DomainEvent):
    """运动计划更新事件"""
    
    def __init__(self, plan_id: str, user_id: str, changes: dict, **kwargs):
        super().__init__(**kwargs)
        self.plan_id = plan_id
        self.user_id = user_id
        self.changes = changes
    
    def to_dict(self):
        return {
            'event_type': 'exercise_plan_updated',
            'plan_id': self.plan_id,
            'user_id': self.user_id,
            'changes': self.changes,
            'occurred_at': self.occurred_at.isoformat(),
        }


class ExerciseProgressEvent(DomainEvent):
    """运动进度事件"""
    
    def __init__(
        self,
        user_id: str,
        total_sessions: int,
        total_minutes: float,
        consistency: str,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.total_sessions = total_sessions
        self.total_minutes = total_minutes
        self.consistency = consistency
    
    def to_dict(self):
        return {
            'event_type': 'exercise_progress',
            'user_id': self.user_id,
            'total_sessions': self.total_sessions,
            'total_minutes': self.total_minutes,
            'consistency': self.consistency,
            'occurred_at': self.occurred_at.isoformat(),
        }
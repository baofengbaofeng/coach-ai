"""
运动领域模块
包含运动类型、运动记录、运动计划等核心业务概念
"""

from .value_objects import (
    ExerciseCategory, ExerciseDifficulty, Duration, 
    Intensity, Repetition, Weight, Distance
)
from .entities import ExerciseType, ExerciseRecord, ExercisePlan
from .services import ExerciseService, ExercisePlanService
from .events import (
    ExerciseTypeCreatedEvent,
    ExerciseRecordCreatedEvent,
    ExerciseStartedEvent,
    ExerciseCompletedEvent,
    ExercisePlanCreatedEvent,
    ExercisePlanUpdatedEvent
)

__all__ = [
    # 值对象
    'ExerciseCategory',
    'ExerciseDifficulty',
    'Duration',
    'Intensity',
    'Repetition',
    'Weight',
    'Distance',
    
    # 实体
    'ExerciseType',
    'ExerciseRecord',
    'ExercisePlan',
    
    # 领域服务
    'ExerciseService',
    'ExercisePlanService',
    
    # 领域事件
    'ExerciseTypeCreatedEvent',
    'ExerciseRecordCreatedEvent',
    'ExerciseStartedEvent',
    'ExerciseCompletedEvent',
    'ExercisePlanCreatedEvent',
    'ExercisePlanUpdatedEvent',
]
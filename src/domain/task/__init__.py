"""
任务领域模块
包含任务、任务分配、任务提交、任务评估等核心业务概念
"""

from .value_objects import (
    TaskType, TaskStatus, TaskPriority, TaskDifficulty,
    AssignmentStatus, EvaluationStatus, SubmissionStatus
)
from .entities import Task, TaskAssignment, TaskSubmission, TaskEvaluation
from .services import TaskService, AssignmentService, EvaluationService
from .events import (
    TaskCreatedEvent,
    TaskUpdatedEvent,
    TaskAssignedEvent,
    TaskStartedEvent,
    TaskProgressUpdatedEvent,
    TaskCompletedEvent,
    TaskOverdueEvent,
    SubmissionCreatedEvent,
    SubmissionEvaluatedEvent,
    TaskArchivedEvent,
    TaskCancelledEvent,
    AssignmentCancelledEvent,
    TaskDependencyAddedEvent,
    TaskDependencyRemovedEvent
)

__all__ = [
    # 值对象
    'TaskType',
    'TaskStatus',
    'TaskPriority',
    'TaskDifficulty',
    'AssignmentStatus',
    'EvaluationStatus',
    'SubmissionStatus',
    
    # 实体
    'Task',
    'TaskAssignment',
    'TaskSubmission',
    'TaskEvaluation',
    
    # 领域服务
    'TaskService',
    'AssignmentService',
    'EvaluationService',
    
    # 领域事件
    'TaskCreatedEvent',
    'TaskUpdatedEvent',
    'TaskAssignedEvent',
    'TaskStartedEvent',
    'TaskProgressUpdatedEvent',
    'TaskCompletedEvent',
    'TaskOverdueEvent',
    'SubmissionCreatedEvent',
    'SubmissionEvaluatedEvent',
    'TaskArchivedEvent',
    'TaskCancelledEvent',
    'AssignmentCancelledEvent',
    'TaskDependencyAddedEvent',
    'TaskDependencyRemovedEvent',
]
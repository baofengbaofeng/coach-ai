"""
任务领域事件
"""

from datetime import datetime
from typing import Optional, Dict, Any
from domain.base_simple import DomainEvent


class TaskCreatedEvent(DomainEvent):
    """任务创建事件"""
    
    def __init__(
        self,
        task_id: str,
        title: str,
        task_type: str,
        created_by: str,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.task_id = task_id
        self.title = title
        self.task_type = task_type
        self.created_by = created_by
        self.tenant_id = tenant_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'task_created',
            'task_id': self.task_id,
            'title': self.title,
            'task_type': self.task_type,
            'created_by': self.created_by,
            'tenant_id': self.tenant_id,
            'occurred_at': self.occurred_at.isoformat(),
        }


class TaskUpdatedEvent(DomainEvent):
    """任务更新事件"""
    
    def __init__(
        self,
        task_id: str,
        updated_by: str,
        changes: Dict[str, Any],
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.task_id = task_id
        self.updated_by = updated_by
        self.changes = changes
        self.tenant_id = tenant_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'task_updated',
            'task_id': self.task_id,
            'updated_by': self.updated_by,
            'changes': self.changes,
            'tenant_id': self.tenant_id,
            'occurred_at': self.occurred_at.isoformat(),
        }


class TaskAssignedEvent(DomainEvent):
    """任务分配事件"""
    
    def __init__(
        self,
        task_id: str,
        assignment_id: str,
        student_id: str,
        assigner_id: str,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.task_id = task_id
        self.assignment_id = assignment_id
        self.student_id = student_id
        self.assigner_id = assigner_id
        self.tenant_id = tenant_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'task_assigned',
            'task_id': self.task_id,
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'assigner_id': self.assigner_id,
            'tenant_id': self.tenant_id,
            'occurred_at': self.occurred_at.isoformat(),
        }


class TaskStartedEvent(DomainEvent):
    """任务开始事件"""
    
    def __init__(
        self,
        assignment_id: str,
        student_id: str,
        started_at: datetime,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.assignment_id = assignment_id
        self.student_id = student_id
        self.started_at = started_at
        self.tenant_id = tenant_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'task_started',
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'started_at': self.started_at.isoformat(),
            'tenant_id': self.tenant_id,
            'occurred_at': self.occurred_at.isoformat(),
        }


class TaskProgressUpdatedEvent(DomainEvent):
    """任务进度更新事件"""
    
    def __init__(
        self,
        assignment_id: str,
        student_id: str,
        progress: float,
        notes: Optional[str] = None,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.assignment_id = assignment_id
        self.student_id = student_id
        self.progress = progress
        self.notes = notes
        self.tenant_id = tenant_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'task_progress_updated',
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'progress': self.progress,
            'notes': self.notes,
            'tenant_id': self.tenant_id,
            'occurred_at': self.occurred_at.isoformat(),
        }


class TaskCompletedEvent(DomainEvent):
    """任务完成事件"""
    
    def __init__(
        self,
        assignment_id: str,
        student_id: str,
        completed_at: datetime,
        actual_duration: Optional[int] = None,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.assignment_id = assignment_id
        self.student_id = student_id
        self.completed_at = completed_at
        self.actual_duration = actual_duration
        self.tenant_id = tenant_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'task_completed',
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'completed_at': self.completed_at.isoformat(),
            'actual_duration': self.actual_duration,
            'tenant_id': self.tenant_id,
            'occurred_at': self.occurred_at.isoformat(),
        }


class TaskOverdueEvent(DomainEvent):
    """任务逾期事件"""
    
    def __init__(
        self,
        assignment_id: str,
        task_id: str,
        student_id: str,
        deadline: datetime,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.assignment_id = assignment_id
        self.task_id = task_id
        self.student_id = student_id
        self.deadline = deadline
        self.tenant_id = tenant_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'task_overdue',
            'assignment_id': self.assignment_id,
            'task_id': self.task_id,
            'student_id': self.student_id,
            'deadline': self.deadline.isoformat(),
            'tenant_id': self.tenant_id,
            'occurred_at': self.occurred_at.isoformat(),
        }


class SubmissionCreatedEvent(DomainEvent):
    """任务提交创建事件"""
    
    def __init__(
        self,
        submission_id: str,
        assignment_id: str,
        submitted_by: str,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.submission_id = submission_id
        self.assignment_id = assignment_id
        self.submitted_by = submitted_by
        self.tenant_id = tenant_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'submission_created',
            'submission_id': self.submission_id,
            'assignment_id': self.assignment_id,
            'submitted_by': self.submitted_by,
            'tenant_id': self.tenant_id,
            'occurred_at': self.occurred_at.isoformat(),
        }


class SubmissionEvaluatedEvent(DomainEvent):
    """任务提交评估事件"""
    
    def __init__(
        self,
        submission_id: str,
        evaluator_id: str,
        score: float,
        feedback: str,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.submission_id = submission_id
        self.evaluator_id = evaluator_id
        self.score = score
        self.feedback = feedback
        self.tenant_id = tenant_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'submission_evaluated',
            'submission_id': self.submission_id,
            'evaluator_id': self.evaluator_id,
            'score': self.score,
            'feedback': self.feedback,
            'tenant_id': self.tenant_id,
            'occurred_at': self.occurred_at.isoformat(),
        }


class TaskArchivedEvent(DomainEvent):
    """任务归档事件"""
    
    def __init__(
        self,
        task_id: str,
        archived_by: str,
        archived_at: datetime,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.task_id = task_id
        self.archived_by = archived_by
        self.archived_at = archived_at
        self.tenant_id = tenant_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'task_archived',
            'task_id': self.task_id,
            'archived_by': self.archived_by,
            'archived_at': self.archived_at.isoformat(),
            'tenant_id': self.tenant_id,
            'occurred_at': self.occurred_at.isoformat(),
        }


class TaskCancelledEvent(DomainEvent):
    """任务取消事件"""
    
    def __init__(
        self,
        task_id: str,
        cancelled_by: str,
        reason: Optional[str] = None,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.task_id = task_id
        self.cancelled_by = cancelled_by
        self.reason = reason
        self.tenant_id = tenant_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'task_cancelled',
            'task_id': self.task_id,
            'cancelled_by': self.cancelled_by,
            'reason': self.reason,
            'tenant_id': self.tenant_id,
            'occurred_at': self.occurred_at.isoformat(),
        }


class AssignmentCancelledEvent(DomainEvent):
    """任务分配取消事件"""
    
    def __init__(
        self,
        assignment_id: str,
        cancelled_by: str,
        reason: Optional[str] = None,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.assignment_id = assignment_id
        self.cancelled_by = cancelled_by
        self.reason = reason
        self.tenant_id = tenant_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'assignment_cancelled',
            'assignment_id': self.assignment_id,
            'cancelled_by': self.cancelled_by,
            'reason': self.reason,
            'tenant_id': self.tenant_id,
            'occurred_at': self.occurred_at.isoformat(),
        }


class TaskDependencyAddedEvent(DomainEvent):
    """任务依赖添加事件"""
    
    def __init__(
        self,
        task_id: str,
        dependency_id: str,
        added_by: str,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.task_id = task_id
        self.dependency_id = dependency_id
        self.added_by = added_by
        self.tenant_id = tenant_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'task_dependency_added',
            'task_id': self.task_id,
            'dependency_id': self.dependency_id,
            'added_by': self.added_by,
            'tenant_id': self.tenant_id,
            'occurred_at': self.occurred_at.isoformat(),
        }


class TaskDependencyRemovedEvent(DomainEvent):
    """任务依赖移除事件"""
    
    def __init__(
        self,
        task_id: str,
        dependency_id: str,
        removed_by: str,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.task_id = task_id
        self.dependency_id = dependency_id
        self.removed_by = removed_by
        self.tenant_id = tenant_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'task_dependency_removed',
            'task_id': self.task_id,
            'dependency_id': self.dependency_id,
            'removed_by': self.removed_by,
            'tenant_id': self.tenant_id,
            'occurred_at': self.occurred_at.isoformat(),
        }
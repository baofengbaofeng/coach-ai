"""
任务领域实体
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from domain.base_simple import AggregateRoot
from .value_objects import (
    TaskType, TaskStatus, TaskPriority, TaskDifficulty,
    AssignmentStatus, EvaluationStatus, SubmissionStatus,
    TaskContent, TaskMetadata
)


class Task(AggregateRoot):
    """任务实体（聚合根）"""
    
    def __init__(
        self,
        title: str,
        task_type: TaskType,
        created_by: str,
        tenant_id: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        difficulty: Optional[TaskDifficulty] = None,
        tags: Optional[List[str]] = None,
        content: Optional[TaskContent] = None,
        metadata: Optional[TaskMetadata] = None,
        start_time: Optional[datetime] = None,
        deadline: Optional[datetime] = None,
        estimated_duration: Optional[int] = None,
        dependencies: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.title = title
        self.task_type = task_type
        self.created_by = created_by
        self.tenant_id = tenant_id
        self.description = description
        self.status = status or TaskStatus("draft")
        self.priority = priority or TaskPriority("medium")
        self.difficulty = difficulty or TaskDifficulty("beginner")
        self.tags = tags or []
        self.content = content or TaskContent({})
        self.metadata = metadata or TaskMetadata({})
        self.start_time = start_time
        self.deadline = deadline
        self.estimated_duration = estimated_duration
        self.dependencies = dependencies or []
        
        # 扩展字段
        self.actual_duration: Optional[int] = None
        self.completed_at: Optional[datetime] = None
        self.cancelled_at: Optional[datetime] = None
        self.archived_at: Optional[datetime] = None
        
        self._validate()
    
    def _validate(self):
        """验证任务数据"""
        if not self.title or len(self.title.strip()) < 2:
            raise ValueError("任务标题长度必须至少2个字符")
        
        if not self.created_by:
            raise ValueError("创建者ID不能为空")
        
        if self.deadline and self.start_time and self.deadline < self.start_time:
            raise ValueError("截止时间不能早于开始时间")
        
        if self.estimated_duration is not None and self.estimated_duration < 0:
            raise ValueError("预计完成时间不能为负数")
    
    def update_info(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[TaskPriority] = None,
        difficulty: Optional[TaskDifficulty] = None,
        tags: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        deadline: Optional[datetime] = None,
        estimated_duration: Optional[int] = None
    ) -> None:
        """更新任务信息"""
        if not self.status.can_be_modified():
            raise ValueError(f"任务状态为{self.status}，无法修改")
        
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if priority is not None:
            self.priority = priority
        if difficulty is not None:
            self.difficulty = difficulty
        if tags is not None:
            self.tags = tags
        if start_time is not None:
            self.start_time = start_time
        if deadline is not None:
            self.deadline = deadline
        if estimated_duration is not None:
            self.estimated_duration = estimated_duration
        
        self.mark_updated()
    
    def activate(self) -> None:
        """激活任务"""
        if not self.status.is_draft():
            raise ValueError(f"只有草稿状态的任务可以激活，当前状态: {self.status}")
        
        self.status = TaskStatus("active")
        self.mark_updated()
    
    def complete(self, actual_duration: Optional[int] = None) -> None:
        """完成任务"""
        if not self.status.is_active():
            raise ValueError(f"只有活跃状态的任务可以完成，当前状态: {self.status}")
        
        self.status = TaskStatus("completed")
        self.completed_at = datetime.now()
        if actual_duration is not None:
            self.actual_duration = actual_duration
        
        self.mark_updated()
    
    def cancel(self, reason: Optional[str] = None) -> None:
        """取消任务"""
        if not self.status.can_be_modified():
            raise ValueError(f"任务状态为{self.status}，无法取消")
        
        self.status = TaskStatus("cancelled")
        self.cancelled_at = datetime.now()
        if reason:
            self.metadata.set("cancellation_reason", reason)
        
        self.mark_updated()
    
    def archive(self) -> None:
        """归档任务"""
        if not self.status.is_completed():
            raise ValueError(f"只有完成状态的任务可以归档，当前状态: {self.status}")
        
        self.status = TaskStatus("archived")
        self.archived_at = datetime.now()
        self.mark_updated()
    
    def add_dependency(self, task_id: str) -> None:
        """添加任务依赖"""
        if task_id not in self.dependencies:
            self.dependencies.append(task_id)
            self.mark_updated()
    
    def remove_dependency(self, task_id: str) -> None:
        """移除任务依赖"""
        if task_id in self.dependencies:
            self.dependencies.remove(task_id)
            self.mark_updated()
    
    def is_overdue(self) -> bool:
        """检查任务是否逾期"""
        if not self.deadline or self.status.is_completed() or self.status.is_cancelled():
            return False
        
        return datetime.now() > self.deadline
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'task_type': str(self.task_type),
            'created_by': self.created_by,
            'tenant_id': self.tenant_id,
            'description': self.description,
            'status': str(self.status),
            'priority': str(self.priority),
            'difficulty': str(self.difficulty),
            'tags': self.tags,
            'content': self.content.to_dict(),
            'metadata': self.metadata.to_dict(),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'estimated_duration': self.estimated_duration,
            'actual_duration': self.actual_duration,
            'dependencies': self.dependencies,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'archived_at': self.archived_at.isoformat() if self.archived_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<Task(id='{self.id}', title='{self.title}', status='{self.status}')>"


class TaskAssignment(AggregateRoot):
    """任务分配实体"""
    
    def __init__(
        self,
        task_id: str,
        student_id: str,
        assigner_id: str,
        tenant_id: Optional[str] = None,
        status: Optional[AssignmentStatus] = None,
        progress: float = 0.0,
        assigned_at: Optional[datetime] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        expected_completion_time: Optional[datetime] = None,
        notes: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.task_id = task_id
        self.student_id = student_id
        self.assigner_id = assigner_id
        self.tenant_id = tenant_id
        self.status = status or AssignmentStatus("assigned")
        self.progress = progress
        self.assigned_at = assigned_at or datetime.now()
        self.started_at = started_at
        self.completed_at = completed_at
        self.expected_completion_time = expected_completion_time
        self.notes = notes
        
        # 扩展字段
        self.feedback: Optional[str] = None
        self.rating: Optional[float] = None
        self.metadata: Dict[str, Any] = {}
        
        self._validate()
    
    def _validate(self):
        """验证分配数据"""
        if not self.task_id:
            raise ValueError("任务ID不能为空")
        
        if not self.student_id:
            raise ValueError("学员ID不能为空")
        
        if not self.assigner_id:
            raise ValueError("分配者ID不能为空")
        
        if not 0.0 <= self.progress <= 100.0:
            raise ValueError("进度必须在0-100之间")
        
        if self.completed_at and self.started_at and self.completed_at < self.started_at:
            raise ValueError("完成时间不能早于开始时间")
    
    def start(self) -> None:
        """开始任务"""
        if not self.status.can_start():
            raise ValueError(f"分配状态为{self.status}，无法开始")
        
        self.status = AssignmentStatus("in_progress")
        self.started_at = datetime.now()
        self.mark_updated()
    
    def update_progress(self, progress: float, notes: Optional[str] = None) -> None:
        """更新进度"""
        if not self.status.is_in_progress():
            raise ValueError(f"只有进行中的任务可以更新进度，当前状态: {self.status}")
        
        if not 0.0 <= progress <= 100.0:
            raise ValueError("进度必须在0-100之间")
        
        self.progress = progress
        if notes is not None:
            self.notes = notes
        
        self.mark_updated()
    
    def complete(self, feedback: Optional[str] = None, rating: Optional[float] = None) -> None:
        """完成任务分配"""
        if not self.status.can_complete():
            raise ValueError(f"分配状态为{self.status}，无法完成")
        
        self.status = AssignmentStatus("completed")
        self.progress = 100.0
        self.completed_at = datetime.now()
        
        if feedback is not None:
            self.feedback = feedback
        if rating is not None:
            if not 0.0 <= rating <= 5.0:
                raise ValueError("评分必须在0-5之间")
            self.rating = rating
        
        self.mark_updated()
    
    def cancel(self, reason: Optional[str] = None) -> None:
        """取消任务分配"""
        if self.status.is_completed():
            raise ValueError("已完成的任务分配无法取消")
        
        self.status = AssignmentStatus("cancelled")
        if reason:
            self.metadata["cancellation_reason"] = reason
        
        self.mark_updated()
    
    def mark_overdue(self) -> None:
        """标记为逾期"""
        if self.status.is_completed() or self.status.is_cancelled():
            return
        
        self.status = AssignmentStatus("overdue")
        self.mark_updated()
    
    def is_overdue(self) -> bool:
        """检查是否逾期"""
        if self.status.is_overdue():
            return True
        
        if self.expected_completion_time and not self.status.is_completed():
            return datetime.now() > self.expected_completion_time
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'student_id': self.student_id,
            'assigner_id': self.assigner_id,
            'tenant_id': self.tenant_id,
            'status': str(self.status),
            'progress': self.progress,
            'assigned_at': self.assigned_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'expected_completion_time': self.expected_completion_time.isoformat() if self.expected_completion_time else None,
            'notes': self.notes,
            'feedback': self.feedback,
            'rating': self.rating,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<TaskAssignment(id='{self.id}', task_id='{self.task_id}', student_id='{self.student_id}')>"


class TaskSubmission(AggregateRoot):
    """任务提交实体"""
    
    def __init__(
        self,
        assignment_id: str,
        submitted_by: str,
        content: Dict[str, Any],
        tenant_id: Optional[str] = None,
        status: Optional[SubmissionStatus] = None,
        submitted_at: Optional[datetime] = None,
        revision_count: int = 0,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.assignment_id = assignment_id
        self.submitted_by = submitted_by
        self.content = content
        self.tenant_id = tenant_id
        self.status = status or SubmissionStatus("draft")
        self.submitted_at = submitted_at
        self.revision_count = revision_count
        
        # 扩展字段
        self.attachments: List[Dict[str, Any]] = []
        self.comments: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        
        self._validate()
    
    def _validate(self):
        """验证提交数据"""
        if not self.assignment_id:
            raise ValueError("分配ID不能为空")
        
        if not self.submitted_by:
            raise ValueError("提交者ID不能为空")
        
        if not isinstance(self.content, dict):
            raise ValueError("提交内容必须是字典格式")
    
    def submit(self) -> None:
        """提交任务"""
        if not self.status.can_be_submitted():
            raise ValueError(f"提交状态为{self.status}，无法提交")
        
        self.status = SubmissionStatus("submitted")
        self.submitted_at = datetime.now()
        self.mark_updated()
    
    def revise(self, new_content: Dict[str, Any]) -> None:
        """修订任务提交"""
        if not self.status.is_submitted():
            raise ValueError(f"只有已提交的任务可以修订，当前状态: {self.status}")
        
        self.content = new_content
        self.status = SubmissionStatus("revised")
        self.revision_count += 1
        self.mark_updated()
    
    def accept(self) -> None:
        """接受任务提交"""
        if not self.status.is_submitted() and not self.status.is_revised():
            raise ValueError(f"只有已提交或已修订的任务可以接受，当前状态: {self.status}")
        
        self.status = SubmissionStatus("accepted")
        self.mark_updated()
    
    def reject(self, reason: str) -> None:
        """拒绝任务提交"""
        if not self.status.is_submitted() and not self.status.is_revised():
            raise ValueError(f"只有已提交或已修订的任务可以拒绝，当前状态: {self.status}")
        
        self.status = SubmissionStatus("rejected")
        self.metadata["rejection_reason"] = reason
        self.mark_updated()
    
    def add_attachment(self, file_name: str, file_url: str, file_type: str) -> None:
        """添加附件"""
        attachment = {
            'id': len(self.attachments) + 1,
            'file_name': file_name,
            'file_url': file_url,
            'file_type': file_type,
            'uploaded_at': datetime.now().isoformat(),
        }
        
        self.attachments.append(attachment)
        self.mark_updated()
    
    def add_comment(self, user_id: str, content: str) -> None:
        """添加评论"""
        comment = {
            'id': len(self.comments) + 1,
            'user_id': user_id,
            'content': content,
            'created_at': datetime.now().isoformat(),
        }
        
        self.comments.append(comment)
        self.mark_updated()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'submitted_by': self.submitted_by,
            'tenant_id': self.tenant_id,
            'status': str(self.status),
            'content': self.content,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'revision_count': self.revision_count,
            'attachments': self.attachments,
            'comments': self.comments,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<TaskSubmission(id='{self.id}', assignment_id='{self.assignment_id}', status='{self.status}')>"


class TaskEvaluation(AggregateRoot):
    """任务评估实体"""
    
    def __init__(
        self,
        submission_id: str,
        evaluator_id: str,
        tenant_id: Optional[str] = None,
        status: Optional[EvaluationStatus] = None,
        score: Optional[float] = None,
        feedback: Optional[str] = None,
        evaluated_at: Optional[datetime] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.submission_id = submission_id
        self.evaluator_id = evaluator_id
        self.tenant_id = tenant_id
        self.status = status or EvaluationStatus("pending")
        self.score = score
        self.feedback = feedback
        self.evaluated_at = evaluated_at
        
        # 扩展字段
        self.criteria_scores: Dict[str, float] = {}
        self.recommendations: List[str] = []
        self.metadata: Dict[str, Any] = {}
        
        self._validate()
    
    def _validate(self):
        """验证评估数据"""
        if not self.submission_id:
            raise ValueError("提交ID不能为空")
        
        if not self.evaluator_id:
            raise ValueError("评估者ID不能为空")
        
        if self.score is not None and not 0.0 <= self.score <= 100.0:
            raise ValueError("分数必须在0-100之间")
    
    def complete_evaluation(
        self,
        score: float,
        feedback: str,
        criteria_scores: Optional[Dict[str, float]] = None,
        recommendations: Optional[List[str]] = None
    ) -> None:
        """完成评估"""
        if not self.status.is_pending():
            raise ValueError(f"评估状态为{self.status}，无法完成评估")
        
        if not 0.0 <= score <= 100.0:
            raise ValueError("分数必须在0-100之间")
        
        self.score = score
        self.feedback = feedback
        self.status = EvaluationStatus("completed")
        self.evaluated_at = datetime.now()
        
        if criteria_scores is not None:
            self.criteria_scores = criteria_scores
        
        if recommendations is not None:
            self.recommendations = recommendations
        
        self.mark_updated()
    
    def cancel_evaluation(self, reason: Optional[str] = None) -> None:
        """取消评估"""
        if self.status.is_completed():
            raise ValueError("已完成的评估无法取消")
        
        self.status = EvaluationStatus("cancelled")
        if reason:
            self.metadata["cancellation_reason"] = reason
        
        self.mark_updated()
    
    def add_criteria_score(self, criteria_name: str, score: float) -> None:
        """添加标准得分"""
        if not 0.0 <= score <= 100.0:
            raise ValueError("标准得分必须在0-100之间")
        
        self.criteria_scores[criteria_name] = score
        self.mark_updated()
    
    def add_recommendation(self, recommendation: str) -> None:
        """添加建议"""
        self.recommendations.append(recommendation)
        self.mark_updated()
    
    def calculate_average_criteria_score(self) -> Optional[float]:
        """计算标准平均分"""
        if not self.criteria_scores:
            return None
        
        total = sum(self.criteria_scores.values())
        return total / len(self.criteria_scores)
    
    def is_passed(self, passing_score: float = 60.0) -> bool:
        """检查是否通过"""
        if self.score is None:
            return False
        
        return self.score >= passing_score
    
    def get_rating(self) -> str:
        """获取评级"""
        if self.score is None:
            return "未评估"
        
        if self.score >= 90.0:
            return "卓越"
        elif self.score >= 80.0:
            return "优秀"
        elif self.score >= 70.0:
            return "良好"
        elif self.score >= 60.0:
            return "及格"
        else:
            return "不及格"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'evaluator_id': self.evaluator_id,
            'tenant_id': self.tenant_id,
            'status': str(self.status),
            'score': self.score,
            'feedback': self.feedback,
            'evaluated_at': self.evaluated_at.isoformat() if self.evaluated_at else None,
            'criteria_scores': self.criteria_scores,
            'recommendations': self.recommendations,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<TaskEvaluation(id='{self.id}', submission_id='{self.submission_id}', score={self.score})>"
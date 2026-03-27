"""
任务管理模块 - 数据模型
定义任务相关的数据模型和验证逻辑
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class TaskType(str, Enum):
    """任务类型枚举"""
    HOMEWORK = "homework"
    EXERCISE = "exercise"
    CUSTOM = "custom"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class TaskPriority(str, Enum):
    """任务优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskDifficulty(str, Enum):
    """任务难度枚举"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class AssignmentStatus(str, Enum):
    """任务分配状态枚举"""
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class SubmissionStatus(str, Enum):
    """任务提交状态枚举"""
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    RETURNED = "returned"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class EvaluationStatus(str, Enum):
    """任务评价状态枚举"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class TaskCreateRequest(BaseModel):
    """创建任务请求模型"""
    title: str 
    description: Optional[str] = None
    task_type: TaskType = Field(TaskType.HOMEWORK, description="任务类型")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="任务优先级")
    difficulty: TaskDifficulty = Field(TaskDifficulty.BEGINNER, description="任务难度")
    tags: Optional[List[str]] 
    content: Optional[Dict[str, Any]] = None
    start_time: Optional[datetime] = None
    deadline: Optional[datetime] = None
    estimated_duration: Optional[int] = None
    prerequisites: Optional[str] = None
    completion_criteria: Optional[str] = None
    scoring_criteria: Optional[str] = None
    exercise_type_id: Optional[str] = None


class TaskUpdateRequest(BaseModel):
    """更新任务请求模型"""
    title: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[TaskType] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    difficulty: Optional[TaskDifficulty] = None
    tags: Optional[List[str]] = None
    content: Optional[Dict[str, Any]] = None
    start_time: Optional[datetime] = None
    deadline: Optional[datetime] = None
    estimated_duration: Optional[int] = None
    prerequisites: Optional[str] = None
    completion_criteria: Optional[str] = None
    scoring_criteria: Optional[str] = None


class TaskAssignmentRequest(BaseModel):
    """任务分配请求模型"""
    task_id: str 
    student_id: str 
    assignment_notes: Optional[str] = None
    expected_completion_at: Optional[datetime] = None
    reminder_settings: Optional[Dict[str, Any]] = None


class TaskAssignmentUpdateRequest(BaseModel):
    """任务分配更新请求模型"""
    status: Optional[AssignmentStatus] = None
    progress: Optional[float] = None
    student_notes: Optional[str] = None
    progress_details: Optional[Dict[str, Any]] = None
    expected_completion_at: Optional[datetime] = None


class TaskSubmissionRequest(BaseModel):
    """任务提交请求模型"""
    assignment_id: str 
    content: Dict[str, Any] 
    submission_notes: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] 
    is_final: bool = Field(False, description="是否为最终提交")


class TaskSubmissionReviewRequest(BaseModel):
    """任务提交审核请求模型"""
    status: SubmissionStatus 
    review_notes: Optional[str] = None


class TaskEvaluationRequest(BaseModel):
    """任务评价请求模型"""
    assignment_id: str 
    submission_id: Optional[str] = None
    overall_score: float 
    score_details: Optional[Dict[str, float]] = None
    comments: Optional[str] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    improvement_suggestions: Optional[str] = None
    next_goals: Optional[str] = None
    recommended_for_advancement: bool = Field(False, description="是否推荐进阶")
    recommended_next_task_id: Optional[str] = None


class TaskEvaluationUpdateRequest(BaseModel):
    """任务评价更新请求模型"""
    overall_score: Optional[float] = None
    score_details: Optional[Dict[str, float]] = None
    comments: Optional[str] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    improvement_suggestions: Optional[str] = None
    next_goals: Optional[str] = None
    recommended_for_advancement: Optional[bool] = None
    recommended_next_task_id: Optional[str] = None
    status: Optional[EvaluationStatus] = None


class TaskFilter(BaseModel):
    """任务筛选条件"""
    task_type: Optional[TaskType] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    difficulty: Optional[TaskDifficulty] = None
    creator_id: Optional[str] = None
    tenant_id: Optional[str] = None
    start_time_from: Optional[datetime] = None
    start_time_to: Optional[datetime] = None
    deadline_from: Optional[datetime] = None
    deadline_to: Optional[datetime] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = None


class TaskAssignmentFilter(BaseModel):
    """任务分配筛选条件"""
    task_id: Optional[str] = None
    student_id: Optional[str] = None
    assigner_id: Optional[str] = None
    status: Optional[AssignmentStatus] = None
    tenant_id: Optional[str] = None
    assigned_at_from: Optional[datetime] = None
    assigned_at_to: Optional[datetime] = None
    expected_completion_at_from: Optional[datetime] = None
    expected_completion_at_to: Optional[datetime] = None
    is_overdue: Optional[bool] = None


class TaskAnalyticsRequest(BaseModel):
    """任务分析请求模型"""
    start_date: datetime 
    end_date: datetime 
    tenant_id: Optional[str] = None
    student_id: Optional[str] = None
    task_type: Optional[TaskType] = None
    group_by: Optional[str] = Field("day", description="分组方式：day, week, month, task_type, difficulty")


class TaskSchedulerRequest(BaseModel):
    """任务调度请求模型"""
    student_id: str 
    start_date: datetime 
    end_date: datetime 
    max_tasks_per_day: int = Field(5, ge=1, le=20, description="每天最大任务数")
    consider_difficulty: bool = Field(True, description="是否考虑难度")
    consider_priority: bool = Field(True, description="是否考虑优先级")
    consider_dependencies: bool = Field(True, description="是否考虑依赖关系")


class TaskResponse(BaseModel):
    """任务响应模型"""
    id: str 
    title: str 
    description: Optional[str] = None
    task_type: TaskType 
    status: TaskStatus 
    priority: TaskPriority 
    difficulty: TaskDifficulty 
    tags: List[str] 
    content: Optional[Dict[str, Any]] = None
    start_time: Optional[datetime] = None
    deadline: Optional[datetime] = None
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    creator_id: str 
    tenant_id: str 
    exercise_type_id: Optional[str] = None
    created_at: datetime 
    updated_at: datetime 
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class TaskAssignmentResponse(BaseModel):
    """任务分配响应模型"""
    id: str 
    task_id: str 
    student_id: str 
    assigner_id: str 
    status: AssignmentStatus 
    progress: float 
    assigned_at: datetime 
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expected_completion_at: Optional[datetime] = None
    actual_completion_at: Optional[datetime] = None
    tenant_id: str 
    created_at: datetime 
    updated_at: datetime 
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class TaskSubmissionResponse(BaseModel):
    """任务提交响应模型"""
    id: str 
    assignment_id: str 
    submitter_id: str 
    status: SubmissionStatus 
    content: Dict[str, Any] 
    submitted_at: datetime 
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[str] = None
    version: int 
    is_final: bool 
    tenant_id: str 
    created_at: datetime 
    updated_at: datetime 
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class TaskEvaluationResponse(BaseModel):
    """任务评价响应模型"""
    id: str 
    assignment_id: str 
    submission_id: Optional[str] = None
    evaluator_id: str 
    student_id: str 
    overall_score: float 
    score_grade: str 
    comments: Optional[str] = None
    evaluated_at: datetime 
    status: EvaluationStatus 
    recommended_for_advancement: bool 
    recommended_next_task_id: Optional[str] = None
    tenant_id: str 
    created_at: datetime 
    updated_at: datetime 
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
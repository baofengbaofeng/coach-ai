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
    title: str = Field(..., min_length=1, max_length=200, description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    task_type: TaskType = Field(TaskType.HOMEWORK, description="任务类型")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="任务优先级")
    difficulty: TaskDifficulty = Field(TaskDifficulty.BEGINNER, description="任务难度")
    tags: Optional[List[str]] = Field(default_factory=list, description="任务标签")
    content: Optional[Dict[str, Any]] = Field(None, description="任务内容")
    start_time: Optional[datetime] = Field(None, description="任务开始时间")
    deadline: Optional[datetime] = Field(None, description="任务截止时间")
    estimated_duration: Optional[int] = Field(None, ge=1, description="预计完成时间（分钟）")
    prerequisites: Optional[str] = Field(None, description="任务前置条件")
    completion_criteria: Optional[str] = Field(None, description="任务完成条件")
    scoring_criteria: Optional[str] = Field(None, description="任务评分标准")
    exercise_type_id: Optional[str] = Field(None, description="关联的运动类型ID")


class TaskUpdateRequest(BaseModel):
    """更新任务请求模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    task_type: Optional[TaskType] = Field(None, description="任务类型")
    status: Optional[TaskStatus] = Field(None, description="任务状态")
    priority: Optional[TaskPriority] = Field(None, description="任务优先级")
    difficulty: Optional[TaskDifficulty] = Field(None, description="任务难度")
    tags: Optional[List[str]] = Field(None, description="任务标签")
    content: Optional[Dict[str, Any]] = Field(None, description="任务内容")
    start_time: Optional[datetime] = Field(None, description="任务开始时间")
    deadline: Optional[datetime] = Field(None, description="任务截止时间")
    estimated_duration: Optional[int] = Field(None, ge=1, description="预计完成时间（分钟）")
    prerequisites: Optional[str] = Field(None, description="任务前置条件")
    completion_criteria: Optional[str] = Field(None, description="任务完成条件")
    scoring_criteria: Optional[str] = Field(None, description="任务评分标准")


class TaskAssignmentRequest(BaseModel):
    """任务分配请求模型"""
    task_id: str = Field(..., description="任务ID")
    student_id: str = Field(..., description="学员ID")
    assignment_notes: Optional[str] = Field(None, description="分配备注")
    expected_completion_at: Optional[datetime] = Field(None, description="预计完成时间")
    reminder_settings: Optional[Dict[str, Any]] = Field(None, description="提醒设置")


class TaskAssignmentUpdateRequest(BaseModel):
    """任务分配更新请求模型"""
    status: Optional[AssignmentStatus] = Field(None, description="分配状态")
    progress: Optional[float] = Field(None, ge=0, le=100, description="进度百分比")
    student_notes: Optional[str] = Field(None, description="学员备注")
    progress_details: Optional[Dict[str, Any]] = Field(None, description="进度详情")
    expected_completion_at: Optional[datetime] = Field(None, description="预计完成时间")


class TaskSubmissionRequest(BaseModel):
    """任务提交请求模型"""
    assignment_id: str = Field(..., description="任务分配ID")
    content: Dict[str, Any] = Field(..., description="提交内容")
    submission_notes: Optional[str] = Field(None, description="提交备注")
    attachments: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="附件列表")
    is_final: bool = Field(False, description="是否为最终提交")


class TaskSubmissionReviewRequest(BaseModel):
    """任务提交审核请求模型"""
    status: SubmissionStatus = Field(..., description="审核状态")
    review_notes: Optional[str] = Field(None, description="审核备注")


class TaskEvaluationRequest(BaseModel):
    """任务评价请求模型"""
    assignment_id: str = Field(..., description="任务分配ID")
    submission_id: Optional[str] = Field(None, description="任务提交ID")
    overall_score: float = Field(..., ge=0, le=100, description="总体评分")
    score_details: Optional[Dict[str, float]] = Field(None, description="评分详情")
    comments: Optional[str] = Field(None, description="评语")
    strengths: Optional[str] = Field(None, description="优点")
    areas_for_improvement: Optional[str] = Field(None, description="待改进点")
    improvement_suggestions: Optional[str] = Field(None, description="改进建议")
    next_goals: Optional[str] = Field(None, description="下次目标")
    recommended_for_advancement: bool = Field(False, description="是否推荐进阶")
    recommended_next_task_id: Optional[str] = Field(None, description="推荐的下个任务ID")


class TaskEvaluationUpdateRequest(BaseModel):
    """任务评价更新请求模型"""
    overall_score: Optional[float] = Field(None, ge=0, le=100, description="总体评分")
    score_details: Optional[Dict[str, float]] = Field(None, description="评分详情")
    comments: Optional[str] = Field(None, description="评语")
    strengths: Optional[str] = Field(None, description="优点")
    areas_for_improvement: Optional[str] = Field(None, description="待改进点")
    improvement_suggestions: Optional[str] = Field(None, description="改进建议")
    next_goals: Optional[str] = Field(None, description="下次目标")
    recommended_for_advancement: Optional[bool] = Field(None, description="是否推荐进阶")
    recommended_next_task_id: Optional[str] = Field(None, description="推荐的下个任务ID")
    status: Optional[EvaluationStatus] = Field(None, description="评价状态")


class TaskFilter(BaseModel):
    """任务筛选条件"""
    task_type: Optional[TaskType] = Field(None, description="任务类型")
    status: Optional[TaskStatus] = Field(None, description="任务状态")
    priority: Optional[TaskPriority] = Field(None, description="任务优先级")
    difficulty: Optional[TaskDifficulty] = Field(None, description="任务难度")
    creator_id: Optional[str] = Field(None, description="创建者ID")
    tenant_id: Optional[str] = Field(None, description="租户ID")
    start_time_from: Optional[datetime] = Field(None, description="开始时间从")
    start_time_to: Optional[datetime] = Field(None, description="开始时间到")
    deadline_from: Optional[datetime] = Field(None, description="截止时间从")
    deadline_to: Optional[datetime] = Field(None, description="截止时间到")
    tags: Optional[List[str]] = Field(None, description="标签")
    search: Optional[str] = Field(None, description="搜索关键词")


class TaskAssignmentFilter(BaseModel):
    """任务分配筛选条件"""
    task_id: Optional[str] = Field(None, description="任务ID")
    student_id: Optional[str] = Field(None, description="学员ID")
    assigner_id: Optional[str] = Field(None, description="分配者ID")
    status: Optional[AssignmentStatus] = Field(None, description="分配状态")
    tenant_id: Optional[str] = Field(None, description="租户ID")
    assigned_at_from: Optional[datetime] = Field(None, description="分配时间从")
    assigned_at_to: Optional[datetime] = Field(None, description="分配时间到")
    expected_completion_at_from: Optional[datetime] = Field(None, description="预计完成时间从")
    expected_completion_at_to: Optional[datetime] = Field(None, description="预计完成时间到")
    is_overdue: Optional[bool] = Field(None, description="是否过期")


class TaskAnalyticsRequest(BaseModel):
    """任务分析请求模型"""
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    tenant_id: Optional[str] = Field(None, description="租户ID")
    student_id: Optional[str] = Field(None, description="学员ID")
    task_type: Optional[TaskType] = Field(None, description="任务类型")
    group_by: Optional[str] = Field("day", description="分组方式：day, week, month, task_type, difficulty")


class TaskSchedulerRequest(BaseModel):
    """任务调度请求模型"""
    student_id: str = Field(..., description="学员ID")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    max_tasks_per_day: int = Field(5, ge=1, le=20, description="每天最大任务数")
    consider_difficulty: bool = Field(True, description="是否考虑难度")
    consider_priority: bool = Field(True, description="是否考虑优先级")
    consider_dependencies: bool = Field(True, description="是否考虑依赖关系")


class TaskResponse(BaseModel):
    """任务响应模型"""
    id: str = Field(..., description="任务ID")
    title: str = Field(..., description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    task_type: TaskType = Field(..., description="任务类型")
    status: TaskStatus = Field(..., description="任务状态")
    priority: TaskPriority = Field(..., description="任务优先级")
    difficulty: TaskDifficulty = Field(..., description="任务难度")
    tags: List[str] = Field(default_factory=list, description="任务标签")
    content: Optional[Dict[str, Any]] = Field(None, description="任务内容")
    start_time: Optional[datetime] = Field(None, description="任务开始时间")
    deadline: Optional[datetime] = Field(None, description="任务截止时间")
    estimated_duration: Optional[int] = Field(None, description="预计完成时间（分钟）")
    actual_duration: Optional[int] = Field(None, description="实际完成时间（分钟）")
    creator_id: str = Field(..., description="创建者ID")
    tenant_id: str = Field(..., description="租户ID")
    exercise_type_id: Optional[str] = Field(None, description="关联的运动类型ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class TaskAssignmentResponse(BaseModel):
    """任务分配响应模型"""
    id: str = Field(..., description="分配ID")
    task_id: str = Field(..., description="任务ID")
    student_id: str = Field(..., description="学员ID")
    assigner_id: str = Field(..., description="分配者ID")
    status: AssignmentStatus = Field(..., description="分配状态")
    progress: float = Field(..., description="进度百分比")
    assigned_at: datetime = Field(..., description="分配时间")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    expected_completion_at: Optional[datetime] = Field(None, description="预计完成时间")
    actual_completion_at: Optional[datetime] = Field(None, description="实际完成时间")
    tenant_id: str = Field(..., description="租户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class TaskSubmissionResponse(BaseModel):
    """任务提交响应模型"""
    id: str = Field(..., description="提交ID")
    assignment_id: str = Field(..., description="任务分配ID")
    submitter_id: str = Field(..., description="提交者ID")
    status: SubmissionStatus = Field(..., description="提交状态")
    content: Dict[str, Any] = Field(..., description="提交内容")
    submitted_at: datetime = Field(..., description="提交时间")
    reviewed_at: Optional[datetime] = Field(None, description="审核时间")
    reviewer_id: Optional[str] = Field(None, description="审核者ID")
    version: int = Field(..., description="版本号")
    is_final: bool = Field(..., description="是否为最终提交")
    tenant_id: str = Field(..., description="租户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class TaskEvaluationResponse(BaseModel):
    """任务评价响应模型"""
    id: str = Field(..., description="评价ID")
    assignment_id: str = Field(..., description="任务分配ID")
    submission_id: Optional[str] = Field(None, description="任务提交ID")
    evaluator_id: str = Field(..., description="评价者ID")
    student_id: str = Field(..., description="被评价者ID")
    overall_score: float = Field(..., description="总体评分")
    score_grade: str = Field(..., description="评分等级")
    comments: Optional[str] = Field(None, description="评语")
    evaluated_at: datetime = Field(..., description="评价时间")
    status: EvaluationStatus = Field(..., description="评价状态")
    recommended_for_advancement: bool = Field(..., description="是否推荐进阶")
    recommended_next_task_id: Optional[str] = Field(None, description="推荐的下个任务ID")
    tenant_id: str = Field(..., description="租户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
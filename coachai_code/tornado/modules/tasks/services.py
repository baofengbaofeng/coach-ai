"""
任务管理模块 - 服务层
提供任务相关的业务逻辑服务
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func

from coachai_code.database.models import (
    Task, TaskAssignment, TaskSubmission, TaskEvaluation,
    User, Tenant, ExerciseType
)
from .models import (
    TaskCreateRequest, TaskUpdateRequest, TaskAssignmentRequest,
    TaskAssignmentUpdateRequest, TaskSubmissionRequest, TaskSubmissionReviewRequest,
    TaskEvaluationRequest, TaskEvaluationUpdateRequest, TaskFilter,
    TaskAssignmentFilter, TaskAnalyticsRequest, TaskSchedulerRequest,
    TaskType, TaskStatus, AssignmentStatus, SubmissionStatus, EvaluationStatus
)

logger = logging.getLogger(__name__)


class TaskService:
    """任务服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_task(self, request: TaskCreateRequest, creator_id: str, tenant_id: str) -> Task:
        """
        创建任务
        
        Args:
            request: 创建任务请求
            creator_id: 创建者ID
            tenant_id: 租户ID
            
        Returns:
            Task: 创建的任务对象
        """
        try:
            # 验证关联的运动类型
            exercise_type = None
            if request.exercise_type_id:
                exercise_type = self.db.query(ExerciseType).filter(
                    ExerciseType.id == request.exercise_type_id,
                    ExerciseType.tenant_id == tenant_id
                ).first()
                if not exercise_type:
                    raise ValueError(f"Exercise type not found: {request.exercise_type_id}")
            
            # 创建任务
            task = Task(
                title=request.title,
                description=request.description,
                task_type=request.task_type.value,
                status='draft',
                priority=request.priority.value,
                difficulty=request.difficulty.value,
                tags=request.tags,
                content=request.content,
                start_time=request.start_time,
                deadline=request.deadline,
                estimated_duration=request.estimated_duration,
                prerequisites=request.prerequisites,
                completion_criteria=request.completion_criteria,
                scoring_criteria=request.scoring_criteria,
                creator_id=creator_id,
                tenant_id=tenant_id,
                exercise_type_id=request.exercise_type_id
            )
            
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
            
            logger.info(f"Task created: {task.id} by {creator_id}")
            return task
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create task: {str(e)}")
            raise
    
    def get_task(self, task_id: str, tenant_id: str) -> Optional[Task]:
        """
        获取任务
        
        Args:
            task_id: 任务ID
            tenant_id: 租户ID
            
        Returns:
            Optional[Task]: 任务对象，如果不存在则返回None
        """
        return self.db.query(Task).filter(
            Task.id == task_id,
            Task.tenant_id == tenant_id
        ).first()
    
    def update_task(self, task_id: str, request: TaskUpdateRequest, tenant_id: str) -> Optional[Task]:
        """
        更新任务
        
        Args:
            task_id: 任务ID
            request: 更新任务请求
            tenant_id: 租户ID
            
        Returns:
            Optional[Task]: 更新后的任务对象，如果不存在则返回None
        """
        try:
            task = self.get_task(task_id, tenant_id)
            if not task:
                return None
            
            # 更新字段
            if request.title is not None:
                task.title = request.title
            if request.description is not None:
                task.description = request.description
            if request.task_type is not None:
                task.task_type = request.task_type.value
            if request.status is not None:
                task.status = request.status.value
            if request.priority is not None:
                task.priority = request.priority.value
            if request.difficulty is not None:
                task.difficulty = request.difficulty.value
            if request.tags is not None:
                task.tags = request.tags
            if request.content is not None:
                task.content = request.content
            if request.start_time is not None:
                task.start_time = request.start_time
            if request.deadline is not None:
                task.deadline = request.deadline
            if request.estimated_duration is not None:
                task.estimated_duration = request.estimated_duration
            if request.prerequisites is not None:
                task.prerequisites = request.prerequisites
            if request.completion_criteria is not None:
                task.completion_criteria = request.completion_criteria
            if request.scoring_criteria is not None:
                task.scoring_criteria = request.scoring_criteria
            
            self.db.commit()
            self.db.refresh(task)
            
            logger.info(f"Task updated: {task_id}")
            return task
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update task {task_id}: {str(e)}")
            raise
    
    def delete_task(self, task_id: str, tenant_id: str) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            tenant_id: 租户ID
            
        Returns:
            bool: 是否成功删除
        """
        try:
            task = self.get_task(task_id, tenant_id)
            if not task:
                return False
            
            # 检查是否有分配记录
            assignments = self.db.query(TaskAssignment).filter(
                TaskAssignment.task_id == task_id
            ).count()
            
            if assignments > 0:
                # 如果有分配记录，只标记为已删除
                task.deleted_at = datetime.utcnow()
            else:
                # 如果没有分配记录，直接删除
                self.db.delete(task)
            
            self.db.commit()
            logger.info(f"Task deleted: {task_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete task {task_id}: {str(e)}")
            return False
    
    def list_tasks(self, filter_params: TaskFilter, tenant_id: str, page: int = 1, page_size: int = 20) -> Tuple[List[Task], int]:
        """
        列出任务
        
        Args:
            filter_params: 筛选条件
            tenant_id: 租户ID
            page: 页码
            page_size: 每页大小
            
        Returns:
            Tuple[List[Task], int]: 任务列表和总数
        """
        query = self.db.query(Task).filter(Task.tenant_id == tenant_id)
        
        # 应用筛选条件
        if filter_params.task_type:
            query = query.filter(Task.task_type == filter_params.task_type.value)
        if filter_params.status:
            query = query.filter(Task.status == filter_params.status.value)
        if filter_params.priority:
            query = query.filter(Task.priority == filter_params.priority.value)
        if filter_params.difficulty:
            query = query.filter(Task.difficulty == filter_params.difficulty.value)
        if filter_params.creator_id:
            query = query.filter(Task.creator_id == filter_params.creator_id)
        if filter_params.start_time_from:
            query = query.filter(Task.start_time >= filter_params.start_time_from)
        if filter_params.start_time_to:
            query = query.filter(Task.start_time <= filter_params.start_time_to)
        if filter_params.deadline_from:
            query = query.filter(Task.deadline >= filter_params.deadline_from)
        if filter_params.deadline_to:
            query = query.filter(Task.deadline <= filter_params.deadline_to)
        if filter_params.tags:
            # 使用JSON_CONTAINS查询标签
            for tag in filter_params.tags:
                query = query.filter(Task.tags.contains([tag]))
        if filter_params.search:
            search_term = f"%{filter_params.search}%"
            query = query.filter(
                or_(
                    Task.title.like(search_term),
                    Task.description.like(search_term)
                )
            )
        
        # 获取总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        query = query.order_by(desc(Task.created_at)).offset(offset).limit(page_size)
        
        return query.all(), total
    
    def activate_task(self, task_id: str, tenant_id: str) -> Optional[Task]:
        """
        激活任务
        
        Args:
            task_id: 任务ID
            tenant_id: 租户ID
            
        Returns:
            Optional[Task]: 激活后的任务对象
        """
        task = self.get_task(task_id, tenant_id)
        if not task:
            return None
        
        if task.status == 'draft':
            task.status = 'active'
            self.db.commit()
            self.db.refresh(task)
            logger.info(f"Task activated: {task_id}")
        
        return task


class TaskAssignmentService:
    """任务分配服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def assign_task(self, request: TaskAssignmentRequest, assigner_id: str, tenant_id: str) -> TaskAssignment:
        """
        分配任务
        
        Args:
            request: 任务分配请求
            assigner_id: 分配者ID
            tenant_id: 租户ID
            
        Returns:
            TaskAssignment: 任务分配对象
        """
        try:
            # 验证任务
            task = self.db.query(Task).filter(
                Task.id == request.task_id,
                Task.tenant_id == tenant_id,
                Task.status == 'active'
            ).first()
            
            if not task:
                raise ValueError(f"Task not found or not active: {request.task_id}")
            
            # 验证学员
            student = self.db.query(User).filter(
                User.id == request.student_id,
                User.tenant_id == tenant_id
            ).first()
            
            if not student:
                raise ValueError(f"Student not found: {request.student_id}")
            
            # 检查是否已经分配
            existing_assignment = self.db.query(TaskAssignment).filter(
                TaskAssignment.task_id == request.task_id,
                TaskAssignment.student_id == request.student_id,
                TaskAssignment.tenant_id == tenant_id
            ).first()
            
            if existing_assignment:
                raise ValueError(f"Task already assigned to student: {request.task_id}")
            
            # 创建分配记录
            assignment = TaskAssignment(
                task_id=request.task_id,
                student_id=request.student_id,
                assigner_id=assigner_id,
                status='assigned',
                progress=0.0,
                assignment_notes=request.assignment_notes,
                expected_completion_at=request.expected_completion_at,
                reminder_settings=request.reminder_settings,
                tenant_id=tenant_id
            )
            
            self.db.add(assignment)
            self.db.commit()
            self.db.refresh(assignment)
            
            logger.info(f"Task assigned: {request.task_id} to {request.student_id} by {assigner_id}")
            return assignment
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to assign task: {str(e)}")
            raise
    
    def get_assignment(self, assignment_id: str, tenant_id: str) -> Optional[TaskAssignment]:
        """
        获取任务分配
        
        Args:
            assignment_id: 分配ID
            tenant_id: 租户ID
            
        Returns:
            Optional[TaskAssignment]: 任务分配对象
        """
        return self.db.query(TaskAssignment).filter(
            TaskAssignment.id == assignment_id,
            TaskAssignment.tenant_id == tenant_id
        ).first()
    
    def update_assignment(self, assignment_id: str, request: TaskAssignmentUpdateRequest, tenant_id: str) -> Optional[TaskAssignment]:
        """
        更新任务分配
        
        Args:
            assignment_id: 分配ID
            request: 更新请求
            tenant_id: 租户ID
            
        Returns:
            Optional[TaskAssignment]: 更新后的任务分配对象
        """
        try:
            assignment = self.get_assignment(assignment_id, tenant_id)
            if not assignment:
                return None
            
            # 更新字段
            if request.status is not None:
                assignment.status = request.status.value
            if request.progress is not None:
                assignment.update_progress(request.progress, request.progress_details)
            if request.student_notes is not None:
                assignment.student_notes = request.student_notes
            if request.expected_completion_at is not None:
                assignment.expected_completion_at = request.expected_completion_at
            
            self.db.commit()
            self.db.refresh(assignment)
            
            logger.info(f"Assignment updated: {assignment_id}")
            return assignment
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update assignment {assignment_id}: {str(e)}")
            raise
    
    def list_assignments(self, filter_params: TaskAssignmentFilter, tenant_id: str, page: int = 1, page_size: int = 20) -> Tuple[List[TaskAssignment], int]:
        """
        列出任务分配
        
        Args:
            filter_params: 筛选条件
            tenant_id: 租户ID
            page: 页码
            page_size: 每页大小
            
        Returns:
            Tuple[List[TaskAssignment], int]: 分配列表和总数
        """
        query = self.db.query(TaskAssignment).filter(TaskAssignment.tenant_id == tenant_id)
        
        # 应用筛选条件
        if filter_params.task_id:
            query = query.filter(TaskAssignment.task_id == filter_params.task_id)
        if filter_params.student_id:
            query = query.filter(TaskAssignment.student_id == filter_params.student_id)
        if filter_params.assigner_id:
            query = query.filter(TaskAssignment.assigner_id == filter_params.assigner_id)
        if filter_params.status:
            query = query.filter(TaskAssignment.status == filter_params.status.value)
        if filter_params.assigned_at_from:
            query = query.filter(TaskAssignment.assigned_at >= filter_params.assigned_at_from)
        if filter_params.assigned_at_to:
            query = query.filter(TaskAssignment.assigned_at <= filter_params.assigned_at_to)
        if filter_params.expected_completion_at_from:
            query = query.filter(TaskAssignment.expected_completion_at >= filter_params.expected_completion_at_from)
        if filter_params.expected_completion_at_to:
            query = query.filter(TaskAssignment.expected_completion_at <= filter_params.expected_completion_at_to)
        if filter_params.is_overdue is not None:
            if filter_params.is_overdue:
                query = query.filter(
                    TaskAssignment.expected_completion_at < datetime.utcnow(),
                    TaskAssignment.status.in_(['assigned', 'in_progress'])
                )
            else:
                query = query.filter(
                    or_(
                        TaskAssignment.expected_completion_at >= datetime.utcnow(),
                        TaskAssignment.status.in_(['completed', 'cancelled'])
                    )
                )
        
        # 获取总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        query = query.order_by(desc(TaskAssignment.created_at)).offset(offset).limit(page_size)
        
        return query.all(), total
    
    def get_student_assignments(self, student_id: str, tenant_id: str, include_completed: bool = False) -> List[TaskAssignment]:
        """
        获取学员的任务分配
        
        Args:
            student_id: 学员ID
            tenant_id: 租户ID
            include_completed: 是否包含已完成的任务
            
        Returns:
            List[TaskAssignment]: 任务分配列表
        """
        query = self.db.query(TaskAssignment).filter(
            TaskAssignment.student_id == student_id,
            TaskAssignment.tenant_id == tenant_id
        )
        
        if not include_completed:
            query = query.filter(TaskAssignment.status.in_(['assigned', 'in_progress']))
        
        return query.order_by(
            asc(TaskAssignment.expected_completion_at),
            desc(TaskAssignment.priority)
        ).all()


class TaskSubmissionService:
    """任务提交服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def submit_task(self, request: TaskSubmissionRequest, submitter_id: str, tenant_id: str) -> TaskSubmission:
        """
        提交任务
        
        Args:
            request: 任务提交请求
            submitter_id: 提交者ID
            tenant_id: 租户ID
            
        Returns:
            TaskSubmission: 任务提交对象
        """
        try:
            # 验证任务分配
            assignment = self.db.query(TaskAssignment).filter(
                TaskAssignment.id == request.assignment_id,
                TaskAssignment.student_id == submitter_id,
                TaskAssignment.tenant_id == tenant_id,
                TaskAssignment.status.in_(['assigned', 'in_progress'])
            ).first()
            
            if not assignment:
                raise ValueError(f"Assignment not found or not available for submission: {request.assignment_id}")
            
            # 获取当前版本号
            latest_submission = self.db.query(TaskSubmission).filter(
                TaskSubmission.assignment_id == request.assignment_id
            ).order_by(desc(TaskSubmission.version)).first()
            
            version = 1
            if latest_submission:
                version = latest_submission.version + 1
            
            # 创建提交记录
            submission = TaskSubmission(
                assignment_id=request.assignment_id,
                submitter_id=submitter_id,
                status='submitted',
                content=request.content,
                submission_notes=request.submission_notes,
                attachments=request.attachments,
                version=version,
                is_final=request.is_final,
                tenant_id=tenant_id
            )
            
            # 更新任务分配进度
            if request.is_final:
                assignment.update_progress(90, {'final_submission': True})
            else:
                assignment.update_progress(50, {'draft_submission': True})
            
            self.db.add(submission)
            self.db.commit()
            self.db.refresh(submission)
            
            logger.info(f"Task submitted: assignment={request.assignment_id}, version={version} by {submitter_id}")
            return submission
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to submit task: {str(e)}")
            raise
    
    def get_submission(self, submission_id: str, tenant_id: str) -> Optional[TaskSubmission]:
        """
        获取任务提交
        
        Args:
            submission_id: 提交ID
            tenant_id: 租户ID
            
        Returns:
            Optional[TaskSubmission]: 任务提交对象
        """
        return self.db.query(TaskSubmission).filter(
            TaskSubmission.id == submission_id,
            TaskSubmission.tenant_id == tenant_id
        ).first()
    
    def review_submission(self, submission_id: str, request: TaskSubmissionReviewRequest, reviewer_id: str, tenant_id: str) -> Optional[TaskSubmission]:
        """
        审核任务提交
        
        Args:
            submission_id: 提交ID
            request: 审核请求
            reviewer_id: 审核者ID
            tenant_id: 租户ID
            
        Returns:
            Optional[TaskSubmission]: 审核后的任务提交对象
        """
        try:
            submission = self.get_submission(submission_id, tenant_id)
            if not submission:
                return None
            
            # 检查是否可以审核
            if not submission.can_be_reviewed():
                raise ValueError("Submission cannot be reviewed")
            
            # 执行审核
            submission.review(reviewer_id, request.status.value, request.review_notes)
            
            self.db.commit()
            self.db.refresh(submission)
            
            logger.info(f"Submission reviewed: {submission_id} by {reviewer_id}")
            return submission
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to review submission {submission_id}: {str(e)}")
            raise
    
    def list_submissions(self, assignment_id: Optional[str] = None, submitter_id: Optional[str] = None,
                        status: Optional[str] = None, tenant_id: str = None,
                        page: int = 1, page_size: int = 20) -> Tuple[List[TaskSubmission], int]:
        """
        列出任务提交
        
        Args:
            assignment_id: 任务分配ID
            submitter_id: 提交者ID
            status: 提交状态
            tenant_id: 租户ID
            page: 页码
            page_size: 每页大小
            
        Returns:
            Tuple[List[TaskSubmission], int]: 提交列表和总数
        """
        query = self.db.query(TaskSubmission)
        
        if tenant_id:
            query = query.filter(TaskSubmission.tenant_id == tenant_id)
        if assignment_id:
            query = query.filter(TaskSubmission.assignment_id == assignment_id)
        if submitter_id:
            query = query.filter(TaskSubmission.submitter_id == submitter_id)
        if status:
            query = query.filter(TaskSubmission.status == status)
        
        # 获取总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        query = query.order_by(desc(TaskSubmission.submitted_at)).offset(offset).limit(page_size)
        
        return query.all(), total


class TaskEvaluationService:
    """任务评价服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_evaluation(self, request: TaskEvaluationRequest, evaluator_id: str, tenant_id: str) -> TaskEvaluation:
        """
        创建任务评价
        
        Args:
            request: 任务评价请求
            evaluator_id: 评价者ID
            tenant_id: 租户ID
            
        Returns:
            TaskEvaluation: 任务评价对象
        """
        try:
            # 验证任务分配
            assignment = self.db.query(TaskAssignment).filter(
                TaskAssignment.id == request.assignment_id,
                TaskAssignment.tenant_id == tenant_id,
                TaskAssignment.status == 'completed'
            ).first()
            
            if not assignment:
                raise ValueError(f"Assignment not found or not completed: {request.assignment_id}")
            
            # 验证提交（如果提供了提交ID）
            if request.submission_id:
                submission = self.db.query(TaskSubmission).filter(
                    TaskSubmission.id == request.submission_id,
                    TaskSubmission.assignment_id == request.assignment_id,
                    TaskSubmission.tenant_id == tenant_id
                ).first()
                
                if not submission:
                    raise ValueError(f"Submission not found: {request.submission_id}")
            
            # 验证学员
            student = self.db.query(User).filter(
                User.id == assignment.student_id,
                User.tenant_id == tenant_id
            ).first()
            
            if not student:
                raise ValueError(f"Student not found: {assignment.student_id}")
            
            # 创建评价记录
            evaluation = TaskEvaluation(
                assignment_id=request.assignment_id,
                submission_id=request.submission_id,
                evaluator_id=evaluator_id,
                student_id=assignment.student_id,
                overall_score=request.overall_score,
                score_details=request.score_details,
                comments=request.comments,
                strengths=request.strengths,
                areas_for_improvement=request.areas_for_improvement,
                improvement_suggestions=request.improvement_suggestions,
                next_goals=request.next_goals,
                recommended_for_advancement=request.recommended_for_advancement,
                recommended_next_task_id=request.recommended_next_task_id,
                status='draft',
                tenant_id=tenant_id
            )
            
            self.db.add(evaluation)
            self.db.commit()
            self.db.refresh(evaluation)
            
            logger.info(f"Evaluation created: for assignment={request.assignment_id} by {evaluator_id}")
            return evaluation
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create evaluation: {str(e)}")
            raise
    
    def get_evaluation(self, evaluation_id: str, tenant_id: str) -> Optional[TaskEvaluation]:
        """
        获取任务评价
        
        Args:
            evaluation_id: 评价ID
            tenant_id: 租户ID
            
        Returns:
            Optional[TaskEvaluation]: 任务评价对象
        """
        return self.db.query(TaskEvaluation).filter(
            TaskEvaluation.id == evaluation_id,
            TaskEvaluation.tenant_id == tenant_id
        ).first()
    
    def update_evaluation(self, evaluation_id: str, request: TaskEvaluationUpdateRequest, tenant_id: str) -> Optional[TaskEvaluation]:
        """
        更新任务评价
        
        Args:
            evaluation_id: 评价ID
            request: 更新请求
            tenant_id: 租户ID
            
        Returns:
            Optional[TaskEvaluation]: 更新后的任务评价对象
        """
        try:
            evaluation = self.get_evaluation(evaluation_id, tenant_id)
            if not evaluation:
                return None
            
            # 更新字段
            if request.overall_score is not None:
                evaluation.overall_score = request.overall_score
            if request.score_details is not None:
                evaluation.update_score_details(request.score_details)
            if request.comments is not None:
                evaluation.comments = request.comments
            if request.strengths is not None:
                evaluation.strengths = request.strengths
            if request.areas_for_improvement is not None:
                evaluation.areas_for_improvement = request.areas_for_improvement
            if request.improvement_suggestions is not None:
                evaluation.improvement_suggestions = request.improvement_suggestions
            if request.next_goals is not None:
                evaluation.next_goals = request.next_goals
            if request.recommended_for_advancement is not None:
                evaluation.recommended_for_advancement = request.recommended_for_advancement
            if request.recommended_next_task_id is not None:
                evaluation.recommended_next_task_id = request.recommended_next_task_id
            if request.status is not None:
                evaluation.status = request.status.value
            
            self.db.commit()
            self.db.refresh(evaluation)
            
            logger.info(f"Evaluation updated: {evaluation_id}")
            return evaluation
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update evaluation {evaluation_id}: {str(e)}")
            raise
    
    def publish_evaluation(self, evaluation_id: str, tenant_id: str) -> Optional[TaskEvaluation]:
        """
        发布任务评价
        
        Args:
            evaluation_id: 评价ID
            tenant_id: 租户ID
            
        Returns:
            Optional[TaskEvaluation]: 发布后的任务评价对象
        """
        evaluation = self.get_evaluation(evaluation_id, tenant_id)
        if not evaluation:
            return None
        
        if evaluation.publish():
            self.db.commit()
            self.db.refresh(evaluation)
            logger.info(f"Evaluation published: {evaluation_id}")
        
        return evaluation
    
    def list_evaluations(self, assignment_id: Optional[str] = None, student_id: Optional[str] = None,
                        evaluator_id: Optional[str] = None, status: Optional[str] = None,
                        tenant_id: str = None, page: int = 1, page_size: int = 20) -> Tuple[List[TaskEvaluation], int]:
        """
        列出任务评价
        
        Args:
            assignment_id: 任务分配ID
            student_id: 学员ID
            evaluator_id: 评价者ID
            status: 评价状态
            tenant_id: 租户ID
            page: 页码
            page_size: 每页大小
            
        Returns:
            Tuple[List[TaskEvaluation], int]: 评价列表和总数
        """
        query = self.db.query(TaskEvaluation)
        
        if tenant_id:
            query = query.filter(TaskEvaluation.tenant_id == tenant_id)
        if assignment_id:
            query = query.filter(TaskEvaluation.assignment_id == assignment_id)
        if student_id:
            query = query.filter(TaskEvaluation.student_id == student_id)
        if evaluator_id:
            query = query.filter(TaskEvaluation.evaluator_id == evaluator_id)
        if status:
            query = query.filter(TaskEvaluation.status == status)
        
        # 获取总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        query = query.order_by(desc(TaskEvaluation.evaluated_at)).offset(offset).limit(page_size)
        
        return query.all(), total


class TaskSchedulerService:
    """任务调度服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def schedule_tasks(self, request: TaskSchedulerRequest, tenant_id: str) -> List[Dict[str, Any]]:
        """
        智能调度任务
        
        Args:
            request: 调度请求
            tenant_id: 租户ID
            
        Returns:
            List[Dict[str, Any]]: 调度结果
        """
        try:
            # 获取学员的待分配任务
            pending_assignments = self.db.query(TaskAssignment).filter(
                TaskAssignment.student_id == request.student_id,
                TaskAssignment.tenant_id == tenant_id,
                TaskAssignment.status.in_(['assigned', 'in_progress'])
            ).all()
            
            # 获取学员的历史表现
            completed_evaluations = self.db.query(TaskEvaluation).filter(
                TaskEvaluation.student_id == request.student_id,
                TaskEvaluation.tenant_id == tenant_id,
                TaskEvaluation.status == 'published'
            ).all()
            
            # 获取可用的任务
            available_tasks = self.db.query(Task).filter(
                Task.tenant_id == tenant_id,
                Task.status == 'active',
                Task.start_time <= request.end_date,
                or_(Task.deadline.is_(None), Task.deadline >= request.start_date)
            ).all()
            
            # 智能调度算法
            schedule = self._intelligent_scheduling(
                pending_assignments,
                completed_evaluations,
                available_tasks,
                request
            )
            
            logger.info(f"Tasks scheduled for student {request.student_id}: {len(schedule)} tasks")
            return schedule
            
        except Exception as e:
            logger.error(f"Failed to schedule tasks: {str(e)}")
            raise
    
    def _intelligent_scheduling(self, pending_assignments, completed_evaluations, available_tasks, request):
        """
        智能调度算法
        
        Args:
            pending_assignments: 待处理的任务分配
            completed_evaluations: 已完成的任务评价
            available_tasks: 可用的任务
            request: 调度请求
            
        Returns:
            List[Dict[str, Any]]: 调度结果
        """
        schedule = []
        
        # 1. 优先安排已分配但未开始的任务
        for assignment in pending_assignments:
            if assignment.status == 'assigned':
                schedule.append({
                    'type': 'existing_assignment',
                    'assignment_id': assignment.id,
                    'task_id': assignment.task_id,
                    'priority': 'high',
                    'reason': 'Already assigned but not started'
                })
        
        # 2. 分析学员能力
        student_ability = self._analyze_student_ability(completed_evaluations)
        
        # 3. 筛选适合学员能力的任务
        suitable_tasks = []
        for task in available_tasks:
            # 检查是否已经分配
            already_assigned = any(a.task_id == task.id for a in pending_assignments)
            if already_assigned:
                continue
            
            # 检查任务难度是否适合
            if request.consider_difficulty:
                if not self._is_task_suitable_for_ability(task, student_ability):
                    continue
            
            suitable_tasks.append(task)
        
        # 4. 根据优先级和依赖关系排序
        sorted_tasks = self._sort_tasks_by_priority(suitable_tasks, request)
        
        # 5. 分配到时间窗口
        schedule.extend(self._allocate_to_time_window(sorted_tasks, request))
        
        return schedule
    
    def _analyze_student_ability(self, completed_evaluations):
        """
        分析学员能力
        
        Args:
            completed_evaluations: 已完成的任务评价
            
        Returns:
            Dict[str, Any]: 学员能力分析
        """
        if not completed_evaluations:
            return {
                'overall_score': 0,
                'difficulty_level': 'beginner',
                'strengths': [],
                'weaknesses': []
            }
        
        total_score = sum(eval.overall_score for eval in completed_evaluations)
        avg_score = total_score / len(completed_evaluations)
        
        # 根据平均分确定难度级别
        if avg_score >= 85:
            difficulty_level = 'advanced'
        elif avg_score >= 70:
            difficulty_level = 'intermediate'
        else:
            difficulty_level = 'beginner'
        
        return {
            'overall_score': avg_score,
            'difficulty_level': difficulty_level,
            'strengths': ['基础扎实'],  # 简化处理
            'weaknesses': ['需要更多练习']  # 简化处理
        }
    
    def _is_task_suitable_for_ability(self, task, student_ability):
        """
        检查任务是否适合学员能力
        
        Args:
            task: 任务对象
            student_ability: 学员能力分析
            
        Returns:
            bool: 是否适合
        """
        difficulty_mapping = {
            'beginner': 1,
            'intermediate': 2,
            'advanced': 3,
            'expert': 4
        }
        
        task_difficulty = difficulty_mapping.get(task.difficulty, 1)
        student_level = difficulty_mapping.get(student_ability['difficulty_level'], 1)
        
        # 允许学员挑战稍高难度的任务，但不能太高
        return task_difficulty <= student_level + 1
    
    def _sort_tasks_by_priority(self, tasks, request):
        """
        根据优先级排序任务
        
        Args:
            tasks: 任务列表
            request: 调度请求
            
        Returns:
            List[Task]: 排序后的任务列表
        """
        def task_sort_key(task):
            priority_score = 0
            
            # 优先级权重
            if request.consider_priority:
                priority_weights = {
                    'urgent': 100,
                    'high': 80,
                    'medium': 60,
                    'low': 40
                }
                priority_score += priority_weights.get(task.priority, 50)
            
            # 截止时间权重（越近权重越高）
            if task.deadline:
                days_until_deadline = (task.deadline - datetime.utcnow()).days
                if days_until_deadline <= 7:
                    priority_score += (7 - days_until_deadline) * 10
            
            return -priority_score  # 降序排列
        
        return sorted(tasks, key=task_sort_key)
    
    def _allocate_to_time_window(self, tasks, request):
        """
        将任务分配到时间窗口
        
        Args:
            tasks: 任务列表
            request: 调度请求
            
        Returns:
            List[Dict[str, Any]]: 分配结果
        """
        allocations = []
        tasks_per_day = {}
        
        # 初始化每天的任务计数
        current_date = request.start_date.date()
        end_date = request.end_date.date()
        while current_date <= end_date:
            tasks_per_day[current_date] = 0
            current_date += timedelta(days=1)
        
        # 分配任务
        for task in tasks:
            # 找到最早可用的日期
            allocated = False
            current_date = request.start_date.date()
            
            while current_date <= end_date and not allocated:
                # 检查是否超过每天最大任务数
                if tasks_per_day[current_date] < request.max_tasks_per_day:
                    # 检查任务时间要求
                    if task.start_time and task.start_time.date() > current_date:
                        current_date += timedelta(days=1)
                        continue
                    
                    if task.deadline and task.deadline.date() < current_date:
                        current_date += timedelta(days=1)
                        continue
                    
                    # 分配任务
                    allocations.append({
                        'type': 'new_assignment',
                        'task_id': task.id,
                        'task_title': task.title,
                        'scheduled_date': current_date.isoformat(),
                        'priority': task.priority,
                        'difficulty': task.difficulty,
                        'estimated_duration': task.estimated_duration
                    })
                    
                    tasks_per_day[current_date] += 1
                    allocated = True
                
                current_date += timedelta(days=1)
        
        return allocations


class TaskAnalyticsService:
    """任务分析服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_task_analytics(self, request: TaskAnalyticsRequest) -> Dict[str, Any]:
        """
        获取任务分析数据
        
        Args:
            request: 分析请求
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        try:
            # 基础查询
            task_query = self.db.query(Task)
            assignment_query = self.db.query(TaskAssignment)
            submission_query = self.db.query(TaskSubmission)
            evaluation_query = self.db.query(TaskEvaluation)
            
            # 应用租户过滤
            if request.tenant_id:
                task_query = task_query.filter(Task.tenant_id == request.tenant_id)
                assignment_query = assignment_query.filter(TaskAssignment.tenant_id == request.tenant_id)
                submission_query = submission_query.filter(TaskSubmission.tenant_id == request.tenant_id)
                evaluation_query = evaluation_query.filter(TaskEvaluation.tenant_id == request.tenant_id)
            
            # 应用时间过滤
            task_query = task_query.filter(
                Task.created_at >= request.start_date,
                Task.created_at <= request.end_date
            )
            assignment_query = assignment_query.filter(
                TaskAssignment.assigned_at >= request.start_date,
                TaskAssignment.assigned_at <= request.end_date
            )
            submission_query = submission_query.filter(
                TaskSubmission.submitted_at >= request.start_date,
                TaskSubmission.submitted_at <= request.end_date
            )
            evaluation_query = evaluation_query.filter(
                TaskEvaluation.evaluated_at >= request.start_date,
                TaskEvaluation.evaluated_at <= request.end_date
            )
            
            # 应用学员过滤
            if request.student_id:
                assignment_query = assignment_query.filter(TaskAssignment.student_id == request.student_id)
                submission_query = submission_query.filter(TaskSubmission.submitter_id == request.student_id)
                evaluation_query = evaluation_query.filter(TaskEvaluation.student_id == request.student_id)
            
            # 应用任务类型过滤
            if request.task_type:
                task_query = task_query.filter(Task.task_type == request.task_type.value)
                # 需要关联查询任务分配
                assignment_query = assignment_query.join(Task).filter(Task.task_type == request.task_type.value)
            
            # 获取统计数据
            total_tasks = task_query.count()
            total_assignments = assignment_query.count()
            total_submissions = submission_query.count()
            total_evaluations = evaluation_query.count()
            
            # 计算完成率
            completed_assignments = assignment_query.filter(
                TaskAssignment.status == 'completed'
            ).count()
            
            completion_rate = 0
            if total_assignments > 0:
                completion_rate = (completed_assignments / total_assignments) * 100
            
            # 计算平均评分
            avg_score = 0
            if total_evaluations > 0:
                avg_score = evaluation_query.with_entities(
                    func.avg(TaskEvaluation.overall_score)
                ).scalar() or 0
            
            # 分组统计
            grouped_data = self._get_grouped_data(request)
            
            # 难度分布
            difficulty_distribution = self._get_difficulty_distribution(request)
            
            # 优先级分布
            priority_distribution = self._get_priority_distribution(request)
            
            # 任务类型分布
            task_type_distribution = self._get_task_type_distribution(request)
            
            # 时间趋势
            time_trend = self._get_time_trend(request)
            
            return {
                'summary': {
                    'total_tasks': total_tasks,
                    'total_assignments': total_assignments,
                    'total_submissions': total_submissions,
                    'total_evaluations': total_evaluations,
                    'completion_rate': round(completion_rate, 2),
                    'average_score': round(avg_score, 2),
                    'overdue_rate': self._calculate_overdue_rate(request)
                },
                'distributions': {
                    'difficulty': difficulty_distribution,
                    'priority': priority_distribution,
                    'task_type': task_type_distribution
                },
                'trends': {
                    'time': time_trend
                },
                'grouped_data': grouped_data,
                'top_performers': self._get_top_performers(request),
                'areas_for_improvement': self._get_areas_for_improvement(request)
            }
            
        except Exception as e:
            logger.error(f"Failed to get task analytics: {str(e)}")
            raise
    
    def _get_grouped_data(self, request):
        """
        获取分组数据
        
        Args:
            request: 分析请求
            
        Returns:
            Dict[str, Any]: 分组数据
        """
        if request.group_by == 'day':
            return self._group_by_day(request)
        elif request.group_by == 'week':
            return self._group_by_week(request)
        elif request.group_by == 'month':
            return self._group_by_month(request)
        elif request.group_by == 'task_type':
            return self._group_by_task_type(request)
        elif request.group_by == 'difficulty':
            return self._group_by_difficulty(request)
        else:
            return {}
    
    def _group_by_day(self, request):
        """按天分组"""
        # 简化实现
        return {'method': 'day_grouping', 'data': []}
    
    def _group_by_week(self, request):
        """按周分组"""
        return {'method': 'week_grouping', 'data': []}
    
    def _group_by_month(self, request):
        """按月分组"""
        return {'method': 'month_grouping', 'data': []}
    
    def _group_by_task_type(self, request):
        """按任务类型分组"""
        query = self.db.query(
            Task.task_type,
            func.count(Task.id).label('count')
        )
        
        if request.tenant_id:
            query = query.filter(Task.tenant_id == request.tenant_id)
        
        query = query.filter(
            Task.created_at >= request.start_date,
            Task.created_at <= request.end_date
        )
        
        if request.task_type:
            query = query.filter(Task.task_type == request.task_type.value)
        
        results = query.group_by(Task.task_type).all()
        
        return {
            'method': 'task_type',
            'data': [{'task_type': r.task_type, 'count': r.count} for r in results]
        }
    
    def _group_by_difficulty(self, request):
        """按难度分组"""
        query = self.db.query(
            Task.difficulty,
            func.count(Task.id).label('count')
        )
        
        if request.tenant_id:
            query = query.filter(Task.tenant_id == request.tenant_id)
        
        query = query.filter(
            Task.created_at >= request.start_date,
            Task.created_at <= request.end_date
        )
        
        if request.task_type:
            query = query.filter(Task.task_type == request.task_type.value)
        
        results = query.group_by(Task.difficulty).all()
        
        return {
            'method': 'difficulty',
            'data': [{'difficulty': r.difficulty, 'count': r.count} for r in results]
        }
    
    def _get_difficulty_distribution(self, request):
        """获取难度分布"""
        return self._group_by_difficulty(request)
    
    def _get_priority_distribution(self, request):
        """获取优先级分布"""
        query = self.db.query(
            Task.priority,
            func.count(Task.id).label('count')
        )
        
        if request.tenant_id:
            query = query.filter(Task.tenant_id == request.tenant_id)
        
        query = query.filter(
            Task.created_at >= request.start_date,
            Task.created_at <= request.end_date
        )
        
        if request.task_type:
            query = query.filter(Task.task_type == request.task_type.value)
        
        results = query.group_by(Task.priority).all()
        
        return {
            'method': 'priority',
            'data': [{'priority': r.priority, 'count': r.count} for r in results]
        }
    
    def _get_task_type_distribution(self, request):
        """获取任务类型分布"""
        return self._group_by_task_type(request)
    
    def _get_time_trend(self, request):
        """获取时间趋势"""
        # 简化实现
        return {'method': 'time_trend', 'data': []}
    
    def _calculate_overdue_rate(self, request):
        """计算过期率"""
        query = self.db.query(TaskAssignment)
        
        if request.tenant_id:
            query = query.filter(TaskAssignment.tenant_id == request.tenant_id)
        
        if request.student_id:
            query = query.filter(TaskAssignment.student_id == request.student_id)
        
        query = query.filter(
            TaskAssignment.assigned_at >= request.start_date,
            TaskAssignment.assigned_at <= request.end_date
        )
        
        total_assignments = query.count()
        
        if total_assignments == 0:
            return 0
        
        overdue_assignments = query.filter(
            TaskAssignment.expected_completion_at < datetime.utcnow(),
            TaskAssignment.status.in_(['assigned', 'in_progress'])
        ).count()
        
        return round((overdue_assignments / total_assignments) * 100, 2)
    
    def _get_top_performers(self, request):
        """获取表现最佳的学员"""
        if not request.tenant_id:
            return []
        
        query = self.db.query(
            TaskEvaluation.student_id,
            User.username,
            func.avg(TaskEvaluation.overall_score).label('avg_score'),
            func.count(TaskEvaluation.id).label('evaluation_count')
        ).join(
            User, TaskEvaluation.student_id == User.id
        ).filter(
            TaskEvaluation.tenant_id == request.tenant_id,
            TaskEvaluation.status == 'published',
            TaskEvaluation.evaluated_at >= request.start_date,
            TaskEvaluation.evaluated_at <= request.end_date
        ).group_by(
            TaskEvaluation.student_id, User.username
        ).order_by(
            desc('avg_score')
        ).limit(10)
        
        results = query.all()
        
        return [
            {
                'student_id': r.student_id,
                'username': r.username,
                'average_score': round(r.avg_score, 2),
                'evaluation_count': r.evaluation_count
            }
            for r in results
        ]
    
    def _get_areas_for_improvement(self, request):
        """获取需要改进的领域"""
        if not request.tenant_id:
            return []
        
        query = self.db.query(
            Task.difficulty,
            func.avg(TaskEvaluation.overall_score).label('avg_score'),
            func.count(TaskEvaluation.id).label('count')
        ).join(
            TaskAssignment, TaskEvaluation.assignment_id == TaskAssignment.id
        ).join(
            Task, TaskAssignment.task_id == Task.id
        ).filter(
            TaskEvaluation.tenant_id == request.tenant_id,
            TaskEvaluation.status == 'published',
            TaskEvaluation.evaluated_at >= request.start_date,
            TaskEvaluation.evaluated_at <= request.end_date
        ).group_by(
            Task.difficulty
        ).order_by(
            asc('avg_score')
        ).limit(5)
        
        results = query.all()
        
        return [
            {
                'difficulty': r.difficulty,
                'average_score': round(r.avg_score, 2),
                'count': r.count,
                'needs_improvement': r.avg_score < 70
            }
            for r in results
        ]

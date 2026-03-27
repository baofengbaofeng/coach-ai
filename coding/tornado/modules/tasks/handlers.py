"""
任务管理模块 - 处理器层
提供任务相关的API处理器
"""

import logging
from typing import Optional, Dict, Any
from tornado.web import RequestHandler
from sqlalchemy.orm import Session

from coding.tornado.core.base_handler import BaseHandler
from coding.tornado.core.auth_middleware import auth_required
from coding.database.session import get_db_session

from .models import (
    TaskCreateRequest, TaskUpdateRequest, TaskAssignmentRequest,
    TaskAssignmentUpdateRequest, TaskSubmissionRequest, TaskSubmissionReviewRequest,
    TaskEvaluationRequest, TaskEvaluationUpdateRequest, TaskFilter,
    TaskAssignmentFilter, TaskAnalyticsRequest, TaskSchedulerRequest,
    TaskResponse, TaskAssignmentResponse, TaskSubmissionResponse, TaskEvaluationResponse
)
from .services import (
    TaskService, TaskAssignmentService, TaskSubmissionService,
    TaskEvaluationService, TaskSchedulerService, TaskAnalyticsService
)

logger = logging.getLogger(__name__)


class TaskHandler(BaseHandler):
    """任务处理器"""
    
    @auth_required
    async def post(self):
        """
        创建任务
        POST /api/v1/tasks
        """
        try:
            # 获取当前用户和租户
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            # 解析请求数据
            request_data = self.get_json_body()
            request = TaskCreateRequest(**request_data)
            
            # 创建任务
            db: Session = get_db_session()
            task_service = TaskService(db)
            task = task_service.create_task(request, current_user.id, tenant_id)
            
            # 构建响应
            response = TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                task_type=task.task_type,
                status=task.status,
                priority=task.priority,
                difficulty=task.difficulty,
                tags=task.tags or [],
                content=task.content,
                start_time=task.start_time,
                deadline=task.deadline,
                estimated_duration=task.estimated_duration,
                actual_duration=task.actual_duration,
                creator_id=task.creator_id,
                tenant_id=task.tenant_id,
                exercise_type_id=task.exercise_type_id,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            
            self.write_success(response.dict())
            
        except Exception as e:
            logger.error(f"Failed to create task: {str(e)}")
            self.write_error(400, str(e))
    
    @auth_required
    async def get(self, task_id: Optional[str] = None):
        """
        获取任务或任务列表
        GET /api/v1/tasks
        GET /api/v1/tasks/{task_id}
        """
        try:
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            db: Session = get_db_session()
            task_service = TaskService(db)
            
            if task_id:
                # 获取单个任务
                task = task_service.get_task(task_id, tenant_id)
                if not task:
                    self.write_error(404, "Task not found")
                    return
                
                response = TaskResponse(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    task_type=task.task_type,
                    status=task.status,
                    priority=task.priority,
                    difficulty=task.difficulty,
                    tags=task.tags or [],
                    content=task.content,
                    start_time=task.start_time,
                    deadline=task.deadline,
                    estimated_duration=task.estimated_duration,
                    actual_duration=task.actual_duration,
                    creator_id=task.creator_id,
                    tenant_id=task.tenant_id,
                    exercise_type_id=task.exercise_type_id,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                )
                
                self.write_success(response.dict())
            else:
                # 获取任务列表
                page = int(self.get_argument("page", "1"))
                page_size = int(self.get_argument("page_size", "20"))
                
                # 解析筛选条件
                filter_params = TaskFilter(
                    task_type=self.get_argument("task_type", None),
                    status=self.get_argument("status", None),
                    priority=self.get_argument("priority", None),
                    difficulty=self.get_argument("difficulty", None),
                    creator_id=self.get_argument("creator_id", None),
                    start_time_from=self.get_argument("start_time_from", None),
                    start_time_to=self.get_argument("start_time_to", None),
                    deadline_from=self.get_argument("deadline_from", None),
                    deadline_to=self.get_argument("deadline_to", None),
                    tags=self.get_argument("tags", None),
                    search=self.get_argument("search", None)
                )
                
                tasks, total = task_service.list_tasks(filter_params, tenant_id, page, page_size)
                
                # 构建响应列表
                task_list = []
                for task in tasks:
                    task_list.append(TaskResponse(
                        id=task.id,
                        title=task.title,
                        description=task.description,
                        task_type=task.task_type,
                        status=task.status,
                        priority=task.priority,
                        difficulty=task.difficulty,
                        tags=task.tags or [],
                        content=task.content,
                        start_time=task.start_time,
                        deadline=task.deadline,
                        estimated_duration=task.estimated_duration,
                        actual_duration=task.actual_duration,
                        creator_id=task.creator_id,
                        tenant_id=task.tenant_id,
                        exercise_type_id=task.exercise_type_id,
                        created_at=task.created_at,
                        updated_at=task.updated_at
                    ).dict())
                
                self.write_success({
                    "tasks": task_list,
                    "pagination": {
                        "page": page,
                        "page_size": page_size,
                        "total": total,
                        "total_pages": (total + page_size - 1) // page_size
                    }
                })
                
        except Exception as e:
            logger.error(f"Failed to get tasks: {str(e)}")
            self.write_error(400, str(e))
    
    @auth_required
    async def put(self, task_id: str):
        """
        更新任务
        PUT /api/v1/tasks/{task_id}
        """
        try:
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            # 解析请求数据
            request_data = self.get_json_body()
            request = TaskUpdateRequest(**request_data)
            
            # 更新任务
            db: Session = get_db_session()
            task_service = TaskService(db)
            task = task_service.update_task(task_id, request, tenant_id)
            
            if not task:
                self.write_error(404, "Task not found")
                return
            
            # 构建响应
            response = TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                task_type=task.task_type,
                status=task.status,
                priority=task.priority,
                difficulty=task.difficulty,
                tags=task.tags or [],
                content=task.content,
                start_time=task.start_time,
                deadline=task.deadline,
                estimated_duration=task.estimated_duration,
                actual_duration=task.actual_duration,
                creator_id=task.creator_id,
                tenant_id=task.tenant_id,
                exercise_type_id=task.exercise_type_id,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            
            self.write_success(response.dict())
            
        except Exception as e:
            logger.error(f"Failed to update task: {str(e)}")
            self.write_error(400, str(e))
    
    @auth_required
    async def delete(self, task_id: str):
        """
        删除任务
        DELETE /api/v1/tasks/{task_id}
        """
        try:
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            db: Session = get_db_session()
            task_service = TaskService(db)
            
            success = task_service.delete_task(task_id, tenant_id)
            
            if not success:
                self.write_error(404, "Task not found")
                return
            
            self.write_success({"message": "Task deleted successfully"})
            
        except Exception as e:
            logger.error(f"Failed to delete task: {str(e)}")
            self.write_error(400, str(e))
    
    @auth_required
    async def patch(self, task_id: str):
        """
        激活任务
        PATCH /api/v1/tasks/{task_id}/activate
        """
        try:
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            db: Session = get_db_session()
            task_service = TaskService(db)
            
            task = task_service.activate_task(task_id, tenant_id)
            
            if not task:
                self.write_error(404, "Task not found")
                return
            
            # 构建响应
            response = TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                task_type=task.task_type,
                status=task.status,
                priority=task.priority,
                difficulty=task.difficulty,
                tags=task.tags or [],
                content=task.content,
                start_time=task.start_time,
                deadline=task.deadline,
                estimated_duration=task.estimated_duration,
                actual_duration=task.actual_duration,
                creator_id=task.creator_id,
                tenant_id=task.tenant_id,
                exercise_type_id=task.exercise_type_id,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            
            self.write_success(response.dict())
            
        except Exception as e:
            logger.error(f"Failed to activate task: {str(e)}")
            self.write_error(400, str(e))


class TaskAssignmentHandler(BaseHandler):
    """任务分配处理器"""
    
    @auth_required
    async def post(self):
        """
        分配任务
        POST /api/v1/task-assignments
        """
        try:
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            # 解析请求数据
            request_data = self.get_json_body()
            request = TaskAssignmentRequest(**request_data)
            
            # 分配任务
            db: Session = get_db_session()
            assignment_service = TaskAssignmentService(db)
            assignment = assignment_service.assign_task(request, current_user.id, tenant_id)
            
            # 构建响应
            response = TaskAssignmentResponse(
                id=assignment.id,
                task_id=assignment.task_id,
                student_id=assignment.student_id,
                assigner_id=assignment.assigner_id,
                status=assignment.status,
                progress=assignment.progress,
                assigned_at=assignment.assigned_at,
                started_at=assignment.started_at,
                completed_at=assignment.completed_at,
                expected_completion_at=assignment.expected_completion_at,
                actual_completion_at=assignment.actual_completion_at,
                tenant_id=assignment.tenant_id,
                created_at=assignment.created_at,
                updated_at=assignment.updated_at
            )
            
            self.write_success(response.dict())
            
        except Exception as e:
            logger.error(f"Failed to assign task: {str(e)}")
            self.write_error(400, str(e))
    
    @auth_required
    async def get(self, assignment_id: Optional[str] = None):
        """
        获取任务分配或分配列表
        GET /api/v1/task-assignments
        GET /api/v1/task-assignments/{assignment_id}
        """
        try:
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            db: Session = get_db_session()
            assignment_service = TaskAssignmentService(db)
            
            if assignment_id:
                # 获取单个分配
                assignment = assignment_service.get_assignment(assignment_id, tenant_id)
                if not assignment:
                    self.write_error(404, "Assignment not found")
                    return
                
                response = TaskAssignmentResponse(
                    id=assignment.id,
                    task_id=assignment.task_id,
                    student_id=assignment.student_id,
                    assigner_id=assignment.assigner_id,
                    status=assignment.status,
                    progress=assignment.progress,
                    assigned_at=assignment.assigned_at,
                    started_at=assignment.started_at,
                    completed_at=assignment.completed_at,
                    expected_completion_at=assignment.expected_completion_at,
                    actual_completion_at=assignment.actual_completion_at,
                    tenant_id=assignment.tenant_id,
                    created_at=assignment.created_at,
                    updated_at=assignment.updated_at
                )
                
                self.write_success(response.dict())
            else:
                # 获取分配列表
                page = int(self.get_argument("page", "1"))
                page_size = int(self.get_argument("page_size", "20"))
                
                # 解析筛选条件
                filter_params = TaskAssignmentFilter(
                    task_id=self.get_argument("task_id", None),
                    student_id=self.get_argument("student_id", None),
                    assigner_id=self.get_argument("assigner_id", None),
                    status=self.get_argument("status", None),
                    assigned_at_from=self.get_argument("assigned_at_from", None),
                    assigned_at_to=self.get_argument("assigned_at_to", None),
                    expected_completion_at_from=self.get_argument("expected_completion_at_from", None),
                    expected_completion_at_to=self.get_argument("expected_completion_at_to", None),
                    is_overdue=self.get_argument("is_overdue", None)
                )
                
                assignments, total = assignment_service.list_assignments(filter_params, tenant_id, page, page_size)
                
                # 构建响应列表
                assignment_list = []
                for assignment in assignments:
                    assignment_list.append(TaskAssignmentResponse(
                        id=assignment.id,
                        task_id=assignment.task_id,
                        student_id=assignment.student_id,
                        assigner_id=assignment.assigner_id,
                        status=assignment.status,
                        progress=assignment.progress,
                        assigned_at=assignment.assigned_at,
                        started_at=assignment.started_at,
                        completed_at=assignment.completed_at,
                        expected_completion_at=assignment.expected_completion_at,
                        actual_completion_at=assignment.actual_completion_at,
                        tenant_id=assignment.tenant_id,
                        created_at=assignment.created_at,
                        updated_at=assignment.updated_at
                    ).dict())
                
                self.write_success({
                    "assignments": assignment_list,
                    "pagination": {
                        "page": page,
                        "page_size": page_size,
                        "total": total,
                        "total_pages": (total + page_size - 1) // page_size
                    }
                })
                
        except Exception as e:
            logger.error(f"Failed to get task assignments: {str(e)}")
            self.write_error(400, str(e))
    
    @auth_required
    async def put(self, assignment_id: str):
        """
        更新任务分配
        PUT /api/v1/task-assignments/{assignment_id}
        """
        try:
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            # 解析请求数据
            request_data = self.get_json_body()
            request = TaskAssignmentUpdateRequest(**request_data)
            
            # 更新分配
            db: Session = get_db_session()
            assignment_service = TaskAssignmentService(db)
            assignment = assignment_service.update_assignment(assignment_id, request, tenant_id)
            
            if not assignment:
                self.write_error(404, "Assignment not found")
                return
            
            # 构建响应
            response = TaskAssignmentResponse(
                id=assignment.id,
                task_id=assignment.task_id,
                student_id=assignment.student_id,
                assigner_id=assignment.assigner_id,
                status=assignment.status,
                progress=assignment.progress,
                assigned_at=assignment.assigned_at,
                started_at=assignment.started_at,
                completed_at=assignment.completed_at,
                expected_completion_at=assignment.expected_completion_at,
                actual_completion_at=assignment.actual_completion_at,
                tenant_id=assignment.tenant_id,
                created_at=assignment.created_at,
                updated_at=assignment.updated_at
            )
            
            self.write_success(response.dict())
            
        except Exception as e:
            logger.error(f"Failed to update task assignment: {str(e)}")
            self.write_error(400, str(e))
    
    @auth_required
    async def get_student_assignments(self, student_id: str):
        """
        获取学员的任务分配
        GET /api/v1/students/{student_id}/task-assignments
        """
        try:
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            include_completed = self.get_argument("include_completed", "false").lower() == "true"
            
            db: Session = get_db_session()
            assignment_service = TaskAssignmentService(db)
            
            assignments = assignment_service.get_student_assignments(student_id, tenant_id, include_completed)
            
            # 构建响应列表
            assignment_list = []
            for assignment in assignments:
                assignment_list.append(TaskAssignmentResponse(
                    id=assignment.id,
                    task_id=assignment.task_id,
                    student_id=assignment.student_id,
                    assigner_id=assignment.assigner_id,
                    status=assignment.status,
                    progress=assignment.progress,
                    assigned_at=assignment.assigned_at,
                    started_at=assignment.started_at,
                    completed_at=assignment.completed_at,
                    expected_completion_at=assignment.expected_completion_at,
                    actual_completion_at=assignment.actual_completion_at,
                    tenant_id=assignment.tenant_id,
                    created_at=assignment.created_at,
                    updated_at=assignment.updated_at
                ).dict())
            
            self.write_success({
                "assignments": assignment_list,
                "student_id": student_id,
                "include_completed": include_completed
            })
            
        except Exception as e:
            logger.error(f"Failed to get student assignments: {str(e)}")
            self.write_error(400, str(e))


class TaskSubmissionHandler(BaseHandler):
    """任务提交处理器"""
    
    @auth_required
    async def post(self):
        """
        提交任务
        POST /api/v1/task-submissions
        """
        try:
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            # 解析请求数据
            request_data = self.get_json_body()
            request = TaskSubmissionRequest(**request_data)
            
            # 提交任务
            db: Session = get_db_session()
            submission_service = TaskSubmissionService(db)
            submission = submission_service.submit_task(request, current_user.id, tenant_id)
            
            # 构建响应
            response = TaskSubmissionResponse(
                id=submission.id,
                assignment_id=submission.assignment_id,
                submitter_id=submission.submitter_id,
                status=submission.status,
                content=submission.content,
                submitted_at=submission.submitted_at,
                reviewed_at=submission.reviewed_at,
                reviewer_id=submission.reviewer_id,
                version=submission.version,
                is_final=submission.is_final,
                tenant_id=submission.tenant_id,
                created_at=submission.created_at,
                updated_at=submission.updated_at
            )
            
            self.write_success(response.dict())
            
        except Exception as e:
            logger.error(f"Failed to submit task: {str(e)}")
            self.write_error(400, str(e))
    
    @auth_required
    async def get(self, submission_id: Optional[str] = None):
        """
        获取任务提交或提交列表
        GET /api/v1/task-submissions
        GET /api/v1/task-submissions/{submission_id}
        """
        try:
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            db: Session = get_db_session()
            submission_service = TaskSubmissionService(db)
            
            if submission_id:
                # 获取单个提交
                submission = submission_service.get_submission(submission_id, tenant_id)
                if not submission:
                    self.write_error(404, "Submission not found")
                    return
                
                response = TaskSubmissionResponse(
                    id=submission.id,
                    assignment_id=submission.assignment_id,
                    submitter_id=submission.submitter_id,
                    status=submission.status,
                    content=submission.content,
                    submitted_at=submission.submitted_at,
                    reviewed_at=submission.reviewed_at,
                    reviewer_id=submission.reviewer_id,
                    version=submission.version,
                    is_final=submission.is_final,
                    tenant_id=submission.tenant_id,
                    created_at=submission.created_at,
                    updated_at=submission.updated_at
                )
                
                self.write_success(response.dict())
            else:
                # 获取提交列表
                page = int(self.get_argument("page", "1"))
                page_size = int(self.get_argument("page_size", "20"))
                assignment_id = self.get_argument("assignment_id", None)
                submitter_id = self.get_argument("submitter_id", None)
                status = self.get_argument("status", None)
                
                submissions, total = submission_service.list_submissions(
                    assignment_id, submitter_id, status, tenant_id, page, page_size
                )
                
                # 构建响应列表
                submission_list = []
                for submission in submissions:
                    submission_list.append(TaskSubmissionResponse(
                        id=submission.id,
                        assignment_id=submission.assignment_id,
                        submitter_id=submission.submitter_id,
                        status=submission.status,
                        content=submission.content,
                        submitted_at=submission.submitted_at,
                        reviewed_at=submission.reviewed_at,
                        reviewer_id=submission.reviewer_id,
                        version=submission.version,
                        is_final=submission.is_final,
                        tenant_id=submission.tenant_id,
                        created_at=submission.created_at,
                        updated_at=submission.updated_at
                    ).dict())
                
                self.write_success({
                    "submissions": submission_list,
                    "pagination": {
                        "page": page,
                        "page_size": page_size,
                        "total": total,
                        "total_pages": (total + page_size - 1) // page_size
                    }
                })
                
        except Exception as e:
            logger.error(f"Failed to get task submissions: {str(e)}")
            self.write_error(400, str(e))
    
    @auth_required
    async def patch(self, submission_id: str):
        """
        审核任务提交
        PATCH /api/v1/task-submissions/{submission_id}/review
        """
        try:
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            # 解析请求数据
            request_data = self.get_json_body()
            request = TaskSubmissionReviewRequest(**request_data)
            
            # 审核提交
            db: Session = get_db_session()
            submission_service = TaskSubmissionService(db)
            submission = submission_service.review_submission(
                submission_id, request, current_user.id, tenant_id
            )
            
            if not submission:
                self.write_error(404, "Submission not found")
                return
            
            # 构建响应
            response = TaskSubmissionResponse(
                id=submission.id,
                assignment_id=submission.assignment_id,
                submitter_id=submission.submitter_id,
                status=submission.status,
                content=submission.content,
                submitted_at=submission.submitted_at,
                reviewed_at=submission.reviewed_at,
                reviewer_id=submission.reviewer_id,
                version=submission.version,
                is_final=submission.is_final,
                tenant_id=submission.tenant_id,
                created_at=submission.created_at,
                updated_at=submission.updated_at
            )
            
            self.write_success(response.dict())
            
        except Exception as e:
            logger.error(f"Failed to review task submission: {str(e)}")
            self.write_error(400, str(e))


class TaskEvaluationHandler(BaseHandler):
    """任务评价处理器"""
    
    @auth_required
    async def post(self):
        """
        创建任务评价
        POST /api/v1/task-evaluations
        """
        try:
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            # 解析请求数据
            request_data = self.get_json_body()
            request = TaskEvaluationRequest(**request_data)
            
            # 创建评价
            db: Session = get_db_session()
            evaluation_service = TaskEvaluationService(db)
            evaluation = evaluation_service.create_evaluation(request, current_user.id, tenant_id)
            
            # 构建响应
            response = TaskEvaluationResponse(
                id=evaluation.id,
                assignment_id=evaluation.assignment_id,
                submission_id=evaluation.submission_id,
                evaluator_id=evaluation.evaluator_id,
                student_id=evaluation.student_id,
                overall_score=evaluation.overall_score,
                score_grade=evaluation.get_score_grade(),
                comments=evaluation.comments,
                evaluated_at=evaluation.evaluated_at,
                status=evaluation.status,
                recommended_for_advancement=evaluation.recommended_for_advancement,
                recommended_next_task_id=evaluation.recommended_next_task_id,
                tenant_id=evaluation.tenant_id,
                created_at=evaluation.created_at,
                updated_at=evaluation.updated_at
            )
            
            self.write_success(response.dict())
            
        except Exception as e:
            logger.error(f"Failed to create task evaluation: {str(e)}")
            self.write_error(400, str(e))
    
    @auth_required
    async def get(self, evaluation_id: Optional[str] = None):
        """
        获取任务评价或评价列表
        GET /api/v1/task-evaluations
        GET /api/v1/task-evaluations/{evaluation_id}
        """
        try:
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            db: Session = get_db_session()
            evaluation_service = TaskEvaluationService(db)
            
            if evaluation_id:
                # 获取单个评价
                evaluation = evaluation_service.get_evaluation(evaluation_id, tenant_id)
                if not evaluation:
                    self.write_error(404, "Evaluation not found")
                    return
                
                response = TaskEvaluationResponse(
                    id=evaluation.id,
                    assignment_id=evaluation.assignment_id,
                    submission_id=evaluation.submission_id,
                    evaluator_id=evaluation.evaluator_id,
                    student_id=evaluation.student_id,
                    overall_score=evaluation.overall_score,
                    score_grade=evaluation.get_score_grade(),
                    comments=evaluation.comments,
                    evaluated_at=evaluation.evaluated_at,
                    status=evaluation.status,
                    recommended_for_advancement=evaluation.recommended_for_advancement,
                    recommended_next_task_id=evaluation.recommended_next_task_id,
                    tenant_id=evaluation.tenant_id,
                    created_at=evaluation.created_at,
                    updated_at=evaluation.updated_at
                )
                
                self.write_success(response.dict())
            else:
                # 获取评价列表
                page = int(self.get_argument("page", "1"))
                page_size = int(self.get_argument("page_size", "20"))
                assignment_id = self.get_argument("assignment_id", None)
                student_id = self.get_argument("student_id", None)
                evaluator_id = self.get_argument("evaluator_id", None)
                status = self.get_argument("status", None)
                
                evaluations, total = evaluation_service.list_evaluations(
                    assignment_id, student_id, evaluator_id, status, tenant_id, page, page_size
                )
                
                # 构建响应列表
                evaluation_list = []
                for evaluation in evaluations:
                    evaluation_list.append(TaskEvaluationResponse(
                        id=evaluation.id,
                        assignment_id=evaluation.assignment_id,
                        submission_id=evaluation.submission_id,
                        evaluator_id=evaluation.evaluator_id,
                        student_id=evaluation.student_id,
                        overall_score=evaluation.overall_score,
                        score_grade=evaluation.get_score_grade(),
                        comments=evaluation.comments,
                        evaluated_at=evaluation.evaluated_at,
                        status=evaluation.status,
                        recommended_for_advancement=evaluation.recommended_for_advancement,
                        recommended_next_task_id=evaluation.recommended_next_task_id,
                        tenant_id=evaluation.tenant_id,
                        created_at=evaluation.created_at,
                        updated_at=evaluation.updated_at
                    ).dict())
                
                self.write_success({
                    "evaluations": evaluation_list,
                    "pagination": {
                        "page": page,
                        "page_size": page_size,
                        "total": total,
                        "total_pages": (total + page_size - 1) // page_size
                    }
                })
                
        except Exception as e:
            logger.error(f"Failed to get task evaluations: {str(e)}")
            self.write_error(400, str(e))
    
    @auth_required
    async def put(self, evaluation_id: str):
        """
        更新任务评价
        PUT /api/v1/task-evaluations/{evaluation_id}
        """
        try:
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            # 解析请求数据
            request_data = self.get_json_body()
            request = TaskEvaluationUpdateRequest(**request_data)
            
            # 更新评价
            db: Session = get_db_session()
            evaluation_service = TaskEvaluationService(db)
            evaluation = evaluation_service.update_evaluation(evaluation_id, request, tenant_id)
            
            if not evaluation:
                self.write_error(404, "Evaluation not found")
                return
            
            # 构建响应
            response = TaskEvaluationResponse(
                id=evaluation.id,
                assignment_id=evaluation.assignment_id,
                submission_id=evaluation.submission_id,
                evaluator_id=evaluation.evaluator_id,
                student_id=evaluation.student_id,
                overall_score=evaluation.overall_score,
                score_grade=evaluation.get_score_grade(),
                comments=evaluation.comments,
                evaluated_at=evaluation.evaluated_at,
                status=evaluation.status,
                recommended_for_advancement=evaluation.recommended_for_advancement,
                recommended_next_task_id=evaluation.recommended_next_task_id,
                tenant_id=evaluation.tenant_id,
                created_at=evaluation.created_at,
                updated_at=evaluation.updated_at
            )
            
            self.write_success(response.dict())
            
        except Exception as e:
            logger.error(f"Failed to update task evaluation: {str(e)}")
            self.write_error(400, str(e))
    
    @auth_required
    async def patch(self, evaluation_id: str):
        """
        发布任务评价
        PATCH /api/v1/task-evaluations/{evaluation_id}/publish
        """
        try:
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            db: Session = get_db_session()
            evaluation_service = TaskEvaluationService(db)
            
            evaluation = evaluation_service.publish_evaluation(evaluation_id, tenant_id)
            
            if not evaluation:
                self.write_error(404, "Evaluation not found")
                return
            
            # 构建响应
            response = TaskEvaluationResponse(
                id=evaluation.id,
                assignment_id=evaluation.assignment_id,
                submission_id=evaluation.submission_id,
                evaluator_id=evaluation.evaluator_id,
                student_id=evaluation.student_id,
                overall_score=evaluation.overall_score,
                score_grade=evaluation.get_score_grade(),
                comments=evaluation.comments,
                evaluated_at=evaluation.evaluated_at,
                status=evaluation.status,
                recommended_for_advancement=evaluation.recommended_for_advancement,
                recommended_next_task_id=evaluation.recommended_next_task_id,
                tenant_id=evaluation.tenant_id,
                created_at=evaluation.created_at,
                updated_at=evaluation.updated_at
            )
            
            self.write_success(response.dict())
            
        except Exception as e:
            logger.error(f"Failed to publish task evaluation: {str(e)}")
            self.write_error(400, str(e))


class TaskSchedulerHandler(BaseHandler):
    """任务调度处理器"""
    
    @auth_required
    async def post(self):
        """
        智能调度任务
        POST /api/v1/task-scheduler/schedule
        """
        try:
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            # 解析请求数据
            request_data = self.get_json_body()
            request = TaskSchedulerRequest(**request_data)
            
            # 调度任务
            db: Session = get_db_session()
            scheduler_service = TaskSchedulerService(db)
            schedule = scheduler_service.schedule_tasks(request, tenant_id)
            
            self.write_success({
                "schedule": schedule,
                "student_id": request.student_id,
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to schedule tasks: {str(e)}")
            self.write_error(400, str(e))


class TaskAnalyticsHandler(BaseHandler):
    """任务分析处理器"""
    
    @auth_required
    async def post(self):
        """
        获取任务分析数据
        POST /api/v1/task-analytics
        """
        try:
            current_user = self.current_user
            tenant_id = current_user.tenant_id
            
            # 解析请求数据
            request_data = self.get_json_body()
            request_data['tenant_id'] = tenant_id
            request = TaskAnalyticsRequest(**request_data)
            
            # 获取分析数据
            db: Session = get_db_session()
            analytics_service = TaskAnalyticsService(db)
            analytics = analytics_service.get_task_analytics(request)
            
            self.write_success(analytics)
            
        except Exception as e:
            logger.error(f"Failed to get task analytics: {str(e)}")
            self.write_error(400, str(e))

"""
任务管理模块 - 处理器层（DDD迁移版）
提供任务相关的API处理器
"""

import logging
from typing import Optional, Dict, Any
from tornado.web import RequestHandler
from loguru import logger

from src.interfaces.api.middleware.auth_middleware import auth_required
from src.application.services.task_service_simple import TaskService

logger = logging.getLogger(__name__)


class TaskHandler(RequestHandler):
    """任务处理器"""
    
    def initialize(self):
        """初始化处理器"""
        self.task_service = TaskService()
    
    def set_default_headers(self):
        """设置默认响应头"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    
    def write_json(self, data: Dict[str, Any], status_code: int = 200):
        """写入JSON响应"""
        self.set_status(status_code)
        self.write({
            'success': status_code < 400,
            'data': data,
            'timestamp': self.request.request_time()
        })
    
    def write_error(self, status_code: int, **kwargs):
        """写入错误响应"""
        exc_info = kwargs.get('exc_info')
        if exc_info:
            error = exc_info[1]
            error_message = str(error)
        else:
            error_message = self._reason
        
        self.set_status(status_code)
        self.write({
            'success': False,
            'error': {
                'code': f'HTTP_{status_code}',
                'message': error_message
            },
            'timestamp': self.request.request_time()
        })
    
    @auth_required
    async def post(self):
        """
        创建任务
        POST /api/v1/tasks
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            # 解析请求数据
            request_data = self.get_json_body()
            
            # 创建任务
            result = await self.task_service.create_task(
                user_id=user_id,
                title=request_data.get('title'),
                description=request_data.get('description'),
                task_type=request_data.get('task_type', 'general'),
                priority=request_data.get('priority', 'medium'),
                difficulty=request_data.get('difficulty', 'medium'),
                estimated_minutes=request_data.get('estimated_minutes'),
                due_date=request_data.get('due_date'),
                assignee_id=request_data.get('assignee_id'),
                tags=request_data.get('tags', []),
                metadata=request_data.get('metadata', {})
            )
            
            if result['success']:
                self.write_json(result['data'])
            else:
                self.write_json({'error': result['error']}, 400)
                
        except Exception as e:
            logger.error(f"Create task error: {e}")
            self.write_json({'error': str(e)}, 500)
    
    @auth_required
    async def get(self, task_id: Optional[str] = None):
        """
        获取任务或任务列表
        GET /api/v1/tasks - 获取任务列表
        GET /api/v1/tasks/{task_id} - 获取单个任务
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            if task_id:
                # 获取单个任务
                result = await self.task_service.get_task(task_id, user_id)
                if result['success']:
                    self.write_json(result['data'])
                else:
                    self.write_json({'error': result['error']}, 404)
            else:
                # 获取任务列表
                page = int(self.get_argument('page', '1'))
                limit = int(self.get_argument('limit', '20'))
                status = self.get_argument('status', None)
                task_type = self.get_argument('task_type', None)
                priority = self.get_argument('priority', None)
                
                result = await self.task_service.list_user_tasks(
                    user_id=user_id,
                    status=status,
                    task_type=task_type,
                    priority=priority,
                    page=page,
                    limit=limit
                )
                
                if result['success']:
                    self.write_json(result['data'])
                else:
                    self.write_json({'error': result['error']}, 400)
                    
        except Exception as e:
            logger.error(f"Get task(s) error: {e}")
            self.write_json({'error': str(e)}, 500)
    
    @auth_required
    async def put(self, task_id: str):
        """
        更新任务
        PUT /api/v1/tasks/{task_id}
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            # 解析请求数据
            request_data = self.get_json_body()
            
            # 更新任务
            result = await self.task_service.update_task(
                task_id=task_id,
                user_id=user_id,
                update_data=request_data
            )
            
            if result['success']:
                self.write_json(result['data'])
            else:
                self.write_json({'error': result['error']}, 400)
                
        except Exception as e:
            logger.error(f"Update task error: {e}")
            self.write_json({'error': str(e)}, 500)
    
    @auth_required
    async def delete(self, task_id: str):
        """
        删除任务
        DELETE /api/v1/tasks/{task_id}
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            # 删除任务
            result = await self.task_service.delete_task(task_id, user_id)
            
            if result['success']:
                self.write_json(result['data'])
            else:
                self.write_json({'error': result['error']}, 400)
                
        except Exception as e:
            logger.error(f"Delete task error: {e}")
            self.write_json({'error': str(e)}, 500)


class TaskAssignmentHandler(RequestHandler):
    """任务分配处理器"""
    
    def initialize(self):
        """初始化处理器"""
        self.task_service = TaskService()
    
    def set_default_headers(self):
        """设置默认响应头"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    
    def write_json(self, data: Dict[str, Any], status_code: int = 200):
        """写入JSON响应"""
        self.set_status(status_code)
        self.write({
            'success': status_code < 400,
            'data': data,
            'timestamp': self.request.request_time()
        })
    
    @auth_required
    async def post(self):
        """
        分配任务
        POST /api/v1/tasks/assignments
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            assigner_id = current_user.get('id') if current_user else None
            
            if not assigner_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            # 解析请求数据
            request_data = self.get_json_body()
            
            # 分配任务
            result = await self.task_service.assign_task(
                task_id=request_data.get('task_id'),
                assigner_id=assigner_id,
                assignee_id=request_data.get('assignee_id'),
                due_date=request_data.get('due_date'),
                notes=request_data.get('notes')
            )
            
            if result['success']:
                self.write_json(result['data'])
            else:
                self.write_json({'error': result['error']}, 400)
                
        except Exception as e:
            logger.error(f"Assign task error: {e}")
            self.write_json({'error': str(e)}, 500)
    
    @auth_required
    async def get(self, assignment_id: Optional[str] = None):
        """
        获取任务分配
        GET /api/v1/tasks/assignments - 获取分配列表
        GET /api/v1/tasks/assignments/{assignment_id} - 获取单个分配
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            if assignment_id:
                # 获取单个分配
                result = await self.task_service.get_assignment(assignment_id, user_id)
                if result['success']:
                    self.write_json(result['data'])
                else:
                    self.write_json({'error': result['error']}, 404)
            else:
                # 获取分配列表
                page = int(self.get_argument('page', '1'))
                limit = int(self.get_argument('limit', '20'))
                status = self.get_argument('status', None)
                
                result = await self.task_service.list_user_assignments(
                    user_id=user_id,
                    status=status,
                    page=page,
                    limit=limit
                )
                
                if result['success']:
                    self.write_json(result['data'])
                else:
                    self.write_json({'error': result['error']}, 400)
                    
        except Exception as e:
            logger.error(f"Get assignment(s) error: {e}")
            self.write_json({'error': str(e)}, 500)
    
    @auth_required
    async def put(self, assignment_id: str):
        """
        更新任务分配
        PUT /api/v1/tasks/assignments/{assignment_id}
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            # 解析请求数据
            request_data = self.get_json_body()
            
            # 更新分配
            result = await self.task_service.update_assignment(
                assignment_id=assignment_id,
                user_id=user_id,
                update_data=request_data
            )
            
            if result['success']:
                self.write_json(result['data'])
            else:
                self.write_json({'error': result['error']}, 400)
                
        except Exception as e:
            logger.error(f"Update assignment error: {e}")
            self.write_json({'error': str(e)}, 500)


class TaskSubmissionHandler(RequestHandler):
    """任务提交处理器"""
    
    def initialize(self):
        """初始化处理器"""
        self.task_service = TaskService()
    
    def set_default_headers(self):
        """设置默认响应头"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    
    def write_json(self, data: Dict[str, Any], status_code: int = 200):
        """写入JSON响应"""
        self.set_status(status_code)
        self.write({
            'success': status_code < 400,
            'data': data,
            'timestamp': self.request.request_time()
        })
    
    @auth_required
    async def post(self):
        """
        提交任务
        POST /api/v1/tasks/submissions
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            # 解析请求数据
            request_data = self.get_json_body()
            
            # 提交任务
            result = await self.task_service.submit_task(
                assignment_id=request_data.get('assignment_id'),
                user_id=user_id,
                content=request_data.get('content'),
                attachments=request_data.get('attachments', []),
                notes=request_data.get('notes')
            )
            
            if result['success']:
                self.write_json(result['data'])
            else:
                self.write_json({'error': result['error']}, 400)
                
        except Exception as e:
            logger.error(f"Submit task error: {e}")
            self.write_json({'error': str(e)}, 500)
    
    @auth_required
    async def get(self, submission_id: Optional[str] = None):
        """
        获取任务提交
        GET /api/v1/tasks/submissions - 获取提交列表
        GET /api/v1/tasks/submissions/{submission_id} - 获取单个提交
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            if submission_id:
                # 获取单个提交
                result = await self.task_service.get_submission(submission_id, user_id)
                if result['success']:
                    self.write_json(result['data'])
                else:
                    self.write_json({'error': result['error']}, 404)
            else:
                # 获取提交列表
                page = int(self.get_argument('page', '1'))
                limit = int(self.get_argument('limit', '20'))
                status = self.get_argument('status', None)
                
                result = await self.task_service.list_user_submissions(
                    user_id=user_id,
                    status=status,
                    page=page,
                    limit=limit
                )
                
                if result['success']:
                    self.write_json(result['data'])
                else:
                    self.write_json({'error': result['error']}, 400)
                    
        except Exception as e:
            logger.error(f"Get submission(s) error: {e}")
            self.write_json({'error': str(e)}, 500)


class TaskEvaluationHandler(RequestHandler):
    """任务评估处理器"""
    
    def initialize(self):
        """初始化处理器"""
        self.task_service = TaskService()
    
    def set_default_headers(self):
        """设置默认响应头"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    
    def write_json(self, data: Dict[str, Any], status_code: int = 200):
        """写入JSON响应"""
        self.set_status(status_code)
        self.write({
            'success': status_code < 400,
            'data': data,
            'timestamp': self.request.request_time()
        })
    
    @auth_required
    async def post(self):
        """
        评估任务
        POST /api/v1/tasks/evaluations
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            evaluator_id = current_user.get('id') if current_user else None
            
            if not evaluator_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            # 解析请求数据
            request_data = self.get_json_body()
            
            # 评估任务
            result = await self.task_service.evaluate_task(
                submission_id=request_data.get('submission_id'),
                evaluator_id=evaluator_id,
                score=request_data.get('score'),
                feedback=request_data.get('feedback'),
                status=request_data.get('status', 'completed')
            )
            
            if result['success']:
                self.write_json(result['data'])
            else:
                self.write_json({'error': result['error']}, 400)
                
        except Exception as e:
            logger.error(f"Evaluate task error: {e}")
            self.write_json({'error': str(e)}, 500)
    
    @auth_required
    async def get(self, evaluation_id: Optional[str] = None):
        """
        获取任务评估
        GET /api/v1/tasks/evaluations - 获取评估列表
        GET /api/v1/tasks/evaluations/{evaluation_id} - 获取单个评估
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            if evaluation_id:
                # 获取单个评估
                result = await self.task_service.get_evaluation(evaluation_id, user_id)
                if result['success']:
                    self.write_json(result['data'])
                else:
                    self.write_json({'error': result['error']}, 404)
            else:
                # 获取评估列表
                page = int(self.get_argument('page', '1'))
                limit = int(self.get_argument('limit', '20'))
                
                result = await self.task_service.list_user_evaluations(
                    user_id=user_id,
                    page=page,
                    limit=limit
                )
                
                if result['success']:
                    self.write_json(result['data'])
                else:
                    self.write_json({'error': result['error']}, 400)
                    
        except Exception as e:
            logger.error(f"Get evaluation(s) error: {e}")
            self.write_json
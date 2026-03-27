"""
任务路由配置
"""

from .handlers import (
    TaskHandler,
    TaskAssignmentHandler,
    TaskSubmissionHandler,
    TaskEvaluationHandler
)


def get_task_routes():
    """获取任务路由配置"""
    return [
        # 任务管理路由
        (r"/api/v1/tasks", TaskHandler),
        (r"/api/v1/tasks/([^/]+)", TaskHandler),
        
        # 任务分配路由
        (r"/api/v1/tasks/assignments", TaskAssignmentHandler),
        (r"/api/v1/tasks/assignments/([^/]+)", TaskAssignmentHandler),
        
        # 任务提交路由
        (r"/api/v1/tasks/submissions", TaskSubmissionHandler),
        (r"/api/v1/tasks/submissions/([^/]+)", TaskSubmissionHandler),
        
        # 任务评估路由
        (r"/api/v1/tasks/evaluations", TaskEvaluationHandler),
        (r"/api/v1/tasks/evaluations/([^/]+)", TaskEvaluationHandler),
    ]
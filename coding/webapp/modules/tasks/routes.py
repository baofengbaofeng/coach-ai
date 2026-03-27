"""
任务管理模块 - 路由配置
定义任务相关的API路由
"""

from .handlers import (
    TaskHandler, TaskAssignmentHandler, TaskSubmissionHandler,
    TaskEvaluationHandler, TaskSchedulerHandler, TaskAnalyticsHandler
)


def get_task_routes():
    """
    获取任务管理模块的路由配置
    
    Returns:
        list: 路由配置列表
    """
    return [
        # 任务管理
        (r"/api/v1/tasks", TaskHandler),
        (r"/api/v1/tasks/([^/]+)", TaskHandler),
        (r"/api/v1/tasks/([^/]+)/activate", TaskHandler),
        
        # 任务分配
        (r"/api/v1/task-assignments", TaskAssignmentHandler),
        (r"/api/v1/task-assignments/([^/]+)", TaskAssignmentHandler),
        (r"/api/v1/students/([^/]+)/task-assignments", TaskAssignmentHandler),
        
        # 任务提交
        (r"/api/v1/task-submissions", TaskSubmissionHandler),
        (r"/api/v1/task-submissions/([^/]+)", TaskSubmissionHandler),
        (r"/api/v1/task-submissions/([^/]+)/review", TaskSubmissionHandler),
        
        # 任务评价
        (r"/api/v1/task-evaluations", TaskEvaluationHandler),
        (r"/api/v1/task-evaluations/([^/]+)", TaskEvaluationHandler),
        (r"/api/v1/task-evaluations/([^/]+)/publish", TaskEvaluationHandler),
        
        # 任务调度
        (r"/api/v1/task-scheduler/schedule", TaskSchedulerHandler),
        
        # 任务分析
        (r"/api/v1/task-analytics", TaskAnalyticsHandler),
    ]
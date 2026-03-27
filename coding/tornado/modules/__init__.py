"""
业务模块
按DDD领域划分的业务模块
"""

from typing import List, Tuple
from tornado.web import url


def get_routes() -> List[Tuple]:
    """
    获取所有模块的路由
    
    Returns:
        路由列表
    """
    routes = []
    
    # 导入认证模块路由
    try:
        from .auth.routes import get_auth_routes
        routes.extend(get_auth_routes())
    except ImportError:
        pass
    
    # 导入租户模块路由
    try:
        from .tenant.routes import get_tenant_routes
        routes.extend(get_tenant_routes())
    except ImportError:
        pass
    
    # 导入运动模块路由
    try:
        from .exercise.routes import get_exercise_routes
        routes.extend(get_exercise_routes())
    except ImportError:
        pass
    
    # 导入任务模块路由
    try:
        from .tasks.routes import get_task_routes
        routes.extend(get_task_routes())
    except ImportError:
        pass
    
    # 导入成就系统模块路由
    try:
        from .achievements.routes import get_achievement_routes
        routes.extend(get_achievement_routes())
    except ImportError:
        pass
    
    return routes
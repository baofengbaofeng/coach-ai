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
    
    # 暂时跳过所有模块路由，只返回基础路由
    # 后续再逐个修复模块导入问题
    
    return routes
"""
运动模块路由配置
"""

from typing import List, Tuple
from tornado.web import url
from .handlers import (
    CreateExerciseTypeHandler,
    GetExerciseTypeHandler,
    UpdateExerciseTypeHandler,
    DeleteExerciseTypeHandler,
    ListExerciseTypesHandler,
    CreateExercisePlanHandler,
    GetExercisePlanHandler,
    UpdateExercisePlanHandler,
    DeleteExercisePlanHandler,
    ListExercisePlansHandler,
    StartExerciseSessionHandler,
    EndExerciseSessionHandler,
    GetExerciseSessionHandler,
    ListExerciseSessionsHandler,
    SubmitExerciseDataHandler,
    GetExerciseStatisticsHandler,
    GetExerciseProgressHandler,
    GetExerciseRecommendationsHandler
)


def get_exercise_routes() -> List[Tuple]:
    """
    获取运动模块路由
    
    Returns:
        路由列表
    """
    return [
        # 运动类型管理
        url(r"/api/exercise/types", CreateExerciseTypeHandler, name="create_exercise_type"),
        url(r"/api/exercise/types/([^/]+)", GetExerciseTypeHandler, name="get_exercise_type"),
        url(r"/api/exercise/types/([^/]+)/update", UpdateExerciseTypeHandler, name="update_exercise_type"),
        url(r"/api/exercise/types/([^/]+)/delete", DeleteExerciseTypeHandler, name="delete_exercise_type"),
        url(r"/api/exercise/types", ListExerciseTypesHandler, name="list_exercise_types"),
        
        # 运动计划管理
        url(r"/api/exercise/plans", CreateExercisePlanHandler, name="create_exercise_plan"),
        url(r"/api/exercise/plans/([^/]+)", GetExercisePlanHandler, name="get_exercise_plan"),
        url(r"/api/exercise/plans/([^/]+)/update", UpdateExercisePlanHandler, name="update_exercise_plan"),
        url(r"/api/exercise/plans/([^/]+)/delete", DeleteExercisePlanHandler, name="delete_exercise_plan"),
        url(r"/api/exercise/plans", ListExercisePlansHandler, name="list_exercise_plans"),
        
        # 运动会话管理
        url(r"/api/exercise/sessions/start", StartExerciseSessionHandler, name="start_exercise_session"),
        url(r"/api/exercise/sessions/([^/]+)/end", EndExerciseSessionHandler, name="end_exercise_session"),
        url(r"/api/exercise/sessions/([^/]+)", GetExerciseSessionHandler, name="get_exercise_session"),
        url(r"/api/exercise/sessions", ListExerciseSessionsHandler, name="list_exercise_sessions"),
        
        # 运动数据提交
        url(r"/api/exercise/sessions/([^/]+)/data", SubmitExerciseDataHandler, name="submit_exercise_data"),
        
        # 统计和分析
        url(r"/api/exercise/statistics", GetExerciseStatisticsHandler, name="get_exercise_statistics"),
        url(r"/api/exercise/progress", GetExerciseProgressHandler, name="get_exercise_progress"),
        url(r"/api/exercise/recommendations", GetExerciseRecommendationsHandler, name="get_exercise_recommendations"),
    ]
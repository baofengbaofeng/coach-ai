"""
运动路由配置
"""

from .handlers import (
    ExerciseTypeHandler,
    ExerciseRecordHandler,
    ExercisePlanHandler,
    ExerciseProgressHandler,
    ExerciseRecommendationHandler
)


def get_exercise_routes():
    """获取运动路由配置"""
    return [
        # 运动类型路由
        (r"/api/exercise/types", ExerciseTypeHandler),
        (r"/api/exercise/types/([^/]+)", ExerciseTypeHandler),
        
        # 运动记录路由
        (r"/api/exercise/records", ExerciseRecordHandler),
        (r"/api/exercise/records/([^/]+)", ExerciseRecordHandler),
        
        # 运动计划路由
        (r"/api/exercise/plans", ExercisePlanHandler),
        (r"/api/exercise/plans/([^/]+)", ExercisePlanHandler),
        
        # 运动进度路由
        (r"/api/exercise/progress", ExerciseProgressHandler),
        
        # 运动推荐路由
        (r"/api/exercise/recommendations", ExerciseRecommendationHandler),
    ]
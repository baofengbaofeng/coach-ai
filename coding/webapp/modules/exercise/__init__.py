"""
运动管理模块
提供运动类型、运动记录、运动计划、摄像头集成等功能
"""

from .handlers import (
    ExerciseTypeHandler,
    ExerciseRecordHandler,
    ExerciseStatisticsHandler,
    ExercisePlanHandler,
    CameraDeviceHandler,
    ExerciseStartHandler,
    ExerciseCompleteHandler,
    PoseAnalysisHandler,
    WebRTCSignalingHandler
)

# 模块路由配置
routes = [
    # 运动类型管理
    (r"/api/exercise/types", ExerciseTypeHandler),
    (r"/api/exercise/types/([^/]+)", ExerciseTypeHandler),
    
    # 运动记录管理
    (r"/api/exercise/records", ExerciseRecordHandler),
    (r"/api/exercise/records/([^/]+)", ExerciseRecordHandler),
    
    # 运动统计
    (r"/api/exercise/statistics", ExerciseStatisticsHandler),
    
    # 运动计划管理
    (r"/api/exercise/plans", ExercisePlanHandler),
    (r"/api/exercise/plans/([^/]+)", ExercisePlanHandler),
    
    # 摄像头设备管理
    (r"/api/exercise/cameras", CameraDeviceHandler),
    (r"/api/exercise/cameras/([^/]+)", CameraDeviceHandler),
    
    # 运动控制
    (r"/api/exercise/start", ExerciseStartHandler),
    (r"/api/exercise/complete/([^/]+)", ExerciseCompleteHandler),
    
    # 姿势分析
    (r"/api/exercise/analyze/([^/]+)", PoseAnalysisHandler),
    
    # WebRTC信令
    (r"/api/exercise/webrtc/([^/]+)/signal", WebRTCSignalingHandler),
]

# 模块元数据
module_info = {
    'name': 'exercise',
    'version': '1.0.0',
    'description': '运动管理模块',
    'author': 'CoachAI Team',
    'routes': routes,
    'dependencies': ['auth', 'tenant'],
    'models': [
        'ExerciseType',
        'ExerciseRecord', 
        'ExercisePlan',
        'CameraDevice'
    ]
}

__all__ = [
    'ExerciseTypeHandler',
    'ExerciseRecordHandler',
    'ExerciseStatisticsHandler',
    'ExercisePlanHandler',
    'CameraDeviceHandler',
    'ExerciseStartHandler',
    'ExerciseCompleteHandler',
    'PoseAnalysisHandler',
    'WebRTCSignalingHandler',
    'routes',
    'module_info'
]
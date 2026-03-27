"""
运动处理器（简化迁移版）
处理运动相关的HTTP请求
"""

import logging
import json
from typing import Dict, Any, List
from tornado.web import RequestHandler
from src.interfaces.api.middleware.exceptions import ValidationError, AuthenticationError
from src.interfaces.api.middleware.auth_middleware import auth_required
from src.application.services.exercise_service import ExerciseService

logger = logging.getLogger(__name__)


class BaseExerciseHandler(RequestHandler):
    """基础运动处理器"""
    
    def get_json_body(self) -> Dict[str, Any]:
        """获取JSON请求体"""
        try:
            return json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            raise ValidationError("Invalid JSON format")
    
    def write_success(self, data: Dict[str, Any] = None, message: str = "Success"):
        """写入成功响应"""
        response = {
            "success": True,
            "message": message,
            "data": data or {}
        }
        self.write(response)
    
    def write_error_response(self, status_code: int, message: str):
        """写入错误响应"""
        self.set_status(status_code)
        self.write({
            "success": False,
            "error": {"message": message}
        })


class ExerciseTypeHandler(BaseExerciseHandler):
    """
    运动类型处理器
    """
    
    @auth_required
    async def get(self, type_id: str = None):
        """
        获取运动类型
        GET /api/exercise/types - 列出所有运动类型
        GET /api/exercise/types/{type_id} - 获取特定运动类型
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            tenant_id = self.current_user.get('tenant_id') if hasattr(self, 'current_user') else None
            
            exercise_service = ExerciseService()
            
            if type_id:
                # 获取特定运动类型
                result = await exercise_service.get_exercise_type(type_id, tenant_id)
            else:
                # 列出运动类型
                category = self.get_argument('category', None)
                difficulty = self.get_argument('difficulty', None)
                page = int(self.get_argument('page', 1))
                limit = int(self.get_argument('limit', 20))
                
                result = await exercise_service.list_exercise_types(
                    tenant_id=tenant_id,
                    category=category,
                    difficulty=difficulty,
                    page=page,
                    limit=limit
                )
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to get exercise types'))
            
            self.write_success(result.get('data'), "Exercise types retrieved")
            
        except Exception as e:
            logger.error(f"Get exercise types error: {e}")
            self.write_error_response(400, str(e))
    
    @auth_required
    async def post(self):
        """
        创建运动类型
        POST /api/exercise/types
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            tenant_id = self.current_user.get('tenant_id') if hasattr(self, 'current_user') else None
            
            data = self.get_json_body()
            
            required_fields = ['name_zh', 'name_en', 'code', 'category']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValidationError(f"Field '{field}' is required")
            
            exercise_service = ExerciseService()
            result = await exercise_service.create_exercise_type(
                name_zh=data['name_zh'],
                name_en=data['name_en'],
                code=data['code'],
                category=data['category'],
                difficulty=data.get('difficulty', 'beginner'),
                description=data.get('description'),
                standard_movement=data.get('standard_movement'),
                standard_video_url=data.get('standard_video_url'),
                tenant_id=tenant_id
            )
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to create exercise type'))
            
            self.write_success(result.get('data'), "Exercise type created")
            
        except Exception as e:
            logger.error(f"Create exercise type error: {e}")
            self.write_error_response(400, str(e))
    
    @auth_required
    async def put(self, type_id: str):
        """
        更新运动类型
        PUT /api/exercise/types/{type_id}
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            tenant_id = self.current_user.get('tenant_id') if hasattr(self, 'current_user') else None
            
            data = self.get_json_body()
            
            exercise_service = ExerciseService()
            result = await exercise_service.update_exercise_type(
                type_id=type_id,
                tenant_id=tenant_id,
                update_data=data
            )
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to update exercise type'))
            
            self.write_success(result.get('data'), "Exercise type updated")
            
        except Exception as e:
            logger.error(f"Update exercise type error: {e}")
            self.write_error_response(400, str(e))


class ExerciseRecordHandler(BaseExerciseHandler):
    """
    运动记录处理器
    """
    
    @auth_required
    async def get(self, record_id: str = None):
        """
        获取运动记录
        GET /api/exercise/records - 列出用户运动记录
        GET /api/exercise/records/{record_id} - 获取特定记录
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            exercise_service = ExerciseService()
            
            if record_id:
                # 获取特定记录
                result = await exercise_service.get_exercise_record(record_id, user_id)
            else:
                # 列出用户记录
                exercise_type_id = self.get_argument('exercise_type_id', None)
                start_date = self.get_argument('start_date', None)
                end_date = self.get_argument('end_date', None)
                page = int(self.get_argument('page', 1))
                limit = int(self.get_argument('limit', 20))
                
                result = await exercise_service.list_user_records(
                    user_id=user_id,
                    exercise_type_id=exercise_type_id,
                    start_date=start_date,
                    end_date=end_date,
                    page=page,
                    limit=limit
                )
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to get exercise records'))
            
            self.write_success(result.get('data'), "Exercise records retrieved")
            
        except Exception as e:
            logger.error(f"Get exercise records error: {e}")
            self.write_error_response(400, str(e))
    
    @auth_required
    async def post(self):
        """
        创建运动记录
        POST /api/exercise/records
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            data = self.get_json_body()
            
            required_fields = ['exercise_type_id']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValidationError(f"Field '{field}' is required")
            
            exercise_service = ExerciseService()
            result = await exercise_service.create_exercise_record(
                user_id=user_id,
                exercise_type_id=data['exercise_type_id'],
                duration_minutes=data.get('duration_minutes'),
                repetitions=data.get('repetitions'),
                sets=data.get('sets'),
                weight_kg=data.get('weight_kg'),
                distance_km=data.get('distance_km'),
                intensity=data.get('intensity'),
                notes=data.get('notes'),
                started_at=data.get('started_at'),
                completed_at=data.get('completed_at')
            )
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to create exercise record'))
            
            self.write_success(result.get('data'), "Exercise record created")
            
        except Exception as e:
            logger.error(f"Create exercise record error: {e}")
            self.write_error_response(400, str(e))
    
    @auth_required
    async def put(self, record_id: str):
        """
        更新运动记录
        PUT /api/exercise/records/{record_id}
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            data = self.get_json_body()
            
            exercise_service = ExerciseService()
            result = await exercise_service.update_exercise_record(
                record_id=record_id,
                user_id=user_id,
                update_data=data
            )
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to update exercise record'))
            
            self.write_success(result.get('data'), "Exercise record updated")
            
        except Exception as e:
            logger.error(f"Update exercise record error: {e}")
            self.write_error_response(400, str(e))
    
    @auth_required
    async def delete(self, record_id: str):
        """
        删除运动记录
        DELETE /api/exercise/records/{record_id}
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            exercise_service = ExerciseService()
            result = await exercise_service.delete_exercise_record(record_id, user_id)
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to delete exercise record'))
            
            self.write_success(result.get('data'), "Exercise record deleted")
            
        except Exception as e:
            logger.error(f"Delete exercise record error: {e}")
            self.write_error_response(400, str(e))


class ExercisePlanHandler(BaseExerciseHandler):
    """
    运动计划处理器
    """
    
    @auth_required
    async def get(self, plan_id: str = None):
        """
        获取运动计划
        GET /api/exercise/plans - 列出用户运动计划
        GET /api/exercise/plans/{plan_id} - 获取特定计划
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            exercise_service = ExerciseService()
            
            if plan_id:
                # 获取特定计划
                result = await exercise_service.get_exercise_plan(plan_id, user_id)
            else:
                # 列出用户计划
                status = self.get_argument('status', None)
                page = int(self.get_argument('page', 1))
                limit = int(self.get_argument('limit', 20))
                
                result = await exercise_service.list_user_plans(
                    user_id=user_id,
                    status=status,
                    page=page,
                    limit=limit
                )
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to get exercise plans'))
            
            self.write_success(result.get('data'), "Exercise plans retrieved")
            
        except Exception as e:
            logger.error(f"Get exercise plans error: {e}")
            self.write_error_response(400, str(e))
    
    @auth_required
    async def post(self):
        """
        创建运动计划
        POST /api/exercise/plans
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            data = self.get_json_body()
            
            required_fields = ['plan_name', 'schedule']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValidationError(f"Field '{field}' is required")
            
            exercise_service = ExerciseService()
            result = await exercise_service.create_exercise_plan(
                user_id=user_id,
                plan_name=data['plan_name'],
                description=data.get('description'),
                schedule=data['schedule'],
                plan_items=data.get('plan_items', [])
            )
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to create exercise plan'))
            
            self.write_success(result.get('data'), "Exercise plan created")
            
        except Exception as e:
            logger.error(f"Create exercise plan error: {e}")
            self.write_error_response(400, str(e))
    
    @auth_required
    async def put(self, plan_id: str):
        """
        更新运动计划
        PUT /api/exercise/plans/{plan_id}
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            data = self.get_json_body()
            
            exercise_service = ExerciseService()
            result = await exercise_service.update_exercise_plan(
                plan_id=plan_id,
                user_id=user_id,
                update_data=data
            )
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to update exercise plan'))
            
            self.write_success(result.get('data'), "Exercise plan updated")
            
        except Exception as e:
            logger.error(f"Update exercise plan error: {e}")
            self.write_error_response(400, str(e))


class ExerciseProgressHandler(BaseExerciseHandler):
    """
    运动进度处理器
    """
    
    @auth_required
    async def get(self):
        """
        获取运动进度分析
        GET /api/exercise/progress
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            period_days = int(self.get_argument('period_days', 30))
            
            exercise_service = ExerciseService()
            result = await exercise_service.analyze_exercise_progress(
                user_id=user_id,
                period_days=period_days
            )
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to analyze exercise progress'))
            
            self.write_success(result.get('data'), "Exercise progress analyzed")
            
        except Exception as e:
            logger.error(f"Get exercise progress error: {e}")
            self.write_error_response(400, str(e))


class ExerciseRecommendationHandler(BaseExerciseHandler):
    """
    运动推荐处理器
    """
    
    @auth_required
    async def get(self):
        """
        获取运动推荐
        GET /api/exercise/recommendations
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            goal = self.get_argument('goal', 'general_fitness')
            available_time = int(self.get_argument('available_time', 30))
            
            exercise_service = ExerciseService()
            result = await exercise_service.get_exercise_recommendations(
                user_id=user_id,
                goal=goal,
                available_time_minutes=available_time
            )
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to get exercise recommendations'))
            
            self.write_success(result.get('data'), "Exercise recommendations generated")
            
        except Exception as e:
            logger.error(f"Get exercise recommendations error: {e}")
            self.write_error_response(400, str(e))
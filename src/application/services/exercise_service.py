"""
运动应用服务
处理运动相关的业务逻辑
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger

from src.domain.exercise.services_simple import ExerciseService as DomainExerciseService
from src.domain.exercise.services_simple import ExercisePlanService as DomainExercisePlanService
from src.domain.exercise.entities import ExerciseType, ExerciseRecord, ExercisePlan


class ExerciseService:
    """运动应用服务"""
    
    def __init__(self):
        self.domain_service = DomainExerciseService()
        self.plan_service = DomainExercisePlanService()
    
    # 运动类型管理
    async def create_exercise_type(
        self,
        name_zh: str,
        name_en: str,
        code: str,
        category: str,
        difficulty: str = "beginner",
        description: Optional[str] = None,
        standard_movement: Optional[str] = None,
        standard_video_url: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建运动类型"""
        try:
            # 验证数据
            validation_result = self._validate_exercise_type_data(
                name_zh, name_en, code, category, difficulty
            )
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'error': '; '.join(validation_result['errors'])
                }
            
            # 检查代码是否已存在
            code_exists = await self._check_exercise_code_exists(code, tenant_id)
            if code_exists:
                return {
                    'success': False,
                    'error': 'Exercise code already exists'
                }
            
            # 创建运动类型实体
            exercise_type = self.domain_service.create_exercise_type(
                name_zh=name_zh,
                name_en=name_en,
                code=code,
                category=category,
                difficulty=difficulty,
                description=description,
                standard_movement=standard_movement,
                standard_video_url=standard_video_url,
                tenant_id=tenant_id
            )
            
            # 保存运动类型（需要持久化）
            # exercise_type_repository.save(exercise_type)
            
            return {
                'success': True,
                'data': {
                    'exercise_type': {
                        'id': exercise_type.id,
                        'name_zh': exercise_type.name_zh,
                        'name_en': exercise_type.name_en,
                        'code': exercise_type.code,
                        'category': str(exercise_type.category),
                        'difficulty': str(exercise_type.difficulty),
                        'created_at': exercise_type.created_at.isoformat()
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Create exercise type error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_exercise_type(self, type_id: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """获取运动类型"""
        try:
            # 查找运动类型
            # exercise_type = exercise_type_repository.find_by_id(type_id, tenant_id)
            # if not exercise_type:
            #     return {
            #         'success': False,
            #         'error': 'Exercise type not found'
            #     }
            
            # 暂时返回模拟数据
            return {
                'success': True,
                'data': {
                    'exercise_type': {
                        'id': type_id,
                        'name_zh': '俯卧撑',
                        'name_en': 'Push Up',
                        'code': 'pushup',
                        'category': 'strength',
                        'difficulty': 'beginner',
                        'description': '基础的上肢力量训练',
                        'created_at': '2026-03-27T00:00:00Z'
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Get exercise type error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def list_exercise_types(
        self,
        tenant_id: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """列出运动类型"""
        try:
            # 计算分页
            offset = (page - 1) * limit
            
            # 查找运动类型（需要持久化支持）
            # exercise_types = exercise_type_repository.find_all(
            #     tenant_id=tenant_id,
            #     category=category,
            #     difficulty=difficulty,
            #     offset=offset,
            #     limit=limit
            # )
            # total = exercise_type_repository.count_all(
            #     tenant_id=tenant_id,
            #     category=category,
            #     difficulty=difficulty
            # )
            
            # 暂时返回模拟数据
            exercise_types = [
                {
                    'id': 'type_1',
                    'name_zh': '俯卧撑',
                    'name_en': 'Push Up',
                    'code': 'pushup',
                    'category': 'strength',
                    'difficulty': 'beginner'
                },
                {
                    'id': 'type_2',
                    'name_zh': '深蹲',
                    'name_en': 'Squat',
                    'code': 'squat',
                    'category': 'strength',
                    'difficulty': 'beginner'
                },
                {
                    'id': 'type_3',
                    'name_zh': '跑步',
                    'name_en': 'Running',
                    'code': 'running',
                    'category': 'cardio',
                    'difficulty': 'beginner'
                }
            ]
            
            total = len(exercise_types)
            
            return {
                'success': True,
                'data': {
                    'exercise_types': exercise_types,
                    'total': total
                },
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
            }
            
        except Exception as e:
            logger.error(f"List exercise types error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def update_exercise_type(
        self,
        type_id: str,
        tenant_id: Optional[str],
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新运动类型"""
        try:
            # 验证更新数据
            validation_result = self._validate_exercise_type_update_data(update_data)
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'error': '; '.join(validation_result['errors'])
                }
            
            # 查找运动类型
            # exercise_type = exercise_type_repository.find_by_id(type_id, tenant_id)
            # if not exercise_type:
            #     return {
            #         'success': False,
            #         'error': 'Exercise type not found'
            #     }
            
            # 更新运动类型
            # if 'name_zh' in update_data:
            #     exercise_type.update_name_zh(update_data['name_zh'])
            # if 'name_en' in update_data:
            #     exercise_type.update_name_en(update_data['name_en'])
            # if 'description' in update_data:
            #     exercise_type.update_description(update_data['description'])
            
            # exercise_type_repository.save(exercise_type)
            
            return {
                'success': True,
                'data': {
                    'message': 'Exercise type updated successfully'
                }
            }
            
        except Exception as e:
            logger.error(f"Update exercise type error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # 运动记录管理
    async def create_exercise_record(
        self,
        user_id: str,
        exercise_type_id: str,
        duration_minutes: Optional[float] = None,
        repetitions: Optional[int] = None,
        sets: Optional[int] = None,
        weight_kg: Optional[float] = None,
        distance_km: Optional[float] = None,
        intensity: Optional[int] = None,
        notes: Optional[str] = None,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建运动记录"""
        try:
            # 验证数据
            validation_result = self._validate_exercise_record_data(
                duration_minutes, repetitions, sets, weight_kg, distance_km, intensity
            )
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'error': '; '.join(validation_result['errors'])
                }
            
            # 查找运动类型
            # exercise_type = exercise_type_repository.find_by_id(exercise_type_id)
            # if not exercise_type:
            #     return {
            #         'success': False,
            #         'error': 'Exercise type not found'
            #     }
            
            # 解析时间
            started_time = datetime.fromisoformat(started_at) if started_at else datetime.now()
            completed_time = datetime.fromisoformat(completed_at) if completed_at else datetime.now()
            
            # 计算卡路里（需要运动类型信息）
            # calories = self.domain_service.calculate_calories(
            #     exercise_type=exercise_type,
            #     user_weight_kg=70.0,  # 需要用户体重信息
            #     duration_minutes=duration_minutes or 0
            # )
            
            # 创建运动记录实体
            # record = ExerciseRecord(
            #     user_id=user_id,
            #     exercise_type_id=exercise_type_id,
            #     duration_minutes=duration_minutes,
            #     repetitions=repetitions,
            #     sets=sets,
            #     weight_kg=weight_kg,
            #     distance_km=distance_km,
            #     intensity=intensity,
            #     notes=notes,
            #     started_at=started_time,
            #     completed_at=completed_time,
            #     calories_burned=calories
            # )
            
            # 保存记录
            # exercise_record_repository.save(record)
            
            # 发送记录创建通知（异步）
            asyncio.create_task(self._send_exercise_record_notification(user_id, exercise_type_id))
            
            return {
                'success': True,
                'data': {
                    'record': {
                        'id': 'record_1',  # 临时ID
                        'user_id': user_id,
                        'exercise_type_id': exercise_type_id,
                        'duration_minutes': duration_minutes,
                        'calories_burned': 150,  # 临时值
                        'created_at': datetime.now().isoformat()
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Create exercise record error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_exercise_record(self, record_id: str, user_id: str) -> Dict[str, Any]:
        """获取运动记录"""
        try:
            # 查找记录
            # record = exercise_record_repository.find_by_id_and_user(record_id, user_id)
            # if not record:
            #     return {
            #         'success': False,
            #         'error': 'Exercise record not found'
            #     }
            
            # 暂时返回模拟数据
            return {
                'success': True,
                'data': {
                    'record': {
                        'id': record_id,
                        'user_id': user_id,
                        'exercise_type_id': 'type_1',
                        'exercise_type_name': '俯卧撑',
                        'duration_minutes': 30,
                        'repetitions': 50,
                        'sets': 3,
                        'calories_burned': 150,
                        'started_at': '2026-03-27T10:00:00Z',
                        'completed_at': '2026-03-27T10:30:00Z',
                        'notes': '今天的训练感觉很好'
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Get exercise record error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def list_user_records(
        self,
        user_id: str,
        exercise_type_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """列出用户运动记录"""
        try:
            # 计算分页
            offset = (page - 1) * limit
            
            # 解析日期
            start_datetime = datetime.fromisoformat(start_date) if start_date else None
            end_datetime = datetime.fromisoformat(end_date) if end_date else None
            
            # 查找记录（需要持久化支持）
            # records = exercise_record_repository.find_by_user(
            #     user_id=user_id,
            #     exercise_type_id=exercise_type_id,
            #     start_date=start_datetime,
            #     end_date=end_datetime,
            #     offset=offset,
            #     limit=limit
            # )
            # total = exercise_record_repository.count_by_user(
            #     user_id=user_id,
            #     exercise_type_id=exercise_type_id,
            #     start_date=start_datetime,
            #     end_date=end_datetime
            # )
            
            # 暂时返回模拟数据
            records = [
                {
                    'id': 'record_1',
                    'exercise_type_id': 'type_1',
                    'exercise_type_name': '俯卧撑',
                    'duration_minutes': 30,
                    'calories_burned': 150,
                    'completed_at': '2026-03-27T10:30:00Z'
                },
                {
                    'id': 'record_2',
                    'exercise_type_id': 'type_3',
                    'exercise_type_name': '跑步',
                    'duration_minutes': 45,
                    'distance_km': 5.0,
                    'calories_burned': 300,
                    'completed_at': '2026-03-26T09:00:00Z'
                }
            ]
            
            total = len(records)
            
            return {
                'success': True,
                'data': {
                    'records': records,
                    'total': total
                },
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
            }
            
        except Exception as e:
            logger.error(f"List user records error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def update_exercise_record(
        self,
        record_id: str,
        user_id: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新运动记录"""
        try:
            # 验证更新数据
            validation_result = self._validate_exercise_record_update_data(update_data)
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'error': '; '.join(validation_result['errors'])
                }
            
            # 查找记录
            # record = exercise_record_repository.find_by_id_and_user(record_id, user_id)
            # if not record:
            #     return {
            #         'success': False,
            #         'error': 'Exercise record not found'
            #     }
            
            # 更新记录
            # if 'duration_minutes' in update_data:
            #     record.update_duration(update_data['duration_minutes'])
            # if 'notes' in update_data:
            #     record.update_notes(update_data['notes'])
            
            # 重新计算卡路里
            # if any(field in update_data for field in ['duration_minutes', 'repetitions', 'sets', 'weight_kg', 'distance_km']):
            #     # 需要重新计算卡路里
            #     pass
            
            # exercise_record_repository.save(record)
            
            return {
                'success': True,
                'data': {
                    'message': 'Exercise record updated successfully'
                }
            }
            
        except Exception as e:
            logger.error(f"Update exercise record error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def delete_exercise_record(self, record_id: str, user_id: str) -> Dict[str, Any]:
        """删除运动记录"""
        try:
            # 查找记录
            # record = exercise_record_repository.find_by_id_and_user(record_id, user_id)
            # if not record:
            #     return {
            #         'success': False,
            #         'error': 'Exercise record not found'
            #     }
            
            # 删除记录
            # exercise_record_repository.delete(record_id)
            
            return {
                'success': True,
                'data': {
                    'message': 'Exercise record deleted successfully'
                }
            }
            
        except Exception as e:
            logger.error(f"Delete exercise record error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # 运动计划管理
    async def create_exercise_plan(
        self,
        user_id: str,
        plan_name: str,
        description: Optional[str] = None,
        schedule: Optional[Dict[str, Any]] = None,
        plan_items: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """创建运动计划"""
        try:
            # 验证数据
            if not plan_name or len(plan_name.strip()) < 2:
                return {
                    'success': False,
                    'error': 'Plan name must be at least 2 characters'
                }
            
            # 创建运动计划
            plan = self.plan_service.create_plan(
                user_id=user_id,
                level='beginner',  # 需要用户水平信息
                goal='general_fitness',  # 需要用户目标信息
                days_per_week=
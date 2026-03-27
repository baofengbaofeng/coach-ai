"""
运动模块服务层
处理运动相关的业务逻辑
"""

import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
import json
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc

from coding.database.connection import get_db_session
from coding.database.models import (
    ExerciseType, ExerciseRecord, ExercisePlan, CameraDevice,
    User, Tenant
)
from .models import (
    ExerciseStatistics, ExerciseGoal, ExerciseAchievement,
    CameraStreamConfig, PoseAnalysisResult, ExerciseRecommendation
)

logger = logging.getLogger(__name__)


class ExerciseTypeService:
    """
    运动类型服务
    """
    
    def __init__(self, db_session: Session = None):
        """
        初始化运动类型服务
        
        Args:
            db_session: 数据库会话，如果为None则创建新会话
        """
        self.db_session = db_session or get_db_session()
    
    def create_exercise_type(self, data: Dict[str, Any], created_by: str = None) -> ExerciseType:
        """
        创建运动类型
        
        Args:
            data: 运动类型数据
            created_by: 创建者ID
            
        Returns:
            ExerciseType: 创建的运动类型对象
        """
        try:
            # 验证必要字段
            required_fields = ['name_zh', 'name_en', 'code']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # 检查code是否已存在
            existing = self.db_session.query(ExerciseType).filter(
                ExerciseType.code == data['code']
            ).first()
            
            if existing:
                raise ValueError(f"Exercise type with code '{data['code']}' already exists")
            
            # 处理JSON字段
            if 'target_muscles' in data and isinstance(data['target_muscles'], list):
                data['target_muscles'] = json.dumps(data['target_muscles'])
            
            if 'secondary_muscles' in data and isinstance(data['secondary_muscles'], list):
                data['secondary_muscles'] = json.dumps(data['secondary_muscles'])
            
            # 创建运动类型
            exercise_type = ExerciseType(**data)
            
            if created_by:
                exercise_type.created_by = created_by
            
            self.db_session.add(exercise_type)
            self.db_session.commit()
            
            logger.info(f"Created exercise type: {exercise_type.code}")
            return exercise_type
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to create exercise type: {str(e)}")
            raise
    
    def get_exercise_type(self, exercise_type_id: str) -> Optional[ExerciseType]:
        """
        获取运动类型
        
        Args:
            exercise_type_id: 运动类型ID
            
        Returns:
            Optional[ExerciseType]: 运动类型对象，如果不存在则返回None
        """
        try:
            exercise_type = self.db_session.query(ExerciseType).filter(
                ExerciseType.id == exercise_type_id,
                ExerciseType.is_deleted == False
            ).first()
            
            return exercise_type
            
        except Exception as e:
            logger.error(f"Failed to get exercise type {exercise_type_id}: {str(e)}")
            raise
    
    def update_exercise_type(self, exercise_type_id: str, data: Dict[str, Any], updated_by: str = None) -> Optional[ExerciseType]:
        """
        更新运动类型
        
        Args:
            exercise_type_id: 运动类型ID
            data: 更新数据
            updated_by: 更新者ID
            
        Returns:
            Optional[ExerciseType]: 更新后的运动类型对象，如果不存在则返回None
        """
        try:
            exercise_type = self.get_exercise_type(exercise_type_id)
            if not exercise_type:
                return None
            
            # 处理JSON字段
            if 'target_muscles' in data and isinstance(data['target_muscles'], list):
                data['target_muscles'] = json.dumps(data['target_muscles'])
            
            if 'secondary_muscles' in data and isinstance(data['secondary_muscles'], list):
                data['secondary_muscles'] = json.dumps(data['secondary_muscles'])
            
            # 更新字段
            for key, value in data.items():
                if hasattr(exercise_type, key):
                    setattr(exercise_type, key, value)
            
            if updated_by:
                exercise_type.updated_by = updated_by
            
            self.db_session.commit()
            
            logger.info(f"Updated exercise type: {exercise_type.code}")
            return exercise_type
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to update exercise type {exercise_type_id}: {str(e)}")
            raise
    
    def delete_exercise_type(self, exercise_type_id: str, deleted_by: str = None) -> bool:
        """
        删除运动类型（软删除）
        
        Args:
            exercise_type_id: 运动类型ID
            deleted_by: 删除者ID
            
        Returns:
            bool: 是否成功删除
        """
        try:
            exercise_type = self.get_exercise_type(exercise_type_id)
            if not exercise_type:
                return False
            
            exercise_type.soft_delete(deleted_by)
            self.db_session.commit()
            
            logger.info(f"Deleted exercise type: {exercise_type.code}")
            return True
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to delete exercise type {exercise_type_id}: {str(e)}")
            raise
    
    def list_exercise_types(self, filters: Dict[str, Any] = None, 
                          page: int = 1, page_size: int = 20) -> Tuple[List[ExerciseType], int]:
        """
        列出运动类型
        
        Args:
            filters: 过滤条件
            page: 页码
            page_size: 每页大小
            
        Returns:
            Tuple[List[ExerciseType], int]: (运动类型列表, 总数)
        """
        try:
            query = self.db_session.query(ExerciseType).filter(
                ExerciseType.is_deleted == False
            )
            
            # 应用过滤条件
            if filters:
                if 'category' in filters:
                    query = query.filter(ExerciseType.category == filters['category'])
                
                if 'difficulty' in filters:
                    query = query.filter(ExerciseType.difficulty == filters['difficulty'])
                
                if 'is_active' in filters:
                    query = query.filter(ExerciseType.is_active == filters['is_active'])
                
                if 'tenant_id' in filters:
                    query = query.filter(ExerciseType.tenant_id == filters['tenant_id'])
                
                if 'search' in filters:
                    search_term = f"%{filters['search']}%"
                    query = query.filter(
                        or_(
                            ExerciseType.name_zh.like(search_term),
                            ExerciseType.name_en.like(search_term),
                            ExerciseType.code.like(search_term),
                            ExerciseType.description.like(search_term)
                        )
                    )
            
            # 获取总数
            total = query.count()
            
            # 分页
            offset = (page - 1) * page_size
            query = query.order_by(ExerciseType.created_at.desc())
            query = query.offset(offset).limit(page_size)
            
            exercise_types = query.all()
            
            return exercise_types, total
            
        except Exception as e:
            logger.error(f"Failed to list exercise types: {str(e)}")
            raise


class ExerciseRecordService:
    """
    运动记录服务
    """
    
    def __init__(self, db_session: Session = None):
        """
        初始化运动记录服务
        
        Args:
            db_session: 数据库会话，如果为None则创建新会话
        """
        self.db_session = db_session or get_db_session()
    
    def create_exercise_record(self, data: Dict[str, Any], created_by: str = None) -> ExerciseRecord:
        """
        创建运动记录
        
        Args:
            data: 运动记录数据
            created_by: 创建者ID
            
        Returns:
            ExerciseRecord: 创建的运动记录对象
        """
        try:
            # 验证必要字段
            required_fields = ['user_id', 'exercise_type_id', 'start_time']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # 处理JSON字段
            if 'sensor_data' in data and isinstance(data['sensor_data'], dict):
                data['sensor_data'] = json.dumps(data['sensor_data'])
            
            if 'video_analysis_data' in data and isinstance(data['video_analysis_data'], dict):
                data['video_analysis_data'] = json.dumps(data['video_analysis_data'])
            
            # 创建运动记录
            exercise_record = ExerciseRecord(**data)
            
            if created_by:
                exercise_record.created_by = created_by
            
            # 如果提供了结束时间，计算持续时间
            if exercise_record.end_time:
                exercise_record.calculate_duration()
                exercise_record.calculate_calories()
            
            self.db_session.add(exercise_record)
            self.db_session.commit()
            
            logger.info(f"Created exercise record for user {exercise_record.user_id}")
            return exercise_record
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to create exercise record: {str(e)}")
            raise
    
    def start_exercise(self, user_id: str, exercise_type_id: str, 
                      user_weight_kg: float = None, camera_device_id: str = None) -> ExerciseRecord:
        """
        开始运动
        
        Args:
            user_id: 用户ID
            exercise_type_id: 运动类型ID
            user_weight_kg: 用户体重（公斤）
            camera_device_id: 摄像头设备ID
            
        Returns:
            ExerciseRecord: 创建的运动记录对象
        """
        try:
            data = {
                'user_id': user_id,
                'exercise_type_id': exercise_type_id,
                'start_time': datetime.utcnow(),
                'status': 'in_progress',
                'mode': 'camera_auto' if camera_device_id else 'manual'
            }
            
            if user_weight_kg:
                data['user_weight_kg'] = user_weight_kg
            
            if camera_device_id:
                data['camera_device_id'] = camera_device_id
            
            exercise_record = self.create_exercise_record(data, created_by=user_id)
            
            logger.info(f"Started exercise for user {user_id}")
            return exercise_record
            
        except Exception as e:
            logger.error(f"Failed to start exercise for user {user_id}: {str(e)}")
            raise
    
    def complete_exercise(self, exercise_record_id: str, total_repetitions: int = 0, 
                         total_sets: int = 0, notes: str = None) -> Optional[ExerciseRecord]:
        """
        完成运动
        
        Args:
            exercise_record_id: 运动记录ID
            total_repetitions: 总重复次数
            total_sets: 总组数
            notes: 备注
            
        Returns:
            Optional[ExerciseRecord]: 更新后的运动记录对象，如果不存在则返回None
        """
        try:
            exercise_record = self.get_exercise_record(exercise_record_id)
            if not exercise_record:
                return None
            
            if exercise_record.status != 'in_progress':
                raise ValueError(f"Cannot complete exercise with status: {exercise_record.status}")
            
            exercise_record.complete_exercise(total_repetitions, total_sets, notes)
            self.db_session.commit()
            
            logger.info(f"Completed exercise record {exercise_record_id}")
            return exercise_record
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to complete exercise record {exercise_record_id}: {str(e)}")
            raise
    
    def get_exercise_record(self, exercise_record_id: str) -> Optional[ExerciseRecord]:
        """
        获取运动记录
        
        Args:
            exercise_record_id: 运动记录ID
            
        Returns:
            Optional[ExerciseRecord]: 运动记录对象，如果不存在则返回None
        """
        try:
            exercise_record = self.db_session.query(ExerciseRecord).filter(
                ExerciseRecord.id == exercise_record_id,
                ExerciseRecord.is_deleted == False
            ).first()
            
            return exercise_record
            
        except Exception as e:
            logger.error(f"Failed to get exercise record {exercise_record_id}: {str(e)}")
            raise
    
    def list_exercise_records(self, user_id: str = None, filters: Dict[str, Any] = None,
                            page: int = 1, page_size: int = 20) -> Tuple[List[ExerciseRecord], int]:
        """
        列出运动记录
        
        Args:
            user_id: 用户ID（可选）
            filters: 过滤条件
            page: 页码
            page_size: 每页大小
            
        Returns:
            Tuple[List[ExerciseRecord], int]: (运动记录列表, 总数)
        """
        try:
            query = self.db_session.query(ExerciseRecord).filter(
                ExerciseRecord.is_deleted == False
            )
            
            if user_id:
                query = query.filter(ExerciseRecord.user_id == user_id)
            
            # 应用过滤条件
            if filters:
                if 'exercise_type_id' in filters:
                    query = query.filter(ExerciseRecord.exercise_type_id == filters['exercise_type_id'])
                
                if 'status' in filters:
                    query = query.filter(ExerciseRecord.status == filters['status'])
                
                if 'mode' in filters:
                    query = query.filter(ExerciseRecord.mode == filters['mode'])
                
                if 'start_date' in filters:
                    query = query.filter(ExerciseRecord.start_time >= filters['start_date'])
                
                if 'end_date' in filters:
                    query = query.filter(ExerciseRecord.start_time <= filters['end_date'])
                
                if 'tenant_id' in filters:
                    query = query.filter(ExerciseRecord.tenant_id == filters['tenant_id'])
                
                if 'is_verified' in filters:
                    query = query.filter(ExerciseRecord.is_verified == filters['is_verified'])
            
            # 获取总数
            total = query.count()
            
            # 分页
            offset = (page - 1) * page_size
            query = query.order_by(ExerciseRecord.start_time.desc())
            query = query.offset(offset).limit(page_size)
            
            exercise_records = query.all()
            
            return exercise_records, total
            
        except Exception as e:
            logger.error(f"Failed to list exercise records: {str(e)}")
            raise
    
    def get_statistics(self, user_id: str, period: str = 'daily', 
                      start_date: date = None, end_date: date = None) -> ExerciseStatistics:
        """
        获取运动统计数据
        
        Args:
            user_id: 用户ID
            period: 统计周期
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            ExerciseStatistics: 运动统计数据
        """
        try:
            stats = ExerciseStatistics(user_id, period)
            
            # 设置日期范围
            today = datetime.utcnow().date()
            if period == 'daily':
                stats.start_date = today
                stats.end_date = today
            elif period == 'weekly':
                stats.start_date = today - timedelta(days=today.weekday())
                stats.end_date = stats.start_date + timedelta(days=6)
            elif period == 'monthly':
                stats.start_date = today.replace(day=1)
                next_month = stats.start_date.replace(day=28) + timedelta(days=4)
                stats.end_date = next_month - timedelta(days=next_month.day)
            elif period == 'yearly':
                stats.start_date = today.replace(month=1, day=1)
                stats.end_date = today.replace(month=12, day=31)
            
            # 如果提供了自定义日期范围
            if start_date:
                stats.start_date = start_date
            if end_date:
                stats.end_date = end_date
            
            # 查询运动记录
            query = self.db_session.query(ExerciseRecord).filter(
                ExerciseRecord.user_id == user_id,
                ExerciseRecord.is_deleted == False,
                ExerciseRecord.status == 'completed',
                func.date(ExerciseRecord.start_time) >= stats.start_date,
                func.date(ExerciseRecord.start_time) <= stats.end_date
            )
            
            records = query.all()
            
            # 计算统计数据
            stats.total_exercises = len(records)
            
            for record in records:
                stats.total_duration_minutes += record.duration_minutes
                stats.total_calories += record.estimated_calories or 0
                stats.total_repetitions += record.total_repetitions
                stats.total_sets += record.total_sets
                
                if record.quality_score:
                    stats.avg_quality_score += record.quality_score
                
                if record.posture_accuracy:
                    stats.avg_posture_accuracy += record.posture_accuracy
                
                # 运动类型分布
                exercise_type_id = record.exercise_type_id
                stats.exercise_type_distribution[exercise_type_id] = \
                    stats.exercise_type_distribution.get(exercise_type_id, 0) + 1
            
            # 计算平均值
            if stats.total_exercises > 0:
                stats.avg_quality_score = round(stats.avg_quality_score / stats.total_exercises, 1)
                stats.avg_posture_accuracy = round(stats.avg_posture_accuracy / stats.total_exercises, 1)
            
            # 获取最频繁的运动
            if stats.exercise_type_distribution:
                most_frequent_id = max(stats.exercise_type_distribution, 
                                     key=stats.exercise_type_distribution.get)
                # 这里可以查询运动类型名称
                # stats.most_frequent_exercise = most_frequent_id
            
            # 获取质量最好的运动
            if records:
                best_record = max(records, key=lambda r: r.quality_score or 0)
                stats.best_quality_exercise = best_record.id
            
            # 计算每日完成率（需要查询计划）
            # 这里简化处理
            stats.daily_completion_rate = min(100, stats.total_exercises * 10)
            
            # 获取连续天数
            stats.streak_days = self._calculate_streak_days(user_id)
            
            # 获取最近活动
            recent_records = records[:5]  # 最近5条记录
            stats.recent_activities = [
                {
                    'id': r.id,
                    'exercise_type_id': r.exercise_type_id,
                    'start_time': r.start_time.isoformat() if r.start_time else None,
                    'duration_minutes': r.duration_minutes,
                    'total_repetitions': r.total_repetitions,
                    'quality_score': r.quality_score
                }
                for r in recent_records
            ]
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics for user {user_id}: {str(e)}")
            raise
    
    def _calculate_streak_days(self, user_id: str) -> int:
        """
        计算连续运动天数
        
        Args:
            user_id: 用户ID
            
        Returns:
            int: 连续天数
        """
        try:
            # 查询最近的运动记录日期
            query = self.db_session.query(
                func.date(ExerciseRecord.start_time).label('exercise_date')
            ).filter(
                ExerciseRecord.user_id == user_id,
                ExerciseRecord.is_deleted == False,
                ExerciseRecord.status == 'completed'
            ).group_by(
                func.date(ExerciseRecord.start_time)
            ).order_by(
                desc(func.date(ExerciseRecord.start_time))
            )
            
            dates = [row.exercise_date for row in query.all()]
            
            # 计算连续天数
            streak = 0
            today = datetime.utcnow().date()
            current_date = today
            
            for i in range(30):  # 最多检查30天
                if current_date in dates:
                    streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break
            
            return streak
            
        except Exception as e:
            logger.error(f"Failed to calculate streak days for user {user_id}: {str(e)}")
            return 0


class ExercisePlanService:
    """
    运动计划服务
    """
    
    def __init__(self, db_session: Session = None):
        """
        初始化运动计划服务
        
        Args:
            db_session: 数据库会话，如果为None则创建新会话
        """
        self.db_session = db_session or get_db_session()
    
    def create_exercise_plan(self, data: Dict[str, Any], created_by: str = None) -> ExercisePlan:
        """
        创建运动计划
        
        Args:
            data: 运动计划数据
            created_by: 创建者ID
            
        Returns:
            ExercisePlan: 创建的运动计划对象
        """
        try:
            # 验证必要字段
            required_fields = ['user_id', 'exercise_type_id', 'plan_name', 'start_date']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # 处理JSON字段
            if 'weekly_days' in data and isinstance(data['weekly_days'], list):
                data['weekly_days'] = json.dumps(data['weekly_days'])
            
            if 'custom_rules' in data and isinstance(data['custom_rules'], dict):
                data['custom_rules'] = json.dumps(data['custom_rules'])
            
            # 创建运动计划
            exercise_plan = ExercisePlan(**data)
            
            if created_by:
                exercise_plan.created_by = created_by
            
            self.db_session.add(exercise_plan)
            self.db_session.commit()
            
            logger.info(f"Created exercise plan: {exercise_plan.plan_name}")
            return exercise_plan
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to create exercise plan: {str(e)}")
            raise
    
    def get_exercise_plan(self, exercise_plan_id: str) -> Optional[ExercisePlan]:
        """
        获取运动计划
        
        Args:
            exercise_plan_id: 运动计划ID
            
        Returns:
            Optional[ExercisePlan]: 运动计划对象，如果不存在则返回None
        """
        try:
            exercise_plan = self.db_session.query(ExercisePlan).filter(
                ExercisePlan.id == exercise_plan_id,
                ExercisePlan.is_deleted == False
            ).first()
            
            return exercise_plan
            
        except Exception as e:
            logger.error(f"Failed to get exercise plan {exercise_plan_id}: {str(e)}")
            raise
    
    def update_exercise_plan(self, exercise_plan_id: str, data: Dict[str, Any], 
                           updated_by: str = None) -> Optional[ExercisePlan]:
        """
        更新运动计划
        
        Args:
            exercise_plan_id: 运动计划ID
            data: 更新数据
            updated_by: 更新者ID
            
        Returns:
            Optional[ExercisePlan]: 更新后的运动计划对象，如果不存在则返回None
        """
        try:
            exercise_plan = self.get_exercise_plan(exercise_plan_id)
            if not exercise_plan:
                return None
            
            # 处理JSON字段
            if 'weekly_days' in data and isinstance(data['weekly_days'], list):
                data['weekly_days'] = json.dumps(data['weekly_days'])
            
            if 'custom_rules' in data and isinstance(data['custom_rules'], dict):
                data['custom_rules'] = json.dumps(data['custom_rules'])
            
            # 更新字段
            for key, value in data.items():
                if hasattr(exercise_plan, key):
                    setattr(exercise_plan, key, value)
            
            if updated_by:
                exercise_plan.updated_by = updated_by
            
            self.db_session.commit()
            
            logger.info(f"Updated exercise plan: {exercise_plan.plan_name}")
            return exercise_plan
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to update exercise plan {exercise_plan_id}: {str(e)}")
            raise
    
    def mark_plan_completed(self, exercise_plan_id: str, 
                          actual_repetitions: int = None, 
                          actual_sets: int = None, 
                          actual_duration: int = None) -> Optional[ExercisePlan]:
        """
        标记计划为已完成
        
        Args:
            exercise_plan_id: 运动计划ID
            actual_repetitions: 实际重复次数
            actual_sets: 实际组数
            actual_duration: 实际持续时间
            
        Returns:
            Optional[ExercisePlan]: 更新后的运动计划对象，如果不存在则返回None
        """
        try:
            exercise_plan = self.get_exercise_plan(exercise_plan_id)
            if not exercise_plan:
                return None
            
            exercise_plan.mark_completed(actual_repetitions, actual_sets, actual_duration)
            self.db_session.commit()
            
            logger.info(f"Marked exercise plan {exercise_plan_id} as completed")
            return exercise_plan
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to mark exercise plan {exercise_plan_id} as completed: {str(e)}")
            raise
    
    def get_todays_plans(self, user_id: str) -> List[ExercisePlan]:
        """
        获取用户今天的运动计划
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[ExercisePlan]: 今天的运动计划列表
        """
        try:
            query = self.db_session.query(ExercisePlan).filter(
                ExercisePlan.user_id == user_id,
                ExercisePlan.is_deleted == False,
                ExercisePlan.status == 'active'
            )
            
            plans = query.all()
            
            # 过滤出今天到期的计划
            todays_plans = [plan for plan in plans if plan.is_due_today]
            
            return todays_plans
            
        except Exception as e:
            logger.error(f"Failed to get today's plans for user {user_id}: {str(e)}")
            raise


class CameraDeviceService:
    """
    摄像头设备服务
    """
    
    def __init__(self, db_session: Session = None):
        """
        初始化摄像头设备服务
        
        Args:
            db_session: 数据库会话，如果为None则创建新会话
        """
        self.db_session = db_session or get_db_session()
    
    def register_camera_device(self, data: Dict[str, Any], created_by: str = None) -> CameraDevice:
        """
        注册摄像头设备
        
        Args:
            data: 摄像头设备数据
            created_by: 创建者ID
            
        Returns:
            CameraDevice: 注册的摄像头设备对象
        """
        try:
            # 验证必要字段
            required_fields = ['device_name', 'serial_number', 'device_type']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # 检查序列号是否已存在
            existing = self.db_session.query(CameraDevice).filter(
                CameraDevice.serial_number == data['serial_number']
            ).first()
            
            if existing:
                raise ValueError(f"Camera device with serial number '{data['serial_number']}' already exists")
            
            # 处理JSON字段
            if 'calibration_data' in data and isinstance(data['calibration_data'], dict):
                data['calibration_data'] = json.dumps(data['calibration_data'])
            
            if 'device_config' in data and isinstance(data['device_config'], dict):
                data['device_config'] = json.dumps(data['device_config'])
            
            # 创建摄像头设备
            camera_device = CameraDevice(**data)
            
            if created_by:
                camera_device.created_by = created_by
            
            self.db_session.add(camera_device)
            self.db_session.commit()
            
            logger.info(f"Registered camera device: {camera_device.device_name}")
            return camera_device
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to register camera device: {str(e)}")
            raise
    
    def connect_camera_device(self, camera_device_id: str, ip_address: str = None, 
                            port: int = None) -> Optional[CameraDevice]:
        """
        连接摄像头设备
        
        Args:
            camera_device_id: 摄像头设备ID
            ip_address: IP地址
            port: 端口
            
        Returns:
            Optional[CameraDevice]: 更新后的摄像头设备对象，如果不存在则返回None
        """
        try:
            camera_device = self.get_camera_device(camera_device_id)
            if not camera_device:
                return None
            
            camera_device.connect(ip_address, port)
            self.db_session.commit()
            
            logger.info(f"Connected camera device: {camera_device.device_name}")
            return camera_device
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to connect camera device {camera_device_id}: {str(e)}")
            raise
    
    def get_available_cameras(self, tenant_id: str = None) -> List[CameraDevice]:
        """
        获取可用的摄像头设备
        
        Args:
            tenant_id: 租户ID（可选）
            
        Returns:
            List[CameraDevice]: 可用的摄像头设备列表
        """
        try:
            query = self.db_session.query(CameraDevice).filter(
                CameraDevice.is_deleted == False,
                CameraDevice.is_enabled == True,
                CameraDevice.connection_status == 'online',
                CameraDevice.is_in_use == False
            )
            
            if tenant_id:
                query = query.filter(CameraDevice.tenant_id == tenant_id)
            
            cameras = query.all()
            return cameras
            
        except Exception as e:
            logger.error(f"Failed to get available cameras: {str(e)}")
            raise
    
    def get_camera_device(self, camera_device_id: str) -> Optional[CameraDevice]:
        """
        获取摄像头设备
        
        Args:
            camera_device_id: 摄像头设备ID
            
        Returns:
            Optional[CameraDevice]: 摄像头设备对象，如果不存在则返回None
        """
        try:
            camera_device = self.db_session.query(CameraDevice).filter(
                CameraDevice.id == camera_device_id,
                CameraDevice.is_deleted == False
            ).first()
            
            return camera_device
            
        except Exception as e:
            logger.error(f"Failed to get camera device {camera_device_id}: {str(e)}")
            raise


class ExerciseAnalysisService:
    """
    运动分析服务
    """
    
    def __init__(self, db_session: Session = None):
        """
        初始化运动分析服务
        
        Args:
            db_session: 数据库会话，如果为None则创建新会话
        """
        self.db_session = db_session or get_db_session()
    
    def analyze_pose(self, exercise_record_id: str, landmarks: List[Dict], 
                    exercise_type: ExerciseType) -> PoseAnalysisResult:
        """
        分析姿势
        
        Args:
            exercise_record_id: 运动记录ID
            landmarks: 关键点坐标
            exercise_type: 运动类型
            
        Returns:
            PoseAnalysisResult: 姿势分析结果
        """
        try:
            result = PoseAnalysisResult(exercise_record_id)
            result.landmarks = landmarks
            
            # 这里可以实现具体的姿势分析逻辑
            # 基于运动类型分析关键点
            
            if exercise_type.code == 'pushup':
                result = self._analyze_pushup(landmarks, result)
            elif exercise_type.code == 'squat':
                result = self._analyze_squat(landmarks, result)
            elif exercise_type.code == 'situp':
                result = self._analyze_situp(landmarks, result)
            # 添加其他运动类型的分析
            
            result.calculate_posture_score()
            
            logger.info(f"Analyzed pose for exercise record {exercise_record_id}, score: {result.posture_score}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze pose for exercise record {exercise_record_id}: {str(e)}")
            raise
    
    def _analyze_pushup(self, landmarks: List[Dict], result: PoseAnalysisResult) -> PoseAnalysisResult:
        """
        分析俯卧撑姿势
        
        Args:
            landmarks: 关键点坐标
            result: 姿势分析结果
            
        Returns:
            PoseAnalysisResult: 更新后的姿势分析结果
        """
        # 这里实现俯卧撑姿势分析逻辑
        # 检查关键点：肩膀、肘部、手腕、臀部、膝盖、脚踝
        
        # 示例：检查身体是否成直线
        shoulder_y = landmarks[11]['y'] if len(landmarks) > 11 else 0  # 左肩
        hip_y = landmarks[23]['y'] if len(landmarks) > 23 else 0  # 左臀
        ankle_y = landmarks[27]['y'] if len(landmarks) > 27 else 0  # 左脚踝
        
        # 计算身体直线度
        body_alignment = abs((shoulder_y - hip_y) - (hip_y - ankle_y))
        
        if body_alignment > 0.1:  # 阈值
            result.add_feedback("Keep your body in a straight line", "warning")
            result.alignment_errors.append({
                'type': 'body_alignment',
                'severity': 'medium',
                'message': 'Body not in straight line'
            })
        
        # 计算肘部角度
        # 这里需要实现角度计算逻辑
        
        result.movement_quality = 85  # 示例值
        result.confidence = 0.9
        
        return result
    
    def _analyze_squat(self, landmarks: List[Dict], result: PoseAnalysisResult) -> PoseAnalysisResult:
        """
        分析深蹲姿势
        
        Args:
            landmarks: 关键点坐标
            result: 姿势分析结果
            
        Returns:
            PoseAnalysisResult: 更新后的姿势分析结果
        """
        # 这里实现深蹲姿势分析逻辑
        # 检查关键点：臀部、膝盖、脚踝
        
        result.movement_quality = 80  # 示例值
        result.confidence = 0.85
        
        return result
    
    def _analyze_situp(self, landmarks: List[Dict], result: PoseAnalysisResult) -> PoseAnalysisResult:
        """
        分析仰卧起坐姿势
        
        Args:
            landmarks: 关键点坐标
            result: 姿势分析结果
            
        Returns:
            PoseAnalysisResult: 更新后的姿势分析结果
        """
        # 这里实现仰卧起坐姿势分析逻辑
        
        result.movement_quality = 90  # 示例值
        result.confidence = 0.95
        
        return result
    
    def count_repetitions(self, exercise_record_id: str, 
                         pose_results: List[PoseAnalysisResult]) -> int:
        """
        计算重复次数
        
        Args:
            exercise_record_id: 运动记录ID
            pose_results: 姿势分析结果列表
            
        Returns:
            int: 重复次数
        """
        try:
            # 基于姿势分析结果计算重复次数
            # 这里可以实现基于运动类型的重复计数算法
            
            repetition_count = 0
            last_phase = None
            
            for result in pose_results:
                current_phase = result.repetition_phase
                
                # 检测相位变化来计数
                if last_phase == 'up' and current_phase == 'down':
                    repetition_count += 1
                
                last_phase = current_phase
            
            logger.info(f"Counted {repetition_count} repetitions for exercise record {exercise_record_id}")
            return repetition_count
            
        except Exception as e:
            logger.error(f"Failed to count repetitions for exercise record {exercise_record_id}: {str(e)}")
            return 0
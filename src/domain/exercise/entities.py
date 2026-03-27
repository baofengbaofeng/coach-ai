"""
运动领域实体
"""

from datetime import datetime
from typing import Optional, List, Dict
from domain.base_simple import AggregateRoot
from .value_objects import (
    ExerciseCategory, ExerciseDifficulty, Duration,
    Repetition, Weight, Intensity
)


class ExerciseType(AggregateRoot):
    """运动类型实体"""
    
    def __init__(
        self,
        name_zh: str,
        name_en: str,
        code: str,
        category: ExerciseCategory,
        difficulty: ExerciseDifficulty = None,
        description: Optional[str] = None,
        standard_movement: Optional[str] = None,
        standard_video_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.name_zh = name_zh
        self.name_en = name_en
        self.code = code
        self.category = category
        self.difficulty = difficulty or ExerciseDifficulty("beginner")
        self.description = description
        self.standard_movement = standard_movement
        self.standard_video_url = standard_video_url
        self.tenant_id = tenant_id
        
        # 扩展字段
        self.standard_image_url: Optional[str] = None
        self.target_muscles: List[str] = []
        self.secondary_muscles: List[str] = []
        self.standard_duration: int = 0
        self.standard_repetitions: int = 10
        self.standard_sets: int = 3
        self.rest_between_sets: int = 60
        self.calorie_factor: float = 0.1
        self.is_active: bool = True
        self.requires_equipment: bool = False
        self.equipment_description: Optional[str] = None
        
        self._validate()
    
    def _validate(self):
        if not self.name_zh or len(self.name_zh) < 2:
            raise ValueError("运动类型中文名称长度必须至少2个字符")
        if not self.name_en or len(self.name_en) < 2:
            raise ValueError("运动类型英文名称长度必须至少2个字符")
        if not self.code or len(self.code) < 2:
            raise ValueError("运动类型代码长度必须至少2个字符")
    
    def update_info(
        self,
        name_zh: Optional[str] = None,
        name_en: Optional[str] = None,
        description: Optional[str] = None,
        standard_movement: Optional[str] = None,
        standard_video_url: Optional[str] = None
    ):
        if name_zh is not None:
            self.name_zh = name_zh
        if name_en is not None:
            self.name_en = name_en
        if description is not None:
            self.description = description
        if standard_movement is not None:
            self.standard_movement = standard_movement
        if standard_video_url is not None:
            self.standard_video_url = standard_video_url
        
        self.mark_updated()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name_zh': self.name_zh,
            'name_en': self.name_en,
            'code': self.code,
            'category': str(self.category),
            'difficulty': str(self.difficulty),
            'description': self.description,
            'standard_movement': self.standard_movement,
            'standard_video_url': self.standard_video_url,
            'tenant_id': self.tenant_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class ExerciseRecord(AggregateRoot):
    """运动记录实体"""
    
    def __init__(
        self,
        user_id: str,
        exercise_type_id: str,
        started_at: datetime,
        duration: Optional[Duration] = None,
        repetitions: Optional[Repetition] = None,
        weight: Optional[Weight] = None,
        intensity: Optional[Intensity] = None,
        calories_burned: Optional[float] = None,
        notes: Optional[str] = None,
        completed_at: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.user_id = user_id
        self.exercise_type_id = exercise_type_id
        self.started_at = started_at
        self.duration = duration
        self.repetitions = repetitions
        self.weight = weight
        self.intensity = intensity
        self.calories_burned = calories_burned
        self.notes = notes
        self.completed_at = completed_at
        self.tenant_id = tenant_id
        
        self._validate()
    
    def _validate(self):
        if not self.user_id:
            raise ValueError("用户ID不能为空")
        if not self.exercise_type_id:
            raise ValueError("运动类型ID不能为空")
        if self.completed_at and self.completed_at < self.started_at:
            raise ValueError("完成时间不能早于开始时间")
    
    def complete(
        self,
        completed_at: Optional[datetime] = None,
        duration: Optional[Duration] = None,
        repetitions: Optional[Repetition] = None,
        weight: Optional[Weight] = None,
        intensity: Optional[Intensity] = None,
        calories_burned: Optional[float] = None,
        notes: Optional[str] = None
    ):
        self.completed_at = completed_at or datetime.now()
        
        if duration is not None:
            self.duration = duration
        if repetitions is not None:
            self.repetitions = repetitions
        if weight is not None:
            self.weight = weight
        if intensity is not None:
            self.intensity = intensity
        if calories_burned is not None:
            self.calories_burned = calories_burned
        if notes is not None:
            self.notes = notes
        
        self.mark_updated()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exercise_type_id': self.exercise_type_id,
            'started_at': self.started_at.isoformat(),
            'duration': str(self.duration) if self.duration else None,
            'repetitions': str(self.repetitions) if self.repetitions else None,
            'weight': str(self.weight) if self.weight else None,
            'intensity': str(self.intensity) if self.intensity else None,
            'calories_burned': self.calories_burned,
            'notes': self.notes,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'tenant_id': self.tenant_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class ExercisePlan(AggregateRoot):
    """运动计划实体"""
    
    def __init__(
        self,
        user_id: str,
        plan_name: str,
        description: Optional[str] = None,
        schedule: Optional[Dict] = None,
        is_active: bool = True,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.user_id = user_id
        self.plan_name = plan_name
        self.description = description
        self.schedule = schedule or {}
        self.is_active = is_active
        self.tenant_id = tenant_id
        
        # 计划项
        self.plan_items: List[Dict] = []
        
        self._validate()
    
    def _validate(self):
        if not self.user_id:
            raise ValueError("用户ID不能为空")
        if not self.plan_name or len(self.plan_name) < 2:
            raise ValueError("计划名称长度必须至少2个字符")
    
    def add_plan_item(
        self,
        exercise_type_id: str,
        day_of_week: int,  # 0-6，0表示周日
        order: int,
        sets: int = 3,
        repetitions: Optional[int] = None,
        duration: Optional[int] = None,
        weight: Optional[float] = None
    ):
        """添加计划项"""
        plan_item = {
            'id': len(self.plan_items) + 1,
            'exercise_type_id': exercise_type_id,
            'day_of_week': day_of_week,
            'order': order,
            'sets': sets,
            'repetitions': repetitions,
            'duration': duration,
            'weight': weight,
        }
        
        self.plan_items.append(plan_item)
        self.mark_updated()
    
    def update_plan_item(self, item_id: int, **kwargs):
        """更新计划项"""
        for item in self.plan_items:
            if item['id'] == item_id:
                item.update(kwargs)
                self.mark_updated()
                return True
        return False
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_name': self.plan_name,
            'description': self.description,
            'schedule': self.schedule,
            'is_active': self.is_active,
            'tenant_id': self.tenant_id,
            'plan_items': self.plan_items,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
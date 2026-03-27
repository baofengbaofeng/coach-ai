#!/usr/bin/env python3
"""
快速迁移运动领域
"""

import os
import re
from pathlib import Path

def extract_model_info(file_path):
    """从模型文件中提取信息"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取类名
    class_match = re.search(r'class (\w+)\(BaseModel\):', content)
    if not class_match:
        return None
    
    class_name = class_match.group(1)
    
    # 提取表名
    table_match = re.search(r"__tablename__ = '(\w+)'", content)
    table_name = table_match.group(1) if table_match else class_name.lower() + 's'
    
    # 提取字段
    fields = []
    field_pattern = r'(\w+)\s*=\s*Column\([^)]+\)'
    for match in re.finditer(field_pattern, content):
        field_name = match.group(1)
        if field_name not in ['id', 'created_at', 'updated_at', 'is_deleted']:
            fields.append(field_name)
    
    return {
        'class_name': class_name,
        'table_name': table_name,
        'fields': fields,
        'file_name': os.path.basename(file_path),
        'docstring': extract_docstring(content)
    }

def extract_docstring(content):
    """提取文档字符串"""
    doc_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
    if doc_match:
        return doc_match.group(1).strip()
    return ""

def create_value_objects():
    """创建运动领域值对象"""
    value_objects_code = '''"""
运动领域值对象
包含运动分类、难度、持续时间等不可变的值对象
"""

from domain.base_simple import ValueObject


class ExerciseCategory(ValueObject):
    """运动分类值对象"""
    
    VALID_CATEGORIES = {'strength', 'cardio', 'flexibility', 'balance', 'mixed'}
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_CATEGORIES:
            raise ValueError(f"无效的运动分类: {self.value}")
    
    def is_strength(self) -> bool:
        """是否为力量训练"""
        return self.value == 'strength'
    
    def is_cardio(self) -> bool:
        """是否为有氧运动"""
        return self.value == 'cardio'
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"ExerciseCategory('{self.value}')"


class ExerciseDifficulty(ValueObject):
    """运动难度值对象"""
    
    VALID_DIFFICULTIES = {'beginner', 'intermediate', 'advanced', 'expert'}
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_DIFFICULTIES:
            raise ValueError(f"无效的运动难度: {self.value}")
    
    def is_beginner(self) -> bool:
        """是否为初级"""
        return self.value == 'beginner'
    
    def is_expert(self) -> bool:
        """是否为专家级"""
        return self.value == 'expert'
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"ExerciseDifficulty('{self.value}')"


class Duration(ValueObject):
    """持续时间值对象（秒）"""
    
    def __init__(self, seconds: int):
        if seconds < 0:
            raise ValueError("持续时间不能为负数")
        self.seconds = seconds
    
    @classmethod
    def from_minutes(cls, minutes: float) -> 'Duration':
        """从分钟创建"""
        return cls(int(minutes * 60))
    
    @classmethod
    def from_hours(cls, hours: float) -> 'Duration':
        """从小时创建"""
        return cls(int(hours * 3600))
    
    def to_minutes(self) -> float:
        """转换为分钟"""
        return self.seconds / 60
    
    def to_hours(self) -> float:
        """转换为小时"""
        return self.seconds / 3600
    
    def __str__(self) -> str:
        if self.seconds < 60:
            return f"{self.seconds}秒"
        elif self.seconds < 3600:
            return f"{self.to_minutes():.1f}分钟"
        else:
            return f"{self.to_hours():.1f}小时"
    
    def __repr__(self) -> str:
        return f"Duration({self.seconds}秒)"


class Intensity(ValueObject):
    """运动强度值对象（1-10）"""
    
    def __init__(self, value: int):
        if not 1 <= value <= 10:
            raise ValueError("运动强度必须在1-10之间")
        self.value = value
    
    def is_low(self) -> bool:
        """是否为低强度"""
        return self.value <= 3
    
    def is_medium(self) -> bool:
        """是否为中等强度"""
        return 4 <= self.value <= 7
    
    def is_high(self) -> bool:
        """是否为高强度"""
        return self.value >= 8
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return f"Intensity({self.value})"


class Repetition(ValueObject):
    """重复次数值对象"""
    
    def __init__(self, count: int):
        if count < 0:
            raise ValueError("重复次数不能为负数")
        self.count = count
    
    def __str__(self) -> str:
        return f"{self.count}次"
    
    def __repr__(self) -> str:
        return f"Repetition({self.count})"


class Weight(ValueObject):
    """重量值对象（千克）"""
    
    def __init__(self, kilograms: float):
        if kilograms < 0:
            raise ValueError("重量不能为负数")
        self.kilograms = kilograms
    
    @classmethod
    def from_pounds(cls, pounds: float) -> 'Weight':
        """从磅创建"""
        return cls(pounds * 0.453592)
    
    def to_pounds(self) -> float:
        """转换为磅"""
        return self.kilograms * 2.20462
    
    def __str__(self) -> str:
        return f"{self.kilograms}kg"
    
    def __repr__(self) -> str:
        return f"Weight({self.kilograms}kg)"


class Distance(ValueObject):
    """距离值对象（米）"""
    
    def __init__(self, meters: float):
        if meters < 0:
            raise ValueError("距离不能为负数")
        self.meters = meters
    
    @classmethod
    def from_kilometers(cls, kilometers: float) -> 'Distance':
        """从千米创建"""
        return cls(kilometers * 1000)
    
    @classmethod
    def from_miles(cls, miles: float) -> 'Distance':
        """从英里创建"""
        return cls(miles * 1609.34)
    
    def to_kilometers(self) -> float:
        """转换为千米"""
        return self.meters / 1000
    
    def to_miles(self) -> float:
        """转换为英里"""
        return self.meters / 1609.34
    
    def __str__(self) -> str:
        if self.meters < 1000:
            return f"{self.meters:.0f}米"
        else:
            return f"{self.to_kilometers():.2f}千米"
    
    def __repr__(self) -> str:
        return f"Distance({self.meters}米)"
'''
    
    return value_objects_code

def create_entity_code(model_info):
    """根据模型信息创建实体代码"""
    class_name = model_info['class_name']
    fields = model_info['fields']
    docstring = model_info['docstring'] or f"{class_name}实体"
    
    # 基础字段映射
    field_mapping = {
        'name_zh': ('name_zh', 'str'),
        'name_en': ('name_en', 'str'),
        'code': ('code', 'str'),
        'category': ('category', 'ExerciseCategory'),
        'difficulty': ('difficulty', 'ExerciseDifficulty'),
        'description': ('description', 'str'),
        'standard_movement': ('standard_movement', 'str'),
        'standard_video_url': ('standard_video_url', 'str'),
        'user_id': ('user_id', 'str'),
        'exercise_type_id': ('exercise_type_id', 'str'),
        'started_at': ('started_at', 'datetime'),
        'completed_at': ('completed_at', 'datetime'),
        'duration_seconds': ('duration_seconds', 'Duration'),
        'repetitions': ('repetitions', 'Repetition'),
        'weight_kg': ('weight_kg', 'Weight'),
        'distance_meters': ('distance_meters', 'Distance'),
        'intensity': ('intensity', 'Intensity'),
        'calories_burned': ('calories_burned', 'float'),
        'notes': ('notes', 'str'),
        'plan_name': ('plan_name', 'str'),
        'plan_description': ('plan_description', 'str'),
        'is_active': ('is_active', 'bool'),
        'schedule': ('schedule', 'dict'),
    }
    
    # 生成构造函数参数
    init_params = []
    init_body = []
    field_definitions = []
    
    for field in fields:
        if field in field_mapping:
            param_name, param_type = field_mapping[field]
            init_params.append(f"{param_name}: Optional[{param_type}] = None")
            init_body.append(f"self.{param_name} = {param_name}")
            field_definitions.append(f"self.{param_name}: Optional[{param_type}] = None")
        else:
            # 默认处理为字符串
            init_params.append(f"{field}: Optional[str] = None")
            init_body.append(f"self.{field} = {field}")
            field_definitions.append(f"self.{field}: Optional[str] = None")
    
    init_params_str = ', '.join(init_params)
    init_body_str = '\n        '.join(init_body)
    field_definitions_str = '\n        '.join(field_definitions)
    
    code = f'''"""
{model_info['file_name']} 迁移的实体
{docstring}
"""

from datetime import datetime
from typing import Optional
from domain.base_simple import AggregateRoot


class {class_name}(AggregateRoot):
    """{docstring}"""
    
    def __init__(
        self,
        {init_params_str},
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # 字段定义
        {field_definitions_str}
        
        # 初始化字段
        {init_body_str}
        
        self._validate()
    
    def _validate(self):
        """验证实体数据"""
        # 这里可以添加具体的验证逻辑
        pass
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = {{
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }}
        
        # 添加其他字段
        fields = [{', '.join([f"'{f}'" for f in fields])}]
        for field in fields:
            value = getattr(self, field, None)
            if value is not None:
                if hasattr(value, '__str__'):
                    data[field] = str(value)
                else:
                    data[field] = value
        
        return data
    
    def __repr__(self) -> str:
        return f"<{class_name}(id='{{self.id}}')>"
'''
    
    return code

def main():
    """主函数"""
    project_root = Path(__file__).parent
    coding_dir = project_root / "coding"
    domain_dir = project_root / "src" / "domain" / "exercise"
    
    print("快速迁移运动领域")
    print("=" * 50)
    
    # 运动领域模型文件
    exercise_files = [
        "exercise_type.py",
        "exercise_record.py", 
        "exercise_plan.py"
    ]
    
    # 创建值对象
    print("\n1. 创建值对象...")
    value_objects_path = domain_dir / "value_objects.py"
    value_objects_path.write_text(create_value_objects(), encoding='utf-8')
    print(f"   ✅ 值对象已创建: {value_objects_path}")
    
    # 创建实体
    print("\n2. 创建实体...")
    entities_code = '''"""
运动领域实体
包含运动类型、运动记录、运动计划等核心实体
"""

from datetime import datetime
from typing import Optional, Dict, List
from domain.base_simple import AggregateRoot
from .value_objects import (
    ExerciseCategory, ExerciseDifficulty, Duration,
    Intensity, Repetition, Weight, Distance
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
        
        self._validate()
    
    def _validate(self):
        """验证运动类型数据"""
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
    ) -> None:
        """更新运动类型信息"""
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
    
    def to_dict(self) -> dict:
        """转换为字典"""
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
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<ExerciseType(id='{self.id}', name_zh='{self.name_zh}', code='{self.code}')>"


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
        distance: Optional[Distance] = None,
        intensity: Optional[Intensity] = None,
        calories_burned: Optional[float] = None,
        notes: Optional[str] = None,
        completed_at: Optional[datetime] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.user_id = user_id
        self.exercise_type_id = exercise_type_id
        self.started_at = started_at
        self.duration = duration
        self.repetitions = repetitions
        self.weight = weight
        self.distance = distance
        self.intensity = intensity
        self.calories_burned = calories_burned
        self.notes = notes
        self.completed_at = completed_at
        
        self._validate()
    
    def _validate(self):
        """验证运动记录数据"""
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
        distance: Optional[Distance] = None,
        intensity: Optional[Intensity] = None,
        calories_burned: Optional[float] = None,
        notes: Optional[str] = None
    ) -> None:
        """完成运动记录"""
        self.completed_at = completed_at or datetime.now()
        
        if duration is not None:
            self.duration = duration
        elif not self.duration and self.completed_at:
            # 自动计算持续时间
            duration_seconds = (self.com
"""
运动类型模型
定义不同类型的运动，如俯卧撑、深蹲、仰卧起坐等
"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, Enum, ForeignKey, Index
from sqlalchemy.dialects.mysql import CHAR, VARCHAR
from sqlalchemy.orm import relationship

from .base import BaseModel


class ExerciseType(BaseModel):
    """
    运动类型模型
    定义运动的基本属性和分类
    """
    __tablename__ = 'exercise_types'
    
    # 运动类型名称（中文）
    name_zh = Column(VARCHAR(100), nullable=False, index=True)
    
    # 运动类型名称（英文）
    name_en = Column(VARCHAR(100), nullable=False, index=True)
    
    # 运动类型代码（唯一标识）
    code = Column(VARCHAR(50), unique=True, nullable=False, index=True)
    
    # 运动分类：strength, cardio, flexibility, balance, etc.
    category = Column(
        Enum('strength', 'cardio', 'flexibility', 'balance', 'mixed', name='exercise_category'),
        default='strength',
        nullable=False
    )
    
    # 运动难度级别：beginner, intermediate, advanced, expert
    difficulty = Column(
        Enum('beginner', 'intermediate', 'advanced', 'expert', name='exercise_difficulty'),
        default='beginner',
        nullable=False
    )
    
    # 运动描述
    description = Column(Text, nullable=True)
    
    # 标准动作说明
    standard_movement = Column(Text, nullable=True)
    
    # 标准动作视频URL
    standard_video_url = Column(Text, nullable=True)
    
    # 标准动作图片URL
    standard_image_url = Column(Text, nullable=True)
    
    # 目标肌肉群（JSON格式存储）
    target_muscles = Column(Text, nullable=True)  # JSON: ["chest", "triceps", "shoulders"]
    
    # 辅助肌肉群（JSON格式存储）
    secondary_muscles = Column(Text, nullable=True)
    
    # 标准持续时间（秒，0表示按次数计算）
    standard_duration = Column(Integer, default=0, nullable=False)
    
    # 标准重复次数（0表示按时长计算）
    standard_repetitions = Column(Integer, default=10, nullable=False)
    
    # 标准组数
    standard_sets = Column(Integer, default=3, nullable=False)
    
    # 组间休息时间（秒）
    rest_between_sets = Column(Integer, default=60, nullable=False)
    
    # 卡路里消耗系数（每公斤体重每分钟消耗的卡路里）
    calorie_factor = Column(Float, default=0.1, nullable=False)
    
    # 是否启用
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 是否需要设备
    requires_equipment = Column(Boolean, default=False, nullable=False)
    
    # 设备要求描述
    equipment_description = Column(Text, nullable=True)
    
    # 租户ID（多租户支持）
    tenant_id = Column(CHAR(36), ForeignKey('tenants.id'), nullable=True, index=True)
    
    # 租户关系
    tenant = relationship('Tenant', backref='exercise_types')
    
    # 运动记录关系
    exercise_records = relationship('ExerciseRecord', back_populates='exercise_type')
    
    # 运动计划关系
    exercise_plans = relationship('ExercisePlan', back_populates='exercise_type')
    
    # 索引
    __table_args__ = (
        Index('idx_exercise_type_category', 'category'),
        Index('idx_exercise_type_difficulty', 'difficulty'),
        Index('idx_exercise_type_active', 'is_active'),
        Index('idx_exercise_type_tenant', 'tenant_id'),
        Index('idx_exercise_type_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ExerciseType(id='{self.id}', name_zh='{self.name_zh}', code='{self.code}')>"
    
    def to_dict(self):
        """
        转换为字典，包含额外处理
        """
        data = super().to_dict()
        
        # 处理JSON字段
        import json
        if self.target_muscles:
            try:
                data['target_muscles'] = json.loads(self.target_muscles)
            except:
                data['target_muscles'] = []
        else:
            data['target_muscles'] = []
            
        if self.secondary_muscles:
            try:
                data['secondary_muscles'] = json.loads(self.secondary_muscles)
            except:
                data['secondary_muscles'] = []
        else:
            data['secondary_muscles'] = []
            
        return data
    
    def calculate_calories(self, user_weight_kg, duration_minutes=None, repetitions=None):
        """
        计算卡路里消耗
        
        Args:
            user_weight_kg: 用户体重（公斤）
            duration_minutes: 运动时长（分钟），如果为None则使用标准时长
            repetitions: 重复次数，如果为None则使用标准次数
            
        Returns:
            float: 估算的卡路里消耗
        """
        if self.standard_duration > 0:
            # 按时长计算
            if duration_minutes is None:
                duration_minutes = self.standard_duration / 60
            return self.calorie_factor * user_weight_kg * duration_minutes
        else:
            # 按次数计算
            if repetitions is None:
                repetitions = self.standard_repetitions
            # 假设每次重复消耗基础卡路里
            base_calories_per_rep = 0.05  # 每次重复的基础卡路里
            return base_calories_per_rep * repetitions * (user_weight_kg / 70)  # 以70kg为标准体重
    
    def get_difficulty_multiplier(self):
        """
        获取难度系数
        """
        multipliers = {
            'beginner': 1.0,
            'intermediate': 1.5,
            'advanced': 2.0,
            'expert': 2.5
        }
        return multipliers.get(self.difficulty, 1.0)
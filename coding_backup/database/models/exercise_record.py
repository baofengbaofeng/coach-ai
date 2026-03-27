"""
运动记录模型
记录用户每次的运动数据
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, Enum, ForeignKey, DateTime, Index
from sqlalchemy.dialects.mysql import CHAR, VARCHAR
from sqlalchemy.orm import relationship

from .base import BaseModel


class ExerciseRecord(BaseModel):
    """
    运动记录模型
    记录用户每次的运动数据
    """
    __tablename__ = 'exercise_records'
    
    # 用户ID
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # 运动类型ID
    exercise_type_id = Column(CHAR(36), ForeignKey('exercise_types.id'), nullable=False, index=True)
    
    # 租户ID（多租户支持）
    tenant_id = Column(CHAR(36), ForeignKey('tenants.id'), nullable=True, index=True)
    
    # 运动开始时间
    start_time = Column(DateTime, nullable=False, index=True)
    
    # 运动结束时间
    end_time = Column(DateTime, nullable=False, index=True)
    
    # 运动状态：completed, in_progress, paused, cancelled
    status = Column(
        Enum('completed', 'in_progress', 'paused', 'cancelled', name='exercise_status'),
        default='completed',
        nullable=False
    )
    
    # 运动模式：manual, camera_auto, sensor_auto
    mode = Column(
        Enum('manual', 'camera_auto', 'sensor_auto', name='exercise_mode'),
        default='manual',
        nullable=False
    )
    
    # 总重复次数
    total_repetitions = Column(Integer, default=0, nullable=False)
    
    # 总组数
    total_sets = Column(Integer, default=0, nullable=False)
    
    # 总持续时间（秒）
    total_duration = Column(Integer, default=0, nullable=False)
    
    # 平均心率
    avg_heart_rate = Column(Integer, nullable=True)
    
    # 最大心率
    max_heart_rate = Column(Integer, nullable=True)
    
    # 最小心率
    min_heart_rate = Column(Integer, nullable=True)
    
    # 估算卡路里消耗
    estimated_calories = Column(Float, default=0.0, nullable=False)
    
    # 用户体重（公斤，记录时的体重）
    user_weight_kg = Column(Float, nullable=True)
    
    # 运动质量评分（0-100）
    quality_score = Column(Integer, nullable=True)
    
    # 姿势正确率（0-100）
    posture_accuracy = Column(Integer, nullable=True)
    
    # 完成度评分（0-100）
    completion_score = Column(Integer, nullable=True)
    
    # 疲劳度评分（1-10）
    fatigue_level = Column(Integer, nullable=True)
    
    # 用户主观感受评分（1-10）
    subjective_feeling = Column(Integer, nullable=True)
    
    # 备注
    notes = Column(Text, nullable=True)
    
    # 摄像头设备ID（如果使用摄像头）
    camera_device_id = Column(CHAR(36), ForeignKey('camera_devices.id'), nullable=True, index=True)
    
    # 传感器数据（JSON格式存储原始数据）
    sensor_data = Column(Text, nullable=True)
    
    # 视频分析数据（JSON格式存储分析结果）
    video_analysis_data = Column(Text, nullable=True)
    
    # 是否已验证（管理员或系统验证）
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # 验证者ID
    verified_by = Column(CHAR(36), ForeignKey('users.id'), nullable=True)
    
    # 验证时间
    verified_at = Column(DateTime, nullable=True)
    
    # 验证备注
    verification_notes = Column(Text, nullable=True)
    
    # 关系
    user = relationship('User', foreign_keys=[user_id], backref='exercise_records')
    exercise_type = relationship('ExerciseType', back_populates='exercise_records')
    tenant = relationship('Tenant', backref='exercise_records')
    camera_device = relationship('CameraDevice', backref='exercise_records')
    verifier = relationship('User', foreign_keys=[verified_by])
    
    # 索引
    __table_args__ = (
        Index('idx_exercise_record_user_date', 'user_id', 'start_time'),
        Index('idx_exercise_record_status', 'status'),
        Index('idx_exercise_record_mode', 'mode'),
        Index('idx_exercise_record_verified', 'is_verified'),
        Index('idx_exercise_record_tenant_date', 'tenant_id', 'start_time'),
    )
    
    def __repr__(self):
        return f"<ExerciseRecord(id='{self.id}', user_id='{self.user_id}', exercise_type='{self.exercise_type_id}')>"
    
    @property
    def duration_minutes(self):
        """
        获取运动时长（分钟）
        """
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            return round(duration / 60, 2)
        return 0
    
    @property
    def is_active(self):
        """
        检查是否正在进行中
        """
        return self.status == 'in_progress'
    
    def calculate_duration(self):
        """
        计算持续时间
        """
        if self.start_time and self.end_time:
            self.total_duration = int((self.end_time - self.start_time).total_seconds())
    
    def calculate_calories(self):
        """
        计算卡路里消耗
        """
        if self.exercise_type and self.user_weight_kg:
            if self.exercise_type.standard_duration > 0:
                # 按时长计算
                duration_minutes = self.total_duration / 60
                self.estimated_calories = self.exercise_type.calculate_calories(
                    self.user_weight_kg, duration_minutes
                )
            else:
                # 按次数计算
                self.estimated_calories = self.exercise_type.calculate_calories(
                    self.user_weight_kg, repetitions=self.total_repetitions
                )
    
    def start_exercise(self, user_weight_kg=None):
        """
        开始运动
        """
        self.start_time = datetime.utcnow()
        self.status = 'in_progress'
        if user_weight_kg:
            self.user_weight_kg = user_weight_kg
    
    def pause_exercise(self):
        """
        暂停运动
        """
        if self.status == 'in_progress':
            self.status = 'paused'
    
    def resume_exercise(self):
        """
        恢复运动
        """
        if self.status == 'paused':
            self.status = 'in_progress'
    
    def complete_exercise(self, total_repetitions=0, total_sets=0, notes=None):
        """
        完成运动
        """
        self.end_time = datetime.utcnow()
        self.status = 'completed'
        self.total_repetitions = total_repetitions
        self.total_sets = total_sets
        self.calculate_duration()
        self.calculate_calories()
        
        if notes:
            self.notes = notes
    
    def cancel_exercise(self, reason=None):
        """
        取消运动
        """
        self.end_time = datetime.utcnow()
        self.status = 'cancelled'
        self.calculate_duration()
        
        if reason:
            self.notes = f"Cancelled: {reason}"
    
    def verify_record(self, verifier_id, notes=None):
        """
        验证运动记录
        """
        self.is_verified = True
        self.verified_by = verifier_id
        self.verified_at = datetime.utcnow()
        if notes:
            self.verification_notes = notes
    
    def to_dict(self):
        """
        转换为字典，包含额外处理
        """
        data = super().to_dict()
        
        # 添加计算属性
        data['duration_minutes'] = self.duration_minutes
        
        # 处理JSON字段
        import json
        if self.sensor_data:
            try:
                data['sensor_data'] = json.loads(self.sensor_data)
            except:
                data['sensor_data'] = {}
        else:
            data['sensor_data'] = {}
            
        if self.video_analysis_data:
            try:
                data['video_analysis_data'] = json.loads(self.video_analysis_data)
            except:
                data['video_analysis_data'] = {}
        else:
            data['video_analysis_data'] = {}
            
        return data
    
    def get_summary(self):
        """
        获取运动摘要
        """
        return {
            'id': self.id,
            'exercise_type': self.exercise_type.name_zh if self.exercise_type else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'total_repetitions': self.total_repetitions,
            'total_sets': self.total_sets,
            'estimated_calories': self.estimated_calories,
            'status': self.status,
            'quality_score': self.quality_score
        }
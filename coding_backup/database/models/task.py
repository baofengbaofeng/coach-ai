"""
任务模型
定义不同类型的任务：作业任务、运动任务、自定义任务
"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, Enum, ForeignKey, DateTime, JSON, Index
from sqlalchemy.dialects.mysql import CHAR, VARCHAR
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel


class Task(BaseModel):
    """
    任务模型
    定义任务的基本属性和分类
    """
    __tablename__ = 'tasks'
    
    # 任务标题
    title = Column(VARCHAR(200), nullable=False, index=True)
    
    # 任务描述
    description = Column(Text, nullable=True)
    
    # 任务类型：homework, exercise, custom
    task_type = Column(
        Enum('homework', 'exercise', 'custom', name='task_type'),
        default='homework',
        nullable=False,
        index=True
    )
    
    # 任务状态：draft, active, completed, cancelled, archived
    status = Column(
        Enum('draft', 'active', 'completed', 'cancelled', 'archived', name='task_status'),
        default='draft',
        nullable=False,
        index=True
    )
    
    # 任务优先级：low, medium, high, urgent
    priority = Column(
        Enum('low', 'medium', 'high', 'urgent', name='task_priority'),
        default='medium',
        nullable=False,
        index=True
    )
    
    # 任务难度级别：beginner, intermediate, advanced, expert
    difficulty = Column(
        Enum('beginner', 'intermediate', 'advanced', 'expert', name='task_difficulty'),
        default='beginner',
        nullable=False
    )
    
    # 任务标签（JSON数组）
    tags = Column(JSON, nullable=True, default=list)
    
    # 任务内容（JSON格式，根据任务类型不同而不同）
    content = Column(JSON, nullable=True)
    
    # 任务元数据（JSON格式，存储额外信息）
    task_metadata = Column('metadata', JSON, nullable=True)
    
    # 任务开始时间
    start_time = Column(DateTime, nullable=True, index=True)
    
    # 任务截止时间
    deadline = Column(DateTime, nullable=True, index=True)
    
    # 预计完成时间（分钟）
    estimated_duration = Column(Integer, nullable=True)
    
    # 实际完成时间（分钟）
    actual_duration = Column(Integer, nullable=True)
    
    # 任务依赖关系（JSON数组，存储依赖的任务ID）
    dependencies = Column(JSON, nullable=True, default=list)
    
    # 任务前置条件
    prerequisites = Column(Text, nullable=True)
    
    # 任务完成条件
    completion_criteria = Column(Text, nullable=True)
    
    # 任务评分标准
    scoring_criteria = Column(Text, nullable=True)
    
    # 任务附件（JSON数组，存储附件信息）
    attachments = Column(JSON, nullable=True, default=list)
    
    # 创建者ID
    creator_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # 租户ID
    tenant_id = Column(CHAR(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # 关联的运动类型ID（如果是运动任务）
    exercise_type_id = Column(CHAR(36), ForeignKey('exercise_types.id'), nullable=True, index=True)
    
    # 关联关系
    creator = relationship('User', backref='created_tasks')
    tenant = relationship('Tenant', backref='tasks')
    exercise_type = relationship('ExerciseType', backref='tasks')
    
    # 索引
    __table_args__ = (
        Index('idx_tasks_tenant_status', 'tenant_id', 'status'),
        Index('idx_tasks_tenant_priority', 'tenant_id', 'priority'),
        Index('idx_tasks_tenant_deadline', 'tenant_id', 'deadline'),
        Index('idx_tasks_creator_status', 'creator_id', 'status'),
    )
    
    def to_dict(self, include_relations=False):
        """
        转换为字典格式
        
        Args:
            include_relations: 是否包含关联对象
            
        Returns:
            dict: 任务字典
        """
        result = super().to_dict()
        
        # 格式化时间字段
        if self.start_time:
            result['start_time'] = self.start_time.isoformat()
        if self.deadline:
            result['deadline'] = self.deadline.isoformat()
        
        if include_relations:
            if self.creator:
                result['creator'] = self.creator.to_dict()
            if self.tenant:
                result['tenant'] = self.tenant.to_dict()
            if self.exercise_type:
                result['exercise_type'] = self.exercise_type.to_dict()
        
        return result
    
    def is_overdue(self):
        """
        检查任务是否过期
        
        Returns:
            bool: 是否过期
        """
        if not self.deadline:
            return False
        return datetime.utcnow() > self.deadline
    
    def get_progress(self):
        """
        获取任务进度
        
        Returns:
            float: 进度百分比（0-100）
        """
        # 这里需要根据任务分配和提交情况计算进度
        # 暂时返回0，后续在服务层实现
        return 0.0
    
    def can_be_assigned(self):
        """
        检查任务是否可以分配
        
        Returns:
            bool: 是否可以分配
        """
        return self.status in ['draft', 'active']
    
    def can_be_submitted(self):
        """
        检查任务是否可以提交
        
        Returns:
            bool: 是否可以提交
        """
        return self.status == 'active'
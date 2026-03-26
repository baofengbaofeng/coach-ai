"""
任务分配模型
定义任务分配给学员的关系和进度跟踪
"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, Enum, ForeignKey, DateTime, JSON, Index
from sqlalchemy.dialects.mysql import CHAR, VARCHAR
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel


class TaskAssignment(BaseModel):
    """
    任务分配模型
    记录任务分配给学员的情况和进度
    """
    __tablename__ = 'task_assignments'
    
    # 任务ID
    task_id = Column(CHAR(36), ForeignKey('tasks.id'), nullable=False, index=True)
    
    # 学员ID
    student_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # 分配者ID（教练或管理员）
    assigner_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # 分配状态：assigned, in_progress, completed, cancelled, overdue
    status = Column(
        Enum('assigned', 'in_progress', 'completed', 'cancelled', 'overdue', name='assignment_status'),
        default='assigned',
        nullable=False,
        index=True
    )
    
    # 进度百分比（0-100）
    progress = Column(Float, default=0.0, nullable=False)
    
    # 分配时间
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 开始时间
    started_at = Column(DateTime, nullable=True)
    
    # 完成时间
    completed_at = Column(DateTime, nullable=True)
    
    # 预计完成时间
    expected_completion_at = Column(DateTime, nullable=True)
    
    # 实际完成时间
    actual_completion_at = Column(DateTime, nullable=True)
    
    # 分配备注
    assignment_notes = Column(Text, nullable=True)
    
    # 学员备注
    student_notes = Column(Text, nullable=True)
    
    # 进度详情（JSON格式，存储详细的进度信息）
    progress_details = Column(JSON, nullable=True)
    
    # 提醒设置（JSON格式，存储提醒规则）
    reminder_settings = Column(JSON, nullable=True)
    
    # 最后提醒时间
    last_reminded_at = Column(DateTime, nullable=True)
    
    # 自动分配标记
    is_auto_assigned = Column(Boolean, default=False, nullable=False)
    
    # 分配优先级（用于智能调度）
    assignment_priority = Column(Integer, default=0, nullable=False)
    
    # 租户ID
    tenant_id = Column(CHAR(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # 关联关系
    task = relationship('Task', backref='assignments')
    student = relationship('User', foreign_keys=[student_id], backref='assigned_tasks')
    assigner = relationship('User', foreign_keys=[assigner_id], backref='assigned_tasks_by_me')
    tenant = relationship('Tenant', backref='task_assignments')
    
    # 索引
    __table_args__ = (
        Index('idx_task_assignments_task_student', 'task_id', 'student_id', unique=True),
        Index('idx_task_assignments_student_status', 'student_id', 'status'),
        Index('idx_task_assignments_tenant_status', 'tenant_id', 'status'),
        Index('idx_task_assignments_deadline', 'expected_completion_at'),
        Index('idx_task_assignments_progress', 'progress'),
    )
    
    def to_dict(self, include_relations=False):
        """
        转换为字典格式
        
        Args:
            include_relations: 是否包含关联对象
            
        Returns:
            dict: 任务分配字典
        """
        result = super().to_dict()
        
        # 格式化时间字段
        if self.assigned_at:
            result['assigned_at'] = self.assigned_at.isoformat()
        if self.started_at:
            result['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            result['completed_at'] = self.completed_at.isoformat()
        if self.expected_completion_at:
            result['expected_completion_at'] = self.expected_completion_at.isoformat()
        if self.actual_completion_at:
            result['actual_completion_at'] = self.actual_completion_at.isoformat()
        if self.last_reminded_at:
            result['last_reminded_at'] = self.last_reminded_at.isoformat()
        
        if include_relations:
            if self.task:
                result['task'] = self.task.to_dict()
            if self.student:
                result['student'] = self.student.to_dict()
            if self.assigner:
                result['assigner'] = self.assigner.to_dict()
            if self.tenant:
                result['tenant'] = self.tenant.to_dict()
        
        return result
    
    def update_progress(self, new_progress, details=None):
        """
        更新进度
        
        Args:
            new_progress: 新的进度值（0-100）
            details: 进度详情
            
        Returns:
            bool: 是否成功更新
        """
        if new_progress < 0 or new_progress > 100:
            return False
        
        self.progress = new_progress
        
        # 更新状态
        if new_progress >= 100:
            self.status = 'completed'
            self.completed_at = datetime.utcnow()
        elif new_progress > 0:
            self.status = 'in_progress'
            if not self.started_at:
                self.started_at = datetime.utcnow()
        
        # 更新进度详情
        if details:
            if not self.progress_details:
                self.progress_details = []
            self.progress_details.append({
                'timestamp': datetime.utcnow().isoformat(),
                'progress': new_progress,
                'details': details
            })
        
        return True
    
    def is_overdue(self):
        """
        检查分配是否过期
        
        Returns:
            bool: 是否过期
        """
        if not self.expected_completion_at:
            return False
        
        if self.status in ['completed', 'cancelled']:
            return False
        
        return datetime.utcnow() > self.expected_completion_at
    
    def get_time_remaining(self):
        """
        获取剩余时间（秒）
        
        Returns:
            int: 剩余秒数，None表示无截止时间
        """
        if not self.expected_completion_at:
            return None
        
        remaining = self.expected_completion_at - datetime.utcnow()
        return max(0, int(remaining.total_seconds()))
    
    def should_remind(self, reminder_hours_before=24):
        """
        检查是否需要提醒
        
        Args:
            reminder_hours_before: 提前多少小时提醒
            
        Returns:
            bool: 是否需要提醒
        """
        if self.status in ['completed', 'cancelled']:
            return False
        
        if not self.expected_completion_at:
            return False
        
        # 检查是否已经提醒过
        if self.last_reminded_at:
            # 如果最近24小时内已经提醒过，不再提醒
            time_since_last_reminder = datetime.utcnow() - self.last_reminded_at
            if time_since_last_reminder.total_seconds() < 24 * 3600:
                return False
        
        # 检查是否接近截止时间
        time_remaining = self.get_time_remaining()
        if time_remaining is None:
            return False
        
        reminder_seconds = reminder_hours_before * 3600
        return time_remaining <= reminder_seconds
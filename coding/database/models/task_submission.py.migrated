"""
任务提交模型
定义学员提交任务成果的记录
"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, Enum, ForeignKey, DateTime, JSON, Index
from sqlalchemy.dialects.mysql import CHAR, VARCHAR
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel


class TaskSubmission(BaseModel):
    """
    任务提交模型
    记录学员提交的任务成果
    """
    __tablename__ = 'task_submissions'
    
    # 任务分配ID
    assignment_id = Column(CHAR(36), ForeignKey('task_assignments.id'), nullable=False, index=True)
    
    # 提交者ID（学员）
    submitter_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # 提交状态：submitted, reviewed, returned, accepted, rejected
    status = Column(
        Enum('submitted', 'reviewed', 'returned', 'accepted', 'rejected', name='submission_status'),
        default='submitted',
        nullable=False,
        index=True
    )
    
    # 提交内容（JSON格式，存储提交的具体内容）
    content = Column(JSON, nullable=False)
    
    # 提交备注
    submission_notes = Column(Text, nullable=True)
    
    # 提交时间
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 审核时间
    reviewed_at = Column(DateTime, nullable=True)
    
    # 审核者ID
    reviewer_id = Column(CHAR(36), ForeignKey('users.id'), nullable=True, index=True)
    
    # 审核备注
    review_notes = Column(Text, nullable=True)
    
    # 附件列表（JSON数组，存储附件信息）
    attachments = Column(JSON, nullable=True, default=list)
    
    # 版本号（用于多次提交）
    version = Column(Integer, default=1, nullable=False)
    
    # 是否为最终提交
    is_final = Column(Boolean, default=False, nullable=False)
    
    # 提交IP地址
    ip_address = Column(VARCHAR(45), nullable=True)
    
    # 用户代理
    user_agent = Column(Text, nullable=True)
    
    # 提交设备信息
    device_info = Column(JSON, nullable=True)
    
    # 租户ID
    tenant_id = Column(CHAR(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # 关联关系
    assignment = relationship('TaskAssignment', backref='submissions')
    submitter = relationship('User', foreign_keys=[submitter_id], backref='task_submissions')
    reviewer = relationship('User', foreign_keys=[reviewer_id], backref='reviewed_submissions')
    tenant = relationship('Tenant', backref='task_submissions')
    
    # 索引
    __table_args__ = (
        Index('idx_task_submissions_assignment_version', 'assignment_id', 'version'),
        Index('idx_task_submissions_submitter_status', 'submitter_id', 'status'),
        Index('idx_task_submissions_tenant_status', 'tenant_id', 'status'),
        Index('idx_task_submissions_submitted_at', 'submitted_at'),
    )
    
    def to_dict(self, include_relations=False):
        """
        转换为字典格式
        
        Args:
            include_relations: 是否包含关联对象
            
        Returns:
            dict: 任务提交字典
        """
        result = super().to_dict()
        
        # 格式化时间字段
        if self.submitted_at:
            result['submitted_at'] = self.submitted_at.isoformat()
        if self.reviewed_at:
            result['reviewed_at'] = self.reviewed_at.isoformat()
        
        if include_relations:
            if self.assignment:
                result['assignment'] = self.assignment.to_dict()
            if self.submitter:
                result['submitter'] = self.submitter.to_dict()
            if self.reviewer:
                result['reviewer'] = self.reviewer.to_dict()
            if self.tenant:
                result['tenant'] = self.tenant.to_dict()
        
        return result
    
    def review(self, reviewer_id, status, notes=None):
        """
        审核提交
        
        Args:
            reviewer_id: 审核者ID
            status: 审核状态
            notes: 审核备注
            
        Returns:
            bool: 是否成功审核
        """
        if status not in ['reviewed', 'returned', 'accepted', 'rejected']:
            return False
        
        self.status = status
        self.reviewer_id = reviewer_id
        self.reviewed_at = datetime.utcnow()
        
        if notes:
            self.review_notes = notes
        
        # 如果是最终状态，更新任务分配
        if status in ['accepted', 'rejected'] and self.assignment:
            if status == 'accepted':
                self.assignment.update_progress(100, {'submission_accepted': True})
            elif status == 'rejected':
                self.assignment.update_progress(50, {'submission_rejected': True})
        
        return True
    
    def get_content_summary(self):
        """
        获取提交内容摘要
        
        Returns:
            str: 内容摘要
        """
        if not self.content:
            return "无内容"
        
        # 根据内容类型生成摘要
        content_type = self.content.get('type', 'unknown')
        
        if content_type == 'text':
            text = self.content.get('text', '')
            return text[:100] + ('...' if len(text) > 100 else '')
        elif content_type == 'exercise':
            exercise_type = self.content.get('exercise_type', '未知')
            count = self.content.get('count', 0)
            return f"运动任务：{exercise_type}，完成{count}次"
        elif content_type == 'file':
            files = self.content.get('files', [])
            return f"文件提交：{len(files)}个文件"
        else:
            return f"{content_type}类型提交"
    
    def can_be_reviewed(self):
        """
        检查提交是否可以审核
        
        Returns:
            bool: 是否可以审核
        """
        return self.status == 'submitted'
    
    def can_be_resubmitted(self):
        """
        检查提交是否可以重新提交
        
        Returns:
            bool: 是否可以重新提交
        """
        return self.status in ['returned', 'rejected']
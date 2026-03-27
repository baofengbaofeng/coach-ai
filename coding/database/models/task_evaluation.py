"""
任务评价模型
定义任务完成后的评分、评语和反馈
"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, Enum, ForeignKey, DateTime, JSON, Index
from sqlalchemy.dialects.mysql import CHAR, VARCHAR
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel


class TaskEvaluation(BaseModel):
    """
    任务评价模型
    记录任务完成后的评分和反馈
    """
    __tablename__ = 'task_evaluations'
    
    # 任务分配ID
    assignment_id = Column(CHAR(36), ForeignKey('task_assignments.id'), nullable=False, index=True)
    
    # 任务提交ID（可选，如果有提交的话）
    submission_id = Column(CHAR(36), ForeignKey('task_submissions.id'), nullable=True, index=True)
    
    # 评价者ID（教练或管理员）
    evaluator_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # 被评价者ID（学员）
    student_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # 总体评分（0-100）
    overall_score = Column(Float, nullable=False)
    
    # 评分详情（JSON格式，存储各项评分）
    score_details = Column(JSON, nullable=True)
    
    # 评语
    comments = Column(Text, nullable=True)
    
    # 评价时间
    evaluated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 评价状态：draft, published, archived
    status = Column(
        Enum('draft', 'published', 'archived', name='evaluation_status'),
        default='draft',
        nullable=False,
        index=True
    )
    
    # 评价维度（JSON格式，存储评价维度定义）
    evaluation_dimensions = Column(JSON, nullable=True)
    
    # 改进建议
    improvement_suggestions = Column(Text, nullable=True)
    
    # 优点
    strengths = Column(Text, nullable=True)
    
    # 待改进点
    areas_for_improvement = Column(Text, nullable=True)
    
    # 下次目标
    next_goals = Column(Text, nullable=True)
    
    # 是否推荐进阶
    recommended_for_advancement = Column(Boolean, default=False, nullable=False)
    
    # 推荐的下个任务ID
    recommended_next_task_id = Column(CHAR(36), ForeignKey('tasks.id'), nullable=True, index=True)
    
    # 评价模板ID
    evaluation_template_id = Column(CHAR(36), nullable=True, index=True)
    
    # 租户ID
    tenant_id = Column(CHAR(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # 关联关系
    assignment = relationship('TaskAssignment', backref='evaluations')
    submission = relationship('TaskSubmission', backref='evaluation')
    evaluator = relationship('User', foreign_keys=[evaluator_id], backref='given_evaluations')
    student = relationship('User', foreign_keys=[student_id], backref='received_evaluations')
    recommended_next_task = relationship('Task', foreign_keys=[recommended_next_task_id], backref='recommended_from_evaluations')
    tenant = relationship('Tenant', backref='task_evaluations')
    
    # 索引
    __table_args__ = (
        Index('idx_task_evaluations_assignment_evaluator', 'assignment_id', 'evaluator_id', unique=True),
        Index('idx_task_evaluations_student_score', 'student_id', 'overall_score'),
        Index('idx_task_evaluations_tenant_status', 'tenant_id', 'status'),
        Index('idx_task_evaluations_evaluated_at', 'evaluated_at'),
    )
    
    def to_dict(self, include_relations=False):
        """
        转换为字典格式
        
        Args:
            include_relations: 是否包含关联对象
            
        Returns:
            dict: 任务评价字典
        """
        result = super().to_dict()
        
        # 格式化时间字段
        if self.evaluated_at:
            result['evaluated_at'] = self.evaluated_at.isoformat()
        
        # 计算评分等级
        result['score_grade'] = self.get_score_grade()
        
        if include_relations:
            if self.assignment:
                result['assignment'] = self.assignment.to_dict()
            if self.submission:
                result['submission'] = self.submission.to_dict()
            if self.evaluator:
                result['evaluator'] = self.evaluator.to_dict()
            if self.student:
                result['student'] = self.student.to_dict()
            if self.recommended_next_task:
                result['recommended_next_task'] = self.recommended_next_task.to_dict()
            if self.tenant:
                result['tenant'] = self.tenant.to_dict()
        
        return result
    
    def get_score_grade(self):
        """
        根据评分获取等级
        
        Returns:
            str: 评分等级
        """
        score = self.overall_score
        
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'A-'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'B-'
        elif score >= 60:
            return 'C+'
        elif score >= 55:
            return 'C'
        elif score >= 50:
            return 'C-'
        elif score >= 40:
            return 'D'
        else:
            return 'F'
    
    def get_score_details_summary(self):
        """
        获取评分详情摘要
        
        Returns:
            dict: 评分摘要
        """
        if not self.score_details:
            return {}
        
        summary = {
            'dimensions': len(self.score_details),
            'average': self.overall_score,
            'max_score': 0,
            'min_score': 100,
            'dimension_scores': {}
        }
        
        for dimension, score in self.score_details.items():
            if isinstance(score, (int, float)):
                summary['dimension_scores'][dimension] = score
                summary['max_score'] = max(summary['max_score'], score)
                summary['min_score'] = min(summary['min_score'], score)
        
        return summary
    
    def publish(self):
        """
        发布评价
        
        Returns:
            bool: 是否成功发布
        """
        if self.status != 'draft':
            return False
        
        self.status = 'published'
        return True
    
    def archive(self):
        """
        归档评价
        
        Returns:
            bool: 是否成功归档
        """
        self.status = 'archived'
        return True
    
    def update_score_details(self, dimension_scores):
        """
        更新评分详情并重新计算总体评分
        
        Args:
            dimension_scores: 维度评分字典
            
        Returns:
            bool: 是否成功更新
        """
        if not dimension_scores:
            return False
        
        self.score_details = dimension_scores
        
        # 计算平均分
        scores = [score for score in dimension_scores.values() if isinstance(score, (int, float))]
        if scores:
            self.overall_score = sum(scores) / len(scores)
        
        return True
    
    def get_evaluation_report(self):
        """
        获取评价报告
        
        Returns:
            dict: 评价报告
        """
        return {
            'evaluation_id': self.id,
            'student_id': self.student_id,
            'evaluator_id': self.evaluator_id,
            'overall_score': self.overall_score,
            'score_grade': self.get_score_grade(),
            'comments': self.comments,
            'strengths': self.strengths,
            'areas_for_improvement': self.areas_for_improvement,
            'improvement_suggestions': self.improvement_suggestions,
            'next_goals': self.next_goals,
            'recommended_for_advancement': self.recommended_for_advancement,
            'evaluated_at': self.evaluated_at.isoformat() if self.evaluated_at else None,
            'score_details': self.get_score_details_summary()
        }
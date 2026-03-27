"""
运动计划模型
定义用户的运动计划，包括每日、每周计划
"""

from datetime import datetime, time
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, Enum, ForeignKey, Time, Date, Index
from sqlalchemy.dialects.mysql import CHAR, VARCHAR
from sqlalchemy.orm import relationship

from .base import BaseModel


class ExercisePlan(BaseModel):
    """
    运动计划模型
    定义用户的运动计划
    """
    __tablename__ = 'exercise_plans'
    
    # 用户ID
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # 运动类型ID
    exercise_type_id = Column(CHAR(36), ForeignKey('exercise_types.id'), nullable=False, index=True)
    
    # 租户ID（多租户支持）
    tenant_id = Column(CHAR(36), ForeignKey('tenants.id'), nullable=True, index=True)
    
    # 计划名称
    plan_name = Column(VARCHAR(200), nullable=False)
    
    # 计划描述
    description = Column(Text, nullable=True)
    
    # 计划类型：daily, weekly, custom
    plan_type = Column(
        Enum('daily', 'weekly', 'custom', name='plan_type'),
        default='daily',
        nullable=False
    )
    
    # 计划状态：active, paused, completed, cancelled
    status = Column(
        Enum('active', 'paused', 'completed', 'cancelled', name='plan_status'),
        default='active',
        nullable=False
    )
    
    # 开始日期
    start_date = Column(Date, nullable=False, index=True)
    
    # 结束日期
    end_date = Column(Date, nullable=True, index=True)
    
    # 目标重复次数
    target_repetitions = Column(Integer, default=0, nullable=False)
    
    # 目标组数
    target_sets = Column(Integer, default=0, nullable=False)
    
    # 目标持续时间（秒）
    target_duration = Column(Integer, default=0, nullable=False)
    
    # 每周频率（每周几次）
    weekly_frequency = Column(Integer, default=7, nullable=False)
    
    # 每周的哪几天（JSON格式，[1,3,5]表示周一、三、五）
    weekly_days = Column(Text, nullable=True)  # JSON: [1, 3, 5] where 1=Monday, 7=Sunday
    
    # 每日计划时间
    daily_time = Column(Time, nullable=True)
    
    # 优先级（1-10，10为最高）
    priority = Column(Integer, default=5, nullable=False)
    
    # 是否提醒
    enable_reminder = Column(Boolean, default=True, nullable=False)
    
    # 提醒时间（提前分钟数）
    reminder_minutes_before = Column(Integer, default=15, nullable=False)
    
    # 完成奖励积分
    reward_points = Column(Integer, default=10, nullable=False)
    
    # 进度（0-100）
    progress = Column(Integer, default=0, nullable=False)
    
    # 已完成次数
    completed_count = Column(Integer, default=0, nullable=False)
    
    # 失败次数
    failed_count = Column(Integer, default=0, nullable=False)
    
    # 最后完成时间
    last_completed_at = Column(Date, nullable=True)
    
    # 连续完成天数
    streak_days = Column(Integer, default=0, nullable=False)
    
    # 最长连续完成天数
    max_streak_days = Column(Integer, default=0, nullable=False)
    
    # 自定义规则（JSON格式）
    custom_rules = Column(Text, nullable=True)
    
    # 备注
    notes = Column(Text, nullable=True)
    
    # 关系
    user = relationship('User', backref='exercise_plans')
    exercise_type = relationship('ExerciseType', back_populates='exercise_plans')
    tenant = relationship('Tenant', backref='exercise_plans')
    
    # 索引
    __table_args__ = (
        Index('idx_exercise_plan_user_status', 'user_id', 'status'),
        Index('idx_exercise_plan_type', 'plan_type'),
        Index('idx_exercise_plan_dates', 'start_date', 'end_date'),
        Index('idx_exercise_plan_priority', 'priority'),
        Index('idx_exercise_plan_tenant', 'tenant_id'),
    )
    
    def __repr__(self):
        return f"<ExercisePlan(id='{self.id}', plan_name='{self.plan_name}', user_id='{self.user_id}')>"
    
    @property
    def is_active(self):
        """
        检查计划是否活跃
        """
        today = datetime.utcnow().date()
        if self.status != 'active':
            return False
        if self.start_date and today < self.start_date:
            return False
        if self.end_date and today > self.end_date:
            return False
        return True
    
    @property
    def is_due_today(self):
        """
        检查今天是否需要执行
        """
        if not self.is_active:
            return False
        
        today = datetime.utcnow().date()
        
        # 检查是否今天已经完成
        if self.last_completed_at == today:
            return False
        
        # 根据计划类型检查
        if self.plan_type == 'daily':
            return True
        elif self.plan_type == 'weekly':
            if not self.weekly_days:
                return False
            import json
            try:
                days = json.loads(self.weekly_days)
                # Python的weekday(): Monday=0, Sunday=6
                # 我们的系统: Monday=1, Sunday=7
                current_day = datetime.utcnow().weekday() + 1
                return current_day in days
            except:
                return False
        elif self.plan_type == 'custom':
            # 自定义规则需要解析custom_rules
            return self._check_custom_rules()
        
        return False
    
    @property
    def next_due_date(self):
        """
        获取下一个到期日期
        """
        if not self.is_active:
            return None
        
        today = datetime.utcnow().date()
        
        if self.plan_type == 'daily':
            return today
        elif self.plan_type == 'weekly':
            if not self.weekly_days:
                return None
            import json
            try:
                days = json.loads(self.weekly_days)
                current_day = datetime.utcnow().weekday() + 1
                
                # 找到下一个计划日
                for i in range(1, 8):
                    next_day = (current_day + i - 1) % 7 + 1
                    if next_day in days:
                        from datetime import timedelta
                        return today + timedelta(days=i)
            except:
                return None
        
        return today
    
    def _check_custom_rules(self):
        """
        检查自定义规则
        """
        if not self.custom_rules:
            return False
        
        import json
        try:
            rules = json.loads(self.custom_rules)
            # 这里可以实现复杂的规则检查逻辑
            # 例如：{"type": "alternate_days", "last_completed": "2024-01-01"}
            return True
        except:
            return False
    
    def mark_completed(self, actual_repetitions=None, actual_sets=None, actual_duration=None):
        """
        标记为已完成
        """
        today = datetime.utcnow().date()
        
        # 更新进度
        self.completed_count += 1
        self.last_completed_at = today
        
        # 更新连续天数
        if self.last_completed_at == today:
            yesterday = today - datetime.timedelta(days=1)
            if self.last_completed_at == yesterday:
                self.streak_days += 1
            else:
                self.streak_days = 1
            
            # 更新最长连续天数
            if self.streak_days > self.max_streak_days:
                self.max_streak_days = self.streak_days
        
        # 计算进度（基于完成次数）
        if self.end_date:
            total_days = (self.end_date - self.start_date).days + 1
            elapsed_days = (today - self.start_date).days + 1
            self.progress = min(100, int((self.completed_count / elapsed_days) * 100))
        else:
            # 无限期计划，基于周频率
            expected_count = (datetime.utcnow() - self.created_at).days * self.weekly_frequency / 7
            if expected_count > 0:
                self.progress = min(100, int((self.completed_count / expected_count) * 100))
    
    def mark_failed(self, reason=None):
        """
        标记为失败
        """
        self.failed_count += 1
        self.streak_days = 0
        
        if reason and self.notes:
            self.notes += f"\nFailed on {datetime.utcnow().date()}: {reason}"
        elif reason:
            self.notes = f"Failed on {datetime.utcnow().date()}: {reason}"
    
    def pause_plan(self):
        """
        暂停计划
        """
        self.status = 'paused'
    
    def resume_plan(self):
        """
        恢复计划
        """
        if self.status == 'paused':
            self.status = 'active'
    
    def complete_plan(self):
        """
        完成计划
        """
        self.status = 'completed'
        self.progress = 100
        self.end_date = datetime.utcnow().date()
    
    def cancel_plan(self, reason=None):
        """
        取消计划
        """
        self.status = 'cancelled'
        if reason:
            self.notes = f"Cancelled: {reason}"
    
    def get_today_target(self):
        """
        获取今日目标
        """
        if self.target_duration > 0:
            return {
                'type': 'duration',
                'value': self.target_duration,
                'unit': 'seconds'
            }
        elif self.target_repetitions > 0:
            return {
                'type': 'repetitions',
                'value': self.target_repetitions,
                'unit': 'times'
            }
        else:
            return {
                'type': 'sets',
                'value': self.target_sets,
                'unit': 'sets'
            }
    
    def to_dict(self):
        """
        转换为字典，包含额外处理
        """
        data = super().to_dict()
        
        # 添加计算属性
        data['is_active'] = self.is_active
        data['is_due_today'] = self.is_due_today
        data['next_due_date'] = self.next_due_date.isoformat() if self.next_due_date else None
        
        # 处理JSON字段
        import json
        if self.weekly_days:
            try:
                data['weekly_days'] = json.loads(self.weekly_days)
            except:
                data['weekly_days'] = []
        else:
            data['weekly_days'] = []
            
        if self.custom_rules:
            try:
                data['custom_rules'] = json.loads(self.custom_rules)
            except:
                data['custom_rules'] = {}
        else:
            data['custom_rules'] = {}
            
        # 处理时间字段
        if self.daily_time:
            data['daily_time'] = self.daily_time.strftime('%H:%M:%S')
            
        return data
    
    def get_progress_summary(self):
        """
        获取进度摘要
        """
        return {
            'plan_name': self.plan_name,
            'progress': self.progress,
            'completed_count': self.completed_count,
            'failed_count': self.failed_count,
            'streak_days': self.streak_days,
            'max_streak_days': self.max_streak_days,
            'is_due_today': self.is_due_today,
            'next_due_date': self.next_due_date.isoformat() if self.next_due_date else None
        }
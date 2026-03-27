"""
成就领域值对象
"""

from domain.base_simple import ValueObject


class AchievementType(ValueObject):
    """成就类型值对象"""
    
    VALID_TYPES = {'exercise', 'task', 'streak', 'milestone', 'special', 'collection'}
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_TYPES:
            raise ValueError(f"无效的成就类型: {self.value}")
    
    def is_exercise(self) -> bool:
        """是否为运动成就"""
        return self.value == 'exercise'
    
    def is_task(self) -> bool:
        """是否为任务成就"""
        return self.value == 'task'
    
    def is_streak(self) -> bool:
        """是否为连续成就"""
        return self.value == 'streak'
    
    def __str__(self) -> str:
        return self.value


class AchievementDifficulty(ValueObject):
    """成就难度值对象"""
    
    VALID_DIFFICULTIES = {'easy', 'medium', 'hard', 'legendary'}
    DIFFICULTY_LEVELS = {'easy': 1, 'medium': 2, 'hard': 3, 'legendary': 4}
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_DIFFICULTIES:
            raise ValueError(f"无效的成就难度: {self.value}")
    
    def level(self) -> int:
        """获取难度级别"""
        return self.DIFFICULTY_LEVELS[self.value]
    
    def is_easy(self) -> bool:
        """是否为简单难度"""
        return self.value == 'easy'
    
    def is_legendary(self) -> bool:
        """是否为传奇难度"""
        return self.value == 'legendary'
    
    def __str__(self) -> str:
        return self.value


class AchievementStatus(ValueObject):
    """成就状态值对象"""
    
    VALID_STATUSES = {'active', 'inactive', 'archived'}
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_STATUSES:
            raise ValueError(f"无效的成就状态: {self.value}")
    
    def is_active(self) -> bool:
        """是否为活跃状态"""
        return self.value == 'active'
    
    def is_archived(self) -> bool:
        """是否为归档状态"""
        return self.value == 'archived'
    
    def __str__(self) -> str:
        return self.value


class BadgeType(ValueObject):
    """徽章类型值对象"""
    
    VALID_TYPES = {'achievement', 'participation', 'special', 'seasonal', 'event'}
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_TYPES:
            raise ValueError(f"无效的徽章类型: {self.value}")
    
    def is_achievement(self) -> bool:
        """是否为成就徽章"""
        return self.value == 'achievement'
    
    def is_seasonal(self) -> bool:
        """是否为季节徽章"""
        return self.value == 'seasonal'
    
    def __str__(self) -> str:
        return self.value


class BadgeRarity(ValueObject):
    """徽章稀有度值对象"""
    
    VALID_RARITIES = {'common', 'uncommon', 'rare', 'epic', 'legendary'}
    RARITY_LEVELS = {'common': 1, 'uncommon': 2, 'rare': 3, 'epic': 4, 'legendary': 5}
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_RARITIES:
            raise ValueError(f"无效的徽章稀有度: {self.value}")
    
    def level(self) -> int:
        """获取稀有度级别"""
        return self.RARITY_LEVELS[self.value]
    
    def is_common(self) -> bool:
        """是否为普通"""
        return self.value == 'common'
    
    def is_legendary(self) -> bool:
        """是否为传奇"""
        return self.value == 'legendary'
    
    def __str__(self) -> str:
        return self.value


class RewardType(ValueObject):
    """奖励类型值对象"""
    
    VALID_TYPES = {'points', 'badge', 'item', 'currency', 'privilege'}
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_TYPES:
            raise ValueError(f"无效的奖励类型: {self.value}")
    
    def is_points(self) -> bool:
        """是否为积分奖励"""
        return self.value == 'points'
    
    def is_badge(self) -> bool:
        """是否为徽章奖励"""
        return self.value == 'badge'
    
    def __str__(self) -> str:
        return self.value


class TriggerType(ValueObject):
    """触发类型值对象"""
    
    VALID_TYPES = {
        'exercise_count', 'exercise_duration', 'exercise_calories',
        'task_completed', 'task_perfect', 'streak_days',
        'level_reached', 'collection_complete', 'special_event'
    }
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_TYPES:
            raise ValueError(f"无效的触发类型: {self.value}")
    
    def is_exercise_related(self) -> bool:
        """是否为运动相关"""
        return self.value.startswith('exercise_')
    
    def is_task_related(self) -> bool:
        """是否为任务相关"""
        return self.value.startswith('task_')
    
    def __str__(self) -> str:
        return self.value


class Progress(ValueObject):
    """进度值对象"""
    
    def __init__(self, current: int, target: int):
        if current < 0:
            raise ValueError("当前值不能为负数")
        if target <= 0:
            raise ValueError("目标值必须大于0")
        if current > target:
            raise ValueError("当前值不能超过目标值")
        
        self.current = current
        self.target = target
    
    def percentage(self) -> float:
        """计算完成百分比"""
        return (self.current / self.target) * 100
    
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.current >= self.target
    
    def remaining(self) -> int:
        """剩余数量"""
        return max(0, self.target - self.current)
    
    def __str__(self) -> str:
        return f"{self.current}/{self.target}"
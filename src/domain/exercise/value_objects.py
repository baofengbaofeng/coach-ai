"""
运动领域值对象
"""

from domain.base_simple import ValueObject


class ExerciseCategory(ValueObject):
    """运动分类"""
    
    VALID_CATEGORIES = {'strength', 'cardio', 'flexibility', 'balance', 'mixed'}
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_CATEGORIES:
            raise ValueError(f"无效的运动分类: {self.value}")
    
    def is_strength(self) -> bool:
        return self.value == 'strength'
    
    def is_cardio(self) -> bool:
        return self.value == 'cardio'
    
    def __str__(self):
        return self.value


class ExerciseDifficulty(ValueObject):
    """运动难度"""
    
    VALID_DIFFICULTIES = {'beginner', 'intermediate', 'advanced', 'expert'}
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_DIFFICULTIES:
            raise ValueError(f"无效的运动难度: {self.value}")
    
    def is_beginner(self) -> bool:
        return self.value == 'beginner'
    
    def __str__(self):
        return self.value


class Duration(ValueObject):
    """持续时间（秒）"""
    
    def __init__(self, seconds: int):
        if seconds < 0:
            raise ValueError("持续时间不能为负数")
        self.seconds = seconds
    
    @classmethod
    def from_minutes(cls, minutes: float):
        return cls(int(minutes * 60))
    
    def to_minutes(self):
        return self.seconds / 60
    
    def __str__(self):
        if self.seconds < 60:
            return f"{self.seconds}秒"
        return f"{self.to_minutes():.1f}分钟"


class Repetition(ValueObject):
    """重复次数"""
    
    def __init__(self, count: int):
        if count < 0:
            raise ValueError("重复次数不能为负数")
        self.count = count
    
    def __str__(self):
        return f"{self.count}次"


class Weight(ValueObject):
    """重量（千克）"""
    
    def __init__(self, kilograms: float):
        if kilograms < 0:
            raise ValueError("重量不能为负数")
        self.kilograms = kilograms
    
    def __str__(self):
        return f"{self.kilograms}kg"


class Intensity(ValueObject):
    """强度（1-10）"""
    
    def __init__(self, value: int):
        if not 1 <= value <= 10:
            raise ValueError("强度必须在1-10之间")
        self.value = value
    
    def __str__(self):
        return str(self.value)
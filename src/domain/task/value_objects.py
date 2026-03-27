"""
任务领域值对象
"""

from domain.base_simple import ValueObject
from typing import List, Dict, Any, Optional


class TaskType(ValueObject):
    """任务类型值对象"""
    
    VALID_TYPES = {'homework', 'exercise', 'custom'}
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_TYPES:
            raise ValueError(f"无效的任务类型: {self.value}")
    
    def is_homework(self) -> bool:
        """是否为作业任务"""
        return self.value == 'homework'
    
    def is_exercise(self) -> bool:
        """是否为运动任务"""
        return self.value == 'exercise'
    
    def is_custom(self) -> bool:
        """是否为自定义任务"""
        return self.value == 'custom'
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"TaskType('{self.value}')"


class TaskStatus(ValueObject):
    """任务状态值对象"""
    
    VALID_STATUSES = {'draft', 'active', 'completed', 'cancelled', 'archived'}
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_STATUSES:
            raise ValueError(f"无效的任务状态: {self.value}")
    
    def is_draft(self) -> bool:
        """是否为草稿状态"""
        return self.value == 'draft'
    
    def is_active(self) -> bool:
        """是否为活跃状态"""
        return self.value == 'active'
    
    def is_completed(self) -> bool:
        """是否为完成状态"""
        return self.value == 'completed'
    
    def can_be_modified(self) -> bool:
        """是否可以修改"""
        return self.value in {'draft', 'active'}
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"TaskStatus('{self.value}')"


class TaskPriority(ValueObject):
    """任务优先级值对象"""
    
    VALID_PRIORITIES = {'low', 'medium', 'high', 'urgent'}
    PRIORITY_LEVELS = {'low': 1, 'medium': 2, 'high': 3, 'urgent': 4}
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_PRIORITIES:
            raise ValueError(f"无效的任务优先级: {self.value}")
    
    def level(self) -> int:
        """获取优先级级别（数字）"""
        return self.PRIORITY_LEVELS[self.value]
    
    def is_urgent(self) -> bool:
        """是否为紧急优先级"""
        return self.value == 'urgent'
    
    def is_high_or_urgent(self) -> bool:
        """是否为高或紧急优先级"""
        return self.value in {'high', 'urgent'}
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"TaskPriority('{self.value}')"


class TaskDifficulty(ValueObject):
    """任务难度值对象"""
    
    VALID_DIFFICULTIES = {'beginner', 'intermediate', 'advanced', 'expert'}
    DIFFICULTY_LEVELS = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_DIFFICULTIES:
            raise ValueError(f"无效的任务难度: {self.value}")
    
    def level(self) -> int:
        """获取难度级别（数字）"""
        return self.DIFFICULTY_LEVELS[self.value]
    
    def is_beginner(self) -> bool:
        """是否为初级难度"""
        return self.value == 'beginner'
    
    def is_expert(self) -> bool:
        """是否为专家难度"""
        return self.value == 'expert'
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"TaskDifficulty('{self.value}')"


class AssignmentStatus(ValueObject):
    """任务分配状态值对象"""
    
    VALID_STATUSES = {'assigned', 'in_progress', 'completed', 'cancelled', 'overdue'}
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_STATUSES:
            raise ValueError(f"无效的分配状态: {self.value}")
    
    def is_assigned(self) -> bool:
        """是否为已分配状态"""
        return self.value == 'assigned'
    
    def is_in_progress(self) -> bool:
        """是否为进行中状态"""
        return self.value == 'in_progress'
    
    def is_completed(self) -> bool:
        """是否为完成状态"""
        return self.value == 'completed'
    
    def is_overdue(self) -> bool:
        """是否为逾期状态"""
        return self.value == 'overdue'
    
    def can_start(self) -> bool:
        """是否可以开始"""
        return self.value == 'assigned'
    
    def can_complete(self) -> bool:
        """是否可以完成"""
        return self.value == 'in_progress'
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"AssignmentStatus('{self.value}')"


class EvaluationStatus(ValueObject):
    """任务评估状态值对象"""
    
    VALID_STATUSES = {'pending', 'evaluating', 'completed', 'cancelled'}
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_STATUSES:
            raise ValueError(f"无效的评估状态: {self.value}")
    
    def is_pending(self) -> bool:
        """是否为待评估状态"""
        return self.value == 'pending'
    
    def is_completed(self) -> bool:
        """是否为完成状态"""
        return self.value == 'completed'
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"EvaluationStatus('{self.value}')"


class SubmissionStatus(ValueObject):
    """任务提交状态值对象"""
    
    VALID_STATUSES = {'draft', 'submitted', 'revised', 'accepted', 'rejected'}
    
    def __init__(self, value: str):
        self.value = value
        if self.value not in self.VALID_STATUSES:
            raise ValueError(f"无效的提交状态: {self.value}")
    
    def is_draft(self) -> bool:
        """是否为草稿状态"""
        return self.value == 'draft'
    
    def is_submitted(self) -> bool:
        """是否为已提交状态"""
        return self.value == 'submitted'
    
    def is_accepted(self) -> bool:
        """是否为已接受状态"""
        return self.value == 'accepted'
    
    def can_be_submitted(self) -> bool:
        """是否可以提交"""
        return self.value in {'draft', 'revised'}
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"SubmissionStatus('{self.value}')"


class TaskContent(ValueObject):
    """任务内容值对象（JSON格式）"""
    
    def __init__(self, content: Dict[str, Any]):
        self.content = content or {}
        self._validate()
    
    def _validate(self):
        """验证任务内容"""
        if not isinstance(self.content, dict):
            raise ValueError("任务内容必须是字典格式")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取内容中的值"""
        return self.content.get(key, default)
    
    def update(self, updates: Dict[str, Any]) -> None:
        """更新内容"""
        self.content.update(updates)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.content.copy()
    
    def __str__(self) -> str:
        return str(self.content)
    
    def __repr__(self) -> str:
        return f"TaskContent({self.content})"


class TaskMetadata(ValueObject):
    """任务元数据值对象（JSON格式）"""
    
    def __init__(self, metadata: Dict[str, Any]):
        self.metadata = metadata or {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取元数据中的值"""
        return self.metadata.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置元数据值"""
        self.metadata[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.metadata.copy()
    
    def __str__(self) -> str:
        return str(self.metadata)
    
    def __repr__(self) -> str:
        return f"TaskMetadata({self.metadata})"
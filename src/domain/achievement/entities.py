"""
成就领域实体
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from domain.base_simple import AggregateRoot
from .value_objects import (
    AchievementType, AchievementDifficulty, AchievementStatus,
    BadgeType, BadgeRarity, RewardType, TriggerType, Progress
)


class Achievement(AggregateRoot):
    """成就实体"""
    
    def __init__(
        self,
        name: str,
        description: str,
        achievement_type: AchievementType,
        difficulty: AchievementDifficulty,
        trigger_type: TriggerType,
        target_value: int,
        reward_points: int = 0,
        status: Optional[AchievementStatus] = None,
        icon_url: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.name = name
        self.description = description
        self.achievement_type = achievement_type
        self.difficulty = difficulty
        self.trigger_type = trigger_type
        self.target_value = target_value
        self.reward_points = reward_points
        self.status = status or AchievementStatus("active")
        self.icon_url = icon_url
        self.category = category
        self.tags = tags or []
        self.tenant_id = tenant_id
        
        # 扩展字段
        self.banner_url: Optional[str] = None
        self.reward_badge_id: Optional[str] = None
        self.reward_items: List[Dict[str, Any]] = []
        self.prerequisites: List[str] = []
        self.unlock_count: int = 0
        
        self._validate()
    
    def _validate(self):
        """验证成就数据"""
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("成就名称长度必须至少2个字符")
        
        if not self.description or len(self.description.strip()) < 5:
            raise ValueError("成就描述长度必须至少5个字符")
        
        if self.target_value <= 0:
            raise ValueError("目标值必须大于0")
        
        if self.reward_points < 0:
            raise ValueError("奖励积分不能为负数")
    
    def update_info(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon_url: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """更新成就信息"""
        if not self.status.is_active():
            raise ValueError(f"成就状态为{self.status}，无法修改")
        
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if icon_url is not None:
            self.icon_url = icon_url
        if category is not None:
            self.category = category
        if tags is not None:
            self.tags = tags
        
        self.mark_updated()
    
    def archive(self) -> None:
        """归档成就"""
        self.status = AchievementStatus("archived")
        self.mark_updated()
    
    def activate(self) -> None:
        """激活成就"""
        self.status = AchievementStatus("active")
        self.mark_updated()
    
    def record_unlock(self) -> None:
        """记录解锁次数"""
        self.unlock_count += 1
        self.mark_updated()
    
    def add_prerequisite(self, achievement_id: str) -> None:
        """添加前置成就"""
        if achievement_id not in self.prerequisites:
            self.prerequisites.append(achievement_id)
            self.mark_updated()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'achievement_type': str(self.achievement_type),
            'difficulty': str(self.difficulty),
            'trigger_type': str(self.trigger_type),
            'target_value': self.target_value,
            'reward_points': self.reward_points,
            'status': str(self.status),
            'icon_url': self.icon_url,
            'category': self.category,
            'tags': self.tags,
            'tenant_id': self.tenant_id,
            'unlock_count': self.unlock_count,
            'prerequisites': self.prerequisites,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<Achievement(id='{self.id}', name='{self.name}', type='{self.achievement_type}')>"


class Badge(AggregateRoot):
    """徽章实体"""
    
    def __init__(
        self,
        name: str,
        description: str,
        badge_type: BadgeType,
        rarity: BadgeRarity,
        icon_url: str,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.name = name
        self.description = description
        self.badge_type = badge_type
        self.rarity = rarity
        self.icon_url = icon_url
        self.tenant_id = tenant_id
        
        # 扩展字段
        self.banner_url: Optional[str] = None
        self.achievement_id: Optional[str] = None
        self.earn_count: int = 0
        self.metadata: Dict[str, Any] = {}
        
        self._validate()
    
    def _validate(self):
        """验证徽章数据"""
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("徽章名称长度必须至少2个字符")
        
        if not self.description or len(self.description.strip()) < 5:
            raise ValueError("徽章描述长度必须至少5个字符")
        
        if not self.icon_url:
            raise ValueError("徽章图标URL不能为空")
    
    def record_earn(self) -> None:
        """记录获得次数"""
        self.earn_count += 1
        self.mark_updated()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'badge_type': str(self.badge_type),
            'rarity': str(self.rarity),
            'icon_url': self.icon_url,
            'tenant_id': self.tenant_id,
            'earn_count': self.earn_count,
            'achievement_id': self.achievement_id,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<Badge(id='{self.id}', name='{self.name}', rarity='{self.rarity}')>"


class UserAchievement(AggregateRoot):
    """用户成就实体"""
    
    def __init__(
        self,
        user_id: str,
        achievement_id: str,
        progress: Progress,
        is_unlocked: bool = False,
        unlocked_at: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.user_id = user_id
        self.achievement_id = achievement_id
        self.progress = progress
        self.is_unlocked = is_unlocked
        self.unlocked_at = unlocked_at
        self.tenant_id = tenant_id
        
        self._validate()
    
    def _validate(self):
        """验证用户成就数据"""
        if not self.user_id:
            raise ValueError("用户ID不能为空")
        
        if not self.achievement_id:
            raise ValueError("成就ID不能为空")
    
    def update_progress(self, new_current: int) -> None:
        """更新进度"""
        if self.is_unlocked:
            return  # 已解锁的成就不再更新进度
        
        # 创建新的进度对象
        self.progress = Progress(new_current, self.progress.target)
        
        # 检查是否解锁
        if self.progress.is_completed() and not self.is_unlocked:
            self.is_unlocked = True
            self.unlocked_at = datetime.now()
        
        self.mark_updated()
    
    def unlock(self) -> None:
        """解锁成就"""
        if not self.is_unlocked:
            self.is_unlocked = True
            self.unlocked_at = datetime.now()
            self.mark_updated()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'achievement_id': self.achievement_id,
            'progress': str(self.progress),
            'progress_percentage': self.progress.percentage(),
            'is_unlocked': self.is_unlocked,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
            'tenant_id': self.tenant_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<UserAchievement(user_id='{self.user_id}', achievement_id='{self.achievement_id}', unlocked={self.is_unlocked})>"


class UserBadge(AggregateRoot):
    """用户徽章实体"""
    
    def __init__(
        self,
        user_id: str,
        badge_id: str,
        earned_at: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.user_id = user_id
        self.badge_id = badge_id
        self.earned_at = earned_at or datetime.now()
        self.tenant_id = tenant_id
        
        self._validate()
    
    def _validate(self):
        """验证用户徽章数据"""
        if not self.user_id:
            raise ValueError("用户ID不能为空")
        
        if not self.badge_id:
            raise ValueError("徽章ID不能为空")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'badge_id': self.badge_id,
            'earned_at': self.earned_at.isoformat(),
            'tenant_id': self.tenant_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<UserBadge(user_id='{self.user_id}', badge_id='{self.badge_id}')>"
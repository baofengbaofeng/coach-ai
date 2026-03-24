"""
成就系统数据模型模块，定义成就、用户成就进度、成就分类和奖励等数据模型。
按照豆包AI助手最佳实践：使用Django ORM进行数据建模。
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from core.constants import BusinessRules


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 用户模型引用 ====================
User = get_user_model()


# ==================== 成就分类模型 ====================
class AchievementCategory(models.Model):
    """
    成就分类模型类，用于对成就进行分类管理。
    """
    
    name: models.CharField = models.CharField(
        max_length=100,
        verbose_name="分类名称",
        help_text="成就分类的名称，如：学习成就、运动成就等",
    )
    
    description: models.TextField = models.TextField(
        verbose_name="分类描述",
        help_text="成就分类的详细描述",
        blank=True,
        null=True,
    )
    
    icon: models.CharField = models.CharField(
        max_length=50,
        verbose_name="图标",
        help_text="分类图标名称或路径",
        blank=True,
        null=True,
    )
    
    color: models.CharField = models.CharField(
        max_length=7,
        verbose_name="颜色",
        help_text="分类颜色代码，如：#3B82F6",
        default="#3B82F6",
    )
    
    order: models.PositiveIntegerField = models.PositiveIntegerField(
        verbose_name="排序",
        help_text="分类显示顺序，数字越小越靠前",
        default=0,
    )
    
    is_active: models.BooleanField = models.BooleanField(
        verbose_name="是否激活",
        help_text="是否激活该分类",
        default=True,
    )
    
    created_at: models.DateTimeField = models.DateTimeField(
        verbose_name="创建时间",
        auto_now_add=True,
    )
    
    updated_at: models.DateTimeField = models.DateTimeField(
        verbose_name="更新时间",
        auto_now=True,
    )
    
    class Meta:
        """成就分类模型的元数据配置。"""
        
        verbose_name: str = "成就分类"
        verbose_name_plural: str = "成就分类"
        db_table: str = "achievements_achievementcategory"
        ordering: List[str] = ["order", "name"]
        indexes: List[models.Index] = [
            models.Index(fields=["name"]),
            models.Index(fields=["order", "is_active"]),
            models.Index(fields=["is_active"]),
        ]
    
    def __str__(self) -> str:
        """返回成就分类的字符串表示。"""
        return self.name
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """保存成就分类前的处理。"""
        is_new: bool = self.pk is None
        
        super().save(*args, **kwargs)
        
        if is_new:
            _LOGGER.info("成就分类创建成功: %s (ID: %s)", self.name, self.pk)
        else:
            _LOGGER.debug("成就分类更新成功: %s (ID: %s)", self.name, self.pk)
    
    @property
    def achievement_count(self) -> int:
        """获取该分类下的成就数量。"""
        return self.achievements.filter(is_active=True).count()


# ==================== 成就模型 ====================
class Achievement(models.Model):
    """
    成就模型类，定义具体的成就条件和奖励。
    """
    
    # 成就类型枚举
    class AchievementType(models.TextChoices):
        """成就类型枚举类。"""
        
        COUNT = "count", "计数型"  # 完成特定次数
        STREAK = "streak", "连续型"  # 连续完成
        COMPOSITE = "composite", "复合型"  # 多个条件组合
        TIME_BASED = "time_based", "时间型"  # 时间限制内完成
        MILESTONE = "milestone", "里程碑型"  # 达到特定里程碑
    
    # 成就难度枚举
    class DifficultyLevel(models.TextChoices):
        """成就难度枚举类。"""
        
        EASY = "easy", "简单"
        MEDIUM = "medium", "中等"
        HARD = "hard", "困难"
        EXPERT = "expert", "专家"
        MASTER = "master", "大师"
    
    name: models.CharField = models.CharField(
        max_length=200,
        verbose_name="成就名称",
        help_text="成就的名称，如：学习达人、运动健将等",
    )
    
    description: models.TextField = models.TextField(
        verbose_name="成就描述",
        help_text="成就的详细描述",
    )
    
    category: models.ForeignKey = models.ForeignKey(
        AchievementCategory,
        on_delete=models.SET_NULL,
        verbose_name="成就分类",
        help_text="成就所属的分类",
        related_name="achievements",
        blank=True,
        null=True,
    )
    
    achievement_type: models.CharField = models.CharField(
        max_length=20,
        verbose_name="成就类型",
        help_text="成就的类型",
        choices=AchievementType.choices,
        default=AchievementType.COUNT,
    )
    
    difficulty: models.CharField = models.CharField(
        max_length=20,
        verbose_name="难度等级",
        help_text="成就的难度等级",
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.MEDIUM,
    )
    
    icon: models.CharField = models.CharField(
        max_length=50,
        verbose_name="图标",
        help_text="成就图标名称或路径",
        blank=True,
        null=True,
    )
    
    badge_image: models.CharField = models.CharField(
        max_length=255,
        verbose_name="徽章图片",
        help_text="成就徽章图片路径",
        blank=True,
        null=True,
    )
    
    # 成就条件
    condition_type: models.CharField = models.CharField(
        max_length=50,
        verbose_name="条件类型",
        help_text="成就条件的类型，如：task_completed、exercise_duration等",
    )
    
    condition_value: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="条件值",
        help_text="成就条件的目标值",
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    
    condition_operator: models.CharField = models.CharField(
        max_length=10,
        verbose_name="条件运算符",
        help_text="条件比较运算符，如：gte、lte、eq等",
        default="gte",
    )
    
    # 时间限制（可选）
    time_limit_days: models.PositiveIntegerField = models.PositiveIntegerField(
        verbose_name="时间限制（天）",
        help_text="成就完成的时间限制（天），0表示无限制",
        default=0,
    )
    
    # 奖励设置
    reward_points: models.PositiveIntegerField = models.PositiveIntegerField(
        verbose_name="奖励积分",
        help_text="成就解锁后奖励的积分",
        default=0,
    )
    
    reward_badge: models.CharField = models.CharField(
        max_length=100,
        verbose_name="奖励徽章",
        help_text="成就解锁后奖励的徽章名称",
        blank=True,
        null=True,
    )
    
    reward_message: models.TextField = models.TextField(
        verbose_name="奖励消息",
        help_text="成就解锁时显示的消息",
        blank=True,
        null=True,
    )
    
    # 显示设置
    display_order: models.PositiveIntegerField = models.PositiveIntegerField(
        verbose_name="显示顺序",
        help_text="成就显示顺序，数字越小越靠前",
        default=0,
    )
    
    is_secret: models.BooleanField = models.BooleanField(
        verbose_name="是否隐藏",
        help_text="成就是否隐藏，直到解锁才显示",
        default=False,
    )
    
    is_active: models.BooleanField = models.BooleanField(
        verbose_name="是否激活",
        help_text="是否激活该成就",
        default=True,
    )
    
    created_at: models.DateTimeField = models.DateTimeField(
        verbose_name="创建时间",
        auto_now_add=True,
    )
    
    updated_at: models.DateTimeField = models.DateTimeField(
        verbose_name="更新时间",
        auto_now=True,
    )
    
    class Meta:
        """成就模型的元数据配置。"""
        
        verbose_name: str = "成就"
        verbose_name_plural: str = "成就"
        db_table: str = "achievements_achievement"
        ordering: List[str] = ["display_order", "name"]
        indexes: List[models.Index] = [
            models.Index(fields=["name"]),
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["achievement_type"]),
            models.Index(fields=["difficulty"]),
            models.Index(fields=["is_active", "display_order"]),
        ]
    
    def __str__(self) -> str:
        """返回成就的字符串表示。"""
        return f"{self.name} ({self.get_difficulty_display()})"
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """保存成就前的处理。"""
        is_new: bool = self.pk is None
        
        # 验证条件值
        if self.condition_value <= 0:
            raise ValueError("条件值必须大于0")
        
        super().save(*args, **kwargs)
        
        if is_new:
            _LOGGER.info("成就创建成功: %s (ID: %s)", self.name, self.pk)
        else:
            _LOGGER.debug("成就更新成功: %s (ID: %s)", self.name, self.pk)
    
    def check_condition(self, current_value: Decimal) -> bool:
        """检查是否满足成就条件。"""
        if self.condition_operator == "gte":
            return current_value >= self.condition_value
        elif self.condition_operator == "lte":
            return current_value <= self.condition_value
        elif self.condition_operator == "eq":
            return current_value == self.condition_value
        elif self.condition_operator == "gt":
            return current_value > self.condition_value
        elif self.condition_operator == "lt":
            return current_value < self.condition_value
        else:
            _LOGGER.warning("未知的条件运算符: %s", self.condition_operator)
            return False
    
    @property
    def unlocked_count(self) -> int:
        """获取已解锁该成就的用户数量。"""
        return self.user_achievements.filter(is_unlocked=True).count()
    
    @property
    def unlock_rate(self) -> float:
        """获取成就解锁率。"""
        total_users: int = User.objects.count()
        if total_users == 0:
            return 0.0
        return (self.unlocked_count / total_users) * 100


# ==================== 用户成就模型 ====================
class UserAchievement(models.Model):
    """
    用户成就模型类，记录用户对成就的进度和解锁状态。
    """
    
    user: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="用户",
        help_text="关联的用户",
        related_name="user_achievements",
    )
    
    achievement: models.ForeignKey = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        verbose_name="成就",
        help_text="关联的成就",
        related_name="user_achievements",
    )
    
    # 进度跟踪
    current_value: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="当前值",
        help_text="成就条件的当前进度值",
        default=Decimal("0.00"),
    )
    
    progress_percentage: models.PositiveIntegerField = models.PositiveIntegerField(
        verbose_name="进度百分比",
        help_text="成就进度百分比（0-100）",
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    
    # 解锁状态
    is_unlocked: models.BooleanField = models.BooleanField(
        verbose_name="是否已解锁",
        help_text="成就是否已解锁",
        default=False,
    )
    
    unlocked_at: models.DateTimeField = models.DateTimeField(
        verbose_name="解锁时间",
        help_text="成就解锁的时间",
        blank=True,
        null=True,
    )
    
    # 奖励领取状态
    is_reward_claimed: models.BooleanField = models.BooleanField(
        verbose_name="奖励是否已领取",
        help_text="成就奖励是否已领取",
        default=False,
    )
    
    reward_claimed_at: models.DateTimeField = models.DateTimeField(
        verbose_name="奖励领取时间",
        help_text="成就奖励领取的时间",
        blank=True,
        null=True,
    )
    
    # 时间跟踪
    started_at: models.DateTimeField = models.DateTimeField(
        verbose_name="开始时间",
        help_text="开始追踪成就的时间",
        auto_now_add=True,
    )
    
    last_updated_at: models.DateTimeField = models.DateTimeField(
        verbose_name="最后更新时间",
        help_text="成就进度最后更新的时间",
        auto_now=True,
    )
    
    # 元数据
    metadata: models.JSONField = models.JSONField(
        verbose_name="元数据",
        help_text="存储额外的进度数据",
        blank=True,
        null=True,
        default=dict,
    )
    
    class Meta:
        """用户成就模型的元数据配置。"""
        
        verbose_name: str = "用户成就"
        verbose_name_plural: str = "用户成就"
        db_table: str = "achievements_userachievement"
        ordering: List[str] = ["-unlocked_at", "-last_updated_at"]
        indexes: List[models.Index] = [
            models.Index(fields=["user", "achievement"]),
            models.Index(fields=["user", "is_unlocked"]),
            models.Index(fields=["achievement", "is_unlocked"]),
            models.Index(fields=["is_unlocked", "unlocked_at"]),
            models.Index(fields=["progress_percentage"]),
        ]
        constraints: List[models.Constraint] = [
            models.UniqueConstraint(
                fields=["user", "achievement"],
                name="unique_user_achievement"
            )
        ]
    
    def __str__(self) -> str:
        """返回用户成就的字符串表示。"""
        status: str = "已解锁" if self.is_unlocked else "进行中"
        return f"{self.user.username} - {self.achievement.name} ({status})"
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """保存用户成就前的处理。"""
        is_new: bool = self.pk is None
        
        # 计算进度百分比
        if self.achievement.condition_value > 0:
            self.progress_percentage = min(
                100,
                int((self.current_value / self.achievement.condition_value) * 100)
            )
        else:
            self.progress_percentage = 0
        
        # 检查是否满足解锁条件
        if not self.is_unlocked and self.achievement.check_condition(self.current_value):
            self.is_unlocked = True
            self.unlocked_at = timezone.now()
            _LOGGER.info(
                "成就解锁: 用户 %s 解锁成就 %s (ID: %s)",
                self.user.username, self.achievement.name, self.achievement.pk
            )
        
        super().save(*args, **kwargs)
        
        if is_new:
            _LOGGER.info(
                "用户成就记录创建: 用户 %s, 成就 %s",
                self.user.username, self.achievement.name
            )
    
    def update_progress(self, new_value: Decimal, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """更新成就进度。"""
        self.current_value = new_value
        
        if metadata:
            if self.metadata is None:
                self.metadata = {}
            self.metadata.update(metadata)
        
        # 触发保存以重新计算进度和解锁状态
        self.save()
        
        return self.is_unlocked
    
    def claim_reward(self) -> bool:
        """领取成就奖励。"""
        if not self.is_unlocked:
            _LOGGER.warning(
                "无法领取奖励: 用户 %s 的成就 %s 尚未解锁",
                self.user.username, self.achievement.name
            )
            return False
        
        if self.is_reward_claimed:
            _LOGGER.warning(
                "奖励已领取: 用户 %s 的成就 %s 奖励已领取",
                self.user.username, self.achievement.name
            )
            return False
        
        self.is_reward_claimed = True
        self.reward_claimed_at = timezone.now()
        self.save()
        
        _LOGGER.info(
            "奖励领取成功: 用户 %s 领取成就 %s 的奖励",
            self.user.username, self.achievement.name
        )
        
        return True
    
    @property
    def time_to_unlock(self) -> Optional[float]:
        """获取解锁所需的时间（秒）。"""
        if self.is_unlocked and self.unlocked_at and self.started_at:
            return (self.unlocked_at - self.started_at).total_seconds()
        return None
    
    @property
    def days_since_started(self) -> int:
        """获取从开始到现在经过的天数。"""
        return (timezone.now() - self.started_at).days


# ==================== 成就奖励模型 ====================
class AchievementReward(models.Model):
    """
    成就奖励模型类，定义成就的奖励内容。
    """
    
    achievement: models.OneToOneField = models.OneToOneField(
        Achievement,
        on_delete=models.CASCADE,
        verbose_name="成就",
        help_text="关联的成就",
        related_name="reward",
    )
    
    # 奖励类型
    reward_type: models.CharField = models.CharField(
        max_length=50,
        verbose_name="奖励类型",
        help_text="奖励的类型，如：points、badge、coupon、privilege等",
    )
    
    # 奖励内容
    reward_value: models.CharField = models.CharField(
        max_length=255,
        verbose_name="奖励值",
        help_text="奖励的具体值，如积分数量、徽章名称等",
    )
    
    reward_description: models.TextField = models.TextField(
        verbose_name="奖励描述",
        help_text="奖励的详细描述",
        blank=True,
        null=True,
    )
    
    # 奖励限制
    is_limited: models.BooleanField = models.BooleanField(
        verbose_name="是否有限制",
        help_text="奖励是否有数量或时间限制",
        default=False,
    )
    
    limit_count: models.PositiveIntegerField = models.PositiveIntegerField(
        verbose_name="限制数量",
        help_text="奖励的发放数量限制",
        default=0,
    )
    
    limit_expires_at: models.DateTimeField = models.DateTimeField(
        verbose_name="限制过期时间",
        help_text="奖励的过期时间",
        blank=True,
        null=True,
    )
    
    # 统计信息
    claimed_count: models.PositiveIntegerField = models.PositiveIntegerField(
        verbose_name="已领取数量",
        help_text="奖励已被领取的数量",
        default=0,
    )
    
    created_at: models.DateTimeField = models.DateTimeField(
        verbose_name="创建时间",
        auto_now_add=True,
    )
    
    updated_at: models.DateTimeField = models.DateTimeField(
        verbose_name="更新时间",
        auto_now=True,
    )
    
    class Meta:
        """成就奖励模型的元数据配置。"""
        
        verbose_name: str = "成就奖励"
        verbose_name_plural: str = "成就奖励"
        db_table: str = "achievements_achievementreward"
        ordering: List[str] = ["-created_at"]
        indexes: List[models.Index] = [
            models.Index(fields=["achievement"]),
            models.Index(fields=["reward_type"]),
            models.Index(fields=["is_limited", "limit_expires_at"]),
        ]
    
    def __str__(self) -> str:
        """返回成就奖励的字符串表示。"""
        return f"{self.achievement.name} - {self.reward_type}: {self.reward_value}"
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """保存成就奖励前的处理。"""
        is_new: bool = self.pk is None
        
        super().save(*args, **kwargs)
        
        if is_new:
            _LOGGER.info(
                "成就奖励创建成功: 成就 %s, 奖励类型 %s",
                self.achievement.name, self.reward_type
            )
    
    def can_claim(self) -> bool:
        """检查奖励是否可以领取。"""
        if not self.is_limited:
            return True
        
        # 检查数量限制
        if self.limit_count > 0 and self.claimed_count >= self.limit_count:
            return False
        
        # 检查时间限制
        if self.limit_expires_at and timezone.now() > self.limit_expires_at:
            return False
        
        return True
    
    def claim(self) -> bool:
        """领取奖励。"""
        if not self.can_claim():
            _LOGGER.warning(
                "无法领取奖励: 成就 %s 的奖励已达到限制",
                self.achievement.name
            )
            return False
        
        self.claimed_count += 1
        self.save()
        
        _LOGGER.info(
            "奖励领取记录: 成就 %s 的奖励被领取，当前已领取 %s 次",
            self.achievement.name, self.claimed_count
        )
        
        return True


# ==================== 成就统计模型 ====================
class AchievementStatistic(models.Model):
    """
    成就统计模型类，用于记录成就系统的统计信息。
    """
    
    # 统计类型枚举
    class StatisticType(models.TextChoices):
        """统计类型枚举类。"""
        
        DAILY_UNLOCKS = "daily_unlocks", "每日解锁数"
        CATEGORY_DISTRIBUTION = "category_distribution", "分类分布"
        DIFFICULTY_DISTRIBUTION = "difficulty_distribution", "难度分布"
        USER_PROGRESS = "user_progress", "用户进度"
        REWARD_DISTRIBUTION = "reward_distribution", "奖励分布"
    
    statistic_type: models.CharField = models.CharField(
        max_length=50,
        verbose_name="统计类型",
        help_text="统计的类型",
        choices=StatisticType.choices,
    )
    
    statistic_date: models.DateField = models.DateField(
        verbose_name="统计日期",
        help_text="统计的日期",
    )
    
    # 统计数据
    data: models.JSONField = models.JSONField(
        verbose_name="统计数据",
        help_text="统计的详细数据",
        default=dict,
    )
    
    # 汇总信息
    total_count: models.PositiveIntegerField = models.PositiveIntegerField(
        verbose_name="总数",
        help_text="统计的总数",
        default=0,
    )
    
    average_value: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="平均值",
        help_text="统计的平均值",
        default=Decimal("0.00"),
    )
    
    max_value: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="最大值",
        help_text="统计的最大值",
        default=Decimal("0.00"),
    )
    
    min_value: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="最小值",
        help_text="统计的最小值",
        default=Decimal("0.00"),
    )
    
    created_at: models.DateTimeField = models.DateTimeField(
        verbose_name="创建时间",
        auto_now_add=True,
    )
    
    updated_at: models.DateTimeField = models.DateTimeField(
        verbose_name="更新时间",
        auto_now=True,
    )
    
    class Meta:
        """成就统计模型的元数据配置。"""
        
        verbose_name: str = "成就统计"
        verbose_name_plural: str = "成就统计"
        db_table: str = "achievements_achievementstatistic"
        ordering: List[str] = ["-statistic_date", "statistic_type"]
        indexes: List[models.Index] = [
            models.Index(fields=["statistic_type", "statistic_date"]),
            models.Index(fields=["statistic_date"]),
        ]
        constraints: List[models.Constraint] = [
            models.UniqueConstraint(
                fields=["statistic_type", "statistic_date"],
                name="unique_statistic_type_date"
            )
        ]
    
    def __str__(self) -> str:
        """返回成就统计的字符串表示。"""
        return f"{self.get_statistic_type_display()} - {self.statistic_date}"
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """保存成就统计前的处理。"""
        is_new: bool = self.pk is None
        
        super().save(*args, **kwargs)
        
        if is_new:
            _LOGGER.info(
                "成就统计创建成功: 类型 %s, 日期 %s",
                self.statistic_type, self.statistic_date
            )
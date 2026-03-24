"""
运动管理数据模型模块，定义运动记录、运动计划、运动分析等核心数据结构和关系。
按照豆包AI助手最佳实践：使用Django模型实现业务数据持久化。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.constants import BusinessRules, ExerciseType, FileTypes


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 运动记录模型 ====================
class ExerciseRecord(models.Model):
    """
    运动记录模型类，表示用户的一次运动记录。
    """
    
    # 基础信息
    title = models.CharField(
        _("运动标题"),
        max_length=BusinessRules.EXERCISE_TITLE_MAX_LENGTH,
        help_text=_("运动的标题，用于快速识别运动内容"),
    )
    
    description = models.TextField(
        _("运动描述"),
        max_length=BusinessRules.EXERCISE_DESCRIPTION_MAX_LENGTH,
        blank=True,
        help_text=_("运动的详细描述和目标"),
    )
    
    # 关联信息
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="exercise_records",
        verbose_name=_("用户"),
        help_text=_("进行运动的用户"),
    )
    
    exercise_type = models.CharField(
        _("运动类型"),
        max_length=BusinessRules.EXERCISE_TYPE_MAX_LENGTH,
        choices=ExerciseType.choices(),
        default=ExerciseType.OTHER,
        help_text=_("运动的类型，如跳绳、俯卧撑、仰卧起坐等"),
    )
    
    # 运动数据
    duration_seconds = models.PositiveIntegerField(
        _("运动时长（秒）"),
        validators=[
            MinValueValidator(BusinessRules.MIN_EXERCISE_DURATION),
            MaxValueValidator(BusinessRules.MAX_EXERCISE_DURATION),
        ],
        help_text=_("运动的总时长，单位为秒"),
    )
    
    repetitions = models.PositiveIntegerField(
        _("重复次数"),
        default=0,
        help_text=_("运动的重复次数（如跳绳次数、俯卧撑个数等）"),
    )
    
    calories_burned = models.DecimalField(
        _("消耗卡路里"),
        max_digits=BusinessRules.CALORIES_MAX_DIGITS,
        decimal_places=BusinessRules.CALORIES_DECIMAL_PLACES,
        default=0,
        help_text=_("运动消耗的卡路里（千卡）"),
    )
    
    heart_rate_avg = models.PositiveIntegerField(
        _("平均心率"),
        null=True,
        blank=True,
        help_text=_("运动的平均心率（次/分钟）"),
    )
    
    heart_rate_max = models.PositiveIntegerField(
        _("最大心率"),
        null=True,
        blank=True,
        help_text=_("运动的最大心率（次/分钟）"),
    )
    
    # 文件信息
    video_file = models.FileField(
        _("运动视频"),
        upload_to="exercise/videos/%Y/%m/%d/",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=FileTypes.VIDEO_EXTENSIONS),
        ],
        help_text=_("运动的视频记录文件"),
    )
    
    # 位置信息
    latitude = models.DecimalField(
        _("纬度"),
        max_digits=BusinessRules.COORDINATE_MAX_DIGITS,
        decimal_places=BusinessRules.COORDINATE_DECIMAL_PLACES,
        null=True,
        blank=True,
        help_text=_("运动地点的纬度"),
    )
    
    longitude = models.DecimalField(
        _("经度"),
        max_digits=BusinessRules.COORDINATE_MAX_DIGITS,
        decimal_places=BusinessRules.COORDINATE_DECIMAL_PLACES,
        null=True,
        blank=True,
        help_text=_("运动地点的经度"),
    )
    
    location_name = models.CharField(
        _("地点名称"),
        max_length=BusinessRules.LOCATION_NAME_MAX_LENGTH,
        blank=True,
        help_text=_("运动地点的名称（如：健身房、公园等）"),
    )
    
    # 时间信息
    started_at = models.DateTimeField(
        _("开始时间"),
        default=timezone.now,
        help_text=_("运动开始的时间"),
    )
    
    ended_at = models.DateTimeField(
        _("结束时间"),
        null=True,
        blank=True,
        help_text=_("运动结束的时间"),
    )
    
    # 元数据
    created_at = models.DateTimeField(
        _("创建时间"),
        auto_now_add=True,
        help_text=_("记录创建时间"),
    )
    
    updated_at = models.DateTimeField(
        _("更新时间"),
        auto_now=True,
        help_text=_("记录最后更新时间"),
    )
    
    class Meta:
        """运动记录模型的元数据配置。"""
        
        verbose_name = _("运动记录")
        verbose_name_plural = _("运动记录列表")
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["user", "exercise_type"]),
            models.Index(fields=["started_at", "ended_at"]),
            models.Index(fields=["exercise_type", "duration_seconds"]),
        ]
    
    def __str__(self) -> str:
        """返回运动记录的字符串表示。"""
        return f"{self.title} - {self.user.username} ({self.get_exercise_type_display()})"
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """保存运动记录前的预处理。"""
        is_new: bool = self.pk is None
        
        # 如果结束时间未设置，自动计算
        if self.started_at and not self.ended_at:
            self.ended_at = self.started_at + timezone.timedelta(seconds=self.duration_seconds)
        
        # 调用父类保存方法
        super().save(*args, **kwargs)
        
        # 记录日志
        if is_new:
            _LOGGER.info("运动记录创建成功: %s (用户: %s)", self.title, self.user.username)
        else:
            _LOGGER.debug("运动记录更新成功: %s (ID: %s)", self.title, self.id)
    
    def get_duration_minutes(self) -> float:
        """获取运动时长（分钟）。"""
        return self.duration_seconds / 60.0
    
    def get_calories_per_minute(self) -> float:
        """获取每分钟消耗的卡路里。"""
        if self.duration_seconds == 0:
            return 0.0
        return float(self.calories_burned) / (self.duration_seconds / 60.0)
    
    def get_repetitions_per_minute(self) -> float:
        """获取每分钟的重复次数。"""
        if self.duration_seconds == 0:
            return 0.0
        return self.repetitions / (self.duration_seconds / 60.0)
    
    def is_completed(self) -> bool:
        """检查运动是否已完成。"""
        return self.ended_at is not None and self.ended_at <= timezone.now()
    
    def get_progress_percentage(self) -> float:
        """获取运动进度百分比。"""
        if not self.started_at or not self.ended_at:
            return 0.0
        
        now = timezone.now()
        total_duration = (self.ended_at - self.started_at).total_seconds()
        
        if now <= self.started_at:
            return 0.0
        elif now >= self.ended_at:
            return 100.0
        else:
            elapsed = (now - self.started_at).total_seconds()
            return (elapsed / total_duration) * 100


# ==================== 运动计划模型 ====================
class ExercisePlan(models.Model):
    """
    运动计划模型类，表示用户的长期运动计划。
    """
    
    # 基础信息
    name = models.CharField(
        _("计划名称"),
        max_length=BusinessRules.EXERCISE_PLAN_NAME_MAX_LENGTH,
        help_text=_("运动计划的名称"),
    )
    
    description = models.TextField(
        _("计划描述"),
        max_length=BusinessRules.EXERCISE_PLAN_DESC_MAX_LENGTH,
        blank=True,
        help_text=_("运动计划的详细描述和目标"),
    )
    
    # 关联信息
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="exercise_plans",
        verbose_name=_("用户"),
        help_text=_("制定计划的用户"),
    )
    
    # 计划设置
    target_duration_minutes = models.PositiveIntegerField(
        _("目标时长（分钟）"),
        help_text=_("每次运动的目标时长（分钟）"),
    )
    
    target_repetitions = models.PositiveIntegerField(
        _("目标重复次数"),
        default=0,
        help_text=_("每次运动的目标重复次数"),
    )
    
    target_calories = models.DecimalField(
        _("目标卡路里"),
        max_digits=BusinessRules.CALORIES_MAX_DIGITS,
        decimal_places=BusinessRules.CALORIES_DECIMAL_PLACES,
        default=0,
        help_text=_("每次运动的目标卡路里消耗"),
    )
    
    frequency_per_week = models.PositiveIntegerField(
        _("每周频率"),
        default=3,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(7),
        ],
        help_text=_("每周计划运动的次数"),
    )
    
    # 时间设置
    start_date = models.DateField(
        _("开始日期"),
        default=timezone.now,
        help_text=_("计划开始的日期"),
    )
    
    end_date = models.DateField(
        _("结束日期"),
        null=True,
        blank=True,
        help_text=_("计划结束的日期"),
    )
    
    preferred_time = models.TimeField(
        _("偏好时间"),
        null=True,
        blank=True,
        help_text=_("偏好的运动时间"),
    )
    
    # 状态信息
    is_active = models.BooleanField(
        _("是否激活"),
        default=True,
        help_text=_("标记计划是否处于激活状态"),
    )
    
    # 统计信息
    completed_count = models.PositiveIntegerField(
        _("已完成次数"),
        default=0,
        help_text=_("计划已完成的次数"),
    )
    
    success_rate = models.DecimalField(
        _("完成率"),
        max_digits=BusinessRules.PERCENTAGE_MAX_DIGITS,
        decimal_places=BusinessRules.PERCENTAGE_DECIMAL_PLACES,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text=_("计划的完成率（百分比）"),
    )
    
    # 元数据
    created_at = models.DateTimeField(
        _("创建时间"),
        auto_now_add=True,
        help_text=_("记录创建时间"),
    )
    
    updated_at = models.DateTimeField(
        _("更新时间"),
        auto_now=True,
        help_text=_("记录最后更新时间"),
    )
    
    class Meta:
        """运动计划模型的元数据配置。"""
        
        verbose_name = _("运动计划")
        verbose_name_plural = _("运动计划列表")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["start_date", "end_date"]),
            models.Index(fields=["is_active", "success_rate"]),
        ]
    
    def __str__(self) -> str:
        """返回运动计划的字符串表示。"""
        status = "激活" if self.is_active else "停用"
        return f"{self.name} - {self.user.username} ({status})"
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """保存运动计划前的预处理。"""
        is_new: bool = self.pk is None
        
        # 计算完成率
        if self.completed_count > 0 and self.end_date and self.start_date:
            total_days = (self.end_date - self.start_date).days
            if total_days > 0:
                expected_count = (total_days // 7) * self.frequency_per_week
                if expected_count > 0:
                    self.success_rate = (self.completed_count / expected_count) * 100
        
        # 调用父类保存方法
        super().save(*args, **kwargs)
        
        # 记录日志
        if is_new:
            _LOGGER.info("运动计划创建成功: %s (用户: %s)", self.name, self.user.username)
        else:
            _LOGGER.debug("运动计划更新成功: %s (ID: %s)", self.name, self.id)
    
    def get_remaining_days(self) -> Optional[int]:
        """获取剩余天数。"""
        if not self.end_date:
            return None
        
        today = timezone.now().date()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days
    
    def get_progress_percentage(self) -> float:
        """获取计划进度百分比。"""
        if not self.end_date or not self.start_date:
            return 0.0
        
        today = timezone.now().date()
        total_days = (self.end_date - self.start_date).days
        
        if today <= self.start_date:
            return 0.0
        elif today >= self.end_date:
            return 100.0
        else:
            elapsed_days = (today - self.start_date).days
            return (elapsed_days / total_days) * 100
    
    def get_expected_completion_count(self) -> int:
        """获取预期的完成次数。"""
        if not self.end_date or not self.start_date:
            return 0
        
        total_days = (self.end_date - self.start_date).days
        return (total_days // 7) * self.frequency_per_week
    
    def can_add_exercise(self) -> bool:
        """检查是否可以添加新的运动记录。"""
        if not self.is_active:
            return False
        
        # 检查是否超过预期次数
        expected_count = self.get_expected_completion_count()
        return self.completed_count < expected_count


# ==================== 运动分析模型 ====================
class ExerciseAnalysis(models.Model):
    """
    运动分析模型类，表示对用户运动数据的分析结果。
    """
    
    # 关联信息
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="exercise_analyses",
        verbose_name=_("用户"),
        help_text=_("被分析的用户"),
    )
    
    # 分析周期
    analysis_period = models.CharField(
        _("分析周期"),
        max_length=BusinessRules.ANALYSIS_PERIOD_MAX_LENGTH,
        choices=[
            ("daily", _("每日")),
            ("weekly", _("每周")),
            ("monthly", _("每月")),
            ("yearly", _("每年")),
        ],
        default="weekly",
        help_text=_("分析的时间周期"),
    )
    
    period_start = models.DateField(
        _("周期开始"),
        help_text=_("分析周期的开始日期"),
    )
    
    period_end = models.DateField(
        _("周期结束"),
        help_text=_("分析周期的结束日期"),
    )
    
    # 统计指标
    total_duration_minutes = models.DecimalField(
        _("总时长（分钟）"),
        max_digits=BusinessRules.DURATION_MAX_DIGITS,
        decimal_places=BusinessRules.DURATION_DECIMAL_PLACES,
        default=0,
        help_text=_("周期内的总运动时长（分钟）"),
    )
    
    total_calories = models.DecimalField(
        _("总卡路里"),
        max_digits=BusinessRules.CALORIES_MAX_DIGITS,
        decimal_places=BusinessRules.CALORIES_DECIMAL_PLACES,
        default=0,
        help_text=_("周期内的总卡路里消耗"),
    )
    
    total_repetitions = models.PositiveIntegerField(
        _("总重复次数"),
        default=0,
        help_text=_("周期内的总重复次数"),
    )
    
    exercise_count = models.PositiveIntegerField(
        _("运动次数"),
        default=0,
        help_text=_("周期内的运动次数"),
    )
    
    # 分析结果
    average_duration_minutes = models.DecimalField(
        _("平均时长（分钟）"),
        max_digits=BusinessRules.DURATION_MAX_DIGITS,
        decimal_places=BusinessRules.DURATION_DECIMAL_PLACES,
        default=0,
        help_text=_("每次运动的平均时长（分钟）"),
    )
    
    average_calories = models.DecimalField(
        _("平均卡路里"),
        max_digits=BusinessRules.CALORIES_MAX_DIGITS,
        decimal_places=BusinessRules.CALORIES_DECIMAL_PLACES,
        default=0,
        help_text=_("每次运动的平均卡路里消耗"),
    )
    
    consistency_rate = models.DecimalField(
        _("坚持率"),
        max_digits=BusinessRules.PERCENTAGE_MAX_DIGITS,
        decimal_places=BusinessRules.PERCENTAGE_DECIMAL_PLACES,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text=_("运动计划的坚持率（百分比）"),
    )
    
    improvement_rate = models.DecimalField(
        _("进步率"),
        max_digits=BusinessRules.PERCENTAGE_MAX_DIGITS,
        decimal_places=BusinessRules.PERCENTAGE_DECIMAL_PLACES,
        default=0,
        help_text=_("与前一周期的进步率（百分比）"),
    )
    
    # 分析报告
    strengths = models.TextField(
        _("优势分析"),
        max_length=BusinessRules.ANALYSIS_TEXT_MAX_LENGTH,
        blank=True,
        help_text=_("运动的优势分析"),
    )
    
    weaknesses = models.TextField(
        _("待改进点"),
        max_length=BusinessRules.ANALYSIS_TEXT_MAX_LENGTH,
        blank=True,
        help_text=_("需要改进的方面"),
    )
    
    recommendations = models.TextField(
        _("建议"),
        max_length=BusinessRules.ANALYSIS_TEXT_MAX_LENGTH,
        blank=True,
        help_text=_("改进运动的建议"),
    )
    
    # 元数据
    created_at = models.DateTimeField(
        _("创建时间"),
        auto_now_add=True,
        help_text=_("记录创建时间"),
    )
    
    updated_at = models.DateTimeField(
        _("更新时间"),
        auto_now=True,
        help_text=_("记录最后更新时间"),
    )
    
    class Meta:
        """运动分析模型的元数据配置。"""
        
        verbose_name = _("运动分析")
        verbose_name_plural = _("运动分析列表")
        ordering = ["-period_end"]
        indexes = [
            models.Index(fields=["user", "analysis_period"]),
            models.Index(fields=["period_start", "period_end"]),
            models.Index(fields=["consistency_rate", "improvement_rate"]),
        ]
        unique_together = [["user", "analysis_period", "period_start", "period_end"]]
    
    def __str__(self) -> str:
        """返回运动分析的字符串表示。"""
        return f"{self.user.username} - {self.get_analysis_period_display()}分析 ({self.period_start} 至 {self.period_end})"
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """保存运动分析前的预处理。"""
        is_new: bool = self.pk is None
        
        # 计算平均值
        if self.exercise_count > 0:
            self.average_duration_minutes = self.total_duration_minutes / self.exercise_count
            self.average_calories = self.total_calories / self.exercise_count
        
        # 调用父类保存方法
        super().save(*args, **kwargs)
        
        # 记录日志
        if is_new:
            _LOGGER.info(
                "运动分析创建成功: 用户=%s, 周期=%s",
                self.user.username,
                self.get_analysis_period_display(),
            )
        else:
            _LOGGER.debug(
                "运动分析更新成功: ID=%s, 用户=%s",
                self.id,
                self.user.username,
            )
    
    def get_period_days(self) -> int:
        """获取分析周期的天数。"""
        return (self.period_end - self.period_start).days + 1
    
    def get_daily_average_duration(self) -> float:
        """获取每日平均运动时长。"""
        period_days = self.get_period_days()
        if period_days == 0:
            return 0.0
        return float(self.total_duration_minutes) / period_days
    
    def get_daily_average_calories(self) -> float:
        """获取每日平均卡路里消耗。"""
        period_days = self.get_period_days()
        if period_days == 0:
            return 0.0
        return float(self.total_calories) / period_days
    
    def get_exercise_frequency(self) -> float:
        """获取运动频率（次/天）。"""
        period_days = self.get_period_days()
        if period_days == 0:
            return 0.0
        return self.exercise_count / period_days
    
    def get_health_score(self) -> float:
        """计算健康评分（0-100）。"""
        # 基于多个指标计算综合评分
        score = 0.0
        
        # 1. 坚持率权重：40%
        score += float(self.consistency_rate) * 0.4
        
        # 2. 进步率权重：30%
        score += min(float(self.improvement_rate), 50) * 0.3  # 进步率最高50分
        
        # 3. 运动频率权重：30%
        target_frequency = 0.7  # 目标：每周5次，约0.7次/天
        actual_frequency = self.get_exercise_frequency()
        frequency_score = min(actual_frequency / target_frequency * 30, 30)
        score += frequency_score
        
        return min(score, 100.0)

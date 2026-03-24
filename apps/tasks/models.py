"""
任务管理数据模型模块，定义任务、提醒、任务分类等核心数据结构和关系。
按照豆包AI助手最佳实践：使用Django模型实现业务数据持久化。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.constants import BusinessRules, FileTypes, TaskPriority, TaskStatus


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 任务分类模型 ====================
class TaskCategory(models.Model):
    """
    任务分类模型类，表示任务的分类标签。
    """
    
    # 基础信息
    name = models.CharField(
        _("分类名称"),
        max_length=BusinessRules.TASK_TITLE_MAX_LENGTH,
        unique=True,
        help_text=_("任务分类的名称"),
    )
    
    description = models.TextField(
        _("分类描述"),
        max_length=BusinessRules.TASK_TITLE_MAX_LENGTH * 2,
        blank=True,
        help_text=_("任务分类的详细描述"),
    )
    
    color = models.CharField(
        _("分类颜色"),
        max_length=7,  # #RRGGBB格式
        default="#3B82F6",  # 蓝色
        help_text=_("分类显示颜色（十六进制格式，如#3B82F6）"),
    )
    
    icon = models.CharField(
        _("分类图标"),
        max_length=50,
        blank=True,
        help_text=_("分类图标名称（如：homework、exercise、reading等）"),
    )
    
    # 排序和显示
    order = models.PositiveIntegerField(
        _("排序序号"),
        default=0,
        help_text=_("分类显示顺序，数字越小越靠前"),
    )
    
    is_active = models.BooleanField(
        _("是否激活"),
        default=True,
        help_text=_("标记分类是否处于激活状态"),
    )
    
    # 统计信息
    task_count = models.PositiveIntegerField(
        _("任务数量"),
        default=0,
        help_text=_("该分类下的任务数量"),
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
        """任务分类模型的元数据配置。"""
        
        verbose_name = _("任务分类")
        verbose_name_plural = _("任务分类列表")
        ordering = ["order", "name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["order", "is_active"]),
            models.Index(fields=["is_active", "task_count"]),
        ]
    
    def __str__(self) -> str:
        """返回任务分类的字符串表示。"""
        return self.name
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """保存任务分类前的预处理。"""
        is_new: bool = self.pk is None
        
        # 确保颜色格式正确
        if self.color and not self.color.startswith("#"):
            self.color = f"#{self.color}"
        
        # 调用父类保存方法
        super().save(*args, **kwargs)
        
        # 记录日志
        if is_new:
            _LOGGER.info("任务分类创建成功: %s", self.name)
        else:
            _LOGGER.debug("任务分类更新成功: %s (ID: %s)", self.name, self.id)
    
    def update_task_count(self) -> None:
        """更新任务数量统计。"""
        from apps.tasks.models import Task
        
        count = Task.objects.filter(category=self, is_deleted=False).count()
        self.task_count = count
        self.save(update_fields=["task_count", "updated_at"])
        
        _LOGGER.debug("任务分类统计更新: %s, 任务数: %s", self.name, count)


# ==================== 任务模型 ====================
class Task(models.Model):
    """
    任务模型类，表示用户的一个待办任务。
    """
    
    # 基础信息
    title = models.CharField(
        _("任务标题"),
        max_length=BusinessRules.TASK_TITLE_MAX_LENGTH,
        help_text=_("任务的标题，用于快速识别任务内容"),
    )
    
    description = models.TextField(
        _("任务描述"),
        max_length=BusinessRules.TASK_TITLE_MAX_LENGTH * 5,
        blank=True,
        help_text=_("任务的详细描述和要求"),
    )
    
    # 关联信息
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name=_("用户"),
        help_text=_("任务所属的用户"),
    )
    
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name=_("任务分类"),
        help_text=_("任务的分类标签"),
    )
    
    # 状态和优先级
    status = models.CharField(
        _("任务状态"),
        max_length=20,
        choices=TaskStatus.choices(),
        default=TaskStatus.PENDING,
        help_text=_("任务的当前状态"),
    )
    
    priority = models.CharField(
        _("任务优先级"),
        max_length=10,
        choices=TaskPriority.choices(),
        default=TaskPriority.MEDIUM,
        help_text=_("任务的优先级"),
    )
    
    # 时间信息
    due_date = models.DateTimeField(
        _("截止时间"),
        null=True,
        blank=True,
        help_text=_("任务的截止时间"),
    )
    
    start_date = models.DateTimeField(
        _("开始时间"),
        null=True,
        blank=True,
        help_text=_("任务的计划开始时间"),
    )
    
    completed_at = models.DateTimeField(
        _("完成时间"),
        null=True,
        blank=True,
        help_text=_("任务的实际完成时间"),
    )
    
    estimated_hours = models.DecimalField(
        _("预计耗时"),
        max_digits=5,
        decimal_places=2,
        default=1.0,
        validators=[
            MinValueValidator(0.1),
            MaxValueValidator(1000),
        ],
        help_text=_("任务预计需要的小时数"),
    )
    
    actual_hours = models.DecimalField(
        _("实际耗时"),
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1000),
        ],
        help_text=_("任务实际花费的小时数"),
    )
    
    # 进度和评估
    progress_percentage = models.PositiveIntegerField(
        _("进度百分比"),
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text=_("任务完成进度（0-100%）"),
    )
    
    difficulty_level = models.PositiveIntegerField(
        _("难度等级"),
        default=3,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        help_text=_("任务难度等级（1-5，5为最难）"),
    )
    
    satisfaction_score = models.PositiveIntegerField(
        _("满意度评分"),
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        help_text=_("任务完成后的满意度评分（1-5，5为最满意）"),
    )
    
    # 附件信息
    attachment = models.FileField(
        _("任务附件"),
        upload_to="tasks/attachments/%Y/%m/%d/",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=FileTypes.ALL_EXTENSIONS),
        ],
        help_text=_("任务相关的附件文件"),
    )
    
    # 标签和备注
    tags = models.JSONField(
        _("任务标签"),
        default=list,
        blank=True,
        help_text=_("任务的标签列表，用于快速筛选和分类"),
    )
    
    notes = models.TextField(
        _("任务备注"),
        blank=True,
        help_text=_("任务的额外备注信息"),
    )
    
    # 关联任务
    parent_task = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subtasks",
        verbose_name=_("父任务"),
        help_text=_("如果这是子任务，指向其父任务"),
    )
    
    # 状态标志
    is_recurring = models.BooleanField(
        _("是否重复任务"),
        default=False,
        help_text=_("标记是否为重复性任务"),
    )
    
    recurrence_rule = models.CharField(
        _("重复规则"),
        max_length=200,
        blank=True,
        help_text=_("任务的重复规则（如：每天、每周一等）"),
    )
    
    is_important = models.BooleanField(
        _("是否重要"),
        default=False,
        help_text=_("标记任务是否重要"),
    )
    
    is_urgent = models.BooleanField(
        _("是否紧急"),
        default=False,
        help_text=_("标记任务是否紧急"),
    )
    
    is_deleted = models.BooleanField(
        _("是否删除"),
        default=False,
        help_text=_("标记任务是否已删除（软删除）"),
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
        """任务模型的元数据配置。"""
        
        verbose_name = _("任务")
        verbose_name_plural = _("任务列表")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "priority"]),
            models.Index(fields=["user", "due_date"]),
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["category", "is_deleted"]),
            models.Index(fields=["is_important", "is_urgent"]),
        ]
    
    def __str__(self) -> str:
        """返回任务的字符串表示。"""
        return f"{self.title} - {self.user.username} ({self.get_status_display()})"
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """保存任务前的预处理。"""
        is_new: bool = self.pk is None
        
        # 自动设置状态相关字段
        if self.status == TaskStatus.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
            if self.progress_percentage < 100:
                self.progress_percentage = 100
        
        # 根据优先级设置重要/紧急标志
        if self.priority == TaskPriority.URGENT:
            self.is_urgent = True
            self.is_important = True
        elif self.priority == TaskPriority.HIGH:
            self.is_important = True
        
        # 调用父类保存方法
        super().save(*args, **kwargs)
        
        # 更新分类的任务计数
        if self.category and not self.is_deleted:
            self.category.update_task_count()
        
        # 记录日志
        if is_new:
            _LOGGER.info("任务创建成功: %s (用户: %s)", self.title, self.user.username)
        else:
            _LOGGER.debug("任务更新成功: %s (ID: %s)", self.title, self.id)
    
    def delete(self, *args: Any, **kwargs: Any) -> None:
        """软删除任务。"""
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])
        
        # 更新分类的任务计数
        if self.category:
            self.category.update_task_count()
        
        _LOGGER.info("任务软删除: %s (ID: %s)", self.title, self.id)
    
    def hard_delete(self, *args: Any, **kwargs: Any) -> None:
        """硬删除任务。"""
        super().delete(*args, **kwargs)
        _LOGGER.warning("任务硬删除: %s (ID: %s)", self.title, self.id)
    
    def is_overdue(self) -> bool:
        """检查任务是否已过期。"""
        if not self.due_date or self.status == TaskStatus.COMPLETED:
            return False
        return self.due_date < timezone.now()
    
    def get_overdue_days(self) -> Optional[int]:
        """获取任务过期天数。"""
        if not self.is_overdue():
            return None
        
        overdue_days = (timezone.now() - self.due_date).days
        return max(overdue_days, 1)
    
    def get_remaining_days(self) -> Optional[int]:
        """获取任务剩余天数。"""
        if not self.due_date or self.status == TaskStatus.COMPLETED:
            return None
        
        remaining = (self.due_date - timezone.now()).days
        return max(remaining, 0) if remaining >= 0 else None
    
    def get_time_spent_ratio(self) -> float:
        """获取时间花费比率（实际耗时/预计耗时）。"""
        if self.estimated_hours == 0:
            return 0.0
        return float(self.actual_hours) / float(self.estimated_hours)
    
    def get_efficiency_score(self) -> Optional[float]:
        """获取效率评分（基于进度和时间花费）。"""
        if self.actual_hours == 0 or self.progress_percentage == 0:
            return None
        
        # 效率 = 进度百分比 / 实际耗时（小时）
        efficiency = self.progress_percentage / float(self.actual_hours)
        
        # 标准化到0-10分
        return min(efficiency * 10, 10.0)
    
    def has_subtasks(self) -> bool:
        """检查任务是否有子任务。"""
        return self.subtasks.filter(is_deleted=False).exists()
    
    def get_subtask_count(self) -> int:
        """获取子任务数量。"""
        return self.subtasks.filter(is_deleted=False).count()
    
    def get_completed_subtask_count(self) -> int:
        """获取已完成的子任务数量。"""
        return self.subtasks.filter(
            is_deleted=False,
            status=TaskStatus.COMPLETED,
        ).count()
    
    def get_subtask_progress(self) -> float:
        """获取子任务总体进度。"""
        total_subtasks = self.get_subtask_count()
        if total_subtasks == 0:
            return 0.0
        
        completed_subtasks = self.get_completed_subtask_count()
        return (completed_subtasks / total_subtasks) * 100
    
    def can_complete(self) -> bool:
        """检查任务是否可以标记为完成。"""
        if self.status == TaskStatus.COMPLETED:
            return False
        
        # 如果有子任务，需要所有子任务都完成
        if self.has_subtasks():
            subtask_progress = self.get_subtask_progress()
            return subtask_progress >= 100
        
        return True
    
    def mark_as_completed(self) -> bool:
        """标记任务为完成。"""
        if not self.can_complete():
            return False
        
        self.status = TaskStatus.COMPLETED
        self.completed_at = timezone.now()
        self.progress_percentage = 100
        self.save()
        
        _LOGGER.info("任务标记为完成: %s (ID: %s)", self.title, self.id)
        return True
    
    def mark_as_in_progress(self) -> None:
        """标记任务为进行中。"""
        if self.status != TaskStatus.IN_PROGRESS:
            self.status = TaskStatus.IN_PROGRESS
            self.save()
            _LOGGER.info("任务标记为进行中: %s (ID: %s)", self.title, self.id)
    
    def update_progress(self, percentage: int, actual_hours: Optional[float] = None) -> None:
        """更新任务进度。"""
        if percentage < 0 or percentage > 100:
            raise ValueError("进度百分比必须在0-100之间")
        
        old_progress = self.progress_percentage
        self.progress_percentage = percentage
        
        if actual_hours is not None:
            self.actual_hours = actual_hours
        
        # 如果进度>0，自动标记为进行中
        if percentage > 0 and self.status == TaskStatus.PENDING:
            self.status = TaskStatus.IN_PROGRESS
        
        # 如果进度=100，自动标记为完成
        if percentage == 100:
            self.status = TaskStatus.COMPLETED
            if not self.completed_at:
                self.completed_at = timezone.now()
        
        self.save()
        
        _LOGGER.info(
            "任务进度更新: %s (ID: %s), 进度: %s%% → %s%%",
            self.title,
            self.id,
            old_progress,
            percentage,
        )


# ==================== 任务提醒模型 ====================
class TaskReminder(models.Model):
    """
    任务提醒模型类，表示任务的提醒设置。
    """
    
    # 关联信息
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="reminders",
        verbose_name=_("任务"),
        help_text=_("关联的任务"),
    )
    
    # 提醒设置
    reminder_time = models.DateTimeField(
        _("提醒时间"),
        help_text=_("提醒触发的时间"),
    )
    
    reminder_type = models.CharField(
        _("提醒类型"),
        max_length=20,
        choices=[
            ("notification", _("通知提醒")),
            ("email", _("邮件提醒")),
            ("sms", _("短信提醒")),
            ("push", _("推送提醒")),
        ],
        default="notification",
        help_text=_("提醒的发送方式"),
    )
    
    reminder_message = models.TextField(
        _("提醒消息"),
        max_length=500,
        blank=True,
        help_text=_("提醒的具体消息内容"),
    )
    
    # 状态信息
    is_sent = models.BooleanField(
        _("是否已发送"),
        default=False,
        help_text=_("标记提醒是否已发送"),
    )
    
    sent_at = models.DateTimeField(
        _("发送时间"),
        null=True,
        blank=True,
        help_text=_("提醒实际发送的时间"),
    )
    
    is_active = models.BooleanField(
        _("是否激活"),
        default=True,
        help_text=_("标记提醒是否处于激活状态"),
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
        """任务提醒模型的元数据配置。"""
        
        verbose_name = _("任务提醒")
        verbose_name_plural = _("任务提醒列表")
        ordering = ["reminder_time"]
        indexes = [
            models.Index(fields=["task", "is_active"]),
            models.Index(fields=["reminder_time", "is_sent"]),
            models.Index(fields=["is_active", "is_sent"]),
        ]
    
    def __str__(self) -> str:
        """返回任务提醒的字符串表示。"""
        return f"{self.task.title} - {self.reminder_time.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """保存任务提醒前的预处理。"""
        is_new: bool = self.pk is None
        
        # 验证提醒数量限制
        if is_new:
            task_reminders_count = TaskReminder.objects.filter(
                task=self.task,
                is_active=True,
            ).count()
            
            if task_reminders_count >= BusinessRules.MAX_TASK_REMINDERS:
                raise ValueError(
                    f"每个任务最多只能设置{BusinessRules.MAX_TASK_REMINDERS}个提醒"
                )
        
        # 如果任务已完成，不能设置提醒
        if self.task.status == TaskStatus.COMPLETED:
            raise ValueError("已完成的任务不能设置提醒")
        
        # 提醒时间不能晚于任务截止时间
        if self.task.due_date and self.reminder_time > self.task.due_date:
            raise ValueError("提醒时间不能晚于任务截止时间")
        
        # 调用父类保存方法
        super().save(*args, **kwargs)
        
        # 记录日志
        if is_new:
            _LOGGER.info(
                "任务提醒创建成功: 任务=%s, 时间=%s",
                self.task.title,
                self.reminder_time.strftime("%Y-%m-%d %H:%M"),
            )
        else:
            _LOGGER.debug("任务提醒更新成功: ID=%s", self.id)
    
    def mark_as_sent(self) -> None:
        """标记提醒为已发送。"""
        if not self.is_sent:
            self.is_sent = True
            self.sent_at = timezone.now()
            self.save()
            
            _LOGGER.info("任务提醒标记为已发送: ID=%s, 任务=%s", self.id, self.task.title)
    
    def is_due(self) -> bool:
        """检查提醒是否到期。"""
        if self.is_sent or not self.is_active:
            return False
        
        return self.reminder_time <= timezone.now()
    
    def get_time_until_reminder(self) -> Optional[float]:
        """获取距离提醒还有多少小时。"""
        if self.is_sent or not self.is_active:
            return None
        
        time_diff = self.reminder_time - timezone.now()
        if time_diff.total_seconds() <= 0:
            return 0.0
        
        return time_diff.total_seconds() / 3600  # 转换为小时
    
    def can_send_now(self) -> bool:
        """检查是否可以立即发送提醒。"""
        return (
            self.is_active
            and not self.is_sent
            and self.reminder_time <= timezone.now()
            and self.task.status != TaskStatus.COMPLETED
            and not self.task.is_deleted
        )


# ==================== 任务评论模型 ====================
class TaskComment(models.Model):
    """
    任务评论模型类，表示用户对任务的评论和反馈。
    """
    
    # 关联信息
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("任务"),
        help_text=_("关联的任务"),
    )
    
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="task_comments",
        verbose_name=_("用户"),
        help_text=_("发表评论的用户"),
    )
    
    # 评论内容
    content = models.TextField(
        _("评论内容"),
        max_length=2000,
        help_text=_("评论的具体内容"),
    )
    
    # 附件信息
    attachment = models.FileField(
        _("评论附件"),
        upload_to="tasks/comments/%Y/%m/%d/",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=FileTypes.ALL_EXTENSIONS),
        ],
        help_text=_("评论相关的附件文件"),
    )
    
    # 状态信息
    is_edited = models.BooleanField(
        _("是否编辑过"),
        default=False,
        help_text=_("标记评论是否被编辑过"),
    )
    
    edited_at = models.DateTimeField(
        _("编辑时间"),
        null=True,
        blank=True,
        help_text=_("评论最后编辑的时间"),
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
        """任务评论模型的元数据配置。"""
        
        verbose_name = _("任务评论")
        verbose_name_plural = _("任务评论列表")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["task", "user"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]
    
    def __str__(self) -> str:
        """返回任务评论的字符串表示。"""
        return f"{self.user.username} 评论于 {self.task.title}"
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """保存任务评论前的预处理。"""
        is_new: bool = self.pk is None
        
        # 如果是更新且内容有变化，标记为已编辑
        if not is_new:
            original = TaskComment.objects.get(pk=self.pk)
            if original.content != self.content:
                self.is_edited = True
                self.edited_at = timezone.now()
        
        # 调用父类保存方法
        super().save(*args, **kwargs)
        
        # 记录日志
        if is_new:
            _LOGGER.info(
                "任务评论创建成功: 用户=%s, 任务=%s",
                self.user.username,
                self.task.title,
            )
        else:
            _LOGGER.debug("任务评论更新成功: ID=%s", self.id)
    
    def get_short_content(self, length: int = 100) -> str:
        """获取评论内容的简短版本。"""
        if len(self.content) <= length:
            return self.content
        return self.content[:length] + "..."
    
    def can_edit(self, user) -> bool:
        """检查用户是否可以编辑评论。"""
        return user == self.user or user.is_superuser
    
    def can_delete(self, user) -> bool:
        """检查用户是否可以删除评论。"""
        return (
            user == self.user
            or user == self.task.user
            or user.is_superuser
        )
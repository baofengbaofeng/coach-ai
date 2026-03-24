"""
任务管理序列化器模块，定义任务、提醒、评论等数据的序列化和反序列化逻辑。
按照豆包AI助手最佳实践：使用Django REST Framework序列化器。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.core.validators import FileExtensionValidator
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.tasks.models import Task, TaskCategory, TaskComment, TaskReminder
from core.constants import BusinessRules, FileTypes, TaskPriority, TaskStatus


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 任务分类序列化器 ====================
class TaskCategorySerializer(serializers.ModelSerializer):
    """
    任务分类序列化器类，用于任务分类的序列化和反序列化。
    """
    
    task_count_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        """任务分类序列化器的元数据配置。"""
        
        model = TaskCategory
        fields = [
            "id",
            "name",
            "description",
            "color",
            "icon",
            "order",
            "is_active",
            "task_count",
            "task_count_display",
            "status_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "task_count",
            "task_count_display",
            "status_display",
            "created_at",
            "updated_at",
        ]
    
    def get_task_count_display(self, obj: TaskCategory) -> str:
        """获取任务数量显示文本。"""
        return f"{obj.task_count} 个任务"
    
    def get_status_display(self, obj: TaskCategory) -> str:
        """获取状态显示文本。"""
        return "激活" if obj.is_active else "停用"
    
    def validate_name(self, value: str) -> str:
        """验证分类名称。"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("分类名称不能为空")
        if len(value) > BusinessRules.TASK_TITLE_MAX_LENGTH:
            raise serializers.ValidationError(
                f"分类名称不能超过{BusinessRules.TASK_TITLE_MAX_LENGTH}个字符"
            )
        return value
    
    def validate_color(self, value: str) -> str:
        """验证颜色格式。"""
        value = value.strip()
        if not value.startswith("#"):
            value = f"#{value}"
        
        # 简单的十六进制颜色验证
        if len(value) != 7 or not all(c in "0123456789ABCDEFabcdef" for c in value[1:]):
            raise serializers.ValidationError("颜色必须是#RRGGBB格式的十六进制颜色")
        
        return value
    
    def create(self, validated_data: Dict[str, Any]) -> TaskCategory:
        """创建任务分类。"""
        task_category = TaskCategory.objects.create(**validated_data)
        _LOGGER.info("任务分类创建成功: %s", task_category.name)
        
        return task_category
    
    def update(self, instance: TaskCategory, validated_data: Dict[str, Any]) -> TaskCategory:
        """更新任务分类。"""
        # 更新任务分类
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        _LOGGER.info("任务分类更新成功: %s (ID: %s)", instance.name, instance.id)
        
        return instance


# ==================== 任务序列化器 ====================
class TaskSerializer(serializers.ModelSerializer):
    """
    任务序列化器类，用于任务的序列化和反序列化。
    """
    
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    is_overdue = serializers.SerializerMethodField()
    overdue_days = serializers.SerializerMethodField()
    remaining_days = serializers.SerializerMethodField()
    time_spent_ratio = serializers.SerializerMethodField()
    efficiency_score = serializers.SerializerMethodField()
    has_subtasks = serializers.SerializerMethodField()
    subtask_count = serializers.SerializerMethodField()
    subtask_progress = serializers.SerializerMethodField()
    can_complete = serializers.SerializerMethodField()
    user_name = serializers.CharField(source="user.username", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True, allow_null=True)
    
    class Meta:
        """任务序列化器的元数据配置。"""
        
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "user",
            "user_name",
            "category",
            "category_name",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "due_date",
            "start_date",
            "completed_at",
            "estimated_hours",
            "actual_hours",
            "progress_percentage",
            "difficulty_level",
            "satisfaction_score",
            "attachment",
            "tags",
            "notes",
            "parent_task",
            "is_recurring",
            "recurrence_rule",
            "is_important",
            "is_urgent",
            "is_overdue",
            "overdue_days",
            "remaining_days",
            "time_spent_ratio",
            "efficiency_score",
            "has_subtasks",
            "subtask_count",
            "subtask_progress",
            "can_complete",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user_name",
            "category_name",
            "status_display",
            "priority_display",
            "is_overdue",
            "overdue_days",
            "remaining_days",
            "time_spent_ratio",
            "efficiency_score",
            "has_subtasks",
            "subtask_count",
            "subtask_progress",
            "can_complete",
            "created_at",
            "updated_at",
        ]
    
    def get_is_overdue(self, obj: Task) -> bool:
        """获取是否过期。"""
        return obj.is_overdue()
    
    def get_overdue_days(self, obj: Task) -> Optional[int]:
        """获取过期天数。"""
        return obj.get_overdue_days()
    
    def get_remaining_days(self, obj: Task) -> Optional[int]:
        """获取剩余天数。"""
        return obj.get_remaining_days()
    
    def get_time_spent_ratio(self, obj: Task) -> float:
        """获取时间花费比率。"""
        return obj.get_time_spent_ratio()
    
    def get_efficiency_score(self, obj: Task) -> Optional[float]:
        """获取效率评分。"""
        return obj.get_efficiency_score()
    
    def get_has_subtasks(self, obj: Task) -> bool:
        """获取是否有子任务。"""
        return obj.has_subtasks()
    
    def get_subtask_count(self, obj: Task) -> int:
        """获取子任务数量。"""
        return obj.get_subtask_count()
    
    def get_subtask_progress(self, obj: Task) -> float:
        """获取子任务进度。"""
        return obj.get_subtask_progress()
    
    def get_can_complete(self, obj: Task) -> bool:
        """获取是否可以完成。"""
        return obj.can_complete()
    
    def validate_title(self, value: str) -> str:
        """验证任务标题。"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("任务标题不能为空")
        if len(value) > BusinessRules.TASK_TITLE_MAX_LENGTH:
            raise serializers.ValidationError(
                f"任务标题不能超过{BusinessRules.TASK_TITLE_MAX_LENGTH}个字符"
            )
        return value
    
    def validate_due_date(self, value: Optional[timezone.datetime]) -> Optional[timezone.datetime]:
        """验证截止时间。"""
        if value:
            # 截止时间不能早于当前时间（对于新任务）
            if self.instance is None and value < timezone.now():
                raise serializers.ValidationError("截止时间不能早于当前时间")
            
            # 截止时间不能早于开始时间
            start_date = self.initial_data.get("start_date")
            if start_date:
                try:
                    start_date = timezone.datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                    if value <= start_date:
                        raise serializers.ValidationError("截止时间必须晚于开始时间")
                except (ValueError, AttributeError):
                    pass
        
        return value
    
    def validate_estimated_hours(self, value: float) -> float:
        """验证预计耗时。"""
        if value < 0.1:
            raise serializers.ValidationError("预计耗时不能少于0.1小时")
        if value > 1000:
            raise serializers.ValidationError("预计耗时不能超过1000小时")
        return value
    
    def validate_progress_percentage(self, value: int) -> int:
        """验证进度百分比。"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("进度百分比必须在0-100之间")
        return value
    
    def validate_attachment(self, value: Any) -> Any:
        """验证附件文件。"""
        if value:
            # 检查文件扩展名
            validator = FileExtensionValidator(
                allowed_extensions=FileTypes.ALL_EXTENSIONS
            )
            validator(value)
        
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """验证任务数据的整体一致性。"""
        due_date = attrs.get("due_date")
        start_date = attrs.get("start_date")
        status = attrs.get("status")
        completed_at = attrs.get("completed_at")
        
        # 检查日期关系
        if start_date and due_date and due_date <= start_date:
            raise serializers.ValidationError({
                "due_date": "截止时间必须晚于开始时间"
            })
        
        # 检查状态和完成时间的关系
        if status == TaskStatus.COMPLETED and not completed_at:
            attrs["completed_at"] = timezone.now()
        
        if completed_at and status != TaskStatus.COMPLETED:
            raise serializers.ValidationError({
                "completed_at": "只有已完成的任务才能有完成时间"
            })
        
        # 检查父任务关系
        parent_task = attrs.get("parent_task")
        if parent_task:
            # 不能设置自己为父任务
            if self.instance and parent_task.id == self.instance.id:
                raise serializers.ValidationError({
                    "parent_task": "不能设置自己为父任务"
                })
            
            # 父任务不能是子任务
            if parent_task.parent_task:
                raise serializers.ValidationError({
                    "parent_task": "父任务不能是其他任务的子任务"
                })
        
        return attrs
    
    def create(self, validated_data: Dict[str, Any]) -> Task:
        """创建任务。"""
        # 确保用户字段存在
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data.setdefault("user", request.user)
        
        # 创建任务
        task = Task.objects.create(**validated_data)
        _LOGGER.info(
            "任务创建成功: %s (用户: %s)",
            task.title,
            task.user.username,
        )
        
        return task
    
    def update(self, instance: Task, validated_data: Dict[str, Any]) -> Task:
        """更新任务。"""
        # 检查状态转换
        old_status = instance.status
        new_status = validated_data.get("status", old_status)
        
        if old_status != new_status:
            _LOGGER.info(
                "任务状态变更: %s (ID: %s), 从 %s 变为 %s",
                instance.title,
                instance.id,
                old_status,
                new_status,
            )
        
        # 更新任务
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        _LOGGER.info("任务更新成功: %s (ID: %s)", instance.title, instance.id)
        
        return instance


# ==================== 任务创建序列化器 ====================
class TaskCreateSerializer(serializers.ModelSerializer):
    """
    任务创建序列化器类，专门用于创建任务。
    """
    
    class Meta:
        """任务创建序列化器的元数据配置。"""
        
        model = Task
        fields = [
            "title",
            "description",
            "category",
            "priority",
            "due_date",
            "start_date",
            "estimated_hours",
            "difficulty_level",
            "tags",
            "notes",
            "parent_task",
            "is_recurring",
            "recurrence_rule",
        ]
    
    def create(self, validated_data: Dict[str, Any]) -> Task:
        """创建任务。"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("用户未认证")
        
        # 设置用户
        validated_data["user"] = request.user
        
        # 创建任务
        task = Task.objects.create(**validated_data)
        _LOGGER.info(
            "任务创建成功: %s (用户: %s)",
            task.title,
            request.user.username,
        )
        
        return task


# ==================== 任务进度更新序列化器 ====================
class TaskProgressSerializer(serializers.Serializer):
    """
    任务进度更新序列化器类，用于更新任务进度。
    """
    
    progress_percentage = serializers.IntegerField(
        min_value=0,
        max_value=100,
        help_text="任务进度百分比（0-100）",
    )
    
    actual_hours = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=0,
        max_value=1000,
        required=False,
        help_text="实际耗时（小时）",
    )
    
    def save(self, task_id: int) -> Task:
        """保存进度更新。"""
        from django.db import transaction
        
        progress_percentage = self.validated_data["progress_percentage"]
        actual_hours = self.validated_data.get("actual_hours")
        
        with transaction.atomic():
            # 获取任务
            try:
                task = Task.objects.get(id=task_id)
            except Task.DoesNotExist:
                raise serializers.ValidationError(f"任务ID {task_id} 不存在")
            
            # 更新进度
            task.update_progress(progress_percentage, actual_hours)
            
            _LOGGER.info(
                "任务进度更新: %s (ID: %s), 进度: %s%%",
                task.title,
                task.id,
                progress_percentage,
            )
            
            return task


# ==================== 任务提醒序列化器 ====================
class TaskReminderSerializer(serializers.ModelSerializer):
    """
    任务提醒序列化器类，用于任务提醒的序列化和反序列化。
    """
    
    reminder_type_display = serializers.CharField(source="get_reminder_type_display", read_only=True)
    is_due = serializers.SerializerMethodField()
    time_until_reminder = serializers.SerializerMethodField()
    can_send_now = serializers.SerializerMethodField()
    task_title = serializers.CharField(source="task.title", read_only=True)
    
    class Meta:
        """任务提醒序列化器的元数据配置。"""
        
        model = TaskReminder
        fields = [
            "id",
            "task",
            "task_title",
            "reminder_time",
            "reminder_type",
            "reminder_type_display",
            "reminder_message",
            "is_sent",
            "sent_at",
            "is_active",
            "is_due",
            "time_until_reminder",
            "can_send_now",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "task_title",
            "reminder_type_display",
            "is_sent",
            "sent_at",
            "is_due",
            "time_until_reminder",
            "can_send_now",
            "created_at",
            "updated_at",
        ]
    
    def get_is_due(self, obj: TaskReminder) -> bool:
        """获取是否到期。"""
        return obj.is_due()
    
    def get_time_until_reminder(self, obj: TaskReminder) -> Optional[float]:
        """获取距离提醒还有多少小时。"""
        return obj.get_time_until_reminder()
    
    def get_can_send_now(self, obj: TaskReminder) -> bool:
        """获取是否可以立即发送。"""
        return obj.can_send_now()
    
    def validate_reminder_time(self, value: timezone.datetime) -> timezone.datetime:
        """验证提醒时间。"""
        # 提醒时间不能早于当前时间
        if value < timezone.now():
            raise serializers.ValidationError("提醒时间不能早于当前时间")
        
        # 获取关联的任务
        task_id = self.initial_data.get("task")
        if task_id:
            try:
                task = Task.objects.get(id=task_id)
                # 提醒时间不能晚于任务截止时间
                if task.due_date and value > task.due_date:
                    raise serializers.ValidationError("提醒时间不能晚于任务截止时间")
                
                # 如果任务已完成，不能设置提醒
                if task.status == TaskStatus.COMPLETED:
                    raise serializers.ValidationError("已完成的任务不能设置提醒")
            except Task.DoesNotExist:
                pass
        
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """验证任务提醒数据的整体一致性。"""
        task = attrs.get("task")
        reminder_time = attrs.get("reminder_time")
        
        if task and reminder_time:
            # 检查提醒数量限制
            if self.instance is None:  # 新建提醒
                active_reminders = TaskReminder.objects.filter(
                    task=task,
                    is_active=True,
                ).count()
                
                if active_reminders >= BusinessRules.MAX_TASK_REMINDERS:
                    raise serializers.ValidationError({
                        "task": f"每个任务最多只能设置{BusinessRules.MAX_TASK_REMINDERS}个提醒"
                    })
            
            # 提醒时间不能晚于任务截止时间
            if task.due_date and reminder_time > task.due_date:
                raise serializers.ValidationError({
                    "reminder_time": "提醒时间不能晚于任务截止时间"
                })
            
            # 如果任务已完成，不能设置提醒
            if task.status == TaskStatus.COMPLETED:
                raise serializers.ValidationError({
                    "task": "已完成的任务不能设置提醒"
                })
        
        return attrs
    
    def create(self, validated_data: Dict[str, Any]) -> TaskReminder:
        """创建任务提醒。"""
        # 创建任务提醒
        task_reminder = TaskReminder.objects.create(**validated_data)
        _LOGGER.info(
            "任务提醒创建成功: 任务=%s, 时间=%s",
            task_reminder.task.title,
            task_reminder.reminder_time.strftime("%Y-%m-%d %H:%M"),
        )
        
        return task_reminder
    
    def update(self, instance: TaskReminder, validated_data: Dict[str, Any]) -> TaskReminder:
        """更新任务提醒。"""
        # 检查状态转换
        old_is_active = instance.is_active
        new_is_active = validated_data.get("is_active", old_is_active)
        
        if old_is_active != new_is_active:
            _LOGGER.info(
                "任务提醒状态变更: ID=%s, 从 %s 变为 %s",
                instance.id,
                "激活" if old_is_active else "停用",
                "激活" if new_is_active else "停用",
            )
        
        # 更新任务提醒
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        _LOGGER.info("任务提醒更新成功: ID=%s", instance.id)
        
        return instance


# ==================== 任务评论序列化器 ====================
class TaskCommentSerializer(serializers.ModelSerializer):
    """
    任务评论序列化器类，用于任务评论的序列化和反序列化。
    """
    
    user_name = serializers.CharField(source="user.username", read_only=True)
    task_title = serializers.CharField(source="task.title", read_only=True)
    short_content = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    
    class Meta:
        """任务评论序列化器的元数据配置。"""
        
        model = TaskComment
        fields = [
            "id",
            "task",
            "task_title",
            "user",
            "user_name",
            "content",
            "short_content",
            "attachment",
            "is_edited",
            "edited_at",
            "can_edit",
            "can_delete",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "task_title",
            "user_name",
            "short_content",
            "is_edited",
            "edited_at",
            "can_edit",
            "can_delete",
            "created_at",
            "updated_at",
        ]
    
    def get_short_content(self, obj: TaskComment) -> str:
        """获取简短内容。"""
        return obj.get_short_content()
    
    def get_can_edit(self, obj: TaskComment) -> bool:
        """获取是否可以编辑。"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.can_edit(request.user)
    
    def get_can_delete(self, obj: TaskComment) -> bool:
        """获取是否可以删除。"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.can_delete(request.user)
    
    def validate_content(self, value: str) -> str:
        """验证评论内容。"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("评论内容不能为空")
        if len(value) > 2000:
            raise serializers.ValidationError("评论内容不能超过2000个字符")
        return value
    
    def validate_attachment(self, value: Any) -> Any:
        """验证附件文件。"""
        if value:
            # 检查文件扩展名
            validator = FileExtensionValidator(
                allowed_extensions=FileTypes.ALL_EXTENSIONS
            )
            validator(value)
        
        return value
    
    def create(self, validated_data: Dict[str, Any]) -> TaskComment:
        """创建任务评论。"""
        # 确保用户字段存在
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data.setdefault("user", request.user)
        
        # 创建任务评论
        task_comment = TaskComment.objects.create(**validated_data)
        _LOGGER.info(
            "任务评论创建成功: 用户=%s, 任务=%s",
            task_comment.user.username,
            task_comment.task.title,
        )
        
        return task_comment
    
    def update(self, instance: TaskComment, validated_data: Dict[str, Any]) -> TaskComment:
        """更新任务评论。"""
        # 检查内容是否有变化
        old_content = instance.content
        new_content = validated_data.get("content", old_content)
        
        if old_content != new_content:
            _LOGGER.info(
                "任务评论内容更新: ID=%s, 任务=%s",
                instance.id,
                instance.task.title,
            )
        
        # 更新任务评论
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        _LOGGER.info("任务评论更新成功: ID=%s", instance.id)
        
        return instance


# ==================== 任务统计序列化器 ====================
class TaskStatisticsSerializer(serializers.Serializer):
    """
    任务统计序列化器类，用于任务统计数据的序列化。
    """
    
    total_tasks = serializers.IntegerField(help_text="总任务数")
    completed_tasks = serializers.IntegerField(help_text="已完成任务数")
    in_progress_tasks = serializers.IntegerField(help_text="进行中任务数")
    overdue_tasks = serializers.IntegerField(help_text="过期任务数")
    completion_rate = serializers.FloatField(help_text="完成率")
    average_progress = serializers.FloatField(help_text="平均进度")
    priority_distribution = serializers.DictField(help_text="优先级分布")
    status_distribution = serializers.DictField(help_text="状态分布")
    category_distribution = serializers.DictField(help_text="分类分布")
    weekly_trend = serializers.ListField(help_text="周趋势数据")

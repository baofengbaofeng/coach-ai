"""
任务管理后台配置模块。
按照豆包AI助手最佳实践：使用Django Admin进行数据管理。
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.tasks.models import Task, TaskCategory, TaskComment, TaskReminder


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    """任务分类管理。"""
    
    list_display = ["id", "name", "color", "icon", "order", "is_active", "task_count", "created_at"]
    list_display_links = ["id", "name"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description", "icon"]
    list_per_page = 50
    
    fieldsets = (
        (_("基础信息"), {"fields": ("name", "description", "color", "icon")}),
        (_("排序和显示"), {"fields": ("order", "is_active")}),
        (_("统计信息"), {"fields": ("task_count",), "classes": ("collapse",)}),
        (_("元数据"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    
    readonly_fields = ["created_at", "updated_at", "task_count"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """任务管理。"""
    
    list_display = [
        "id", "title", "user", "category", "status", "priority", 
        "due_date", "progress_percentage", "is_important", "is_urgent", "created_at"
    ]
    list_display_links = ["id", "title"]
    list_filter = ["status", "priority", "category", "is_important", "is_urgent", "due_date", "created_at", "user"]
    search_fields = ["title", "description", "notes", "user__username", "user__email"]
    list_per_page = 50
    
    fieldsets = (
        (_("基础信息"), {"fields": ("title", "description", "user", "category", "parent_task")}),
        (_("状态和优先级"), {"fields": ("status", "priority", "is_important", "is_urgent")}),
        (_("时间信息"), {"fields": ("due_date", "start_date", "completed_at", "estimated_hours", "actual_hours")}),
        (_("进度和评估"), {"fields": ("progress_percentage", "difficulty_level", "satisfaction_score")}),
        (_("附件和标签"), {"fields": ("attachment", "tags", "notes"), "classes": ("collapse",)}),
        (_("重复设置"), {"fields": ("is_recurring", "recurrence_rule"), "classes": ("collapse",)}),
        (_("状态标志"), {"fields": ("is_deleted",), "classes": ("collapse",)}),
        (_("元数据"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    
    readonly_fields = ["created_at", "updated_at"]


@admin.register(TaskReminder)
class TaskReminderAdmin(admin.ModelAdmin):
    """任务提醒管理。"""
    
    list_display = ["id", "task", "reminder_time", "reminder_type", "is_sent", "is_active", "created_at"]
    list_display_links = ["id", "task"]
    list_filter = ["reminder_type", "is_sent", "is_active", "reminder_time", "created_at"]
    search_fields = ["task__title", "reminder_message"]
    list_per_page = 50
    
    fieldsets = (
        (_("关联信息"), {"fields": ("task",)}),
        (_("提醒设置"), {"fields": ("reminder_time", "reminder_type", "reminder_message")}),
        (_("状态信息"), {"fields": ("is_sent", "sent_at", "is_active")}),
        (_("元数据"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    
    readonly_fields = ["created_at", "updated_at", "sent_at"]


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    """任务评论管理。"""
    
    list_display = ["id", "task", "user", "short_content", "is_edited", "created_at"]
    list_display_links = ["id", "task"]
    list_filter = ["is_edited", "created_at", "user"]
    search_fields = ["content", "task__title", "user__username", "user__email"]
    list_per_page = 50
    
    fieldsets = (
        (_("关联信息"), {"fields": ("task", "user")}),
        (_("评论内容"), {"fields": ("content", "attachment")}),
        (_("状态信息"), {"fields": ("is_edited", "edited_at"), "classes": ("collapse",)}),
        (_("元数据"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    
    readonly_fields = ["created_at", "updated_at", "edited_at"]
    
    def short_content(self, obj):
        """显示简短内容。"""
        content = obj.content
        if len(content) > 50:
            return content[:50] + "..."
        return content
    
    short_content.short_description = _("评论内容")
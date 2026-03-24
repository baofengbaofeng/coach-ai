"""
作业管理后台配置模块，定义Django管理界面的展示和操作逻辑。
按照豆包AI助手最佳实践：为每个模型创建友好的管理界面。
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils import timezone
from django.utils.html import format_html

from apps.homework.models import Homework, KnowledgePoint, Question
from core.constants import HomeworkStatus


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 题目内联管理 ====================
class QuestionInline(admin.TabularInline):
    """
    题目内联管理类，在作业管理页面中内嵌题目管理。
    """
    
    model: type[Question] = Question
    extra: int = 0
    fields: list[str] = [
        "question_number",
        "content",
        "question_type",
        "student_answer",
        "correct_answer",
        "max_score",
        "actual_score",
        "is_correct",
    ]
    readonly_fields: list[str] = ["actual_score", "is_correct"]
    ordering: list[str] = ["question_number"]
    
    def has_add_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        """控制是否允许添加题目。"""
        return True
    
    def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        """控制是否允许修改题目。"""
        return True
    
    def has_delete_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        """控制是否允许删除题目。"""
        return True


# ==================== 知识点内联管理 ====================
class KnowledgePointInline(admin.TabularInline):
    """
    知识点内联管理类，在题目管理页面中内嵌知识点管理。
    """
    
    model: type[KnowledgePoint] = KnowledgePoint.questions.through
    extra: int = 0
    verbose_name: str = "关联知识点"
    verbose_name_plural: str = "关联知识点列表"
    
    def has_add_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        """控制是否允许添加知识点关联。"""
        return True
    
    def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        """控制是否允许修改知识点关联。"""
        return True
    
    def has_delete_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        """控制是否允许删除知识点关联。"""
        return True


# ==================== 作业管理配置 ====================
@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    """
    作业管理配置类。
    """
    
    # 列表页配置
    list_display: list[str] = [
        "id",
        "title",
        "student",
        "subject",
        "status_display",
        "progress_bar",
        "total_score",
        "accuracy_rate",
        "submitted_at",
        "is_overdue_display",
    ]
    
    list_filter: list[str] = [
        "status",
        "subject",
        "submitted_at",
        "corrected_at",
    ]
    
    search_fields: list[str] = [
        "title",
        "description",
        "student__username",
        "student__email",
    ]
    
    list_per_page: int = 20
    ordering: list[str] = ["-submitted_at"]
    date_hierarchy: str = "submitted_at"
    
    # 详情页配置
    fieldsets: tuple = (
        ("基本信息", {
            "fields": (
                "title",
                "description",
                "student",
                "subject",
            ),
        }),
        ("状态信息", {
            "fields": (
                "status",
                "submitted_at",
                "deadline",
                "corrected_at",
            ),
        }),
        ("文件信息", {
            "fields": (
                "original_file",
                "processed_file",
            ),
        }),
        ("统计信息", {
            "fields": (
                "total_score",
                "accuracy_rate",
            ),
        }),
        ("元数据", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )
    
    readonly_fields: list[str] = [
        "created_at",
        "updated_at",
        "total_score",
        "accuracy_rate",
    ]
    
    # 内联管理
    inlines: list[type[admin.TabularInline]] = [QuestionInline]
    
    # 自定义操作
    actions: list[str] = [
        "mark_as_processing",
        "mark_as_correcting",
        "mark_as_completed",
        "mark_as_error",
        "recalculate_scores",
    ]
    
    def status_display(self, obj: Homework) -> str:
        """显示状态的中文名称。"""
        return obj.get_status_display()
    
    status_display.short_description = "状态"
    status_display.admin_order_field = "status"
    
    def progress_bar(self, obj: Homework) -> str:
        """显示进度条。"""
        progress = obj.get_progress_percentage()
        color = "green" if progress == 100 else "orange" if progress >= 50 else "red"
        
        return format_html(
            '<div style="width: 100px; background: #eee; border-radius: 3px;">'
            '<div style="width: {}%; background: {}; height: 20px; border-radius: 3px; '
            'text-align: center; color: white; line-height: 20px;">{}%</div>'
            '</div>',
            progress,
            color,
            int(progress),
        )
    
    progress_bar.short_description = "进度"
    
    def is_overdue_display(self, obj: Homework) -> str:
        """显示是否过期。"""
        if obj.is_overdue():
            return format_html('<span style="color: red;">⚠️ 已过期</span>')
        elif obj.deadline:
            return format_html('<span style="color: green;">✓ 未过期</span>')
        else:
            return format_html('<span style="color: gray;">- 无截止时间</span>')
    
    is_overdue_display.short_description = "过期状态"
    
    # 自定义操作方法
    @admin.action(description="标记为处理中")
    def mark_as_processing(self, request: HttpRequest, queryset: QuerySet[Homework]) -> None:
        """将选中的作业标记为处理中状态。"""
        updated = queryset.filter(status=HomeworkStatus.SUBMITTED).update(
            status=HomeworkStatus.PROCESSING
        )
        
        self.message_user(
            request,
            f"成功将 {updated} 份作业标记为处理中",
            messages.SUCCESS,
        )
    
    @admin.action(description="标记为批改中")
    def mark_as_correcting(self, request: HttpRequest, queryset: QuerySet[Homework]) -> None:
        """将选中的作业标记为批改中状态。"""
        updated = queryset.filter(status=HomeworkStatus.PROCESSING).update(
            status=HomeworkStatus.CORRECTING
        )
        
        self.message_user(
            request,
            f"成功将 {updated} 份作业标记为批改中",
            messages.SUCCESS,
        )
    
    @admin.action(description="标记为已完成")
    def mark_as_completed(self, request: HttpRequest, queryset: QuerySet[Homework]) -> None:
        """将选中的作业标记为已完成状态。"""
        updated = queryset.filter(status=HomeworkStatus.CORRECTING).update(
            status=HomeworkStatus.COMPLETED,
            corrected_at=timezone.now(),
        )
        
        self.message_user(
            request,
            f"成功将 {updated} 份作业标记为已完成",
            messages.SUCCESS,
        )
    
    @admin.action(description="标记为错误")
    def mark_as_error(self, request: HttpRequest, queryset: QuerySet[Homework]) -> None:
        """将选中的作业标记为错误状态。"""
        updated = queryset.exclude(status=HomeworkStatus.COMPLETED).update(
            status=HomeworkStatus.ERROR
        )
        
        self.message_user(
            request,
            f"成功将 {updated} 份作业标记为错误",
            messages.SUCCESS,
        )
    
    @admin.action(description="重新计算得分")
    def recalculate_scores(self, request: HttpRequest, queryset: QuerySet[Homework]) -> None:
        """重新计算选中作业的得分。"""
        from django.db import transaction
        
        updated_count = 0
        
        with transaction.atomic():
            for homework in queryset:
                # 重新计算所有题目的得分
                questions = homework.questions.all()
                for question in questions:
                    question.update_score()
                    question.save()
                
                # 计算作业总分和正确率
                total_score = sum(q.actual_score for q in questions)
                correct_count = questions.filter(is_correct=True).count()
                accuracy_rate = (correct_count / len(questions) * 100) if questions else 0
                
                # 更新作业
                homework.total_score = total_score
                homework.accuracy_rate = accuracy_rate
                homework.save()
                
                updated_count += 1
        
        self.message_user(
            request,
            f"成功重新计算 {updated_count} 份作业的得分",
            messages.SUCCESS,
        )
    
    def save_model(self, request: HttpRequest, obj: Homework, form: Any, change: bool) -> None:
        """保存作业模型时的自定义逻辑。"""
        # 如果是新创建的作业且未设置状态，默认为草稿
        if not change and not obj.status:
            obj.status = HomeworkStatus.DRAFT
        
        # 如果状态变为已完成，设置批改时间
        if change and "status" in form.changed_data and obj.status == HomeworkStatus.COMPLETED:
            obj.corrected_at = timezone.now()
        
        super().save_model(request, obj, form, change)
        
        _LOGGER.info(
            "作业%s保存成功: %s (ID: %s)",
            "更新" if change else "创建",
            obj.title,
            obj.id,
        )


# ==================== 题目管理配置 ====================
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    题目管理配置类。
    """
    
    # 列表页配置
    list_display: list[str] = [
        "id",
        "homework",
        "question_number",
        "content_preview",
        "question_type_display",
        "max_score",
        "actual_score",
        "score_percentage",
        "is_correct_display",
        "created_at",
    ]
    
    list_filter: list[str] = [
        "question_type",
        "is_correct",
        "homework__subject",
        "homework__status",
    ]
    
    search_fields: list[str] = [
        "content",
        "student_answer",
        "correct_answer",
        "correction_notes",
        "homework__title",
        "homework__student__username",
    ]
    
    list_per_page: int = 20
    ordering: list[str] = ["homework", "question_number"]
    date_hierarchy: str = "created_at"
    
    # 详情页配置
    fieldsets: tuple = (
        ("基础信息", {
            "fields": (
                "homework",
                "question_number",
                "content",
                "question_type",
            ),
        }),
        ("答案信息", {
            "fields": (
                "student_answer",
                "correct_answer",
            ),
        }),
        ("评分信息", {
            "fields": (
                "max_score",
                "actual_score",
                "correction_notes",
                "is_correct",
            ),
        }),
        ("元数据", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )
    
    readonly_fields: list[str] = [
        "created_at",
        "updated_at",
        "actual_score",
        "is_correct",
    ]
    
    # 内联管理
    inlines: list[type[admin.TabularInline]] = [KnowledgePointInline]
    
    # 自定义操作
    actions: list[str] = [
        "recalculate_scores",
        "mark_as_correct",
        "mark_as_incorrect",
    ]
    
    def content_preview(self, obj: Question) -> str:
        """显示内容预览。"""
        preview = obj.content[:50]
        if len(obj.content) > 50:
            preview += "..."
        return preview
    
    content_preview.short_description = "题目内容"
    
    def question_type_display(self, obj: Question) -> str:
        """显示题目类型的中文名称。"""
        return obj.get_question_type_display()
    
    question_type_display.short_description = "题目类型"
    question_type_display.admin_order_field = "question_type"
    
    def score_percentage(self, obj: Question) -> str:
        """显示得分百分比。"""
        if obj.max_score == 0:
            return "0%"
        
        percentage = (obj.actual_score / obj.max_score) * 100
        color = "green" if percentage >= 80 else "orange" if percentage >= 60 else "red"
        
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color,
            percentage,
        )
    
    score_percentage.short_description = "得分率"
    
    def is_correct_display(self, obj: Question) -> str:
        """显示是否正确。"""
        if obj.is_correct:
            return format_html('<span style="color: green;">✓ 正确</span>')
        else:
            return format_html('<span style="color: red;">✗ 错误</span>')
    
    is_correct_display.short_description = "正确性"
    
    # 自定义操作方法
    @admin.action(description="重新计算得分")
    def recalculate_scores(self, request: HttpRequest, queryset: QuerySet[Question]) -> None:
        """重新计算选中题目的得分。"""
        updated_count = 0
        
        for question in queryset:
            question.update_score()
            question.save()
            updated_count += 1
        
        self.message_user(
            request,
            f"成功重新计算 {updated_count} 道题目的得分",
            messages.SUCCESS,
        )
    
    @admin.action(description="标记为正确")
    def mark_as_correct(self, request: HttpRequest, queryset: QuerySet[Question]) -> None:
        """将选中的题目标记为正确。"""
        updated = queryset.update(
            is_correct=True,
            actual_score=models.F("max_score"),
        )
        
        self.message_user(
            request,
            f"成功将 {updated} 道题目标记为正确",
            messages.SUCCESS,
        )
    
    @admin.action(description="标记为错误")
    def mark_as_incorrect(self, request: HttpRequest, queryset: QuerySet[Question]) -> None:
        """将选中的题目标记为错误。"""
        updated = queryset.update(
            is_correct=False,
            actual_score=0,
        )
        
        self.message_user(
            request,
            f"成功将 {updated} 道题目标记为错误",
            messages.SUCCESS,
        )
    
    def save_model(self, request: HttpRequest, obj: Question, form: Any, change: bool) -> None:
        """保存题目模型时的自定义逻辑。"""
        # 保存前重新计算得分
        obj.update_score()
        
        super().save_model(request, obj, form, change)
        
        _LOGGER.info(
            "题目%s保存成功: 作业ID=%s, 题号=%s",
            "更新" if change else "创建",
            obj.homework_id,
            obj.question_number,
        )


# ==================== 知识点管理配置 ====================
@admin.register(KnowledgePoint)
class KnowledgePointAdmin(admin.ModelAdmin):
    """
    知识点管理配置类。
    """
    
    # 列表页配置
    list_display: list[str] = [
        "id",
        "name",
        "subject",
        "difficulty_display",
        "question_count",
        "created_at",
    ]
    
    list_filter: list[str] = [
        "subject",
        "difficulty_level",
    ]
    
    search_fields: list[str] = [
        "name",
        "description",
        "subject",
    ]
    
    list_per_page: int = 20
    ordering: list[str] = ["subject", "difficulty_level", "name"]
    date_hierarchy: str = "created_at"
    
    # 详情页配置
    fieldsets: tuple = (
        ("基本信息", {
            "fields": (
                "name",
                "description",
                "subject",
                "difficulty_level",
            ),
        }),
        ("关联信息", {
            "fields": (
                "questions",
            ),
        }),
        ("元数据", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )
    
    readonly_fields: list[str] = [
        "created_at",
        "updated_at",
    ]
    
    filter_horizontal: list[str] = ["questions"]
    
    def difficulty_display(self, obj: KnowledgePoint) -> str:
        """显示难度等级的中文名称。"""
        difficulty_map = {
            1: "非常简单",
            2: "简单",
            3: "中等",
            4: "困难",
            5: "非常困难",
        }
        return difficulty_map.get(obj.difficulty_level, str(obj.difficulty_level))
    
    difficulty_display.short_description = "难度等级"
    difficulty_display.admin_order_field = "difficulty_level"
    
    def question_count(self, obj: KnowledgePoint) -> int:
        """显示关联的题目数量。"""
        return obj.questions.count()
    
    question_count.short_description = "关联题目数"
    
    def save_model(self, request: HttpRequest, obj: KnowledgePoint, form: Any, change: bool) -> None:
        """保存知识点模型时的自定义逻辑。"""
        super().save_model(request, obj, form, change)
        
        _LOGGER.info(
            "知识点%s保存成功: %s (ID: %s)",
            "更新" if change else "创建",
            obj.name,
            obj.id,
        )
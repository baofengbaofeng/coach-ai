"""
运动管理后台配置模块，定义Django管理后台的界面和功能。
按照豆包AI助手最佳实践：使用Django Admin进行数据管理。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.exercise.models import ExerciseAnalysis, ExercisePlan, ExerciseRecord
from core.constants import ExerciseType


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 运动记录管理 ====================
@admin.register(ExerciseRecord)
class ExerciseRecordAdmin(admin.ModelAdmin):
    """
    运动记录管理类，配置运动记录在Django Admin中的显示和操作。
    """
    
    # 列表页显示字段
    list_display = [
        "id",
        "title",
        "user",
        "get_exercise_type_display",
        "duration_seconds",
        "calories_burned",
        "repetitions",
        "started_at",
        "ended_at",
        "is_completed_display",
        "created_at",
    ]
    
    # 列表页可点击字段
    list_display_links = ["id", "title"]
    
    # 列表页过滤条件
    list_filter = [
        "exercise_type",
        "started_at",
        "ended_at",
        "created_at",
    ]
    
    # 搜索字段
    search_fields = [
        "title",
        "description",
        "user__username",
        "user__email",
        "location_name",
    ]
    
    # 分页设置
    list_per_page = 50
    
    # 字段分组显示
    fieldsets = (
        (_("基础信息"), {
            "fields": (
                "title",
                "description",
                "user",
                "exercise_type",
            ),
        }),
        (_("运动数据"), {
            "fields": (
                "duration_seconds",
                "repetitions",
                "calories_burned",
                "heart_rate_avg",
                "heart_rate_max",
            ),
        }),
        (_("文件信息"), {
            "fields": ("video_file",),
            "classes": ("collapse",),
        }),
        (_("位置信息"), {
            "fields": (
                "latitude",
                "longitude",
                "location_name",
            ),
            "classes": ("collapse",),
        }),
        (_("时间信息"), {
            "fields": (
                "started_at",
                "ended_at",
            ),
        }),
        (_("元数据"), {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )
    
    # 只读字段
    readonly_fields = ["created_at", "updated_at"]
    
    # 自定义动作
    actions = [
        "mark_as_completed",
        "calculate_calories",
        "export_selected",
    ]
    
    def is_completed_display(self, obj: ExerciseRecord) -> str:
        """显示是否完成。"""
        return _("已完成") if obj.is_completed() else _("进行中")
    
    is_completed_display.short_description = _("完成状态")
    is_completed_display.admin_order_field = "ended_at"
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[ExerciseRecord]:
        """获取查询集，优化查询性能。"""
        queryset = super().get_queryset(request)
        return queryset.select_related("user")
    
    def get_form(self, request: HttpRequest, obj: Optional[ExerciseRecord] = None, **kwargs: Any) -> Any:
        """获取表单，动态设置字段。"""
        form = super().get_form(request, obj, **kwargs)
        
        # 如果是编辑现有记录，将用户字段设为只读
        if obj and obj.pk:
            form.base_fields["user"].disabled = True
        
        return form
    
    def save_model(self, request: HttpRequest, obj: ExerciseRecord, form: Any, change: bool) -> None:
        """保存模型前的处理。"""
        if not change:  # 新建记录
            _LOGGER.info(
                "管理员创建运动记录: %s (用户: %s)",
                obj.title,
                obj.user.username,
            )
        else:  # 更新记录
            _LOGGER.info(
                "管理员更新运动记录: %s (ID: %s)",
                obj.title,
                obj.id,
            )
        
        super().save_model(request, obj, form, change)
    
    @admin.action(description=_("标记为已完成"))
    def mark_as_completed(self, request: HttpRequest, queryset: QuerySet[ExerciseRecord]) -> None:
        """批量标记运动记录为已完成。"""
        updated_count = 0
        
        for record in queryset:
            if not record.is_completed():
                record.ended_at = timezone.now()
                record.save()
                updated_count += 1
        
        self.message_user(
            request,
            _("成功标记 %(count)d 条记录为已完成") % {"count": updated_count},
            messages.SUCCESS,
        )
        
        _LOGGER.info("管理员批量标记运动记录完成: %s 条", updated_count)
    
    @admin.action(description=_("重新计算卡路里"))
    def calculate_calories(self, request: HttpRequest, queryset: QuerySet[ExerciseRecord]) -> None:
        """批量重新计算卡路里（示例功能）。"""
        updated_count = 0
        
        for record in queryset:
            # 示例：根据运动类型和时长估算卡路里
            if record.exercise_type == ExerciseType.RUNNING:
                # 跑步：每公斤体重每分钟消耗0.1千卡（假设体重60kg）
                weight_kg = 60
                calories = weight_kg * 0.1 * (record.duration_seconds / 60)
                record.calories_burned = calories
                record.save()
                updated_count += 1
        
        self.message_user(
            request,
            _("成功重新计算 %(count)d 条记录的卡路里") % {"count": updated_count},
            messages.SUCCESS,
        )
        
        _LOGGER.info("管理员批量重新计算卡路里: %s 条", updated_count)
    
    @admin.action(description=_("导出选中记录"))
    def export_selected(self, request: HttpRequest, queryset: QuerySet[ExerciseRecord]) -> None:
        """导出选中的运动记录（示例功能）。"""
        count = queryset.count()
        
        # 这里可以添加实际的导出逻辑
        # 例如：生成CSV、Excel或PDF文件
        
        self.message_user(
            request,
            _("准备导出 %(count)d 条记录") % {"count": count},
            messages.INFO,
        )
        
        _LOGGER.info("管理员准备导出运动记录: %s 条", count)


# ==================== 运动计划管理 ====================
@admin.register(ExercisePlan)
class ExercisePlanAdmin(admin.ModelAdmin):
    """
    运动计划管理类，配置运动计划在Django Admin中的显示和操作。
    """
    
    # 列表页显示字段
    list_display = [
        "id",
        "name",
        "user",
        "target_duration_minutes",
        "frequency_per_week",
        "start_date",
        "end_date",
        "is_active_display",
        "completed_count",
        "success_rate_display",
        "created_at",
    ]
    
    # 列表页可点击字段
    list_display_links = ["id", "name"]
    
    # 列表页过滤条件
    list_filter = [
        "is_active",
        "start_date",
        "end_date",
        "created_at",
    ]
    
    # 搜索字段
    search_fields = [
        "name",
        "description",
        "user__username",
        "user__email",
    ]
    
    # 分页设置
    list_per_page = 50
    
    # 字段分组显示
    fieldsets = (
        (_("基础信息"), {
            "fields": (
                "name",
                "description",
                "user",
            ),
        }),
        (_("计划设置"), {
            "fields": (
                "target_duration_minutes",
                "target_repetitions",
                "target_calories",
                "frequency_per_week",
            ),
        }),
        (_("时间设置"), {
            "fields": (
                "start_date",
                "end_date",
                "preferred_time",
            ),
        }),
        (_("状态信息"), {
            "fields": (
                "is_active",
                "completed_count",
                "success_rate",
            ),
        }),
        (_("元数据"), {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )
    
    # 只读字段
    readonly_fields = ["created_at", "updated_at", "success_rate"]
    
    # 自定义动作
    actions = [
        "activate_plans",
        "deactivate_plans",
        "reset_progress",
    ]
    
    def is_active_display(self, obj: ExercisePlan) -> str:
        """显示激活状态。"""
        return _("激活") if obj.is_active else _("停用")
    
    is_active_display.short_description = _("状态")
    is_active_display.admin_order_field = "is_active"
    
    def success_rate_display(self, obj: ExercisePlan) -> str:
        """显示完成率。"""
        return f"{obj.success_rate:.1f}%"
    
    success_rate_display.short_description = _("完成率")
    success_rate_display.admin_order_field = "success_rate"
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[ExercisePlan]:
        """获取查询集，优化查询性能。"""
        queryset = super().get_queryset(request)
        return queryset.select_related("user")
    
    @admin.action(description=_("激活选中计划"))
    def activate_plans(self, request: HttpRequest, queryset: QuerySet[ExercisePlan]) -> None:
        """批量激活运动计划。"""
        updated_count = queryset.filter(is_active=False).update(is_active=True)
        
        self.message_user(
            request,
            _("成功激活 %(count)d 个计划") % {"count": updated_count},
            messages.SUCCESS,
        )
        
        _LOGGER.info("管理员批量激活运动计划: %s 个", updated_count)
    
    @admin.action(description=_("停用选中计划"))
    def deactivate_plans(self, request: HttpRequest, queryset: QuerySet[ExercisePlan]) -> None:
        """批量停用运动计划。"""
        updated_count = queryset.filter(is_active=True).update(is_active=False)
        
        self.message_user(
            request,
            _("成功停用 %(count)d 个计划") % {"count": updated_count},
            messages.SUCCESS,
        )
        
        _LOGGER.info("管理员批量停用运动计划: %s 个", updated_count)
    
    @admin.action(description=_("重置进度"))
    def reset_progress(self, request: HttpRequest, queryset: QuerySet[ExercisePlan]) -> None:
        """批量重置运动计划进度。"""
        updated_count = 0
        
        for plan in queryset:
            plan.completed_count = 0
            plan.success_rate = 0
            plan.save()
            updated_count += 1
        
        self.message_user(
            request,
            _("成功重置 %(count)d 个计划的进度") % {"count": updated_count},
            messages.SUCCESS,
        )
        
        _LOGGER.info("管理员批量重置运动计划进度: %s 个", updated_count)


# ==================== 运动分析管理 ====================
@admin.register(ExerciseAnalysis)
class ExerciseAnalysisAdmin(admin.ModelAdmin):
    """
    运动分析管理类，配置运动分析在Django Admin中的显示和操作。
    """
    
    # 列表页显示字段
    list_display = [
        "id",
        "user",
        "get_analysis_period_display",
        "period_start",
        "period_end",
        "exercise_count",
        "total_duration_minutes",
        "total_calories",
        "health_score_display",
        "created_at",
    ]
    
    # 列表页可点击字段
    list_display_links = ["id", "user"]
    
    # 列表页过滤条件
    list_filter = [
        "analysis_period",
        "period_start",
        "period_end",
        "created_at",
    ]
    
    # 搜索字段
    search_fields = [
        "user__username",
        "user__email",
        "strengths",
        "weaknesses",
        "recommendations",
    ]
    
    # 分页设置
    list_per_page = 50
    
    # 字段分组显示
    fieldsets = (
        (_("基础信息"), {
            "fields": (
                "user",
                "analysis_period",
                "period_start",
                "period_end",
            ),
        }),
        (_("统计指标"), {
            "fields": (
                "total_duration_minutes",
                "total_calories",
                "total_repetitions",
                "exercise_count",
            ),
        }),
        (_("分析结果"), {
            "fields": (
                "average_duration_minutes",
                "average_calories",
                "consistency_rate",
                "improvement_rate",
            ),
        }),
        (_("分析报告"), {
            "fields": (
                "strengths",
                "weaknesses",
                "recommendations",
            ),
        }),
        (_("元数据"), {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )
    
    # 只读字段
    readonly_fields = [
        "created_at",
        "updated_at",
        "average_duration_minutes",
        "average_calories",
    ]
    
    # 自定义动作
    actions = [
        "regenerate_analysis",
        "export_analysis_reports",
    ]
    
    def health_score_display(self, obj: ExerciseAnalysis) -> str:
        """显示健康评分。"""
        score = obj.get_health_score()
        if score >= 90:
            color = "green"
            label = _("卓越")
        elif score >= 80:
            color = "blue"
            label = _("优秀")
        elif score >= 60:
            color = "orange"
            label = _("良好")
        else:
            color = "red"
            label = _("需改进")
        
        return f'<span style="color: {color}; font-weight: bold;">{score:.1f} ({label})</span>'
    
    health_score_display.short_description = _("健康评分")
    health_score_display.admin_order_field = "health_score"
    health_score_display.allow_tags = True
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[ExerciseAnalysis]:
        """获取查询集，优化查询性能。"""
        queryset = super().get_queryset(request)
        return queryset.select_related("user")
    
    @admin.action(description=_("重新生成分析"))
    def regenerate_analysis(self, request: HttpRequest, queryset: QuerySet[ExerciseAnalysis]) -> None:
        """批量重新生成运动分析。"""
        updated_count = 0
        
        for analysis in queryset:
            # 重新计算平均值
            if analysis.exercise_count > 0:
                analysis.average_duration_minutes = analysis.total_duration_minutes / analysis.exercise_count
                analysis.average_calories = analysis.total_calories / analysis.exercise_count
                analysis.save()
                updated_count += 1
        
        self.message_user(
            request,
            _("成功重新生成 %(count)d 个分析") % {"count": updated_count},
            messages.SUCCESS,
        )
        
        _LOGGER.info("管理员批量重新生成运动分析: %s 个", updated_count)
    
    @admin.action(description=_("导出分析报告"))
    def export_analysis_reports(self, request: HttpRequest, queryset: QuerySet[ExerciseAnalysis]) -> None:
        """导出运动分析报告（示例功能）。"""
        count = queryset.count()
        
        # 这里可以添加实际的导出逻辑
        # 例如：生成PDF报告或Excel文件
        
        self.message_user(
            request,
            _("准备导出 %(count)d 个分析报告") % {"count": count},
            messages.INFO,
        )
        
        _LOGGER.info("管理员准备导出运动分析报告: %s 个", count)
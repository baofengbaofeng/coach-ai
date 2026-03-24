"""
成就系统管理界面配置模块，配置Django Admin后台管理界面。
按照豆包AI助手最佳实践：使用Django Admin进行数据管理。
"""
from __future__ import annotations

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg
from django.utils.html import format_html
from django.utils import timezone

from apps.achievements.models import (
    Achievement,
    AchievementCategory,
    AchievementReward,
    AchievementStatistic,
    UserAchievement,
)


# ==================== 用户模型引用 ====================
User = get_user_model()


# ==================== 内联管理类 ====================
class AchievementRewardInline(admin.TabularInline):
    """
    成就奖励内联管理类。
    """
    
    model = AchievementReward
    extra = 0
    fields = ["reward_type", "reward_value", "is_limited", "limit_count", "claimed_count"]
    readonly_fields = ["claimed_count"]


class UserAchievementInline(admin.TabularInline):
    """
    用户成就内联管理类。
    """
    
    model = UserAchievement
    extra = 0
    fields = ["user", "current_value", "progress_percentage", "is_unlocked", "unlocked_at"]
    readonly_fields = ["progress_percentage", "unlocked_at"]
    show_change_link = True
    
    def get_queryset(self, request):
        """优化查询集。"""
        return super().get_queryset(request).select_related("user")


# ==================== 管理类装饰器 ====================
@admin.register(AchievementCategory)
class AchievementCategoryAdmin(admin.ModelAdmin):
    """
    成就分类管理类。
    """
    
    list_display = [
        "name",
        "achievement_count",
        "is_active",
        "order",
        "created_at",
    ]
    
    list_filter = [
        "is_active",
        "created_at",
    ]
    
    search_fields = [
        "name",
        "description",
    ]
    
    fieldsets = (
        ("基本信息", {
            "fields": [
                "name",
                "description",
                "icon",
                "color",
            ]
        }),
        ("显示设置", {
            "fields": [
                "order",
                "is_active",
            ]
        }),
        ("时间信息", {
            "fields": [
                "created_at",
                "updated_at",
            ],
            "classes": ["collapse"],
        }),
    )
    
    readonly_fields = [
        "created_at",
        "updated_at",
        "achievement_count",
    ]
    
    ordering = ["order", "name"]
    
    def get_queryset(self, request):
        """优化查询集。"""
        return super().get_queryset(request).annotate(
            achievement_count=Count("achievements")
        )
    
    def achievement_count(self, obj):
        """显示成就数量。"""
        return obj.achievement_count
    achievement_count.short_description = "成就数量"
    achievement_count.admin_order_field = "achievement_count"


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """
    成就管理类。
    """
    
    list_display = [
        "name",
        "category",
        "achievement_type_display",
        "difficulty_display",
        "unlocked_count_display",
        "unlock_rate_display",
        "reward_points",
        "is_active",
        "display_order",
    ]
    
    list_filter = [
        "category",
        "achievement_type",
        "difficulty",
        "is_active",
        "is_secret",
        "created_at",
    ]
    
    search_fields = [
        "name",
        "description",
        "condition_type",
    ]
    
    fieldsets = (
        ("基本信息", {
            "fields": [
                "name",
                "description",
                "category",
            ]
        }),
        ("成就设置", {
            "fields": [
                "achievement_type",
                "difficulty",
                "icon",
                "badge_image",
            ]
        }),
        ("成就条件", {
            "fields": [
                "condition_type",
                "condition_value",
                "condition_operator",
                "time_limit_days",
            ]
        }),
        ("奖励设置", {
            "fields": [
                "reward_points",
                "reward_badge",
                "reward_message",
            ]
        }),
        ("显示设置", {
            "fields": [
                "display_order",
                "is_secret",
                "is_active",
            ]
        }),
        ("统计信息", {
            "fields": [
                "unlocked_count",
                "unlock_rate",
            ],
            "classes": ["collapse"],
        }),
        ("时间信息", {
            "fields": [
                "created_at",
                "updated_at",
            ],
            "classes": ["collapse"],
        }),
    )
    
    readonly_fields = [
        "unlocked_count",
        "unlock_rate",
        "created_at",
        "updated_at",
    ]
    
    inlines = [AchievementRewardInline, UserAchievementInline]
    
    ordering = ["display_order", "name"]
    
    def get_queryset(self, request):
        """优化查询集。"""
        return super().get_queryset(request).select_related("category")
    
    def achievement_type_display(self, obj):
        """显示成就类型。"""
        return obj.get_achievement_type_display()
    achievement_type_display.short_description = "类型"
    achievement_type_display.admin_order_field = "achievement_type"
    
    def difficulty_display(self, obj):
        """显示难度等级。"""
        return obj.get_difficulty_display()
    difficulty_display.short_description = "难度"
    difficulty_display.admin_order_field = "difficulty"
    
    def unlocked_count_display(self, obj):
        """显示解锁数量。"""
        return f"{obj.unlocked_count}人"
    unlocked_count_display.short_description = "解锁人数"
    unlocked_count_display.admin_order_field = "unlocked_count"
    
    def unlock_rate_display(self, obj):
        """显示解锁率。"""
        return f"{obj.unlock_rate:.1f}%"
    unlock_rate_display.short_description = "解锁率"
    unlock_rate_display.admin_order_field = "unlock_rate"


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    """
    用户成就管理类。
    """
    
    list_display = [
        "user",
        "achievement",
        "progress_bar",
        "is_unlocked_display",
        "is_reward_claimed_display",
        "started_at",
        "unlocked_at",
    ]
    
    list_filter = [
        "is_unlocked",
        "is_reward_claimed",
        "achievement__category",
        "achievement__difficulty",
        "started_at",
        "unlocked_at",
    ]
    
    search_fields = [
        "user__username",
        "user__email",
        "achievement__name",
    ]
    
    fieldsets = (
        ("基本信息", {
            "fields": [
                "user",
                "achievement",
            ]
        }),
        ("进度信息", {
            "fields": [
                "current_value",
                "progress_percentage",
                "metadata",
            ]
        }),
        ("解锁状态", {
            "fields": [
                "is_unlocked",
                "unlocked_at",
            ]
        }),
        ("奖励状态", {
            "fields": [
                "is_reward_claimed",
                "reward_claimed_at",
            ]
        }),
        ("时间信息", {
            "fields": [
                "started_at",
                "last_updated_at",
            ],
            "classes": ["collapse"],
        }),
    )
    
    readonly_fields = [
        "progress_percentage",
        "unlocked_at",
        "reward_claimed_at",
        "started_at",
        "last_updated_at",
        "time_to_unlock",
        "days_since_started",
    ]
    
    ordering = ["-last_updated_at"]
    
    def get_queryset(self, request):
        """优化查询集。"""
        return super().get_queryset(request).select_related("user", "achievement")
    
    def progress_bar(self, obj):
        """显示进度条。"""
        color = "green" if obj.is_unlocked else "blue"
        return format_html(
            '<div style="width: 100px; background-color: #eee; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; '
            'text-align: center; color: white; line-height: 20px;">{}%</div>'
            '</div>',
            obj.progress_percentage, color, obj.progress_percentage
        )
    progress_bar.short_description = "进度"
    
    def is_unlocked_display(self, obj):
        """显示解锁状态。"""
        if obj.is_unlocked:
            return format_html(
                '<span style="color: green;">✓ 已解锁</span>'
            )
        return format_html(
            '<span style="color: orange;">● 进行中</span>'
        )
    is_unlocked_display.short_description = "解锁状态"
    
    def is_reward_claimed_display(self, obj):
        """显示奖励领取状态。"""
        if not obj.is_unlocked:
            return format_html(
                '<span style="color: gray;">-</span>'
            )
        if obj.is_reward_claimed:
            return format_html(
                '<span style="color: green;">✓ 已领取</span>'
            )
        return format_html(
            '<span style="color: blue;">● 待领取</span>'
        )
    is_reward_claimed_display.short_description = "奖励状态"
    
    def time_to_unlock(self, obj):
        """显示解锁所需时间。"""
        if obj.time_to_unlock:
            if obj.time_to_unlock < 60:
                return f"{obj.time_to_unlock:.0f}秒"
            elif obj.time_to_unlock < 3600:
                return f"{obj.time_to_unlock / 60:.1f}分钟"
            elif obj.time_to_unlock < 86400:
                return f"{obj.time_to_unlock / 3600:.1f}小时"
            else:
                return f"{obj.time_to_unlock / 86400:.1f}天"
        return "-"
    time_to_unlock.short_description = "解锁时间"


@admin.register(AchievementReward)
class AchievementRewardAdmin(admin.ModelAdmin):
    """
    成就奖励管理类。
    """
    
    list_display = [
        "achievement",
        "reward_type",
        "reward_value",
        "is_limited_display",
        "claimed_count_display",
        "can_claim_display",
        "created_at",
    ]
    
    list_filter = [
        "reward_type",
        "is_limited",
        "created_at",
    ]
    
    search_fields = [
        "achievement__name",
        "reward_value",
        "reward_description",
    ]
    
    fieldsets = (
        ("基本信息", {
            "fields": [
                "achievement",
            ]
        }),
        ("奖励内容", {
            "fields": [
                "reward_type",
                "reward_value",
                "reward_description",
            ]
        }),
        ("奖励限制", {
            "fields": [
                "is_limited",
                "limit_count",
                "limit_expires_at",
            ]
        }),
        ("统计信息", {
            "fields": [
                "claimed_count",
            ],
            "classes": ["collapse"],
        }),
        ("时间信息", {
            "fields": [
                "created_at",
                "updated_at",
            ],
            "classes": ["collapse"],
        }),
    )
    
    readonly_fields = [
        "claimed_count",
        "created_at",
        "updated_at",
    ]
    
    ordering = ["-created_at"]
    
    def get_queryset(self, request):
        """优化查询集。"""
        return super().get_queryset(request).select_related("achievement")
    
    def is_limited_display(self, obj):
        """显示限制状态。"""
        if obj.is_limited:
            if obj.limit_expires_at and timezone.now() > obj.limit_expires_at:
                return format_html(
                    '<span style="color: red;">已过期</span>'
                )
            if obj.limit_count > 0:
                remaining = obj.limit_count - obj.claimed_count
                return format_html(
                    f'<span style="color: orange;">限量 ({remaining}/{obj.limit_count})</span>'
                )
            return format_html(
                '<span style="color: blue;">时间限制</span>'
            )
        return format_html(
            '<span style="color: green;">无限量</span>'
        )
    is_limited_display.short_description = "限制状态"
    
    def claimed_count_display(self, obj):
        """显示领取数量。"""
        return f"{obj.claimed_count}次"
    claimed_count_display.short_description = "领取次数"
    
    def can_claim_display(self, obj):
        """显示是否可以领取。"""
        if obj.can_claim():
            return format_html(
                '<span style="color: green;">可领取</span>'
            )
        return format_html(
            '<span style="color: red;">不可领取</span>'
        )
    can_claim_display.short_description = "领取状态"


@admin.register(AchievementStatistic)
class AchievementStatisticAdmin(admin.ModelAdmin):
    """
    成就统计管理类。
    """
    
    list_display = [
        "statistic_type_display",
        "statistic_date",
        "total_count",
        "average_value",
        "created_at",
    ]
    
    list_filter = [
        "statistic_type",
        "statistic_date",
    ]
    
    search_fields = [
        "statistic_type",
    ]
    
    fieldsets = (
        ("基本信息", {
            "fields": [
                "statistic_type",
                "statistic_date",
            ]
        }),
        ("统计数据", {
            "fields": [
                "data",
            ]
        }),
        ("汇总信息", {
            "fields": [
                "total_count",
                "average_value",
                "max_value",
                "min_value",
            ]
        }),
        ("时间信息", {
            "fields": [
                "created_at",
                "updated_at",
            ],
            "classes": ["collapse"],
        }),
    )
    
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    
    ordering = ["-statistic_date", "statistic_type"]
    
    def statistic_type_display(self, obj):
        """显示统计类型。"""
        return obj.get_statistic_type_display()
    statistic_type_display.short_description = "统计类型"
    statistic_type_display.admin_order_field = "statistic_type"


# ==================== 管理站点配置 ====================
class AchievementAdminSite(admin.AdminSite):
    """
    成就系统管理站点配置。
    """
    
    site_header = "CoachAI 成就系统管理"
    site_title = "成就系统管理"
    index_title = "成就系统管理"


# 创建成就系统管理站点实例
achievement_admin_site = AchievementAdminSite(name="achievements_admin")
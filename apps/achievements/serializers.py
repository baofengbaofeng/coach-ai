"""
成就系统序列化器模块，定义成就、用户成就进度、成就分类和奖励等数据的序列化和反序列化逻辑。
按照豆包AI助手最佳实践：使用Django REST Framework序列化器。
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.achievements.models import (
    Achievement,
    AchievementCategory,
    AchievementReward,
    AchievementStatistic,
    UserAchievement,
)
from core.constants import BusinessRules


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 成就分类序列化器 ====================
class AchievementCategorySerializer(serializers.ModelSerializer):
    """
    成就分类序列化器类，用于成就分类的序列化和反序列化。
    """
    
    achievement_count_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        """成就分类序列化器的元数据配置。"""
        
        model = AchievementCategory
        fields = [
            "id",
            "name",
            "description",
            "icon",
            "color",
            "order",
            "is_active",
            "achievement_count",
            "achievement_count_display",
            "status_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "achievement_count",
            "achievement_count_display",
            "status_display",
            "created_at",
            "updated_at",
        ]
    
    def get_achievement_count_display(self, obj: AchievementCategory) -> str:
        """获取成就数量显示文本。"""
        count: int = obj.achievement_count
        return f"{count}个成就"
    
    def get_status_display(self, obj: AchievementCategory) -> str:
        """获取状态显示文本。"""
        return "激活" if obj.is_active else "停用"
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证成就分类数据。"""
        # 验证颜色格式
        if "color" in data and data["color"]:
            color: str = data["color"]
            if not color.startswith("#") or len(color) not in [4, 7]:
                raise serializers.ValidationError({
                    "color": "颜色格式不正确，应为#RGB或#RRGGBB格式"
                })
        
        return data


# ==================== 成就序列化器 ====================
class AchievementSerializer(serializers.ModelSerializer):
    """
    成就序列化器类，用于成就的序列化和反序列化。
    """
    
    category_display = serializers.SerializerMethodField()
    achievement_type_display = serializers.SerializerMethodField()
    difficulty_display = serializers.SerializerMethodField()
    unlocked_count_display = serializers.SerializerMethodField()
    unlock_rate_display = serializers.SerializerMethodField()
    
    class Meta:
        """成就序列化器的元数据配置。"""
        
        model = Achievement
        fields = [
            "id",
            "name",
            "description",
            "category",
            "category_display",
            "achievement_type",
            "achievement_type_display",
            "difficulty",
            "difficulty_display",
            "icon",
            "badge_image",
            "condition_type",
            "condition_value",
            "condition_operator",
            "time_limit_days",
            "reward_points",
            "reward_badge",
            "reward_message",
            "display_order",
            "is_secret",
            "is_active",
            "unlocked_count",
            "unlocked_count_display",
            "unlock_rate",
            "unlock_rate_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "unlocked_count",
            "unlocked_count_display",
            "unlock_rate",
            "unlock_rate_display",
            "created_at",
            "updated_at",
        ]
    
    def get_category_display(self, obj: Achievement) -> str:
        """获取分类显示文本。"""
        return obj.category.name if obj.category else "未分类"
    
    def get_achievement_type_display(self, obj: Achievement) -> str:
        """获取成就类型显示文本。"""
        return obj.get_achievement_type_display()
    
    def get_difficulty_display(self, obj: Achievement) -> str:
        """获取难度显示文本。"""
        return obj.get_difficulty_display()
    
    def get_unlocked_count_display(self, obj: Achievement) -> str:
        """获取解锁数量显示文本。"""
        return f"{obj.unlocked_count}人已解锁"
    
    def get_unlock_rate_display(self, obj: Achievement) -> str:
        """获取解锁率显示文本。"""
        return f"{obj.unlock_rate:.1f}%"
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证成就数据。"""
        # 验证条件值
        if "condition_value" in data and data["condition_value"] <= 0:
            raise serializers.ValidationError({
                "condition_value": "条件值必须大于0"
            })
        
        # 验证时间限制
        if "time_limit_days" in data and data["time_limit_days"] < 0:
            raise serializers.ValidationError({
                "time_limit_days": "时间限制不能为负数"
            })
        
        # 验证奖励积分
        if "reward_points" in data and data["reward_points"] < 0:
            raise serializers.ValidationError({
                "reward_points": "奖励积分不能为负数"
            })
        
        return data


# ==================== 成就创建序列化器 ====================
class AchievementCreateSerializer(serializers.ModelSerializer):
    """
    成就创建序列化器类，用于创建成就时的序列化和反序列化。
    """
    
    class Meta:
        """成就创建序列化器的元数据配置。"""
        
        model = Achievement
        fields = [
            "name",
            "description",
            "category",
            "achievement_type",
            "difficulty",
            "icon",
            "badge_image",
            "condition_type",
            "condition_value",
            "condition_operator",
            "time_limit_days",
            "reward_points",
            "reward_badge",
            "reward_message",
            "display_order",
            "is_secret",
            "is_active",
        ]
    
    def create(self, validated_data: Dict[str, Any]) -> Achievement:
        """创建成就。"""
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            _LOGGER.info(
                "用户 %s 创建成就: %s",
                request.user.username, validated_data["name"]
            )
        
        return super().create(validated_data)


# ==================== 用户成就序列化器 ====================
class UserAchievementSerializer(serializers.ModelSerializer):
    """
    用户成就序列化器类，用于用户成就进度的序列化和反序列化。
    """
    
    achievement_details = serializers.SerializerMethodField()
    user_display = serializers.SerializerMethodField()
    progress_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    time_to_unlock_display = serializers.SerializerMethodField()
    
    class Meta:
        """用户成就序列化器的元数据配置。"""
        
        model = UserAchievement
        fields = [
            "id",
            "user",
            "user_display",
            "achievement",
            "achievement_details",
            "current_value",
            "progress_percentage",
            "progress_display",
            "is_unlocked",
            "status_display",
            "unlocked_at",
            "is_reward_claimed",
            "reward_claimed_at",
            "started_at",
            "last_updated_at",
            "metadata",
            "time_to_unlock",
            "time_to_unlock_display",
            "days_since_started",
        ]
        read_only_fields = [
            "id",
            "user_display",
            "achievement_details",
            "progress_percentage",
            "progress_display",
            "status_display",
            "unlocked_at",
            "reward_claimed_at",
            "started_at",
            "last_updated_at",
            "time_to_unlock",
            "time_to_unlock_display",
            "days_since_started",
        ]
    
    def get_achievement_details(self, obj: UserAchievement) -> Dict[str, Any]:
        """获取成就详细信息。"""
        return {
            "name": obj.achievement.name,
            "description": obj.achievement.description,
            "difficulty": obj.achievement.get_difficulty_display(),
            "condition_type": obj.achievement.condition_type,
            "condition_value": str(obj.achievement.condition_value),
            "condition_operator": obj.achievement.condition_operator,
            "reward_points": obj.achievement.reward_points,
        }
    
    def get_user_display(self, obj: UserAchievement) -> str:
        """获取用户显示文本。"""
        return obj.user.username
    
    def get_progress_display(self, obj: UserAchievement) -> str:
        """获取进度显示文本。"""
        return f"{obj.progress_percentage}%"
    
    def get_status_display(self, obj: UserAchievement) -> str:
        """获取状态显示文本。"""
        if obj.is_unlocked:
            if obj.is_reward_claimed:
                return "奖励已领取"
            return "已解锁"
        return "进行中"
    
    def get_time_to_unlock_display(self, obj: UserAchievement) -> Optional[str]:
        """获取解锁时间显示文本。"""
        if obj.time_to_unlock:
            if obj.time_to_unlock < 60:
                return f"{obj.time_to_unlock:.0f}秒"
            elif obj.time_to_unlock < 3600:
                return f"{obj.time_to_unlock / 60:.1f}分钟"
            elif obj.time_to_unlock < 86400:
                return f"{obj.time_to_unlock / 3600:.1f}小时"
            else:
                return f"{obj.time_to_unlock / 86400:.1f}天"
        return None
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证用户成就数据。"""
        # 验证当前值
        if "current_value" in data and data["current_value"] < 0:
            raise serializers.ValidationError({
                "current_value": "当前值不能为负数"
            })
        
        return data


# ==================== 用户成就进度更新序列化器 ====================
class UserAchievementProgressSerializer(serializers.Serializer):
    """
    用户成就进度更新序列化器类，用于更新用户成就进度。
    """
    
    current_value = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="新的当前进度值",
    )
    
    metadata = serializers.DictField(
        required=False,
        allow_null=True,
        help_text="额外的进度数据",
    )
    
    def validate_current_value(self, value: Decimal) -> Decimal:
        """验证当前值。"""
        if value < 0:
            raise serializers.ValidationError("当前值不能为负数")
        return value


# ==================== 成就奖励序列化器 ====================
class AchievementRewardSerializer(serializers.ModelSerializer):
    """
    成就奖励序列化器类，用于成就奖励的序列化和反序列化。
    """
    
    achievement_display = serializers.SerializerMethodField()
    can_claim_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        """成就奖励序列化器的元数据配置。"""
        
        model = AchievementReward
        fields = [
            "id",
            "achievement",
            "achievement_display",
            "reward_type",
            "reward_value",
            "reward_description",
            "is_limited",
            "limit_count",
            "limit_expires_at",
            "claimed_count",
            "can_claim",
            "can_claim_display",
            "status_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "achievement_display",
            "can_claim",
            "can_claim_display",
            "status_display",
            "claimed_count",
            "created_at",
            "updated_at",
        ]
    
    def get_achievement_display(self, obj: AchievementReward) -> str:
        """获取成就显示文本。"""
        return obj.achievement.name
    
    def get_can_claim_display(self, obj: AchievementReward) -> str:
        """获取是否可以领取显示文本。"""
        return "可领取" if obj.can_claim() else "不可领取"
    
    def get_status_display(self, obj: AchievementReward) -> str:
        """获取状态显示文本。"""
        if obj.is_limited:
            if obj.limit_expires_at and timezone.now() > obj.limit_expires_at:
                return "已过期"
            if obj.limit_count > 0 and obj.claimed_count >= obj.limit_count:
                return "已领完"
            return f"剩余{obj.limit_count - obj.claimed_count}个"
        return "无限量"
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证成就奖励数据。"""
        # 验证限制数量
        if "is_limited" in data and data["is_limited"]:
            if "limit_count" not in data or data["limit_count"] <= 0:
                raise serializers.ValidationError({
                    "limit_count": "限制数量必须大于0"
                })
        
        # 验证过期时间
        if "limit_expires_at" in data and data["limit_expires_at"]:
            if data["limit_expires_at"] <= timezone.now():
                raise serializers.ValidationError({
                    "limit_expires_at": "过期时间必须晚于当前时间"
                })
        
        return data


# ==================== 成就统计序列化器 ====================
class AchievementStatisticSerializer(serializers.ModelSerializer):
    """
    成就统计序列化器类，用于成就统计数据的序列化和反序列化。
    """
    
    statistic_type_display = serializers.SerializerMethodField()
    date_display = serializers.SerializerMethodField()
    
    class Meta:
        """成就统计序列化器的元数据配置。"""
        
        model = AchievementStatistic
        fields = [
            "id",
            "statistic_type",
            "statistic_type_display",
            "statistic_date",
            "date_display",
            "data",
            "total_count",
            "average_value",
            "max_value",
            "min_value",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "statistic_type_display",
            "date_display",
            "created_at",
            "updated_at",
        ]
    
    def get_statistic_type_display(self, obj: AchievementStatistic) -> str:
        """获取统计类型显示文本。"""
        return obj.get_statistic_type_display()
    
    def get_date_display(self, obj: AchievementStatistic) -> str:
        """获取日期显示文本。"""
        return obj.statistic_date.strftime("%Y年%m月%d日")
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证成就统计数据。"""
        # 验证统计日期
        if "statistic_date" in data and data["statistic_date"] > timezone.now().date():
            raise serializers.ValidationError({
                "statistic_date": "统计日期不能晚于今天"
            })
        
        # 验证统计值
        for field in ["total_count", "average_value", "max_value", "min_value"]:
            if field in data and data[field] < 0:
                raise serializers.ValidationError({
                    field: f"{field}不能为负数"
                })
        
        return data


# ==================== 用户成就统计序列化器 ====================
class UserAchievementStatisticsSerializer(serializers.Serializer):
    """
    用户成就统计序列化器类，用于用户成就统计数据的序列化。
    """
    
    total_achievements = serializers.IntegerField(
        help_text="总成就数量",
    )
    
    unlocked_achievements = serializers.IntegerField(
        help_text="已解锁成就数量",
    )
    
    in_progress_achievements = serializers.IntegerField(
        help_text="进行中成就数量",
    )
    
    total_reward_points = serializers.IntegerField(
        help_text="总奖励积分",
    )
    
    claimed_rewards = serializers.IntegerField(
        help_text="已领取奖励数量",
    )
    
    unlock_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="成就解锁率",
    )
    
    average_progress = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="平均进度",
    )
    
    category_distribution = serializers.DictField(
        help_text="分类分布",
    )
    
    difficulty_distribution = serializers.DictField(
        help_text="难度分布",
    )
    
    recent_unlocks = serializers.ListField(
        help_text="最近解锁的成就",
    )
    
    upcoming_achievements = serializers.ListField(
        help_text="即将解锁的成就",
    )
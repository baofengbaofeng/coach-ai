"""
运动管理序列化器模块，定义运动记录、运动计划、运动分析等数据的序列化和反序列化逻辑。
按照豆包AI助手最佳实践：使用Django REST Framework序列化器。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.core.validators import FileExtensionValidator
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.exercise.models import ExerciseAnalysis, ExercisePlan, ExerciseRecord
from core.constants import BusinessRules, ExerciseType, FileTypes


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 运动记录序列化器 ====================
class ExerciseRecordSerializer(serializers.ModelSerializer):
    """
    运动记录序列化器类，用于运动记录的序列化和反序列化。
    """
    
    exercise_type_display = serializers.CharField(source="get_exercise_type_display", read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    calories_per_minute = serializers.SerializerMethodField()
    repetitions_per_minute = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    user_name = serializers.CharField(source="user.username", read_only=True)
    
    class Meta:
        """运动记录序列化器的元数据配置。"""
        
        model = ExerciseRecord
        fields = [
            "id",
            "title",
            "description",
            "user",
            "user_name",
            "exercise_type",
            "exercise_type_display",
            "duration_seconds",
            "duration_minutes",
            "repetitions",
            "calories_burned",
            "heart_rate_avg",
            "heart_rate_max",
            "video_file",
            "latitude",
            "longitude",
            "location_name",
            "started_at",
            "ended_at",
            "calories_per_minute",
            "repetitions_per_minute",
            "progress_percentage",
            "is_completed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user_name",
            "exercise_type_display",
            "duration_minutes",
            "calories_per_minute",
            "repetitions_per_minute",
            "progress_percentage",
            "is_completed",
            "created_at",
            "updated_at",
        ]
    
    def get_duration_minutes(self, obj: ExerciseRecord) -> float:
        """获取运动时长（分钟）。"""
        return obj.get_duration_minutes()
    
    def get_calories_per_minute(self, obj: ExerciseRecord) -> float:
        """获取每分钟消耗的卡路里。"""
        return obj.get_calories_per_minute()
    
    def get_repetitions_per_minute(self, obj: ExerciseRecord) -> float:
        """获取每分钟的重复次数。"""
        return obj.get_repetitions_per_minute()
    
    def get_progress_percentage(self, obj: ExerciseRecord) -> float:
        """获取运动进度百分比。"""
        return obj.get_progress_percentage()
    
    def get_is_completed(self, obj: ExerciseRecord) -> bool:
        """检查运动是否已完成。"""
        return obj.is_completed()
    
    def validate_title(self, value: str) -> str:
        """验证运动标题。"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("运动标题不能为空")
        if len(value) > BusinessRules.EXERCISE_TITLE_MAX_LENGTH:
            raise serializers.ValidationError(
                f"运动标题不能超过{BusinessRules.EXERCISE_TITLE_MAX_LENGTH}个字符"
            )
        return value
    
    def validate_duration_seconds(self, value: int) -> int:
        """验证运动时长。"""
        if value < BusinessRules.MIN_EXERCISE_DURATION:
            raise serializers.ValidationError(
                f"运动时长不能少于{BusinessRules.MIN_EXERCISE_DURATION}秒"
            )
        if value > BusinessRules.MAX_EXERCISE_DURATION:
            raise serializers.ValidationError(
                f"运动时长不能超过{BusinessRules.MAX_EXERCISE_DURATION}秒"
            )
        return value
    
    def validate_video_file(self, value: Any) -> Any:
        """验证运动视频文件。"""
        if value:
            # 检查文件扩展名
            validator = FileExtensionValidator(
                allowed_extensions=FileTypes.VIDEO_EXTENSIONS
            )
            validator(value)
        
        return value
    
    def validate_started_at(self, value: timezone.datetime) -> timezone.datetime:
        """验证开始时间。"""
        if value > timezone.now():
            raise serializers.ValidationError("开始时间不能晚于当前时间")
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """验证运动记录数据的整体一致性。"""
        started_at = attrs.get("started_at")
        ended_at = attrs.get("ended_at")
        duration_seconds = attrs.get("duration_seconds")
        
        # 检查开始时间和结束时间的关系
        if started_at and ended_at:
            if ended_at <= started_at:
                raise serializers.ValidationError({
                    "ended_at": "结束时间必须晚于开始时间"
                })
            
            # 计算时长并与duration_seconds比较
            calculated_duration = (ended_at - started_at).total_seconds()
            if duration_seconds and abs(calculated_duration - duration_seconds) > 60:
                # 允许1分钟的误差
                raise serializers.ValidationError({
                    "duration_seconds": f"运动时长与开始/结束时间不匹配。计算时长: {calculated_duration}秒，输入时长: {duration_seconds}秒"
                })
        
        # 如果只有开始时间和时长，自动计算结束时间
        if started_at and duration_seconds and not ended_at:
            attrs["ended_at"] = started_at + timezone.timedelta(seconds=duration_seconds)
        
        return attrs
    
    def create(self, validated_data: Dict[str, Any]) -> ExerciseRecord:
        """创建运动记录。"""
        # 确保用户字段存在
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data.setdefault("user", request.user)
        
        # 创建运动记录
        exercise_record = ExerciseRecord.objects.create(**validated_data)
        _LOGGER.info(
            "运动记录创建成功: %s (用户: %s)",
            exercise_record.title,
            exercise_record.user.username,
        )
        
        return exercise_record
    
    def update(self, instance: ExerciseRecord, validated_data: Dict[str, Any]) -> ExerciseRecord:
        """更新运动记录。"""
        # 更新运动记录
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        _LOGGER.info("运动记录更新成功: %s (ID: %s)", instance.title, instance.id)
        
        return instance


# ==================== 运动计划序列化器 ====================
class ExercisePlanSerializer(serializers.ModelSerializer):
    """
    运动计划序列化器类，用于运动计划的序列化和反序列化。
    """
    
    remaining_days = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    expected_completion_count = serializers.SerializerMethodField()
    can_add_exercise = serializers.SerializerMethodField()
    user_name = serializers.CharField(source="user.username", read_only=True)
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        """运动计划序列化器的元数据配置。"""
        
        model = ExercisePlan
        fields = [
            "id",
            "name",
            "description",
            "user",
            "user_name",
            "target_duration_minutes",
            "target_repetitions",
            "target_calories",
            "frequency_per_week",
            "start_date",
            "end_date",
            "preferred_time",
            "is_active",
            "completed_count",
            "success_rate",
            "remaining_days",
            "progress_percentage",
            "expected_completion_count",
            "can_add_exercise",
            "status_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user_name",
            "completed_count",
            "success_rate",
            "remaining_days",
            "progress_percentage",
            "expected_completion_count",
            "can_add_exercise",
            "status_display",
            "created_at",
            "updated_at",
        ]
    
    def get_remaining_days(self, obj: ExercisePlan) -> Optional[int]:
        """获取剩余天数。"""
        return obj.get_remaining_days()
    
    def get_progress_percentage(self, obj: ExercisePlan) -> float:
        """获取计划进度百分比。"""
        return obj.get_progress_percentage()
    
    def get_expected_completion_count(self, obj: ExercisePlan) -> int:
        """获取预期的完成次数。"""
        return obj.get_expected_completion_count()
    
    def get_can_add_exercise(self, obj: ExercisePlan) -> bool:
        """检查是否可以添加新的运动记录。"""
        return obj.can_add_exercise()
    
    def get_status_display(self, obj: ExercisePlan) -> str:
        """获取状态显示文本。"""
        return "激活" if obj.is_active else "停用"
    
    def validate_name(self, value: str) -> str:
        """验证计划名称。"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("计划名称不能为空")
        if len(value) > BusinessRules.EXERCISE_PLAN_NAME_MAX_LENGTH:
            raise serializers.ValidationError(
                f"计划名称不能超过{BusinessRules.EXERCISE_PLAN_NAME_MAX_LENGTH}个字符"
            )
        return value
    
    def validate_frequency_per_week(self, value: int) -> int:
        """验证每周频率。"""
        if value < 1 or value > 7:
            raise serializers.ValidationError("每周频率必须在1-7之间")
        return value
    
    def validate_end_date(self, value: Optional[timezone.datetime.date]) -> Optional[timezone.datetime.date]:
        """验证结束日期。"""
        if value:
            start_date = self.initial_data.get("start_date")
            if start_date:
                try:
                    start_date = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
                    if value <= start_date:
                        raise serializers.ValidationError("结束日期必须晚于开始日期")
                except ValueError:
                    pass
        
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """验证运动计划数据的整体一致性。"""
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        
        # 检查日期关系
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({
                "end_date": "结束日期必须晚于开始日期"
            })
        
        # 新创建的计划默认激活
        if self.instance is None:
            attrs.setdefault("is_active", True)
        
        return attrs
    
    def create(self, validated_data: Dict[str, Any]) -> ExercisePlan:
        """创建运动计划。"""
        # 确保用户字段存在
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data.setdefault("user", request.user)
        
        # 创建运动计划
        exercise_plan = ExercisePlan.objects.create(**validated_data)
        _LOGGER.info(
            "运动计划创建成功: %s (用户: %s)",
            exercise_plan.name,
            exercise_plan.user.username,
        )
        
        return exercise_plan
    
    def update(self, instance: ExercisePlan, validated_data: Dict[str, Any]) -> ExercisePlan:
        """更新运动计划。"""
        # 检查状态转换
        old_is_active = instance.is_active
        new_is_active = validated_data.get("is_active", old_is_active)
        
        if old_is_active != new_is_active:
            _LOGGER.info(
                "运动计划状态变更: %s (ID: %s), 从 %s 变为 %s",
                instance.name,
                instance.id,
                "激活" if old_is_active else "停用",
                "激活" if new_is_active else "停用",
            )
        
        # 更新运动计划
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        _LOGGER.info("运动计划更新成功: %s (ID: %s)", instance.name, instance.id)
        
        return instance


# ==================== 运动分析序列化器 ====================
class ExerciseAnalysisSerializer(serializers.ModelSerializer):
    """
    运动分析序列化器类，用于运动分析的序列化和反序列化。
    """
    
    analysis_period_display = serializers.CharField(source="get_analysis_period_display", read_only=True)
    period_days = serializers.SerializerMethodField()
    daily_average_duration = serializers.SerializerMethodField()
    daily_average_calories = serializers.SerializerMethodField()
    exercise_frequency = serializers.SerializerMethodField()
    health_score = serializers.SerializerMethodField()
    user_name = serializers.CharField(source="user.username", read_only=True)
    
    class Meta:
        """运动分析序列化器的元数据配置。"""
        
        model = ExerciseAnalysis
        fields = [
            "id",
            "user",
            "user_name",
            "analysis_period",
            "analysis_period_display",
            "period_start",
            "period_end",
            "period_days",
            "total_duration_minutes",
            "total_calories",
            "total_repetitions",
            "exercise_count",
            "average_duration_minutes",
            "average_calories",
            "consistency_rate",
            "improvement_rate",
            "strengths",
            "weaknesses",
            "recommendations",
            "daily_average_duration",
            "daily_average_calories",
            "exercise_frequency",
            "health_score",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user_name",
            "analysis_period_display",
            "period_days",
            "average_duration_minutes",
            "average_calories",
            "daily_average_duration",
            "daily_average_calories",
            "exercise_frequency",
            "health_score",
            "created_at",
            "updated_at",
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=ExerciseAnalysis.objects.all(),
                fields=["user", "analysis_period", "period_start", "period_end"],
                message="同一用户在同一周期的分析记录已存在",
            ),
        ]
    
    def get_period_days(self, obj: ExerciseAnalysis) -> int:
        """获取分析周期的天数。"""
        return obj.get_period_days()
    
    def get_daily_average_duration(self, obj: ExerciseAnalysis) -> float:
        """获取每日平均运动时长。"""
        return obj.get_daily_average_duration()
    
    def get_daily_average_calories(self, obj: ExerciseAnalysis) -> float:
        """获取每日平均卡路里消耗。"""
        return obj.get_daily_average_calories()
    
    def get_exercise_frequency(self, obj: ExerciseAnalysis) -> float:
        """获取运动频率（次/天）。"""
        return obj.get_exercise_frequency()
    
    def get_health_score(self, obj: ExerciseAnalysis) -> float:
        """计算健康评分。"""
        return obj.get_health_score()
    
    def validate_analysis_period(self, value: str) -> str:
        """验证分析周期。"""
        valid_periods = ["daily", "weekly", "monthly", "yearly"]
        if value not in valid_periods:
            raise serializers.ValidationError(f"分析周期必须是以下之一: {', '.join(valid_periods)}")
        return value
    
    def validate_period_end(self, value: timezone.datetime.date) -> timezone.datetime.date:
        """验证周期结束日期。"""
        period_start = self.initial_data.get("period_start")
        if period_start:
            try:
                period_start = timezone.datetime.strptime(period_start, "%Y-%m-%d").date()
                if value <= period_start:
                    raise serializers.ValidationError("周期结束日期必须晚于周期开始日期")
            except ValueError:
                pass
        
        return value
    
    def validate_consistency_rate(self, value: float) -> float:
        """验证坚持率。"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("坚持率必须在0-100之间")
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """验证运动分析数据的整体一致性。"""
        period_start = attrs.get("period_start")
        period_end = attrs.get("period_end")
        
        # 检查日期关系
        if period_start and period_end and period_end <= period_start:
            raise serializers.ValidationError({
                "period_end": "周期结束日期必须晚于周期开始日期"
            })
        
        # 验证统计数据的逻辑一致性
        exercise_count = attrs.get("exercise_count", 0)
        total_duration = attrs.get("total_duration_minutes", 0)
        total_calories = attrs.get("total_calories", 0)
        
        if exercise_count > 0:
            # 验证平均值计算
            if "average_duration_minutes" in attrs:
                expected_avg = total_duration / exercise_count
                if abs(attrs["average_duration_minutes"] - expected_avg) > 0.01:
                    raise serializers.ValidationError({
                        "average_duration_minutes": f"平均时长计算错误。预期: {expected_avg:.2f}, 实际: {attrs['average_duration_minutes']}"
                    })
            
            if "average_calories" in attrs:
                expected_avg = total_calories / exercise_count
                if abs(attrs["average_calories"] - expected_avg) > 0.01:
                    raise serializers.ValidationError({
                        "average_calories": f"平均卡路里计算错误。预期: {expected_avg:.2f}, 实际: {attrs['average_calories']}"
                    })
        
        return attrs
    
    def create(self, validated_data: Dict[str, Any]) -> ExerciseAnalysis:
        """创建运动分析。"""
        # 确保用户字段存在
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data.setdefault("user", request.user)
        
        # 创建运动分析
        exercise_analysis = ExerciseAnalysis.objects.create(**validated_data)
        _LOGGER.info(
            "运动分析创建成功: 用户=%s, 周期=%s",
            exercise_analysis.user.username,
            exercise_analysis.get_analysis_period_display(),
        )
        
        return exercise_analysis
    
    def update(self, instance: ExerciseAnalysis, validated_data: Dict[str, Any]) -> ExerciseAnalysis:
        """更新运动分析。"""
        # 更新运动分析
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        _LOGGER.info(
            "运动分析更新成功: ID=%s, 用户=%s",
            instance.id,
            instance.user.username,
        )
        
        return instance


# ==================== 运动记录创建序列化器 ====================
class ExerciseRecordCreateSerializer(serializers.ModelSerializer):
    """
    运动记录创建序列化器类，专门用于创建运动记录。
    """
    
    class Meta:
        """运动记录创建序列化器的元数据配置。"""
        
        model = ExerciseRecord
        fields = [
            "title",
            "description",
            "exercise_type",
            "duration_seconds",
            "repetitions",
            "calories_burned",
            "heart_rate_avg",
            "heart_rate_max",
            "video_file",
            "latitude",
            "longitude",
            "location_name",
            "started_at",
        ]
    
    def create(self, validated_data: Dict[str, Any]) -> ExerciseRecord:
        """创建运动记录。"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("用户未认证")
        
        # 设置用户
        validated_data["user"] = request.user
        
        # 如果未设置结束时间，自动计算
        if "started_at" in validated_data and "duration_seconds" in validated_data:
            if "ended_at" not in validated_data:
                validated_data["ended_at"] = validated_data["started_at"] + timezone.timedelta(
                    seconds=validated_data["duration_seconds"]
                )
        
        # 创建运动记录
        exercise_record = ExerciseRecord.objects.create(**validated_data)
        _LOGGER.info(
            "运动记录创建成功: %s (用户: %s)",
            exercise_record.title,
            request.user.username,
        )
        
        return exercise_record


# ==================== 运动计划进度更新序列化器 ====================
class ExercisePlanProgressSerializer(serializers.Serializer):
    """
    运动计划进度更新序列化器类，用于更新运动计划的完成进度。
    """
    
    completed_count = serializers.IntegerField(
        min_value=0,
        help_text="完成的运动次数",
    )
    
    def validate_completed_count(self, value: int) -> int:
        """验证完成次数。"""
        # 获取计划实例
        view = self.context.get("view")
        if view and hasattr(view, "get_object"):
            exercise_plan = view.get_object()
            expected_count = exercise_plan.get_expected_completion_count()
            
            if value > expected_count:
                raise serializers.ValidationError(
                    f"完成次数不能超过预期次数 ({expected_count})"
                )
        
        return value
    
    def save(self, exercise_plan_id: int) -> ExercisePlan:
        """保存进度更新。"""
        from django.db import transaction
        
        completed_count = self.validated_data["completed_count"]
        
        with transaction.atomic():
            # 获取运动计划
            try:
                exercise_plan = ExercisePlan.objects.get(id=exercise_plan_id)
            except ExercisePlan.DoesNotExist:
                raise serializers.ValidationError(f"运动计划ID {exercise_plan_id} 不存在")
            
            # 更新完成次数
            exercise_plan.completed_count = completed_count
            
            # 重新计算完成率
            expected_count = exercise_plan.get_expected_completion_count()
            if expected_count > 0:
                exercise_plan.success_rate = (completed_count / expected_count) * 100
            
            exercise_plan.save()
            
            _LOGGER.info(
                "运动计划进度更新: %s (ID: %s), 完成次数: %s, 完成率: %.1f%%",
                exercise_plan.name,
                exercise_plan.id,
                completed_count,
                exercise_plan.success_rate,
            )
            
            return exercise_plan
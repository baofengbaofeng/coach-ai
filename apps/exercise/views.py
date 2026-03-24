"""
运动管理视图模块，定义运动相关的API端点和处理逻辑。
按照豆包AI助手最佳实践：使用Django REST Framework视图集。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.db.models import Avg, Count, Q, QuerySet, Sum
from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.exercise.models import ExerciseAnalysis, ExercisePlan, ExerciseRecord
from apps.exercise.serializers import (
    ExerciseAnalysisSerializer,
    ExercisePlanProgressSerializer,
    ExercisePlanSerializer,
    ExerciseRecordCreateSerializer,
    ExerciseRecordSerializer,
)
from core.constants import ExerciseType
from core.permissions import IsOwnerOrReadOnly, IsOwnerOrTeacherOrAdmin


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 运动记录视图集 ====================
class ExerciseRecordViewSet(viewsets.ModelViewSet):
    """
    运动记录视图集类，提供运动记录的CRUD操作。
    """
    
    serializer_class = ExerciseRecordSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "location_name"]
    ordering_fields = [
        "started_at",
        "ended_at",
        "duration_seconds",
        "calories_burned",
        "repetitions",
        "created_at",
    ]
    ordering = ["-started_at"]
    
    def get_queryset(self) -> QuerySet[ExerciseRecord]:
        """获取运动记录查询集，根据用户角色和权限过滤。"""
        user = self.request.user
        queryset = ExerciseRecord.objects.select_related("user")
        
        # 用户只能查看自己的运动记录
        if user.role == "student":
            queryset = queryset.filter(user=user)
        # 老师和家长可以查看所有运动记录
        elif user.role in ["teacher", "parent"]:
            pass  # 不进行过滤
        # 管理员可以查看所有运动记录
        elif user.is_superuser:
            pass  # 不进行过滤
        else:
            queryset = queryset.none()
        
        # 运动类型过滤
        exercise_type = self.request.query_params.get("exercise_type")
        if exercise_type:
            queryset = queryset.filter(exercise_type=exercise_type)
        
        # 时间范围过滤
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            queryset = queryset.filter(started_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(started_at__date__lte=end_date)
        
        # 是否完成过滤
        completed = self.request.query_params.get("completed")
        if completed is not None:
            if completed.lower() == "true":
                queryset = queryset.filter(ended_at__lte=timezone.now())
            elif completed.lower() == "false":
                queryset = queryset.filter(
                    Q(ended_at__isnull=True) | Q(ended_at__gt=timezone.now())
                )
        
        # 最小时长过滤
        min_duration = self.request.query_params.get("min_duration")
        if min_duration and min_duration.isdigit():
            queryset = queryset.filter(duration_seconds__gte=int(min_duration))
        
        # 最大时长过滤
        max_duration = self.request.query_params.get("max_duration")
        if max_duration and max_duration.isdigit():
            queryset = queryset.filter(duration_seconds__lte=int(max_duration))
        
        return queryset
    
    def get_serializer_class(self):
        """根据动作选择序列化器。"""
        if self.action == "create":
            return ExerciseRecordCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer: ExerciseRecordSerializer) -> None:
        """创建运动记录时自动设置用户。"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=["GET"])
    def statistics(self, request: Request) -> Response:
        """获取运动记录统计信息。"""
        user = request.user
        queryset = self.get_queryset()
        
        # 基础统计
        total_count = queryset.count()
        completed_count = queryset.filter(ended_at__lte=timezone.now()).count()
        
        # 按运动类型统计
        type_stats = (
            queryset.values("exercise_type")
            .annotate(
                count=Count("id"),
                total_duration=Sum("duration_seconds"),
                total_calories=Sum("calories_burned"),
                total_repetitions=Sum("repetitions"),
                avg_duration=Avg("duration_seconds"),
                avg_calories=Avg("calories_burned"),
            )
            .order_by("-count")
        )
        
        # 时间趋势统计（最近30天）
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        daily_stats = (
            queryset.filter(started_at__gte=thirty_days_ago)
            .extra({"date": "DATE(started_at)"})
            .values("date")
            .annotate(
                count=Count("id"),
                total_duration=Sum("duration_seconds"),
                total_calories=Sum("calories_burned"),
            )
            .order_by("date")
        )
        
        # 计算总时长和总卡路里
        total_duration = queryset.aggregate(total=Sum("duration_seconds"))["total"] or 0
        total_calories = queryset.aggregate(total=Sum("calories_burned"))["total"] or 0
        total_repetitions = queryset.aggregate(total=Sum("repetitions"))["total"] or 0
        
        # 计算平均指标
        avg_duration = queryset.aggregate(avg=Avg("duration_seconds"))["avg"] or 0
        avg_calories = queryset.aggregate(avg=Avg("calories_burned"))["avg"] or 0
        
        return Response({
            "total_count": total_count,
            "completed_count": completed_count,
            "completion_rate": (completed_count / total_count * 100) if total_count > 0 else 0,
            "total_duration_seconds": total_duration,
            "total_duration_minutes": total_duration / 60,
            "total_calories": total_calories,
            "total_repetitions": total_repetitions,
            "average_duration_seconds": avg_duration,
            "average_calories": avg_calories,
            "type_statistics": list(type_stats),
            "daily_trend": list(daily_stats),
        })
    
    @action(detail=False, methods=["GET"])
    def summary(self, request: Request) -> Response:
        """获取运动记录摘要信息。"""
        user = request.user
        queryset = self.get_queryset()
        
        # 今日运动
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timezone.timedelta(days=1)
        
        today_exercises = queryset.filter(
            started_at__gte=today_start,
            started_at__lt=today_end,
        )
        
        today_count = today_exercises.count()
        today_duration = today_exercises.aggregate(total=Sum("duration_seconds"))["total"] or 0
        today_calories = today_exercises.aggregate(total=Sum("calories_burned"))["total"] or 0
        
        # 本周运动
        week_start = today_start - timezone.timedelta(days=today_start.weekday())
        week_exercises = queryset.filter(started_at__gte=week_start)
        
        week_count = week_exercises.count()
        week_duration = week_exercises.aggregate(total=Sum("duration_seconds"))["total"] or 0
        week_calories = week_exercises.aggregate(total=Sum("calories_burned"))["total"] or 0
        
        # 本月运动
        month_start = today_start.replace(day=1)
        month_exercises = queryset.filter(started_at__gte=month_start)
        
        month_count = month_exercises.count()
        month_duration = month_exercises.aggregate(total=Sum("duration_seconds"))["total"] or 0
        month_calories = month_exercises.aggregate(total=Sum("calories_burned"))["total"] or 0
        
        # 最常进行的运动类型
        favorite_type = (
            queryset.values("exercise_type")
            .annotate(count=Count("id"))
            .order_by("-count")
            .first()
        )
        
        return Response({
            "today": {
                "count": today_count,
                "duration_seconds": today_duration,
                "duration_minutes": today_duration / 60,
                "calories": today_calories,
            },
            "this_week": {
                "count": week_count,
                "duration_seconds": week_duration,
                "duration_minutes": week_duration / 60,
                "calories": week_calories,
            },
            "this_month": {
                "count": month_count,
                "duration_seconds": month_duration,
                "duration_minutes": month_duration / 60,
                "calories": month_calories,
            },
            "favorite_exercise_type": favorite_type,
            "user": {
                "username": user.username,
                "role": user.role,
            },
        })


# ==================== 运动计划视图集 ====================
class ExercisePlanViewSet(viewsets.ModelViewSet):
    """
    运动计划视图集类，提供运动计划的CRUD操作。
    """
    
    serializer_class = ExercisePlanSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = [
        "start_date",
        "end_date",
        "success_rate",
        "created_at",
    ]
    ordering = ["-created_at"]
    
    def get_queryset(self) -> QuerySet[ExercisePlan]:
        """获取运动计划查询集，根据用户角色和权限过滤。"""
        user = self.request.user
        queryset = ExercisePlan.objects.select_related("user")
        
        # 用户只能查看自己的运动计划
        if user.role == "student":
            queryset = queryset.filter(user=user)
        # 老师和家长可以查看所有运动计划
        elif user.role in ["teacher", "parent"]:
            pass  # 不进行过滤
        # 管理员可以查看所有运动计划
        elif user.is_superuser:
            pass  # 不进行过滤
        else:
            queryset = queryset.none()
        
        # 状态过滤
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=(is_active.lower() == "true"))
        
        # 时间范围过滤
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        
        # 完成率过滤
        min_success_rate = self.request.query_params.get("min_success_rate")
        max_success_rate = self.request.query_params.get("max_success_rate")
        if min_success_rate and min_success_rate.isdigit():
            queryset = queryset.filter(success_rate__gte=int(min_success_rate))
        if max_success_rate and max_success_rate.isdigit():
            queryset = queryset.filter(success_rate__lte=int(max_success_rate))
        
        return queryset
    
    def perform_create(self, serializer: ExercisePlanSerializer) -> None:
        """创建运动计划时自动设置用户。"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=["POST"])
    def update_progress(self, request: Request, pk: Optional[int] = None) -> Response:
        """更新运动计划的完成进度。"""
        exercise_plan = self.get_object()
        serializer = ExercisePlanProgressSerializer(
            data=request.data,
            context={"request": request, "view": self},
        )
        serializer.is_valid(raise_exception=True)
        
        try:
            updated_plan = serializer.save(exercise_plan_id=exercise_plan.id)
            
            # 返回更新后的计划信息
            plan_serializer = self.get_serializer(updated_plan)
            return Response(plan_serializer.data)
        except Exception as e:
            _LOGGER.error("更新运动计划进度失败: %s", str(e))
            return Response(
                {"error": "更新进度失败"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=True, methods=["POST"])
    def activate(self, request: Request, pk: Optional[int] = None) -> Response:
        """激活运动计划。"""
        exercise_plan = self.get_object()
        
        if exercise_plan.is_active:
            return Response(
                {"error": "运动计划已经是激活状态"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        exercise_plan.is_active = True
        exercise_plan.save()
        
        _LOGGER.info("运动计划激活: %s (ID: %s)", exercise_plan.name, exercise_plan.id)
        
        serializer = self.get_serializer(exercise_plan)
        return Response(serializer.data)
    
    @action(detail=True, methods=["POST"])
    def deactivate(self, request: Request, pk: Optional[int] = None) -> Response:
        """停用运动计划。"""
        exercise_plan = self.get_object()
        
        if not exercise_plan.is_active:
            return Response(
                {"error": "运动计划已经是停用状态"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        exercise_plan.is_active = False
        exercise_plan.save()
        
        _LOGGER.info("运动计划停用: %s (ID: %s)", exercise_plan.name, exercise_plan.id)
        
        serializer = self.get_serializer(exercise_plan)
        return Response(serializer.data)
    
    @action(detail=False, methods=["GET"])
    def statistics(self, request: Request) -> Response:
        """获取运动计划统计信息。"""
        user = request.user
        queryset = self.get_queryset()
        
        # 基础统计
        total_count = queryset.count()
        active_count = queryset.filter(is_active=True).count()
        completed_count = queryset.filter(success_rate__gte=80).count()  # 完成率80%以上视为完成
        
        # 按状态统计
        status_stats = (
            queryset.values("is_active")
            .annotate(count=Count("id"))
            .order_by("-is_active")
        )
        
        # 计算平均完成率
        avg_success_rate = queryset.aggregate(avg=Avg("success_rate"))["avg"] or 0
        
        # 时间趋势统计（最近12个月）
        twelve_months_ago = timezone.now() - timezone.timedelta(days=365)
        monthly_stats = (
            queryset.filter(created_at__gte=twelve_months_ago)
            .extra({"month": "strftime('%Y-%m', created_at)"})
            .values("month")
            .annotate(
                count=Count("id"),
                avg_success_rate=Avg("success_rate"),
            )
            .order_by("month")
        )
        
        return Response({
            "total_count": total_count,
            "active_count": active_count,
            "completed_count": completed_count,
            "completion_rate": (completed_count / total_count * 100) if total_count > 0 else 0,
            "average_success_rate": avg_success_rate,
            "status_statistics": list(status_stats),
            "monthly_trend": list(monthly_stats),
        })


# ==================== 运动分析视图集 ====================
class ExerciseAnalysisViewSet(viewsets.ModelViewSet):
    """
    运动分析视图集类，提供运动分析的CRUD操作。
    """
    
    serializer_class = ExerciseAnalysisSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = [
        "period_start",
        "period_end",
        "health_score",
        "created_at",
    ]
    ordering = ["-period_end"]
    
    def get_queryset(self) -> QuerySet[ExerciseAnalysis]:
        """获取运动分析查询集，根据用户角色和权限过滤。"""
        user = self.request.user
        queryset = ExerciseAnalysis.objects.select_related("user")
        
        # 用户只能查看自己的运动分析
        if user.role == "student":
            queryset = queryset.filter(user=user)
        # 老师和家长可以查看所有运动分析
        elif user.role in ["teacher", "parent"]:
            pass  # 不进行过滤
        # 管理员可以查看所有运动分析
        elif user.is_superuser:
            pass  # 不进行过滤
        else:
            queryset = queryset.none()
        
        # 分析周期过滤
        analysis_period = self.request.query_params.get("analysis_period")
        if analysis_period:
            queryset = queryset.filter(analysis_period=analysis_period)
        
        # 时间范围过滤
        period_start = self.request.query_params.get("period_start")
        period_end = self.request.query_params.get("period_end")
        if period_start:
            queryset = queryset.filter(period_start__gte=period_start)
        if period_end:
            queryset = queryset.filter(period_end__lte=period_end)
        
        # 健康评分过滤
        min_health_score = self.request.query_params.get("min_health_score")
        max_health_score = self.request.query_params.get("max_health_score")
        if min_health_score and min_health_score.isdigit():
            queryset = queryset.filter(health_score__gte=int(min_health_score))
        if max_health_score and max_health_score.isdigit():
            queryset = queryset.filter(health_score__lte=int(max_health_score))
        
        return queryset
    
    def perform_create(self, serializer: ExerciseAnalysisSerializer) -> None:
        """创建运动分析时自动设置用户。"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=["GET"])
    def generate_weekly(self, request: Request) -> Response:
        """生成每周运动分析。"""
        user = request.user
        
        # 计算上周的日期范围
        today = timezone.now().date()
        last_week_start = today - timezone.timedelta(days=today.weekday() + 7)
        last_week_end = last_week_start + timezone.timedelta(days=6)
        
        # 检查是否已存在上周的分析
        existing_analysis = ExerciseAnalysis.objects.filter(
            user=user,
            analysis_period="weekly",
            period_start=last_week_start,
            period_end=last_week_end,
        ).first()
        
        if existing_analysis:
            serializer = self.get_serializer(existing_analysis)
            return Response(serializer.data)
        
        # 获取上周的运动记录
        last_week_records = ExerciseRecord.objects.filter(
            user=user,
            started_at__date__gte=last_week_start,
            started_at__date__lte=last_week_end,
        )
        
        # 计算统计指标
        total_duration_minutes = sum(
            record.duration_seconds / 60 for record in last_week_records
        )
        total_calories = sum(record.calories_burned for record in last_week_records)
        total_repetitions = sum(record.repetitions for record in last_week_records)
        exercise_count = last_week_records.count()
        
        # 获取前一周的数据用于计算进步率
        two_weeks_ago_start = last_week_start - timezone.timedelta(days=7)
        two_weeks_ago_end = last_week_end - timezone.timedelta(days=7)
        
        previous_week_records = ExerciseRecord.objects.filter(
            user=user,
            started_at__date__gte=two_weeks_ago_start,
            started_at__date__lte=two_weeks_ago_end,
        )
        
        previous_duration = sum(
            record.duration_seconds / 60 for record in previous_week_records
        )
        previous_calories = sum(record.calories_burned for record in previous_week_records)
        
        # 计算进步率
        improvement_rate = 0
        if previous_duration > 0:
            duration_improvement = ((total_duration_minutes - previous_duration) / previous_duration) * 100
            calories_improvement = ((total_calories - previous_calories) / previous_calories) * 100
            improvement_rate = (duration_improvement + calories_improvement) / 2
        
        # 创建分析记录
        analysis_data = {
            "user": user,
            "analysis_period": "weekly",
            "period_start": last_week_start,
            "period_end": last_week_end,
            "total_duration_minutes": total_duration_minutes,
            "total_calories": total_calories,
            "total_repetitions": total_repetitions,
            "exercise_count": exercise_count,
            "average_duration_minutes": total_duration_minutes / exercise_count if exercise_count > 0 else 0,
            "average_calories": total_calories / exercise_count if exercise_count > 0 else 0,
            "consistency_rate": min((exercise_count / 7) * 100, 100),  # 假设每天运动一次为100%
            "improvement_rate": improvement_rate,
            "strengths": self._generate_strengths_analysis(last_week_records),
            "weaknesses": self._generate_weaknesses_analysis(last_week_records),
            "recommendations": self._generate_recommendations(last_week_records),
        }
        
        serializer = self.get_serializer(data=analysis_data)
        serializer.is_valid(raise_exception=True)
        analysis = serializer.save()
        
        _LOGGER.info("每周运动分析生成成功: 用户=%s, 周期=%s 至 %s", user.username, last_week_start, last_week_end)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def _generate_strengths_analysis(self, records: QuerySet[ExerciseRecord]) -> str:
        """生成优势分析。"""
        if not records.exists():
            return "本周暂无运动记录"
        
        strengths = []
        
        # 检查运动频率
        unique_days = len(set(record.started_at.date() for record in records))
        if unique_days >= 5:
            strengths.append("运动频率较高，坚持得很好")
        
        # 检查运动时长
        avg_duration = sum(record.duration_seconds for record in records) / len(records) / 60
        if avg_duration >= 30:
            strengths.append(f"平均运动时长达到{avg_duration:.1f}分钟，表现优秀")
        
        # 检查运动类型多样性
        exercise_types = set(record.exercise_type for record in records)
        if len(exercise_types) >= 3:
            strengths.append(f"运动类型多样，涵盖了{len(exercise_types)}种不同的运动")
        
        return "；".join(strengths) if strengths else "本周运动表现平稳"
    
    def _generate_weaknesses_analysis(self, records: QuerySet[ExerciseRecord]) -> str:
        """生成待改进点分析。"""
        if not records.exists():
            return "建议开始规律运动，每周至少3次，每次30分钟"
        
        weaknesses = []
        
        # 检查运动频率
        unique_days = len(set(record.started_at.date() for record in records))
        if unique_days < 3:
            weaknesses.append(f"运动频率较低，本周只运动了{unique_days}天，建议增加到3-5天")
        
        # 检查运动时长
        avg_duration = sum(record.duration_seconds for record in records) / len(records) / 60
        if avg_duration < 20:
            weaknesses.append(f"平均运动时长只有{avg_duration:.1f}分钟，建议增加到30分钟以上")
        
        # 检查运动强度
        avg_calories = sum(record.calories_burned for record in records) / len(records)
        if avg_calories < 100:
            weaknesses.append(f"运动强度较低，平均每次只消耗{avg_calories:.1f}千卡，建议增加运动强度")
        
        return "；".join(weaknesses) if weaknesses else "本周运动表现良好，继续保持"
    
    def _generate_recommendations(self, records: QuerySet[ExerciseRecord]) -> str:
        """生成改进建议。"""
        if not records.exists():
            return "1. 制定一个简单的运动计划，从每周3次、每次20分钟开始\n2. 选择喜欢的运动类型，如跳绳、慢跑、瑜伽等\n3. 记录每次运动，跟踪进度"
        
        recommendations = []
        
        # 检查运动频率
        unique_days = len(set(record.started_at.date() for record in records))
        if unique_days < 5:
            recommendations.append(f"建议将运动频率增加到每周{5-unique_days}天")
        
        # 检查运动类型
        exercise_types = set(record.exercise_type for record in records)
        if len(exercise_types) < 2:
            recommendations.append("建议尝试不同类型的运动，如有氧运动+力量训练结合")
        
        # 检查运动时间
        morning_count = sum(1 for record in records if record.started_at.hour < 12)
        evening_count = sum(1 for record in records if record.started_at.hour >= 17)
        
        if morning_count == 0:
            recommendations.append("可以尝试早晨运动，有助于提高一天的精力和代谢")
        if evening_count == 0:
            recommendations.append("可以尝试傍晚运动，有助于缓解一天的压力")
        
        return "；".join(recommendations) if recommendations else "继续保持当前的运动习惯，可以适当增加运动强度或尝试新的运动类型"
    
    @action(detail=False, methods=["GET"])
    def statistics(self, request: Request) -> Response:
        """获取运动分析统计信息。"""
        user = request.user
        queryset = self.get_queryset()
        
        # 基础统计
        total_count = queryset.count()
        
        # 按分析周期统计
        period_stats = (
            queryset.values("analysis_period")
            .annotate(
                count=Count("id"),
                avg_health_score=Avg("health_score"),
                avg_consistency_rate=Avg("consistency_rate"),
                avg_improvement_rate=Avg("improvement_rate"),
            )
            .order_by("-count")
        )
        
        # 健康评分分布
        health_score_ranges = [
            (0, 60, "需改进"),
            (60, 80, "良好"),
            (80, 90, "优秀"),
            (90, 100, "卓越"),
        ]
        
        score_distribution = []
        for min_score, max_score, label in health_score_ranges:
            count = queryset.filter(
                health_score__gte=min_score,
                health_score__lt=max_score,
            ).count()
            score_distribution.append({
                "range": f"{min_score}-{max_score}",
                "label": label,
                "count": count,
                "percentage": (count / total_count * 100) if total_count > 0 else 0,
            })
        
        # 时间趋势统计（最近12个月）
        twelve_months_ago = timezone.now() - timezone.timedelta(days=365)
        monthly_stats = (
            queryset.filter(created_at__gte=twelve_months_ago)
            .extra({"month": "strftime('%Y-%m', created_at)"})
            .values("month")
            .annotate(
                count=Count("id"),
                avg_health_score=Avg("health_score"),
            )
            .order_by("month")
        )
        
        return Response({
            "total_count": total_count,
            "period_statistics": list(period_stats),
            "health_score_distribution": score_distribution,
            "monthly_trend": list(monthly_stats),
        })
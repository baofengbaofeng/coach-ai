"""
成就系统视图模块，定义成就、用户成就进度、成就分类和奖励等API视图。
按照豆包AI助手最佳实践：使用Django REST Framework视图集。
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Q, Sum, Avg, Max, Min
from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.achievements.models import (
    Achievement,
    AchievementCategory,
    AchievementReward,
    AchievementStatistic,
    UserAchievement,
)
from apps.achievements.serializers import (
    AchievementCategorySerializer,
    AchievementCreateSerializer,
    AchievementRewardSerializer,
    AchievementSerializer,
    AchievementStatisticSerializer,
    UserAchievementProgressSerializer,
    UserAchievementSerializer,
    UserAchievementStatisticsSerializer,
)
from core.constants import BusinessRules, ErrorMessages


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 用户模型引用 ====================
User = get_user_model()


# ==================== 成就分类视图集 ====================
class AchievementCategoryViewSet(viewsets.ModelViewSet):
    """
    成就分类视图集类，提供成就分类的CRUD操作。
    """
    
    queryset = AchievementCategory.objects.all()
    serializer_class = AchievementCategorySerializer
    permission_classes = [IsAdminUser]  # 只有管理员可以管理分类
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["order", "name", "created_at"]
    ordering = ["order", "name"]
    
    def get_permissions(self):
        """根据动作调整权限。"""
        if self.action in ["list", "retrieve"]:
            # 所有人都可以查看分类
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer: AchievementCategorySerializer) -> None:
        """创建成就分类。"""
        category = serializer.save()
        _LOGGER.info(
            "用户 %s 创建成就分类: %s (ID: %s)",
            self.request.user.username, category.name, category.pk
        )
    
    def perform_update(self, serializer: AchievementCategorySerializer) -> None:
        """更新成就分类。"""
        category = serializer.save()
        _LOGGER.info(
            "用户 %s 更新成就分类: %s (ID: %s)",
            self.request.user.username, category.name, category.pk
        )
    
    def perform_destroy(self, instance: AchievementCategory) -> None:
        """删除成就分类。"""
        _LOGGER.info(
            "用户 %s 删除成就分类: %s (ID: %s)",
            self.request.user.username, instance.name, instance.pk
        )
        super().perform_destroy(instance)
    
    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None) -> Response:
        """获取分类统计信息。"""
        category = self.get_object()
        
        # 统计分类下的成就
        achievements = category.achievements.filter(is_active=True)
        total_achievements = achievements.count()
        unlocked_achievements = achievements.filter(
            user_achievements__is_unlocked=True
        ).distinct().count()
        
        # 统计用户进度
        user_achievements = UserAchievement.objects.filter(
            achievement__category=category
        )
        total_users = user_achievements.values("user").distinct().count()
        unlocked_users = user_achievements.filter(is_unlocked=True).values("user").distinct().count()
        
        statistics = {
            "category": {
                "id": category.id,
                "name": category.name,
                "description": category.description,
            },
            "achievement_stats": {
                "total_achievements": total_achievements,
                "unlocked_achievements": unlocked_achievements,
                "unlock_rate": (
                    (unlocked_achievements / total_achievements * 100)
                    if total_achievements > 0 else 0
                ),
            },
            "user_stats": {
                "total_users": total_users,
                "unlocked_users": unlocked_users,
                "participation_rate": (
                    (unlocked_users / total_users * 100)
                    if total_users > 0 else 0
                ),
            },
            "difficulty_distribution": achievements.values(
                "difficulty"
            ).annotate(count=Count("id")).order_by("difficulty"),
        }
        
        return Response(statistics)


# ==================== 成就视图集 ====================
class AchievementViewSet(viewsets.ModelViewSet):
    """
    成就视图集类，提供成就的CRUD操作。
    """
    
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [IsAdminUser]  # 只有管理员可以管理成就
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "condition_type"]
    ordering_fields = [
        "display_order", "name", "difficulty", "reward_points",
        "unlocked_count", "created_at"
    ]
    ordering = ["display_order", "name"]
    
    def get_permissions(self):
        """根据动作调整权限。"""
        if self.action in ["list", "retrieve", "user_progress", "recommendations"]:
            # 所有人都可以查看成就
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        """根据动作选择序列化器。"""
        if self.action == "create":
            return AchievementCreateSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
        """根据用户权限过滤查询集。"""
        queryset = super().get_queryset()
        
        # 非管理员只能看到非隐藏的成就
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_secret=False, is_active=True)
        
        # 过滤分类
        category_id = self.request.query_params.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # 过滤难度
        difficulty = self.request.query_params.get("difficulty")
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # 过滤成就类型
        achievement_type = self.request.query_params.get("type")
        if achievement_type:
            queryset = queryset.filter(achievement_type=achievement_type)
        
        # 过滤解锁状态（针对当前用户）
        unlock_status = self.request.query_params.get("unlock_status")
        if unlock_status and self.request.user.is_authenticated:
            user = self.request.user
            if unlock_status == "unlocked":
                queryset = queryset.filter(
                    user_achievements__user=user,
                    user_achievements__is_unlocked=True
                )
            elif unlock_status == "locked":
                queryset = queryset.exclude(
                    user_achievements__user=user,
                    user_achievements__is_unlocked=True
                )
        
        return queryset
    
    def perform_create(self, serializer: AchievementCreateSerializer) -> None:
        """创建成就。"""
        achievement = serializer.save()
        _LOGGER.info(
            "用户 %s 创建成就: %s (ID: %s)",
            self.request.user.username, achievement.name, achievement.pk
        )
    
    def perform_update(self, serializer: AchievementSerializer) -> None:
        """更新成就。"""
        achievement = serializer.save()
        _LOGGER.info(
            "用户 %s 更新成就: %s (ID: %s)",
            self.request.user.username, achievement.name, achievement.pk
        )
    
    def perform_destroy(self, instance: Achievement) -> None:
        """删除成就。"""
        _LOGGER.info(
            "用户 %s 删除成就: %s (ID: %s)",
            self.request.user.username, instance.name, instance.pk
        )
        super().perform_destroy(instance)
    
    @action(detail=True, methods=["get"])
    def user_progress(self, request, pk=None) -> Response:
        """获取当前用户在该成就上的进度。"""
        achievement = self.get_object()
        user = request.user
        
        try:
            user_achievement = UserAchievement.objects.get(
                user=user,
                achievement=achievement
            )
            serializer = UserAchievementSerializer(user_achievement)
            return Response(serializer.data)
        except UserAchievement.DoesNotExist:
            # 如果用户还没有该成就的记录，创建一条
            user_achievement = UserAchievement.objects.create(
                user=user,
                achievement=achievement,
                current_value=Decimal("0.00")
            )
            serializer = UserAchievementSerializer(user_achievement)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=["post"])
    def update_progress(self, request, pk=None) -> Response:
        """更新用户在该成就上的进度。"""
        achievement = self.get_object()
        user = request.user
        
        # 获取或创建用户成就记录
        user_achievement, created = UserAchievement.objects.get_or_create(
            user=user,
            achievement=achievement,
            defaults={"current_value": Decimal("0.00")}
        )
        
        # 验证进度数据
        progress_serializer = UserAchievementProgressSerializer(data=request.data)
        if not progress_serializer.is_valid():
            return Response(
                progress_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 更新进度
        new_value = progress_serializer.validated_data["current_value"]
        metadata = progress_serializer.validated_data.get("metadata")
        
        was_unlocked = user_achievement.update_progress(new_value, metadata)
        
        # 记录日志
        _LOGGER.info(
            "用户 %s 更新成就 %s 进度: %s -> %s, 解锁状态: %s",
            user.username, achievement.name,
            user_achievement.current_value, new_value,
            "已解锁" if was_unlocked else "未解锁"
        )
        
        # 返回更新后的用户成就
        serializer = UserAchievementSerializer(user_achievement)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"])
    def claim_reward(self, request, pk=None) -> Response:
        """领取成就奖励。"""
        achievement = self.get_object()
        user = request.user
        
        try:
            user_achievement = UserAchievement.objects.get(
                user=user,
                achievement=achievement
            )
        except UserAchievement.DoesNotExist:
            return Response(
                {"error": "用户尚未解锁该成就"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 尝试领取奖励
        if user_achievement.claim_reward():
            return Response({
                "success": True,
                "message": "奖励领取成功",
                "reward_points": achievement.reward_points,
                "reward_badge": achievement.reward_badge,
            })
        else:
            return Response({
                "success": False,
                "message": "奖励领取失败，可能已领取或尚未解锁"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=["get"])
    def recommendations(self, request) -> Response:
        """获取成就推荐。"""
        user = request.user
        
        # 获取用户已解锁的成就
        unlocked_achievements = Achievement.objects.filter(
            user_achievements__user=user,
            user_achievements__is_unlocked=True
        ).values_list("id", flat=True)
        
        # 推荐策略1：基于用户兴趣（分类）
        user_categories = AchievementCategory.objects.filter(
            achievements__user_achievements__user=user
        ).distinct()
        
        # 推荐策略2：基于难度递进
        easy_achievements = Achievement.objects.filter(
            difficulty="easy",
            is_active=True,
            is_secret=False
        ).exclude(id__in=unlocked_achievements).order_by("display_order")[:5]
        
        # 推荐策略3：热门成就（解锁人数多）
        popular_achievements = Achievement.objects.filter(
            is_active=True,
            is_secret=False
        ).exclude(id__in=unlocked_achievements).order_by("-unlocked_count")[:5]
        
        # 推荐策略4：即将解锁的成就
        user_achievements = UserAchievement.objects.filter(
            user=user,
            is_unlocked=False
        ).select_related("achievement").order_by("-progress_percentage")[:5]
        
        recommendations = {
            "based_on_interests": AchievementSerializer(
                Achievement.objects.filter(
                    category__in=user_categories,
                    is_active=True,
                    is_secret=False
                ).exclude(id__in=unlocked_achievements).order_by("?")[:5],
                many=True
            ).data,
            "easy_achievements": AchievementSerializer(easy_achievements, many=True).data,
            "popular_achievements": AchievementSerializer(popular_achievements, many=True).data,
            "upcoming_achievements": UserAchievementSerializer(user_achievements, many=True).data,
        }
        
        return Response(recommendations)
    
    @action(detail=False, methods=["get"])
    def statistics(self, request) -> Response:
        """获取成就统计信息。"""
        # 总体统计
        total_achievements = Achievement.objects.filter(is_active=True).count()
        total_unlocks = UserAchievement.objects.filter(is_unlocked=True).count()
        total_users = User.objects.count()
        
        # 分类统计
        category_stats = AchievementCategory.objects.filter(
            is_active=True
        ).annotate(
            achievement_count=Count("achievements", filter=Q(achievements__is_active=True)),
            unlocked_count=Count(
                "achievements__user_achievements",
                filter=Q(achievements__user_achievements__is_unlocked=True)
            )
        ).values("id", "name", "achievement_count", "unlocked_count")
        
        # 难度统计
        difficulty_stats = Achievement.objects.filter(
            is_active=True
        ).values("difficulty").annotate(
            count=Count("id"),
            avg_unlock_rate=Avg("unlock_rate"),
            max_reward_points=Max("reward_points")
        ).order_by("difficulty")
        
        # 时间统计（最近30天）
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_unlocks = UserAchievement.objects.filter(
            unlocked_at__gte=thirty_days_ago
        ).extra({
            "date": "DATE(unlocked_at)"
        }).values("date").annotate(
            count=Count("id")
        ).order_by("date")
        
        statistics = {
            "overall": {
                "total_achievements": total_achievements,
                "total_unlocks": total_unlocks,
                "total_users": total_users,
                "average_unlocks_per_user": (
                    total_unlocks / total_users if total_users > 0 else 0
                ),
            },
            "category_distribution": list(category_stats),
            "difficulty_distribution": list(difficulty_stats),
            "recent_activity": {
                "daily_unlocks": list(daily_unlocks),
                "top_achievements": AchievementSerializer(
                    Achievement.objects.filter(is_active=True).order_by("-unlocked_count")[:10],
                    many=True
                ).data,
            },
        }
        
        return Response(statistics)


# ==================== 用户成就视图集 ====================
class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    用户成就视图集类，提供用户成就进度的只读操作。
    """
    
    serializer_class = UserAchievementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["achievement__name", "achievement__description"]
    ordering_fields = [
        "progress_percentage", "unlocked_at", "last_updated_at",
        "achievement__difficulty", "achievement__reward_points"
    ]
    ordering = ["-unlocked_at", "-last_updated_at"]
    
    def get_queryset(self):
        """只返回当前用户的成就记录。"""
        return UserAchievement.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=["get"])
    def statistics(self, request) -> Response:
        """获取用户成就统计信息。"""
        user = request.user
        
        # 获取用户的所有成就记录
        user_achievements = UserAchievement.objects.filter(user=user)
        
        # 基础统计
        total_achievements = Achievement.objects.filter(is_active=True).count()
        unlocked_achievements = user_achievements.filter(is_unlocked=True).count()
        in_progress_achievements = user_achievements.filter(is_unlocked=False).count()
        
        # 奖励统计
        total_reward_points = user_achievements.filter(
            is_unlocked=True
        ).aggregate(
            total_points=Sum("achievement__reward_points")
        )["total_points"] or 0
        
        claimed_rewards = user_achievements.filter(
            is_unlocked=True, is_reward_claimed=True
        ).count()
        
        # 进度统计
        average_progress = user_achievements.filter(
            is_unlocked=False
        ).aggregate(
            avg_progress=Avg("progress_percentage")
        )["avg_progress"] or 0
        
        # 分类分布
        category_distribution = user_achievements.values(
            "achievement__category__name"
        ).annotate(
            count=Count("id"),
            unlocked=Count("id", filter=Q(is_unlocked=True))
        ).order_by("-count")
        
        # 难度分布
        difficulty_distribution = user_achievements.values(
            "achievement__difficulty"
        ).annotate(
            count=Count("id"),
            unlocked=Count("id", filter=Q(is_unlocked=True))
        ).order_by("achievement__difficulty")
        
        # 最近解锁的成就
        recent_unlocks = user_achievements.filter(
            is_unlocked=True
        ).order_by("-unlocked_at")[:10]
        
        # 即将解锁的成就（进度>80%）
        upcoming_achievements = user_achievements.filter(
            is_unlocked=False,
            progress_percentage__gte=80
        ).order_by("-progress_percentage")[:10]
        
        statistics = {
            "total_achievements": total_achievements,
            "unlocked_achievements": unlocked_achievements,
            "in_progress_achievements": in_progress_achievements,
            "total_reward_points": total_reward_points,
            "claimed_rewards": claimed_rewards,
            "unlock_rate": (
                (unlocked_achievements / total_achievements * 100)
                if total_achievements > 0 else 0
            ),
            "average_progress": float(average_progress),
            "category_distribution": {
                item["achievement__category__name"] or "未分类": {
                    "total": item["count"],
                    "unlocked": item["unlocked"]
                }
                for item in category_distribution
            },
            "difficulty_distribution": {
                item["achievement__difficulty"]: {
                    "total": item["count"],
                    "unlocked": item["unlocked"]
                }
                for item in difficulty_distribution
            },
            "recent_unlocks": UserAchievementSerializer(recent_unlocks, many=True).data,
            "upcoming_achievements": UserAchievementSerializer(upcoming_achievements, many=True).data,
        }
        
        serializer = UserAchievementStatisticsSerializer(statistics)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def dashboard(self, request) -> Response:
        """获取用户成就仪表板数据。"""
        user = request.user
        
        # 今日解锁的成就
        today = timezone.now().date()
        today_unlocks = UserAchievement.objects.filter(
            user=user,
            is_unlocked=True,
            unlocked_at__date=today
        ).count()
        
        # 本周解锁的成就
        week_start = today - timedelta(days=today.weekday())
        week_unlocks = UserAchievement.objects.filter(
            user=user,
            is_unlocked=True,
            unlocked_at__date__gte=week_start
        ).count()
        
        # 连续解锁天数
        consecutive_days = 0
        current_date = today
        while True:
            has_unlock = UserAchievement.objects.filter(
                user=user,
                is_unlocked=True,
                unlocked_at__date=current_date
            ).exists()
            
            if has_unlock:
                consecutive_days += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        # 成就里程碑
        milestones = []
        total_unlocks = UserAchievement.objects.filter(user=user, is_unlocked=True).count()
        
        for milestone in [1, 10, 25, 50, 100]:
            if total_unlocks >= milestone:
                milestones.append({
                    "name": f"解锁{milestone}个成就",
                    "achieved": True,
                    "achieved_at": UserAchievement.objects.filter(
                        user=user, is_unlocked=True
                    ).order_by("unlocked_at")[milestone-1].unlocked_at
                })
            else:
                milestones.append({
                    "name": f"解锁{milestone}个成就",
                    "achieved": False,
                    "remaining": milestone - total_unlocks
                })
        
        dashboard_data = {
            "today_stats": {
                "unlocks": today_unlocks,
                "reward_points": UserAchievement.objects.filter(
                    user=user,
                    is_unlocked=True,
                    unlocked_at__date=today
                ).aggregate(
                    total=Sum("achievement__reward_points")
                )["total"] or 0,
            },
            "week_stats": {
                "unlocks": week_unlocks,
                "reward_points": UserAchievement.objects.filter(
                    user=user,
                    is_unlocked=True,
                    unlocked_at__date__gte=week_start
                ).aggregate(
                    total=Sum("achievement__reward_points")
                )["total"] or 0,
            },
            "streaks": {
                "consecutive_days": consecutive_days,
                "current_streak_start": today - timedelta(days=consecutive_days-1) if consecutive_days > 0 else None,
            },
            "milestones": milestones,
            "quick_stats": {
                "total_unlocks": total_unlocks,
                "total_reward_points": UserAchievement.objects.filter(
                    user=user, is_unlocked=True
                ).aggregate(
                    total=Sum("achievement__reward_points")
                )["total"] or 0,
                "average_unlock_time": UserAchievement.objects.filter(
                    user=user,
                    is_unlocked=True,
                    time_to_unlock__isnull=False
                ).aggregate(
                    avg_time=Avg("time_to_unlock")
                )["avg_time"],
            },
        }
        
        return Response(dashboard_data)


# ==================== 成就奖励视图集 ====================
class AchievementRewardViewSet(viewsets.ModelViewSet):
    """
    成就奖励视图集类，提供成就奖励的CRUD操作。
    """
    
    queryset = AchievementReward.objects.all()
    serializer_class = AchievementRewardSerializer
    permission_classes = [IsAdminUser]  # 只有管理员可以管理奖励
    
    def get_permissions(self):
        """根据动作调整权限。"""
        if self.action in ["list", "retrieve", "claim"]:
            # 所有人都可以查看奖励，但只有用户可以领取
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer: AchievementRewardSerializer) -> None:
        """创建成就奖励。"""
        reward = serializer.save()
        _LOGGER.info(
            "用户 %s 创建成就奖励: 成就 %s, 奖励类型 %s",
            self.request.user.username, reward.achievement.name, reward.reward_type
        )
    
    def perform_update(self, serializer: AchievementRewardSerializer) -> None:
        """更新成就奖励。"""
        reward = serializer.save()
        _LOGGER.info(
            "用户 %s 更新成就奖励: 成就 %s, 奖励类型 %s",
            self.request.user.username, reward.achievement.name, reward.reward_type
        )
    
    def perform_destroy(self, instance: AchievementReward) -> None:
        """删除成就奖励。"""
        _LOGGER.info(
            "用户 %s 删除成就奖励: 成就 %s, 奖励类型 %s",
            self.request.user.username, instance.achievement.name, instance.reward_type
        )
        super().perform_destroy(instance)
    
    @action(detail=True, methods=["post"])
    def claim(self, request, pk=None) -> Response:
        """领取成就奖励。"""
        reward = self.get_object()
        user = request.user
        
        # 检查用户是否已解锁对应的成就
        try:
            user_achievement = UserAchievement.objects.get(
                user=user,
                achievement=reward.achievement
            )
        except UserAchievement.DoesNotExist:
            return Response(
                {"error": "用户尚未解锁该成就"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user_achievement.is_unlocked:
            return Response(
                {"error": "用户尚未解锁该成就"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user_achievement.is_reward_claimed:
            return Response(
                {"error": "奖励已领取"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查奖励是否可以领取
        if not reward.can_claim():
            return Response(
                {"error": "奖励已达到限制，无法领取"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 领取奖励
        with transaction.atomic():
            # 记录奖励领取
            reward.claim()
            
            # 更新用户成就的奖励领取状态
            user_achievement.claim_reward()
            
            _LOGGER.info(
                "用户 %s 领取成就奖励: 成就 %s, 奖励类型 %s",
                user.username, reward.achievement.name, reward.reward_type
            )
        
        return Response({
            "success": True,
            "message": "奖励领取成功",
            "reward_type": reward.reward_type,
            "reward_value": reward.reward_value,
            "reward_description": reward.reward_description,
        })


# ==================== 成就统计视图集 ====================
class AchievementStatisticViewSet(viewsets.ReadOnlyModelViewSet):
    """
    成就统计视图集类，提供成就统计数据的只读操作。
    """
    
    queryset = AchievementStatistic.objects.all()
    serializer_class = AchievementStatisticSerializer
    permission_classes = [IsAdminUser]  # 只有管理员可以查看详细统计
    
    def get_permissions(self):
        """根据动作调整权限。"""
        if self.action in ["overview", "daily_unlocks"]:
            # 所有人都可以查看概览统计
            return [IsAuthenticated()]
        return super().get_permissions()
    
    @action(detail=False, methods=["get"])
    def overview(self, request) -> Response:
        """获取成就系统概览统计。"""
        # 总体统计
        total_achievements = Achievement.objects.filter(is_active=True).count()
        total_users = User.objects.count()
        total_unlocks = UserAchievement.objects.filter(is_unlocked=True).count()
        
        # 今日统计
        today = timezone.now().date()
        today_unlocks = UserAchievement.objects.filter(
            is_unlocked=True,
            unlocked_at__date=today
        ).count()
        
        # 本周统计
        week_start = today - timedelta(days=today.weekday())
        week_unlocks = UserAchievement.objects.filter(
            is_unlocked=True,
            unlocked_at__date__gte=week_start
        ).count()
        
        # 分类统计
        category_stats = AchievementCategory.objects.filter(
            is_active=True
        ).annotate(
            achievement_count=Count("achievements", filter=Q(achievements__is_active=True)),
            unlocked_count=Count(
                "achievements__user_achievements",
                filter=Q(achievements__user_achievements__is_unlocked=True)
            )
        ).values("id", "name", "achievement_count", "unlocked_count")[:10]
        
        # 热门成就
        popular_achievements = Achievement.objects.filter(
            is_active=True
        ).order_by("-unlocked_count")[:10].values(
            "id", "name", "unlocked_count", "unlock_rate"
        )
        
        overview = {
            "overall": {
                "total_achievements": total_achievements,
                "total_users": total_users,
                "total_unlocks": total_unlocks,
                "average_unlocks_per_user": (
                    total_unlocks / total_users if total_users > 0 else 0
                ),
            },
            "today": {
                "unlocks": today_unlocks,
                "new_users": User.objects.filter(
                    date_joined__date=today
                ).count(),
            },
            "this_week": {
                "unlocks": week_unlocks,
                "new_users": User.objects.filter(
                    date_joined__date__gte=week_start
                ).count(),
            },
            "category_stats": list(category_stats),
            "popular_achievements": list(popular_achievements),
        }
        
        return Response(overview)
    
    @action(detail=False, methods=["get"])
    def daily_unlocks(self, request) -> Response:
        """获取每日解锁统计。"""
        # 获取最近30天的数据
        days = int(request.query_params.get("days", 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # 查询每日解锁数据
        daily_data = []
        current_date = start_date
        
        while current_date <= end_date:
            unlocks = UserAchievement.objects.filter(
                is_unlocked=True,
                unlocked_at__date=current_date
            ).count()
            
            daily_data.append({
                "date": current_date.isoformat(),
                "unlocks": unlocks,
            })
            
            current_date += timedelta(days=1)
        
        return Response({
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days,
            },
            "daily_unlocks": daily_data,
            "total_unlocks": sum(item["unlocks"] for item in daily_data),
            "average_daily_unlocks": (
                sum(item["unlocks"] for item in daily_data) / days
                if days > 0 else 0
            ),
        })
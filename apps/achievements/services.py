"""
成就系统服务模块，处理成就系统的核心业务逻辑。
按照豆包AI助手最佳实践：业务逻辑写在 services.py，视图层只做参数接收和响应返回。
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Q, Sum, Avg, Max, Min
from django.utils import timezone

from apps.achievements.models import (
    Achievement,
    AchievementCategory,
    AchievementReward,
    AchievementStatistic,
    UserAchievement,
)
from core.constants import BusinessRules, ErrorMessages


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 用户模型引用 ====================
User = get_user_model()


# ==================== 成就服务类 ====================
class AchievementService:
    """
    成就服务类，处理成就相关的业务逻辑。
    """
    
    @staticmethod
    def create_achievement(
        name: str,
        description: str,
        category_id: Optional[int] = None,
        achievement_type: str = "count",
        difficulty: str = "medium",
        condition_type: str = "task_completed",
        condition_value: Decimal = Decimal("1.00"),
        condition_operator: str = "gte",
        reward_points: int = 0,
        **kwargs: Any
    ) -> Tuple[bool, Optional[Achievement], str]:
        """
        创建成就。
        
        Args:
            name: 成就名称
            description: 成就描述
            category_id: 分类ID
            achievement_type: 成就类型
            difficulty: 难度等级
            condition_type: 条件类型
            condition_value: 条件值
            condition_operator: 条件运算符
            reward_points: 奖励积分
            **kwargs: 其他参数
            
        Returns:
            (成功标志, 成就对象, 消息)
        """
        try:
            # 验证分类
            category = None
            if category_id:
                try:
                    category = AchievementCategory.objects.get(id=category_id, is_active=True)
                except AchievementCategory.DoesNotExist:
                    return False, None, "分类不存在或已停用"
            
            # 创建成就
            achievement = Achievement.objects.create(
                name=name,
                description=description,
                category=category,
                achievement_type=achievement_type,
                difficulty=difficulty,
                condition_type=condition_type,
                condition_value=condition_value,
                condition_operator=condition_operator,
                reward_points=reward_points,
                **kwargs
            )
            
            _LOGGER.info("成就创建成功: %s (ID: %s)", name, achievement.pk)
            return True, achievement, "成就创建成功"
            
        except Exception as e:
            _LOGGER.error("成就创建失败: %s, 错误: %s", name, str(e))
            return False, None, f"成就创建失败: {str(e)}"
    
    @staticmethod
    def update_user_progress(
        user_id: int,
        achievement_id: int,
        current_value: Decimal,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[UserAchievement], str]:
        """
        更新用户成就进度。
        
        Args:
            user_id: 用户ID
            achievement_id: 成就ID
            current_value: 当前进度值
            metadata: 元数据
            
        Returns:
            (成功标志, 用户成就对象, 消息)
        """
        try:
            # 获取用户和成就
            user = User.objects.get(id=user_id)
            achievement = Achievement.objects.get(id=achievement_id, is_active=True)
            
            # 获取或创建用户成就记录
            user_achievement, created = UserAchievement.objects.get_or_create(
                user=user,
                achievement=achievement,
                defaults={"current_value": Decimal("0.00")}
            )
            
            # 更新进度
            was_unlocked = user_achievement.update_progress(current_value, metadata)
            
            message = "进度更新成功"
            if was_unlocked and not created:
                message = "成就解锁成功！"
            
            _LOGGER.info(
                "用户 %s 成就 %s 进度更新: %s -> %s, 解锁: %s",
                user.username, achievement.name,
                user_achievement.current_value, current_value,
                was_unlocked
            )
            
            return True, user_achievement, message
            
        except User.DoesNotExist:
            return False, None, "用户不存在"
        except Achievement.DoesNotExist:
            return False, None, "成就不存在或已停用"
        except Exception as e:
            _LOGGER.error(
                "用户成就进度更新失败: 用户ID %s, 成就ID %s, 错误: %s",
                user_id, achievement_id, str(e)
            )
            return False, None, f"进度更新失败: {str(e)}"
    
    @staticmethod
    def check_and_unlock_achievements(
        user_id: int,
        condition_type: str,
        current_value: Decimal,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        检查并解锁符合条件的成就。
        
        Args:
            user_id: 用户ID
            condition_type: 条件类型
            current_value: 当前值
            metadata: 元数据
            
        Returns:
            解锁的成就列表
        """
        try:
            user = User.objects.get(id=user_id)
            
            # 查找符合条件的成就
            achievements = Achievement.objects.filter(
                condition_type=condition_type,
                is_active=True
            )
            
            unlocked_achievements = []
            
            for achievement in achievements:
                # 检查是否满足条件
                if achievement.check_condition(current_value):
                    # 更新用户成就进度
                    success, user_achievement, message = AchievementService.update_user_progress(
                        user_id=user_id,
                        achievement_id=achievement.id,
                        current_value=current_value,
                        metadata=metadata
                    )
                    
                    if success and user_achievement and user_achievement.is_unlocked:
                        unlocked_achievements.append({
                            "achievement": achievement,
                            "user_achievement": user_achievement,
                            "message": message,
                        })
            
            _LOGGER.info(
                "用户 %s 检查成就解锁: 条件类型 %s, 当前值 %s, 解锁 %s 个成就",
                user.username, condition_type, current_value, len(unlocked_achievements)
            )
            
            return unlocked_achievements
            
        except Exception as e:
            _LOGGER.error(
                "检查成就解锁失败: 用户ID %s, 条件类型 %s, 错误: %s",
                user_id, condition_type, str(e)
            )
            return []
    
    @staticmethod
    def get_user_recommendations(user_id: int, limit: int = 10) -> List[Achievement]:
        """
        获取用户成就推荐。
        
        Args:
            user_id: 用户ID
            limit: 推荐数量
            
        Returns:
            推荐的成就列表
        """
        try:
            user = User.objects.get(id=user_id)
            
            # 获取用户已解锁的成就ID
            unlocked_achievement_ids = UserAchievement.objects.filter(
                user=user,
                is_unlocked=True
            ).values_list("achievement_id", flat=True)
            
            # 推荐策略1：基于用户已解锁成就的分类
            user_categories = AchievementCategory.objects.filter(
                achievements__user_achievements__user=user,
                achievements__user_achievements__is_unlocked=True
            ).distinct()
            
            # 推荐策略2：基于难度递进
            recommendations = []
            
            # 先推荐同分类的成就
            if user_categories.exists():
                category_recommendations = Achievement.objects.filter(
                    category__in=user_categories,
                    is_active=True,
                    is_secret=False
                ).exclude(id__in=unlocked_achievement_ids).order_by("difficulty", "display_order")[:limit]
                recommendations.extend(category_recommendations)
            
            # 如果推荐数量不足，补充其他成就
            if len(recommendations) < limit:
                remaining = limit - len(recommendations)
                other_recommendations = Achievement.objects.filter(
                    is_active=True,
                    is_secret=False
                ).exclude(
                    id__in=unlocked_achievement_ids
                ).exclude(
                    id__in=[a.id for a in recommendations]
                ).order_by("difficulty", "display_order")[:remaining]
                recommendations.extend(other_recommendations)
            
            _LOGGER.info(
                "用户 %s 成就推荐: 推荐 %s 个成就",
                user.username, len(recommendations)
            )
            
            return recommendations
            
        except Exception as e:
            _LOGGER.error(
                "获取成就推荐失败: 用户ID %s, 错误: %s",
                user_id, str(e)
            )
            return []


# ==================== 成就统计服务类 ====================
class AchievementStatisticService:
    """
    成就统计服务类，处理成就统计相关的业务逻辑。
    """
    
    @staticmethod
    def generate_daily_statistics(date: Optional[datetime.date] = None) -> bool:
        """
        生成每日成就统计。
        
        Args:
            date: 统计日期，默认为昨天
            
        Returns:
            是否成功
        """
        try:
            if date is None:
                date = timezone.now().date() - timedelta(days=1)
            
            # 检查是否已生成该日期的统计
            if AchievementStatistic.objects.filter(
                statistic_type="daily_unlocks",
                statistic_date=date
            ).exists():
                _LOGGER.warning("该日期的统计已存在: %s", date)
                return False
            
            # 统计每日解锁数据
            daily_unlocks = UserAchievement.objects.filter(
                is_unlocked=True,
                unlocked_at__date=date
            ).count()
            
            # 统计分类分布
            category_distribution = AchievementCategory.objects.filter(
                is_active=True
            ).annotate(
                unlock_count=Count(
                    "achievements__user_achievements",
                    filter=Q(
                        achievements__user_achievements__is_unlocked=True,
                        achievements__user_achievements__unlocked_at__date=date
                    )
                )
            ).values("id", "name", "unlock_count")
            
            # 统计难度分布
            difficulty_distribution = Achievement.objects.filter(
                is_active=True
            ).annotate(
                unlock_count=Count(
                    "user_achievements",
                    filter=Q(
                        user_achievements__is_unlocked=True,
                        user_achievements__unlocked_at__date=date
                    )
                )
            ).values("difficulty").annotate(
                count=Count("id"),
                unlock_count=Sum("unlock_count")
            ).order_by("difficulty")
            
            # 创建统计记录
            statistic = AchievementStatistic.objects.create(
                statistic_type="daily_unlocks",
                statistic_date=date,
                data={
                    "daily_unlocks": daily_unlocks,
                    "category_distribution": list(category_distribution),
                    "difficulty_distribution": list(difficulty_distribution),
                },
                total_count=daily_unlocks,
                average_value=Decimal(str(daily_unlocks)),
                max_value=Decimal(str(daily_unlocks)),
                min_value=Decimal(str(daily_unlocks)),
            )
            
            _LOGGER.info("每日成就统计生成成功: 日期 %s, 解锁数 %s", date, daily_unlocks)
            return True
            
        except Exception as e:
            _LOGGER.error("生成每日成就统计失败: 日期 %s, 错误: %s", date, str(e))
            return False
    
    @staticmethod
    def get_system_overview() -> Dict[str, Any]:
        """
        获取成就系统概览统计。
        
        Returns:
            概览统计数据
        """
        try:
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
            
            # 热门成就（解锁人数最多的前10个）
            popular_achievements = Achievement.objects.filter(
                is_active=True
            ).order_by("-unlocked_count")[:10].values(
                "id", "name", "unlocked_count", "unlock_rate"
            )
            
            # 活跃用户（最近7天有解锁记录的用户）
            seven_days_ago = today - timedelta(days=7)
            active_users = User.objects.filter(
                user_achievements__is_unlocked=True,
                user_achievements__unlocked_at__date__gte=seven_days_ago
            ).distinct().count()
            
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
                    "new_users": User.objects.filter(date_joined__date=today).count(),
                },
                "this_week": {
                    "unlocks": week_unlocks,
                    "new_users": User.objects.filter(date_joined__date__gte=week_start).count(),
                    "active_users": active_users,
                },
                "popular_achievements": list(popular_achievements),
            }
            
            return overview
            
        except Exception as e:
            _LOGGER.error("获取成就系统概览失败: %s", str(e))
            return {}


# ==================== 成就奖励服务类 ====================
class AchievementRewardService:
    """
    成就奖励服务类，处理成就奖励相关的业务逻辑。
    """
    
    @staticmethod
    def claim_achievement_reward(user_id: int, achievement_id: int) -> Tuple[bool, Dict[str, Any], str]:
        """
        领取成就奖励。
        
        Args:
            user_id: 用户ID
            achievement_id: 成就ID
            
        Returns:
            (成功标志, 奖励信息, 消息)
        """
        try:
            with transaction.atomic():
                # 获取用户和成就
                user = User.objects.get(id=user_id)
                achievement = Achievement.objects.get(id=achievement_id, is_active=True)
                
                # 检查用户成就
                try:
                    user_achievement = UserAchievement.objects.get(
                        user=user,
                        achievement=achievement
                    )
                except UserAchievement.DoesNotExist:
                    return False, {}, "用户尚未解锁该成就"
                
                if not user_achievement.is_unlocked:
                    return False, {}, "用户尚未解锁该成就"
                
                if user_achievement.is_reward_claimed:
                    return False, {}, "奖励已领取"
                
                # 检查成就奖励
                try:
                    reward = AchievementReward.objects.get(achievement=achievement)
                except AchievementReward.DoesNotExist:
                    # 如果没有设置奖励，使用成就的基本奖励
                    reward_info = {
                        "reward_points": achievement.reward_points,
                        "reward_badge": achievement.reward_badge,
                        "reward_message": achievement.reward_message,
                    }
                    
                    # 标记奖励已领取
                    user_achievement.claim_reward()
                    
                    _LOGGER.info(
                        "用户 %s 领取成就 %s 的基本奖励",
                        user.username, achievement.name
                    )
                    
                    return True, reward_info, "奖励领取成功"
                
                # 检查奖励是否可以领取
                if not reward.can_claim():
                    return False, {}, "奖励已达到限制，无法领取"
                
                # 领取奖励
                reward.claim()
                user_achievement.claim_reward()
                
                reward_info = {
                    "reward_type": reward.reward_type,
                    "reward_value": reward.reward_value,
                    "reward_description": reward.reward_description,
                    "reward_points": achievement.reward_points,
                    "reward_badge": achievement.reward_badge,
                }
                
                _LOGGER.info(
                    "用户 %s 领取成就 %s 的奖励: 类型 %s, 值 %s",
                    user.username, achievement.name, reward.reward_type, reward.reward_value
                )
                
                return True, reward_info, "奖励领取成功"
                
        except User.DoesNotExist:
            return False, {}, "用户不存在"
        except Achievement.DoesNotExist:
            return False, {}, "成就不存在或已停用"
        except Exception as e:
            _LOGGER.error(
                "领取成就奖励失败: 用户ID %s, 成就ID %s, 错误: %s",
                user_id, achievement_id, str(e)
            )
            return False, {}, f"奖励领取失败: {str(e)}"


# ==================== 服务工厂函数 ====================
def get_achievement_service() -> AchievementService:
    """获取成就服务实例。"""
    return AchievementService()


def get_achievement_statistic_service() -> AchievementStatisticService:
    """获取成就统计服务实例。"""
    return AchievementStatisticService()


def get_achievement_reward_service() -> AchievementRewardService:
    """获取成就奖励服务实例。"""
    return AchievementRewardService()
"""
智能推荐服务模块，提供基于用户行为的个性化推荐。
按照豆包AI助手最佳实践：提供类型安全的推荐服务。
"""
from __future__ import annotations

import logging
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Max, Q, Sum
from django.utils import timezone

from apps.achievements.models import Achievement, UserAchievement
from apps.exercise.models import ExercisePlan, ExerciseRecord
from apps.tasks.models import Task, TaskCategory
from services.base import UserAwareAIService, ConfigurableAIService


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 用户模型引用 ====================
User = get_user_model()


# ==================== 智能推荐服务 ====================
class RecommendationService(ConfigurableAIService, UserAwareAIService):
    """
    智能推荐服务类，提供个性化推荐。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化推荐服务。
        
        Args:
            config: 服务配置
        """
        super().__init__("recommendation", config)
        
        # 推荐类型权重
        self._recommendation_weights: Dict[str, float] = {
            "exercise": 0.3,
            "task": 0.3,
            "achievement": 0.2,
            "category": 0.1,
            "reminder": 0.1,
        }
        
        # 用户行为分析缓存
        self._user_behavior_cache: Dict[int, Dict[str, Any]] = {}
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置。
        
        Returns:
            默认配置字典
        """
        return {
            "max_recommendations": 10,
            "cache_ttl_minutes": 30,
            "similarity_threshold": 0.6,
            "diversity_factor": 0.3,
            "recency_weight": 0.4,
            "frequency_weight": 0.3,
            "relevance_weight": 0.3,
            "enable_content_based": True,
            "enable_collaborative": True,
            "enable_hybrid": True,
        }
    
    def _initialize_internal(self) -> bool:
        """
        内部初始化逻辑。
        
        Returns:
            是否初始化成功
        """
        try:
            config = self.get_config()
            self._logger.info(
                "推荐服务初始化完成，配置: max_recommendations=%s, cache_ttl=%s分钟",
                config["max_recommendations"],
                config["cache_ttl_minutes"],
            )
            return True
        except Exception as e:
            self._logger.error("推荐服务初始化失败: %s", str(e))
            return False
    
    def _process_internal(self, input_data: Any, **kwargs: Any) -> Any:
        """
        内部处理逻辑，生成推荐。
        
        Args:
            input_data: 输入数据（用户ID或用户对象）
            **kwargs: 其他参数
            
        Returns:
            推荐结果
        """
        # 获取用户
        user = self._get_user_from_input(input_data)
        if not user:
            raise ValueError("无效的用户输入")
        
        # 设置用户上下文
        self.set_user_context(user, kwargs.get("user_context"))
        
        try:
            # 获取推荐类型
            recommendation_type = kwargs.get("type", "all")
            
            # 生成推荐
            if recommendation_type == "all":
                recommendations = self._generate_all_recommendations(user, **kwargs)
            elif recommendation_type == "exercise":
                recommendations = self._generate_exercise_recommendations(user, **kwargs)
            elif recommendation_type == "task":
                recommendations = self._generate_task_recommendations(user, **kwargs)
            elif recommendation_type == "achievement":
                recommendations = self._generate_achievement_recommendations(user, **kwargs)
            elif recommendation_type == "category":
                recommendations = self._generate_category_recommendations(user, **kwargs)
            else:
                raise ValueError(f"不支持的推荐类型: {recommendation_type}")
            
            # 格式化推荐结果
            formatted_recommendations = self._format_recommendations(recommendations, **kwargs)
            
            return {
                "success": True,
                "user_id": user.id,
                "username": user.username,
                "recommendation_type": recommendation_type,
                "total_count": len(formatted_recommendations),
                "recommendations": formatted_recommendations,
                "generated_at": timezone.now().isoformat(),
            }
        finally:
            self.clear_user_context()
    
    def _get_user_from_input(self, input_data: Any) -> Optional[User]:
        """
        从输入数据获取用户对象。
        
        Args:
            input_data: 输入数据
            
        Returns:
            用户对象
        """
        if isinstance(input_data, User):
            return input_data
        elif isinstance(input_data, int):
            try:
                return User.objects.get(id=input_data)
            except User.DoesNotExist:
                return None
        elif isinstance(input_data, str):
            try:
                return User.objects.get(username=input_data)
            except User.DoesNotExist:
                try:
                    return User.objects.get(email=input_data)
                except User.DoesNotExist:
                    return None
        return None
    
    def _generate_all_recommendations(self, user: User, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        生成所有类型的推荐。
        
        Args:
            user: 用户对象
            **kwargs: 其他参数
            
        Returns:
            推荐列表
        """
        all_recommendations: List[Dict[str, Any]] = []
        config = self.get_config()
        
        # 分析用户行为
        user_behavior = self._analyze_user_behavior(user)
        
        # 根据用户行为调整权重
        adjusted_weights = self._adjust_weights_by_behavior(user_behavior)
        
        # 生成各种类型的推荐
        if adjusted_weights.get("exercise", 0) > 0:
            exercise_recs = self._generate_exercise_recommendations(user, **kwargs)
            all_recommendations.extend(exercise_recs)
        
        if adjusted_weights.get("task", 0) > 0:
            task_recs = self._generate_task_recommendations(user, **kwargs)
            all_recommendations.extend(task_recs)
        
        if adjusted_weights.get("achievement", 0) > 0:
            achievement_recs = self._generate_achievement_recommendations(user, **kwargs)
            all_recommendations.extend(achievement_recs)
        
        if adjusted_weights.get("category", 0) > 0:
            category_recs = self._generate_category_recommendations(user, **kwargs)
            all_recommendations.extend(category_recs)
        
        # 排序和去重
        all_recommendations = self._sort_and_deduplicate_recommendations(all_recommendations)
        
        # 限制数量
        max_recs = kwargs.get("max_recommendations", config["max_recommendations"])
        return all_recommendations[:max_recs]
    
    def _generate_exercise_recommendations(self, user: User, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        生成运动推荐。
        
        Args:
            user: 用户对象
            **kwargs: 其他参数
            
        Returns:
            运动推荐列表
        """
        recommendations: List[Dict[str, Any]] = []
        config = self.get_config()
        
        try:
            # 获取用户运动记录
            user_exercises = ExerciseRecord.objects.filter(user=user).order_by("-created_at")
            
            if user_exercises.exists():
                # 基于内容的推荐：推荐相似运动
                recent_exercises = user_exercises[:5]
                for exercise in recent_exercises:
                    similar_plans = ExercisePlan.objects.filter(
                        exercise_type=exercise.exercise_type,
                        difficulty_level=exercise.difficulty_level,
                        is_active=True,
                    ).exclude(
                        Q(user=user) | Q(id__in=[e.plan_id for e in user_exercises if e.plan_id])
                    )[:3]
                    
                    for plan in similar_plans:
                        score = self._calculate_exercise_recommendation_score(user, plan, exercise)
                        if score >= config["similarity_threshold"]:
                            recommendations.append({
                                "type": "exercise",
                                "subtype": "similar",
                                "item": plan,
                                "score": score,
                                "reason": f"基于您最近的{exercise.exercise_type}运动推荐",
                                "metadata": {
                                    "based_on_exercise_id": exercise.id,
                                    "similarity_type": "content",
                                },
                            })
            
            # 协同过滤推荐：推荐其他用户喜欢的运动
            if config["enable_collaborative"]:
                popular_plans = ExercisePlan.objects.filter(
                    is_active=True,
                    is_public=True,
                ).annotate(
                    user_count=Count("exercise_records", distinct=True),
                ).order_by("-user_count", "-created_at")[:5]
                
                for plan in popular_plans:
                    if not user_exercises.filter(plan=plan).exists():
                        score = self._calculate_popularity_score(plan.user_count)
                        recommendations.append({
                            "type": "exercise",
                            "subtype": "popular",
                            "item": plan,
                            "score": score,
                            "reason": "其他用户喜欢的运动计划",
                            "metadata": {
                                "user_count": plan.user_count,
                                "recommendation_type": "collaborative",
                            },
                        })
            
            # 多样性推荐：推荐不同类型的运动
            if config["enable_hybrid"]:
                user_exercise_types = set(user_exercises.values_list("exercise_type", flat=True))
                all_exercise_types = set(ExercisePlan.objects.values_list("exercise_type", flat=True).distinct())
                
                new_types = all_exercise_types - user_exercise_types
                if new_types:
                    for exercise_type in list(new_types)[:2]:
                        new_plans = ExercisePlan.objects.filter(
                            exercise_type=exercise_type,
                            is_active=True,
                            difficulty_level="beginner",  # 从初级开始
                        ).order_by("created_at")[:2]
                        
                        for plan in new_plans:
                            score = 0.5  # 基础分
                            recommendations.append({
                                "type": "exercise",
                                "subtype": "diverse",
                                "item": plan,
                                "score": score,
                                "reason": f"尝试新的运动类型：{exercise_type}",
                                "metadata": {
                                    "exercise_type": exercise_type,
                                    "recommendation_type": "diversity",
                                },
                            })
        
        except Exception as e:
            self._logger.error("生成运动推荐失败: %s", str(e))
        
        return recommendations
    
    def _generate_task_recommendations(self, user: User, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        生成任务推荐。
        
        Args:
            user: 用户对象
            **kwargs: 其他参数
            
        Returns:
            任务推荐列表
        """
        recommendations: List[Dict[str, Any]] = []
        
        try:
            # 获取用户任务
            user_tasks = Task.objects.filter(user=user).order_by("-created_at")
            
            # 推荐未完成的重要任务
            important_tasks = user_tasks.filter(
                priority__in=["high", "urgent"],
                status__in=["pending", "in_progress"],
                due_date__isnull=False,
                due_date__gte=timezone.now(),
            ).order_by("due_date")[:5]
            
            for task in important_tasks:
                urgency_score = self._calculate_task_urgency_score(task)
                recommendations.append({
                    "type": "task",
                    "subtype": "important",
                    "item": task,
                    "score": urgency_score,
                    "reason": "重要且即将到期的任务",
                    "metadata": {
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "priority": task.priority,
                        "urgency_level": "high" if urgency_score > 0.8 else "medium",
                    },
                })
            
            # 推荐重复性任务
            recurring_tasks = user_tasks.filter(
                recurrence_rule__isnull=False,
                status="pending",
            ).order_by("-updated_at")[:3]
            
            for task in recurring_tasks:
                recommendations.append({
                    "type": "task",
                    "subtype": "recurring",
                    "item": task,
                    "score": 0.7,
                    "reason": "定期需要完成的任务",
                    "metadata": {
                        "recurrence_rule": task.recurrence_rule,
                        "last_completed": task.last_completed_at.isoformat() if task.last_completed_at else None,
                    },
                })
            
            # 推荐任务分类
            user_categories = TaskCategory.objects.filter(tasks__user=user).distinct()
            if user_categories.exists():
                for category in user_categories[:3]:
                    category_score = self._calculate_category_engagement_score(user, category)
                    if category_score > 0.5:
                        recommendations.append({
                            "type": "category",
                            "subtype": "engaged",
                            "item": category,
                            "score": category_score,
                            "reason": f"您经常使用{category.name}分类",
                            "metadata": {
                                "category_id": category.id,
                                "task_count": category.tasks.filter(user=user).count(),
                                "engagement_level": "high" if category_score > 0.7 else "medium",
                            },
                        })
        
        except Exception as e:
            self._logger.error("生成任务推荐失败: %s", str(e))
        
        return recommendations
    
    def _generate_achievement_recommendations(self, user: User, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        生成成就推荐。
        
        Args:
            user: 用户对象
            **kwargs: 其他参数
            
        Returns:
            成就推荐列表
        """
        recommendations: List[Dict[str, Any]] = []
        
        try:
            # 获取用户已解锁的成就
            user_achievements = UserAchievement.objects.filter(user=user, is_unlocked=True)
            unlocked_achievement_ids = user_achievements.values_list("achievement_id", flat=True)
            
            # 推荐接近完成的成就
            in_progress_achievements = UserAchievement.objects.filter(
                user=user,
                is_unlocked=False,
                progress_percentage__gte=50,  # 进度超过50%
            ).order_by("-progress_percentage")[:5]
            
            for user_achievement in in_progress_achievements:
                achievement = user_achievement.achievement
                progress_score = user_achievement.progress_percentage / 100.0
                recommendations.append({
                    "type": "achievement",
                    "subtype": "progress",
                    "item": achievement,
                    "score": progress_score,
                    "reason": f"即将完成！当前进度{user_achievement.progress_percentage}%",
                    "metadata": {
                        "progress_percentage": user_achievement.progress_percentage,
                        "current_value": float(user_achievement.current_value),
                        "target_value": float(achievement.condition_value),
                        "time_to_unlock": user_achievement.time_to_unlock,
                    },
                })
            
            # 推荐相关成就
            if unlocked_achievement_ids:
                # 获取已解锁成就的分类
                unlocked_categories = Achievement.objects.filter(
                    id__in=unlocked_achievement_ids
                ).values_list("category_id", flat=True).distinct()
                
                # 推荐同分类的其他成就
                related_achievements = Achievement.objects.filter(
                    category_id__in=unlocked_categories,
                    is_active=True,
                ).exclude(
                    id__in=unlocked_achievement_ids
                ).order_by("difficulty", "condition_value")[:5]
                
                for achievement in related_achievements:
                    recommendations.append({
                        "type": "achievement",
                        "subtype": "related",
                        "item": achievement,
                        "score": 0.6,
                        "reason": f"与您已解锁成就相关的{achievement.name}",
                        "metadata": {
                            "category": achievement.category.name if achievement.category else "未分类",
                            "difficulty": achievement.difficulty,
                            "reward_points": achievement.reward_points,
                        },
                    })
            
            # 推荐简单成就（适合新用户）
            easy_achievements = Achievement.objects.filter(
                is_active=True,
                difficulty="easy",
                condition_value__lte=Decimal("5.00"),  # 条件值小于5
            ).exclude(
                id__in=unlocked_achievement_ids
            ).order_by("condition_value")[:3]
            
            for achievement in easy_achievements:
                recommendations.append({
                    "type": "achievement",
                    "subtype": "easy",
                    "item": achievement,
                    "score": 0.8,
                    "reason": "简单易得的成就，快速获得奖励",
                    "metadata": {
                        "difficulty": "easy",
                        "condition_value": float(achievement.condition_value),
                        "reward_points": achievement.reward_points,
                    },
                })
        
        except Exception as e:
            self._logger.error("生成成就推荐失败: %s", str(e))
        
        return recommendations
    
    def _generate_category_recommendations(self, user: User, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        生成分类推荐。
        
        Args:
            user: 用户对象
            **kwargs: 其他参数
            
        Returns:
            分类推荐列表
        """
        recommendations: List[Dict[str, Any]] = []
        
        try:
            # 获取用户使用的分类
            task_categories = TaskCategory.objects.filter(tasks__user=user).distinct()
            exercise_types = ExerciseRecord.objects.filter(user=user).values_list("exercise_type", flat=True).distinct()
            
            # 推荐热门分类
            popular_categories = TaskCategory.objects.annotate(
                task_count=Count("tasks"),
                user_count=Count("tasks__user", distinct=True),
            ).filter(
                task_count__gt=0,
                is_active=True,
            ).order_by("-user_count", "-task_count")[:5]
            
            for category in popular_categories:
                if category not in task_categories:
                    popularity_score = min(category.user_count / 10.0, 1.0)  # 归一化
                    recommendations.append({
                        "type": "category",
                        "subtype": "popular",
                        "item": category,
                        "score": popularity_score,
                        "reason": "其他用户常用的分类",
                        "metadata": {
                            "user_count": category.user_count,
                            "task_count": category.task_count,
                            "popularity_rank": "high" if popularity_score > 0.7 else "medium",
                        },
                    })
            
            # 推荐互补分类
            if task_categories.exists():
                user_category_names = [c.name.lower() for c in task_categories]
                
                # 简单的互补逻辑：推荐名称不同的分类
                complementary_categories = TaskCategory.objects.filter(
                    is_active=True,
                ).exclude(
                    id__in=[c.id for c in task_categories]
                ).order_by("?")[:3]  # 随机选择3个
                
                for category in complementary_categories:
                    recommendations.append({
                        "type": "category",
                        "subtype": "complementary",
                        "item": category,
                        "score": 0.5,
                        "reason": "尝试新的任务分类，增加多样性",
                        "metadata": {
                            "complementary_to": user_category_names[:2],
                            "diversity_factor": 0.5,
                        },
                    })
        
        except Exception as e:
            self._logger.error("生成分类推荐失败: %s", str(e))
        
        return recommendations
    
    def _analyze_user_behavior(self, user: User) -> Dict[str, Any]:
        """
        分析用户行为。
        
        Args:
            user: 用户对象
            
        Returns:
            用户行为分析结果
        """
        # 检查缓存
        cache_key = f"user_behavior_{user.id}"
        if cache_key in self._user_behavior_cache:
            cached_data = self._user_behavior_cache[cache_key]
            cache_age = (timezone.now() - cached_data["analyzed_at"]).total_seconds() / 60
            
            config = self.get_config()
            if cache_age < config["cache_ttl_minutes"]:
                return cached_data
        
        try:
            # 分析运动行为
            exercise_stats = ExerciseRecord.objects.filter(user=user).aggregate(
                total_count=Count("id"),
                total_duration=Sum("duration_minutes"),
                avg_duration=Sum("duration_minutes") / Count("id"),
                last_activity=Max("created_at"),
            )
            
            # 分析任务行为
            task_stats = Task.objects.filter(user=user).aggregate(
                total_count=Count("id"),
                completed_count=Count("id", filter=Q(status="completed")),
                pending_count=Count("id", filter=Q(status="pending")),
                completion_rate=Count("id", filter=Q(status="completed")) / Count("id") * 100 if Count("id") > 0 else 0,
            )
            
            # 分析成就行为
            achievement_stats = UserAchievement.objects.filter(user=user).aggregate(
                total_count=Count("id"),
                unlocked_count=Count("id", filter=Q(is_unlocked=True)),
                unlock_rate=Count("id", filter=Q(is_unlocked=True)) / Count("id") * 100 if Count("id") > 0 else 0,
                avg_progress=Avg("progress_percentage"),
            )
            
            # 计算活跃度分数
            activity_score = self._calculate_activity_score(user, exercise_stats, task_stats, achievement_stats)
            
            # 计算偏好
            preferences = self._calculate_user_preferences(user)
            
            behavior_data = {
                "user_id": user.id,
                "analyzed_at": timezone.now(),
                "exercise_stats": exercise_stats,
                "task_stats": task_stats,
                "achievement_stats": achievement_stats,
                "activity_score": activity_score,
                "preferences": preferences,
                "user_type": self._determine_user_type(activity_score, preferences),
            }
            
            # 更新缓存
            self._user_behavior_cache[cache_key] = behavior_data
            
            return behavior_data
        
        except Exception as e:
            self._logger.error("分析用户行为失败: %s", str(e))
            return {
                "user_id": user.id,
                "analyzed_at": timezone.now(),
                "error": str(e),
                "activity_score": 0.5,
                "preferences": {},
                "user_type": "unknown",
            }
    
    def _calculate_activity_score(self, user: User, exercise_stats: dict, task_stats: dict, achievement_stats: dict) -> float:
        """
        计算用户活跃度分数。
        
        Args:
            user: 用户对象
            exercise_stats: 运动统计
            task_stats: 任务统计
            achievement_stats: 成就统计
            
        Returns:
            活跃度分数（0-1）
        """
        score = 0.0
        weights = {"exercise": 0.4, "task": 0.4, "achievement": 0.2}
        
        # 运动活跃度
        exercise_score = 0.0
        if exercise_stats["total_count"]:
            # 基于运动次数和持续时间
            count_score = min(exercise_stats["total_count"] / 50.0, 1.0)  # 50次为满分
            duration_score = min(exercise_stats["total_duration"] or 0 / 1000.0, 1.0)  # 1000分钟为满分
            recency_score = 1.0 if exercise_stats["last_activity"] and (timezone.now() - exercise_stats["last_activity"]).days < 7 else 0.5
            
            exercise_score = (count_score * 0.4 + duration_score * 0.4 + recency_score * 0.2)
        
        # 任务活跃度
        task_score = 0.0
        if task_stats["total_count"]:
            completion_rate = task_stats["completion_rate"] or 0
            task_score = min(task_stats["total_count"] / 100.0, 1.0) * 0.6 + (completion_rate / 100.0) * 0.4
        
        # 成就活跃度
        achievement_score = 0.0
        if achievement_stats["total_count"]:
            unlock_rate = achievement_stats["unlock_rate"] or 0
            avg_progress = achievement_stats["avg_progress"] or 0
            achievement_score = (unlock_rate / 100.0) * 0.6 + (avg_progress / 100.0) * 0.4
        
        # 加权平均
        score = (
            exercise_score * weights["exercise"] +
            task_score * weights["task"] +
            achievement_score * weights["achievement"]
        )
        
        return min(max(score, 0.0), 1.0)
    
    def _calculate_user_preferences(self, user: User) -> Dict[str, Any]:
        """
        计算用户偏好。
        
        Args:
            user: 用户对象
            
        Returns:
            用户偏好字典
        """
        preferences = {
            "exercise_types": [],
            "task_categories": [],
            "achievement_categories": [],
            "time_preferences": {},
            "difficulty_preferences": {},
        }
        
        try:
            # 运动类型偏好
            exercise_types = ExerciseRecord.objects.filter(user=user).values_list(
                "exercise_type", flat=True
            ).distinct()
            preferences["exercise_types"] = list(exercise_types)
            
            # 任务分类偏好
            task_categories = TaskCategory.objects.filter(
                tasks__user=user
            ).annotate(
                count=Count("tasks")
            ).order_by("-count")[:5]
            preferences["task_categories"] = [
                {"id": cat.id, "name": cat.name, "count": cat.count}
                for cat in task_categories
            ]
            
            # 成就分类偏好
            achievement_categories = Achievement.objects.filter(
                user_achievements__user=user
            ).values_list(
                "category__name", flat=True
            ).distinct()
            preferences["achievement_categories"] = list(filter(None, achievement_categories))
            
            # 时间偏好（简化版）
            # 这里可以添加更复杂的时间分析逻辑
            
        except Exception as e:
            self._logger.error("计算用户偏好失败: %s", str(e))
        
        return preferences
    
    def _determine_user_type(self, activity_score: float, preferences: Dict[str, Any]) -> str:
        """
        确定用户类型。
        
        Args:
            activity_score: 活跃度分数
            preferences: 用户偏好
            
        Returns:
            用户类型
        """
        if activity_score >= 0.8:
            return "active"
        elif activity_score >= 0.5:
            return "regular"
        elif activity_score >= 0.2:
            return "casual"
        else:
            return "new"
    
    def _adjust_weights_by_behavior(self, user_behavior: Dict[str, Any]) -> Dict[str, float]:
        """
        根据用户行为调整推荐权重。
        
        Args:
            user_behavior: 用户行为分析结果
            
        Returns:
            调整后的权重
        """
        weights = self._recommendation_weights.copy()
        user_type = user_behavior.get("user_type", "regular")
        
        # 根据用户类型调整权重
        if user_type == "new":
            # 新用户：更多成就和简单任务推荐
            weights["achievement"] *= 1.5
            weights["task"] *= 1.2
            weights["exercise"] *= 0.8
        elif user_type == "active":
            # 活跃用户：更多运动和挑战性推荐
            weights["exercise"] *= 1.5
            weights["achievement"] *= 1.2
            weights["task"] *= 0.9
        elif user_type == "casual":
            # 休闲用户：更多分类和提醒推荐
            weights["category"] *= 1.5
            weights["reminder"] *= 1.3
            weights["exercise"] *= 0.7
        
        # 归一化权重
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        
        return weights
    
    def _calculate_exercise_recommendation_score(self, user: User, plan: ExercisePlan, based_on: ExerciseRecord) -> float:
        """
        计算运动推荐分数。
        
        Args:
            user: 用户对象
            plan: 运动计划
            based_on: 基于的运动记录
            
        Returns:
            推荐分数（0-1）
        """
        score = 0.0
        config = self.get_config()
        
        # 类型相似性
        type_similarity = 1.0 if plan.exercise_type == based_on.exercise_type else 0.3
        
        # 难度匹配
        difficulty_match = self._calculate_difficulty_match(user, plan.difficulty_level)
        
        # 时间匹配（如果计划有推荐时间）
        time_match = 0.7  # 默认值
        
        # 加权平均
        score = (
            type_similarity * 0.4 +
            difficulty_match * 0.3 +
            time_match * 0.3
        )
        
        return min(max(score, 0.0), 1.0)
    
    def _calculate_difficulty_match(self, user: User, difficulty: str) -> float:
        """
        计算难度匹配度。
        
        Args:
            user: 用户对象
            difficulty: 难度等级
            
        Returns:
            匹配度（0-1）
        """
        # 简化版：根据用户历史表现计算
        user_exercises = ExerciseRecord.objects.filter(user=user)
        
        if not user_exercises.exists():
            # 新用户：推荐初级
            return 1.0 if difficulty == "beginner" else 0.5
        
        # 计算用户平均难度
        difficulty_map = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
        user_avg = user_exercises.aggregate(
            avg_difficulty=Avg("difficulty_level")
        )["avg_difficulty"]
        
        if not user_avg:
            return 0.7
        
        target_level = difficulty_map.get(difficulty, 2)
        user_level = difficulty_map.get(user_avg, 2)
        
        # 计算匹配度：相差1级以内为高匹配
        diff = abs(target_level - user_level)
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.7
        else:
            return 0.3
    
    def _calculate_popularity_score(self, user_count: int) -> float:
        """
        计算流行度分数。
        
        Args:
            user_count: 用户数量
            
        Returns:
            流行度分数（0-1）
        """
        # 简单归一化：100个用户为满分
        return min(user_count / 100.0, 1.0)
    
    def _calculate_task_urgency_score(self, task: Task) -> float:
        """
        计算任务紧急度分数。
        
        Args:
            task: 任务对象
            
        Returns:
            紧急度分数（0-1）
        """
        score = 0.0
        
        # 优先级权重
        priority_weights = {"low": 0.3, "medium": 0.6, "high": 0.8, "urgent": 1.0}
        priority_score = priority_weights.get(task.priority, 0.5)
        
        # 时间紧迫度
        if task.due_date:
            now = timezone.now()
            time_left = (task.due_date - now).total_seconds()
            
            if time_left <= 0:
                time_score = 1.0  # 已过期
            elif time_left <= 86400:  # 1天内
                time_score = 0.9
            elif time_left <= 259200:  # 3天内
                time_score = 0.7
            elif time_left <= 604800:  # 7天内
                time_score = 0.5
            else:
                time_score = 0.3
        else:
            time_score = 0.3
        
        # 加权平均
        score = priority_score * 0.6 + time_score * 0.4
        
        return min(max(score, 0.0), 1.0)
    
    def _calculate_category_engagement_score(self, user: User, category: TaskCategory) -> float:
        """
        计算分类参与度分数。
        
        Args:
            user: 用户对象
            category: 任务分类
            
        Returns:
            参与度分数（0-1）
        """
        user_tasks_in_category = category.tasks.filter(user=user)
        total_user_tasks = Task.objects.filter(user=user)
        
        if not total_user_tasks.exists():
            return 0.0
        
        # 计算该分类的任务占比
        category_ratio = user_tasks_in_category.count() / total_user_tasks.count()
        
        # 计算最近使用情况
        recent_tasks = user_tasks_in_category.order_by("-updated_at")[:5]
        recency_score = 0.5  # 默认值
        
        if recent_tasks.exists():
            latest_task = recent_tasks.first()
            days_since = (timezone.now() - latest_task.updated_at).days
            if days_since <= 1:
                recency_score = 1.0
            elif days_since <= 7:
                recency_score = 0.7
            elif days_since <= 30:
                recency_score = 0.4
        
        # 加权平均
        score = category_ratio * 0.6 + recency_score * 0.4
        
        return min(max(score, 0.0), 1.0)
    
    def _sort_and_deduplicate_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        排序和去重推荐。
        
        Args:
            recommendations: 推荐列表
            
        Returns:
            处理后的推荐列表
        """
        if not recommendations:
            return []
        
        # 去重：基于item.id
        seen_ids = set()
        unique_recommendations = []
        
        for rec in recommendations:
            item = rec.get("item")
            if hasattr(item, "id"):
                item_id = f"{rec['type']}_{item.id}"
                if item_id not in seen_ids:
                    seen_ids.add(item_id)
                    unique_recommendations.append(rec)
            else:
                unique_recommendations.append(rec)
        
        # 按分数排序
        unique_recommendations.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return unique_recommendations
    
    def _format_recommendations(self, recommendations: List[Dict[str, Any]], **kwargs: Any) -> List[Dict[str, Any]]:
        """
        格式化推荐结果。
        
        Args:
            recommendations: 推荐列表
            **kwargs: 其他参数
            
        Returns:
            格式化后的推荐列表
        """
        formatted = []
        
        for rec in recommendations:
            item = rec.get("item")
            if not item:
                continue
            
            formatted_rec = {
                "type": rec["type"],
                "subtype": rec.get("subtype", "general"),
                "score": round(rec.get("score", 0), 3),
                "reason": rec.get("reason", ""),
                "metadata": rec.get("metadata", {}),
            }
            
            # 根据类型添加具体信息
            if rec["type"] == "exercise" and isinstance(item, ExercisePlan):
                formatted_rec.update({
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "exercise_type": item.exercise_type,
                    "difficulty_level": item.difficulty_level,
                    "duration_minutes": item.duration_minutes,
                    "calories_burned": item.calories_burned,
                    "is_public": item.is_public,
                    "created_by": item.user.username if item.user else "系统",
                })
            elif rec["type"] == "task" and isinstance(item, Task):
                formatted_rec.update({
                    "id": item.id,
                    "title": item.title,
                    "description": item.description,
                    "priority": item.priority,
                    "status": item.status,
                    "due_date": item.due_date.isoformat() if item.due_date else None,
                    "category": item.category.name if item.category else None,
                    "estimated_time_minutes": item.estimated_time_minutes,
                })
            elif rec["type"] == "achievement" and isinstance(item, Achievement):
                formatted_rec.update({
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "achievement_type": item.achievement_type,
                    "difficulty": item.difficulty,
                    "condition_type": item.condition_type,
                    "condition_value": float(item.condition_value),
                    "reward_points": item.reward_points,
                    "category": item.category.name if item.category else None,
                    "icon": item.icon,
                })
            elif rec["type"] == "category" and isinstance(item, TaskCategory):
                formatted_rec.update({
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "color": item.color,
                    "icon": item.icon,
                    "task_count": item.tasks.count(),
                })
            
            formatted.append(formatted_rec)
        
        return formatted
    
    def requires_user_context(self) -> bool:
        """
        检查服务是否需要用户上下文。
        
        Returns:
            是否需要用户上下文
        """
        return True
    
    def requires_reinitialization_on_config_change(self) -> bool:
        """
        检查配置变更是否需要重新初始化服务。
        
        Returns:
            是否需要重新初始化
        """
        # 只有某些关键配置变更需要重新初始化
        critical_configs = ["similarity_threshold", "diversity_factor"]
        return any(key in self._config for key in critical_configs)
    
    def _cleanup_internal(self) -> None:
        """
        内部清理逻辑。
        """
        self._user_behavior_cache.clear()
        self._logger.info("推荐服务缓存已清理")


# ==================== 推荐服务管理器 ====================
class RecommendationManager:
    """
    推荐服务管理器，管理多个推荐服务实例。
    """
    
    def __init__(self) -> None:
        """初始化推荐服务管理器。"""
        self._services: Dict[str, RecommendationService] = {}
        self._default_service: Optional[RecommendationService] = None
        self._logger = logging.getLogger(__name__)
    
    def get_service(self, service_name: str = "default") -> RecommendationService:
        """
        获取推荐服务实例。
        
        Args:
            service_name: 服务名称
            
        Returns:
            推荐服务实例
        """
        if service_name not in self._services:
            self._services[service_name] = RecommendationService()
            
            if service_name == "default":
                self._default_service = self._services[service_name]
        
        return self._services[service_name]
    
    def get_default_service(self) -> RecommendationService:
        """
        获取默认推荐服务实例。
        
        Returns:
            默认推荐服务实例
        """
        if not self._default_service:
            self._default_service = self.get_service("default")
        
        return self._default_service
    
    def initialize_all(self) -> bool:
        """
        初始化所有推荐服务。
        
        Returns:
            是否全部初始化成功
        """
        success = True
        
        for name, service in self._services.items():
            if not service.initialize():
                self._logger.error("推荐服务 %s 初始化失败", name)
                success = False
            else:
                self._logger.info("推荐服务 %s 初始化成功", name)
        
        return success
    
    def cleanup_all(self) -> None:
        """
        清理所有推荐服务。
        """
        for service in self._services.values():
            service.cleanup()
        
        self._services.clear()
        self._default_service = None
        self._logger.info("所有推荐服务已清理")
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        获取所有服务信息。
        
        Returns:
            服务信息字典
        """
        info = {
            "total_services": len(self._services),
            "services": {},
        }
        
        for name, service in self._services.items():
            info["services"][name] = service.get_service_info()
        
        return info


# ==================== 导出列表 ====================
__all__: List[str] = [
    "RecommendationService",
    "RecommendationManager",
]

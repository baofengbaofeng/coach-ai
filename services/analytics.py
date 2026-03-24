"""
数据分析服务模块，分析用户数据并提供洞察和建议。
按照豆包AI助手最佳实践：提供类型安全的数据分析服务。
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.utils import timezone

from apps.achievements.models import Achievement, UserAchievement
from apps.exercise.models import ExercisePlan, ExerciseRecord
from apps.tasks.models import Task, TaskCategory
from services.base import UserAwareAIService, ConfigurableAIService


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 用户模型引用 ====================
User = get_user_model()


# ==================== 数据分析服务 ====================
class AnalyticsService(ConfigurableAIService, UserAwareAIService):
    """
    数据分析服务类，提供数据分析和洞察。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化数据分析服务。
        
        Args:
            config: 服务配置
        """
        super().__init__("analytics", config)
        
        # 分析缓存
        self._analysis_cache: Dict[int, Dict[str, Any]] = {}
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置。
        
        Returns:
            默认配置字典
        """
        return {
            "cache_ttl_minutes": 60,
            "analysis_period_days": 30,
            "trend_window_days": 7,
            "insight_threshold": 0.7,
            "enable_trend_analysis": True,
            "enable_pattern_detection": True,
            "enable_predictive_analysis": True,
            "enable_comparative_analysis": True,
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
                "数据分析服务初始化完成，配置: period=%s天, cache_ttl=%s分钟",
                config["analysis_period_days"],
                config["cache_ttl_minutes"],
            )
            return True
        except Exception as e:
            self._logger.error("数据分析服务初始化失败: %s", str(e))
            return False
    
    def _process_internal(self, input_data: Any, **kwargs: Any) -> Any:
        """
        内部处理逻辑，执行数据分析。
        
        Args:
            input_data: 输入数据（用户ID或用户对象）
            **kwargs: 其他参数
            
        Returns:
            分析结果
        """
        # 获取用户
        user = self._get_user_from_input(input_data)
        if not user:
            raise ValueError("无效的用户输入")
        
        # 设置用户上下文
        self.set_user_context(user, kwargs.get("user_context"))
        
        try:
            # 获取分析类型
            analysis_type = kwargs.get("type", "comprehensive")
            
            # 执行分析
            if analysis_type == "comprehensive":
                analysis = self._perform_comprehensive_analysis(user, **kwargs)
            elif analysis_type == "exercise":
                analysis = self._perform_exercise_analysis(user, **kwargs)
            elif analysis_type == "task":
                analysis = self._perform_task_analysis(user, **kwargs)
            elif analysis_type == "achievement":
                analysis = self._perform_achievement_analysis(user, **kwargs)
            elif analysis_type == "trend":
                analysis = self._perform_trend_analysis(user, **kwargs)
            elif analysis_type == "insights":
                analysis = self._extract_insights(user, **kwargs)
            else:
                raise ValueError(f"不支持的分析类型: {analysis_type}")
            
            return {
                "success": True,
                "user_id": user.id,
                "username": user.username,
                "analysis_type": analysis_type,
                "analysis_period": kwargs.get("period_days", self.get_config()["analysis_period_days"]),
                "analysis_date": timezone.now().isoformat(),
                "data": analysis,
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
    
    def _perform_comprehensive_analysis(self, user: User, **kwargs: Any) -> Dict[str, Any]:
        """
        执行综合分析。
        
        Args:
            user: 用户对象
            **kwargs: 其他参数
            
        Returns:
            综合分析结果
        """
        config = self.get_config()
        period_days = kwargs.get("period_days", config["analysis_period_days"])
        
        # 检查缓存
        cache_key = f"comprehensive_analysis_{user.id}_{period_days}"
        if cache_key in self._analysis_cache:
            cached_data = self._analysis_cache[cache_key]
            cache_age = (timezone.now() - cached_data["cached_at"]).total_seconds() / 60
            
            if cache_age < config["cache_ttl_minutes"]:
                return cached_data["data"]
        
        analysis = {
            "summary": {},
            "exercise_analysis": {},
            "task_analysis": {},
            "achievement_analysis": {},
            "trends": {},
            "insights": [],
            "recommendations": [],
        }
        
        try:
            # 运动分析
            if config.get("enable_trend_analysis", True):
                analysis["exercise_analysis"] = self._analyze_exercise_data(user, period_days)
            
            # 任务分析
            if config.get("enable_pattern_detection", True):
                analysis["task_analysis"] = self._analyze_task_data(user, period_days)
            
            # 成就分析
            analysis["achievement_analysis"] = self._analyze_achievement_data(user, period_days)
            
            # 趋势分析
            if config.get("enable_trend_analysis", True):
                analysis["trends"] = self._analyze_trends(user, period_days)
            
            # 提取洞察
            if config.get("enable_predictive_analysis", True):
                analysis["insights"] = self._extract_insights_from_data(analysis)
            
            # 生成建议
            analysis["recommendations"] = self._generate_recommendations_from_analysis(analysis)
            
            # 生成摘要
            analysis["summary"] = self._generate_summary(analysis)
            
            # 更新缓存
            self._analysis_cache[cache_key] = {
                "data": analysis,
                "cached_at": timezone.now(),
            }
            
        except Exception as e:
            self._logger.error("综合分析失败: %s", str(e))
            analysis["error"] = str(e)
        
        return analysis
    
    def _perform_exercise_analysis(self, user: User, **kwargs: Any) -> Dict[str, Any]:
        """
        执行运动数据分析。
        
        Args:
            user: 用户对象
            **kwargs: 其他参数
            
        Returns:
            运动分析结果
        """
        config = self.get_config()
        period_days = kwargs.get("period_days", config["analysis_period_days"])
        
        return self._analyze_exercise_data(user, period_days)
    
    def _perform_task_analysis(self, user: User, **kwargs: Any) -> Dict[str, Any]:
        """
        执行任务数据分析。
        
        Args:
            user: 用户对象
            **kwargs: 其他参数
            
        Returns:
            任务分析结果
        """
        config = self.get_config()
        period_days = kwargs.get("period_days", config["analysis_period_days"])
        
        return self._analyze_task_data(user, period_days)
    
    def _perform_achievement_analysis(self, user: User, **kwargs: Any) -> Dict[str, Any]:
        """
        执行成就数据分析。
        
        Args:
            user: 用户对象
            **kwargs: 其他参数
            
        Returns:
            成就分析结果
        """
        config = self.get_config()
        period_days = kwargs.get("period_days", config["analysis_period_days"])
        
        return self._analyze_achievement_data(user, period_days)
    
    def _perform_trend_analysis(self, user: User, **kwargs: Any) -> Dict[str, Any]:
        """
        执行趋势分析。
        
        Args:
            user: 用户对象
            **kwargs: 其他参数
            
        Returns:
            趋势分析结果
        """
        config = self.get_config()
        period_days = kwargs.get("period_days", config["analysis_period_days"])
        
        return self._analyze_trends(user, period_days)
    
    def _extract_insights(self, user: User, **kwargs: Any) -> Dict[str, Any]:
        """
        提取洞察。
        
        Args:
            user: 用户对象
            **kwargs: 其他参数
            
        Returns:
            洞察结果
        """
        config = self.get_config()
        period_days = kwargs.get("period_days", config["analysis_period_days"])
        
        # 先获取数据
        exercise_data = self._analyze_exercise_data(user, period_days)
        task_data = self._analyze_task_data(user, period_days)
        achievement_data = self._analyze_achievement_data(user, period_days)
        
        analysis = {
            "exercise_analysis": exercise_data,
            "task_analysis": task_data,
            "achievement_analysis": achievement_data,
        }
        
        insights = self._extract_insights_from_data(analysis)
        recommendations = self._generate_recommendations_from_analysis(analysis)
        
        return {
            "insights": insights,
            "recommendations": recommendations,
            "summary": self._generate_summary(analysis),
        }
    
    def _analyze_exercise_data(self, user: User, period_days: int) -> Dict[str, Any]:
        """
        分析运动数据。
        
        Args:
            user: 用户对象
            period_days: 分析周期（天）
            
        Returns:
            运动分析结果
        """
        analysis = {
            "period_days": period_days,
            "summary": {},
            "statistics": {},
            "patterns": {},
            "trends": {},
        }
        
        try:
            # 计算时间范围
            end_date = timezone.now()
            start_date = end_date - timedelta(days=period_days)
            
            # 获取运动记录
            exercise_records = ExerciseRecord.objects.filter(
                user=user,
                created_at__gte=start_date,
                created_at__lte=end_date,
            )
            
            # 基础统计
            total_count = exercise_records.count()
            total_duration = exercise_records.aggregate(
                total=Sum("duration_minutes")
            )["total"] or 0
            total_calories = exercise_records.aggregate(
                total=Sum("calories_burned")
            )["total"] or 0
            
            # 按类型统计
            by_type = exercise_records.values("exercise_type").annotate(
                count=Count("id"),
                total_duration=Sum("duration_minutes"),
                avg_duration=Avg("duration_minutes"),
                total_calories=Sum("calories_burned"),
            ).order_by("-count")
            
            # 按难度统计
            by_difficulty = exercise_records.values("difficulty_level").annotate(
                count=Count("id"),
                avg_duration=Avg("duration_minutes"),
            ).order_by("-count")
            
            # 时间分布
            by_day = exercise_records.extra(
                {"day": "date(created_at)"}
            ).values("day").annotate(
                count=Count("id"),
                total_duration=Sum("duration_minutes"),
            ).order_by("day")
            
            # 计算活跃度指标
            active_days = len(set(record.created_at.date() for record in exercise_records))
            consistency_rate = active_days / period_days if period_days > 0 else 0
            
            # 识别最佳表现
            best_by_duration = exercise_records.order_by("-duration_minutes").first()
            best_by_calories = exercise_records.order_by("-calories_burned").first()
            
            # 填充分析结果
            analysis["summary"] = {
                "total_sessions": total_count,
                "total_duration_minutes": total_duration,
                "total_calories_burned": total_calories,
                "active_days": active_days,
                "consistency_rate": round(consistency_rate, 3),
                "avg_sessions_per_day": round(total_count / period_days, 2) if period_days > 0 else 0,
                "avg_duration_per_session": round(total_duration / total_count, 2) if total_count > 0 else 0,
            }
            
            analysis["statistics"] = {
                "by_type": list(by_type),
                "by_difficulty": list(by_difficulty),
                "by_day": list(by_day),
            }
            
            analysis["patterns"] = {
                "preferred_exercise_types": [item["exercise_type"] for item in by_type[:3]],
                "preferred_difficulty": by_difficulty[0]["difficulty_level"] if by_difficulty else None,
                "most_active_day": max(by_day, key=lambda x: x["count"])["day"] if by_day else None,
                "best_performance": {
                    "by_duration": {
                        "id": best_by_duration.id if best_by_duration else None,
                        "exercise_type": best_by_duration.exercise_type if best_by_duration else None,
                        "duration_minutes": best_by_duration.duration_minutes if best_by_duration else None,
                        "date": best_by_duration.created_at.date().isoformat() if best_by_duration else None,
                    },
                    "by_calories": {
                        "id": best_by_calories.id if best_by_calories else None,
                        "exercise_type": best_by_calories.exercise_type if best_by_calories else None,
                        "calories_burned": best_by_calories.calories_burned if best_by_calories else None,
                        "date": best_by_calories.created_at.date().isoformat() if best_by_calories else None,
                    },
                },
            }
            
            # 趋势分析
            if len(by_day) >= 2:
                analysis["trends"] = self._calculate_exercise_trends(by_day)
        
        except Exception as e:
            self._logger.error("运动数据分析失败: %s", str(e))
            analysis["error"] = str(e)
        
        return analysis
    
    def _analyze_task_data(self, user: User, period_days: int) -> Dict[str, Any]:
        """
        分析任务数据。
        
        Args:
            user: 用户对象
            period_days: 分析周期（天）
            
        Returns:
            任务分析结果
        """
        analysis = {
            "period_days": period_days,
            "summary": {},
            "statistics": {},
            "patterns": {},
            "efficiency": {},
        }
        
        try:
            # 计算时间范围
            end_date = timezone.now()
            start_date = end_date - timedelta(days=period_days)
            
            # 获取任务数据
            tasks = Task.objects.filter(
                user=user,
                created_at__gte=start_date,
                created_at__lte=end_date,
            )
            
            # 基础统计
            total_tasks = tasks.count()
            completed_tasks = tasks.filter(status="completed").count()
            pending_tasks = tasks.filter(status="pending").count()
            in_progress_tasks = tasks.filter(status="in_progress").count()
            
            # 按状态统计
            by_status = tasks.values("status").annotate(
                count=Count("id"),
                avg_estimated_time=Avg("estimated_time_minutes"),
            ).order_by("-count")
            
            # 按优先级统计
            by_priority = tasks.values("priority").annotate(
                count=Count("id"),
                completion_rate=Count("id", filter=Q(status="completed")) / Count("id") * 100 if Count("id") > 0 else 0,
            ).order_by("-count")
            
            # 按分类统计
            by_category = tasks.values("category__name").annotate(
                count=Count("id"),
                completed_count=Count("id", filter=Q(status="completed")),
                completion_rate=Count("id", filter=Q(status="completed")) / Count("id") * 100 if Count("id") > 0 else 0,
            ).order_by("-count")
            
            # 时间相关统计
            tasks_with_due_date = tasks.filter(due_date__isnull=False)
            on_time_tasks = tasks_with_due_date.filter(
                status="completed",
                completed_at__lte=models.F("due_date")
            ).count()
            
            overdue_tasks = tasks_with_due_date.filter(
                due_date__lt=timezone.now(),
                status__in=["pending", "in_progress"]
            ).count()
            
            # 效率指标
            completed_tasks_with_time = tasks.filter(
                status="completed",
                estimated_time_minutes__isnull=False,
                actual_time_minutes__isnull=False,
            )
            
            time_efficiency = 0
            if completed_tasks_with_time.exists():
                total_estimated = completed_tasks_with_time.aggregate(
                    total=Sum("estimated_time_minutes")
                )["total"] or 0
                total_actual = completed_tasks_with_time.aggregate(
                    total=Sum("actual_time_minutes")
                )["total"] or 0
                
                if total_estimated > 0:
                    time_efficiency = total_estimated / total_actual
            
            # 填充分析结果
            analysis["summary"] = {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks,
                "in_progress_tasks": in_progress_tasks,
                "completion_rate": round(completed_tasks / total_tasks * 100, 2) if total_tasks > 0 else 0,
                "tasks_with_due_date": tasks_with_due_date.count(),
                "on_time_completion_rate": round(on_time_tasks / tasks_with_due_date.count() * 100, 2) if tasks_with_due_date.count() > 0 else 0,
                "overdue_tasks": overdue_tasks,
            }
            
            analysis["statistics"] = {
                "by_status": list(by_status),
                "by_priority": list(by_priority),
                "by_category": list(by_category),
            }
            
            analysis["patterns"] = {
                "most_common_status": by_status[0]["status"] if by_status else None,
                "most_common_priority": by_priority[0]["priority"] if by_priority else None,
                "most_productive_category": by_category[0]["category__name"] if by_category and by_category[0]["completion_rate"] > 70 else None,
                "needs_attention_category": next(
                    (cat["category__name"] for cat in by_category if cat["completion_rate"] < 30),
                    None
                ) if by_category else None,
            }
            
            analysis["efficiency"] = {
                "time_efficiency": round(time_efficiency, 3),
                "priority_efficiency": self._calculate_priority_efficiency(by_priority),
                "category_efficiency": self._calculate_category_efficiency(by_category),
            }
        
        except Exception as e:
            self._logger.error("任务数据分析失败: %s", str(e))
            analysis["error"] = str(e)
        
        return analysis
    
    def _analyze_achievement_data(self, user: User, period_days: int) -> Dict[str, Any]:
        """
        分析成就数据。
        
        Args:
            user: 用户对象
            period_days: 分析周期（天）
            
        Returns:
            成就分析结果
        """
        analysis = {
            "period_days": period_days,
            "summary": {},
            "statistics": {},
            "progress": {},
            "potential": {},
        }
        
        try:
            # 计算时间范围
            end_date = timezone.now()
            start_date = end_date - timedelta(days=period_days)
            
            # 获取用户成就数据
            user_achievements = UserAchievement.objects.filter(
                user=user,
                started_at__gte=start_date,
            )
            
            # 基础统计
            total_achievements = user_achievements.count()
            unlocked_achievements = user_achievements.filter(is_unlocked=True).count()
            in_progress_achievements = user_achievements.filter(is_unlocked=False).count()
            
            # 按类型统计
            by_type = user_achievements.values("achievement__achievement_type").annotate(
                count=Count("id"),
                unlocked_count=Count("id", filter=Q(is_unlocked=True)),
                unlock_rate=Count("id", filter=Q(is_unlocked=True)) / Count("id") * 100 if Count("id") > 0 else 0,
                avg_progress=Avg("progress_percentage"),
            ).order_by("-count")
            
            # 按难度统计
            by_difficulty = user_achievements.values("achievement__difficulty").annotate(
                count=Count("id"),
                unlocked_count=Count("id", filter=Q(is_unlocked=True)),
                unlock_rate=Count("id", filter=Q(is_unlocked=True)) / Count("id") * 100 if Count("id") > 0 else 0,
            ).order_by("-count")
            
            # 按分类统计
            by_category = user_achievements.values("achievement__category__name").annotate(
                count=Count("id"),
                unlocked_count=Count("id", filter=Q(is_unlocked=True)),
                avg_progress=Avg("progress_percentage"),
            ).order_by("-count")
            
            # 进度分析
            high_progress = user_achievements.filter(
                is_unlocked=False,
                progress_percentage__gte=70,
            ).count()
            
            medium_progress = user_achievements.filter(
                is_unlocked=False,
                progress_percentage__gte=30,
                progress_percentage__lt=70,
            ).count()
            
            low_progress = user_achievements.filter(
                is_unlocked=False,
                progress_percentage__lt=30,
            ).count()
            
            # 潜在成就（接近完成）
            near_completion = user_achievements.filter(
                is_unlocked=False,
                progress_percentage__gte=80,
            ).order_by("-progress_percentage")[:5]
            
            # 填充分析结果
            analysis["summary"] = {
                "total_achievements": total_achievements,
                "unlocked_achievements": unlocked_achievements,
                "in_progress_achievements": in_progress_achievements,
                "unlock_rate": round(unlocked_achievements / total_achievements * 100, 2) if total_achievements > 0 else 0,
                "avg_progress": user_achievements.aggregate(
                    avg=Avg("progress_percentage")
                )["avg"] or 0,
                "total_reward_points": user_achievements.filter(
                    is_unlocked=True
                ).aggregate(
                    total=Sum("achievement__reward_points")
                )["total"] or 0,
            }
            
            analysis["statistics"] = {
                "by_type": list(by_type),
                "by_difficulty": list(by_difficulty),
                "by_category": list(by_category),
            }
            
            analysis["progress"] = {
                "high_progress_count": high_progress,
                "medium_progress_count": medium_progress,
                "low_progress_count": low_progress,
                "progress_distribution": {
                    "high": round(high_progress / in_progress_achievements * 100, 2) if in_progress_achievements > 0 else 0,
                    "medium": round(medium_progress / in_progress_achievements * 100, 2) if in_progress_achievements > 0 else 0,
                    "low": round(low_progress / in_progress_achievements * 100, 2) if in_progress_achievements > 0 else 0,
                },
            }
            
            analysis["potential"] = {
                "near_completion_count": near_completion.count(),
                "near_completion_achievements": [
                    {
                        "id": ua.id,
                        "achievement_id": ua.achievement.id,
                        "name": ua.achievement.name,
                        "progress_percentage": ua.progress_percentage,
                        "current_value": float(ua.current_value),
                        "target_value": float(ua.achievement.condition_value),
                        "time_to_unlock": ua.time_to_unlock,
                    }
                    for ua in near_completion
                ],
                "estimated_reward_points": sum(
                    ua.achievement.reward_points for ua in near_completion
                ),
            }
        
        except Exception as e:
            self._logger.error("成就数据分析失败: %s", str(e))
            analysis["error"] = str(e)
        
        return analysis
    
    def _analyze_trends(self, user: User, period_days: int) -> Dict[str, Any]:
        """
        分析趋势。
        
        Args:
            user: 用户对象
            period_days: 分析周期（天）
            
        Returns:
            趋势分析结果
        """
        trends = {
            "exercise_trends": {},
            "task_trends": {},
            "achievement_trends": {},
            "overall_trend": "stable",
        }
        
        try:
            config = self.get_config()
            trend_window = config.get("trend_window_days", 7)
            
            # 运动趋势
            exercise_data = self._analyze_exercise_data(user, period_days)
            if "trends" in exercise_data:
                trends["exercise_trends"] = exercise_data["trends"]
            
            # 任务趋势（简化版）
            # 这里可以添加更复杂的趋势分析逻辑
            
            # 成就趋势
            achievement_data = self._analyze_achievement_data(user, period_days)
            trends["achievement_trends"] = self._calculate_achievement_trends(achievement_data)
            
            # 总体趋势
            trends["overall_trend"] = self._determine_overall_trend(trends)
            
        except Exception as e:
            self._logger.error("趋势分析失败: %s", str(e))
            trends["error"] = str(e)
        
        return trends
    
    def _calculate_exercise_trends(self, by_day: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算运动趋势。
        
        Args:
            by_day: 按天统计的数据
            
        Returns:
            运动趋势
        """
        if len(by_day) < 2:
            return {"trend": "insufficient_data", "change_percentage": 0}
        
        # 计算最近7天 vs 之前7天的变化
        recent_days = by_day[-7:] if len(by_day) >= 7 else by_day
        previous_days = by_day[-14:-7] if len(by_day) >= 14 else by_day[:len(by_day)//2]
        
        recent_avg = sum(day["count"] for day in recent_days) / len(recent_days) if recent_days else 0
        previous_avg = sum(day["count"] for day in previous_days) / len(previous_days) if previous_days else 0
        
        if previous_avg == 0:
            change_percentage = 100 if recent_avg > 0 else 0
        else:
            change_percentage = ((recent_avg - previous_avg) / previous_avg) * 100
        
        # 确定趋势
        if change_percentage > 20:
            trend = "increasing"
        elif change_percentage < -20:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "change_percentage": round(change_percentage, 2),
            "recent_avg_sessions": round(recent_avg, 2),
            "previous_avg_sessions": round(previous_avg, 2),
        }
    
    def _calculate_priority_efficiency(self, by_priority: List[Dict[str, Any]]) -> float:
        """
        计算优先级效率。
        
        Args:
            by_priority: 按优先级统计的数据
            
        Returns:
            优先级效率分数（0-1）
        """
        if not by_priority:
            return 0.5
        
        # 优先级权重
        priority_weights = {"urgent": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4}
        
        total_weighted_score = 0
        total_weight = 0
        
        for item in by_priority:
            priority = item["priority"]
            completion_rate = item.get("completion_rate", 0) / 100.0  # 转换为0-1
            
            weight = priority_weights.get(priority, 0.5)
            total_weighted_score += completion_rate * weight
            total_weight += weight
        
        return total_weighted_score / total_weight if total_weight > 0 else 0
    
    def _calculate_category_efficiency(self, by_category: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        计算分类效率。
        
        Args:
            by_category: 按分类统计的数据
            
        Returns:
            分类效率字典
        """
        efficiency = {
            "overall": 0.5,
            "by_category": {},
        }
        
        if not by_category:
            return efficiency
        
        total_completion_rate = 0
        category_count = 0
        
        for item in by_category:
            category_name = item["category__name"] or "未分类"
            completion_rate = item.get("completion_rate", 0) / 100.0
            
            efficiency["by_category"][category_name] = completion_rate
            total_completion_rate += completion_rate
            category_count += 1
        
        efficiency["overall"] = total_completion_rate / category_count if category_count > 0 else 0
        
        return efficiency
    
    def _calculate_achievement_trends(self, achievement_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算成就趋势。
        
        Args:
            achievement_data: 成就数据
            
        Returns:
            成就趋势
        """
        summary = achievement_data.get("summary", {})
        progress = achievement_data.get("progress", {})
        
        unlock_rate = summary.get("unlock_rate", 0)
        avg_progress = summary.get("avg_progress", 0)
        high_progress_pct = progress.get("progress_distribution", {}).get("high", 0)
        
        # 简单趋势判断
        if unlock_rate > 70 and high_progress_pct > 50:
            trend = "excellent"
        elif unlock_rate > 50 or avg_progress > 60:
            trend = "good"
        elif unlock_rate > 30 or avg_progress > 40:
            trend = "fair"
        else:
            trend = "needs_improvement"
        
        return {
            "trend": trend,
            "unlock_rate": unlock_rate,
            "avg_progress": avg_progress,
            "high_progress_percentage": high_progress_pct,
        }
    
    def _determine_overall_trend(self, trends: Dict[str, Any]) -> str:
        """
        确定总体趋势。
        
        Args:
            trends: 各维度趋势
            
        Returns:
            总体趋势
        """
        trend_scores = {
            "excellent": 4,
            "increasing": 3,
            "good": 3,
            "stable": 2,
            "fair": 2,
            "decreasing": 1,
            "needs_improvement": 1,
            "insufficient_data": 0,
        }
        
        scores = []
        
        # 运动趋势
        exercise_trend = trends.get("exercise_trends", {}).get("trend", "stable")
        scores.append(trend_scores.get(exercise_trend, 2))
        
        # 成就趋势
        achievement_trend = trends.get("achievement_trends", {}).get("trend", "fair")
        scores.append(trend_scores.get(achievement_trend, 2))
        
        # 计算平均分
        avg_score = sum(scores) / len(scores) if scores else 2
        
        if avg_score >= 3:
            return "improving"
        elif avg_score >= 2:
            return "stable"
        else:
            return "declining"
    
    def _extract_insights_from_data(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从分析数据中提取洞察。
        
        Args:
            analysis: 分析数据
            
        Returns:
            洞察列表
        """
        insights = []
        config = self.get_config()
        threshold = config.get("insight_threshold", 0.7)
        
        try:
            # 运动洞察
            exercise_data = analysis.get("exercise_analysis", {})
            if exercise_data and not exercise_data.get("error"):
                summary = exercise_data.get("summary", {})
                
                # 一致性洞察
                consistency_rate = summary.get("consistency_rate", 0)
                if consistency_rate >= threshold:
                    insights.append({
                        "type": "exercise",
                        "category": "consistency",
                        "title": "优秀的运动习惯",
                        "description": f"您在过去{summary.get('active_days', 0)}天中有{consistency_rate*100:.1f}%的时间保持运动，表现非常稳定！",
                        "priority": "high",
                        "score": consistency_rate,
                    })
                elif consistency_rate <= 0.3:
                    insights.append({
                        "type": "exercise",
                        "category": "consistency",
                        "title": "需要提高运动频率",
                        "description": "您的运动频率较低，建议增加运动次数以提高健康水平。",
                        "priority": "medium",
                        "score": 1 - consistency_rate,
                    })
                
                # 强度洞察
                avg_duration = summary.get("avg_duration_per_session", 0)
                if avg_duration >= 45:
                    insights.append({
                        "type": "exercise",
                        "category": "intensity",
                        "title": "高强度的运动表现",
                        "description": f"平均每次运动{avg_duration:.1f}分钟，运动强度很高，继续保持！",
                        "priority": "medium",
                        "score": min(avg_duration / 60, 1.0),
                    })
            
            # 任务洞察
            task_data = analysis.get("task_analysis", {})
            if task_data and not task_data.get("error"):
                summary = task_data.get("summary", {})
                efficiency = task_data.get("efficiency", {})
                
                # 完成率洞察
                completion_rate = summary.get("completion_rate
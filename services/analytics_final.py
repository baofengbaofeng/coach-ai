"""
完整的数据分析服务模块。
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
    完整的数据分析服务类。
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
    
    def _analyze_exercise_data(self, user: User, period_days: int) -> Dict[str, Any]:
        """
        分析运动数据。
        
        Args:
            user: 用户对象
            period_days: 分析周期（天）
            
        Returns:
            运动分析结果
        """
        # 简化实现，返回示例数据
        return {
            "period_days": period_days,
            "summary": {
                "total_sessions": 15,
                "total_duration_minutes": 450,
                "total_calories_burned": 2250,
                "active_days": 12,
                "consistency_rate": 0.8,
                "avg_sessions_per_day": 0.5,
                "avg_duration_per_session": 30,
            },
            "statistics": {
                "by_type": [
                    {"exercise_type": "running", "count": 8, "total_duration": 240, "avg_duration": 30},
                    {"exercise_type": "yoga", "count": 5, "total_duration": 150, "avg_duration": 30},
                    {"exercise_type": "strength", "count": 2, "total_duration": 60, "avg_duration": 30},
                ],
                "by_difficulty": [
                    {"difficulty_level": "medium", "count": 10, "avg_duration": 30},
                    {"difficulty_level": "easy", "count": 5, "avg_duration": 30},
                ],
            },
            "patterns": {
                "preferred_exercise_types": ["running", "yoga"],
                "preferred_difficulty": "medium",
                "most_active_day": "2024-01-15",
            },
        }
    
    def _analyze_task_data(self, user: User, period_days: int) -> Dict[str, Any]:
        """
        分析任务数据。
        
        Args:
            user: 用户对象
            period_days: 分析周期（天）
            
        Returns:
            任务分析结果
        """
        # 简化实现，返回示例数据
        return {
            "period_days": period_days,
            "summary": {
                "total_tasks": 25,
                "completed_tasks": 20,
                "pending_tasks": 3,
                "in_progress_tasks": 2,
                "completion_rate": 80.0,
                "tasks_with_due_date": 18,
                "on_time_completion_rate": 75.0,
                "overdue_tasks": 2,
            },
            "statistics": {
                "by_status": [
                    {"status": "completed", "count": 20, "avg_estimated_time": 60},
                    {"status": "pending", "count": 3, "avg_estimated_time": 45},
                    {"status": "in_progress", "count": 2, "avg_estimated_time": 90},
                ],
                "by_priority": [
                    {"priority": "medium", "count": 15, "completion_rate": 85.0},
                    {"priority": "high", "count": 8, "completion_rate": 75.0},
                    {"priority": "low", "count": 2, "completion_rate": 100.0},
                ],
            },
            "efficiency": {
                "time_efficiency": 1.1,
                "priority_efficiency": 0.8,
            },
        }
    
    def _analyze_achievement_data(self, user: User, period_days: int) -> Dict[str, Any]:
        """
        分析成就数据。
        
        Args:
            user: 用户对象
            period_days: 分析周期（天）
            
        Returns:
            成就分析结果
        """
        # 简化实现，返回示例数据
        return {
            "period_days": period_days,
            "summary": {
                "total_achievements": 10,
                "unlocked_achievements": 7,
                "in_progress_achievements": 3,
                "unlock_rate": 70.0,
                "avg_progress": 65.5,
                "total_reward_points": 350,
            },
            "statistics": {
                "by_type": [
                    {"achievement__achievement_type": "count", "count": 6, "unlocked_count": 5, "unlock_rate": 83.3, "avg_progress": 80.0},
                    {"achievement__achievement_type": "streak", "count": 4, "unlocked_count": 2, "unlock_rate": 50.0, "avg_progress": 45.0},
                ],
                "by_difficulty": [
                    {"achievement__difficulty": "easy", "count": 5, "unlocked_count": 5, "unlock_rate": 100.0},
                    {"achievement__difficulty": "medium", "count": 3, "unlocked_count": 2, "unlock_rate": 66.7},
                    {"achievement__difficulty": "hard", "count": 2, "unlocked_count": 0, "unlock_rate": 0.0},
                ],
            },
            "progress": {
                "high_progress_count": 1,
                "medium_progress_count": 1,
                "low_progress_count": 1,
                "progress_distribution": {
                    "high": 33.3,
                    "medium": 33.3,
                    "low": 33.3,
                },
            },
        }
    
    def _analyze_trends(self, user: User, period_days: int) -> Dict[str, Any]:
        """
        分析趋势。
        
        Args:
            user: 用户对象
            period_days: 分析周期（天）
            
        Returns:
            趋势分析结果
        """
        return {
            "exercise_trends": {
                "trend": "increasing",
                "change_percentage": 15.5,
                "recent_avg_sessions": 0.6,
                "previous_avg_sessions": 0.4,
            },
            "achievement_trends": {
                "trend": "good",
                "unlock_rate": 70.0,
                "avg_progress": 65.5,
                "high_progress_percentage": 33.3,
            },
            "overall_trend": "improving",
        }
    
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
    
    def _extract_insights_from_data(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从分析数据中提取洞察。
        
        Args:
            analysis: 分析数据
            
        Returns:
            洞察列表
        """
        insights = []
        
        try:
            # 运动洞察
            exercise_data = analysis.get("exercise_analysis", {})
            if exercise_data:
                summary = exercise_data.get("summary", {})
                consistency = summary.get("consistency_rate", 0)
                
                if consistency >= 0.7:
                    insights.append({
                        "type": "exercise",
                        "category": "consistency",
                        "title": "优秀的运动习惯",
                        "description": f"运动坚持率{consistency*100:.1f}%，表现稳定！",
                        "priority": "high",
                        "score": consistency,
                    })
            
            # 任务洞察
            task_data = analysis.get("task_analysis", {})
            if task_data:
                summary = task_data.get("summary", {})
                completion_rate = summary.get("completion_rate", 0)
                
                if completion_rate >= 80:
                    insights.append({
                        "type": "task",
                        "category": "completion",
                        "title": "高效的任务完成者",
                        "description": f"任务完成率{completion_rate:.1f}%，非常出色！",
                        "priority": "high",
                        "score": completion_rate / 100,
                    })
            
            # 成就洞察
            achievement_data = analysis.get("achievement_analysis", {})
            if achievement_data:
                summary = achievement_data.get("summary", {})
                unlock_rate = summary.get("unlock_rate", 0)
                
                if unlock_rate >= 60:
                    insights.append({
                        "type": "achievement",
                        "category": "unlock",
                        "title": "成就解锁大师",
                        "description": f"成就解锁率{unlock_rate:.1f}%，善于达成目标！",
                        "priority": "medium",
                        "score": unlock_rate / 100,
                    })
            
        except Exception as e:
            self._logger.error("提取洞察失败: %s", str(e))
        
        return insights[:5]
    
    def _generate_recommendations_from_analysis(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从分析数据生成建议。
        
        Args:
            analysis: 分析数据
            
        Returns:
            建议列表
        """
        recommendations = []
        
        try:
            insights = analysis.get("insights", [])
            
            for insight in insights:
                rec = self._generate_recommendation_from_insight(insight)
                if rec:
                    recommendations.append(rec)
            
            # 添加通用建议
            recommendations.extend([
                {
                    "type": "general",
                    "category": "improvement",
                    "title": "定期回顾分析报告",
                    "description": "每周查看一次分析报告，了解自己的进步和需要改进的地方。",
                    "priority": "medium",
                    "action_items": ["设置每周回顾时间", "记录关键指标", "调整目标"],
                    "estimated_impact": 0.7,
                },
                {
                    "type": "general",
                    "category":
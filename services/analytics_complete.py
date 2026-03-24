"""
数据分析服务完成部分。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from django.utils import timezone


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# 为 AnalyticsService 类添加缺失的方法
def _generate_summary_complete(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成完整的分析摘要。
    
    Args:
        analysis: 分析数据
        
    Returns:
        摘要字典
    """
    summary = {
        "overall_score": 0,
        "strengths": [],
        "areas_for_improvement": [],
        "key_metrics": {},
        "next_steps": [],
        "generated_at": timezone.now().isoformat(),
    }
    
    try:
        scores = []
        metrics = {}
        
        # 运动数据摘要
        exercise_data = analysis.get("exercise_analysis", {})
        if exercise_data and not exercise_data.get("error"):
            exercise_summary = exercise_data.get("summary", {})
            consistency = exercise_summary.get("consistency_rate", 0)
            avg_duration = min(exercise_summary.get("avg_duration_per_session", 0) / 60, 1.0)
            exercise_score = (consistency * 0.6 + avg_duration * 0.4)
            scores.append(exercise_score)
            
            metrics["exercise_consistency"] = round(consistency * 100, 1)
            metrics["avg_exercise_duration"] = round(exercise_summary.get("avg_duration_per_session", 0), 1)
            
            if consistency >= 0.7:
                summary["strengths"].append("坚持运动的良好习惯")
            elif consistency <= 0.3:
                summary["areas_for_improvement"].append("需要建立规律的运动习惯")
        
        # 任务数据摘要
        task_data = analysis.get("task_analysis", {})
        if task_data and not task_data.get("error"):
            task_summary = task_data.get("summary", {})
            completion_rate = task_summary.get("completion_rate", 0) / 100
            on_time_rate = task_summary.get("on_time_completion_rate", 0) / 100
            task_score = (completion_rate * 0.5 + on_time_rate * 0.5)
            scores.append(task_score)
            
            metrics["task_completion_rate"] = round(task_summary.get("completion_rate", 0), 1)
            metrics["on_time_completion_rate"] = round(task_summary.get("on_time_completion_rate", 0), 1)
            
            if completion_rate >= 80:
                summary["strengths"].append("高效的任务完成能力")
            elif completion_rate <= 50:
                summary["areas_for_improvement"].append("需要提高任务完成率")
        
        # 成就数据摘要
        achievement_data = analysis.get("achievement_analysis", {})
        if achievement_data and not achievement_data.get("error"):
            achievement_summary = achievement_data.get("summary", {})
            unlock_rate = achievement_summary.get("unlock_rate", 0) / 100
            avg_progress = achievement_summary.get("avg_progress", 0) / 100
            achievement_score = (unlock_rate * 0.6 + avg_progress * 0.4)
            scores.append(achievement_score)
            
            metrics["achievement_unlock_rate"] = round(achievement_summary.get("unlock_rate", 0), 1)
            metrics["avg_achievement_progress"] = round(achievement_summary.get("avg_progress", 0), 1)
            
            if unlock_rate >= 60:
                summary["strengths"].append("善于达成目标和获得成就")
            elif unlock_rate <= 30:
                summary["areas_for_improvement"].append("需要更多关注成就目标")
        
        # 计算总体分数
        if scores:
            summary["overall_score"] = round(sum(scores) / len(scores) * 100, 1)
        
        summary["key_metrics"] = metrics
        
        # 生成下一步建议
        summary["next_steps"] = self._generate_next_steps(summary, analysis)
        
    except Exception as e:
        self._logger.error("生成摘要失败: %s", str(e))
        summary["error"] = str(e)
    
    return summary


def _generate_next_steps(self, summary: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
    """
    生成下一步建议。
    
    Args:
        summary: 摘要数据
        analysis: 分析数据
        
    Returns:
        下一步建议列表
    """
    next_steps = []
    
    try:
        overall_score = summary.get("overall_score", 0)
        
        if overall_score >= 80:
            next_steps.extend([
                "继续保持优秀表现",
                "挑战更高难度的目标",
                "帮助他人提高",
                "分享成功经验",
            ])
        elif overall_score >= 60:
            next_steps.extend([
                "巩固现有良好习惯",
                "关注需要改进的领域",
                "设定具体改进目标",
                "定期检查进度",
            ])
        else:
            next_steps.extend([
                "制定明确的改进计划",
                "从简单目标开始",
                "寻求指导或帮助",
                "每天记录进步",
            ])
        
        # 基于具体数据的建议
        areas_for_improvement = summary.get("areas_for_improvement", [])
        for area in areas_for_improvement[:2]:  # 最多关注2个领域
            if "运动" in area:
                next_steps.append("制定每周运动计划")
            elif "任务" in area:
                next_steps.append("使用任务管理工具")
            elif "成就" in area:
                next_steps.append("关注简单成就目标")
        
        # 添加通用建议
        next_steps.extend([
            "定期查看分析报告",
            "调整目标以适应变化",
            "庆祝每一个进步",
        ])
        
    except Exception as e:
        self._logger.error("生成下一步建议失败: %s", str(e))
    
    return list(dict.fromkeys(next_steps))[:5]  # 去重并限制数量


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
    # 关键配置变更需要重新初始化
    critical_configs = ["analysis_period_days", "trend_window_days", "insight_threshold"]
    return any(key in self._config for key in critical_configs)


def _cleanup_internal(self) -> None:
    """
    内部清理逻辑。
    """
    self._analysis_cache.clear()
    self._logger.info("数据分析服务缓存已清理")


# ==================== 数据分析服务管理器 ====================
class AnalyticsManager:
    """
    数据分析服务管理器，管理多个数据分析服务实例。
    """
    
    def __init__(self) -> None:
        """初始化数据分析服务管理器。"""
        self._services: Dict[str, AnalyticsService] = {}
        self._default_service: Optional[AnalyticsService] = None
        self._logger = logging.getLogger(__name__)
    
    def get_service(self, service_name: str = "default") -> AnalyticsService:
        """
        获取数据分析服务实例。
        
        Args:
            service_name: 服务名称
            
        Returns:
            数据分析服务实例
        """
        if service_name not in self._services:
            self._services[service_name] = AnalyticsService()
            
            if service_name == "default":
                self._default_service = self._services[service_name]
        
        return self._services[service_name]
    
    def get_default_service(self) -> AnalyticsService:
        """
        获取默认数据分析服务实例。
        
        Returns:
            默认数据分析服务实例
        """
        if not self._default_service:
            self._default_service = self.get_service("default")
        
        return self._default_service
    
    def initialize_all(self) -> bool:
        """
        初始化所有数据分析服务。
        
        Returns:
            是否全部初始化成功
        """
        success = True
        
        for name, service in self._services.items():
            if not service.initialize():
                self._logger.error("数据分析服务 %s 初始化失败", name)
                success = False
            else:
                self._logger.info("数据分析服务 %s 初始化成功", name)
        
        return success
    
    def cleanup_all(self) -> None:
        """
        清理所有数据分析服务。
        """
        for service in self._services.values():
            service.cleanup()
        
        self._services.clear()
        self._default_service = None
        self._logger.info("所有数据分析服务已清理")
    
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
    "AnalyticsService",
    "AnalyticsManager",
]
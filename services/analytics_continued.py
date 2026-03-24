"""
数据分析服务续写部分。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from django.utils import timezone

from services.analytics import AnalyticsService


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# 继续 AnalyticsService 类的方法
def _extract_insights_from_data_continued(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    从分析数据中提取洞察（续写）。
    
    Args:
        analysis: 分析数据
        
    Returns:
        洞察列表
    """
    insights = []
    config = self.get_config()
    threshold = config.get("insight_threshold", 0.7)
    
    try:
        # 任务洞察
        task_data = analysis.get("task_analysis", {})
        if task_data and not task_data.get("error"):
            summary = task_data.get("summary", {})
            efficiency = task_data.get("efficiency", {})
            
            # 完成率洞察
            completion_rate = summary.get("completion_rate", 0)
            if completion_rate >= 80:
                insights.append({
                    "type": "task",
                    "category": "completion",
                    "title": "高效的任务完成者",
                    "description": f"任务完成率高达{completion_rate:.1f}%，您非常善于完成任务！",
                    "priority": "high",
                    "score": completion_rate / 100,
                })
            elif completion_rate <= 50:
                insights.append({
                    "type": "task",
                    "category": "completion",
                    "title": "需要提高任务完成率",
                    "description": f"当前任务完成率为{completion_rate:.1f}%，建议优先完成重要任务。",
                    "priority": "medium",
                    "score": 1 - (completion_rate / 100),
                })
            
            # 时间效率洞察
            time_efficiency = efficiency.get("time_efficiency", 0)
            if time_efficiency >= 1.2:
                insights.append({
                    "type": "task",
                    "category": "efficiency",
                    "title": "超高效的时间管理",
                    "description": "您完成任务的速度比预计快20%以上，时间管理能力出色！",
                    "priority": "medium",
                    "score": min(time_efficiency / 2, 1.0),
                })
            elif time_efficiency <= 0.8:
                insights.append({
                    "type": "task",
                    "category": "efficiency",
                    "title": "时间估算需要调整",
                    "description": "实际用时经常超过预计时间，建议更准确地估算任务时间。",
                    "priority": "low",
                    "score": 1 - time_efficiency,
                })
        
        # 成就洞察
        achievement_data = analysis.get("achievement_analysis", {})
        if achievement_data and not achievement_data.get("error"):
            summary = achievement_data.get("summary", {})
            potential = achievement_data.get("potential", {})
            
            # 解锁率洞察
            unlock_rate = summary.get("unlock_rate", 0)
            if unlock_rate >= 60:
                insights.append({
                    "type": "achievement",
                    "category": "unlock",
                    "title": "成就解锁大师",
                    "description": f"成就解锁率{unlock_rate:.1f}%，您非常善于达成目标！",
                    "priority": "high",
                    "score": unlock_rate / 100,
                })
            
            # 潜在成就洞察
            near_completion_count = potential.get("near_completion_count", 0)
            if near_completion_count >= 3:
                insights.append({
                    "type": "achievement",
                    "category": "potential",
                    "title": "即将获得多项成就",
                    "description": f"有{near_completion_count}个成就接近完成，继续努力！",
                    "priority": "medium",
                    "score": min(near_completion_count / 5, 1.0),
                })
        
        # 综合洞察
        trends = analysis.get("trends", {})
        overall_trend = trends.get("overall_trend", "stable")
        
        if overall_trend == "improving":
            insights.append({
                "type": "overall",
                "category": "trend",
                "title": "整体表现持续提升",
                "description": "您的运动、任务和成就表现都在稳步提升，继续保持！",
                "priority": "high",
                "score": 0.9,
            })
        elif overall_trend == "declining":
            insights.append({
                "type": "overall",
                "category": "trend",
                "title": "需要注意表现下滑",
                "description": "近期表现有所下滑，建议调整计划或寻求帮助。",
                "priority": "high",
                "score": 0.3,
            })
        
        # 平衡性洞察
        exercise_summary = analysis.get("exercise_analysis", {}).get("summary", {})
        task_summary = analysis.get("task_analysis", {}).get("summary", {})
        
        if exercise_summary and task_summary:
            exercise_score = exercise_summary.get("consistency_rate", 0)
            task_score = task_summary.get("completion_rate", 0) / 100
            
            balance_diff = abs(exercise_score - task_score)
            if balance_diff > 0.4:
                if exercise_score > task_score:
                    insights.append({
                        "type": "balance",
                        "category": "imbalance",
                        "title": "运动表现优于任务完成",
                        "description": "您的运动习惯很好，但任务完成需要更多关注。",
                        "priority": "medium",
                        "score": balance_diff,
                    })
                else:
                    insights.append({
                        "type": "balance",
                        "category": "imbalance",
                        "title": "任务完成优于运动表现",
                        "description": "您很善于完成任务，但需要更多关注运动健康。",
                        "priority": "medium",
                        "score": balance_diff,
                    })
        
    except Exception as e:
        self._logger.error("提取洞察失败: %s", str(e))
    
    # 按优先级和分数排序
    insights.sort(key=lambda x: (x.get("priority", "low"), x.get("score", 0)), reverse=True)
    
    return insights[:10]  # 返回前10个洞察


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
            rec = self._generate_recommendation_from_insight(insight, analysis)
            if rec:
                recommendations.append(rec)
        
        # 添加基于数据的通用建议
        generic_recs = self._generate_generic_recommendations(analysis)
        recommendations.extend(generic_recs)
        
        # 去重和排序
        recommendations = self._deduplicate_and_sort_recommendations(recommendations)
        
    except Exception as e:
        self._logger.error("生成建议失败: %s", str(e))
    
    return recommendations[:5]  # 返回前5个建议


def _generate_recommendation_from_insight(self, insight: Dict[str, Any], analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    从洞察生成建议。
    
    Args:
        insight: 洞察数据
        analysis: 分析数据
        
    Returns:
        建议字典
    """
    insight_type = insight.get("type")
    insight_category = insight.get("category")
    insight_title = insight.get("title", "")
    
    recommendation_templates = {
        ("exercise", "consistency"): {
            "high": "继续保持当前的运动频率，可以考虑增加一些多样性。",
            "low": "建议制定每周运动计划，从每周2-3次开始，逐渐增加频率。",
        },
        ("exercise", "intensity"): {
            "high": "您的运动强度很好，可以尝试增加一些新的运动类型。",
            "medium": "考虑适当增加运动时长或尝试更高难度的运动。",
        },
        ("task", "completion"): {
            "high": "优秀的任务完成能力，可以挑战更复杂的任务。",
            "low": "建议将大任务分解为小步骤，设置明确的截止日期。",
        },
        ("task", "efficiency"): {
            "high": "时间管理能力出色，可以承担更多责任。",
            "low": "尝试使用时间追踪工具，更准确地估算任务时间。",
        },
        ("achievement", "unlock"): {
            "high": "成就解锁能力很强，可以挑战更高难度的成就。",
            "medium": "关注接近完成的成就，优先完成它们。",
        },
        ("achievement", "potential"): {
            "high": "多个成就接近完成，集中精力完成它们以获得奖励。",
            "medium": "检查接近完成的成就，制定完成计划。",
        },
        ("overall", "trend"): {
            "improving": "继续保持当前的良好势头！",
            "declining": "建议回顾近期活动，找出需要改进的地方。",
        },
        ("balance", "imbalance"): {
            "default": "尝试在运动、任务和成就之间找到更好的平衡。",
        },
    }
    
    # 获取建议模板
    template_key = (insight_type, insight_category)
    template = recommendation_templates.get(template_key)
    
    if not template:
        return None
    
    # 根据洞察优先级选择建议
    insight_priority = insight.get("priority", "medium")
    suggestion = template.get(insight_priority, template.get("default", ""))
    
    if not suggestion:
        return None
    
    return {
        "type": insight_type,
        "category": insight_category,
        "title": f"基于'{insight_title}'的建议",
        "description": suggestion,
        "priority": insight_priority,
        "action_items": self._generate_action_items(insight, analysis),
        "estimated_impact": insight.get("score", 0.5),
    }


def _generate_generic_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    生成通用建议。
    
    Args:
        analysis: 分析数据
        
    Returns:
        通用建议列表
    """
    recommendations = []
    
    try:
        # 基于运动数据的建议
        exercise_data = analysis.get("exercise_analysis", {})
        if exercise_data:
            exercise_summary = exercise_data.get("summary", {})
            avg_sessions = exercise_summary.get("avg_sessions_per_day", 0)
            
            if avg_sessions < 0.5:  # 平均每天少于0.5次
                recommendations.append({
                    "type": "exercise",
                    "category": "frequency",
                    "title": "增加运动频率",
                    "description": "建议每周至少运动3次，每次30分钟以上。",
                    "priority": "medium",
                    "action_items": ["制定每周运动计划", "设置运动提醒", "寻找运动伙伴"],
                    "estimated_impact": 0.7,
                })
        
        # 基于任务数据的建议
        task_data = analysis.get("task_analysis", {})
        if task_data:
            task_summary = task_data.get("summary", {})
            overdue_tasks = task_summary.get("overdue_tasks", 0)
            
            if overdue_tasks > 0:
                recommendations.append({
                    "type": "task",
                    "category": "timeliness",
                    "title": "处理逾期任务",
                    "description": f"您有{overdue_tasks}个任务已逾期，建议优先处理。",
                    "priority": "high",
                    "action_items": ["检查所有逾期任务", "重新评估截止日期", "寻求帮助或委派"],
                    "estimated_impact": 0.8,
                })
        
        # 基于成就数据的建议
        achievement_data = analysis.get("achievement_analysis", {})
        if achievement_data:
            achievement_summary = achievement_data.get("summary", {})
            unlock_rate = achievement_summary.get("unlock_rate", 0)
            
            if unlock_rate < 30:
                recommendations.append({
                    "type": "achievement",
                    "category": "engagement",
                    "title": "提高成就参与度",
                    "description": "尝试关注一些简单成就，快速获得成就感。",
                    "priority": "medium",
                    "action_items": ["查看简单成就列表", "设置成就目标", "追踪成就进度"],
                    "estimated_impact": 0.6,
                })
        
    except Exception as e:
        self._logger.error("生成通用建议失败: %s", str(e))
    
    return recommendations


def _generate_action_items(self, insight: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
    """
    生成具体的行动项。
    
    Args:
        insight: 洞察数据
        analysis: 分析数据
        
    Returns:
        行动项列表
    """
    action_items = []
    insight_type = insight.get("type")
    insight_category = insight.get("category")
    
    action_templates = {
        ("exercise", "consistency"): [
            "制定每周运动计划",
            "设置运动提醒",
            "记录每次运动",
            "寻找运动伙伴",
        ],
        ("exercise", "intensity"): [
            "尝试新的运动类型",
            "增加运动时长10%",
            "提高运动难度",
            "参加运动挑战",
        ],
        ("task", "completion"): [
            "分解大任务为小步骤",
            "设置明确的截止日期",
            "使用任务优先级系统",
            "定期回顾任务进度",
        ],
        ("task", "efficiency"): [
            "使用时间追踪工具",
            "学习时间管理技巧",
            "减少多任务处理",
            "优化工作环境",
        ],
        ("achievement", "unlock"): [
            "查看成就列表",
            "设置成就目标",
            "追踪成就进度",
            "庆祝成就解锁",
        ],
        ("achievement", "potential"): [
            "关注接近完成的成就",
            "制定成就完成计划",
            "寻求帮助或指导",
            "调整目标优先级",
        ],
    }
    
    # 获取行动项模板
    template_key = (insight_type, insight_category)
    items = action_templates.get(template_key, [])
    
    # 添加通用行动项
    items.extend([
        "定期查看分析报告",
        "调整个人目标",
        "寻求反馈和建议",
        "庆祝小进步",
    ])
    
    return items[:4]  # 返回前4个行动项


def _deduplicate_and_sort_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    去重和排序建议。
    
    Args:
        recommendations: 建议列表
        
    Returns:
        处理后的建议列表
    """
    if not recommendations:
        return []
    
    # 去重：基于标题和描述
    seen = set()
    unique_recommendations = []
    
    for rec in recommendations:
        key = (rec.get("title", ""), rec.get("description", ""))
        if key not in seen:
            seen.add(key)
            unique_recommendations.append(rec)
    
    # 按优先级和影响排序
    priority_scores = {"high": 3, "medium": 2, "low": 1}
    unique_recommendations.sort(
        key=lambda x: (
            priority_scores.get(x.get("priority", "low"), 1),
            x.get("estimated_impact", 0),
        ),
        reverse=True,
    )
    
    return unique_recommendations


def _generate_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成分析摘要。
    
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
    }
    
    try:
        # 计算总体分数
        scores = []
        
        # 运动分数
        exercise_summary = analysis.get("exercise_analysis", {}).get("summary", {})
        if exercise_summary:
            consistency = exercise_summary.get("consistency_rate", 0)
            avg_duration = min(exercise_summary.get("avg_duration_per_session", 0) / 60, 1.0)
            exercise_score = (consistency * 0.6 + avg_duration * 0.4)
            scores.append(exercise_score)
            
            if consistency >= 0.7:
                summary["strengths"].append("优秀的运动习惯")
            elif consistency <= 0.3:
                summary["areas_for_improvement"].append("需要提高运动频率")
        
        # 任务分数
        task_summary = analysis.get("task_analysis", {}).get("summary", {})
        if task_summary:
            completion_rate = task_summary.get("completion_rate", 0) / 100
            on_time_rate = task_summary.get("on
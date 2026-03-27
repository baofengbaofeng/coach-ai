"""
成就数据分析处理器

实现成就数据分析的RESTful API接口
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

import tornado.web
from tornado.escape import json_decode

from coding.tornado.core.base_handler import BaseHandler
from coding.tornado.core.error_handler import APIError
from coding.tornado.core.middleware import auth_required
from database.connection import get_db_session

from .analytics import AchievementAnalyticsService

logger = logging.getLogger(__name__)


class UserAchievementAnalyticsHandler(BaseHandler):
    """用户成就分析处理器"""
    
    @auth_required
    async def get(self, user_id: str = None):
        """获取用户成就分析数据"""
        try:
            # 如果未指定用户ID，使用当前用户
            if user_id is None:
                user_id = self.current_user.id
            else:
                user_id = int(user_id)
            
            # 验证权限（用户只能查看自己的数据，管理员可以查看所有）
            if user_id != self.current_user.id and not self.current_user.is_admin():
                raise APIError(403, "Permission denied")
            
            with get_db_session() as session:
                service = AchievementAnalyticsService(session)
                analytics_data = service.get_user_achievement_analytics(user_id)
                
                if "error" in analytics_data:
                    raise APIError(500, analytics_data["error"])
                
                self.write_success({
                    "analytics": analytics_data
                })
                
        except ValueError:
            self.write_error(400, "Invalid user ID")
        except APIError as e:
            self.write_error(e.status_code, e.message)
        except Exception as e:
            logger.error(f"Failed to get user achievement analytics: {str(e)}")
            self.write_error(500, "Internal server error")


class SystemAchievementAnalyticsHandler(BaseHandler):
    """系统成就分析处理器"""
    
    @auth_required
    async def get(self):
        """获取系统成就分析数据"""
        try:
            # 验证权限（仅管理员可访问）
            if not self.current_user.is_admin():
                raise APIError(403, "Permission denied")
            
            with get_db_session() as session:
                service = AchievementAnalyticsService(session)
                analytics_data = service.get_system_achievement_analytics()
                
                if "error" in analytics_data:
                    raise APIError(500, analytics_data["error"])
                
                self.write_success({
                    "analytics": analytics_data
                })
                
        except APIError as e:
            self.write_error(e.status_code, e.message)
        except Exception as e:
            logger.error(f"Failed to get system achievement analytics: {str(e)}")
            self.write_error(500, "Internal server error")


class AchievementPerformanceMetricsHandler(BaseHandler):
    """成就系统性能指标处理器"""
    
    @auth_required
    async def get(self):
        """获取成就系统性能指标"""
        try:
            # 验证权限（仅管理员可访问）
            if not self.current_user.is_admin():
                raise APIError(403, "Permission denied")
            
            with get_db_session() as session:
                service = AchievementAnalyticsService(session)
                metrics_data = service.get_achievement_performance_metrics()
                
                if "error" in metrics_data:
                    raise APIError(500, metrics_data["error"])
                
                self.write_success({
                    "metrics": metrics_data
                })
                
        except APIError as e:
            self.write_error(e.status_code, e.message)
        except Exception as e:
            logger.error(f"Failed to get achievement performance metrics: {str(e)}")
            self.write_error(500, "Internal server error")


class AchievementRecommendationsHandler(BaseHandler):
    """成就推荐处理器"""
    
    @auth_required
    async def get(self, user_id: str = None):
        """获取成就推荐"""
        try:
            # 如果未指定用户ID，使用当前用户
            if user_id is None:
                user_id = self.current_user.id
            else:
                user_id = int(user_id)
            
            # 验证权限（用户只能查看自己的推荐，管理员可以查看所有）
            if user_id != self.current_user.id and not self.current_user.is_admin():
                raise APIError(403, "Permission denied")
            
            # 获取查询参数
            limit = int(self.get_argument("limit", 5))
            
            # 验证参数
            if limit > 20:
                limit = 20
            if limit < 1:
                limit = 1
            
            with get_db_session() as session:
                service = AchievementAnalyticsService(session)
                recommendations = service.generate_achievement_recommendations(user_id, limit)
                
                self.write_success({
                    "user_id": user_id,
                    "recommendations": recommendations,
                    "count": len(recommendations)
                })
                
        except ValueError:
            self.write_error(400, "Invalid user ID or limit parameter")
        except APIError as e:
            self.write_error(e.status_code, e.message)
        except Exception as e:
            logger.error(f"Failed to get achievement recommendations: {str(e)}")
            self.write_error(500, "Internal server error")


class AchievementTrendAnalysisHandler(BaseHandler):
    """成就趋势分析处理器"""
    
    @auth_required
    async def get(self):
        """获取成就趋势分析"""
        try:
            # 验证权限（仅管理员可访问）
            if not self.current_user.is_admin():
                raise APIError(403, "Permission denied")
            
            # 获取查询参数
            days = int(self.get_argument("days", 30))
            analysis_type = self.get_argument("type", "unlock_trend")
            
            # 验证参数
            if days > 365:
                days = 365
            if days < 7:
                days = 7
            
            with get_db_session() as session:
                service = AchievementAnalyticsService(session)
                
                if analysis_type == "unlock_trend":
                    trend_data = service._get_system_unlock_trend(days)
                    result = {
                        "analysis_type": "unlock_trend",
                        "days": days,
                        "data": trend_data
                    }
                elif analysis_type == "user_activity":
                    distribution = service._get_user_activity_distribution()
                    result = {
                        "analysis_type": "user_activity_distribution",
                        "days": days,
                        "data": distribution
                    }
                else:
                    raise APIError(400, f"Unsupported analysis type: {analysis_type}")
                
                self.write_success(result)
                
        except ValueError:
            self.write_error(400, "Invalid parameters")
        except APIError as e:
            self.write_error(e.status_code, e.message)
        except Exception as e:
            logger.error(f"Failed to get achievement trend analysis: {str(e)}")
            self.write_error(500, "Internal server error")


class PopularAchievementsHandler(BaseHandler):
    """热门成就处理器"""
    
    @auth_required
    async def get(self):
        """获取热门成就列表"""
        try:
            # 获取查询参数
            limit = int(self.get_argument("limit", 10))
            days = int(self.get_argument("days", 30))
            
            # 验证参数
            if limit > 50:
                limit = 50
            if limit < 1:
                limit = 1
            if days > 365:
                days = 365
            if days < 1:
                days = 1
            
            with get_db_session() as session:
                service = AchievementAnalyticsService(session)
                
                # 获取最近N天的热门成就
                start_date = datetime.now() - timedelta(days=days)
                
                # 这里简化实现，实际应该使用更复杂的查询
                from sqlalchemy import func
                from database.models import Achievement, UserAchievement
                
                popular_achievements = session.query(
                    Achievement,
                    func.count(UserAchievement.id).label('unlock_count')
                ).join(
                    UserAchievement, Achievement.id == UserAchievement.achievement_id
                ).filter(
                    UserAchievement.status == 'completed',
                    UserAchievement.unlocked_at >= start_date,
                    UserAchievement.is_deleted == False,
                    Achievement.is_deleted == False,
                    Achievement.status == 'active'
                ).group_by(Achievement.id).order_by(
                    func.count(UserAchievement.id).desc()
                ).limit(limit).all()
                
                result = []
                for achievement, unlock_count in popular_achievements:
                    result.append({
                        "id": achievement.id,
                        "name": achievement.name,
                        "description": achievement.description,
                        "type": achievement.achievement_type.value,
                        "difficulty": achievement.difficulty.value,
                        "unlock_count": unlock_count,
                        "reward_points": achievement.reward_points
                    })
                
                self.write_success({
                    "popular_achievements": result,
                    "days": days,
                    "limit": limit,
                    "count": len(result)
                })
                
        except ValueError:
            self.write_error(400, "Invalid parameters")
        except Exception as e:
            logger.error(f"Failed to get popular achievements: {str(e)}")
            self.write_error(500, "Internal server error")


class DifficultAchievementsHandler(BaseHandler):
    """困难成就处理器"""
    
    @auth_required
    async def get(self):
        """获取困难成就列表"""
        try:
            # 获取查询参数
            limit = int(self.get_argument("limit", 10))
            min_attempts = int(self.get_argument("min_attempts", 10))
            
            # 验证参数
            if limit > 50:
                limit = 50
            if limit < 1:
                limit = 1
            if min_attempts < 1:
                min_attempts = 1
            
            with get_db_session() as session:
                service = AchievementAnalyticsService(session)
                difficult_achievements = service._get_difficult_achievements(limit)
                
                # 过滤尝试次数不足的成就
                filtered_achievements = [
                    a for a in difficult_achievements 
                    if a["total_assignments"] >= min_attempts
                ]
                
                self.write_success({
                    "difficult_achievements": filtered_achievements[:limit],
                    "limit": limit,
                    "min_attempts": min_attempts,
                    "count": len(filtered_achievements[:limit])
                })
                
        except ValueError:
            self.write_error(400, "Invalid parameters")
        except Exception as e:
            logger.error(f"Failed to get difficult achievements: {str(e)}")
            self.write_error(500, "Internal server error")


class AchievementComparisonHandler(BaseHandler):
    """成就对比处理器"""
    
    @auth_required
    async def post(self):
        """对比多个用户的成就数据"""
        try:
            # 获取请求数据
            data = json_decode(self.request.body)
            
            # 验证必要字段
            if "user_ids" not in data:
                raise APIError(400, "Missing required field: user_ids")
            
            user_ids = data["user_ids"]
            if not isinstance(user_ids, list) or len(user_ids) < 2:
                raise APIError(400, "user_ids must be a list with at least 2 user IDs")
            
            if len(user_ids) > 10:
                raise APIError(400, "Cannot compare more than 10 users at once")
            
            # 验证权限（用户只能对比自己和其他用户，管理员可以对比所有）
            current_user_id = self.current_user.id
            if not self.current_user.is_admin():
                if current_user_id not in user_ids:
                    raise APIError(403, "You can only compare data that includes yourself")
            
            with get_db_session() as session:
                service = AchievementAnalyticsService(session)
                
                comparison_data = []
                for user_id in user_ids:
                    analytics = service.get_user_achievement_analytics(user_id)
                    if "error" not in analytics:
                        comparison_data.append({
                            "user_id": user_id,
                            "analytics": analytics
                        })
                
                # 计算对比指标
                comparison_metrics = self._calculate_comparison_metrics(comparison_data)
                
                self.write_success({
                    "comparison": comparison_data,
                    "metrics": comparison_metrics,
                    "count": len(comparison_data)
                })
                
        except APIError as e:
            self.write_error(e.status_code, e.message)
        except Exception as e:
            logger.error(f"Failed to compare achievement data: {str(e)}")
            self.write_error(500, "Internal server error")
    
    def _calculate_comparison_metrics(self, comparison_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算对比指标"""
        try:
            if not comparison_data:
                return {}
            
            metrics = {
                "total_users": len(comparison_data),
                "completion_rate_avg": 0.0,
                "completion_rate_min": 100.0,
                "completion_rate_max": 0.0,
                "activity_score_avg": 0.0,
                "activity_score_min": 100.0,
                "activity_score_max": 0.0,
                "total_achievements_avg": 0.0,
                "total_achievements_min": float('inf'),
                "total_achievements_max": 0.0
            }
            
            completion_rates = []
            activity_scores = []
            total_achievements = []
            
            for data in comparison_data:
                analytics = data["analytics"]
                stats = analytics.get("stats", {})
                
                completion_rate = stats.get("completion_rate", 0.0)
                activity_score = stats.get("activity_score", 0.0)
                total_ach = stats.get("total_achievements", 0)
                
                completion_rates.append(completion_rate)
                activity_scores.append(activity_score)
                total_achievements.append(total_ach)
            
            if completion_rates:
                metrics["completion_rate_avg"] = round(sum(completion_rates) / len(completion_rates), 2)
                metrics["completion_rate_min"] = round(min(completion_rates), 2)
                metrics["completion_rate_max"] = round(max(completion_rates), 2)
            
            if activity_scores:
                metrics["activity_score_avg"] = round(sum(activity_scores) / len(activity_scores), 2)
                metrics["activity_score_min"] = round(min(activity_scores), 2)
                metrics["activity_score_max"] = round(max(activity_scores), 2)
            
            if total_achievements:
                metrics["total_achievements_avg"] = round(sum(total_achievements) / len(total_achievements), 2)
                metrics["total_achievements_min"] = min(total_achievements)
                metrics["total_achievements_max"] = max(total_achievements)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate comparison metrics: {str(e)}")
            return {}
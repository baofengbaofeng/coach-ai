"""
成就数据分析服务

实现成就系统的数据分析和统计功能，包括用户行为分析、趋势分析和性能监控
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, extract, case
import json

from coding.database.models import (
    Achievement, AchievementType, AchievementDifficulty, AchievementStatus,
    UserAchievement, UserAchievementStatus,
    Badge, BadgeRarity, BadgeType, BadgeStatus,
    UserBadge,
    Reward, RewardType, RewardStatus,
    UserReward, UserRewardStatus,
    User
)

logger = logging.getLogger(__name__)


class AchievementAnalyticsService:
    """成就数据分析服务类"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_user_achievement_analytics(self, user_id: int) -> Dict[str, Any]:
        """获取用户成就分析数据"""
        try:
            # 获取用户基本信息
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            # 获取用户成就统计
            user_achievements = self.db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.is_deleted == False
            ).all()
            
            # 计算基本统计
            total_achievements = len(user_achievements)
            unlocked_achievements = len([ua for ua in user_achievements if ua.status == UserAchievementStatus.COMPLETED])
            in_progress_achievements = len([ua for ua in user_achievements if ua.status == UserAchievementStatus.IN_PROGRESS])
            locked_achievements = len([ua for ua in user_achievements if ua.status == UserAchievementStatus.LOCKED])
            
            # 计算完成率
            completion_rate = 0.0
            if total_achievements > 0:
                completion_rate = (unlocked_achievements / total_achievements) * 100
            
            # 按类型统计
            type_stats = self._get_achievement_stats_by_type(user_achievements)
            
            # 按难度统计
            difficulty_stats = self._get_achievement_stats_by_difficulty(user_achievements)
            
            # 获取解锁趋势
            unlock_trend = self._get_unlock_trend(user_id)
            
            # 获取最近解锁的成就
            recent_achievements = self._get_recent_achievements(user_id, limit=10)
            
            # 获取徽章统计
            badge_stats = self._get_badge_stats(user_id)
            
            # 获取奖励统计
            reward_stats = self._get_reward_stats(user_id)
            
            # 计算活跃度
            activity_score = self._calculate_activity_score(user_id)
            
            return {
                "user_id": user_id,
                "username": user.username,
                "stats": {
                    "total_achievements": total_achievements,
                    "unlocked_achievements": unlocked_achievements,
                    "in_progress_achievements": in_progress_achievements,
                    "locked_achievements": locked_achievements,
                    "completion_rate": round(completion_rate, 2),
                    "activity_score": activity_score
                },
                "type_distribution": type_stats,
                "difficulty_distribution": difficulty_stats,
                "unlock_trend": unlock_trend,
                "recent_achievements": recent_achievements,
                "badge_stats": badge_stats,
                "reward_stats": reward_stats,
                "calculated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get user achievement analytics for user {user_id}: {str(e)}")
            return {"error": str(e)}
    
    def _get_achievement_stats_by_type(self, user_achievements: List[UserAchievement]) -> Dict[str, Any]:
        """按类型统计成就"""
        try:
            type_stats = defaultdict(lambda: {"total": 0, "unlocked": 0, "in_progress": 0, "locked": 0})
            
            for ua in user_achievements:
                if ua.achievement:
                    achievement_type = ua.achievement.achievement_type.value
                    type_stats[achievement_type]["total"] += 1
                    
                    if ua.status == UserAchievementStatus.COMPLETED:
                        type_stats[achievement_type]["unlocked"] += 1
                    elif ua.status == UserAchievementStatus.IN_PROGRESS:
                        type_stats[achievement_type]["in_progress"] += 1
                    else:
                        type_stats[achievement_type]["locked"] += 1
            
            return dict(type_stats)
        except Exception as e:
            logger.error(f"Failed to get achievement stats by type: {str(e)}")
            return {}
    
    def _get_achievement_stats_by_difficulty(self, user_achievements: List[UserAchievement]) -> Dict[str, Any]:
        """按难度统计成就"""
        try:
            difficulty_stats = defaultdict(lambda: {"total": 0, "unlocked": 0, "in_progress": 0, "locked": 0})
            
            for ua in user_achievements:
                if ua.achievement:
                    difficulty = ua.achievement.difficulty.value
                    difficulty_stats[difficulty]["total"] += 1
                    
                    if ua.status == UserAchievementStatus.COMPLETED:
                        difficulty_stats[difficulty]["unlocked"] += 1
                    elif ua.status == UserAchievementStatus.IN_PROGRESS:
                        difficulty_stats[difficulty]["in_progress"] += 1
                    else:
                        difficulty_stats[difficulty]["locked"] += 1
            
            return dict(difficulty_stats)
        except Exception as e:
            logger.error(f"Failed to get achievement stats by difficulty: {str(e)}")
            return {}
    
    def _get_unlock_trend(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """获取成就解锁趋势"""
        try:
            # 获取最近N天的解锁数据
            start_date = datetime.now() - timedelta(days=days)
            
            # 查询解锁的成就
            unlocked_achievements = self.db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.status == UserAchievementStatus.COMPLETED,
                UserAchievement.unlocked_at >= start_date,
                UserAchievement.is_deleted == False
            ).all()
            
            # 按日期分组
            daily_counts = defaultdict(int)
            for ua in unlocked_achievements:
                if ua.unlocked_at:
                    date_str = ua.unlocked_at.strftime("%Y-%m-%d")
                    daily_counts[date_str] += 1
            
            # 转换为列表格式
            trend_data = []
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                count = daily_counts.get(date, 0)
                trend_data.append({
                    "date": date,
                    "count": count
                })
            
            # 按日期排序
            trend_data.sort(key=lambda x: x["date"])
            
            return trend_data
        except Exception as e:
            logger.error(f"Failed to get unlock trend for user {user_id}: {str(e)}")
            return []
    
    def _get_recent_achievements(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近解锁的成就"""
        try:
            recent_achievements = self.db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.status == UserAchievementStatus.COMPLETED,
                UserAchievement.is_deleted == False
            ).order_by(
                UserAchievement.unlocked_at.desc()
            ).limit(limit).all()
            
            result = []
            for ua in recent_achievements:
                if ua.achievement:
                    result.append({
                        "id": ua.achievement.id,
                        "name": ua.achievement.name,
                        "description": ua.achievement.description,
                        "type": ua.achievement.achievement_type.value,
                        "difficulty": ua.achievement.difficulty.value,
                        "unlocked_at": ua.unlocked_at.isoformat() if ua.unlocked_at else None,
                        "reward_points": ua.achievement.reward_points
                    })
            
            return result
        except Exception as e:
            logger.error(f"Failed to get recent achievements for user {user_id}: {str(e)}")
            return []
    
    def _get_badge_stats(self, user_id: int) -> Dict[str, Any]:
        """获取徽章统计"""
        try:
            # 获取用户徽章
            user_badges = self.db.query(UserBadge).filter(
                UserBadge.user_id == user_id,
                UserBadge.is_deleted == False
            ).all()
            
            # 按稀有度统计
            rarity_stats = defaultdict(int)
            for ub in user_badges:
                if ub.badge:
                    rarity = ub.badge.rarity.value
                    rarity_stats[rarity] += 1
            
            # 按类型统计
            type_stats = defaultdict(int)
            for ub in user_badges:
                if ub.badge:
                    badge_type = ub.badge.badge_type.value
                    type_stats[badge_type] += 1
            
            return {
                "total_badges": len(user_badges),
                "rarity_distribution": dict(rarity_stats),
                "type_distribution": dict(type_stats),
                "equipped_count": len([ub for ub in user_badges if ub.is_equipped]),
                "favorite_count": len([ub for ub in user_badges if ub.is_favorite])
            }
        except Exception as e:
            logger.error(f"Failed to get badge stats for user {user_id}: {str(e)}")
            return {}
    
    def _get_reward_stats(self, user_id: int) -> Dict[str, Any]:
        """获取奖励统计"""
        try:
            # 获取用户奖励
            user_rewards = self.db.query(UserReward).filter(
                UserReward.user_id == user_id,
                UserReward.is_deleted == False
            ).all()
            
            # 按类型统计
            type_stats = defaultdict(int)
            total_value = 0
            
            for ur in user_rewards:
                if ur.reward:
                    reward_type = ur.reward.reward_type.value
                    type_stats[reward_type] += 1
                    total_value += ur.reward_value or 0
            
            # 按状态统计
            status_stats = defaultdict(int)
            for ur in user_rewards:
                status = ur.status.value
                status_stats[status] += 1
            
            return {
                "total_rewards": len(user_rewards),
                "type_distribution": dict(type_stats),
                "status_distribution": dict(status_stats),
                "total_value": total_value,
                "claimed_count": status_stats.get("claimed", 0),
                "used_count": status_stats.get("used", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get reward stats for user {user_id}: {str(e)}")
            return {}
    
    def _calculate_activity_score(self, user_id: int) -> float:
        """计算用户活跃度分数"""
        try:
            # 获取最近30天的活动数据
            start_date = datetime.now() - timedelta(days=30)
            
            # 计算成就解锁数量
            achievement_count = self.db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.status == UserAchievementStatus.COMPLETED,
                UserAchievement.unlocked_at >= start_date,
                UserAchievement.is_deleted == False
            ).count()
            
            # 计算徽章获得数量
            badge_count = self.db.query(UserBadge).filter(
                UserBadge.user_id == user_id,
                UserBadge.granted_at >= start_date,
                UserBadge.is_deleted == False
            ).count()
            
            # 计算奖励领取数量
            reward_count = self.db.query(UserReward).filter(
                UserReward.user_id == user_id,
                UserReward.claimed_at >= start_date,
                UserReward.is_deleted == False
            ).count()
            
            # 计算活跃度分数（加权计算）
            activity_score = (
                achievement_count * 10 +  # 每个成就10分
                badge_count * 20 +        # 每个徽章20分
                reward_count * 5          # 每个奖励5分
            )
            
            # 归一化到0-100分
            normalized_score = min(100.0, activity_score / 10.0)
            
            return round(normalized_score, 2)
        except Exception as e:
            logger.error(f"Failed to calculate activity score for user {user_id}: {str(e)}")
            return 0.0
    
    def get_system_achievement_analytics(self) -> Dict[str, Any]:
        """获取系统成就分析数据"""
        try:
            # 获取所有成就统计
            total_achievements = self.db.query(Achievement).filter(
                Achievement.is_deleted == False
            ).count()
            
            active_achievements = self.db.query(Achievement).filter(
                Achievement.is_deleted == False,
                Achievement.status == AchievementStatus.ACTIVE
            ).count()
            
            # 获取用户成就统计
            total_user_achievements = self.db.query(UserAchievement).filter(
                UserAchievement.is_deleted == False
            ).count()
            
            completed_user_achievements = self.db.query(UserAchievement).filter(
                UserAchievement.is_deleted == False,
                UserAchievement.status == UserAchievementStatus.COMPLETED
            ).count()
            
            # 计算平均完成率
            avg_completion_rate = 0.0
            if total_user_achievements > 0:
                avg_completion_rate = (completed_user_achievements / total_user_achievements) * 100
            
            # 获取最受欢迎的成就
            popular_achievements = self._get_popular_achievements(limit=10)
            
            # 获取最难解锁的成就
            difficult_achievements = self._get_difficult_achievements(limit=10)
            
            # 获取解锁趋势
            system_unlock_trend = self._get_system_unlock_trend(days=30)
            
            # 获取用户活跃度分布
            user_activity_distribution = self._get_user_activity_distribution()
            
            return {
                "system_stats": {
                    "total_achievements": total_achievements,
                    "active_achievements": active_achievements,
                    "total_user_achievements": total_user_achievements,
                    "completed_user_achievements": completed_user_achievements,
                    "avg_completion_rate": round(avg_completion_rate, 2),
                    "total_users_with_achievements": self._get_total_users_with_achievements()
                },
                "popular_achievements": popular_achievements,
                "difficult_achievements": difficult_achievements,
                "unlock_trend": system_unlock_trend,
                "user_activity_distribution": user_activity_distribution,
                "calculated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system achievement analytics: {str(e)}")
            return {"error": str(e)}
    
    def _get_popular_achievements(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最受欢迎的成就（解锁次数最多）"""
        try:
            # 使用原生SQL查询以获得更好的性能
            query = """
                SELECT a.id, a.name, a.description, a.achievement_type, a.difficulty,
                       COUNT(ua.id) as unlock_count
                FROM achievements a
                LEFT JOIN user_achievements ua ON a.id = ua.achievement_id 
                    AND ua.status = 'completed' 
                    AND ua.is_deleted = FALSE
                WHERE a.is_deleted = FALSE AND a.status = 'active'
                GROUP BY a.id, a.name, a.description, a.achievement_type, a.difficulty
                ORDER BY unlock_count DESC
                LIMIT :limit
            """
            
            result = self.db.execute(query, {"limit": limit})
            
            popular_achievements = []
            for row in result:
                popular_achievements.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "type": row[3],
                    "difficulty": row[4],
                    "unlock_count": row[5] or 0
                })
            
            return popular_achievements
        except Exception as e:
            logger.error(f"Failed to get popular achievements: {str(e)}")
            return []
    
    def _get_difficult_achievements(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最难解锁的成就（解锁率最低）"""
        try:
            # 计算每个成就的解锁率
            query = """
                SELECT a.id, a.name, a.description, a.achievement_type, a.difficulty,
                       COUNT(ua.id) as total_assignments,
                       SUM(CASE WHEN ua.status = 'completed' THEN 1 ELSE 0 END) as completed_count,
                       CASE WHEN COUNT(ua.id) > 0 
                            THEN (SUM(CASE WHEN ua.status = 'completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(ua.id))
                            ELSE 0 END as completion_rate
                FROM achievements a
                LEFT JOIN user_achievements ua ON a.id = ua.achievement_id 
                    AND ua.is_deleted = FALSE
                WHERE a.is_deleted = FALSE AND a.status = 'active'
                GROUP BY a.id, a.name, a.description, a.achievement_type, a.difficulty
                HAVING COUNT(ua.id) >= 10  -- 至少有10个用户尝试过
                ORDER BY completion_rate ASC
                LIMIT :limit
            """
            
            result = self.db.execute(query, {"limit": limit})
            
            difficult_achievements = []
            for row in result:
                difficult_achievements.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "type": row[3],
                    "difficulty": row[4],
                    "total_assignments": row[5] or 0,
                    "completed_count": row[6] or 0,
                    "completion_rate": round(float(row[7] or 0), 2)
                })
            
            return difficult_achievements
        except Exception as e:
            logger.error(f"Failed to get difficult achievements: {str(e)}")
            return []
    
    def _get_system_unlock_trend(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取系统成就解锁趋势"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            query = """
                SELECT DATE(ua.unlocked_at) as unlock_date,
                       COUNT(ua.id) as unlock_count
                FROM user_achievements ua
                WHERE ua.status = 'completed' 
                    AND ua.unlocked_at >= :start_date
                    AND ua.is_deleted = FALSE
                GROUP BY DATE(ua.unlocked_at)
                ORDER BY unlock_date
            """
            
            result = self.db.execute(query, {"start_date": start_date})
            
            # 创建日期到计数的映射
            daily_counts = {}
            for row in result:
                date_str = row[0].strftime("%Y-%m-%d") if row[0] else None
                if date_str:
                    daily_counts[date_str] = row[1]
            
            # 填充所有日期
            trend_data = []
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                count = daily_counts.get(date, 0)
                trend_data.append({
                    "date": date,
                    "count": count
                })
            
            # 按日期排序
            trend_data.sort(key=lambda x: x["date"])
            
            return trend_data
        except Exception as e:
            logger.error(f"Failed to get system unlock trend: {str(e)}")
            return []
    
    def _get_user_activity_distribution(self) -> Dict[str, int]:
        """获取用户活跃度分布"""
        try:
            # 定义活跃度等级
            activity_levels = {
                "inactive": 0,      # 0-20分
                "casual": 0,        # 21-40分
                "active": 0,        # 41-60分
                "engaged": 0,       # 61-80分
                "highly_engaged": 0 # 81-100分
            }
            
            # 获取所有有成就的用户
            users_with_achievements = self.db.query(User).join(
                UserAchievement, User.id == UserAchievement.user_id
            ).filter(
                UserAchievement.is_deleted == False
            ).distinct().all()
            
            # 计算每个用户的活跃度分数
            for user in users_with_achievements:
                activity_score = self._calculate_activity_score(user.id)
                
                # 分类到不同的活跃度等级
                if activity_score <= 20:
                    activity_levels["inactive"] += 1
                elif activity_score <= 40:
                    activity_levels["casual"] += 1
                elif activity_score <= 60:
                    activity_levels["active"] += 1
                elif activity_score <= 80:
                    activity_levels["engaged"] += 1
                else:
                    activity_levels["highly_engaged"] += 1
            
            return activity_levels
        except Exception as e:
            logger.error(f"Failed to get user activity distribution: {str(e)}")
            return {}
    
    def _get_total_users_with_achievements(self) -> int:
        """获取有成就的用户总数"""
        try:
            count = self.db.query(User).join(
                UserAchievement, User.id == UserAchievement.user_id
            ).filter(
                UserAchievement.is_deleted == False
            ).distinct().count()
            
            return count
        except Exception as e:
            logger.error(f"Failed to get total users with achievements: {str(e)}")
            return 0
    
    def get_achievement_performance_metrics(self) -> Dict[str, Any]:
        """获取成就系统性能指标"""
        try:
            # 计算响应时间指标（这里使用模拟数据，实际应该从监控系统获取）
            response_times = {
                "achievement_unlock": {
                    "avg_response_time_ms": 150,
                    "p95_response_time_ms": 300,
                    "p99_response_time_ms": 500,
                    "success_rate": 99.8
                },
                "badge_grant": {
                    "avg_response_time_ms": 120,
                    "p95_response_time_ms": 250,
                    "p99_response_time_ms": 400,
                    "success_rate": 99.9
                },
                "reward_claim": {
                    "avg_response_time_ms": 180,
                    "p95_response_time_ms": 350,
                    "p99_response_time_ms": 600,
                    "success_rate": 99.7
                }
            }
            
            # 计算系统负载指标
            system_load = {
                "achievements_per_second": self._calculate_achievements_per_second(),
                "concurrent_users": self._estimate_concurrent_users(),
                "database_connections": self._get_database_connection_count()
            }
            
            # 计算错误率指标
            error_rates = {
                "achievement_unlock_errors": self._get_error_count("achievement_unlock"),
                "badge_grant_errors": self._get_error_count("badge_grant"),
                "reward_claim_errors": self._get_error_count("reward_claim"),
                "total_errors_last_24h": self._get_total_errors_last_24h()
            }
            
            return {
                "response_times": response_times,
                "system_load": system_load,
                "error_rates": error_rates,
                "calculated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get achievement performance metrics: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_achievements_per_second(self) -> float:
        """计算每秒成就解锁数量"""
        try:
            # 获取最近1小时的成就解锁数量
            one_hour_ago = datetime.now() - timedelta(hours=1)
            
            count = self.db.query(UserAchievement).filter(
                UserAchievement.status == UserAchievementStatus.COMPLETED,
                UserAchievement.unlocked_at >= one_hour_ago,
                UserAchievement.is_deleted == False
            ).count()
            
            # 计算每秒平均值
            achievements_per_second = count / 3600.0
            
            return round(achievements_per_second, 2)
        except Exception as e:
            logger.error(f"Failed to calculate achievements per second: {str(e)}")
            return 0.0
    
    def _estimate_concurrent_users(self) -> int:
        """估计并发用户数"""
        try:
            # 获取最近5分钟内有活动的用户数
            five_minutes_ago = datetime.now() - timedelta(minutes=5)
            
            # 这里使用简化估计，实际应该从会话系统获取
            count = self.db.query(UserAchievement).filter(
                UserAchievement.updated_at >= five_minutes_ago,
                UserAchievement.is_deleted == False
            ).distinct(UserAchievement.user_id).count()
            
            return count
        except Exception as e:
            logger.error(f"Failed to estimate concurrent users: {str(e)}")
            return 0
    
    def _get_database_connection_count(self) -> int:
        """获取数据库连接数"""
        try:
            # 这里返回模拟数据，实际应该从数据库监控获取
            return 25
        except Exception as e:
            logger.error(f"Failed to get database connection count: {str(e)}")
            return 0
    
    def _get_error_count(self, error_type: str) -> int:
        """获取错误数量"""
        try:
            # 这里返回模拟数据，实际应该从错误日志系统获取
            error_counts = {
                "achievement_unlock": 12,
                "badge_grant": 5,
                "reward_claim": 8
            }
            
            return error_counts.get(error_type, 0)
        except Exception as e:
            logger.error(f"Failed to get error count for {error_type}: {str(e)}")
            return 0
    
    def _get_total_errors_last_24h(self) -> int:
        """获取最近24小时的总错误数"""
        try:
            # 这里返回模拟数据，实际应该从错误日志系统获取
            return 25
        except Exception as e:
            logger.error(f"Failed to get total errors last 24h: {str(e)}")
            return 0
    
    def generate_achievement_recommendations(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """生成成就推荐"""
        try:
            recommendations = []
            
            # 获取用户已解锁的成就
            unlocked_achievement_ids = [
                ua.achievement_id for ua in self.db.query(UserAchievement).filter(
                    UserAchievement.user_id == user_id,
                    UserAchievement.status == UserAchievementStatus.COMPLETED,
                    UserAchievement.is_deleted == False
                ).all()
            ]
            
            # 获取用户进行中的成就
            in_progress_achievements = self.db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.status == UserAchievementStatus.IN_PROGRESS,
                UserAchievement.is_deleted == False
            ).all()
            
            # 推荐1：继续完成进行中的成就
            for ua in in_progress_achievements[:2]:  # 最多推荐2个
                if ua.achievement:
                    progress_percentage = ua.progress_percentage or 0
                    recommendations.append({
                        "type": "continue_progress",
                        "achievement_id": ua.achievement_id,
                        "achievement_name": ua.achievement.name,
                        "description": f"继续完成此成就，当前进度 {progress_percentage}%",
                        "priority": "high",
                        "reason": "您已经开始了这个成就，继续完成它吧！"
                    })
            
            # 推荐2：基于用户兴趣推荐相关成就
            user_interests = self._infer_user_interests(user_id)
            for interest in user_interests[:2]:  # 最多推荐2个
                related_achievements = self.db.query(Achievement).filter(
                    Achievement.tags.contains([interest]),
                    Achievement.id.notin_(unlocked_achievement_ids),
                    Achievement.is_deleted == False,
                    Achievement.status == AchievementStatus.ACTIVE
                ).limit(1).all()
                
                for achievement in related_achievements:
                    recommendations.append({
                        "type": "interest_based",
                        "achievement_id": achievement.id,
                        "achievement_name": achievement.name,
                        "description": achievement.description,
                        "priority": "medium",
                        "reason": f"基于您对'{interest}'的兴趣推荐"
                    })
            
            # 推荐3：推荐热门成就
            popular_achievements = self._get_popular_achievements(limit=10)
            for achievement in popular_achievements[:2]:  # 最多推荐2个
                if achievement["id"] not in unlocked_achievement_ids:
                    recommendations.append({
                        "type": "popular",
                        "achievement_id": achievement["id"],
                        "achievement_name": achievement["name"],
                        "description": achievement["description"],
                        "priority": "medium",
                        "reason": f"这是热门成就，已有{achievement['unlock_count']}人解锁"
                    })
            
            # 限制推荐数量
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Failed to generate achievement recommendations for user {user_id}: {str(e)}")
            return []
    
    def _infer_user_interests(self, user_id: int) -> List[str]:
        """推断用户兴趣"""
        try:
            interests = []
            
            # 获取用户已解锁的成就标签
            unlocked_achievements = self.db.query(UserAchievement).join(
                Achievement, UserAchievement.achievement_id == Achievement.id
            ).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.status == UserAchievementStatus.COMPLETED,
                UserAchievement.is_deleted == False,
                Achievement.is_deleted == False
            ).all()
            
            # 收集所有标签
            all_tags = []
            for ua in unlocked_achievements:
                if ua.achievement and ua.achievement.tags:
                    all_tags.extend(ua.achievement.tags)
            
            # 统计标签出现频率
            tag_counter = Counter(all_tags)
            
            # 返回出现频率最高的标签
            return [tag for tag, count in tag_counter.most_common(5)]
            
        except Exception as e:
            logger.error(f"Failed to infer user interests for user {user_id}: {str(e)}")
            return []
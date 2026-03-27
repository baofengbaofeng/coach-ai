"""
成就系统处理器

实现成就系统的RESTful API接口
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

import tornado.web
from tornado.escape import json_decode

from coding.tornado.core.base_handler import BaseHandler
from coding.tornado.core.error_handler import APIError
from coding.tornado.core.middleware import auth_required
from coding.database.connection import get_db_session

from .services import (
    AchievementService, UserAchievementService, BadgeService,
    RewardService, AchievementTriggerService
)
from .models import (
    AchievementProgressUpdate, AchievementStats, UserAchievementSummary,
    TriggerEventType
)

logger = logging.getLogger(__name__)


class AchievementListHandler(BaseHandler):
    """成就列表处理器"""
    
    @auth_required
    async def get(self):
        """获取成就列表"""
        try:
            # 获取查询参数
            achievement_type = self.get_argument("type", None)
            difficulty = self.get_argument("difficulty", None)
            status = self.get_argument("status", None)
            limit = int(self.get_argument("limit", 100))
            offset = int(self.get_argument("offset", 0))
            
            # 验证参数
            if limit > 1000:
                limit = 1000
            if limit < 1:
                limit = 1
            
            with get_db_session() as session:
                service = AchievementService(session)
                achievements, total = service.get_achievements(
                    achievement_type=achievement_type,
                    difficulty=difficulty,
                    status=status,
                    limit=limit,
                    offset=offset
                )
                
                # 转换为字典
                achievements_data = [achievement.to_dict() for achievement in achievements]
                
                self.write_success({
                    "achievements": achievements_data,
                    "total": total,
                    "limit": limit,
                    "offset": offset
                })
                
        except Exception as e:
            logger.error(f"Failed to get achievements: {str(e)}")
            self.write_error(500, "Internal server error")
    
    @auth_required
    async def post(self):
        """创建成就"""
        try:
            # 获取请求数据
            data = json_decode(self.request.body)
            
            # 验证必要字段
            required_fields = ["name", "description", "trigger_type", "target_value"]
            for field in required_fields:
                if field not in data:
                    raise APIError(400, f"Missing required field: {field}")
            
            with get_db_session() as session:
                service = AchievementService(session)
                achievement = service.create_achievement(data)
                
                if not achievement:
                    raise APIError(500, "Failed to create achievement")
                
                self.write_success({
                    "achievement": achievement.to_dict(),
                    "message": "Achievement created successfully"
                }, status_code=201)
                
        except APIError as e:
            self.write_error(e.status_code, e.message)
        except Exception as e:
            logger.error(f"Failed to create achievement: {str(e)}")
            self.write_error(500, "Internal server error")


class AchievementDetailHandler(BaseHandler):
    """成就详情处理器"""
    
    @auth_required
    async def get(self, achievement_id: str):
        """获取成就详情"""
        try:
            achievement_id_int = int(achievement_id)
            
            with get_db_session() as session:
                service = AchievementService(session)
                achievement = service.get_achievement_by_id(achievement_id_int)
                
                if not achievement:
                    raise APIError(404, "Achievement not found")
                
                self.write_success({
                    "achievement": achievement.to_dict()
                })
                
        except ValueError:
            self.write_error(400, "Invalid achievement ID")
        except APIError as e:
            self.write_error(e.status_code, e.message)
        except Exception as e:
            logger.error(f"Failed to get achievement {achievement_id}: {str(e)}")
            self.write_error(500, "Internal server error")
    
    @auth_required
    async def put(self, achievement_id: str):
        """更新成就"""
        try:
            achievement_id_int = int(achievement_id)
            data = json_decode(self.request.body)
            
            with get_db_session() as session:
                service = AchievementService(session)
                achievement = service.update_achievement(achievement_id_int, data)
                
                if not achievement:
                    raise APIError(404, "Achievement not found")
                
                self.write_success({
                    "achievement": achievement.to_dict(),
                    "message": "Achievement updated successfully"
                })
                
        except ValueError:
            self.write_error(400, "Invalid achievement ID")
        except APIError as e:
            self.write_error(e.status_code, e.message)
        except Exception as e:
            logger.error(f"Failed to update achievement {achievement_id}: {str(e)}")
            self.write_error(500, "Internal server error")
    
    @auth_required
    async def delete(self, achievement_id: str):
        """删除成就"""
        try:
            achievement_id_int = int(achievement_id)
            
            with get_db_session() as session:
                service = AchievementService(session)
                success = service.delete_achievement(achievement_id_int)
                
                if not success:
                    raise APIError(404, "Achievement not found")
                
                self.write_success({
                    "message": "Achievement deleted successfully"
                })
                
        except ValueError:
            self.write_error(400, "Invalid achievement ID")
        except APIError as e:
            self.write_error(e.status_code, e.message)
        except Exception as e:
            logger.error(f"Failed to delete achievement {achievement_id}: {str(e)}")
            self.write_error(500, "Internal server error")


class UserAchievementListHandler(BaseHandler):
    """用户成就列表处理器"""
    
    @auth_required
    async def get(self, user_id: str = None):
        """获取用户成就列表"""
        try:
            # 如果未指定用户ID，使用当前用户
            if user_id is None:
                user_id = self.current_user.id
            else:
                user_id = int(user_id)
            
            # 获取查询参数
            status = self.get_argument("status", None)
            limit = int(self.get_argument("limit", 100))
            offset = int(self.get_argument("offset", 0))
            
            # 验证参数
            if limit > 1000:
                limit = 1000
            if limit < 1:
                limit = 1
            
            with get_db_session() as session:
                service = UserAchievementService(session)
                user_achievements, total = service.get_user_achievements(
                    user_id=user_id,
                    status=status,
                    limit=limit,
                    offset=offset
                )
                
                # 转换为字典
                achievements_data = []
                for ua in user_achievements:
                    achievement_data = ua.to_dict()
                    # 添加成就详情
                    if ua.achievement:
                        achievement_data["achievement"] = ua.achievement.to_dict()
                    achievements_data.append(achievement_data)
                
                self.write_success({
                    "user_achievements": achievements_data,
                    "total": total,
                    "limit": limit,
                    "offset": offset
                })
                
        except Exception as e:
            logger.error(f"Failed to get user achievements: {str(e)}")
            self.write_error(500, "Internal server error")


class UserAchievementDetailHandler(BaseHandler):
    """用户成就详情处理器"""
    
    @auth_required
    async def get(self, user_id: str, achievement_id: str):
        """获取用户成就详情"""
        try:
            user_id_int = int(user_id)
            achievement_id_int = int(achievement_id)
            
            with get_db_session() as session:
                service = UserAchievementService(session)
                user_achievement = service.get_user_achievement(user_id_int, achievement_id_int)
                
                if not user_achievement:
                    raise APIError(404, "User achievement not found")
                
                achievement_data = user_achievement.to_dict()
                if user_achievement.achievement:
                    achievement_data["achievement"] = user_achievement.achievement.to_dict()
                
                self.write_success({
                    "user_achievement": achievement_data
                })
                
        except ValueError:
            self.write_error(400, "Invalid user ID or achievement ID")
        except APIError as e:
            self.write_error(e.status_code, e.message)
        except Exception as e:
            logger.error(f"Failed to get user achievement: {str(e)}")
            self.write_error(500, "Internal server error")


class AchievementProgressHandler(BaseHandler):
    """成就进度处理器"""
    
    @auth_required
    async def post(self):
        """更新成就进度"""
        try:
            # 获取请求数据
            data = json_decode(self.request.body)
            
            # 验证必要字段
            required_fields = ["user_id", "achievement_id", "progress_delta"]
            for field in required_fields:
                if field not in data:
                    raise APIError(400, f"Missing required field: {field}")
            
            # 创建进度更新对象
            progress_update = AchievementProgressUpdate(
                user_id=data["user_id"],
                achievement_id=data["achievement_id"],
                progress_delta=data["progress_delta"],
                event_type=data.get("event_type"),
                event_data=data.get("event_data", {})
            )
            
            with get_db_session() as session:
                service = UserAchievementService(session)
                user_achievement = service.update_user_achievement_progress(progress_update)
                
                if not user_achievement:
                    raise APIError(404, "Achievement not found or not active")
                
                achievement_data = user_achievement.to_dict()
                if user_achievement.achievement:
                    achievement_data["achievement"] = user_achievement.achievement.to_dict()
                
                self.write_success({
                    "user_achievement": achievement_data,
                    "message": "Achievement progress updated successfully"
                })
                
        except APIError as e:
            self.write_error(e.status_code, e.message)
        except Exception as e:
            logger.error(f"Failed to update achievement progress: {str(e)}")
            self.write_error(500, "Internal server error")


class UserAchievementStatsHandler(BaseHandler):
    """用户成就统计处理器"""
    
    @auth_required
    async def get(self, user_id: str = None):
        """获取用户成就统计"""
        try:
            # 如果未指定用户ID，使用当前用户
            if user_id is None:
                user_id = self.current_user.id
            else:
                user_id = int(user_id)
            
            with get_db_session() as session:
                service = UserAchievementService(session)
                stats = service.get_user_achievement_stats(user_id)
                
                self.write_success({
                    "user_id": user_id,
                    "stats": stats.to_dict()
                })
                
        except ValueError:
            self.write_error(400, "Invalid user ID")
        except Exception as e:
            logger.error(f"Failed to get user achievement stats: {str(e)}")
            self.write_error(500, "Internal server error")


class AchievementTriggerHandler(BaseHandler):
    """成就触发处理器"""
    
    @auth_required
    async def post(self):
        """触发成就事件"""
        try:
            # 获取请求数据
            data = json_decode(self.request.body)
            
            # 验证必要字段
            required_fields = ["event_type", "user_id", "event_data"]
            for field in required_fields:
                if field not in data:
                    raise APIError(400, f"Missing required field: {field}")
            
            with get_db_session() as session:
                service = AchievementTriggerService(session)
                notifications = service.handle_event(
                    event_type=data["event_type"],
                    user_id=data["user_id"],
                    event_data=data["event_data"]
                )
                
                # 转换为字典
                notifications_data = [notification.to_dict() for notification in notifications]
                
                self.write_success({
                    "notifications": notifications_data,
                    "count": len(notifications_data),
                    "message": "Event processed successfully"
                })
                
        except APIError as e:
            self.write_error(e.status_code, e.message)
        except Exception as e:
            logger.error(f"Failed to trigger achievement event: {str(e)}")
            self.write_error(500, "Internal server error")


class BadgeGrantHandler(BaseHandler):
    """徽章授予处理器"""
    
    @auth_required
    async def post(self):
        """授予徽章给用户"""
        try:
            # 获取请求数据
            data = json_decode(self.request.body)
            
            # 验证必要字段
            required_fields = ["user_id", "badge_id"]
            for field in required_fields:
                if field not in data:
                    raise APIError(400, f"Missing required field: {field}")
            
            with get_db_session() as session:
                service = BadgeService(session)
                user_badge = service.grant_badge_to_user(
                    user_id=data["user_id"],
                    badge_id=data["badge_id"],
                    grant_reason=data.get("grant_reason"),
                    granted_by=data.get("granted_by")
                )
                
                if not user_badge:
                    raise APIError(404, "Badge not found or not active")
                
                badge_data = user_badge.to_dict()
                if user_badge.badge:
                    badge_data["badge"] = user_badge.badge.to_dict()
                
                self.write_success({
                    "user_badge": badge_data,
                    "message": "Badge granted successfully"
                }, status_code=201)
                
        except APIError as e:
            self.write_error(e.status_code, e.message)
        except Exception as e:
            logger.error(f"Failed to grant badge: {str(e)}")
            self.write_error(500, "Internal server error")


class RewardClaimHandler(BaseHandler):
    """奖励领取处理器"""
    
    @auth_required
    async def post(self):
        """用户领取奖励"""
        try:
            # 获取请求数据
            data = json_decode(self.request.body)
            
            # 验证必要字段
            required_fields = ["user_id", "reward_id"]
            for field in required_fields:
                if field not in data:
                    raise APIError(400, f"Missing required field: {field}")
            
            with get_db_session() as session:
                service = RewardService(session)
                user_reward = service.claim_reward(
                    user_id=data["user_id"],
                    reward_id=data["reward_id"],
                    claim_reason=data.get("claim_reason")
                )
                
                if not user_reward:
                    raise APIError(404, "Reward not found or not available")
                
                reward_data = user_reward.to_dict()
                if user_reward.reward:
                    reward_data["reward"] = user_reward.reward.to_dict()
                
                self.write_success({
                    "user_reward": reward_data,
                    "message": "Reward claimed successfully"
                }, status_code=201)
                
        except APIError as e:
            self.write_error(e.status_code, e.message)
        except Exception as e:
            logger.error(f"Failed to claim reward: {str(e)}")
            self.write_error(500, "Internal server error")


class UserBadgeListHandler(BaseHandler):
    """用户徽章列表处理器"""
    
    @auth_required
    async def get(self, user_id: str = None):
        """获取用户徽章列表"""
        try:
            # 如果未指定用户ID，使用当前用户
            if user_id is None:
                user_id = self.current_user.id
            else:
                user_id = int(user_id)
            
            # 获取查询参数
            limit = int(self.get_argument("limit", 100))
            offset = int(self.get_argument("offset", 0))
            
            # 验证参数
            if limit > 1000:
                limit = 1000
            if limit < 1:
                limit = 1
            
            with get_db_session() as session:
                # 查询用户徽章
                from sqlalchemy.orm import joinedload
                from coding.database.models import UserBadge, Badge
                
                query = session.query(UserBadge).filter(
                    UserBadge.user_id == user_id,
                    UserBadge.is_deleted == False
                ).options(joinedload(UserBadge.badge))
                
                # 总数
                total = query.count()
                
                # 分页
                user_badges = query.order_by(
                    UserBadge.granted_at.desc()
                ).offset(offset).limit(limit).all()
                
                # 转换为字典
                badges_data = []
                for ub in user_badges:
                    badge_data = ub.to_dict()
                    if ub.badge:
                        badge_data["badge"] = ub.badge.to_dict()
                    badges_data.append(badge_data)
                
                self.write_success({
                    "user_badges": badges_data,
                    "total": total,
                    "limit": limit,
                    "offset": offset
                })
                
        except Exception as e:
            logger.error(f"Failed to get user badges: {str(e)}")
            self.write_error(500, "Internal server error")
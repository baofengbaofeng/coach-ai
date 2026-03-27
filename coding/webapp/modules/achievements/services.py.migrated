"""
成就系统服务

实现成就系统的核心业务逻辑
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from database.models import (
    Achievement, AchievementType, AchievementDifficulty, AchievementStatus,
    UserAchievement, UserAchievementStatus,
    Badge, BadgeRarity, BadgeType, BadgeStatus,
    UserBadge,
    Reward, RewardType, RewardStatus,
    UserReward, UserRewardStatus,
    User
)
from .models import (
    AchievementProgressUpdate, AchievementUnlockNotification,
    BadgeGrantNotification, RewardClaimNotification,
    AchievementStats, UserAchievementSummary, TriggerEventType
)
from .notifications import notification_service, social_share_service

logger = logging.getLogger(__name__)


class AchievementService:
    """成就服务类"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_achievement_by_id(self, achievement_id: int) -> Optional[Achievement]:
        """根据ID获取成就"""
        try:
            return self.db.query(Achievement).filter(
                Achievement.id == achievement_id,
                Achievement.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"Failed to get achievement by id {achievement_id}: {str(e)}")
            return None
    
    def get_achievements(
        self,
        achievement_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[Achievement], int]:
        """获取成就列表"""
        try:
            query = self.db.query(Achievement).filter(Achievement.is_deleted == False)
            
            # 过滤条件
            if achievement_type:
                query = query.filter(Achievement.achievement_type == achievement_type)
            if difficulty:
                query = query.filter(Achievement.difficulty == difficulty)
            if status:
                query = query.filter(Achievement.status == status)
            
            # 总数
            total = query.count()
            
            # 分页
            achievements = query.order_by(
                Achievement.display_order,
                Achievement.created_at.desc()
            ).offset(offset).limit(limit).all()
            
            return achievements, total
        except Exception as e:
            logger.error(f"Failed to get achievements: {str(e)}")
            return [], 0
    
    def create_achievement(self, achievement_data: Dict[str, Any]) -> Optional[Achievement]:
        """创建成就"""
        try:
            achievement = Achievement(**achievement_data)
            self.db.add(achievement)
            self.db.commit()
            self.db.refresh(achievement)
            
            logger.info(f"Created achievement: {achievement.id} - {achievement.name}")
            return achievement
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create achievement: {str(e)}")
            return None
    
    def update_achievement(self, achievement_id: int, update_data: Dict[str, Any]) -> Optional[Achievement]:
        """更新成就"""
        try:
            achievement = self.get_achievement_by_id(achievement_id)
            if not achievement:
                return None
            
            for key, value in update_data.items():
                if hasattr(achievement, key):
                    setattr(achievement, key, value)
            
            achievement.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(achievement)
            
            logger.info(f"Updated achievement: {achievement.id}")
            return achievement
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update achievement {achievement_id}: {str(e)}")
            return None
    
    def delete_achievement(self, achievement_id: int) -> bool:
        """删除成就（软删除）"""
        try:
            achievement = self.get_achievement_by_id(achievement_id)
            if not achievement:
                return False
            
            achievement.is_deleted = True
            achievement.updated_at = datetime.now()
            self.db.commit()
            
            logger.info(f"Deleted achievement: {achievement_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete achievement {achievement_id}: {str(e)}")
            return False


class UserAchievementService:
    """用户成就服务类"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_user_achievement(self, user_id: int, achievement_id: int) -> Optional[UserAchievement]:
        """获取用户成就"""
        try:
            return self.db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement_id,
                UserAchievement.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"Failed to get user achievement for user {user_id}, achievement {achievement_id}: {str(e)}")
            return None
    
    def get_user_achievements(
        self,
        user_id: int,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[UserAchievement], int]:
        """获取用户成就列表"""
        try:
            query = self.db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.is_deleted == False
            )
            
            if status:
                query = query.filter(UserAchievement.status == status)
            
            # 总数
            total = query.count()
            
            # 分页
            user_achievements = query.order_by(
                UserAchievement.updated_at.desc()
            ).offset(offset).limit(limit).all()
            
            return user_achievements, total
        except Exception as e:
            logger.error(f"Failed to get user achievements for user {user_id}: {str(e)}")
            return [], 0
    
    def update_user_achievement_progress(self, progress_update: AchievementProgressUpdate) -> Optional[UserAchievement]:
        """更新用户成就进度"""
        try:
            # 获取成就
            achievement = self.db.query(Achievement).filter(
                Achievement.id == progress_update.achievement_id,
                Achievement.is_deleted == False,
                Achievement.status == AchievementStatus.ACTIVE
            ).first()
            
            if not achievement:
                logger.warning(f"Achievement {progress_update.achievement_id} not found or not active")
                return None
            
            # 获取或创建用户成就
            user_achievement = self.get_user_achievement(
                progress_update.user_id,
                progress_update.achievement_id
            )
            
            if not user_achievement:
                user_achievement = UserAchievement(
                    user_id=progress_update.user_id,
                    achievement_id=progress_update.achievement_id,
                    target_value=achievement.target_value,
                    status=UserAchievementStatus.LOCKED,
                    progress=0,
                    progress_percentage=0
                )
                self.db.add(user_achievement)
            
            # 更新进度
            new_progress = user_achievement.progress + progress_update.progress_delta
            user_achievement.update_progress(new_progress)
            
            # 检查是否解锁
            if user_achievement.status == UserAchievementStatus.COMPLETED and not user_achievement.unlocked_at:
                user_achievement.unlocked_at = datetime.now()
                user_achievement.is_new = True
                
                # 更新成就统计
                achievement.unlock_count += 1
                if not achievement.first_unlock_at:
                    achievement.first_unlock_at = datetime.now()
                achievement.last_unlock_at = datetime.now()
                
                # 触发奖励
                self._trigger_achievement_rewards(progress_update.user_id, achievement)
                
                # 发送成就解锁通知
                self._send_achievement_unlock_notification(
                    progress_update.user_id, 
                    achievement, 
                    user_achievement
                )
                
                # 记录日志
                logger.info(f"User {progress_update.user_id} unlocked achievement {achievement.id}: {achievement.name}")
            
            self.db.commit()
            self.db.refresh(user_achievement)
            
            return user_achievement
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update user achievement progress: {str(e)}")
            return None
    
    def _trigger_achievement_rewards(self, user_id: int, achievement: Achievement):
        """触发成就奖励"""
        try:
            # 发放积分奖励
            if achievement.reward_points > 0:
                # TODO: 实现积分系统
                pass
            
            # 发放徽章奖励
            if achievement.reward_badge_id:
                badge_service = BadgeService(self.db)
                user_badge = badge_service.grant_badge_to_user(
                    user_id=user_id,
                    badge_id=achievement.reward_badge_id,
                    grant_reason=f"Achievement unlocked: {achievement.name}"
                )
                
                # 发送徽章授予通知
                if user_badge:
                    self._send_badge_grant_notification(user_id, user_badge.badge, user_badge)
            
            # 发放物品奖励
            if achievement.reward_items:
                # TODO: 实现物品系统
                pass
                
        except Exception as e:
            logger.error(f"Failed to trigger achievement rewards: {str(e)}")
    
    def _send_achievement_unlock_notification(self, user_id: int, achievement: Achievement, user_achievement: UserAchievement):
        """发送成就解锁通知"""
        try:
            notification = AchievementUnlockNotification(
                user_id=user_id,
                achievement=achievement,
                user_achievement=user_achievement
            )
            
            # 发送通知
            notification_service.send_achievement_unlock_notification(notification)
            
            # 可选：自动分享到社交平台
            # social_share_service.share_achievement(notification.to_dict())
            
        except Exception as e:
            logger.error(f"Failed to send achievement unlock notification: {str(e)}")
    
    def _send_badge_grant_notification(self, user_id: int, badge: Badge, user_badge: UserBadge):
        """发送徽章授予通知"""
        try:
            notification = BadgeGrantNotification(
                user_id=user_id,
                badge=badge,
                user_badge=user_badge
            )
            
            # 发送通知
            notification_service.send_badge_grant_notification(notification)
            
            # 可选：自动分享到社交平台
            # social_share_service.share_badge(notification.to_dict())
            
        except Exception as e:
            logger.error(f"Failed to send badge grant notification: {str(e)}")
    
    def _send_reward_claim_notification(self, user_id: int, reward: Reward, user_reward: UserReward):
        """发送奖励领取通知"""
        try:
            notification = RewardClaimNotification(
                user_id=user_id,
                reward=reward,
                user_reward=user_reward
            )
            
            # 发送通知
            notification_service.send_reward_claim_notification(notification)
            
        except Exception as e:
            logger.error(f"Failed to send reward claim notification: {str(e)}")
    
    def get_user_achievement_stats(self, user_id: int) -> AchievementStats:
        """获取用户成就统计"""
        try:
            # 获取用户所有成就
            user_achievements, total = self.get_user_achievements(user_id)
            
            # 统计
            stats = AchievementStats()
            stats.total_achievements = total
            
            for ua in user_achievements:
                if ua.status == UserAchievementStatus.COMPLETED:
                    stats.unlocked_achievements += 1
                elif ua.status == UserAchievementStatus.IN_PROGRESS:
                    stats.in_progress_achievements += 1
                else:
                    stats.locked_achievements += 1
            
            # 计算完成率
            if stats.total_achievements > 0:
                stats.completion_rate = (stats.unlocked_achievements / stats.total_achievements) * 100
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get user achievement stats for user {user_id}: {str(e)}")
            return AchievementStats()


class BadgeService:
    """徽章服务类"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def grant_badge_to_user(
        self,
        user_id: int,
        badge_id: int,
        grant_reason: str = None,
        granted_by: int = None
    ) -> Optional[UserBadge]:
        """授予徽章给用户"""
        try:
            # 检查徽章是否存在
            badge = self.db.query(Badge).filter(
                Badge.id == badge_id,
                Badge.is_deleted == False,
                Badge.status == BadgeStatus.ACTIVE
            ).first()
            
            if not badge:
                logger.warning(f"Badge {badge_id} not found or not active")
                return None
            
            # 检查用户是否已有该徽章
            existing_badge = self.db.query(UserBadge).filter(
                UserBadge.user_id == user_id,
                UserBadge.badge_id == badge_id,
                UserBadge.is_deleted == False
            ).first()
            
            if existing_badge:
                logger.info(f"User {user_id} already has badge {badge_id}")
                return existing_badge
            
            # 创建用户徽章
            user_badge = UserBadge(
                user_id=user_id,
                badge_id=badge_id,
                granted_at=datetime.now(),
                granted_by=granted_by,
                grant_reason=grant_reason,
                is_new=True
            )
            
            self.db.add(user_badge)
            
            # 更新徽章统计
            badge.grant_count += 1
            if not badge.first_grant_at:
                badge.first_grant_at = datetime.now()
            badge.last_grant_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(user_badge)
            
            # 发送徽章授予通知
            self._send_badge_grant_notification(user_id, badge, user_badge)
            
            logger.info(f"Granted badge {badge_id} to user {user_id}")
            return user_badge
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to grant badge to user: {str(e)}")
            return None


class RewardService:
    """奖励服务类"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def claim_reward(
        self,
        user_id: int,
        reward_id: int,
        claim_reason: str = None
    ) -> Optional[UserReward]:
        """用户领取奖励"""
        try:
            # 检查奖励是否存在且可用
            reward = self.db.query(Reward).filter(
                Reward.id == reward_id,
                Reward.is_deleted == False,
                Reward.status == RewardStatus.ACTIVE
            ).first()
            
            if not reward or not reward.is_available():
                logger.warning(f"Reward {reward_id} not found or not available")
                return None
            
            # 检查用户领取限制
            user_claim_count = self.db.query(UserReward).filter(
                UserReward.user_id == user_id,
                UserReward.reward_id == reward_id,
                UserReward.is_deleted == False
            ).count()
            
            if reward.per_user_limit > 0 and user_claim_count >= reward.per_user_limit:
                logger.warning(f"User {user_id} has reached claim limit for reward {reward_id}")
                return None
            
            # 创建用户奖励记录
            user_reward = UserReward(
                user_id=user_id,
                reward_id=reward_id,
                claimed_at=datetime.now(),
                claim_reason=claim_reason,
                reward_data=reward.reward_config,
                reward_value=reward.value,
                status=UserRewardStatus.CLAIMED
            )
            
            self.db.add(user_reward)
            
            # 更新奖励统计
            reward.claim_count += 1
            
            self.db.commit()
            self.db.refresh(user_reward)
            
            # 发送奖励领取通知
            self._send_reward_claim_notification(user_id, reward, user_reward)
            
            logger.info(f"User {user_id} claimed reward {reward_id}")
            return user_reward
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to claim reward: {str(e)}")
            return None


class AchievementTriggerService:
    """成就触发服务类"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.user_achievement_service = UserAchievementService(db_session)
    
    def handle_event(self, event_type: str, user_id: int, event_data: Dict[str, Any]) -> List[AchievementUnlockNotification]:
        """处理事件并触发成就"""
        notifications = []
        
        try:
            # 根据事件类型获取相关成就
            achievements = self.db.query(Achievement).filter(
                Achievement.trigger_type == event_type,
                Achievement.is_deleted == False,
                Achievement.status == AchievementStatus.ACTIVE
            ).all()
            
            for achievement in achievements:
                # 检查触发条件
                if self._check_trigger_condition(achievement, event_data):
                    # 更新成就进度
                    progress_update = AchievementProgressUpdate(
                        user_id=user_id,
                        achievement_id=achievement.id,
                        progress_delta=1,
                        event_type=event_type,
                        event_data=event_data
                    )
                    
                    user_achievement = self.user_achievement_service.update_user_achievement_progress(progress_update)
                    
                    if user_achievement and user_achievement.status == UserAchievementStatus.COMPLETED:
                        # 创建解锁通知
                        notification = AchievementUnlockNotification(
                            user_id=user_id,
                            achievement=achievement,
                            user_achievement=user_achievement
                        )
                        notifications.append(notification)
            
            return notifications
        except Exception as e:
            logger.error(f"Failed to handle event {event_type} for user {user_id}: {str(e)}")
            return notifications
    
    def _check_trigger_condition(self, achievement: Achievement, event_data: Dict[str, Any]) -> bool:
        """检查触发条件"""
        try:
            trigger_config = achievement.trigger_config
            
            # 简单的条件检查逻辑
            # 实际项目中需要根据具体的触发条件实现更复杂的逻辑
            if not trigger_config:
                return True
            
            # 示例：检查事件数据是否匹配配置
            for key, expected_value in trigger_config.items():
                if key in event_data:
                    if event_data[key] != expected_value:
                        return False
                else:
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Failed to check trigger condition: {str(e)}")
            return False
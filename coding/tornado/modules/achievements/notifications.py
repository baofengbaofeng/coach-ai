"""
成就通知服务

实现成就解锁的实时通知功能，包括应用内通知、推送通知和社交分享
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from .models import (
    AchievementUnlockNotification, BadgeGrantNotification, RewardClaimNotification
)
from coding.database.models import (
    User, Achievement, UserAchievement, Badge, UserBadge, Reward, UserReward
)

logger = logging.getLogger(__name__)


class AchievementNotificationService:
    """成就通知服务类"""
    
    def __init__(self):
        self.notification_channels = []
    
    def register_channel(self, channel):
        """注册通知渠道"""
        self.notification_channels.append(channel)
        logger.info(f"Registered notification channel: {channel.__class__.__name__}")
    
    def send_achievement_unlock_notification(self, notification: AchievementUnlockNotification):
        """发送成就解锁通知"""
        try:
            notification_data = notification.to_dict()
            
            # 发送到所有注册的渠道
            for channel in self.notification_channels:
                try:
                    channel.send_achievement_unlock(notification_data)
                except Exception as e:
                    logger.error(f"Failed to send notification via {channel.__class__.__name__}: {str(e)}")
            
            logger.info(f"Sent achievement unlock notification for user {notification.user_id}, achievement {notification.achievement.id}")
            
        except Exception as e:
            logger.error(f"Failed to send achievement unlock notification: {str(e)}")
    
    def send_badge_grant_notification(self, notification: BadgeGrantNotification):
        """发送徽章授予通知"""
        try:
            notification_data = notification.to_dict()
            
            # 发送到所有注册的渠道
            for channel in self.notification_channels:
                try:
                    channel.send_badge_grant(notification_data)
                except Exception as e:
                    logger.error(f"Failed to send notification via {channel.__class__.__name__}: {str(e)}")
            
            logger.info(f"Sent badge grant notification for user {notification.user_id}, badge {notification.badge.id}")
            
        except Exception as e:
            logger.error(f"Failed to send badge grant notification: {str(e)}")
    
    def send_reward_claim_notification(self, notification: RewardClaimNotification):
        """发送奖励领取通知"""
        try:
            notification_data = notification.to_dict()
            
            # 发送到所有注册的渠道
            for channel in self.notification_channels:
                try:
                    channel.send_reward_claim(notification_data)
                except Exception as e:
                    logger.error(f"Failed to send notification via {channel.__class__.__name__}: {str(e)}")
            
            logger.info(f"Sent reward claim notification for user {notification.user_id}, reward {notification.reward.id}")
            
        except Exception as e:
            logger.error(f"Failed to send reward claim notification: {str(e)}")


class InAppNotificationChannel:
    """应用内通知渠道"""
    
    def __init__(self):
        self.name = "in_app"
    
    def send_achievement_unlock(self, notification_data: Dict[str, Any]):
        """发送应用内成就解锁通知"""
        try:
            # 这里应该实现实际的应用内通知逻辑
            # 例如：保存到数据库、触发WebSocket事件等
            
            notification = {
                "type": "achievement_unlocked",
                "user_id": notification_data["user_id"],
                "title": "成就解锁！",
                "message": f"恭喜解锁成就：{notification_data['achievement']['name']}",
                "data": notification_data,
                "timestamp": datetime.now().isoformat(),
                "read": False
            }
            
            # 保存到数据库（这里需要实现数据库操作）
            # self._save_notification_to_db(notification)
            
            # 触发实时事件（这里需要实现WebSocket推送）
            # self._trigger_realtime_event(notification)
            
            logger.debug(f"In-app notification created: {notification['title']}")
            
        except Exception as e:
            logger.error(f"Failed to create in-app notification: {str(e)}")
    
    def send_badge_grant(self, notification_data: Dict[str, Any]):
        """发送应用内徽章授予通知"""
        try:
            notification = {
                "type": "badge_granted",
                "user_id": notification_data["user_id"],
                "title": "获得新徽章！",
                "message": f"恭喜获得徽章：{notification_data['badge']['name']}",
                "data": notification_data,
                "timestamp": datetime.now().isoformat(),
                "read": False
            }
            
            logger.debug(f"In-app badge notification created: {notification['title']}")
            
        except Exception as e:
            logger.error(f"Failed to create in-app badge notification: {str(e)}")
    
    def send_reward_claim(self, notification_data: Dict[str, Any]):
        """发送应用内奖励领取通知"""
        try:
            notification = {
                "type": "reward_claimed",
                "user_id": notification_data["user_id"],
                "title": "奖励已领取！",
                "message": f"成功领取奖励：{notification_data['reward']['name']}",
                "data": notification_data,
                "timestamp": datetime.now().isoformat(),
                "read": False
            }
            
            logger.debug(f"In-app reward notification created: {notification['title']}")
            
        except Exception as e:
            logger.error(f"Failed to create in-app reward notification: {str(e)}")


class PushNotificationChannel:
    """推送通知渠道"""
    
    def __init__(self):
        self.name = "push"
    
    def send_achievement_unlock(self, notification_data: Dict[str, Any]):
        """发送推送成就解锁通知"""
        try:
            # 这里应该实现实际的推送通知逻辑
            # 例如：调用Firebase Cloud Messaging、Apple Push Notification Service等
            
            push_payload = {
                "to": f"/topics/user_{notification_data['user_id']}",
                "notification": {
                    "title": "🎉 成就解锁！",
                    "body": f"恭喜解锁成就：{notification_data['achievement']['name']}",
                    "sound": "default",
                    "badge": "1"
                },
                "data": {
                    "type": "achievement_unlocked",
                    "achievement_id": notification_data["achievement"]["id"],
                    "achievement_name": notification_data["achievement"]["name"],
                    "timestamp": notification_data["timestamp"]
                }
            }
            
            # 实际发送推送通知
            # self._send_push_notification(push_payload)
            
            logger.debug(f"Push notification prepared: {push_payload['notification']['title']}")
            
        except Exception as e:
            logger.error(f"Failed to prepare push notification: {str(e)}")
    
    def send_badge_grant(self, notification_data: Dict[str, Any]):
        """发送推送徽章授予通知"""
        try:
            push_payload = {
                "to": f"/topics/user_{notification_data['user_id']}",
                "notification": {
                    "title": "🏆 获得新徽章！",
                    "body": f"恭喜获得徽章：{notification_data['badge']['name']}",
                    "sound": "default",
                    "badge": "1"
                },
                "data": {
                    "type": "badge_granted",
                    "badge_id": notification_data["badge"]["id"],
                    "badge_name": notification_data["badge"]["name"],
                    "timestamp": notification_data["timestamp"]
                }
            }
            
            logger.debug(f"Push badge notification prepared: {push_payload['notification']['title']}")
            
        except Exception as e:
            logger.error(f"Failed to prepare push badge notification: {str(e)}")
    
    def send_reward_claim(self, notification_data: Dict[str, Any]):
        """发送推送奖励领取通知"""
        try:
            push_payload = {
                "to": f"/topics/user_{notification_data['user_id']}",
                "notification": {
                    "title": "🎁 奖励已领取！",
                    "body": f"成功领取奖励：{notification_data['reward']['name']}",
                    "sound": "default",
                    "badge": "1"
                },
                "data": {
                    "type": "reward_claimed",
                    "reward_id": notification_data["reward"]["id"],
                    "reward_name": notification_data["reward"]["name"],
                    "timestamp": notification_data["timestamp"]
                }
            }
            
            logger.debug(f"Push reward notification prepared: {push_payload['notification']['title']}")
            
        except Exception as e:
            logger.error(f"Failed to prepare push reward notification: {str(e)}")


class EmailNotificationChannel:
    """邮件通知渠道"""
    
    def __init__(self):
        self.name = "email"
    
    def send_achievement_unlock(self, notification_data: Dict[str, Any]):
        """发送邮件成就解锁通知"""
        try:
            # 这里应该实现实际的邮件发送逻辑
            
            email_data = {
                "to": f"user_{notification_data['user_id']}@example.com",  # 实际应该从数据库获取用户邮箱
                "subject": "🎉 恭喜解锁新成就！",
                "template": "achievement_unlocked",
                "data": {
                    "user_name": "用户",  # 实际应该从数据库获取用户名
                    "achievement_name": notification_data["achievement"]["name"],
                    "achievement_description": notification_data["achievement"]["description"],
                    "unlock_time": notification_data["timestamp"],
                    "reward_points": notification_data["achievement"].get("reward_points", 0)
                }
            }
            
            # 实际发送邮件
            # self._send_email(email_data)
            
            logger.debug(f"Email notification prepared for: {email_data['to']}")
            
        except Exception as e:
            logger.error(f"Failed to prepare email notification: {str(e)}")
    
    def send_badge_grant(self, notification_data: Dict[str, Any]):
        """发送邮件徽章授予通知"""
        try:
            email_data = {
                "to": f"user_{notification_data['user_id']}@example.com",
                "subject": "🏆 恭喜获得新徽章！",
                "template": "badge_granted",
                "data": {
                    "user_name": "用户",
                    "badge_name": notification_data["badge"]["name"],
                    "badge_description": notification_data["badge"]["description"],
                    "grant_time": notification_data["timestamp"],
                    "badge_rarity": notification_data["badge"]["rarity"]
                }
            }
            
            logger.debug(f"Email badge notification prepared for: {email_data['to']}")
            
        except Exception as e:
            logger.error(f"Failed to prepare email badge notification: {str(e)}")
    
    def send_reward_claim(self, notification_data: Dict[str, Any]):
        """发送邮件奖励领取通知"""
        try:
            email_data = {
                "to": f"user_{notification_data['user_id']}@example.com",
                "subject": "🎁 奖励领取成功！",
                "template": "reward_claimed",
                "data": {
                    "user_name": "用户",
                    "reward_name": notification_data["reward"]["name"],
                    "reward_description": notification_data["reward"]["description"],
                    "claim_time": notification_data["timestamp"],
                    "reward_value": notification_data["reward"]["value"]
                }
            }
            
            logger.debug(f"Email reward notification prepared for: {email_data['to']}")
            
        except Exception as e:
            logger.error(f"Failed to prepare email reward notification: {str(e)}")


class SocialShareService:
    """社交分享服务"""
    
    def __init__(self):
        self.share_platforms = []
    
    def register_platform(self, platform):
        """注册分享平台"""
        self.share_platforms.append(platform)
        logger.info(f"Registered share platform: {platform.__class__.__name__}")
    
    def share_achievement(self, notification_data: Dict[str, Any], platforms: List[str] = None):
        """分享成就到社交平台"""
        try:
            achievement = notification_data["achievement"]
            user_achievement = notification_data["user_achievement"]
            
            share_data = {
                "title": f"🎉 我刚刚解锁了成就：{achievement['name']}！",
                "message": f"在CoachAI完成了成就：{achievement['description']}",
                "image_url": achievement.get("icon_url") or achievement.get("banner_url"),
                "link": f"https://coachai.example.com/achievements/{achievement['id']}",
                "hashtags": ["#CoachAI", "#成就解锁", "#健身挑战"],
                "timestamp": notification_data["timestamp"]
            }
            
            # 分享到指定平台或所有平台
            target_platforms = platforms or [p.name for p in self.share_platforms]
            
            for platform in self.share_platforms:
                if platform.name in target_platforms:
                    try:
                        platform.share(share_data)
                        logger.info(f"Shared achievement to {platform.name}")
                    except Exception as e:
                        logger.error(f"Failed to share to {platform.name}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Failed to share achievement: {str(e)}")
    
    def share_badge(self, notification_data: Dict[str, Any], platforms: List[str] = None):
        """分享徽章到社交平台"""
        try:
            badge = notification_data["badge"]
            
            share_data = {
                "title": f"🏆 我刚刚获得了徽章：{badge['name']}！",
                "message": f"在CoachAI获得了{badge['rarity']}稀有度的徽章：{badge['description']}",
                "image_url": badge.get("icon_url") or badge.get("banner_url"),
                "link": f"https://coachai.example.com/badges/{badge['id']}",
                "hashtags": ["#CoachAI", "#徽章收集", "#健身成就"],
                "timestamp": notification_data["timestamp"]
            }
            
            target_platforms = platforms or [p.name for p in self.share_platforms]
            
            for platform in self.share_platforms:
                if platform.name in target_platforms:
                    try:
                        platform.share(share_data)
                        logger.info(f"Shared badge to {platform.name}")
                    except Exception as e:
                        logger.error(f"Failed to share to {platform.name}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Failed to share badge: {str(e)}")


class TwitterSharePlatform:
    """Twitter分享平台"""
    
    def __init__(self):
        self.name = "twitter"
    
    def share(self, share_data: Dict[str, Any]):
        """分享到Twitter"""
        try:
            # 这里应该实现实际的Twitter分享逻辑
            # 例如：使用Twitter API发布推文
            
            tweet_content = f"{share_data['title']}\n\n{share_data['message']}\n\n{' '.join(share_data['hashtags'])}\n\n{share_data['link']}"
            
            # 实际发布推文
            # self._post_tweet(tweet_content, share_data.get('image_url'))
            
            logger.debug(f"Twitter share prepared: {tweet_content[:100]}...")
            
        except Exception as e:
            logger.error(f"Failed to prepare Twitter share: {str(e)}")


class FacebookSharePlatform:
    """Facebook分享平台"""
    
    def __init__(self):
        self.name = "facebook"
    
    def share(self, share_data: Dict[str, Any]):
        """分享到Facebook"""
        try:
            # 这里应该实现实际的Facebook分享逻辑
            
            post_data = {
                "message": f"{share_data['title']}\n\n{share_data['message']}",
                "link": share_data["link"],
                "picture": share_data.get("image_url"),
                "caption": "CoachAI成就分享",
                "description": share_data["message"]
            }
            
            # 实际发布到Facebook
            # self._post_to_facebook(post_data)
            
            logger.debug(f"Facebook share prepared: {post_data['message'][:100]}...")
            
        except Exception as e:
            logger.error(f"Failed to prepare Facebook share: {str(e)}")


class WeChatSharePlatform:
    """微信分享平台"""
    
    def __init__(self):
        self.name = "wechat"
    
    def share(self, share_data: Dict[str, Any]):
        """分享到微信"""
        try:
            # 这里应该实现实际的微信分享逻辑
            
            share_card = {
                "title": share_data["title"],
                "description": share_data["message"],
                "url": share_data["link"],
                "thumbUrl": share_data.get("image_url")
            }
            
            # 实际分享到微信
            # self._share_to_wechat(share_card)
            
            logger.debug(f"WeChat share prepared: {share_card['title']}")
            
        except Exception as e:
            logger.error(f"Failed to prepare WeChat share: {str(e)}")


# 全局通知服务实例
notification_service = AchievementNotificationService()
social_share_service = SocialShareService()

# 注册默认渠道和平台
notification_service.register_channel(InAppNotificationChannel())
notification_service.register_channel(PushNotificationChannel())
notification_service.register_channel(EmailNotificationChannel())

social_share_service.register_platform(TwitterSharePlatform())
social_share_service.register_platform(FacebookSharePlatform())
social_share_service.register_platform(WeChatSharePlatform())
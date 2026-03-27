"""
成就系统API集成测试

测试成就系统的RESTful API接口
"""

import pytest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

from webapp.core.application import make_app
from coding.database.models import (
    User, Achievement, UserAchievement, Badge, Reward
)


class TestAchievementAPI:
    """测试成就API"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        return make_app()
    
    @pytest.fixture
    def test_client(self, app, http_server, http_client):
        """创建测试客户端"""
        return http_client
    
    @pytest.fixture
    def auth_headers(self):
        """创建认证头"""
        return {
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json"
        }
    
    @pytest.fixture
    def mock_current_user(self):
        """模拟当前用户"""
        user = MagicMock(spec=User)
        user.id = "test_user_id"
        user.username = "testuser"
        user.email = "test@example.com"
        user.is_active.return_value = True
        user.is_blocked.return_value = False
        return user
    
    def test_get_achievements(self, test_client, auth_headers, mock_current_user):
        """测试获取成就列表"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            with patch('coding.tornado.modules.achievements.handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟成就数据
                achievement1 = MagicMock(spec=Achievement)
                achievement1.id = "achievement_1"
                achievement1.name = "First Exercise"
                achievement1.description = "Complete your first exercise"
                achievement1.to_dict.return_value = {
                    "id": "achievement_1",
                    "name": "First Exercise",
                    "description": "Complete your first exercise"
                }
                
                achievement2 = MagicMock(spec=Achievement)
                achievement2.id = "achievement_2"
                achievement2.name = "Task Master"
                achievement2.description = "Complete 10 tasks"
                achievement2.to_dict.return_value = {
                    "id": "achievement_2",
                    "name": "Task Master",
                    "description": "Complete 10 tasks"
                }
                
                # 模拟查询
                mock_query = MagicMock()
                mock_query.filter.return_value = mock_query
                mock_query.count.return_value = 2
                mock_query.order_by.return_value = mock_query
                mock_query.offset.return_value = mock_query
                mock_query.limit.return_value = [achievement1, achievement2]
                
                mock_db.query.return_value = mock_query
                
                # 发送请求
                response = test_client.fetch(
                    "/api/v1/achievements",
                    method="GET",
                    headers=auth_headers
                )
                
                assert response.code == 200
                
                data = json.loads(response.body)
                assert data["success"] == True
                assert len(data["data"]["achievements"]) == 2
                assert data["data"]["total"] == 2
    
    def test_create_achievement(self, test_client, auth_headers, mock_current_user):
        """测试创建成就"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            with patch('coding.tornado.modules.achievements.handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟成就创建
                achievement = MagicMock(spec=Achievement)
                achievement.id = "new_achievement_id"
                achievement.name = "New Achievement"
                achievement.description = "New achievement description"
                achievement.to_dict.return_value = {
                    "id": "new_achievement_id",
                    "name": "New Achievement",
                    "description": "New achievement description"
                }
                
                mock_db.add.return_value = None
                mock_db.commit.return_value = None
                mock_db.refresh.return_value = None
                
                # 模拟服务
                with patch('coding.tornado.modules.achievements.handlers.AchievementService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    mock_service.create_achievement.return_value = achievement
                    
                    # 发送请求
                    achievement_data = {
                        "name": "New Achievement",
                        "description": "New achievement description",
                        "trigger_type": "exercise_completed",
                        "target_value": 5
                    }
                    
                    response = test_client.fetch(
                        "/api/v1/achievements",
                        method="POST",
                        headers=auth_headers,
                        body=json.dumps(achievement_data)
                    )
                    
                    assert response.code == 201
                    
                    data = json.loads(response.body)
                    assert data["success"] == True
                    assert data["data"]["achievement"]["name"] == "New Achievement"
    
    def test_get_user_achievements(self, test_client, auth_headers, mock_current_user):
        """测试获取用户成就列表"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            with patch('coding.tornado.modules.achievements.handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟用户成就数据
                user_achievement1 = MagicMock(spec=UserAchievement)
                user_achievement1.id = "ua_1"
                user_achievement1.user_id = "test_user_id"
                user_achievement1.achievement_id = "achievement_1"
                user_achievement1.status = "in_progress"
                user_achievement1.progress = 3
                user_achievement1.target_value = 5
                user_achievement1.to_dict.return_value = {
                    "id": "ua_1",
                    "user_id": "test_user_id",
                    "achievement_id": "achievement_1",
                    "status": "in_progress",
                    "progress": 3,
                    "target_value": 5
                }
                
                achievement1 = MagicMock(spec=Achievement)
                achievement1.id = "achievement_1"
                achievement1.name = "First Steps"
                achievement1.to_dict.return_value = {
                    "id": "achievement_1",
                    "name": "First Steps"
                }
                
                user_achievement1.achievement = achievement1
                
                user_achievement2 = MagicMock(spec=UserAchievement)
                user_achievement2.id = "ua_2"
                user_achievement2.user_id = "test_user_id"
                user_achievement2.achievement_id = "achievement_2"
                user_achievement2.status = "completed"
                user_achievement2.progress = 10
                user_achievement2.target_value = 10
                user_achievement2.to_dict.return_value = {
                    "id": "ua_2",
                    "user_id": "test_user_id",
                    "achievement_id": "achievement_2",
                    "status": "completed",
                    "progress": 10,
                    "target_value": 10
                }
                
                achievement2 = MagicMock(spec=Achievement)
                achievement2.id = "achievement_2"
                achievement2.name = "Task Master"
                achievement2.to_dict.return_value = {
                    "id": "achievement_2",
                    "name": "Task Master"
                }
                
                user_achievement2.achievement = achievement2
                
                # 模拟查询
                mock_query = MagicMock()
                mock_query.filter.return_value = mock_query
                mock_query.count.return_value = 2
                mock_query.order_by.return_value = mock_query
                mock_query.offset.return_value = mock_query
                mock_query.limit.return_value = [user_achievement1, user_achievement2]
                
                mock_db.query.return_value = mock_query
                
                # 发送请求
                response = test_client.fetch(
                    "/api/v1/user-achievements",
                    method="GET",
                    headers=auth_headers
                )
                
                assert response.code == 200
                
                data = json.loads(response.body)
                assert data["success"] == True
                assert len(data["data"]["user_achievements"]) == 2
                assert data["data"]["total"] == 2
    
    def test_update_achievement_progress(self, test_client, auth_headers, mock_current_user):
        """测试更新成就进度"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            with patch('coding.tornado.modules.achievements.handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟服务
                with patch('coding.tornado.modules.achievements.handlers.UserAchievementService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    # 模拟用户成就
                    user_achievement = MagicMock(spec=UserAchievement)
                    user_achievement.id = "ua_1"
                    user_achievement.user_id = "test_user_id"
                    user_achievement.achievement_id = "achievement_1"
                    user_achievement.status = "in_progress"
                    user_achievement.progress = 4
                    user_achievement.target_value = 5
                    user_achievement.to_dict.return_value = {
                        "id": "ua_1",
                        "user_id": "test_user_id",
                        "achievement_id": "achievement_1",
                        "status": "in_progress",
                        "progress": 4,
                        "target_value": 5
                    }
                    
                    achievement = MagicMock(spec=Achievement)
                    achievement.id = "achievement_1"
                    achievement.name = "Almost There"
                    achievement.to_dict.return_value = {
                        "id": "achievement_1",
                        "name": "Almost There"
                    }
                    
                    user_achievement.achievement = achievement
                    
                    mock_service.update_user_achievement_progress.return_value = user_achievement
                    
                    # 发送请求
                    progress_data = {
                        "user_id": "test_user_id",
                        "achievement_id": "achievement_1",
                        "progress_delta": 1,
                        "event_type": "exercise_completed",
                        "event_data": {"exercise_type": "pushup"}
                    }
                    
                    response = test_client.fetch(
                        "/api/v1/achievement-progress",
                        method="POST",
                        headers=auth_headers,
                        body=json.dumps(progress_data)
                    )
                    
                    assert response.code == 200
                    
                    data = json.loads(response.body)
                    assert data["success"] == True
                    assert data["data"]["user_achievement"]["progress"] == 4
    
    def test_get_user_achievement_stats(self, test_client, auth_headers, mock_current_user):
        """测试获取用户成就统计"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            with patch('coding.tornado.modules.achievements.handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟服务
                with patch('coding.tornado.modules.achievements.handlers.UserAchievementService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    # 模拟统计
                    from webapp.modules.achievements.models import AchievementStats
                    stats = AchievementStats(
                        total_achievements=10,
                        unlocked_achievements=3,
                        in_progress_achievements=2,
                        locked_achievements=5,
                        total_points=500,
                        total_badges=2,
                        completion_rate=30.0
                    )
                    
                    mock_service.get_user_achievement_stats.return_value = stats
                    
                    # 发送请求
                    response = test_client.fetch(
                        "/api/v1/achievement-stats",
                        method="GET",
                        headers=auth_headers
                    )
                    
                    assert response.code == 200
                    
                    data = json.loads(response.body)
                    assert data["success"] == True
                    assert data["data"]["stats"]["total_achievements"] == 10
                    assert data["data"]["stats"]["unlocked_achievements"] == 3
                    assert data["data"]["stats"]["completion_rate"] == 30.0
    
    def test_trigger_achievement_event(self, test_client, auth_headers, mock_current_user):
        """测试触发成就事件"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            with patch('coding.tornado.modules.achievements.handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟服务
                with patch('coding.tornado.modules.achievements.handlers.AchievementTriggerService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    # 模拟通知
                    from webapp.modules.achievements.models import AchievementUnlockNotification
                    
                    achievement = MagicMock(spec=Achievement)
                    achievement.id = "achievement_1"
                    achievement.name = "First Exercise"
                    achievement.to_dict.return_value = {
                        "id": "achievement_1",
                        "name": "First Exercise"
                    }
                    
                    user_achievement = MagicMock(spec=UserAchievement)
                    user_achievement.id = "ua_1"
                    user_achievement.to_dict.return_value = {
                        "id": "ua_1"
                    }
                    
                    notification = AchievementUnlockNotification(
                        user_id="test_user_id",
                        achievement=achievement,
                        user_achievement=user_achievement
                    )
                    
                    mock_service.handle_event.return_value = [notification]
                    
                    # 发送请求
                    event_data = {
                        "event_type": "exercise_completed",
                        "user_id": "test_user_id",
                        "event_data": {
                            "exercise_type": "pushup",
                            "count": 10
                        }
                    }
                    
                    response = test_client.fetch(
                        "/api/v1/achievement-trigger",
                        method="POST",
                        headers=auth_headers,
                        body=json.dumps(event_data)
                    )
                    
                    assert response.code == 200
                    
                    data = json.loads(response.body)
                    assert data["success"] == True
                    assert data["data"]["count"] == 1
    
    def test_grant_badge(self, test_client, auth_headers, mock_current_user):
        """测试授予徽章"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            with patch('coding.tornado.modules.achievements.handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟服务
                with patch('coding.tornado.modules.achievements.handlers.BadgeService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    # 模拟用户徽章
                    user_badge = MagicMock(spec=UserBadge)
                    user_badge.id = "ub_1"
                    user_badge.user_id = "test_user_id"
                    user_badge.badge_id = "badge_1"
                    user_badge.granted_at = datetime.now()
                    user_badge.to_dict.return_value = {
                        "id": "ub_1",
                        "user_id": "test_user_id",
                        "badge_id": "badge_1"
                    }
                    
                    badge = MagicMock(spec=Badge)
                    badge.id = "badge_1"
                    badge.name = "First Badge"
                    badge.to_dict.return_value = {
                        "id": "badge_1",
                        "name": "First Badge"
                    }
                    
                    user_badge.badge = badge
                    
                    mock_service.grant_badge_to_user.return_value = user_badge
                    
                    # 发送请求
                    grant_data = {
                        "user_id": "test_user_id",
                        "badge_id": "badge_1",
                        "grant_reason": "For completing first achievement"
                    }
                    
                    response = test_client.fetch(
                        "/api/v1/badge-grant",
                        method="POST",
                        headers=auth_headers,
                        body=json.dumps(grant_data)
                    )
                    
                    assert response.code == 201
                    
                    data = json.loads(response.body)
                    assert data["success"] == True
                    assert data["data"]["user_badge"]["badge"]["name"] == "First Badge"
    
    def test_claim_reward(self, test_client, auth_headers, mock_current_user):
        """测试领取奖励"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            with patch('coding.tornado.modules.achievements.handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟服务
                with patch('coding.tornado.modules.achievements.handlers.RewardService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    # 模拟用户奖励
                    user_reward = MagicMock(spec=UserReward)
                    user_reward.id = "ur_1"
                    user_reward.user_id = "test_user_id"
                    user_reward.reward_id = "reward_1"
                    user_reward.claimed_at = datetime.now()
                    user_reward.reward_value = 100
                    user_reward.to_dict.return_value = {
                        "id": "ur_1",
                        "user_id": "test_user_id",
                        "reward_id": "reward_1",
                        "reward_value": 100
                    }
                    
                    reward = MagicMock(spec=Reward)
                    reward.id = "reward_1"
                    reward.name = "Welcome Points"
                    reward.to_dict.return_value = {
                        "id": "reward_1",
                        "name": "Welcome Points"
                    }
                    
                    user_reward.reward = reward
                    
                    mock_service.claim_reward.return_value = user_reward
                    
                    # 发送请求
                    claim_data = {
                        "user_id": "test_user_id",
                        "reward_id": "reward_1",
                        "claim_reason": "Welcome to the platform"
                    }
                    
                    response = test_client.fetch(
                        "/api/v1/reward-claim",
                        method="POST",
                        headers=auth_headers,
                        body=json.dumps(claim_data)
                    )
                    
                    assert response.code == 201
                    
                    data = json.loads(response.body)
                    assert data["success"] == True
                    assert data["data"]["user_reward"]["reward_value"] == 100
    
    def test_get_user_badges(self, test_client, auth_headers, mock_current_user):
        """测试获取用户徽章列表"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            with patch('coding.tornado.modules.achievements.handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟用户徽章数据
                user_badge1 = MagicMock(spec=UserBadge)
                user_badge1.id = "ub_1"
                user_badge1.user_id = "test_user_id"
                user_badge1.badge_id = "badge_1"
                user_badge1.granted_at = datetime.now()
                user_badge1.is_equipped = True
                user_badge1.to_dict.return_value = {
                    "id": "ub_1",
                    "user_id": "test_user_id",
                    "badge_id": "badge_1",
                    "is_equipped": True
                }
                
                badge1 = MagicMock(spec=Badge)
                badge1.id = "badge_1"
                badge1.name = "First Badge"
                badge1.to_dict.return_value = {
                    "id": "badge_1",
                    "name": "First Badge"
                }
                
                user_badge1.badge = badge1
                
                user_badge2 = MagicMock(spec=UserBadge)
                user_badge2.id = "ub_2"
                user_badge2.user_id = "test_user_id"
                user_badge2.badge_id = "badge_2"
                user_badge2.granted_at = datetime.now()
                user_badge2.is_equipped = False
                user_badge2.to_dict.return_value = {
                    "id": "ub_2",
                    "user_id": "test_user_id",
                    "badge_id": "badge_2",
                    "is_equipped": False
                }
                
                badge2 = MagicMock(spec=Badge)
                badge2.id = "badge_2"
                badge2.name = "Rare Badge"
                badge2.to_dict.return_value = {
                    "id": "badge_2",
                    "name": "Rare Badge"
                }
                
                user_badge2.badge = badge2
                
                # 模拟查询
                mock_query = MagicMock()
                mock_query.filter.return_value = mock_query
                mock_query.options.return_value = mock_query
                mock_query.count.return_value = 2
                mock_query.order_by.return_value = mock_query
                mock_query.offset.return_value = mock_query
                mock_query.limit.return_value = [user_badge1, user_badge2]
                
                mock_db.query.return_value = mock_query
                
                # 发送请求
                response = test_client.fetch(
                    "/api/v1/user-badges",
                    method="GET",
                    headers=auth_headers
                )
                
                assert response.code == 200
                
                data = json.loads(response.body)
                assert data["success"] == True
                assert len(data["data"]["user_badges"]) == 2
                assert data["data"]["total"] == 2
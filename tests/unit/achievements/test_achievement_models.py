"""
成就模型单元测试

测试成就系统相关的数据模型
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock

from coachai_code.database.models import (
    Achievement, AchievementType, AchievementDifficulty, AchievementStatus,
    UserAchievement, UserAchievementStatus,
    Badge, BadgeRarity, BadgeType, BadgeStatus,
    UserBadge,
    Reward, RewardType, RewardStatus,
    UserReward, UserRewardStatus
)


@pytest.fixture(scope="function")
def mock_db_session():
    """创建模拟数据库会话"""
    return MagicMock()


class TestAchievementModel:
    """测试成就模型"""
    
    def test_create_achievement(self):
        """测试创建成就"""
        achievement = Achievement(
            name="First Exercise",
            description="Complete your first exercise",
            achievement_type=AchievementType.EXERCISE,
            difficulty=AchievementDifficulty.EASY,
            trigger_type="exercise_completed",
            trigger_config={"exercise_type": "pushup"},
            target_value=1,
            reward_points=100
        )
        
        # 模拟ID
        achievement.id = "test_achievement_id"
        
        assert achievement.id == "test_achievement_id"
        assert achievement.name == "First Exercise"
        assert achievement.achievement_type == AchievementType.EXERCISE
        assert achievement.difficulty == AchievementDifficulty.EASY
        assert achievement.status == AchievementStatus.ACTIVE
        assert achievement.unlock_count == 0
    
    def test_achievement_to_dict(self):
        """测试成就转换为字典"""
        achievement = Achievement(
            name="Test Achievement",
            description="Test description",
            achievement_type=AchievementType.TASK,
            difficulty=AchievementDifficulty.MEDIUM,
            trigger_type="task_completed",
            trigger_config={"task_type": "daily"},
            target_value=5,
            reward_points=200
        )
        
        # 模拟ID和时间
        achievement.id = "test_achievement_id"
        achievement.created_at = datetime.now()
        achievement.updated_at = datetime.now()
        
        achievement_dict = achievement.to_dict()
        
        assert achievement_dict["name"] == "Test Achievement"
        assert achievement_dict["achievement_type"] == "task"
        assert achievement_dict["difficulty"] == "medium"
        assert achievement_dict["status"] == "active"
        assert achievement_dict["reward_points"] == 200


class TestUserAchievementModel:
    """测试用户成就模型"""
    
    def test_create_user_achievement(self):
        """测试创建用户成就"""
        # 模拟用户ID和成就ID
        user_id = "test_user_id"
        achievement_id = "test_achievement_id"
        
        # 创建用户成就
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id,
            target_value=10,
            status=UserAchievementStatus.LOCKED,
            progress=0
        )
        
        # 模拟ID
        user_achievement.id = "test_user_achievement_id"
        
        assert user_achievement.id == "test_user_achievement_id"
        assert user_achievement.user_id == user_id
        assert user_achievement.achievement_id == achievement_id
        assert user_achievement.status == UserAchievementStatus.LOCKED
        assert user_achievement.progress == 0
        assert user_achievement.progress_percentage == 0
    
    def test_update_progress(self):
        """测试更新进度"""
        # 创建用户成就
        user_achievement = UserAchievement(
            user_id="test_user_id",
            achievement_id="test_achievement_id",
            target_value=10,
            status=UserAchievementStatus.LOCKED,
            progress=0
        )
        
        # 模拟ID
        user_achievement.id = "test_user_achievement_id"
        
        # 更新进度
        user_achievement.update_progress(5)
        
        assert user_achievement.progress == 5
        assert user_achievement.progress_percentage == 50
        assert user_achievement.status == UserAchievementStatus.IN_PROGRESS
        
        # 完成成就
        user_achievement.update_progress(10)
        
        assert user_achievement.progress == 10
        assert user_achievement.progress_percentage == 100
        assert user_achievement.status == UserAchievementStatus.COMPLETED
    
    def test_user_achievement_to_dict(self):
        """测试用户成就转换为字典"""
        # 创建用户成就
        user_achievement = UserAchievement(
            user_id="test_user_id",
            achievement_id="test_achievement_id",
            target_value=5,
            status=UserAchievementStatus.IN_PROGRESS,
            progress=3
        )
        
        # 模拟ID和时间
        user_achievement.id = "test_user_achievement_id"
        user_achievement.created_at = datetime.now()
        user_achievement.updated_at = datetime.now()
        user_achievement.last_updated_at = datetime.now()
        
        # 更新进度
        user_achievement.update_progress(3)
        
        user_achievement_dict = user_achievement.to_dict()
        
        assert user_achievement_dict["user_id"] == "test_user_id"
        assert user_achievement_dict["achievement_id"] == "test_achievement_id"
        assert user_achievement_dict["status"] == "in_progress"
        assert user_achievement_dict["progress"] == 3
        assert user_achievement_dict["progress_percentage"] == 60


class TestBadgeModel:
    """测试徽章模型"""
    
    def test_create_badge(self):
        """测试创建徽章"""
        badge = Badge(
            name="First Badge",
            description="Your first badge",
            icon_url="https://example.com/badge.png",
            badge_type=BadgeType.ACHIEVEMENT,
            rarity=BadgeRarity.COMMON,
            is_auto_grant=True
        )
        
        # 模拟ID
        badge.id = "test_badge_id"
        
        assert badge.id == "test_badge_id"
        assert badge.name == "First Badge"
        assert badge.badge_type == BadgeType.ACHIEVEMENT
        assert badge.rarity == BadgeRarity.COMMON
        assert badge.status == BadgeStatus.ACTIVE
        assert badge.grant_count == 0
    
    def test_badge_to_dict(self):
        """测试徽章转换为字典"""
        badge = Badge(
            name="Rare Badge",
            description="A rare badge",
            icon_url="https://example.com/rare.png",
            badge_type=BadgeType.SPECIAL,
            rarity=BadgeRarity.RARE
        )
        
        # 模拟ID和时间
        badge.id = "test_badge_id"
        badge.created_at = datetime.now()
        badge.updated_at = datetime.now()
        
        badge_dict = badge.to_dict()
        
        assert badge_dict["name"] == "Rare Badge"
        assert badge_dict["badge_type"] == "special"
        assert badge_dict["rarity"] == "rare"
        assert badge_dict["status"] == "active"


class TestUserBadgeModel:
    """测试用户徽章模型"""
    
    def test_create_user_badge(self):
        """测试创建用户徽章"""
        # 模拟用户ID和徽章ID
        user_id = "test_user_id"
        badge_id = "test_badge_id"
        
        # 创建用户徽章
        user_badge = UserBadge(
            user_id=user_id,
            badge_id=badge_id,
            granted_at=datetime.now(),
            is_new=True
        )
        
        # 模拟ID
        user_badge.id = "test_user_badge_id"
        
        assert user_badge.id == "test_user_badge_id"
        assert user_badge.user_id == user_id
        assert user_badge.badge_id == badge_id
        assert user_badge.is_new == True
        assert user_badge.is_equipped == False
    
    def test_user_badge_to_dict(self):
        """测试用户徽章转换为字典"""
        # 创建用户徽章
        user_badge = UserBadge(
            user_id="test_user_id",
            badge_id="test_badge_id",
            granted_at=datetime.now(),
            is_equipped=True
        )
        
        # 模拟ID和时间
        user_badge.id = "test_user_badge_id"
        user_badge.created_at = datetime.now()
        user_badge.updated_at = datetime.now()
        
        user_badge_dict = user_badge.to_dict()
        
        assert user_badge_dict["user_id"] == "test_user_id"
        assert user_badge_dict["badge_id"] == "test_badge_id"
        assert user_badge_dict["is_equipped"] == True
        assert user_badge_dict["is_new"] == True


class TestRewardModel:
    """测试奖励模型"""
    
    def test_create_reward(self):
        """测试创建奖励"""
        reward = Reward(
            name="Welcome Reward",
            description="Welcome to the platform",
            reward_type=RewardType.POINTS,
            reward_config={"points": 100},
            value=100,
            max_claims=1000,
            per_user_limit=1
        )
        
        # 模拟ID
        reward.id = "test_reward_id"
        
        assert reward.id == "test_reward_id"
        assert reward.name == "Welcome Reward"
        assert reward.reward_type == RewardType.POINTS
        assert reward.status == RewardStatus.ACTIVE
        assert reward.claim_count == 0
    
    def test_reward_is_available(self):
        """测试奖励可用性检查"""
        from datetime import datetime, timedelta
        
        # 测试活跃奖励
        reward_active = Reward(
            name="Active Reward",
            description="Active reward",
            reward_type=RewardType.POINTS,
            reward_config={"points": 50},
            status=RewardStatus.ACTIVE
        )
        
        assert reward_active.is_available() == True
        
        # 测试非活跃奖励
        reward_inactive = Reward(
            name="Inactive Reward",
            description="Inactive reward",
            reward_type=RewardType.POINTS,
            reward_config={"points": 50},
            status=RewardStatus.INACTIVE
        )
        
        assert reward_inactive.is_available() == False
        
        # 测试过期奖励
        reward_expired = Reward(
            name="Expired Reward",
            description="Expired reward",
            reward_type=RewardType.POINTS,
            reward_config={"points": 50},
            status=RewardStatus.ACTIVE,
            available_until=datetime.now() - timedelta(days=1)
        )
        
        assert reward_expired.is_available() == False
        
        # 测试未开始奖励
        reward_future = Reward(
            name="Future Reward",
            description="Future reward",
            reward_type=RewardType.POINTS,
            reward_config={"points": 50},
            status=RewardStatus.ACTIVE,
            available_from=datetime.now() + timedelta(days=1)
        )
        
        assert reward_future.is_available() == False


class TestUserRewardModel:
    """测试用户奖励模型"""
    
    def test_create_user_reward(self):
        """测试创建用户奖励"""
        # 模拟用户ID和奖励ID
        user_id = "test_user_id"
        reward_id = "test_reward_id"
        
        # 创建用户奖励
        user_reward = UserReward(
            user_id=user_id,
            reward_id=reward_id,
            claimed_at=datetime.now(),
            reward_data={"points": 100},
            reward_value=100,
            status=UserRewardStatus.CLAIMED
        )
        
        # 模拟ID
        user_reward.id = "test_user_reward_id"
        
        assert user_reward.id == "test_user_reward_id"
        assert user_reward.user_id == user_id
        assert user_reward.reward_id == reward_id
        assert user_reward.status == UserRewardStatus.CLAIMED
        assert user_reward.reward_value == 100
    
    def test_user_reward_is_expired(self):
        """测试用户奖励过期检查"""
        from datetime import datetime, timedelta
        
        # 测试未过期奖励
        user_reward_active = UserReward(
            user_id="test_user_id",
            reward_id="test_reward_id",
            claimed_at=datetime.now(),
            reward_data={"points": 100},
            status=UserRewardStatus.CLAIMED,
            expires_at=datetime.now() + timedelta(days=7)
        )
        
        assert user_reward_active.is_expired() == False
        
        # 测试已过期奖励
        user_reward_expired = UserReward(
            user_id="test_user_id",
            reward_id="test_reward_id",
            claimed_at=datetime.now(),
            reward_data={"points": 100},
            status=UserRewardStatus.CLAIMED,
            expires_at=datetime.now() - timedelta(days=1)
        )
        
        assert user_reward_expired.is_expired() == True
        
        # 测试已标记为过期的奖励
        user_reward_marked_expired = UserReward(
            user_id="test_user_id",
            reward_id="test_reward_id",
            claimed_at=datetime.now(),
            reward_data={"points": 100},
            status=UserRewardStatus.EXPIRED
        )
        
        assert user_reward_marked_expired.is_expired() == True
"""
成就系统模型测试模块，测试成就、用户成就进度、成就分类和奖励等数据模型。
按照豆包AI助手最佳实践：使用Django测试框架进行单元测试。
"""
from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.achievements.models import (
    Achievement,
    AchievementCategory,
    AchievementReward,
    AchievementStatistic,
    UserAchievement,
)
from core.constants import (
    AchievementConditionOperator,
    AchievementDifficulty,
    AchievementRewardType,
    AchievementStatisticType,
    AchievementType,
)


User = get_user_model()


# ==================== 成就分类模型测试 ====================
class AchievementCategoryModelTest(TestCase):
    """
    成就分类模型测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.category_data = {
            "name": "学习成就",
            "description": "与学习相关的成就分类",
            "icon": "book",
            "color": "#3B82F6",
            "order": 1,
            "is_active": True,
        }
    
    def test_create_achievement_category(self) -> None:
        """测试创建成就分类。"""
        category = AchievementCategory.objects.create(**self.category_data)
        
        self.assertEqual(category.name, "学习成就")
        self.assertEqual(category.description, "与学习相关的成就分类")
        self.assertEqual(category.color, "#3B82F6")
        self.assertEqual(category.order, 1)
        self.assertTrue(category.is_active)
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)
    
    def test_achievement_category_str(self) -> None:
        """测试成就分类的字符串表示。"""
        category = AchievementCategory.objects.create(**self.category_data)
        self.assertEqual(str(category), "学习成就")
    
    def test_achievement_category_achievement_count(self) -> None:
        """测试成就分类的成就数量属性。"""
        category = AchievementCategory.objects.create(**self.category_data)
        
        # 初始成就数量为0
        self.assertEqual(category.achievement_count, 0)
        
        # 创建成就后，成就数量增加
        Achievement.objects.create(
            name="测试成就",
            description="测试用成就",
            category=category,
            achievement_type=AchievementType.COUNT.value,
            difficulty=AchievementDifficulty.EASY.value,
            condition_type="task_completed",
            condition_value=Decimal("1.00"),
            condition_operator=AchievementConditionOperator.GTE.value,
        )
        
        # 刷新对象以获取最新数据
        category.refresh_from_db()
        self.assertEqual(category.achievement_count, 1)
    
    def test_achievement_category_inactive(self) -> None:
        """测试停用成就分类。"""
        category = AchievementCategory.objects.create(**self.category_data)
        category.is_active = False
        category.save()
        
        self.assertFalse(category.is_active)


# ==================== 成就模型测试 ====================
class AchievementModelTest(TestCase):
    """
    成就模型测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.category = AchievementCategory.objects.create(
            name="测试分类",
            description="测试用分类",
            color="#000000",
            icon="test",
            order=99,
            is_active=True,
        )
        
        self.achievement_data = {
            "name": "学习达人",
            "description": "完成100次学习任务",
            "category": self.category,
            "achievement_type": AchievementType.COUNT.value,
            "difficulty": AchievementDifficulty.MEDIUM.value,
            "icon": "graduation-cap",
            "badge_image": "/badges/learning_master.png",
            "condition_type": "task_completed",
            "condition_value": Decimal("100.00"),
            "condition_operator": AchievementConditionOperator.GTE.value,
            "time_limit_days": 0,
            "reward_points": 100,
            "reward_badge": "learning_master",
            "reward_message": "恭喜成为学习达人！",
            "display_order": 1,
            "is_secret": False,
            "is_active": True,
        }
    
    def test_create_achievement(self) -> None:
        """测试创建成就。"""
        achievement = Achievement.objects.create(**self.achievement_data)
        
        self.assertEqual(achievement.name, "学习达人")
        self.assertEqual(achievement.achievement_type, AchievementType.COUNT.value)
        self.assertEqual(achievement.difficulty, AchievementDifficulty.MEDIUM.value)
        self.assertEqual(achievement.condition_value, Decimal("100.00"))
        self.assertEqual(achievement.reward_points, 100)
        self.assertTrue(achievement.is_active)
    
    def test_achievement_str(self) -> None:
        """测试成就的字符串表示。"""
        achievement = Achievement.objects.create(**self.achievement_data)
        self.assertEqual(str(achievement), "学习达人 (中等)")
    
    def test_achievement_check_condition(self) -> None:
        """测试成就条件检查。"""
        achievement = Achievement.objects.create(**self.achievement_data)
        
        # 测试大于等于条件
        self.assertFalse(achievement.check_condition(Decimal("50.00")))  # 50 < 100
        self.assertTrue(achievement.check_condition(Decimal("100.00")))  # 100 = 100
        self.assertTrue(achievement.check_condition(Decimal("150.00")))  # 150 > 100
        
        # 测试小于等于条件
        achievement.condition_operator = AchievementConditionOperator.LTE.value
        achievement.save()
        
        self.assertTrue(achievement.check_condition(Decimal("50.00")))  # 50 < 100
        self.assertTrue(achievement.check_condition(Decimal("100.00")))  # 100 = 100
        self.assertFalse(achievement.check_condition(Decimal("150.00")))  # 150 > 100
        
        # 测试等于条件
        achievement.condition_operator = AchievementConditionOperator.EQ.value
        achievement.save()
        
        self.assertFalse(achievement.check_condition(Decimal("50.00")))  # 50 ≠ 100
        self.assertTrue(achievement.check_condition(Decimal("100.00")))  # 100 = 100
        self.assertFalse(achievement.check_condition(Decimal("150.00")))  # 150 ≠ 100
    
    def test_achievement_unlocked_count(self) -> None:
        """测试成就解锁数量属性。"""
        achievement = Achievement.objects.create(**self.achievement_data)
        
        # 初始解锁数量为0
        self.assertEqual(achievement.unlocked_count, 0)
        
        # 创建用户和用户成就记录
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        UserAchievement.objects.create(
            user=user,
            achievement=achievement,
            current_value=Decimal("100.00"),
            is_unlocked=True,
            unlocked_at=timezone.now(),
        )
        
        # 刷新对象以获取最新数据
        achievement.refresh_from_db()
        self.assertEqual(achievement.unlocked_count, 1)
    
    def test_achievement_unlock_rate(self) -> None:
        """测试成就解锁率属性。"""
        achievement = Achievement.objects.create(**self.achievement_data)
        
        # 初始解锁率为0
        self.assertEqual(achievement.unlock_rate, 0.0)
        
        # 创建用户
        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123"
        )
        
        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass123"
        )
        
        # 只有一个用户解锁成就
        UserAchievement.objects.create(
            user=user1,
            achievement=achievement,
            current_value=Decimal("100.00"),
            is_unlocked=True,
            unlocked_at=timezone.now(),
        )
        
        # 刷新对象以获取最新数据
        achievement.refresh_from_db()
        self.assertEqual(achievement.unlock_rate, 50.0)  # 1/2 = 50%
    
    def test_achievement_invalid_condition_value(self) -> None:
        """测试无效的条件值。"""
        invalid_data = self.achievement_data.copy()
        invalid_data["condition_value"] = Decimal("0.00")  # 条件值必须大于0
        
        with self.assertRaises(ValueError):
            Achievement.objects.create(**invalid_data)


# ==================== 用户成就模型测试 ====================
class UserAchievementModelTest(TestCase):
    """
    用户成就模型测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        self.category = AchievementCategory.objects.create(
            name="测试分类",
            description="测试用分类",
            color="#000000",
            icon="test",
            order=99,
            is_active=True,
        )
        
        self.achievement = Achievement.objects.create(
            name="测试成就",
            description="测试用成就",
            category=self.category,
            achievement_type=AchievementType.COUNT.value,
            difficulty=AchievementDifficulty.EASY.value,
            condition_type="task_completed",
            condition_value=Decimal("10.00"),
            condition_operator=AchievementConditionOperator.GTE.value,
            reward_points=50,
            is_active=True,
        )
        
        self.user_achievement_data = {
            "user": self.user,
            "achievement": self.achievement,
            "current_value": Decimal("5.00"),
            "progress_percentage": 50,
            "is_unlocked": False,
            "is_reward_claimed": False,
            "metadata": {"source": "test"},
        }
    
    def test_create_user_achievement(self) -> None:
        """测试创建用户成就。"""
        user_achievement = UserAchievement.objects.create(**self.user_achievement_data)
        
        self.assertEqual(user_achievement.user, self.user)
        self.assertEqual(user_achievement.achievement, self.achievement)
        self.assertEqual(user_achievement.current_value, Decimal("5.00"))
        self.assertEqual(user_achievement.progress_percentage, 50)
        self.assertFalse(user_achievement.is_unlocked)
        self.assertFalse(user_achievement.is_reward_claimed)
        self.assertEqual(user_achievement.metadata, {"source": "test"})
        self.assertIsNotNone(user_achievement.started_at)
        self.assertIsNotNone(user_achievement.last_updated_at)
    
    def test_user_achievement_str(self) -> None:
        """测试用户成就的字符串表示。"""
        user_achievement = UserAchievement.objects.create(**self.user_achievement_data)
        self.assertEqual(str(user_achievement), "testuser - 测试成就 (进行中)")
        
        # 测试已解锁状态
        user_achievement.is_unlocked = True
        user_achievement.save()
        user_achievement.refresh_from_db()
        self.assertEqual(str(user_achievement), "testuser - 测试成就 (已解锁)")
    
    def test_user_achievement_update_progress(self) -> None:
        """测试更新用户成就进度。"""
        user_achievement = UserAchievement.objects.create(**self.user_achievement_data)
        
        # 更新进度，但未达到解锁条件
        was_unlocked = user_achievement.update_progress(Decimal("8.00"), {"updated_by": "test"})
        
        self.assertFalse(was_unlocked)
        self.assertEqual(user_achievement.current_value, Decimal("8.00"))
        self.assertEqual(user_achievement.progress_percentage, 80)  # 8/10 = 80%
        self.assertFalse(user_achievement.is_unlocked)
        self.assertEqual(user_achievement.metadata, {"source": "test", "updated_by": "test"})
        
        # 更新进度，达到解锁条件
        was_unlocked = user_achievement.update_progress(Decimal("10.00"))
        
        self.assertTrue(was_unlocked)
        self.assertEqual(user_achievement.current_value, Decimal("10.00"))
        self.assertEqual(user_achievement.progress_percentage, 100)  # 10/10 = 100%
        self.assertTrue(user_achievement.is_unlocked)
        self.assertIsNotNone(user_achievement.unlocked_at)
    
    def test_user_achievement_claim_reward(self) -> None:
        """测试领取用户成就奖励。"""
        user_achievement = UserAchievement.objects.create(**self.user_achievement_data)
        
        # 先解锁成就
        user_achievement.update_progress(Decimal("10.00"))
        
        # 领取奖励
        success = user_achievement.claim_reward()
        
        self.assertTrue(success)
        self.assertTrue(user_achievement.is_reward_claimed)
        self.assertIsNotNone(user_achievement.reward_claimed_at)
        
        # 再次领取应该失败
        success = user_achievement.claim_reward()
        self.assertFalse(success)
    
    def test_user_achievement_time_to_unlock(self) -> None:
        """测试用户成就解锁时间属性。"""
        user_achievement = UserAchievement.objects.create(**self.user_achievement_data)
        
        # 初始未解锁，返回None
        self.assertIsNone(user_achievement.time_to_unlock)
        
        # 解锁成就
        user_achievement.update_progress(Decimal("10.00"))
        
        # 解锁后应该有解锁时间
        self.assertIsNotNone(user_achievement.time_to_unlock)
        self.assertGreater(user_achievement.time_to_unlock, 0)
    
    def test_user_achievement_days_since_started(self) -> None:
        """测试用户成就开始天数属性。"""
        user_achievement = UserAchievement.objects.create(**self.user_achievement_data)
        
        # 天数应该大于等于0
        self.assertGreaterEqual(user_achievement.days_since_started, 0)
    
    def test_user_achievement_unique_constraint(self) -> None:
        """测试用户成就唯一性约束。"""
        # 创建第一个用户成就记录
        UserAchievement.objects.create(**self.user_achievement_data)
        
        # 尝试创建第二个相同的用户成就记录应该失败
        with self.assertRaises(Exception):
            UserAchievement.objects.create(**self.user_achievement_data)


# ==================== 成就奖励模型测试 ====================
class AchievementRewardModelTest(TestCase):
    """
    成就奖励模型测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.category = AchievementCategory.objects.create(
            name="测试分类",
            description="测试用分类",
            color="#000000",
            icon="test",
            order=99,
            is_active=True,
        )
        
        self.achievement = Achievement.objects.create(
            name="测试成就",
            description="测试用成就",
            category=self.category,
            achievement_type=AchievementType.COUNT.value,
            difficulty=AchievementDifficulty.EASY.value,
            condition_type="task_completed",
            condition_value=Decimal("10.00"),
            condition_operator=AchievementConditionOperator.GTE.value,
            reward_points=50,
            is_active=True,
        )
        
        self.reward_data = {
            "achievement": self.achievement,
            "reward_type": AchievementRewardType.POINTS.value,
            "reward_value": "100",
            "reward_description": "奖励100积分",
            "is_limited": True,
            "limit_count": 100,
            "limit_expires_at": timezone.now() + datetime.timedelta(days=30),
            "claimed_count": 0,
        }
    
    def test_create_achievement_reward(self) -> None:
        """测试创建成就奖励。"""
        reward = AchievementReward.objects.create(**self.reward_data)
        
        self.assertEqual(reward.achievement, self.achievement)
        self.assertEqual(reward.reward_type, AchievementRewardType.POINTS.value)
        self.assertEqual(reward.reward_value, "100")
        self.assertTrue(reward.is_limited)
        self.assertEqual(reward.limit_count, 100)
        self.assertEqual(reward.claimed_count, 0)
    
    def test_achievement_reward_str(self) -> None:
        """测试成就奖励的字符串表示。"""
        reward = AchievementReward.objects.create(**self.reward_data)
        self.assertEqual(str(reward), "测试成就 - points: 100")
    
    def test_achievement_reward_can_claim(self) -> None:
        """测试成就奖励是否可以领取。"""
        reward = AchievementReward.objects.create(**self.reward_data)
        
        # 初始状态应该可以领取
        self.assertTrue(reward.can_claim())
        
        # 设置领取数量达到限制
        reward.claimed_count = 100
        reward.save()
        
        # 达到限制后不能领取
        self.assertFalse(reward.can_claim())
        
        # 重置领取数量，设置过期时间
        reward.claimed_count = 0
        reward.limit_expires_at = timezone.now() - datetime.timedelta(days=1)
        reward.save()
        
        # 过期后不能领取
        self.assertFalse(reward.can_claim())
        
        # 无限制的奖励应该始终可以领取
        reward.is_limited = False
        reward.limit_expires_at = None
        reward.save()
        
        self.assertTrue(reward.can_claim())
    
    def test_achievement_reward_claim(self) -> None:
        """测试领取成就奖励。"""
        reward = AchievementReward.objects.create(**self.reward_data)
        
        # 初始领取数量为0
        self.assertEqual(reward.claimed_count, 0)
        
        # 领取奖励
        success = reward.claim()
        
        self.assertTrue(success)
        self.assertEqual(reward.claimed_count, 1)
        
        # 再次领取
        success = reward.claim()
        
        self.assertTrue(success)
        self.assertEqual(reward.claimed_count, 2)
        
        # 达到限制后领取失败
        reward.claimed_count = 100
        reward.save()
        
        success = reward.claim()
        self.assertFalse(success)
        self.assertEqual(reward.claimed_count, 100)  # 数量不变


# ==================== 成就统计模型测试 ====================
class AchievementStatisticModelTest(TestCase):
    """
    成就统计模型测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.statistic_data = {
            "statistic_type": AchievementStatisticType.DAILY_UNLOCKS.value,
            "statistic_date": timezone.now().date(),
            "data": {
                "daily_unlocks": 50,
                "category_distribution": [
                    {"category": "学习", "count": 30},
                    {"category": "运动", "count": 20},
                ],
            },
            "total_count": 50,
            "average_value": Decimal("50.00"),
            "max_value": Decimal("50.00"),
            "min_value": Decimal("50.00"),
        }
    
    def test_create_achievement_statistic(self) -> None:
        """测试创建成就统计。"""
        statistic = AchievementStatistic.objects.create(**self.statistic_data)
        
        self.assertEqual(statistic.statistic_type, AchievementStatisticType.DAILY_UNLOCKS.value)
        self.assertEqual(statistic.total_count, 50)
        self.assertEqual(statistic.average_value, Decimal("50.00"))
        self.assertEqual(statistic.data["daily_unlocks"], 50)
    
    def test_achievement_statistic_str(self) -> None:
        """测试成就统计的字符串表示。"""
        statistic = AchievementStatistic.objects.create(**self.statistic_data)
        expected_str = f"每日解锁数 - {statistic.statistic_date}"
        self.assertEqual(str(statistic), expected_str)
    
    def test_achievement_statistic_unique_constraint(self) -> None:
        """测试成就统计唯一性约束。"""
        # 创建第一个统计记录
        AchievementStatistic.objects.create(**self.statistic_data)
        
        # 尝试创建第二个相同类型和日期的统计记录应该失败
        with self.assertRaises(Exception):
            AchievementStatistic.objects.create(**self.statistic_data)
        
        # 创建不同日期的统计记录应该成功
        different_date = self.statistic_data.copy()
        different_date["statistic_date"] = timezone.now().date() - datetime.timedelta(days=1)
        AchievementStatistic.objects.create(**different_date)
        
        # 创建不同类型的统计记录应该成功
        different_type = self.statistic_data.copy()
        different_type["statistic_type"] = AchievementStatisticType.CATEGORY_DISTRIBUTION.value
        AchievementStatistic.objects.create(**different_type)


# ==================== 模型关系测试 ====================
class ModelRelationshipTest(TestCase):
    """
    模型关系测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        # 创建用户
        self.user = User.objects.create_user(
            username="relationship_test",
            email="relationship@example.com",
            password="testpass123"
        )
        
        # 创建分类
        self.category = AchievementCategory.objects.create(
            name="关系测试分类",
            description="测试模型关系",
            color="#FF0000",
            icon="test",
            order=999,
            is_active=True,
        )
        
        # 创建成就
        self.achievement = Achievement.objects.create(
            name="关系测试成就",
            description="测试模型关系",
            category=self.category,
            achievement_type=AchievementType.COUNT.value,
            difficulty=AchievementDifficulty.MEDIUM.value,
            condition_type="task_completed",
            condition_value=Decimal("5.00"),
            condition_operator=AchievementConditionOperator.GTE.value,
            reward_points=100,
            is_active=True,
        )
    
    def test_category_achievement_relationship(self) -> None:
        """测试分类和成就的关系。"""
        # 分类应该可以访问其成就
        achievements = self.category.achievements.all()
        self.assertEqual(achievements.count(), 1)
        self.assertEqual(achievements.first(), self.achievement)
        
        # 成就应该可以访问其分类
        self.assertEqual(self.achievement.category, self.category)
    
    def test_achievement_user_achievement_relationship(self) -> None:
        """测试成就和用户成就的关系。"""
        # 创建用户成就
        user_achievement = UserAchievement.objects.create(
            user=self.user,
            achievement=self.achievement,
            current_value=Decimal("3.00"),
        )
        
        # 成就应该可以访问其用户成就
        user_achievements = self.achievement.user_achievements.all()
        self.assertEqual(user_achievements.count(), 1)
        self.assertEqual(user_achievements.first(), user_achievement)
        
        # 用户应该可以访问其用户成就
        user_achievements = self.user.user_achievements.all()
        self.assertEqual(user_achievements.count(), 1)
        self.assertEqual(user_achievements.first(), user_achievement)
    
    def test_achievement_reward_relationship(self) -> None:
        """测试成就和奖励的关系。"""
        # 创建成就奖励
        reward = AchievementReward.objects.create(
            achievement=self.achievement,
            reward_type=AchievementRewardType.BADGE.value,
            reward_value="test_badge",
            reward_description="测试徽章",
        )
        
        # 成就应该可以访问其奖励
        self.assertEqual(self.achievement.reward, reward)
        
        # 奖励应该可以访问其成就
        self.assertEqual(reward.achievement, self.achievement)


if __name__ == "__main__":
    import unittest
    unittest.main()

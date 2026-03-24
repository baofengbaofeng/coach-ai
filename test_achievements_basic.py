#!/usr/bin/env python
"""
测试成就系统基本功能
"""
import os
import sys
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.simple")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model
from apps.achievements.models import (
    Achievement,
    AchievementCategory,
    AchievementReward,
    UserAchievement,
)
from core.constants import (
    AchievementConditionOperator,
    AchievementDifficulty,
    AchievementRewardType,
    AchievementType,
)

User = get_user_model()

print("测试成就系统基本功能...")
print("=" * 50)

# 1. 创建测试用户
try:
    user, created = User.objects.get_or_create(
        username="achievement_test_user",
        defaults={
            "email": "achievement@example.com",
            "password": "test123",
        }
    )
    print(f"✅ 用户: {user.username} (ID: {user.id})")
except Exception as e:
    print(f"❌ 创建用户失败: {e}")
    sys.exit(1)

# 2. 创建成就分类
try:
    category, created = AchievementCategory.objects.get_or_create(
        name="测试成就分类",
        defaults={
            "description": "测试用成就分类",
            "color": "#FF0000",
            "icon": "test",
            "order": 999,
            "is_active": True,
        }
    )
    print(f"✅ 分类: {category.name} (ID: {category.id})")
except Exception as e:
    print(f"❌ 创建分类失败: {e}")
    sys.exit(1)

# 3. 创建成就
try:
    achievement, created = Achievement.objects.get_or_create(
        name="测试成就",
        defaults={
            "description": "完成10次测试任务",
            "category": category,
            "achievement_type": AchievementType.COUNT.value,
            "difficulty": AchievementDifficulty.EASY.value,
            "condition_type": "task_completed",
            "condition_value": Decimal("10.00"),
            "condition_operator": AchievementConditionOperator.GTE.value,
            "reward_points": 100,
            "is_active": True,
        }
    )
    print(f"✅ 成就: {achievement.name} (ID: {achievement.id})")
    print(f"   条件: {achievement.condition_type} {achievement.condition_operator} {achievement.condition_value}")
    print(f"   奖励: {achievement.reward_points}积分")
except Exception as e:
    print(f"❌ 创建成就失败: {e}")
    sys.exit(1)

# 4. 创建成就奖励
try:
    reward, created = AchievementReward.objects.get_or_create(
        achievement=achievement,
        defaults={
            "reward_type": AchievementRewardType.POINTS.value,
            "reward_value": "100",
            "reward_description": "奖励100积分",
            "is_limited": False,
        }
    )
    print(f"✅ 奖励: {reward.reward_type} - {reward.reward_value}")
except Exception as e:
    print(f"❌ 创建奖励失败: {e}")

# 5. 创建用户成就记录
try:
    user_achievement, created = UserAchievement.objects.get_or_create(
        user=user,
        achievement=achievement,
        defaults={
            "current_value": Decimal("5.00"),
            "metadata": {"source": "test"},
        }
    )
    print(f"✅ 用户成就: 进度 {user_achievement.progress_percentage}%")
    print(f"   当前值: {user_achievement.current_value}")
    print(f"   解锁状态: {'已解锁' if user_achievement.is_unlocked else '未解锁'}")
except Exception as e:
    print(f"❌ 创建用户成就失败: {e}")
    sys.exit(1)

# 6. 更新用户成就进度
try:
    print("\n更新用户成就进度...")
    
    # 更新到8，应该还是未解锁
    was_unlocked = user_achievement.update_progress(Decimal("8.00"), {"updated_by": "test"})
    print(f"   更新到8.00: 进度 {user_achievement.progress_percentage}%, 解锁: {was_unlocked}")
    
    # 更新到10，应该解锁
    was_unlocked = user_achievement.update_progress(Decimal("10.00"))
    print(f"   更新到10.00: 进度 {user_achievement.progress_percentage}%, 解锁: {was_unlocked}")
    
    if user_achievement.is_unlocked:
        print(f"   ✅ 成就解锁成功! 解锁时间: {user_achievement.unlocked_at}")
    else:
        print(f"   ❌ 成就未解锁")
        
except Exception as e:
    print(f"❌ 更新进度失败: {e}")

# 7. 领取成就奖励
try:
    if user_achievement.is_unlocked and not user_achievement.is_reward_claimed:
        success = user_achievement.claim_reward()
        if success:
            print(f"✅ 奖励领取成功! 领取时间: {user_achievement.reward_claimed_at}")
        else:
            print(f"❌ 奖励领取失败")
    else:
        print(f"⚠️  无法领取奖励: 解锁状态={user_achievement.is_unlocked}, 已领取={user_achievement.is_reward_claimed}")
except Exception as e:
    print(f"❌ 领取奖励失败: {e}")

# 8. 统计
try:
    total_achievements = Achievement.objects.count()
    total_categories = AchievementCategory.objects.count()
    total_user_achievements = UserAchievement.objects.count()
    
    print(f"\n📊 统计:")
    print(f"   总成就数: {total_achievements}")
    print(f"   总分类数: {total_categories}")
    print(f"   总用户成就记录: {total_user_achievements}")
    
    # 成就解锁率
    if total_achievements > 0:
        unlocked_achievements = UserAchievement.objects.filter(is_unlocked=True).count()
        unlock_rate = (unlocked_achievements / total_user_achievements * 100) if total_user_achievements > 0 else 0
        print(f"   成就解锁率: {unlock_rate:.1f}%")
        
except Exception as e:
    print(f"❌ 统计失败: {e}")

# 9. 清理测试数据
try:
    user_achievement.delete()
    reward.delete()
    achievement.delete()
    category.delete()
    user.delete()
    print("\n🧹 清理测试数据完成")
except Exception as e:
    print(f"⚠️  清理数据失败: {e}")

print("\n" + "=" * 50)
print("成就系统基本功能测试完成!")
print("如果所有步骤都显示✅，说明成就系统基本功能正常。")
#!/usr/bin/env python3
"""
创建成就系统表的脚本

用于初始化成就系统的数据库表
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coachai_code.database.migrations import migration_manager
from coachai_code.database.connection import get_engine


def main():
    """主函数"""
    print("开始创建成就系统表...")
    
    try:
        # 获取数据库引擎
        engine = get_engine()
        
        # 运行成就系统迁移
        migration_manager.run_migration(
            engine,
            "005_create_achievement_tables.py",
            "upgrade"
        )
        
        print("成就系统表创建完成！")
        
        # 创建一些示例数据
        create_sample_data(engine)
        
        print("示例数据创建完成！")
        
    except Exception as e:
        print(f"创建成就系统表时出错: {str(e)}")
        sys.exit(1)


def create_sample_data(engine):
    """创建示例数据"""
    from sqlalchemy.orm import sessionmaker
    from coachai_code.database.models import (
        Achievement, AchievementType, AchievementDifficulty,
        Badge, BadgeType, BadgeRarity,
        Reward, RewardType
    )
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("创建示例成就数据...")
        
        # 创建示例徽章
        badges = [
            Badge(
                name="运动新手",
                description="完成第一次运动",
                icon_url="/badges/beginner.png",
                badge_type=BadgeType.ACHIEVEMENT,
                rarity=BadgeRarity.COMMON,
                grant_condition="完成第一次运动"
            ),
            Badge(
                name="任务达人",
                description="完成10个任务",
                icon_url="/badges/task_master.png",
                badge_type=BadgeType.ACHIEVEMENT,
                rarity=BadgeRarity.UNCOMMON,
                grant_condition="完成10个任务"
            ),
            Badge(
                name="连续打卡王",
                description="连续打卡7天",
                icon_url="/badges/streak_king.png",
                badge_type=BadgeType.MILESTONE,
                rarity=BadgeRarity.RARE,
                grant_condition="连续打卡7天"
            ),
        ]
        
        for badge in badges:
            session.add(badge)
        session.commit()
        
        print(f"创建了 {len(badges)} 个徽章")
        
        # 创建示例成就
        achievements = [
            Achievement(
                name="第一次运动",
                description="完成你的第一次运动",
                icon_url="/achievements/first_exercise.png",
                achievement_type=AchievementType.EXERCISE,
                difficulty=AchievementDifficulty.EASY,
                trigger_type="exercise_completed",
                trigger_config={"min_count": 1},
                target_value=1,
                reward_points=100,
                reward_badge_id=badges[0].id
            ),
            Achievement(
                name="运动爱好者",
                description="完成10次运动",
                icon_url="/achievements/exercise_lover.png",
                achievement_type=AchievementType.EXERCISE,
                difficulty=AchievementDifficulty.MEDIUM,
                trigger_type="exercise_completed",
                trigger_config={"min_count": 10},
                target_value=10,
                reward_points=500
            ),
            Achievement(
                name="任务新手",
                description="完成第一个任务",
                icon_url="/achievements/first_task.png",
                achievement_type=AchievementType.TASK,
                difficulty=AchievementDifficulty.EASY,
                trigger_type="task_completed",
                trigger_config={"min_count": 1},
                target_value=1,
                reward_points=150
            ),
            Achievement(
                name="任务大师",
                description="完成10个任务",
                icon_url="/achievements/task_master.png",
                achievement_type=AchievementType.TASK,
                difficulty=AchievementDifficulty.MEDIUM,
                trigger_type="task_completed",
                trigger_config={"min_count": 10},
                target_value=10,
                reward_points=800,
                reward_badge_id=badges[1].id
            ),
            Achievement(
                name="连续打卡3天",
                description="连续打卡3天",
                icon_url="/achievements/streak_3.png",
                achievement_type=AchievementType.STREAK,
                difficulty=AchievementDifficulty.EASY,
                trigger_type="streak_updated",
                trigger_config={"min_days": 3},
                target_value=3,
                reward_points=200
            ),
            Achievement(
                name="连续打卡7天",
                description="连续打卡7天",
                icon_url="/achievements/streak_7.png",
                achievement_type=AchievementType.STREAK,
                difficulty=AchievementDifficulty.MEDIUM,
                trigger_type="streak_updated",
                trigger_config={"min_days": 7},
                target_value=7,
                reward_points=1000,
                reward_badge_id=badges[2].id
            ),
            Achievement(
                name="运动里程碑",
                description="完成100次运动",
                icon_url="/achievements/milestone_100.png",
                achievement_type=AchievementType.MILESTONE,
                difficulty=AchievementDifficulty.HARD,
                trigger_type="exercise_completed",
                trigger_config={"min_count": 100},
                target_value=100,
                reward_points=5000
            ),
        ]
        
        for achievement in achievements:
            session.add(achievement)
        session.commit()
        
        print(f"创建了 {len(achievements)} 个成就")
        
        # 创建示例奖励
        rewards = [
            Reward(
                name="欢迎积分",
                description="欢迎来到CoachAI，获得初始积分",
                icon_url="/rewards/welcome.png",
                reward_type=RewardType.POINTS,
                reward_config={"points": 1000},
                value=1000,
                grant_condition="新用户注册",
                is_auto_grant=True,
                max_claims=1,
                per_user_limit=1
            ),
            Reward(
                name="运动达人奖励",
                description="完成10次运动获得的奖励",
                icon_url="/rewards/expert.png",
                reward_type=RewardType.POINTS,
                reward_config={"points": 500},
                value=500,
                grant_condition="完成运动爱好者成就",
                require_achievement_id=achievements[1].id,
                is_auto_grant=True,
                max_claims=1,
                per_user_limit=1
            ),
            Reward(
                name="任务完成奖励",
                description="完成10个任务获得的奖励",
                icon_url="/rewards/task_complete.png",
                reward_type=RewardType.POINTS,
                reward_config={"points": 1000},
                value=1000,
                grant_condition="完成任务大师成就",
                require_achievement_id=achievements[3].id,
                is_auto_grant=True,
                max_claims=1,
                per_user_limit=1
            ),
        ]
        
        for reward in rewards:
            session.add(reward)
        session.commit()
        
        print(f"创建了 {len(rewards)} 个奖励")
        
        session.commit()
        
    except Exception as e:
        session.rollback()
        print(f"创建示例数据时出错: {str(e)}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
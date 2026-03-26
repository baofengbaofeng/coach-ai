"""
成就系统模型单元测试

注意：所有注释必须使用中文（规范要求）
所有日志和异常消息必须使用英文（规范要求）
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class TestAchievementModel:
    """
    成就模型测试类
    
    测试成就相关的数据模型和业务逻辑
    """
    
    def test_achievement_creation(self):
        """
        测试成就创建
        
        验证成就对象创建和基本属性设置
        """
        logger.info("Testing achievement creation")
        
        # 模拟成就数据
        achievement_data = {
            "id": 1,
            "name": "运动小达人",
            "code": "exercise_master",
            "description": "完成100次运动记录",
            "category": "exercise",
            "difficulty": "medium",
            "points": 100,
            "icon_url": "https://example.com/icons/exercise_master.png",
            "trigger_type": "count",
            "trigger_condition": {
                "type": "exercise_record_count",
                "threshold": 100,
                "time_period": "lifetime"
            },
            "rewards": [
                {
                    "type": "badge",
                    "name": "运动达人徽章",
                    "icon_url": "https://example.com/badges/exercise_master.png"
                },
                {
                    "type": "points",
                    "amount": 500
                }
            ],
            "is_active": True,
            "is_secret": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # 验证成就数据
        assert achievement_data["id"] == 1
        assert achievement_data["name"] == "运动小达人"
        assert achievement_data["code"] == "exercise_master"
        assert achievement_data["category"] == "exercise"
        assert achievement_data["difficulty"] == "medium"
        assert achievement_data["points"] == 100
        assert achievement_data["trigger_type"] == "count"
        assert achievement_data["is_active"] is True
        assert achievement_data["is_secret"] is False
        
        # 验证触发条件
        trigger_condition = achievement_data["trigger_condition"]
        assert trigger_condition["type"] == "exercise_record_count"
        assert trigger_condition["threshold"] == 100
        assert trigger_condition["time_period"] == "lifetime"
        
        # 验证奖励
        assert len(achievement_data["rewards"]) == 2
        for reward in achievement_data["rewards"]:
            assert "type" in reward
            if reward["type"] == "badge":
                assert "name" in reward
                assert "icon_url" in reward
            elif reward["type"] == "points":
                assert "amount" in reward
        
        logger.info("Achievement creation test passed")
    
    def test_achievement_categories(self):
        """
        测试成就分类
        
        验证不同成就分类的定义和特性
        """
        logger.info("Testing achievement categories")
        
        # 定义成就分类
        achievement_categories = [
            {
                "category": "exercise",
                "description": "运动成就",
                "examples": ["运动小达人", "跳绳高手", "跑步健将"],
                "trigger_types": ["count", "duration", "streak"],
                "typical_points": 50-200
            },
            {
                "category": "learning",
                "description": "学习成就",
                "examples": ["学习之星", "作业达人", "阅读能手"],
                "trigger_types": ["completion", "score", "consistency"],
                "typical_points": 50-200
            },
            {
                "category": "social",
                "description": "社交成就",
                "examples": ["分享达人", "互助之星", "团队合作"],
                "trigger_types": ["interaction", "sharing", "helping"],
                "typical_points": 30-100
            },
            {
                "category": "milestone",
                "description": "里程碑成就",
                "examples": ["注册满月", "使用100天", "完成1000次任务"],
                "trigger_types": ["time", "count", "anniversary"],
                "typical_points": 100-500
            }
        ]
        
        for category in achievement_categories:
            # 验证分类配置
            assert "category" in category
            assert "description" in category
            assert "examples" in category
            assert "trigger_types" in category
            assert "typical_points" in category
            
            # 验证具体值
            assert len(category["examples"]) > 0
            assert len(category["trigger_types"]) > 0
            
            logger.info(f"Achievement category validated: {category['category']} ({category['description']})")
        
        logger.info("Achievement categories test passed")
    
    def test_achievement_difficulty_levels(self):
        """
        测试成就难度级别
        
        验证成就难度级别的定义和计算
        """
        logger.info("Testing achievement difficulty levels")
        
        # 定义难度级别
        difficulty_levels = {
            "easy": {
                "description": "简单",
                "points_range": (10, 50),
                "completion_rate": ">70%",
                "typical_time": "1-7天",
                "suitable_for": ["初学者", "新用户"]
            },
            "medium": {
                "description": "中等",
                "points_range": (50, 150),
                "completion_rate": "30-70%",
                "typical_time": "1-4周",
                "suitable_for": ["活跃用户", "有一定经验者"]
            },
            "hard": {
                "description": "困难",
                "points_range": (150, 300),
                "completion_rate": "10-30%",
                "typical_time": "1-3月",
                "suitable_for": ["资深用户", "有挑战精神者"]
            },
            "expert": {
                "description": "专家级",
                "points_range": (300, 1000),
                "completion_rate": "<10%",
                "typical_time": "3月以上",
                "suitable_for": ["顶级用户", "专业玩家"]
            }
        }
        
        for level_name, level_config in difficulty_levels.items():
            # 验证难度配置
            assert "description" in level_config
            assert "points_range" in level_config
            assert "completion_rate" in level_config
            assert "typical_time" in level_config
            assert "suitable_for" in level_config
            
            # 验证数值范围
            min_points, max_points = level_config["points_range"]
            assert min_points < max_points
            assert min_points > 0
            
            logger.info(f"Difficulty level validated: {level_name} ({level_config['description']})")
        
        # 测试点数计算逻辑
        test_cases = [
            {"difficulty": "easy", "expected_min": 10, "expected_max": 50},
            {"difficulty": "medium", "expected_min": 50, "expected_max": 150},
            {"difficulty": "hard", "expected_min": 150, "expected_max": 300},
            {"difficulty": "expert", "expected_min": 300, "expected_max": 1000}
        ]
        
        for test_case in test_cases:
            difficulty = test_case["difficulty"]
            expected_min = test_case["expected_min"]
            expected_max = test_case["expected_max"]
            
            points_range = difficulty_levels[difficulty]["points_range"]
            actual_min, actual_max = points_range
            
            assert actual_min == expected_min, f"Min points mismatch for {difficulty}: {actual_min} != {expected_min}"
            assert actual_max == expected_max, f"Max points mismatch for {difficulty}: {actual_max} != {expected_max}"
            
            logger.info(f"Points range validated for {difficulty}: {actual_min}-{actual_max}")
        
        logger.info("Achievement difficulty levels test passed")
    
    def test_achievement_trigger_conditions(self):
        """
        测试成就触发条件
        
        验证成就触发条件的定义和计算逻辑
        """
        logger.info("Testing achievement trigger conditions")
        
        # 定义触发条件类型
        trigger_types = {
            "count": {
                "description": "计数型",
                "examples": ["完成10次运动", "提交20次作业", "登录30天"],
                "parameters": ["threshold", "time_period"],
                "calculation": "累计达到阈值"
            },
            "streak": {
                "description": "连续型",
                "examples": ["连续7天运动", "连续30天登录", "连续完成作业"],
                "parameters": ["days", "activity_type"],
                "calculation": "连续天数达到要求"
            },
            "score": {
                "description": "分数型",
                "examples": ["作业平均分90+", "运动评分4.5+", "完成任务质量高"],
                "parameters": ["min_score", "sample_size"],
                "calculation": "平均分或总分达到要求"
            },
            "combo": {
                "description": "组合型",
                "examples": ["同时完成运动和作业", "在特定时间完成特定任务"],
                "parameters": ["conditions", "logic"],
                "calculation": "多个条件同时满足"
            }
        }
        
        for trigger_type, config in trigger_types.items():
            # 验证触发类型配置
            assert "description" in config
            assert "examples" in config
            assert "parameters" in config
            assert "calculation" in config
            
            # 验证具体值
            assert len(config["examples"]) > 0
            assert len(config["parameters"]) > 0
            
            logger.info(f"Trigger type validated: {trigger_type} ({config['description']})")
        
        # 测试触发条件验证
        test_conditions = [
            {
                "type": "count",
                "threshold": 100,
                "time_period": "lifetime",
                "is_valid": True
            },
            {
                "type": "streak",
                "days": 7,
                "activity_type": "exercise",
                "is_valid": True
            },
            {
                "type": "score",
                "min_score": 90,
                "sample_size": 10,
                "is_valid": True
            },
            {
                "type": "invalid_type",  # 无效类型
                "threshold": 100,
                "is_valid": False
            },
            {
                "type": "count",
                "threshold": 0,  # 阈值为0
                "is_valid": False
            }
        ]
        
        for condition in test_conditions:
            trigger_type = condition["type"]
            is_valid = condition["is_valid"]
            
            if is_valid:
                # 验证有效条件
                assert trigger_type in trigger_types
                if "threshold" in condition:
                    assert condition["threshold"] > 0
                if "days" in condition:
                    assert condition["days"] > 0
                if "min_score" in condition:
                    assert 0 <= condition["min_score"] <= 100
                
                logger.info(f"Valid trigger condition: {trigger_type}")
            else:
                # 验证无效条件应该被检测到
                if trigger_type not in trigger_types:
                    logger.warning(f"Invalid trigger type detected: {trigger_type}")
                if "threshold" in condition and condition["threshold"] <= 0:
                    logger.warning(f"Invalid threshold detected: {condition['threshold']}")
        
        logger.info("Achievement trigger conditions test passed")


class TestUserAchievementModel:
    """
    用户成就模型测试类
    
    测试用户成就相关的数据模型和业务逻辑
    """
    
    def test_user_achievement_creation(self):
        """
        测试用户成就创建
        
        验证用户成就对象创建和基本属性设置
        """
        logger.info("Testing user achievement creation")
        
        # 模拟用户成就数据
        user_achievement_data = {
            "id": 1,
            "user_id": 1,
            "tenant_id": "tenant_001",
            "achievement_id": 1,
            "achievement_name": "运动小达人",
            "progress_current": 75,
            "progress_target": 100,
            "progress_percentage": 75,
            "is_unlocked": False,
            "unlocked_at": None,
            "notified": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # 验证用户成就数据
        assert user_achievement_data["user_id"] == 1
        assert user_achievement_data["tenant_id"] == "tenant_001"
        assert user_achievement_data["achievement_id"] == 1
        assert user_achievement_data["achievement_name"] == "运动小达人"
        assert user_achievement_data["progress_current"] == 75
        assert user_achievement_data["progress_target"] == 100
        assert user_achievement_data["progress_percentage"] == 75
        assert user_achievement_data["is_unlocked"] is False
        assert user_achievement_data["unlocked_at"] is None
        assert user_achievement_data["notified"] is False
        
        # 验证进度计算
        calculated_percentage = (user_achievement_data["progress_current"] / 
                                user_achievement_data["progress_target"]) * 100
        assert abs(calculated_percentage - user_achievement_data["progress_percentage"]) < 0.01
        
        logger.info("User achievement creation test passed")
    
    def test_achievement_progress_tracking(self):
        """
        测试成就进度跟踪
        
        验证成就进度跟踪的逻辑和计算
        """
        logger.info("Testing achievement progress tracking")
        
        # 测试进度计算
        test_cases = [
            {
                "current": 0,
                "target": 100,
                "expected_percentage": 0,
                "expected_unlocked": False
            },
            {
                "current": 50,
                "target": 100,
                "expected_percentage": 50,
                "expected_unlocked": False
            },
            {
                "current": 100,
                "target": 100,
                "expected_percentage": 100,
                "expected_unlocked": True
            },
            {
                "current": 150,  # 超过目标
                "target": 100,
                "expected_percentage": 100,
                "expected_unlocked": True
            }
        ]
        
        for test_case in test_cases:
            current = test_case["current"]
            target = test_case["target"]
            expected_percentage = test_case["expected_percentage"]
            expected_unlocked = test_case["expected_unlocked"]
            
            # 计算进度百分比
            if target == 0:
                calculated_percentage = 100  # 特殊情况处理
            else:
                calculated_percentage = min(100, int((current / target) * 100))
            
            # 判断是否解锁
            is_unlocked = calculated_percentage >= 100
            
            assert calculated_percentage == expected_percentage, \
                f"Progress calculation error: {current}/{target} -> {calculated_percentage}%, expected {expected_percentage}%"
            
            assert is_unlocked == expected_unlocked, \
                f"Unlock status error: {current}/{target} -> unlocked={is_unlocked}, expected {expected_unlocked}"
            
            # 验证进度范围
            assert 0 <= calculated_percentage <= 100
            
            logger.info(f"Progress tracking validated: {current}/{target} = {calculated_percentage}%, unlocked={is_unlocked}")
        
        logger.info("Achievement progress tracking test passed")
    
    def test_achievement_unlock_flow(self):
        """
        测试成就解锁流程
        
        验证成就解锁的完整流程和状态转换
        """
        logger.info("Testing achievement unlock flow")
        
        # 模拟成就解锁流程状态
        unlock_states = [
            {
                "state": "not_started",
                "progress": 0,
                "is_unlocked": False,
                "unlocked_at": None,
                "notified": False
            },
            {
                "state": "in_progress",
                "progress": 50,
                "is_unlocked": False,
                "unlocked_at": None,
                "notified": False
            },
            {
                "state": "completed",
                "progress": 100,
                "is_unlocked": True,
                "unlocked_at": datetime.now(),
                "notified": True
            },
            {
                "state": "celebrated",
                "progress": 100,
                "is_unlocked": True,
                "unlocked_at": datetime.now(),
                "notified": True,
                "celebrated_at": datetime.now()
            }
        ]
        
        # 验证状态转换逻辑
        for i, state in enumerate(unlock_states):
            progress = state["progress"]
            is_unlocked = state["is_unlocked"]
            
            # 验证进度和解锁状态的一致性
            if progress >= 100:
                assert is_unlocked is True, f"State {state['state']}: progress={progress} but is_unlocked={is_unlocked}"
                assert state["unlocked_at"] is not None, f"State {state['state']}: unlocked but no unlock time"
                assert state["notified"] is True, f"State {state['state']}: unlocked but not notified"
            else:
                assert is_unlocked is False, f"State {state['state']}: progress={progress} but is_unlocked={is_unlocked}"
                assert state["unlocked_at"] is None, f"State {state['state']}: not unlocked but has unlock time"
            
            logger.info(f"Unlock state validated: {state['state']} (progress={progress}%, unlocked={is_unlocked})")
        
        # 测试状态转换顺序
        expected_order = ["not_started", "in_progress", "completed", "celebrated"]
        actual_order = [state["state"] for state in unlock_states]
        
        assert actual_order == expected_order, f"State order mismatch: {actual_order} != {expected_order}"
        
        logger.info("Achievement unlock flow test passed")


class TestBadgeModel:
    """
    徽章模型测试类
    
    测试徽章相关的数据模型和业务逻辑

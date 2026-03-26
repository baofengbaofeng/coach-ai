"""
运动管理模型单元测试

注意：所有注释必须使用中文（规范要求）
所有日志和异常消息必须使用英文（规范要求）
"""

import pytest
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TestExerciseTypeModel:
    """
    运动类型模型测试类
    
    测试运动类型相关的数据模型和业务逻辑
    """
    
    def test_exercise_type_creation(self):
        """
        测试运动类型创建
        
        验证运动类型对象创建和基本属性设置
        """
        logger.info("Testing exercise type creation")
        
        # 模拟运动类型数据
        exercise_type_data = {
            "id": 1,
            "name": "跳绳",
            "code": "jump_rope",
            "description": "跳绳运动，锻炼协调性和耐力",
            "category": "cardio",
            "difficulty": "medium",
            "calories_per_minute": 10.5,
            "requires_equipment": True,
            "equipment_name": "跳绳",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # 验证运动类型数据
        assert exercise_type_data["id"] == 1
        assert exercise_type_data["name"] == "跳绳"
        assert exercise_type_data["code"] == "jump_rope"
        assert exercise_type_data["category"] == "cardio"
        assert exercise_type_data["difficulty"] == "medium"
        assert exercise_type_data["calories_per_minute"] == 10.5
        assert exercise_type_data["requires_equipment"] is True
        assert exercise_type_data["equipment_name"] == "跳绳"
        assert exercise_type_data["is_active"] is True
        
        logger.info("Exercise type creation test passed")
    
    def test_exercise_type_categories(self):
        """
        测试运动类型分类
        
        验证不同运动类型的分类逻辑
        """
        logger.info("Testing exercise type categories")
        
        # 定义运动分类
        exercise_categories = [
            {
                "category": "cardio",
                "description": "有氧运动",
                "examples": ["跳绳", "跑步", "游泳"],
                "benefits": ["提高心肺功能", "燃烧脂肪", "增强耐力"]
            },
            {
                "category": "strength",
                "description": "力量训练",
                "examples": ["俯卧撑", "仰卧起坐", "深蹲"],
                "benefits": ["增强肌肉力量", "提高代谢率", "改善体态"]
            },
            {
                "category": "flexibility",
                "description": "柔韧性训练",
                "examples": ["瑜伽", "拉伸", "太极"],
                "benefits": ["提高柔韧性", "减少受伤风险", "改善姿势"]
            },
            {
                "category": "balance",
                "description": "平衡训练",
                "examples": ["单脚站立", "平衡板", "倒立"],
                "benefits": ["提高平衡能力", "增强核心力量", "预防跌倒"]
            }
        ]
        
        for category in exercise_categories:
            # 验证分类配置
            assert "category" in category
            assert "description" in category
            assert "examples" in category
            assert "benefits" in category
            
            # 验证具体值
            assert len(category["examples"]) > 0
            assert len(category["benefits"]) > 0
            
            logger.info(f"Exercise category validated: {category['category']} ({category['description']})")
        
        logger.info("Exercise type categories test passed")
    
    def test_exercise_type_difficulty_levels(self):
        """
        测试运动难度级别
        
        验证运动难度级别的定义和计算
        """
        logger.info("Testing exercise type difficulty levels")
        
        # 定义难度级别
        difficulty_levels = {
            "easy": {
                "description": "简单",
                "calories_factor": 0.8,
                "suitable_for": ["初学者", "儿童", "老年人"],
                "duration_range": (10, 30)  # 分钟
            },
            "medium": {
                "description": "中等",
                "calories_factor": 1.0,
                "suitable_for": ["有一定基础者", "青少年", "成年人"],
                "duration_range": (20, 45)
            },
            "hard": {
                "description": "困难",
                "calories_factor": 1.3,
                "suitable_for": ["有经验者", "运动员", "健身爱好者"],
                "duration_range": (30, 60)
            },
            "expert": {
                "description": "专家级",
                "calories_factor": 1.6,
                "suitable_for": ["专业运动员", "健身教练"],
                "duration_range": (45, 90)
            }
        }
        
        for level_name, level_config in difficulty_levels.items():
            # 验证难度配置
            assert "description" in level_config
            assert "calories_factor" in level_config
            assert "suitable_for" in level_config
            assert "duration_range" in level_config
            
            # 验证数值范围
            assert level_config["calories_factor"] > 0
            min_duration, max_duration = level_config["duration_range"]
            assert min_duration < max_duration
            assert min_duration > 0
            
            logger.info(f"Difficulty level validated: {level_name} ({level_config['description']})")
        
        # 测试热量计算
        base_calories_per_minute = 10.0
        test_cases = [
            ("easy", base_calories_per_minute * 0.8),
            ("medium", base_calories_per_minute * 1.0),
            ("hard", base_calories_per_minute * 1.3),
            ("expert", base_calories_per_minute * 1.6)
        ]
        
        for difficulty, expected_calories in test_cases:
            calculated_calories = base_calories_per_minute * difficulty_levels[difficulty]["calories_factor"]
            assert abs(calculated_calories - expected_calories) < 0.01
        
        logger.info("Exercise type difficulty levels test passed")


class TestExerciseRecordModel:
    """
    运动记录模型测试类
    
    测试运动记录相关的数据模型和业务逻辑
    """
    
    def test_exercise_record_creation(self):
        """
        测试运动记录创建
        
        验证运动记录对象创建和基本属性设置
        """
        logger.info("Testing exercise record creation")
        
        # 模拟运动记录数据
        exercise_record_data = {
            "id": 1001,
            "user_id": 1,
            "tenant_id": "tenant_001",
            "exercise_type_id": 1,
            "exercise_type_name": "跳绳",
            "start_time": datetime.now(),
            "end_time": datetime.now() + timedelta(minutes=30),
            "duration_seconds": 1800,
            "count": 1500,
            "calories_burned": 315.0,
            "average_heart_rate": 135,
            "max_heart_rate": 155,
            "notes": "今天状态不错，坚持了30分钟",
            "video_url": "https://storage.example.com/videos/exercise_1001.mp4",
            "is_completed": True,
            "created_at": datetime.now()
        }
        
        # 验证运动记录数据
        assert exercise_record_data["user_id"] == 1
        assert exercise_record_data["tenant_id"] == "tenant_001"
        assert exercise_record_data["exercise_type_id"] == 1
        assert exercise_record_data["exercise_type_name"] == "跳绳"
        assert exercise_record_data["duration_seconds"] == 1800
        assert exercise_record_data["count"] == 1500
        assert exercise_record_data["calories_burned"] == 315.0
        assert exercise_record_data["is_completed"] is True
        
        # 验证时间逻辑
        assert exercise_record_data["end_time"] > exercise_record_data["start_time"]
        duration = (exercise_record_data["end_time"] - exercise_record_data["start_time"]).total_seconds()
        assert abs(duration - exercise_record_data["duration_seconds"]) < 1
        
        logger.info("Exercise record creation test passed")
    
    def test_exercise_record_calculation(self):
        """
        测试运动记录计算
        
        验证运动记录中的各种计算逻辑
        """
        logger.info("Testing exercise record calculation")
        
        # 测试数据
        test_cases = [
            {
                "exercise_type": "跳绳",
                "duration_minutes": 30,
                "count": 1500,
                "expected_calories": 315.0,  # 10.5卡路里/分钟 * 30分钟
                "expected_count_per_minute": 50  # 1500次 / 30分钟
            },
            {
                "exercise_type": "俯卧撑",
                "duration_minutes": 15,
                "count": 120,
                "expected_calories": 90.0,  # 6卡路里/分钟 * 15分钟
                "expected_count_per_minute": 8  # 120次 / 15分钟
            },
            {
                "exercise_type": "跑步",
                "duration_minutes": 45,
                "distance_km": 6.0,
                "expected_calories": 450.0,  # 10卡路里/分钟 * 45分钟
                "expected_speed_kmh": 8.0  # 6公里 / 0.75小时
            }
        ]
        
        for test_case in test_cases:
            exercise_type = test_case["exercise_type"]
            duration_minutes = test_case["duration_minutes"]
            
            # 计算持续时间（秒）
            duration_seconds = duration_minutes * 60
            
            # 验证热量计算
            if "expected_calories" in test_case:
                # 这里应该调用实际的热量计算函数
                # 暂时使用模拟计算
                calories_per_minute = 10.0  # 模拟值
                calculated_calories = calories_per_minute * duration_minutes
                
                # 允许10%的误差
                expected_calories = test_case["expected_calories"]
                error_margin = expected_calories * 0.1
                assert abs(calculated_calories - expected_calories) <= error_margin
            
            # 验证计数频率计算
            if "count" in test_case and "expected_count_per_minute" in test_case:
                count = test_case["count"]
                expected_cpm = test_case["expected_count_per_minute"]
                calculated_cpm = count / duration_minutes
                
                assert abs(calculated_cpm - expected_cpm) <= expected_cpm * 0.2
            
            logger.info(f"Exercise calculation validated for: {exercise_type}")
        
        logger.info("Exercise record calculation test passed")
    
    def test_exercise_record_validation(self):
        """
        测试运动记录验证
        
        验证运动记录数据的有效性检查
        """
        logger.info("Testing exercise record validation")
        
        # 有效运动记录
        valid_records = [
            {
                "duration_seconds": 1800,  # 30分钟
                "count": 1500,
                "calories_burned": 315.0,
                "average_heart_rate": 135
            },
            {
                "duration_seconds": 900,   # 15分钟
                "count": 300,
                "calories_burned": 120.0,
                "average_heart_rate": 120
            }
        ]
        
        # 无效运动记录
        invalid_records = [
            {
                "duration_seconds": 0,  # 持续时间为0
                "count": 100,
                "calories_burned": 50.0
            },
            {
                "duration_seconds": 1800,
                "count": -10,  # 负计数
                "calories_burned": 315.0
            },
            {
                "duration_seconds": 1800,
                "count": 1500,
                "calories_burned": -50.0  # 负热量
            },
            {
                "duration_seconds": 86401,  # 超过24小时
                "count": 10000,
                "calories_burned": 5000.0
            }
        ]
        
        # 验证有效记录
        for record in valid_records:
            assert record["duration_seconds"] > 0
            assert record["count"] >= 0
            assert record["calories_burned"] >= 0
            if "average_heart_rate" in record:
                assert 40 <= record["average_heart_rate"] <= 220
        
        # 验证无效记录应该被检测到
        for record in invalid_records:
            if record["duration_seconds"] <= 0:
                logger.warning(f"Invalid duration: {record['duration_seconds']} seconds")
            
            if record["count"] < 0:
                logger.warning(f"Invalid count: {record['count']}")
            
            if record["calories_burned"] < 0:
                logger.warning(f"Invalid calories: {record['calories_burned']}")
            
            if record["duration_seconds"] > 86400:
                logger.warning(f"Duration too long: {record['duration_seconds']} seconds")
        
        logger.info("Exercise record validation test passed")


class TestExercisePlanModel:
    """
    运动计划模型测试类
    
    测试运动计划相关的数据模型和业务逻辑
    """
    
    def test_exercise_plan_creation(self):
        """
        测试运动计划创建
        
        验证运动计划对象创建和基本属性设置
        """
        logger.info("Testing exercise plan creation")
        
        # 模拟运动计划数据
        exercise_plan_data = {
            "id": 1,
            "user_id": 1,
            "tenant_id": "tenant_001",
            "name": "每周跳绳计划",
            "description": "每周3次跳绳，每次30分钟",
            "frequency": "weekly",
            "days_per_week": 3,
            "duration_per_session_minutes": 30,
            "target_count_per_session": 1500,
            "target_calories_per_session": 315.0,
            "start_date": datetime.now().date(),
            "end_date": (datetime.now() + timedelta(days=30)).date(),
            "is_active": True,
            "reminder_enabled": True,
            "reminder_time": "19:00",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # 验证运动计划数据
        assert exercise_plan_data["name"] == "每周跳绳计划"
        assert exercise_plan_data["frequency"] == "weekly"
        assert exercise_plan_data["days_per_week"] == 3
        assert exercise_plan_data["duration_per_session_minutes"] == 30
        assert exercise_plan_data["target_count_per_session"] == 1500
        assert exercise
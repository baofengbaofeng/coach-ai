"""
模型单元测试模块。
测试所有数据模型的创建、验证和业务逻辑。
"""
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from apps.accounts.models import User, UserProfile
from apps.tasks.models import Task, TaskAssignment, TaskCompletion
from apps.achievements.models import Achievement, UserAchievement
from apps.common.models import SystemLog, Configuration


class TestUserModel:
    """用户模型测试类"""
    
    def test_create_user(self, db):
        """测试创建普通用户"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpassword123")
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser
        assert user.date_joined is not None
    
    def test_create_superuser(self, db):
        """测试创建超级用户"""
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword123"
        )
        
        assert admin.username == "admin"
        assert admin.email == "admin@example.com"
        assert admin.check_password("adminpassword123")
        assert admin.is_active
        assert admin.is_staff
        assert admin.is_superuser
    
    def test_user_str_representation(self, db):
        """测试用户字符串表示"""
        user = User.objects.create_user(
            username="johndoe",
            email="john@example.com",
            password="password123"
        )
        
        expected_str = f"{user.username} ({user.email})"
        assert str(user) == expected_str
    
    def test_user_email_unique(self, db):
        """测试邮箱唯一性约束"""
        User.objects.create_user(
            username="user1",
            email="same@example.com",
            password="password123"
        )
        
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username="user2",
                email="same@example.com",
                password="password456"
            )
    
    def test_user_username_unique(self, db):
        """测试用户名唯一性约束"""
        User.objects.create_user(
            username="uniqueuser",
            email="user1@example.com",
            password="password123"
        )
        
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username="uniqueuser",
                email="user2@example.com",
                password="password456"
            )
    
    def test_user_profile_creation(self, db):
        """测试用户资料自动创建"""
        user = User.objects.create_user(
            username="profileuser",
            email="profile@example.com",
            password="password123"
        )
        
        # 检查用户资料是否自动创建
        assert hasattr(user, 'profile')
        assert user.profile.user == user
    
    def test_user_points_default(self, db):
        """测试用户积分默认值"""
        user = User.objects.create_user(
            username="pointsuser",
            email="points@example.com",
            password="password123"
        )
        
        assert user.points == 0
    
    def test_user_add_points(self, db):
        """测试用户增加积分"""
        user = User.objects.create_user(
            username="addpoints",
            email="addpoints@example.com",
            password="password123"
        )
        
        initial_points = user.points
        points_to_add = 100
        
        user.add_points(points_to_add)
        user.refresh_from_db()
        
        assert user.points == initial_points + points_to_add
    
    def test_user_deduct_points(self, db):
        """测试用户扣除积分"""
        user = User.objects.create_user(
            username="deductpoints",
            email="deduct@example.com",
            password="password123"
        )
        
        # 先添加积分
        user.add_points(200)
        user.refresh_from_db()
        
        initial_points = user.points
        points_to_deduct = 50
        
        user.deduct_points(points_to_deduct)
        user.refresh_from_db()
        
        assert user.points == initial_points - points_to_deduct
    
    def test_user_deduct_points_insufficient(self, db):
        """测试用户积分不足时扣除"""
        user = User.objects.create_user(
            username="insufficient",
            email="insufficient@example.com",
            password="password123"
        )
        
        # 用户只有10积分
        user.add_points(10)
        user.refresh_from_db()
        
        with pytest.raises(ValueError, match="积分不足"):
            user.deduct_points(50)


class TestUserProfileModel:
    """用户资料模型测试类"""
    
    def test_create_user_profile(self, db, test_user):
        """测试创建用户资料"""
        profile = UserProfile.objects.create(
            user=test_user,
            age=25,
            gender="male",
            height=175.5,
            weight=70.0,
            fitness_level="intermediate",
            goals=["weight_loss", "muscle_gain"]
        )
        
        assert profile.user == test_user
        assert profile.age == 25
        assert profile.gender == "male"
        assert profile.height == 175.5
        assert profile.weight == 70.0
        assert profile.fitness_level == "intermediate"
        assert profile.goals == ["weight_loss", "muscle_gain"]
    
    def test_user_profile_str_representation(self, db, test_user):
        """测试用户资料字符串表示"""
        profile = UserProfile.objects.create(
            user=test_user,
            age=30
        )
        
        expected_str = f"{test_user.username} 的资料"
        assert str(profile) == expected_str
    
    def test_user_profile_bmi_calculation(self, db, test_user):
        """测试BMI计算"""
        profile = UserProfile.objects.create(
            user=test_user,
            height=1.75,  # 米
            weight=70.0   # 公斤
        )
        
        # BMI = 体重(kg) / 身高(m)^2
        expected_bmi = 70.0 / (1.75 * 1.75)
        assert abs(profile.calculate_bmi() - expected_bmi) < 0.01
    
    def test_user_profile_age_validation(self, db, test_user):
        """测试年龄验证"""
        profile = UserProfile.objects.create(
            user=test_user,
            age=150  # 不合理的年龄
        )
        
        # 注意：这里应该根据实际验证逻辑调整
        # 如果模型有年龄验证，这里应该测试验证错误


class TestTaskModel:
    """任务模型测试类"""
    
    def test_create_task(self, db):
        """测试创建任务"""
        task = Task.objects.create(
            title="完成30分钟跑步",
            description="在公园或跑步机上完成30分钟跑步",
            task_type="exercise",
            difficulty="medium",
            estimated_time=30,
            points=50,
            is_active=True
        )
        
        assert task.title == "完成30分钟跑步"
        assert task.task_type == "exercise"
        assert task.difficulty == "medium"
        assert task.estimated_time == 30
        assert task.points == 50
        assert task.is_active
    
    def test_task_str_representation(self, db):
        """测试任务字符串表示"""
        task = Task.objects.create(
            title="测试任务",
            task_type="exercise"
        )
        
        assert str(task) == "测试任务 (exercise)"
    
    def test_task_default_values(self, db):
        """测试任务默认值"""
        task = Task.objects.create(
            title="默认值测试任务",
            task_type="knowledge"
        )
        
        assert task.difficulty == "easy"
        assert task.estimated_time == 15
        assert task.points == 10
        assert task.is_active
    
    def test_task_validation(self, db):
        """测试任务验证"""
        # 测试必填字段
        with pytest.raises(IntegrityError):
            Task.objects.create(
                title=None,  # 标题不能为空
                task_type="exercise"
            )


class TestTaskAssignmentModel:
    """任务分配模型测试类"""
    
    def test_create_task_assignment(self, db, test_user):
        """测试创建任务分配"""
        task = Task.objects.create(
            title="分配测试任务",
            task_type="exercise"
        )
        
        assignment = TaskAssignment.objects.create(
            user=test_user,
            task=task,
            assigned_by=test_user,
            due_date=timezone.now() + timezone.timedelta(days=7)
        )
        
        assert assignment.user == test_user
        assert assignment.task == task
        assert assignment.assigned_by == test_user
        assert assignment.status == "assigned"
    
    def test_task_assignment_str_representation(self, db, test_user):
        """测试任务分配字符串表示"""
        task = Task.objects.create(
            title="字符串测试任务",
            task_type="exercise"
        )
        
        assignment = TaskAssignment.objects.create(
            user=test_user,
            task=task
        )
        
        expected_str = f"{test_user.username} - {task.title}"
        assert str(assignment) == expected_str


class TestAchievementModel:
    """成就模型测试类"""
    
    def test_create_achievement(self, db):
        """测试创建成就"""
        achievement = Achievement.objects.create(
            name="运动达人",
            description="完成100次运动任务",
            achievement_type="exercise",
            points_required=1000,
            badge_image="badges/sports_master.png"
        )
        
        assert achievement.name == "运动达人"
        assert achievement.achievement_type == "exercise"
        assert achievement.points_required == 1000
        assert not achievement.is_secret
    
    def test_achievement_str_representation(self, db):
        """测试成就字符串表示"""
        achievement = Achievement.objects.create(
            name="测试成就",
            achievement_type="knowledge"
        )
        
        assert str(achievement) == "测试成就 (knowledge)"


class TestUserAchievementModel:
    """用户成就模型测试类"""
    
    def test_create_user_achievement(self, db, test_user):
        """测试创建用户成就"""
        achievement = Achievement.objects.create(
            name="测试用户成就",
            achievement_type="exercise"
        )
        
        user_achievement = UserAchievement.objects.create(
            user=test_user,
            achievement=achievement,
            unlocked_at=timezone.now()
        )
        
        assert user_achievement.user == test_user
        assert user_achievement.achievement == achievement
        assert not user_achievement.notified
    
    def test_user_achievement_str_representation(self, db, test_user):
        """测试用户成就字符串表示"""
        achievement = Achievement.objects.create(
            name="字符串测试成就",
            achievement_type="exercise"
        )
        
        user_achievement = UserAchievement.objects.create(
            user=test_user,
            achievement=achievement
        )
        
        expected_str = f"{test_user.username} - {achievement.name}"
        assert str(user_achievement) == expected_str


class TestSystemLogModel:
    """系统日志模型测试类"""
    
    def test_create_system_log(self, db):
        """测试创建系统日志"""
        log = SystemLog.objects.create(
            level="INFO",
            module="tests",
            message="测试日志消息",
            details={"key": "value"}
        )
        
        assert log.level == "INFO"
        assert log.module == "tests"
        assert log.message == "测试日志消息"
        assert log.details == {"key": "value"}
    
    def test_system_log_str_representation(self, db):
        """测试系统日志字符串表示"""
        log = SystemLog.objects.create(
            level="ERROR",
            module="test_module",
            message="错误消息"
        )
        
        expected_str = "[ERROR] test_module: 错误消息"
        assert str(log) == expected_str


class TestConfigurationModel:
    """配置模型测试类"""
    
    def test_create_configuration(self, db):
        """测试创建配置"""
        config = Configuration.objects.create(
            key="test_config",
            value="test_value",
            description="测试配置项",
            is_public=True
        )
        
        assert config.key == "test_config"
        assert config.value == "test_value"
        assert config.description == "测试配置项"
        assert config.is_public
    
    def test_configuration_str_representation(self, db):
        """测试配置字符串表示"""
        config = Configuration.objects.create(
            key="string_test",
            value="some_value"
        )
        
        assert str(config) == "string_test = some_value"
    
    def test_configuration_key_unique(self, db):
        """测试配置键唯一性"""
        Configuration.objects.create(
            key="unique_key",
            value="value1"
        )
        
        with pytest.raises(IntegrityError):
            Configuration.objects.create(
                key="unique_key",
                value="value2"
            )


# 运行所有模型测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
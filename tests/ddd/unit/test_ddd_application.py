"""
DDD架构应用层单元测试

注意：所有注释必须使用中文（规范要求）
所有日志和异常消息必须使用英文（规范要求）
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


class TestDDDAuthService:
    """DDD认证应用服务测试类"""
    
    def test_auth_service_creation(self):
        """
        测试认证服务创建
        
        验证认证应用服务可以正确创建
        """
        from src.application.services.auth_service import AuthService
        
        # 创建模拟仓储
        mock_user_repository = Mock()
        mock_event_bus = Mock()
        
        # 创建认证服务
        auth_service = AuthService(
            user_repository=mock_user_repository,
            event_bus=mock_event_bus
        )
        
        # 验证属性
        assert auth_service.user_repository == mock_user_repository
        assert auth_service.event_bus == mock_event_bus
        
        # 验证方法
        assert hasattr(auth_service, "register")
        assert hasattr(auth_service, "login")
        assert hasattr(auth_service, "logout")
        
        print("✅ Auth service creation test passed")
    
    def test_auth_service_register(self, ddd_test_user_data, mock_user_repository, mock_event_bus):
        """
        测试认证服务注册功能
        
        验证用户注册功能正常工作
        """
        from src.application.services.auth_service import AuthService
        from src.domain.user.entities_simple import User
        
        # 配置模拟仓储
        mock_user_repository.find_by_email.return_value = None
        mock_user_repository.save.return_value = User(
            id="user_001",
            username=ddd_test_user_data["username"],
            email=ddd_test_user_data["email"],
            full_name=ddd_test_user_data["full_name"],
            role=ddd_test_user_data["role"]
        )
        
        # 创建认证服务
        auth_service = AuthService(
            user_repository=mock_user_repository,
            event_bus=mock_event_bus
        )
        
        # 执行注册
        result = auth_service.register(
            username=ddd_test_user_data["username"],
            email=ddd_test_user_data["email"],
            password=ddd_test_user_data["password"],
            full_name=ddd_test_user_data["full_name"],
            role=ddd_test_user_data["role"]
        )
        
        # 验证结果
        assert result is not None
        assert result.username == ddd_test_user_data["username"]
        assert result.email == ddd_test_user_data["email"]
        
        # 验证仓储调用
        mock_user_repository.find_by_email.assert_called_once_with(ddd_test_user_data["email"])
        mock_user_repository.save.assert_called_once()
        
        # 验证事件发布
        assert mock_event_bus.published_events
        assert len(mock_event_bus.published_events) > 0
        
        print("✅ Auth service register test passed")
    
    def test_auth_service_login(self, ddd_test_user_data, mock_user_repository, mock_event_bus):
        """
        测试认证服务登录功能
        
        验证用户登录功能正常工作
        """
        from src.application.services.auth_service import AuthService
        from src.domain.user.entities_simple import User
        from src.domain.user.value_objects_simple import Password
        
        # 创建测试用户
        test_user = User(
            id="user_001",
            username=ddd_test_user_data["username"],
            email=ddd_test_user_data["email"],
            full_name=ddd_test_user_data["full_name"],
            role=ddd_test_user_data["role"],
            is_active=True
        )
        
        # 配置模拟仓储
        mock_user_repository.find_by_email.return_value = test_user
        
        # 创建认证服务
        auth_service = AuthService(
            user_repository=mock_user_repository,
            event_bus=mock_event_bus
        )
        
        # 执行登录（简化版本，实际需要密码验证）
        result = auth_service.login(
            email=ddd_test_user_data["email"],
            password=ddd_test_user_data["password"]
        )
        
        # 验证结果
        assert result is not None
        assert "user" in result
        assert "access_token" in result
        assert "refresh_token" in result
        
        # 验证仓储调用
        mock_user_repository.find_by_email.assert_called_once_with(ddd_test_user_data["email"])
        
        print("✅ Auth service login test passed")


class TestDDDTaskService:
    """DDD任务应用服务测试类"""
    
    def test_task_service_creation(self):
        """
        测试任务服务创建
        
        验证任务应用服务可以正确创建
        """
        from src.application.services.task_service_simple import TaskService
        
        # 创建模拟仓储
        mock_task_repository = Mock()
        mock_event_bus = Mock()
        
        # 创建任务服务
        task_service = TaskService(
            task_repository=mock_task_repository,
            event_bus=mock_event_bus
        )
        
        # 验证属性
        assert task_service.task_repository == mock_task_repository
        assert task_service.event_bus == mock_event_bus
        
        # 验证方法
        assert hasattr(task_service, "create_task")
        assert hasattr(task_service, "get_task")
        assert hasattr(task_service, "update_task")
        
        print("✅ Task service creation test passed")
    
    def test_task_service_create_task(self, sample_task_entity_data, mock_task_repository, mock_event_bus):
        """
        测试任务服务创建任务功能
        
        验证任务创建功能正常工作
        """
        from src.application.services.task_service_simple import TaskService
        from src.domain.task.entities import Task
        
        # 配置模拟仓储
        mock_task_repository.save.return_value = Task(**sample_task_entity_data)
        
        # 创建任务服务
        task_service = TaskService(
            task_repository=mock_task_repository,
            event_bus=mock_event_bus
        )
        
        # 执行创建任务
        result = task_service.create_task(
            title=sample_task_entity_data["title"],
            description=sample_task_entity_data["description"],
            type=sample_task_entity_data["type"],
            priority=sample_task_entity_data["priority"],
            created_by=sample_task_entity_data["created_by"],
            tenant_id=sample_task_entity_data["tenant_id"]
        )
        
        # 验证结果
        assert result is not None
        assert result.title == sample_task_entity_data["title"]
        assert result.description == sample_task_entity_data["description"]
        
        # 验证仓储调用
        mock_task_repository.save.assert_called_once()
        
        # 验证事件发布
        assert mock_event_bus.published_events
        assert len(mock_event_bus.published_events) > 0
        
        print("✅ Task service create task test passed")
    
    def test_task_service_get_task(self, sample_task_entity_data, mock_task_repository, mock_event_bus):
        """
        测试任务服务获取任务功能
        
        验证任务获取功能正常工作
        """
        from src.application.services.task_service_simple import TaskService
        from src.domain.task.entities import Task
        
        # 创建测试任务
        test_task = Task(**sample_task_entity_data)
        
        # 配置模拟仓储
        mock_task_repository.find_by_id.return_value = test_task
        
        # 创建任务服务
        task_service = TaskService(
            task_repository=mock_task_repository,
            event_bus=mock_event_bus
        )
        
        # 执行获取任务
        result = task_service.get_task(task_id=sample_task_entity_data["id"])
        
        # 验证结果
        assert result is not None
        assert result.id == sample_task_entity_data["id"]
        assert result.title == sample_task_entity_data["title"]
        
        # 验证仓储调用
        mock_task_repository.find_by_id.assert_called_once_with(sample_task_entity_data["id"])
        
        print("✅ Task service get task test passed")


class TestDDDExerciseService:
    """DDD运动应用服务测试类"""
    
    def test_exercise_service_creation(self):
        """
        测试运动服务创建
        
        验证运动应用服务可以正确创建
        """
        from src.application.services.exercise_service_simple import ExerciseService
        
        # 创建模拟仓储
        mock_exercise_repository = Mock()
        mock_event_bus = Mock()
        
        # 创建运动服务
        exercise_service = ExerciseService(
            exercise_repository=mock_exercise_repository,
            event_bus=mock_event_bus
        )
        
        # 验证属性
        assert exercise_service.exercise_repository == mock_exercise_repository
        assert exercise_service.event_bus == mock_event_bus
        
        # 验证方法
        assert hasattr(exercise_service, "create_exercise_record")
        assert hasattr(exercise_service, "get_exercise_records")
        assert hasattr(exercise_service, "analyze_exercise_progress")
        
        print("✅ Exercise service creation test passed")
    
    def test_exercise_service_create_record(self, sample_exercise_entity_data, mock_exercise_repository, mock_event_bus):
        """
        测试运动服务创建记录功能
        
        验证运动记录创建功能正常工作
        """
        from src.application.services.exercise_service_simple import ExerciseService
        from src.domain.exercise.entities import ExerciseRecord
        
        # 配置模拟仓储
        mock_exercise_repository.save.return_value = ExerciseRecord(**sample_exercise_entity_data)
        
        # 创建运动服务
        exercise_service = ExerciseService(
            exercise_repository=mock_exercise_repository,
            event_bus=mock_event_bus
        )
        
        # 执行创建记录
        result = exercise_service.create_exercise_record(
            type=sample_exercise_entity_data["type"],
            duration=sample_exercise_entity_data["duration"],
            count=sample_exercise_entity_data["count"],
            calories=sample_exercise_entity_data["calories"],
            user_id=sample_exercise_entity_data["user_id"],
            tenant_id=sample_exercise_entity_data["tenant_id"]
        )
        
        # 验证结果
        assert result is not None
        assert result.type == sample_exercise_entity_data["type"]
        assert result.duration == sample_exercise_entity_data["duration"]
        
        # 验证仓储调用
        mock_exercise_repository.save.assert_called_once()
        
        print("✅ Exercise service create record test passed")


class TestDDDAchievementService:
    """DDD成就应用服务测试类"""
    
    def test_achievement_service_creation(self):
        """
        测试成就服务创建
        
        验证成就应用服务可以正确创建
        """
        from src.application.services.achievement_service_simple import AchievementService
        
        # 创建模拟仓储
        mock_achievement_repository = Mock()
        mock_event_bus = Mock()
        
        # 创建成就服务
        achievement_service = AchievementService(
            achievement_repository=mock_achievement_repository,
            event_bus=mock_event_bus
        )
        
        # 验证属性
        assert achievement_service.achievement_repository == mock_achievement_repository
        assert achievement_service.event_bus == mock_event_bus
        
        # 验证方法
        assert hasattr(achievement_service, "check_achievements")
        assert hasattr(achievement_service, "unlock_achievement")
        assert hasattr(achievement_service, "get_user_achievements")
        
        print("✅ Achievement service creation test passed")
    
    def test_achievement_service_check_achievements(self, sample_achievement_entity_data, mock_achievement_repository, mock_event_bus):
        """
        测试成就服务检查成就功能
        
        验证成就检查功能正常工作
        """
        from src.application.services.achievement_service_simple import AchievementService
        from src.domain.achievement.entities import Achievement
        
        # 创建测试成就
        test_achievement = Achievement(**sample_achievement_entity_data)
        
        # 配置模拟仓储
        mock_achievement_repository.find_by_type.return_value = [test_achievement]
        
        # 创建成就服务
        achievement_service = AchievementService(
            achievement_repository=mock_achievement_repository,
            event_bus=mock_event_bus
        )
        
        # 执行检查成就
        result = achievement_service.check_achievements(
            user_id="user_001",
            achievement_type=sample_achievement_entity_data["type"],
            current_value=50
        )
        
        # 验证结果
        assert result is not None
        assert isinstance(result, list)
        
        # 验证仓储调用
        mock_achievement_repository.find_by_type.assert_called_once_with(sample_achievement_entity_data["type"])
        
        print("✅ Achievement service check achievements test passed")


class TestDDDEventBus:
    """DDD事件总线测试类"""
    
    def test_event_bus_publish_subscribe(self, mock_event_bus):
        """
        测试事件总线发布和订阅功能
        
        验证事件总线可以正确发布和订阅事件
        """
        # 定义事件处理器
        event_handler_called = False
        
        def test_handler(event):
            nonlocal event_handler_called
            event_handler_called = True
            assert event.event_type == "TestEvent"
        
        # 订阅事件
        mock_event_bus.subscribe("TestEvent", test_handler)
        
        # 创建测试事件
        class TestEvent:
            def __init__(self):
                self.event_type = "TestEvent"
                self.occurred_at = datetime.now()
        
        test_event = TestEvent()
        
        # 发布事件
        mock_event_bus.publish(test_event)
        
        # 验证事件处理器被调用
        assert event_handler_called is True
        assert test_event in mock_event_bus.published_events
        
        print("✅ Event bus publish/subscribe test passed")
    
    def test_event_bus_multiple_subscribers(self, mock_event_bus):
        """
        测试事件总线多个订阅者功能
        
        验证事件总线可以处理多个订阅者
        """
        # 定义事件处理器
        handler1_called = False
        handler2_called = False
        
        def handler1(event):
            nonlocal handler1_called
            handler1_called = True
        
        def handler2(event):
            nonlocal handler2_called
            handler2_called = True
        
        # 订阅事件
        mock_event_bus.subscribe("TestEvent", handler1)
        mock_event_bus.subscribe("TestEvent", handler2)
        
        # 创建测试事件
        class TestEvent:
            def __init__(self):
                self.event_type = "TestEvent"
                self.occurred_at = datetime.now()
        
        test_event = TestEvent()
        
        # 发布事件
        mock_event_bus.publish(test_event)
        
        # 验证所有事件处理器都被调用
        assert handler1_called is True
        assert handler2_called is True
        
        print("✅ Event bus multiple subscribers test passed")


if __name__ == "__main__":
    """
    直接运行测试
    """
    print("=" * 60)
    print("DDD Application Layer Unit Tests")
    print("=" * 60)
    
    # 创建测试实例
    test_classes = [
        TestDDDAuthService,
        TestDDDTaskService,
        TestDDDExerciseService,
        TestDDDAchievementService,
        TestDDDEventBus
    ]
    
    passed_tests = 0
    total_tests = 0
    
    for test_class in test_classes:
        test_instance = test_class()
        
        # 获取所有测试方法
        test_methods = [method for method in dir(test_instance) 
                       if method.startswith('test_') and callable(getattr(test_instance, method))]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_instance, method_name)
                method()
                passed_tests += 1
                print(f"✅ {test_class.__name__}.{method_name} passed")
            except Exception as e:
                print(f"❌ {test_class.__name__}.{method_name} failed: {e}")
    
    print("=" * 60)
    print(f"Test Results: {passed_tests}/{total_tests} tests passed")
    print("=" * 60)
    
    if passed_tests == total_tests:
        print("🎉 All DDD application layer tests passed!")
    else:
        print(f"⚠️  {total_tests - passed_tests} tests failed")
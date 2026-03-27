"""
DDD架构API接口层集成测试

注意：所有注释必须使用中文（规范要求）
所有日志和异常消息必须使用英文（规范要求）
"""

import pytest
import sys
import os
import json
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


class TestDDDAuthAPI:
    """DDD认证API测试类"""
    
    def test_auth_register_handler(self, ddd_test_user_data, ddd_auth_headers):
        """
        测试认证注册处理器
        
        验证认证注册API处理器正常工作
        """
        from src.interfaces.api.v1.auth.handlers import RegisterHandler
        from src.interfaces.web.base_handler import BaseHandler
        
        # 创建模拟请求
        mock_request = Mock()
        mock_request.body = json.dumps(ddd_test_user_data)
        mock_request.headers = ddd_auth_headers
        
        # 创建模拟应用服务
        mock_auth_service = Mock()
        mock_auth_service.register.return_value = {
            "id": "user_001",
            "username": ddd_test_user_data["username"],
            "email": ddd_test_user_data["email"],
            "full_name": ddd_test_user_data["full_name"]
        }
        
        # 创建处理器
        handler = RegisterHandler(mock_request)
        handler.auth_service = mock_auth_service
        
        # 执行处理
        with patch.object(BaseHandler, 'write_json'):
            handler.post()
            
            # 验证服务调用
            mock_auth_service.register.assert_called_once_with(
                username=ddd_test_user_data["username"],
                email=ddd_test_user_data["email"],
                password=ddd_test_user_data["password"],
                full_name=ddd_test_user_data["full_name"],
                role=ddd_test_user_data.get("role", "student")
            )
        
        print("✅ Auth register handler test passed")
    
    def test_auth_login_handler(self, ddd_test_user_data, ddd_auth_headers):
        """
        测试认证登录处理器
        
        验证认证登录API处理器正常工作
        """
        from src.interfaces.api.v1.auth.handlers import LoginHandler
        from src.interfaces.web.base_handler import BaseHandler
        
        # 创建模拟请求
        mock_request = Mock()
        mock_request.body = json.dumps({
            "email": ddd_test_user_data["email"],
            "password": ddd_test_user_data["password"]
        })
        mock_request.headers = ddd_auth_headers
        
        # 创建模拟应用服务
        mock_auth_service = Mock()
        mock_auth_service.login.return_value = {
            "user": {
                "id": "user_001",
                "username": ddd_test_user_data["username"],
                "email": ddd_test_user_data["email"]
            },
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "token_type": "bearer",
            "expires_in": 1800
        }
        
        # 创建处理器
        handler = LoginHandler(mock_request)
        handler.auth_service = mock_auth_service
        
        # 执行处理
        with patch.object(BaseHandler, 'write_json'):
            handler.post()
            
            # 验证服务调用
            mock_auth_service.login.assert_called_once_with(
                email=ddd_test_user_data["email"],
                password=ddd_test_user_data["password"]
            )
        
        print("✅ Auth login handler test passed")


class TestDDDTenantAPI:
    """DDD租户API测试类"""
    
    def test_tenant_create_handler(self, ddd_test_tenant_data, ddd_auth_headers):
        """
        测试租户创建处理器
        
        验证租户创建API处理器正常工作
        """
        from src.interfaces.api.v1.user.tenant_handlers import CreateTenantHandler
        from src.interfaces.web.base_handler import BaseHandler
        
        # 创建模拟请求
        mock_request = Mock()
        mock_request.body = json.dumps(ddd_test_tenant_data)
        mock_request.headers = ddd_auth_headers
        
        # 创建模拟应用服务
        mock_tenant_service = Mock()
        mock_tenant_service.create_tenant.return_value = {
            "id": "tenant_001",
            "name": ddd_test_tenant_data["name"],
            "slug": ddd_test_tenant_data["slug"],
            "status": "active"
        }
        
        # 创建处理器
        handler = CreateTenantHandler(mock_request)
        handler.tenant_service = mock_tenant_service
        
        # 执行处理
        with patch.object(BaseHandler, 'write_json'):
            handler.post()
            
            # 验证服务调用
            mock_tenant_service.create_tenant.assert_called_once_with(
                name=ddd_test_tenant_data["name"],
                slug=ddd_test_tenant_data["slug"],
                description=ddd_test_tenant_data["description"],
                contact_email=ddd_test_tenant_data["contact_email"],
                contact_phone=ddd_test_tenant_data["contact_phone"],
                created_by="user_001"  # 从认证头中提取
            )
        
        print("✅ Tenant create handler test passed")
    
    def test_tenant_get_handler(self, ddd_test_tenant_data, ddd_auth_headers):
        """
        测试租户获取处理器
        
        验证租户获取API处理器正常工作
        """
        from src.interfaces.api.v1.user.tenant_handlers import GetTenantHandler
        from src.interfaces.web.base_handler import BaseHandler
        
        # 创建模拟请求
        mock_request = Mock()
        mock_request.headers = ddd_auth_headers
        mock_request.path_args = ["tenant_001"]
        
        # 创建模拟应用服务
        mock_tenant_service = Mock()
        mock_tenant_service.get_tenant.return_value = {
            "id": "tenant_001",
            "name": ddd_test_tenant_data["name"],
            "slug": ddd_test_tenant_data["slug"],
            "status": "active"
        }
        
        # 创建处理器
        handler = GetTenantHandler(mock_request)
        handler.tenant_service = mock_tenant_service
        
        # 执行处理
        with patch.object(BaseHandler, 'write_json'):
            handler.get("tenant_001")
            
            # 验证服务调用
            mock_tenant_service.get_tenant.assert_called_once_with(
                tenant_id="tenant_001"
            )
        
        print("✅ Tenant get handler test passed")


class TestDDDTaskAPI:
    """DDD任务API测试类"""
    
    def test_task_create_handler(self, sample_task_entity_data, ddd_auth_headers):
        """
        测试任务创建处理器
        
        验证任务创建API处理器正常工作
        """
        from src.interfaces.api.v1.task.handlers import TaskHandler
        from src.interfaces.web.base_handler import BaseHandler
        
        # 创建模拟请求
        mock_request = Mock()
        mock_request.body = json.dumps({
            "title": sample_task_entity_data["title"],
            "description": sample_task_entity_data["description"],
            "type": sample_task_entity_data["type"],
            "priority": sample_task_entity_data["priority"]
        })
        mock_request.headers = ddd_auth_headers
        
        # 创建模拟应用服务
        mock_task_service = Mock()
        mock_task_service.create_task.return_value = {
            "id": "task_001",
            "title": sample_task_entity_data["title"],
            "status": "pending"
        }
        
        # 创建处理器
        handler = TaskHandler(mock_request)
        handler.task_service = mock_task_service
        
        # 执行处理
        with patch.object(BaseHandler, 'write_json'):
            handler.post()
            
            # 验证服务调用
            mock_task_service.create_task.assert_called_once_with(
                title=sample_task_entity_data["title"],
                description=sample_task_entity_data["description"],
                type=sample_task_entity_data["type"],
                priority=sample_task_entity_data["priority"],
                created_by="user_001",  # 从认证头中提取
                tenant_id="tenant_001"  # 从认证头中提取
            )
        
        print("✅ Task create handler test passed")
    
    def test_task_get_handler(self, sample_task_entity_data, ddd_auth_headers):
        """
        测试任务获取处理器
        
        验证任务获取API处理器正常工作
        """
        from src.interfaces.api.v1.task.handlers import TaskHandler
        from src.interfaces.web.base_handler import BaseHandler
        
        # 创建模拟请求
        mock_request = Mock()
        mock_request.headers = ddd_auth_headers
        mock_request.path_args = ["task_001"]
        
        # 创建模拟应用服务
        mock_task_service = Mock()
        mock_task_service.get_task.return_value = {
            "id": "task_001",
            "title": sample_task_entity_data["title"],
            "status": "pending"
        }
        
        # 创建处理器
        handler = TaskHandler(mock_request)
        handler.task_service = mock_task_service
        
        # 执行处理
        with patch.object(BaseHandler, 'write_json'):
            handler.get("task_001")
            
            # 验证服务调用
            mock_task_service.get_task.assert_called_once_with(
                task_id="task_001"
            )
        
        print("✅ Task get handler test passed")


class TestDDDExerciseAPI:
    """DDD运动API测试类"""
    
    def test_exercise_create_handler(self, sample_exercise_entity_data, ddd_auth_headers):
        """
        测试运动记录创建处理器
        
        验证运动记录创建API处理器正常工作
        """
        from src.interfaces.api.v1.exercise.handlers import ExerciseRecordHandler
        from src.interfaces.web.base_handler import BaseHandler
        
        # 创建模拟请求
        mock_request = Mock()
        mock_request.body = json.dumps({
            "type": sample_exercise_entity_data["type"],
            "duration": sample_exercise_entity_data["duration"],
            "count": sample_exercise_entity_data["count"],
            "calories": sample_exercise_entity_data["calories"]
        })
        mock_request.headers = ddd_auth_headers
        
        # 创建模拟应用服务
        mock_exercise_service = Mock()
        mock_exercise_service.create_exercise_record.return_value = {
            "id": "exercise_001",
            "type": sample_exercise_entity_data["type"],
            "duration": sample_exercise_entity_data["duration"]
        }
        
        # 创建处理器
        handler = ExerciseRecordHandler(mock_request)
        handler.exercise_service = mock_exercise_service
        
        # 执行处理
        with patch.object(BaseHandler, 'write_json'):
            handler.post()
            
            # 验证服务调用
            mock_exercise_service.create_exercise_record.assert_called_once_with(
                type=sample_exercise_entity_data["type"],
                duration=sample_exercise_entity_data["duration"],
                count=sample_exercise_entity_data["count"],
                calories=sample_exercise_entity_data["calories"],
                user_id="user_001",  # 从认证头中提取
                tenant_id="tenant_001"  # 从认证头中提取
            )
        
        print("✅ Exercise create handler test passed")


class TestDDDAchievementAPI:
    """DDD成就API测试类"""
    
    def test_achievement_get_handler(self, sample_achievement_entity_data, ddd_auth_headers):
        """
        测试成就获取处理器
        
        验证成就获取API处理器正常工作
        """
        from src.interfaces.api.v1.achievement.handlers import AchievementHandler
        from src.interfaces.web.base_handler import BaseHandler
        
        # 创建模拟请求
        mock_request = Mock()
        mock_request.headers = ddd_auth_headers
        mock_request.path_args = ["achievement_001"]
        
        # 创建模拟应用服务
        mock_achievement_service = Mock()
        mock_achievement_service.get_achievement.return_value = {
            "id": "achievement_001",
            "name": sample_achievement_entity_data["name"],
            "description": sample_achievement_entity_data["description"]
        }
        
        # 创建处理器
        handler = AchievementHandler(mock_request)
        handler.achievement_service = mock_achievement_service
        
        # 执行处理
        with patch.object(BaseHandler, 'write_json'):
            handler.get("achievement_001")
            
            # 验证服务调用
            mock_achievement_service.get_achievement.assert_called_once_with(
                achievement_id="achievement_001"
            )
        
        print("✅ Achievement get handler test passed")


class TestDDDHealthAPI:
    """DDD健康检查API测试类"""
    
    def test_health_check_handler(self):
        """
        测试健康检查处理器
        
        验证健康检查API处理器正常工作
        """
        from src.interfaces.api.v1.health.handlers import HealthHandler
        from src.interfaces.web.base_handler import BaseHandler
        
        # 创建模拟请求
        mock_request = Mock()
        
        # 创建模拟数据库管理器
        mock_db_manager = Mock()
        mock_db_manager.health_check.return_value = {
            "status": "healthy",
            "message": "Database connection is working"
        }
        
        # 创建模拟Redis管理器
        mock_redis_manager = Mock()
        mock_redis_manager.health_check.return_value = {
            "status": "healthy",
            "message": "Redis connection is working"
        }
        
        # 创建处理器
        handler = HealthHandler(mock_request)
        handler.db_manager = mock_db_manager
        handler.redis_manager = mock_redis_manager
        
        # 执行处理
        with patch.object(BaseHandler, 'write_json') as mock_write_json:
            handler.get()
            
            # 验证健康检查调用
            mock_db_manager.health_check.assert_called_once()
            mock_redis_manager.health_check.assert_called_once()
            
            # 验证响应
            mock_write_json.assert_called_once()
            call_args = mock_write_json.call_args[0][0]
            assert "status" in call_args
            assert "timestamp" in call_args
            assert "services" in call_args
        
        print("✅ Health check handler test passed")


class TestDDDErrorHandling:
    """DDD错误处理测试类"""
    
    def test_authentication_error(self):
        """
        测试认证错误处理
        
        验证认证错误被正确处理
        """
        from src.interfaces.api.middleware.exceptions import AuthenticationError
        from src.interfaces.web.error_handler import ErrorHandler
        
        # 创建认证错误
        error = AuthenticationError("Invalid credentials")
        
        # 验证错误属性
        assert error.status_code == 401
        assert "Invalid credentials" in str(error)
        
        print("✅ Authentication error test passed")
    
    def test_authorization_error(self):
        """
        测试授权错误处理
        
        验证授权错误被正确处理
        """
        from src.interfaces.api.middleware.exceptions import AuthorizationError
        
        # 创建授权错误
        error = AuthorizationError("Insufficient permissions")
        
        # 验证错误属性
        assert error.status_code == 403
        assert "Insufficient permissions" in str(error)
        
        print("✅ Authorization error test passed")
    
    def test_validation_error(self):
        """
        测试验证错误处理
        
        验证验证错误被正确处理
        """
        from src.interfaces.api.middleware.exceptions import ValidationError
        
        # 创建验证错误
        error = ValidationError("Invalid input data", {"field": "email", "error": "Invalid format"})
        
        # 验证错误属性
        assert error.status_code == 400
        assert "Invalid input data" in str(error)
        assert "details" in error.to_dict()
        
        print("✅ Validation error test passed")


if __name__ == "__main__":
    """
    直接运行测试
    """
    print("=" * 60)
    print("DDD API Layer Integration Tests")
    print("=" * 60)
    
    # 创建测试实例
    test_classes = [
        TestDDDAuthAPI,
        TestDDDTenantAPI,
        TestDDDTaskAPI,
        TestDDDExerciseAPI,
        TestDDDAchievementAPI,
        TestDDDHealthAPI,
        TestDDDErrorHandling
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
        print("🎉 All DDD API layer tests passed!")
    else:
        print(f"⚠️  {total_tests - passed_tests} tests failed")
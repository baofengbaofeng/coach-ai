"""
DDD架构领域层单元测试

注意：所有注释必须使用中文（规范要求）
所有日志和异常消息必须使用英文（规范要求）
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


class TestDDDUserDomain:
    """DDD用户领域测试类"""
    
    def test_user_entity_creation(self, sample_user_entity_data):
        """
        测试用户实体创建
        
        验证用户实体可以正确创建并包含所有必需属性
        """
        from src.domain.user.entities_simple import User
        
        # 创建用户实体
        user = User(**sample_user_entity_data)
        
        # 验证属性
        assert user.id == sample_user_entity_data["id"]
        assert user.username == sample_user_entity_data["username"]
        assert user.email == sample_user_entity_data["email"]
        assert user.full_name == sample_user_entity_data["full_name"]
        assert user.role == sample_user_entity_data["role"]
        assert user.is_active == sample_user_entity_data["is_active"]
        
        # 验证方法
        assert hasattr(user, "activate")
        assert hasattr(user, "deactivate")
        assert hasattr(user, "update_profile")
        
        print("✅ User entity creation test passed")
    
    def test_user_entity_activation(self, sample_user_entity_data):
        """
        测试用户实体激活/停用
        
        验证用户激活和停用方法正常工作
        """
        from src.domain.user.entities_simple import User
        
        # 创建用户实体
        user = User(**sample_user_entity_data)
        
        # 测试激活（如果当前不是激活状态）
        if not user.is_active:
            user.activate()
            assert user.is_active is True
            print("✅ User activation test passed")
        
        # 测试停用
        user.deactivate()
        assert user.is_active is False
        print("✅ User deactivation test passed")
    
    def test_user_entity_profile_update(self, sample_user_entity_data):
        """
        测试用户实体资料更新
        
        验证用户资料更新方法正常工作
        """
        from src.domain.user.entities_simple import User
        
        # 创建用户实体
        user = User(**sample_user_entity_data)
        
        # 更新资料
        new_full_name = "更新后的用户名"
        new_email = "updated@example.com"
        
        user.update_profile(full_name=new_full_name, email=new_email)
        
        assert user.full_name == new_full_name
        assert user.email == new_email
        assert user.updated_at > user.created_at
        
        print("✅ User profile update test passed")


class TestDDDTenantDomain:
    """DDD租户领域测试类"""
    
    def test_tenant_entity_creation(self, sample_tenant_entity_data):
        """
        测试租户实体创建
        
        验证租户实体可以正确创建并包含所有必需属性
        """
        from src.domain.user.entities_simple import Tenant
        
        # 创建租户实体
        tenant = Tenant(**sample_tenant_entity_data)
        
        # 验证属性
        assert tenant.id == sample_tenant_entity_data["id"]
        assert tenant.name == sample_tenant_entity_data["name"]
        assert tenant.slug == sample_tenant_entity_data["slug"]
        assert tenant.description == sample_tenant_entity_data["description"]
        assert tenant.status == sample_tenant_entity_data["status"]
        
        # 验证方法
        assert hasattr(tenant, "activate")
        assert hasattr(tenant, "suspend")
        assert hasattr(tenant, "update_info")
        
        print("✅ Tenant entity creation test passed")
    
    def test_tenant_entity_status_management(self, sample_tenant_entity_data):
        """
        测试租户实体状态管理
        
        验证租户状态管理方法正常工作
        """
        from src.domain.user.entities_simple import Tenant
        
        # 创建租户实体
        tenant = Tenant(**sample_tenant_entity_data)
        
        # 测试挂起
        tenant.suspend()
        assert tenant.status == "suspended"
        print("✅ Tenant suspension test passed")
        
        # 测试激活
        tenant.activate()
        assert tenant.status == "active"
        print("✅ Tenant activation test passed")
    
    def test_tenant_entity_info_update(self, sample_tenant_entity_data):
        """
        测试租户实体信息更新
        
        验证租户信息更新方法正常工作
        """
        from src.domain.user.entities_simple import Tenant
        
        # 创建租户实体
        tenant = Tenant(**sample_tenant_entity_data)
        
        # 更新信息
        new_name = "更新后的租户名"
        new_description = "更新后的描述"
        
        tenant.update_info(name=new_name, description=new_description)
        
        assert tenant.name == new_name
        assert tenant.description == new_description
        assert tenant.updated_at > tenant.created_at
        
        print("✅ Tenant info update test passed")


class TestDDDTaskDomain:
    """DDD任务领域测试类"""
    
    def test_task_entity_creation(self, sample_task_entity_data):
        """
        测试任务实体创建
        
        验证任务实体可以正确创建并包含所有必需属性
        """
        from src.domain.task.entities import Task
        
        # 创建任务实体
        task = Task(**sample_task_entity_data)
        
        # 验证属性
        assert task.id == sample_task_entity_data["id"]
        assert task.title == sample_task_entity_data["title"]
        assert task.description == sample_task_entity_data["description"]
        assert task.type == sample_task_entity_data["type"]
        assert task.priority == sample_task_entity_data["priority"]
        assert task.status == sample_task_entity_data["status"]
        
        # 验证方法
        assert hasattr(task, "assign")
        assert hasattr(task, "complete")
        assert hasattr(task, "update_status")
        
        print("✅ Task entity creation test passed")
    
    def test_task_entity_status_transitions(self, sample_task_entity_data):
        """
        测试任务实体状态转换
        
        验证任务状态转换方法正常工作
        """
        from src.domain.task.entities import Task
        
        # 创建任务实体
        task = Task(**sample_task_entity_data)
        
        # 测试分配
        assignee_id = "user_002"
        task.assign(assignee_id)
        assert task.assignee_id == assignee_id
        assert task.status == "assigned"
        print("✅ Task assignment test passed")
        
        # 测试完成
        task.complete()
        assert task.status == "completed"
        assert task.completed_at is not None
        print("✅ Task completion test passed")
    
    def test_task_entity_priority_update(self, sample_task_entity_data):
        """
        测试任务实体优先级更新
        
        验证任务优先级更新方法正常工作
        """
        from src.domain.task.entities import Task
        
        # 创建任务实体
        task = Task(**sample_task_entity_data)
        
        # 更新优先级
        new_priority = "high"
        task.update_priority(new_priority)
        
        assert task.priority == new_priority
        assert task.updated_at > task.created_at
        
        print("✅ Task priority update test passed")


class TestDDDValueObjects:
    """DDD值对象测试类"""
    
    def test_email_value_object(self, sample_email_value_object):
        """
        测试Email值对象
        
        验证Email值对象可以正确创建和验证
        """
        from src.domain.user.value_objects_simple import Email
        
        # 创建Email值对象
        email = Email(
            address=sample_email_value_object["address"],
            verified=sample_email_value_object["verified"]
        )
        
        # 验证属性
        assert email.address == sample_email_value_object["address"]
        assert email.verified == sample_email_value_object["verified"]
        
        # 验证方法
        assert hasattr(email, "verify")
        assert hasattr(email, "is_valid")
        
        # 测试验证
        email.verify(sample_email_value_object["verification_token"])
        assert email.verified is True
        
        print("✅ Email value object test passed")
    
    def test_password_value_object(self, sample_password_value_object):
        """
        测试Password值对象
        
        验证Password值对象可以正确创建和验证
        """
        from src.domain.user.value_objects_simple import Password
        
        # 创建Password值对象
        password = Password(
            hash=sample_password_value_object["hash"],
            salt=sample_password_value_object["salt"],
            algorithm=sample_password_value_object["algorithm"]
        )
        
        # 验证属性
        assert password.hash == sample_password_value_object["hash"]
        assert password.salt == sample_password_value_object["salt"]
        assert password.algorithm == sample_password_value_object["algorithm"]
        
        # 验证方法
        assert hasattr(password, "verify")
        assert hasattr(password, "hash_password")
        
        print("✅ Password value object test passed")


class TestDDDDomainServices:
    """DDD领域服务测试类"""
    
    def test_user_service_creation(self):
        """
        测试用户领域服务创建
        
        验证用户领域服务可以正确创建
        """
        from src.domain.user.services import UserService
        
        # 创建用户服务
        user_service = UserService()
        
        # 验证方法
        assert hasattr(user_service, "register_user")
        assert hasattr(user_service, "authenticate_user")
        assert hasattr(user_service, "update_user_profile")
        
        print("✅ User service creation test passed")
    
    def test_task_service_creation(self):
        """
        测试任务领域服务创建
        
        验证任务领域服务可以正确创建
        """
        from src.domain.task.services import TaskService
        
        # 创建任务服务
        task_service = TaskService()
        
        # 验证方法
        assert hasattr(task_service, "create_task")
        assert hasattr(task_service, "assign_task")
        assert hasattr(task_service, "complete_task")
        
        print("✅ Task service creation test passed")


class TestDDDDomainEvents:
    """DDD领域事件测试类"""
    
    def test_user_registered_event(self, sample_user_registered_event_data):
        """
        测试用户注册事件
        
        验证用户注册事件可以正确创建
        """
        from src.domain.user.events_simple import UserRegistered
        
        # 创建用户注册事件
        event = UserRegistered(
            user_id=sample_user_registered_event_data["payload"]["user_id"],
            username=sample_user_registered_event_data["payload"]["username"],
            email=sample_user_registered_event_data["payload"]["email"],
            registered_at=sample_user_registered_event_data["payload"]["registered_at"]
        )
        
        # 验证属性
        assert event.user_id == sample_user_registered_event_data["payload"]["user_id"]
        assert event.username == sample_user_registered_event_data["payload"]["username"]
        assert event.email == sample_user_registered_event_data["payload"]["email"]
        
        # 验证事件类型
        assert event.event_type == "UserRegistered"
        assert event.occurred_at is not None
        
        print("✅ User registered event test passed")
    
    def test_task_created_event(self, sample_task_created_event_data):
        """
        测试任务创建事件
        
        验证任务创建事件可以正确创建
        """
        from src.domain.task.events import TaskCreated
        
        # 创建任务创建事件
        event = TaskCreated(
            task_id=sample_task_created_event_data["payload"]["task_id"],
            title=sample_task_created_event_data["payload"]["title"],
            created_by=sample_task_created_event_data["payload"]["created_by"],
            created_at=sample_task_created_event_data["payload"]["created_at"]
        )
        
        # 验证属性
        assert event.task_id == sample_task_created_event_data["payload"]["task_id"]
        assert event.title == sample_task_created_event_data["payload"]["title"]
        assert event.created_by == sample_task_created_event_data["payload"]["created_by"]
        
        # 验证事件类型
        assert event.event_type == "TaskCreated"
        assert event.occurred_at is not None
        
        print("✅ Task created event test passed")


if __name__ == "__main__":
    """
    直接运行测试
    """
    print("=" * 60)
    print("DDD Domain Layer Unit Tests")
    print("=" * 60)
    
    # 创建测试实例
    test_classes = [
        TestDDDUserDomain,
        TestDDDTenantDomain,
        TestDDDTaskDomain,
        TestDDDValueObjects,
        TestDDDDomainServices,
        TestDDDDomainEvents
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
        print("🎉 All DDD domain layer tests passed!")
    else:
        print(f"⚠️  {total_tests - passed_tests} tests failed")
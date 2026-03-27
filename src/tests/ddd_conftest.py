"""
DDD架构测试配置和共享fixtures

注意：所有注释必须使用中文（规范要求）
所有日志和异常消息必须使用英文（规范要求）
"""

import pytest
import sys
import os
import logging
import asyncio
from typing import Generator, AsyncGenerator, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 配置测试日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 测试数据库配置（使用SQLite内存数据库）
TEST_DATABASE_URL = "sqlite:///:memory:"

# 测试Redis配置（使用模拟Redis）
TEST_REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 15,  # 使用专门的测试数据库
    "password": None,
    "decode_responses": True
}


@pytest.fixture(scope="session")
def ddd_test_config():
    """
    DDD架构测试配置信息
    
    返回:
        dict: 测试配置字典
    """
    config = {
        "app": {
            "env": "testing",
            "debug": True,
            "host": "localhost",
            "port": 8888,
            "secret_key": "test-secret-key"
        },
        "database": {
            "url": TEST_DATABASE_URL,
            "pool_size": 5,
            "max_overflow": 10,
            "pool_recycle": 3600,
            "pool_pre_ping": True
        },
        "redis": TEST_REDIS_CONFIG,
        "jwt": {
            "secret_key": "test-jwt-secret-key",
            "algorithm": "HS256",
            "access_token_expire_minutes": 30,
            "refresh_token_expire_days": 7
        },
        "cache": {
            "key_prefix": "test_coach_ai",
            "default_timeout": 300
        },
        "event_bus": {
            "type": "memory",
            "retry_attempts": 3,
            "retry_delay": 1
        }
    }
    logger.info("DDD test configuration loaded")
    return config


@pytest.fixture(scope="session")
def ddd_test_engine():
    """
    创建DDD测试数据库引擎
    
    返回:
        Engine: SQLAlchemy引擎实例
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    logger.info("DDD test database engine created")
    return engine


@pytest.fixture(scope="session")
def ddd_test_session_factory(ddd_test_engine):
    """
    创建DDD测试会话工厂
    
    参数:
        ddd_test_engine: 测试数据库引擎
        
    返回:
        sessionmaker: SQLAlchemy会话工厂
    """
    return sessionmaker(
        bind=ddd_test_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        future=True
    )


@pytest.fixture
def ddd_db_session(ddd_test_session_factory) -> Generator[Session, None, None]:
    """
    提供DDD数据库会话的fixture
    
    参数:
        ddd_test_session_factory: 测试会话工厂
        
    返回:
        Generator[Session, None, None]: 数据库会话生成器
    """
    session = ddd_test_session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture(scope="session")
def ddd_event_loop():
    """
    为DDD异步测试提供事件循环
    
    返回:
        asyncio.AbstractEventLoop: 事件循环实例
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# DDD领域模型测试fixtures
@pytest.fixture
def sample_user_entity_data():
    """
    示例用户实体测试数据
    
    返回:
        dict: 包含用户实体信息的字典
    """
    return {
        "id": "user_001",
        "username": "test_user",
        "email": "test@example.com",
        "full_name": "测试用户",
        "role": "student",
        "is_active": True,
        "created_at": "2026-03-27T10:00:00Z",
        "updated_at": "2026-03-27T10:00:00Z"
    }


@pytest.fixture
def sample_tenant_entity_data():
    """
    示例租户实体测试数据
    
    返回:
        dict: 包含租户实体信息的字典
    """
    return {
        "id": "tenant_001",
        "name": "测试租户",
        "slug": "test-tenant",
        "description": "这是一个测试租户",
        "contact_email": "contact@test.com",
        "contact_phone": "13800138000",
        "status": "active",
        "created_at": "2026-03-27T10:00:00Z",
        "updated_at": "2026-03-27T10:00:00Z"
    }


@pytest.fixture
def sample_task_entity_data():
    """
    示例任务实体测试数据
    
    返回:
        dict: 包含任务实体信息的字典
    """
    return {
        "id": "task_001",
        "title": "数学作业",
        "description": "完成第5章练习题",
        "type": "homework",
        "priority": "medium",
        "status": "pending",
        "due_date": "2026-03-30T23:59:59Z",
        "estimated_time": 120,  # 分钟
        "created_by": "user_001",
        "tenant_id": "tenant_001",
        "created_at": "2026-03-27T10:00:00Z",
        "updated_at": "2026-03-27T10:00:00Z"
    }


@pytest.fixture
def sample_exercise_entity_data():
    """
    示例运动实体测试数据
    
    返回:
        dict: 包含运动实体信息的字典
    """
    return {
        "id": "exercise_001",
        "type": "jump_rope",
        "duration": 300,  # 5分钟
        "count": 150,
        "calories": 50,
        "user_id": "user_001",
        "tenant_id": "tenant_001",
        "created_at": "2026-03-27T10:00:00Z"
    }


@pytest.fixture
def sample_achievement_entity_data():
    """
    示例成就实体测试数据
    
    返回:
        dict: 包含成就实体信息的字典
    """
    return {
        "id": "achievement_001",
        "name": "运动达人",
        "description": "完成100次运动",
        "type": "exercise",
        "target_value": 100,
        "reward_points": 100,
        "badge_url": "/badges/exercise_master.png",
        "created_at": "2026-03-27T10:00:00Z",
        "updated_at": "2026-03-27T10:00:00Z"
    }


# DDD值对象测试fixtures
@pytest.fixture
def sample_email_value_object():
    """
    示例Email值对象测试数据
    
    返回:
        dict: 包含Email值对象信息的字典
    """
    return {
        "address": "test@example.com",
        "verified": False,
        "verification_token": "verification_token_123"
    }


@pytest.fixture
def sample_password_value_object():
    """
    示例Password值对象测试数据
    
    返回:
        dict: 包含Password值对象信息的字典
    """
    return {
        "hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # bcrypt hash of "Test@123456"
        "salt": "random_salt",
        "algorithm": "bcrypt"
    }


@pytest.fixture
def sample_task_priority_value_object():
    """
    示例任务优先级值对象测试数据
    
    返回:
        dict: 包含任务优先级值对象信息的字典
    """
    return {
        "level": "medium",
        "weight": 5,
        "color": "#FFA500"
    }


# DDD领域事件测试fixtures
@pytest.fixture
def sample_user_registered_event_data():
    """
    示例用户注册事件测试数据
    
    返回:
        dict: 包含用户注册事件信息的字典
    """
    return {
        "event_id": "event_001",
        "event_type": "UserRegistered",
        "aggregate_id": "user_001",
        "aggregate_type": "User",
        "payload": {
            "user_id": "user_001",
            "username": "test_user",
            "email": "test@example.com",
            "registered_at": "2026-03-27T10:00:00Z"
        },
        "metadata": {
            "correlation_id": "corr_001",
            "user_agent": "test-client/1.0",
            "ip_address": "127.0.0.1"
        },
        "occurred_at": "2026-03-27T10:00:00Z"
    }


@pytest.fixture
def sample_task_created_event_data():
    """
    示例任务创建事件测试数据
    
    返回:
        dict: 包含任务创建事件信息的字典
    """
    return {
        "event_id": "event_002",
        "event_type": "TaskCreated",
        "aggregate_id": "task_001",
        "aggregate_type": "Task",
        "payload": {
            "task_id": "task_001",
            "title": "数学作业",
            "created_by": "user_001",
            "created_at": "2026-03-27T10:00:00Z"
        },
        "metadata": {
            "correlation_id": "corr_002",
            "tenant_id": "tenant_001"
        },
        "occurred_at": "2026-03-27T10:00:00Z"
    }


# DDD应用服务测试fixtures
@pytest.fixture
def mock_user_repository():
    """
    模拟用户仓储
    
    返回:
        Mock: 模拟的用户仓储对象
    """
    class MockUserRepository:
        def __init__(self):
            self.users = {}
            self.save_called = False
            self.find_by_id_called = False
            self.find_by_email_called = False
        
        def save(self, user):
            self.save_called = True
            self.users[user.id] = user
            return user
        
        def find_by_id(self, user_id):
            self.find_by_id_called = True
            return self.users.get(user_id)
        
        def find_by_email(self, email):
            self.find_by_email_called = True
            for user in self.users.values():
                if hasattr(user, 'email') and user.email == email:
                    return user
            return None
    
    return MockUserRepository()


@pytest.fixture
def mock_task_repository():
    """
    模拟任务仓储
    
    返回:
        Mock: 模拟的任务仓储对象
    """
    class MockTaskRepository:
        def __init__(self):
            self.tasks = {}
            self.save_called = False
            self.find_by_id_called = False
            self.find_by_user_called = False
        
        def save(self, task):
            self.save_called = True
            self.tasks[task.id] = task
            return task
        
        def find_by_id(self, task_id):
            self.find_by_id_called = True
            return self.tasks.get(task_id)
        
        def find_by_user(self, user_id):
            self.find_by_user_called = True
            return [task for task in self.tasks.values() if hasattr(task, 'user_id') and task.user_id == user_id]
    
    return MockTaskRepository()


@pytest.fixture
def mock_event_bus():
    """
    模拟事件总线
    
    返回:
        Mock: 模拟的事件总线对象
    """
    class MockEventBus:
        def __init__(self):
            self.published_events = []
            self.subscribers = {}
        
        def publish(self, event):
            self.published_events.append(event)
            event_type = event.__class__.__name__
            if event_type in self.subscribers:
                for handler in self.subscribers[event_type]:
                    handler(event)
        
        def subscribe(self, event_type, handler):
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            self.subscribers[event_type].append(handler)
        
        def clear(self):
            self.published_events.clear()
            self.subscribers.clear()
    
    return MockEventBus()


# DDD API测试fixtures
@pytest.fixture
def ddd_auth_headers():
    """
    提供DDD认证头部的fixture
    
    返回:
        dict: 包含认证头部的字典
    """
    return {
        "Authorization": "Bearer test_jwt_token",
        "Content-Type": "application/json",
        "X-Tenant-ID": "tenant_001"
    }


@pytest.fixture
def ddd_test_user_data():
    """
    DDD测试用户数据
    
    返回:
        dict: 测试用户数据
    """
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test@123456",
        "full_name": "测试用户",
        "role": "student"
    }


@pytest.fixture
def ddd_test_tenant_data():
    """
    DDD测试租户数据
    
    返回:
        dict: 测试租户数据
    """
    return {
        "name": "测试租户",
        "slug": "test-tenant",
        "description": "这是一个测试租户",
        "contact_email": "contact@test.com",
        "contact_phone": "13800138000"
    }


# 辅助函数
def validate_ddd_test_data(data: dict, required_fields: list) -> bool:
    """
    验证DDD测试数据是否包含必需字段
    
    参数:
        data: 要验证的数据字典
        required_fields: 必需字段列表
        
    返回:
        bool: 验证是否通过
        
    异常:
        TestDataError: 如果数据验证失败
    """
    if not isinstance(data, dict):
        error_msg = "DDD test data must be a dictionary"
        logger.error(error_msg)
        raise TestDataError(error_msg)
    
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        error_msg = f"Missing required fields: {missing_fields}"
        logger.error(error_msg)
        raise TestDataError(error_msg)
    
    logger.info("DDD test data validation passed")
    return True


def create_ddd_test_user(session, user_data=None):
    """
    创建DDD测试用户
    
    参数:
        session: 数据库会话
        user_data: 用户数据，如果为None则使用默认数据
        
    返回:
        User: 创建的测试用户
    """
    from src.domain.user.entities_simple import User
    
    if user_data is None:
        user_data = {
            "id": "user_001",
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "测试用户",
            "role": "student",
            "is_active": True
        }
    
    user = User(**user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user


def create_ddd_test_tenant(session, tenant_data=None):
    """
    创建DDD测试租户
    
    参数:
        session: 数据库会话
        tenant_data: 租户数据，如果为None则使用默认数据
        
    返回:
        Tenant: 创建的测试租户
    """
    from src.domain.user.entities_simple import Tenant
    
    if tenant_data is None:
        tenant_data = {
            "id": "tenant_001",
            "name": "测试租户",
            "slug": "test-tenant",
            "description": "这是一个测试租户",
            "contact_email": "contact@test.com",
            "status": "active"
        }
    
    tenant = Tenant(**tenant_data)
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    
    return tenant


# 异常类定义
class DDDTestConfigurationError(Exception):
    """DDD测试配置错误异常"""
    pass


class DDDTestDataError(Exception):
    """DDD测试数据错误异常"""
    pass


# pytest配置钩子
def pytest_configure_ddd(config):
    """
    DDD架构pytest配置钩子函数
    
    用于配置DDD测试运行时的行为
    """
    # 添加DDD自定义标记
    config.addinivalue_line(
        "markers", "ddd_unit: mark test as DDD unit test"
    )
    config.addinivalue_line(
        "markers", "ddd_integration: mark test as DDD integration test"
    )
    config.addinivalue_line(
        "markers", "ddd_api: mark test as DDD API test"
    )
    config.addinivalue_line(
        "markers", "ddd_domain: mark test as DDD domain test"
    )
    
    logger.info("DDD pytest configuration completed")


def pytest_sessionstart_ddd(session):
    """
    DDD测试会话开始时的钩子函数
    """
    logger.info("DDD test session started")


def pytest_sessionfinish_ddd(session, exitstatus):
    """
    DDD测试会话结束时的钩子函数
    """
    logger.info(f"DDD test session finished with status: {exitstatus}")
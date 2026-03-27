"""
测试配置和共享fixtures

注意：所有注释必须使用中文（规范要求）
所有日志和异常消息必须使用英文（规范要求）
"""

import pytest
import sys
import os
import logging
import asyncio
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 配置测试日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///:memory:"
# 对于MySQL测试，可以使用：
# TEST_DATABASE_URL = "mysql+pymysql://test:test@localhost/test_coach_ai?charset=utf8mb4"


@pytest.fixture
def sample_user_data():
    """
    示例用户测试数据
    
    返回:
        dict: 包含用户信息的字典
    """
    logger.info("Providing sample user data for test")  # 日志使用英文
    return {
        "id": 1,
        "username": "test_user",
        "email": "test@example.com",
        "role": "student"
    }


@pytest.fixture
def sample_family_data():
    """
    示例家庭测试数据
    
    返回:
        dict: 包含家庭信息的字典
    """
    logger.info("Providing sample family data for test")  # 日志使用英文
    return {
        "id": 1,
        "name": "测试家庭",
        "type": "core_family",
        "member_count": 3
    }


@pytest.fixture
def sample_homework_data():
    """
    示例作业测试数据
    
    返回:
        dict: 包含作业信息的字典
    """
    logger.info("Providing sample homework data for test")  # 日志使用英文
    return {
        "id": 1,
        "title": "数学作业",
        "subject": "math",
        "difficulty": "medium",
        "status": "pending"
    }


@pytest.fixture
def sample_exercise_data():
    """
    示例运动测试数据
    
    返回:
        dict: 包含运动信息的字典
    """
    logger.info("Providing sample exercise data for test")  # 日志使用英文
    return {
        "id": 1,
        "type": "jump_rope",
        "duration": 300,  # 5分钟
        "count": 150,
        "calories": 50
    }


@pytest.fixture(scope="session")
def test_config():
    """
    测试配置信息
    
    返回:
        dict: 测试配置字典
    """
    config = {
        "database": {
            "test_url": "sqlite:///:memory:",
            "echo": False
        },
        "api": {
            "base_url": "http://localhost:8000",
            "timeout": 10
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }
    logger.info("Test configuration loaded")  # 日志使用英文
    return config


@pytest.fixture
def cleanup_test_data():
    """
    测试数据清理fixture
    
    使用yield实现setup/teardown模式
    """
    # Setup阶段
    test_data = []
    logger.info("Starting test data setup")  # 日志使用英文
    
    yield test_data  # 测试执行
    
    # Teardown阶段
    logger.info("Cleaning up test data")  # 日志使用英文
    # 这里可以添加实际的数据清理逻辑
    test_data.clear()


def pytest_configure(config):
    """
    pytest配置钩子函数
    
    用于配置测试运行时的行为
    """
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    
    logger.info("Pytest configuration completed")  # 日志使用英文


def pytest_sessionstart(session):
    """
    测试会话开始时的钩子函数
    """
    logger.info("Test session started")  # 日志使用英文


def pytest_sessionfinish(session, exitstatus):
    """
    测试会话结束时的钩子函数
    """
    logger.info(f"Test session finished with status: {exitstatus}")  # 日志使用英文


# 异常类定义
class TestConfigurationError(Exception):
    """测试配置错误异常"""
    pass


class TestDataError(Exception):
    """测试数据错误异常"""
    pass


# 数据库测试fixtures
@pytest.fixture(scope="session")
def test_engine():
    """
    创建测试数据库引擎
    
    返回:
        Engine: SQLAlchemy引擎实例
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    logger.info("Test database engine created")
    return engine


@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """
    创建测试会话工厂
    
    参数:
        test_engine: 测试数据库引擎
        
    返回:
        sessionmaker: SQLAlchemy会话工厂
    """
    return sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        future=True
    )


@pytest.fixture
def db_session(test_session_factory) -> Generator[Session, None, None]:
    """
    提供数据库会话的fixture
    
    参数:
        test_session_factory: 测试会话工厂
        
    返回:
        Generator[Session, None, None]: 数据库会话生成器
    """
    session = test_session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture(scope="session")
def event_loop():
    """
    为异步测试提供事件循环
    
    返回:
        asyncio.AbstractEventLoop: 事件循环实例
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# API测试fixtures
@pytest.fixture
def auth_headers():
    """
    提供认证头部的fixture
    
    返回:
        dict: 包含认证头部的字典
    """
    return {
        "Authorization": "Bearer test_jwt_token",
        "Content-Type": "application/json"
    }


@pytest.fixture
def test_user_data():
    """
    测试用户数据
    
    返回:
        dict: 测试用户数据
    """
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test@123456",
        "full_name": "测试用户"
    }


@pytest.fixture
def test_tenant_data():
    """
    测试租户数据
    
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
def validate_test_data(data: dict, required_fields: list) -> bool:
    """
    验证测试数据是否包含必需字段
    
    参数:
        data: 要验证的数据字典
        required_fields: 必需字段列表
        
    返回:
        bool: 验证是否通过
        
    异常:
        TestDataError: 如果数据验证失败
    """
    if not isinstance(data, dict):
        error_msg = "Test data must be a dictionary"  # 异常消息使用英文
        logger.error(error_msg)
        raise TestDataError(error_msg)
    
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        error_msg = f"Missing required fields: {missing_fields}"  # 异常消息使用英文
        logger.error(error_msg)
        raise TestDataError(error_msg)
    
    logger.info("Test data validation passed")  # 日志使用英文
    return True


def create_test_user(session, user_data=None):
    """
    创建测试用户
    
    参数:
        session: 数据库会话
        user_data: 用户数据，如果为None则使用默认数据
        
    返回:
        User: 创建的测试用户
    """
    from coding.tornado.modules.auth.models import User
    from coding.tornado.utils.password_utils import hash_password
    
    if user_data is None:
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": hash_password("Test@123456"),
            "full_name": "测试用户",
            "is_active": True
        }
    
    user = User(**user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user


def create_test_tenant(session, tenant_data=None, created_by=None):
    """
    创建测试租户
    
    参数:
        session: 数据库会话
        tenant_data: 租户数据，如果为None则使用默认数据
        created_by: 创建者用户ID
        
    返回:
        Tenant: 创建的测试租户
    """
    from coding.tornado.modules.tenant.models import Tenant
    
    if tenant_data is None:
        tenant_data = {
            "name": "测试租户",
            "slug": "test-tenant",
            "description": "这是一个测试租户",
            "contact_email": "contact@test.com",
            "created_by": created_by
        }
    
    tenant = Tenant(**tenant_data)
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    
    return tenant
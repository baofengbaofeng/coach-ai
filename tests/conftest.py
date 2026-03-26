"""
测试配置和共享fixtures

注意：所有注释必须使用中文（规范要求）
所有日志和异常消息必须使用英文（规范要求）
"""

import pytest
import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 配置测试日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
"""
pytest配置文件，用于设置测试环境和共享fixtures。
"""
import os
import sys
import django
from pathlib import Path
from typing import Dict, Any, Generator

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "apps"))

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")

# 初始化Django
django.setup()

import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

# 导入项目模型
User = get_user_model()


@pytest.fixture(scope="session")
def django_db_setup():
    """
    设置测试数据库。
    这个fixture确保测试使用独立的测试数据库。
    """
    from django.conf import settings
    
    # 确保使用测试数据库配置
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'TEST': {
            'NAME': ':memory:',
        }
    }


@pytest.fixture
def test_client() -> Client:
    """
    提供Django测试客户端。
    """
    return Client()


@pytest.fixture
def api_client() -> APIClient:
    """
    提供DRF API测试客户端。
    """
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client: APIClient, test_user: User) -> APIClient:
    """
    提供已认证的API客户端。
    """
    # 这里可以根据实际认证方式调整
    # 例如使用JWT token或session认证
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def test_user() -> User:
    """
    创建测试用户。
    """
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpassword123",
        first_name="Test",
        last_name="User"
    )
    return user


@pytest.fixture
def admin_user() -> User:
    """
    创建管理员用户。
    """
    admin = User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpassword123"
    )
    return admin


@pytest.fixture
def user_token(test_user: User) -> str:
    """
    为用户创建认证token。
    """
    token, created = Token.objects.get_or_create(user=test_user)
    return token.key


@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """
    提供样本用户数据。
    """
    return {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword123",
        "first_name": "New",
        "last_name": "User",
        "age": 25,
        "gender": "male",
        "fitness_level": "intermediate"
    }


@pytest.fixture
def sample_task_data() -> Dict[str, Any]:
    """
    提供样本任务数据。
    """
    return {
        "title": "完成30分钟有氧运动",
        "description": "跑步、游泳或骑自行车30分钟",
        "task_type": "exercise",
        "difficulty": "medium",
        "estimated_time": 30,
        "points": 50,
        "is_recurring": False,
        "recurrence_pattern": None
    }


@pytest.fixture
def sample_achievement_data() -> Dict[str, Any]:
    """
    提供样本成就数据。
    """
    return {
        "name": "运动新手",
        "description": "完成第一次运动任务",
        "achievement_type": "exercise",
        "points_required": 100,
        "badge_image": "badges/beginner.png",
        "is_secret": False
    }


@pytest.fixture
def sample_ai_recommendation_request() -> Dict[str, Any]:
    """
    提供样本AI推荐请求数据。
    """
    return {
        "user_id": 1,
        "preferences": {
            "exercise_types": ["running", "swimming"],
            "duration_range": [20, 60],
            "difficulty": "medium"
        },
        "context": {
            "time_of_day": "morning",
            "weather": "sunny",
            "available_equipment": ["none"]
        }
    }


@pytest.fixture
def sample_ai_analysis_request() -> Dict[str, Any]:
    """
    提供样本AI分析请求数据。
    """
    return {
        "user_id": 1,
        "data": {
            "recent_activities": [
                {"type": "running", "duration": 30, "intensity": "medium"},
                {"type": "strength", "duration": 45, "intensity": "high"}
            ],
            "health_metrics": {
                "heart_rate": 72,
                "sleep_hours": 7.5,
                "stress_level": "medium"
            }
        },
        "analysis_type": "performance_trend"
    }


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    为所有测试启用数据库访问。
    这个fixture会自动应用到所有测试。
    """
    pass


@pytest.fixture
def cleanup_test_data():
    """
    清理测试数据的fixture。
    使用yield模式在测试后清理。
    """
    # 测试前状态
    yield
    # 测试后清理
    from django.core.management import call_command
    call_command('flush', '--noinput')


def pytest_configure():
    """
    pytest配置钩子。
    用于设置测试环境。
    """
    # 确保测试环境使用正确的设置
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.test'
    
    # 创建测试报告目录
    reports_dir = project_root / "tests" / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # 创建覆盖率报告目录
    coverage_dir = reports_dir / "coverage"
    coverage_dir.mkdir(exist_ok=True)


def pytest_sessionfinish(session, exitstatus):
    """
    pytest会话结束钩子。
    用于生成测试报告。
    """
    # 这里可以添加测试报告生成逻辑
    pass


# 测试配置常量
class TestConfig:
    """测试配置常量"""
    API_BASE_URL = "/api/v1"
    AI_SERVICE_URL = f"{API_BASE_URL}/ai"
    
    # 测试超时设置（秒）
    API_TIMEOUT = 10
    DATABASE_TIMEOUT = 5
    
    # 性能测试参数
    LOAD_TEST_USERS = 100
    LOAD_TEST_DURATION = 60  # 秒
    
    # 安全测试参数
    SECURITY_TEST_ITERATIONS = 1000
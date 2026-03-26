"""
API集成测试模块。
测试所有RESTful API端点的功能和集成。
"""
import json
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.tasks.models import Task, TaskAssignment
from apps.achievements.models import Achievement


class TestHealthCheckAPI:
    """健康检查API测试类"""
    
    def test_health_check_endpoint(self, api_client):
        """测试健康检查端点"""
        url = reverse('health-check')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'healthy'
        assert 'database' in response.data
        assert 'cache' in response.data
        assert 'timestamp' in response.data
    
    def test_health_check_database_status(self, api_client):
        """测试健康检查中的数据库状态"""
        url = reverse('health-check')
        response = api_client.get(url)
        
        assert response.data['database']['status'] == 'connected'
        assert 'response_time' in response.data['database']


class TestSystemStatusAPI:
    """系统状态API测试类"""
    
    def test_system_status_endpoint(self, api_client):
        """测试系统状态端点"""
        url = reverse('system-status')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'status' in response.data
        assert 'version' in response.data
        assert 'environment' in response.data
        assert 'uptime' in response.data
    
    def test_system_status_version_info(self, api_client):
        """测试系统状态中的版本信息"""
        url = reverse('system-status')
        response = api_client.get(url)
        
        assert 'api_version' in response.data
        assert 'django_version' in response.data
        assert 'python_version' in response.data


class TestAPIInfoEndpoint:
    """API信息端点测试类"""
    
    def test_api_info_endpoint(self, api_client):
        """测试API信息端点"""
        url = reverse('api-info')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'name' in response.data
        assert 'description' in response.data
        assert 'version' in response.data
        assert 'endpoints' in response.data
    
    def test_api_info_endpoints_list(self, api_client):
        """测试API信息中的端点列表"""
        url = reverse('api-info')
        response = api_client.get(url)
        
        endpoints = response.data['endpoints']
        assert isinstance(endpoints, list)
        
        # 检查至少包含一些核心端点
        endpoint_urls = [endpoint['url'] for endpoint in endpoints]
        assert any('health' in url for url in endpoint_urls)
        assert any('status' in url for url in endpoint_urls)


class TestAIStatusAPI:
    """AI服务状态API测试类"""
    
    def test_ai_status_endpoint(self, api_client):
        """测试AI服务状态端点"""
        url = reverse('ai-status')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'service_status' in response.data
        assert 'model_version' in response.data
        assert 'last_updated' in response.data
    
    def test_ai_status_authentication(self, authenticated_api_client):
        """测试AI服务状态认证"""
        url = reverse('ai-status')
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK


class TestAIRecommendationAPI:
    """AI推荐API测试类"""
    
    def test_ai_recommendation_endpoint(self, authenticated_api_client, sample_ai_recommendation_request):
        """测试AI推荐端点"""
        url = reverse('ai-recommendation')
        response = authenticated_api_client.post(
            url,
            data=json.dumps(sample_ai_recommendation_request),
            content_type='application/json'
        )
        
        # 注意：根据实际实现，可能返回200或201
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        
        if response.status_code == status.HTTP_200_OK:
            assert 'recommendations' in response.data
            assert 'confidence_score' in response.data
            assert 'generated_at' in response.data
    
    def test_ai_recommendation_validation(self, authenticated_api_client):
        """测试AI推荐数据验证"""
        url = reverse('ai-recommendation')
        
        # 测试无效数据
        invalid_data = {
            "user_id": "not_a_number",  # 应该是数字
            "preferences": {}
        }
        
        response = authenticated_api_client.post(
            url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        # 应该返回验证错误
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data or 'detail' in response.data
    
    def test_ai_recommendation_authentication_required(self, api_client, sample_ai_recommendation_request):
        """测试AI推荐需要认证"""
        url = reverse('ai-recommendation')
        response = api_client.post(
            url,
            data=json.dumps(sample_ai_recommendation_request),
            content_type='application/json'
        )
        
        # 根据实际认证配置，可能返回401或403
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN
        ]


class TestAIAnalysisAPI:
    """AI分析API测试类"""
    
    def test_ai_analysis_endpoint(self, authenticated_api_client, sample_ai_analysis_request):
        """测试AI分析端点"""
        url = reverse('ai-analysis')
        response = authenticated_api_client.post(
            url,
            data=json.dumps(sample_ai_analysis_request),
            content_type='application/json'
        )
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        
        if response.status_code == status.HTTP_200_OK:
            assert 'analysis_results' in response.data
            assert 'insights' in response.data
            assert 'recommendations' in response.data
            assert 'analysis_type' in response.data
    
    def test_ai_analysis_different_types(self, authenticated_api_client):
        """测试不同类型的AI分析"""
        url = reverse('ai-analysis')
        
        analysis_types = [
            "performance_trend",
            "health_assessment",
            "goal_progress",
            "risk_assessment"
        ]
        
        for analysis_type in analysis_types:
            request_data = {
                "user_id": 1,
                "data": {
                    "recent_activities": [
                        {"type": "running", "duration": 30}
                    ]
                },
                "analysis_type": analysis_type
            }
            
            response = authenticated_api_client.post(
                url,
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            # 所有分析类型都应该被接受
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]


class TestAIPredictionAPI:
    """AI预测API测试类"""
    
    def test_ai_prediction_endpoint(self, authenticated_api_client):
        """测试AI预测端点"""
        url = reverse('ai-prediction')
        
        prediction_request = {
            "user_id": 1,
            "prediction_type": "completion_rate",
            "input_data": {
                "historical_completion": [0.8, 0.85, 0.9],
                "current_motivation": "high",
                "time_available": 60
            },
            "time_horizon": 7  # 7天预测
        }
        
        response = authenticated_api_client.post(
            url,
            data=json.dumps(prediction_request),
            content_type='application/json'
        )
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        
        if response.status_code == status.HTTP_200_OK:
            assert 'predictions' in response.data
            assert 'confidence_intervals' in response.data
            assert 'prediction_type' in response.data
            assert 'generated_at' in response.data


class TestUserAuthenticationAPI:
    """用户认证API测试类"""
    
    def test_user_registration(self, api_client, sample_user_data):
        """测试用户注册"""
        url = reverse('user-register')
        response = api_client.post(
            url,
            data=json.dumps(sample_user_data),
            content_type='application/json'
        )
        
        # 注册成功应该返回201
        assert response.status_code == status.HTTP_201_CREATED
        
        # 验证返回的数据
        assert 'id' in response.data
        assert 'username' in response.data
        assert 'email' in response.data
        assert 'token' in response.data or 'access_token' in response.data
        
        # 验证用户确实被创建
        user_exists = User.objects.filter(username=sample_user_data['username']).exists()
        assert user_exists
    
    def test_user_login(self, api_client, test_user):
        """测试用户登录"""
        url = reverse('user-login')
        
        login_data = {
            "username": test_user.username,
            "password": "testpassword123"  # 使用创建用户时的密码
        }
        
        response = api_client.post(
            url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data or 'access_token' in response.data
        assert 'user' in response.data
    
    def test_user_login_invalid_credentials(self, api_client, test_user):
        """测试使用无效凭证登录"""
        url = reverse('user-login')
        
        invalid_login_data = {
            "username": test_user.username,
            "password": "wrongpassword"
        }
        
        response = api_client.post(
            url,
            data=json.dumps(invalid_login_data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_user_profile_get(self, authenticated_api_client, test_user):
        """测试获取用户资料"""
        url = reverse('user-profile', kwargs={'user_id': test_user.id})
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == test_user.id
        assert response.data['username'] == test_user.username
        assert response.data['email'] == test_user.email


class TestTaskManagementAPI:
    """任务管理API测试类"""
    
    def test_create_task(self, authenticated_api_client):
        """测试创建任务"""
        url = reverse('task-list')
        
        task_data = {
            "title": "API测试任务",
            "description": "通过API创建的任务",
            "task_type": "exercise",
            "difficulty": "medium",
            "estimated_time": 45,
            "points": 75
        }
        
        response = authenticated_api_client.post(
            url,
            data=json.dumps(task_data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == task_data['title']
        assert response.data['task_type'] == task_data['task_type']
        
        # 验证任务确实被创建
        task_exists = Task.objects.filter(title=task_data['title']).exists()
        assert task_exists
    
    def test_list_tasks(self, authenticated_api_client):
        """测试列出任务"""
        # 先创建一些测试任务
        for i in range(3):
            Task.objects.create(
                title=f"测试任务 {i}",
                task_type="exercise",
                difficulty="easy",
                estimated_time=30,
                points=50
            )
        
        url = reverse('task-list')
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or isinstance(response.data, list)
        
        # 检查返回的任务数量
        tasks = response.data.get('results', response.data)
        assert len(tasks) >= 3
    
    def test_assign_task_to_user(self, authenticated_api_client, test_user):
        """测试给用户分配任务"""
        # 先创建一个任务
        task = Task.objects.create(
            title="待分配任务",
            task_type="exercise"
        )
        
        url = reverse('task-assign')
        
        assignment_data = {
            "user_id": test_user.id,
            "task_id": task.id,
            "due_date": "2026-03-31T23:59:59Z"
        }
        
        response = authenticated_api_client.post(
            url,
            data=json.dumps(assignment_data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # 验证任务分配确实被创建
        assignment_exists = TaskAssignment.objects.filter(
            user=test_user,
            task=task
        ).exists()
        assert assignment_exists


class TestAchievementAPI:
    """成就API测试类"""
    
    def test_list_achievements(self, authenticated_api_client):
        """测试列出成就"""
        # 先创建一些测试成就
        for i in range(3):
            Achievement.objects.create(
                name=f"测试成就 {i}",
                achievement_type="exercise",
                points_required=(i + 1) * 100
            )
        
        url = reverse('achievement-list')
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or isinstance(response.data, list)
        
        # 检查返回的成就数量
        achievements = response.data.get('results', response.data)
        assert len(achievements) >= 3
    
    def test_get_achievement_detail(self, authenticated_api_client):
        """测试获取成就详情"""
        # 创建一个成就
        achievement = Achievement.objects.create(
            name="详细测试成就",
            description="这是一个测试成就",
            achievement_type="knowledge",
            points_required=500
        )
        
        url = reverse('achievement-detail', kwargs={'pk': achievement.id})
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == achievement.id
        assert response.data['name'] == achievement.name
        assert response.data['description'] == achievement.description


class TestErrorHandling:
    """错误处理测试类"""
    
    def test_404_not_found(self, api_client):
        """测试404错误处理"""
        url = '/api/v1/nonexistent-endpoint/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'detail' in response.data or 'error' in response.data
    
    def test_method_not_allowed(self, api_client):
        """测试方法不允许错误"""
        url = reverse('health-check')
        response = api_client.post(url)  # 健康检查应该只支持GET
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_invalid_json(self, authenticated_api_client):
        """测试无效JSON请求"""
        url = reverse('ai-recommendation')
        response = authenticated_api_client.post(
            url,
            data="这不是有效的JSON",
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# 运行所有API测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
成就系统数据分析集成测试

测试成就系统的数据分析功能
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from coding.tornado.core.application import make_app
from coding.database.models import User


class TestAchievementAnalyticsAPI:
    """测试成就数据分析API"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        return make_app()
    
    @pytest.fixture
    def test_client(self, app, http_server, http_client):
        """创建测试客户端"""
        return http_client
    
    @pytest.fixture
    def auth_headers(self):
        """创建认证头"""
        return {
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json"
        }
    
    @pytest.fixture
    def mock_current_user(self):
        """模拟当前用户"""
        user = MagicMock(spec=User)
        user.id = "test_user_id"
        user.username = "testuser"
        user.email = "test@example.com"
        user.is_active.return_value = True
        user.is_blocked.return_value = False
        user.is_admin.return_value = False
        return user
    
    @pytest.fixture
    def mock_admin_user(self):
        """模拟管理员用户"""
        user = MagicMock(spec=User)
        user.id = "admin_user_id"
        user.username = "admin"
        user.email = "admin@example.com"
        user.is_active.return_value = True
        user.is_blocked.return_value = False
        user.is_admin.return_value = True
        return user
    
    def test_get_user_achievement_analytics(self, test_client, auth_headers, mock_current_user):
        """测试获取用户成就分析数据"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            with patch('coding.tornado.modules.achievements.analytics_handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟用户查询
                mock_user = MagicMock(spec=User)
                mock_user.id = "test_user_id"
                mock_user.username = "testuser"
                mock_db.query.return_value.filter.return_value.first.return_value = mock_user
                
                # 模拟分析服务
                with patch('coding.tornado.modules.achievements.analytics_handlers.AchievementAnalyticsService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    # 模拟分析数据
                    analytics_data = {
                        "user_id": "test_user_id",
                        "username": "testuser",
                        "stats": {
                            "total_achievements": 50,
                            "unlocked_achievements": 15,
                            "in_progress_achievements": 10,
                            "locked_achievements": 25,
                            "completion_rate": 30.0,
                            "activity_score": 65.5
                        },
                        "type_distribution": {
                            "exercise": {"total": 20, "unlocked": 8, "in_progress": 5, "locked": 7},
                            "task": {"total": 15, "unlocked": 4, "in_progress": 3, "locked": 8}
                        },
                        "calculated_at": datetime.now().isoformat()
                    }
                    
                    mock_service.get_user_achievement_analytics.return_value = analytics_data
                    
                    # 发送请求
                    response = test_client.fetch(
                        "/api/v1/achievement-analytics/user",
                        method="GET",
                        headers=auth_headers
                    )
                    
                    assert response.code == 200
                    
                    data = json.loads(response.body)
                    assert data["success"] == True
                    assert data["data"]["analytics"]["user_id"] == "test_user_id"
                    assert data["data"]["analytics"]["stats"]["completion_rate"] == 30.0
    
    def test_get_user_achievement_analytics_with_user_id(self, test_client, auth_headers, mock_current_user):
        """测试获取指定用户的成就分析数据"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            with patch('coding.tornado.modules.achievements.analytics_handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟用户查询
                mock_user = MagicMock(spec=User)
                mock_user.id = "other_user_id"
                mock_user.username = "otheruser"
                mock_db.query.return_value.filter.return_value.first.return_value = mock_user
                
                # 模拟分析服务
                with patch('coding.tornado.modules.achievements.analytics_handlers.AchievementAnalyticsService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    # 模拟分析数据
                    analytics_data = {
                        "user_id": "other_user_id",
                        "username": "otheruser",
                        "stats": {"total_achievements": 30, "completion_rate": 40.0}
                    }
                    
                    mock_service.get_user_achievement_analytics.return_value = analytics_data
                    
                    # 发送请求（当前用户尝试访问其他用户数据，应该被拒绝）
                    response = test_client.fetch(
                        "/api/v1/achievement-analytics/user/other_user_id",
                        method="GET",
                        headers=auth_headers
                    )
                    
                    # 非管理员用户不能访问其他用户数据
                    assert response.code == 403
    
    def test_get_system_achievement_analytics_as_admin(self, test_client, auth_headers, mock_admin_user):
        """测试管理员获取系统成就分析数据"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_admin_user
            
            with patch('coding.tornado.modules.achievements.analytics_handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟分析服务
                with patch('coding.tornado.modules.achievements.analytics_handlers.AchievementAnalyticsService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    # 模拟系统分析数据
                    system_analytics = {
                        "system_stats": {
                            "total_achievements": 100,
                            "active_achievements": 80,
                            "total_user_achievements": 5000,
                            "completed_user_achievements": 1500,
                            "avg_completion_rate": 30.0
                        },
                        "calculated_at": datetime.now().isoformat()
                    }
                    
                    mock_service.get_system_achievement_analytics.return_value = system_analytics
                    
                    # 发送请求
                    response = test_client.fetch(
                        "/api/v1/achievement-analytics/system",
                        method="GET",
                        headers=auth_headers
                    )
                    
                    assert response.code == 200
                    
                    data = json.loads(response.body)
                    assert data["success"] == True
                    assert data["data"]["analytics"]["system_stats"]["total_achievements"] == 100
                    assert data["data"]["analytics"]["system_stats"]["avg_completion_rate"] == 30.0
    
    def test_get_system_achievement_analytics_as_non_admin(self, test_client, auth_headers, mock_current_user):
        """测试非管理员用户获取系统成就分析数据（应该被拒绝）"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            # 发送请求
            response = test_client.fetch(
                "/api/v1/achievement-analytics/system",
                method="GET",
                headers=auth_headers
            )
            
            # 非管理员用户不能访问系统分析数据
            assert response.code == 403
    
    def test_get_achievement_performance_metrics(self, test_client, auth_headers, mock_admin_user):
        """测试获取成就系统性能指标"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_admin_user
            
            with patch('coding.tornado.modules.achievements.analytics_handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟分析服务
                with patch('coding.tornado.modules.achievements.analytics_handlers.AchievementAnalyticsService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    # 模拟性能指标数据
                    performance_metrics = {
                        "response_times": {
                            "achievement_unlock": {
                                "avg_response_time_ms": 150,
                                "success_rate": 99.8
                            }
                        },
                        "calculated_at": datetime.now().isoformat()
                    }
                    
                    mock_service.get_achievement_performance_metrics.return_value = performance_metrics
                    
                    # 发送请求
                    response = test_client.fetch(
                        "/api/v1/achievement-analytics/performance",
                        method="GET",
                        headers=auth_headers
                    )
                    
                    assert response.code == 200
                    
                    data = json.loads(response.body)
                    assert data["success"] == True
                    assert data["data"]["metrics"]["response_times"]["achievement_unlock"]["avg_response_time_ms"] == 150
    
    def test_get_achievement_recommendations(self, test_client, auth_headers, mock_current_user):
        """测试获取成就推荐"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            with patch('coding.tornado.modules.achievements.analytics_handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟分析服务
                with patch('coding.tornado.modules.achievements.analytics_handlers.AchievementAnalyticsService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    # 模拟推荐数据
                    recommendations = [
                        {
                            "type": "continue_progress",
                            "achievement_id": "achievement_1",
                            "achievement_name": "继续完成俯卧撑",
                            "description": "继续完成此成就，当前进度 60%",
                            "priority": "high",
                            "reason": "您已经开始了这个成就，继续完成它吧！"
                        },
                        {
                            "type": "interest_based",
                            "achievement_id": "achievement_2",
                            "achievement_name": "深蹲挑战",
                            "description": "完成30次深蹲",
                            "priority": "medium",
                            "reason": "基于您对'力量训练'的兴趣推荐"
                        }
                    ]
                    
                    mock_service.generate_achievement_recommendations.return_value = recommendations
                    
                    # 发送请求
                    response = test_client.fetch(
                        "/api/v1/achievement-analytics/recommendations",
                        method="GET",
                        headers=auth_headers
                    )
                    
                    assert response.code == 200
                    
                    data = json.loads(response.body)
                    assert data["success"] == True
                    assert len(data["data"]["recommendations"]) == 2
                    assert data["data"]["recommendations"][0]["type"] == "continue_progress"
    
    def test_get_achievement_trend_analysis(self, test_client, auth_headers, mock_admin_user):
        """测试获取成就趋势分析"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_admin_user
            
            with patch('coding.tornado.modules.achievements.analytics_handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟分析服务
                with patch('coding.tornado.modules.achievements.analytics_handlers.AchievementAnalyticsService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    # 模拟趋势数据
                    trend_data = [
                        {"date": "2024-01-01", "count": 10},
                        {"date": "2024-01-02", "count": 15},
                        {"date": "2024-01-03", "count": 12}
                    ]
                    
                    mock_service._get_system_unlock_trend.return_value = trend_data
                    
                    # 发送请求
                    response = test_client.fetch(
                        "/api/v1/achievement-analytics/trend?type=unlock_trend&days=30",
                        method="GET",
                        headers=auth_headers
                    )
                    
                    assert response.code == 200
                    
                    data = json.loads(response.body)
                    assert data["success"] == True
                    assert data["data"]["analysis_type"] == "unlock_trend"
                    assert len(data["data"]["data"]) == 3
    
    def test_get_popular_achievements(self, test_client, auth_headers, mock_current_user):
        """测试获取热门成就"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            with patch('coding.tornado.modules.achievements.analytics_handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟热门成就数据
                popular_achievements = [
                    {
                        "id": "achievement_1",
                        "name": "俯卧撑新手",
                        "description": "完成10次俯卧撑",
                        "type": "exercise",
                        "difficulty": "easy",
                        "unlock_count": 150,
                        "reward_points": 100
                    },
                    {
                        "id": "achievement_2",
                        "name": "任务达人",
                        "description": "完成10个任务",
                        "type": "task",
                        "difficulty": "medium",
                        "unlock_count": 120,
                        "reward_points": 200
                    }
                ]
                
                # 模拟查询
                mock_achievement1 = MagicMock()
                mock_achievement1.id = "achievement_1"
                mock_achievement1.name = "俯卧撑新手"
                mock_achievement1.description = "完成10次俯卧撑"
                mock_achievement1.achievement_type = "exercise"
                mock_achievement1.difficulty = "easy"
                mock_achievement1.reward_points = 100
                
                mock_achievement2 = MagicMock()
                mock_achievement2.id = "achievement_2"
                mock_achievement2.name = "任务达人"
                mock_achievement2.description = "完成10个任务"
                mock_achievement2.achievement_type = "task"
                mock_achievement2.difficulty = "medium"
                mock_achievement2.reward_points = 200
                
                mock_query = MagicMock()
                mock_query.join.return_value = mock_query
                mock_query.filter.return_value = mock_query
                mock_query.group_by.return_value = mock_query
                mock_query.order_by.return_value = mock_query
                mock_query.limit.return_value = [
                    (mock_achievement1, 150),
                    (mock_achievement2, 120)
                ]
                
                mock_db.query.return_value = mock_query
                
                # 发送请求
                response = test_client.fetch(
                    "/api/v1/achievement-analytics/popular?limit=5&days=30",
                    method="GET",
                    headers=auth_headers
                )
                
                assert response.code == 200
                
                data = json.loads(response.body)
                assert data["success"] == True
                assert len(data["data"]["popular_achievements"]) == 2
                assert data["data"]["popular_achievements"][0]["unlock_count"] == 150
    
    def test_get_difficult_achievements(self, test_client, auth_headers, mock_current_user):
        """测试获取困难成就"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            with patch('coding.tornado.modules.achievements.analytics_handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟分析服务
                with patch('coding.tornado.modules.achievements.analytics_handlers.AchievementAnalyticsService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    # 模拟困难成就数据
                    difficult_achievements = [
                        {
                            "id": "achievement_hard_1",
                            "name": "马拉松训练",
                            "description": "连续跑步30天",
                            "type": "exercise",
                            "difficulty": "hard",
                            "total_assignments": 50,
                            "completed_count": 5,
                            "completion_rate": 10.0
                        },
                        {
                            "id": "achievement_hard_2",
                            "name": "专家级任务",
                            "description": "完成50个高难度任务",
                            "type": "task",
                            "difficulty": "legendary",
                            "total_assignments": 30,
                            "completed_count": 3,
                            "completion_rate": 10.0
                        }
                    ]
                    
                    mock_service._get_difficult_achievements.return_value = difficult_achievements
                    
                    # 发送请求
                    response = test_client.fetch(
                        "/api/v1/achievement-analytics/difficult?limit=5&min_attempts=10",
                        method="GET",
                        headers=auth_headers
                    )
                    
                    assert response.code == 200
                    
                    data = json.loads(response.body)
                    assert data["success"] == True
                    assert len(data["data"]["difficult_achievements"]) == 2
                    assert data["data"]["difficult_achievements"][0]["completion_rate"] == 10.0
    
    def test_compare_achievement_data(self, test_client, auth_headers, mock_current_user):
        """测试对比成就数据"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            with patch('coding.tornado.modules.achievements.analytics_handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟分析服务
                with patch('coding.tornado.modules.achievements.analytics_handlers.AchievementAnalyticsService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    # 模拟分析数据
                    analytics_data_1 = {
                        "user_id": "test_user_id",
                        "stats": {
                            "total_achievements": 50,
                            "completion_rate": 30.0,
                            "activity_score": 65.5
                        }
                    }
                    
                    analytics_data_2 = {
                        "user_id": "other_user_id",
                        "stats": {
                            "total_achievements": 40,
                            "completion_rate": 40.0,
                            "activity_score": 55.0
                        }
                    }
                    
                    mock_service.get_user_achievement_analytics.side_effect = [
                        analytics_data_1,
                        analytics_data_2
                    ]
                    
                    # 发送请求（包含当前用户自己）
                    compare_data = {
                        "user_ids": ["test_user_id", "other_user_id"]
                    }
                    
                    response = test_client.fetch(
                        "/api/v1/achievement-analytics/compare",
                        method="POST",
                        headers=auth_headers,
                        body=json.dumps(compare_data)
                    )
                    
                    assert response.code == 200
                    
                    data = json.loads(response.body)
                    assert data["success"] == True
                    assert len(data["data"]["comparison"]) == 2
                    assert data["data"]["metrics"]["total_users"] == 2
                    assert data["data"]["metrics"]["completion_rate_avg"] == 35.0
    
    def test_compare_achievement_data_without_current_user(self, test_client, auth_headers, mock_current_user):
        """测试对比成就数据（不包含当前用户，应该被拒绝）"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            # 发送请求（不包含当前用户）
            compare_data = {
                "user_ids": ["user_1", "user_2"]  # 不包含当前用户
            }
            
            response = test_client.fetch(
                "/api/v1/achievement-analytics/compare",
                method="POST",
                headers=auth_headers,
                body=json.dumps(compare_data)
            )
            
            # 非管理员用户不能对比不包含自己的数据
            assert response.code == 403
    
    def test_compare_achievement_data_as_admin(self, test_client, auth_headers, mock_admin_user):
        """测试管理员对比成就数据"""
        with patch('coding.tornado.core.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_admin_user
            
            with patch('coding.tornado.modules.achievements.analytics_handlers.get_db_session') as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db
                
                # 模拟分析服务
                with patch('coding.tornado.modules.achievements.analytics_handlers.AchievementAnalyticsService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    # 模拟分析数据
                    analytics_data_1 = {
                        "user_id": "user_1",
                        "stats": {"total_achievements": 50, "completion_rate": 30.0}
                    }
                    
                    analytics_data_2 = {
                        "user_id": "user_2",
                        "stats": {"total_achievements": 40, "completion_rate": 40.0}
                    }
                    
                    analytics_data_3 = {
                        "user_id": "user_3",
                        "stats": {"total_achievements": 60, "completion_rate": 50.0}
                    }
                    
                    mock_service.get_user_achievement_analytics.side_effect = [
                        analytics_data_1,
                        analytics_data_2,
                        analytics_data_3
                    ]
                    
                    # 发送请求（管理员可以对比任意用户）
                    compare_data = {
                        "user_ids": ["user_1", "user_2", "user_3"]
                    }
                    
                    response = test_client.fetch(
                        "/api/v1/achievement-analytics/compare",
                        method="POST",
                        headers=auth_headers,
                        body=json.dumps(compare_data)
                    )
                    
                    assert response.code == 200
                    
                    data = json.loads(response.body)
                    assert data["success"] == True
                    assert len(data["data"]["comparison"]) == 3
                    assert data["data"]["metrics"]["total_users"] == 3
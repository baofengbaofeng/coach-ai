"""
运动API集成测试
"""

import pytest
import json
from datetime import datetime, date, timedelta


class TestExerciseTypeAPI:
    """运动类型API测试"""
    
    def test_get_exercise_types(self, test_client, auth_headers):
        """测试获取运动类型列表"""
        response = test_client.get('/api/exercise/types', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert 'total' in data
        assert isinstance(data['items'], list)
    
    def test_get_exercise_type_by_id(self, test_client, auth_headers, create_exercise_type):
        """测试根据ID获取运动类型"""
        exercise_type = create_exercise_type
        
        response = test_client.get(f'/api/exercise/types/{exercise_type.id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == exercise_type.id
        assert data['name_zh'] == exercise_type.name_zh
        assert data['code'] == exercise_type.code
    
    def test_create_exercise_type(self, test_client, admin_headers):
        """测试创建运动类型（需要管理员权限）"""
        exercise_data = {
            'name_zh': '测试创建运动',
            'name_en': 'Test Create Exercise',
            'code': 'test_create_exercise',
            'category': 'strength',
            'difficulty': 'beginner',
            'description': '测试创建运动的描述',
            'standard_repetitions': 15,
            'standard_sets': 3,
            'calorie_factor': 0.1
        }
        
        response = test_client.post(
            '/api/exercise/types',
            json=exercise_data,
            headers=admin_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data['name_zh'] == exercise_data['name_zh']
        assert data['code'] == exercise_data['code']
        assert data['is_active'] == True
    
    def test_search_exercise_types(self, test_client, auth_headers, create_exercise_type):
        """测试搜索运动类型"""
        response = test_client.get(
            '/api/exercise/types?search=俯卧撑',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        
        # 检查是否包含俯卧撑
        items = data['items']
        pushup_found = any(item['name_zh'] == '俯卧撑' for item in items)
        assert pushup_found == True
    
    def test_filter_exercise_types_by_category(self, test_client, auth_headers):
        """测试按分类过滤运动类型"""
        response = test_client.get(
            '/api/exercise/types?category=strength',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data['items']:
            for item in data['items']:
                assert item['category'] == 'strength'


class TestExerciseRecordAPI:
    """运动记录API测试"""
    
    def test_get_exercise_records(self, test_client, auth_headers):
        """测试获取运动记录列表"""
        response = test_client.get('/api/exercise/records', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert 'total' in data
        assert isinstance(data['items'], list)
    
    def test_create_exercise_record(self, test_client, auth_headers, create_exercise_type):
        """测试创建运动记录"""
        exercise_type = create_exercise_type
        
        record_data = {
            'exercise_type_id': exercise_type.id,
            'start_time': datetime.utcnow().isoformat(),
            'end_time': (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            'total_repetitions': 20,
            'total_sets': 3,
            'user_weight_kg': 70.0,
            'status': 'completed'
        }
        
        response = test_client.post(
            '/api/exercise/records',
            json=record_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data['exercise_type_id'] == exercise_type.id
        assert data['total_repetitions'] == 20
        assert data['status'] == 'completed'
    
    def test_start_exercise(self, test_client, auth_headers, create_exercise_type):
        """测试开始运动"""
        exercise_type = create_exercise_type
        
        start_data = {
            'exercise_type_id': exercise_type.id,
            'user_weight_kg': 70.0
        }
        
        response = test_client.post(
            '/api/exercise/start',
            json=start_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert 'exercise_record_id' in data
        assert data['status'] == 'in_progress'
        assert 'start_time' in data
    
    def test_complete_exercise(self, test_client, auth_headers, create_exercise_record):
        """测试完成运动"""
        exercise_record = create_exercise_record
        
        # 先确保记录状态是in_progress
        exercise_record.status = 'in_progress'
        
        complete_data = {
            'total_repetitions': 25,
            'total_sets': 3,
            'notes': '测试完成运动'
        }
        
        response = test_client.post(
            f'/api/exercise/complete/{exercise_record.id}',
            json=complete_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['exercise_record_id'] == exercise_record.id
        assert data['status'] == 'completed'
        assert data['total_repetitions'] == 25
    
    def test_filter_exercise_records_by_date(self, test_client, auth_headers, create_exercise_record):
        """测试按日期过滤运动记录"""
        today = date.today()
        start_date = today.isoformat()
        end_date = today.isoformat()
        
        response = test_client.get(
            f'/api/exercise/records?start_date={start_date}&end_date={end_date}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data


class TestExerciseStatisticsAPI:
    """运动统计API测试"""
    
    def test_get_exercise_statistics(self, test_client, auth_headers, create_exercise_record):
        """测试获取运动统计数据"""
        response = test_client.get('/api/exercise/statistics', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert 'user_id' in data
        assert 'period' in data
        assert 'total_exercises' in data
        assert 'total_duration_minutes' in data
        assert 'total_calories' in data
    
    def test_get_statistics_with_period(self, test_client, auth_headers):
        """测试按周期获取统计数据"""
        response = test_client.get(
            '/api/exercise/statistics?period=weekly',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['period'] == 'weekly'
    
    def test_get_statistics_with_custom_date_range(self, test_client, auth_headers):
        """测试按自定义日期范围获取统计数据"""
        start_date = (date.today() - timedelta(days=7)).isoformat()
        end_date = date.today().isoformat()
        
        response = test_client.get(
            f'/api/exercise/statistics?start_date={start_date}&end_date={end_date}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'start_date' in data
        assert 'end_date' in data


class TestExercisePlanAPI:
    """运动计划API测试"""
    
    def test_get_exercise_plans(self, test_client, auth_headers):
        """测试获取运动计划"""
        response = test_client.get('/api/exercise/plans', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert 'todays_plans' in data
        assert 'total' in data
        assert isinstance(data['todays_plans'], list)
    
    def test_create_exercise_plan(self, test_client, auth_headers, create_exercise_type):
        """测试创建运动计划"""
        exercise_type = create_exercise_type
        
        plan_data = {
            'exercise_type_id': exercise_type.id,
            'plan_name': '每日训练计划',
            'plan_type': 'daily',
            'start_date': date.today().isoformat(),
            'target_repetitions': 30,
            'target_sets': 3,
            'weekly_frequency': 7,
            'enable_reminder': True,
            'reminder_minutes_before': 15
        }
        
        response = test_client.post(
            '/api/exercise/plans',
            json=plan_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data['plan_name'] == '每日训练计划'
        assert data['plan_type'] == 'daily'
        assert data['status'] == 'active'
        assert data['is_active'] == True


class TestCameraDeviceAPI:
    """摄像头设备API测试"""
    
    def test_get_camera_devices(self, test_client, auth_headers):
        """测试获取摄像头设备列表"""
        response = test_client.get('/api/exercise/cameras', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert 'total' in data
        assert isinstance(data['items'], list)
    
    def test_register_camera_device(self, test_client, admin_headers):
        """测试注册摄像头设备（需要管理员权限）"""
        camera_data = {
            'device_name': '测试摄像头',
            'serial_number': 'TEST-CAM-API-001',
            'device_type': 'webcam',
            'brand': 'TestBrand',
            'model': 'TestModel',
            'resolution_width': 1920,
            'resolution_height': 1080,
            'frame_rate': 30,
            'video_codec': 'h264'
        }
        
        response = test_client.post(
            '/api/exercise/cameras',
            json=camera_data,
            headers=admin_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data['device_name'] == '测试摄像头'
        assert data['serial_number'] == 'TEST-CAM-API-001'
        assert data['is_enabled'] == True


class TestPoseAnalysisAPI:
    """姿势分析API测试"""
    
    def test_analyze_pose(self, test_client, auth_headers, create_exercise_record):
        """测试分析姿势"""
        exercise_record = create_exercise_record
        
        # 模拟姿势关键点数据
        landmarks = [
            {'x': 0.5, 'y': 0.5, 'z': 0.0, 'visibility': 0.9},
            {'x': 0.6, 'y': 0.6, 'z': 0.0, 'visibility': 0.8},
            # 添加更多关键点...
        ]
        
        analysis_data = {
            'landmarks': landmarks
        }
        
        response = test_client.post(
            f'/api/exercise/analyze/{exercise_record.id}',
            json=analysis_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'exercise_record_id' in data
        assert 'posture_score' in data
        assert 'landmarks' in data
        assert 'feedback_messages' in data


class TestWebRTCAPI:
    """WebRTC API测试"""
    
    def test_webrtc_signaling(self, test_client, auth_headers, create_camera_device):
        """测试WebRTC信令交换"""
        camera_device = create_camera_device
        
        # 连接摄像头
        camera_device.connect()
        
        signaling_data = {
            'type': 'offer',
            'sdp': 'fake-sdp-offer'
        }
        
        response = test_client.post(
            f'/api/exercise/webrtc/{camera_device.id}/signal',
            json=signaling_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'type' in data
        assert 'camera_device_id' in data
        assert data['camera_device_id'] == camera_device.id


# 测试夹具
@pytest.fixture
def create_exercise_type(db_session):
    """创建测试运动类型夹具"""
    from coding.database.models import ExerciseType
    
    exercise_type = ExerciseType(
        name_zh='俯卧撑',
        name_en='Push-up',
        code='pushup',
        category='strength',
        difficulty='beginner',
        description='经典的上肢力量训练',
        standard_repetitions=15,
        standard_sets=3,
        calorie_factor=0.12
    )
    
    db_session.add(exercise_type)
    db_session.commit()
    return exercise_type


@pytest.fixture
def create_exercise_record(db_session, test_user, create_exercise_type):
    """创建测试运动记录夹具"""
    from coding.database.models import ExerciseRecord
    
    exercise_record = ExerciseRecord(
        user_id=test_user.id,
        exercise_type_id=create_exercise_type.id,
        start_time=datetime.utcnow() - timedelta(minutes=10),
        end_time=datetime.utcnow() - timedelta(minutes=5),
        status='completed',
        total_repetitions=20,
        total_sets=3,
        user_weight_kg=70.0
    )
    
    db_session.add(exercise_record)
    db_session.commit()
    return exercise_record


@pytest.fixture
def create_camera_device(db_session):
    """创建测试摄像头设备夹具"""
    from coding.database.models import CameraDevice
    
    camera_device = CameraDevice(
        device_name='测试摄像头',
        serial_number='TEST-CAM-FIXTURE-001',
        device_type='webcam',
        brand='TestBrand',
        model='TestModel'
    )
    
    db_session.add(camera_device)
    db_session.commit()
    return camera_device
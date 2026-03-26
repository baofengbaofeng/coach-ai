"""
运动模型单元测试
"""

import pytest
from datetime import datetime, date, timedelta
import json

from coachai_code.database.models import (
    ExerciseType, ExerciseRecord, ExercisePlan, CameraDevice,
    User, Tenant
)


class TestExerciseType:
    """运动类型模型测试"""
    
    def test_create_exercise_type(self, db_session):
        """测试创建运动类型"""
        exercise_type = ExerciseType(
            name_zh="测试运动",
            name_en="Test Exercise",
            code="test_exercise",
            category="strength",
            difficulty="beginner",
            description="测试描述",
            standard_repetitions=10,
            standard_sets=3,
            calorie_factor=0.1
        )
        
        db_session.add(exercise_type)
        db_session.commit()
        
        assert exercise_type.id is not None
        assert exercise_type.name_zh == "测试运动"
        assert exercise_type.code == "test_exercise"
        assert exercise_type.is_active == True
        assert exercise_type.requires_equipment == False
    
    def test_exercise_type_to_dict(self, db_session):
        """测试运动类型转换为字典"""
        exercise_type = ExerciseType(
            name_zh="俯卧撑",
            name_en="Push-up",
            code="pushup",
            category="strength",
            difficulty="beginner",
            target_muscles=json.dumps(["chest", "triceps", "shoulders"])
        )
        
        db_session.add(exercise_type)
        db_session.commit()
        
        data = exercise_type.to_dict()
        
        assert data['name_zh'] == "俯卧撑"
        assert data['code'] == "pushup"
        assert isinstance(data['target_muscles'], list)
        assert "chest" in data['target_muscles']
    
    def test_calculate_calories_duration(self, db_session):
        """测试按时长计算卡路里"""
        exercise_type = ExerciseType(
            name_zh="平板支撑",
            name_en="Plank",
            code="plank",
            standard_duration=60,  # 60秒
            calorie_factor=0.05
        )
        
        calories = exercise_type.calculate_calories(70, duration_minutes=2)  # 2分钟
        assert calories > 0
    
    def test_calculate_calories_repetitions(self, db_session):
        """测试按次数计算卡路里"""
        exercise_type = ExerciseType(
            name_zh="俯卧撑",
            name_en="Push-up",
            code="pushup",
            standard_repetitions=10,
            calorie_factor=0.12
        )
        
        calories = exercise_type.calculate_calories(70, repetitions=20)
        assert calories > 0


class TestExerciseRecord:
    """运动记录模型测试"""
    
    def test_create_exercise_record(self, db_session, test_user):
        """测试创建运动记录"""
        exercise_type = ExerciseType(
            name_zh="测试运动",
            name_en="Test Exercise",
            code="test_exercise"
        )
        
        db_session.add(exercise_type)
        db_session.commit()
        
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=5)
        
        exercise_record = ExerciseRecord(
            user_id=test_user.id,
            exercise_type_id=exercise_type.id,
            start_time=start_time,
            end_time=end_time,
            status="completed",
            total_repetitions=20,
            total_sets=3,
            user_weight_kg=70.0
        )
        
        db_session.add(exercise_record)
        db_session.commit()
        
        assert exercise_record.id is not None
        assert exercise_record.user_id == test_user.id
        assert exercise_record.status == "completed"
        assert exercise_record.duration_minutes == 5.0
    
    def test_start_exercise(self, db_session, test_user):
        """测试开始运动"""
        exercise_type = ExerciseType(
            name_zh="测试运动",
            name_en="Test Exercise",
            code="test_exercise"
        )
        
        db_session.add(exercise_type)
        db_session.commit()
        
        exercise_record = ExerciseRecord(
            user_id=test_user.id,
            exercise_type_id=exercise_type.id
        )
        
        exercise_record.start_exercise(user_weight_kg=70.0)
        
        assert exercise_record.status == "in_progress"
        assert exercise_record.start_time is not None
        assert exercise_record.user_weight_kg == 70.0
    
    def test_complete_exercise(self, db_session, test_user):
        """测试完成运动"""
        exercise_type = ExerciseType(
            name_zh="测试运动",
            name_en="Test Exercise",
            code="test_exercise",
            standard_repetitions=10,
            calorie_factor=0.1
        )
        
        db_session.add(exercise_type)
        db_session.commit()
        
        exercise_record = ExerciseRecord(
            user_id=test_user.id,
            exercise_type_id=exercise_type.id
        )
        
        exercise_record.start_exercise(user_weight_kg=70.0)
        exercise_record.complete_exercise(total_repetitions=30, total_sets=3)
        
        assert exercise_record.status == "completed"
        assert exercise_record.end_time is not None
        assert exercise_record.total_repetitions == 30
        assert exercise_record.total_sets == 3
        assert exercise_record.estimated_calories > 0
    
    def test_exercise_record_to_dict(self, db_session, test_user):
        """测试运动记录转换为字典"""
        exercise_type = ExerciseType(
            name_zh="测试运动",
            name_en="Test Exercise",
            code="test_exercise"
        )
        
        db_session.add(exercise_type)
        db_session.commit()
        
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=5)
        
        exercise_record = ExerciseRecord(
            user_id=test_user.id,
            exercise_type_id=exercise_type.id,
            start_time=start_time,
            end_time=end_time,
            status="completed",
            sensor_data=json.dumps({"heart_rate": 120, "steps": 100})
        )
        
        db_session.add(exercise_record)
        db_session.commit()
        
        data = exercise_record.to_dict()
        
        assert data['user_id'] == test_user.id
        assert 'duration_minutes' in data
        assert data['duration_minutes'] == 5.0
        assert isinstance(data['sensor_data'], dict)
        assert data['sensor_data']['heart_rate'] == 120


class TestExercisePlan:
    """运动计划模型测试"""
    
    def test_create_exercise_plan(self, db_session, test_user):
        """测试创建运动计划"""
        exercise_type = ExerciseType(
            name_zh="测试运动",
            name_en="Test Exercise",
            code="test_exercise"
        )
        
        db_session.add(exercise_type)
        db_session.commit()
        
        start_date = date.today()
        
        exercise_plan = ExercisePlan(
            user_id=test_user.id,
            exercise_type_id=exercise_type.id,
            plan_name="每日训练计划",
            plan_type="daily",
            start_date=start_date,
            target_repetitions=30,
            target_sets=3,
            weekly_frequency=7
        )
        
        db_session.add(exercise_plan)
        db_session.commit()
        
        assert exercise_plan.id is not None
        assert exercise_plan.plan_name == "每日训练计划"
        assert exercise_plan.status == "active"
        assert exercise_plan.is_active == True
    
    def test_daily_plan_is_due_today(self, db_session, test_user):
        """测试每日计划今天是否到期"""
        exercise_type = ExerciseType(
            name_zh="测试运动",
            name_en="Test Exercise",
            code="test_exercise"
        )
        
        db_session.add(exercise_type)
        db_session.commit()
        
        exercise_plan = ExercisePlan(
            user_id=test_user.id,
            exercise_type_id=exercise_type.id,
            plan_name="每日计划",
            plan_type="daily",
            start_date=date.today() - timedelta(days=1),
            status="active"
        )
        
        assert exercise_plan.is_due_today == True
    
    def test_weekly_plan_is_due_today(self, db_session, test_user):
        """测试每周计划今天是否到期"""
        exercise_type = ExerciseType(
            name_zh="测试运动",
            name_en="Test Exercise",
            code="test_exercise"
        )
        
        db_session.add(exercise_type)
        db_session.commit()
        
        # 设置每周一、三、五执行
        weekly_days = json.dumps([1, 3, 5])  # Monday, Wednesday, Friday
        
        exercise_plan = ExercisePlan(
            user_id=test_user.id,
            exercise_type_id=exercise_type.id,
            plan_name="每周计划",
            plan_type="weekly",
            start_date=date.today() - timedelta(days=7),
            weekly_days=weekly_days,
            status="active"
        )
        
        # 根据今天是周几来判断是否到期
        current_day = datetime.utcnow().weekday() + 1  # Monday=1, Sunday=7
        expected_due = current_day in [1, 3, 5]
        
        assert exercise_plan.is_due_today == expected_due
    
    def test_mark_plan_completed(self, db_session, test_user):
        """测试标记计划为已完成"""
        exercise_type = ExerciseType(
            name_zh="测试运动",
            name_en="Test Exercise",
            code="test_exercise"
        )
        
        db_session.add(exercise_type)
        db_session.commit()
        
        exercise_plan = ExercisePlan(
            user_id=test_user.id,
            exercise_type_id=exercise_type.id,
            plan_name="测试计划",
            plan_type="daily",
            start_date=date.today(),
            status="active"
        )
        
        db_session.add(exercise_plan)
        db_session.commit()
        
        exercise_plan.mark_completed(actual_repetitions=25, actual_sets=3)
        
        assert exercise_plan.completed_count == 1
        assert exercise_plan.last_completed_at == date.today()
        assert exercise_plan.streak_days == 1
        assert exercise_plan.progress > 0


class TestCameraDevice:
    """摄像头设备模型测试"""
    
    def test_create_camera_device(self, db_session):
        """测试创建摄像头设备"""
        camera_device = CameraDevice(
            device_name="测试摄像头",
            serial_number="TEST-CAM-001",
            device_type="webcam",
            brand="TestBrand",
            model="TestModel",
            resolution_width=1920,
            resolution_height=1080,
            frame_rate=30
        )
        
        db_session.add(camera_device)
        db_session.commit()
        
        assert camera_device.id is not None
        assert camera_device.device_name == "测试摄像头"
        assert camera_device.serial_number == "TEST-CAM-001"
        assert camera_device.resolution == "1920x1080"
        assert camera_device.is_enabled == True
        assert camera_device.connection_status == "offline"
    
    def test_camera_connect_disconnect(self, db_session):
        """测试摄像头连接和断开"""
        camera_device = CameraDevice(
            device_name="测试摄像头",
            serial_number="TEST-CAM-002",
            device_type="webcam"
        )
        
        db_session.add(camera_device)
        db_session.commit()
        
        # 连接摄像头
        camera_device.connect(ip_address="192.168.1.100", port=8080)
        
        assert camera_device.connection_status == "online"
        assert camera_device.ip_address == "192.168.1.100"
        assert camera_device.port == 8080
        assert camera_device.last_connected_at is not None
        
        # 断开摄像头
        camera_device.disconnect()
        
        assert camera_device.connection_status == "offline"
        assert camera_device.last_disconnected_at is not None
        assert camera_device.is_in_use == False
    
    def test_camera_start_use(self, db_session, test_user):
        """测试开始使用摄像头"""
        camera_device = CameraDevice(
            device_name="测试摄像头",
            serial_number="TEST-CAM-003",
            device_type="webcam"
        )
        
        db_session.add(camera_device)
        db_session.commit()
        
        # 先连接摄像头
        camera_device.connect()
        
        # 开始使用
        success = camera_device.start_use(test_user.id)
        
        assert success == True
        assert camera_device.is_in_use == True
        assert camera_device.current_user_id == test_user.id
        assert camera_device.current_use_started_at is not None
    
    def test_camera_get_webrtc_config(self, db_session):
        """测试获取WebRTC配置"""
        camera_device = CameraDevice(
            device_name="测试摄像头",
            serial_number="TEST-CAM-004",
            device_type="webcam",
            webrtc_peer_id="peer-123",
            webrtc_signaling_url="ws://localhost:8080/signal",
            resolution_width=1280,
            resolution_height=720,
            frame_rate=25,
            video_codec="h264",
            has_audio=True,
            audio_codec="opus"
        )
        
        config = camera_device.get_webrtc_config()
        
        assert config['peer_id'] == "peer-123"
        assert config['signaling_url'] == "ws://localhost:8080/signal"
        assert config['video']['width'] == 1280
        assert config['video']['height'] == 720
        assert config['video']['frameRate'] == 25
        assert config['video']['codec'] == "h264"
        assert 'audio' in config
        assert config['audio']['codec'] == "opus"
    
    def test_camera_to_dict(self, db_session):
        """测试摄像头设备转换为字典"""
        calibration_data = {
            "intrinsic": [[1000, 0, 640], [0, 1000, 360], [0, 0, 1]],
            "distortion": [0.1, -0.2, 0.001, 0.002, 0.0]
        }
        
        camera_device = CameraDevice(
            device_name="测试摄像头",
            serial_number="TEST-CAM-005",
            device_type="webcam",
            calibration_data=json.dumps(calibration_data)
        )
        
        db_session.add(camera_device)
        db_session.commit()
        
        data = camera_device.to_dict()
        
        assert data['device_name'] == "测试摄像头"
        assert data['resolution'] == "1920x1080"
        assert data['is_available'] == False  # 默认离线，不可用
        assert isinstance(data['calibration_data'], dict)
        assert 'intrinsic' in data['calibration_data']
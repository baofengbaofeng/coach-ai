"""
运动管理序列化器测试模块，测试运动记录、运动计划、运动分析等序列化器。
按照豆包AI助手最佳实践：使用Django REST Framework测试工具。
"""
from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from apps.exercise.models import ExerciseAnalysis, ExercisePlan, ExerciseRecord
from apps.exercise.serializers import (
    ExerciseAnalysisSerializer,
    ExercisePlanProgressSerializer,
    ExercisePlanSerializer,
    ExerciseRecordCreateSerializer,
    ExerciseRecordSerializer,
)
from core.constants import ExerciseType


User = get_user_model()


# ==================== 运动记录序列化器测试 ====================
class ExerciseRecordSerializerTest(TestCase):
    """
    运动记录序列化器测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.user = User.objects.create_user(
            username="serializeruser",
            email="serializer@example.com",
            password="testpass123",
        )
        
        self.factory = APIRequestFactory()
        
        self.exercise_record = ExerciseRecord.objects.create(
            title="序列化器测试",
            description="测试序列化器功能",
            user=self.user,
            exercise_type=ExerciseType.RUNNING,
            duration_seconds=1800,
            repetitions=0,
            calories_burned=Decimal("300.00"),
            started_at=timezone.now() - datetime.timedelta(hours=1),
            ended_at=timezone.now() - datetime.timedelta(minutes=30),
        )
        
        self.valid_data: Dict[str, Any] = {
            "title": "有效的运动记录",
            "description": "这是一个有效的测试记录",
            "exercise_type": ExerciseType.JUMP_ROPE,
            "duration_seconds": 1200,
            "repetitions": 500,
            "calories_burned": Decimal("200.00"),
            "started_at": timezone.now() - datetime.timedelta(minutes=30),
        }
    
    def test_exercise_record_serializer_valid_data(self) -> None:
        """测试有效数据的序列化。"""
        serializer = ExerciseRecordSerializer(instance=self.exercise_record)
        data = serializer.data
        
        self.assertEqual(data["title"], "序列化器测试")
        self.assertEqual(data["exercise_type"], ExerciseType.RUNNING)
        self.assertEqual(data["duration_seconds"], 1800)
        self.assertEqual(data["calories_burned"], "300.00")
        self.assertIn("exercise_type_display", data)
        self.assertIn("duration_minutes", data)
        self.assertIn("calories_per_minute", data)
        self.assertIn("progress_percentage", data)
        self.assertIn("is_completed", data)
    
    def test_exercise_record_serializer_computed_fields(self) -> None:
        """测试计算字段。"""
        serializer = ExerciseRecordSerializer(instance=self.exercise_record)
        data = serializer.data
        
        # 检查计算字段
        self.assertEqual(data["duration_minutes"], 30.0)
        self.assertAlmostEqual(data["calories_per_minute"], 10.0, places=2)
        self.assertEqual(data["progress_percentage"], 100.0)
        self.assertTrue(data["is_completed"])
    
    def test_exercise_record_serializer_validation(self) -> None:
        """测试序列化器验证。"""
        # 测试标题验证
        invalid_data = self.valid_data.copy()
        invalid_data["title"] = ""  # 空标题
        
        serializer = ExerciseRecordSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)
        
        # 测试时长验证
        invalid_data = self.valid_data.copy()
        invalid_data["duration_seconds"] = 0  # 小于最小值
        
        serializer = ExerciseRecordSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("duration_seconds", serializer.errors)
        
        # 测试开始时间验证
        invalid_data = self.valid_data.copy()
        invalid_data["started_at"] = timezone.now() + datetime.timedelta(hours=1)  # 未来时间
        
        serializer = ExerciseRecordSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("started_at", serializer.errors)
    
    def test_exercise_record_serializer_create(self) -> None:
        """测试序列化器创建功能。"""
        request = self.factory.post("/api/exercise/records/")
        request.user = self.user
        
        serializer = ExerciseRecordCreateSerializer(
            data=self.valid_data,
            context={"request": request},
        )
        
        self.assertTrue(serializer.is_valid())
        exercise_record = serializer.save()
        
        self.assertEqual(exercise_record.title, "有效的运动记录")
        self.assertEqual(exercise_record.user, self.user)
        self.assertEqual(exercise_record.exercise_type, ExerciseType.JUMP_ROPE)
        self.assertIsNotNone(exercise_record.ended_at)  # 应该自动计算结束时间
    
    def test_exercise_record_serializer_update(self) -> None:
        """测试序列化器更新功能。"""
        update_data = {
            "title": "更新后的标题",
            "description": "更新后的描述",
            "duration_seconds": 1500,
        }
        
        serializer = ExerciseRecordSerializer(
            instance=self.exercise_record,
            data=update_data,
            partial=True,
        )
        
        self.assertTrue(serializer.is_valid())
        updated_record = serializer.save()
        
        self.assertEqual(updated_record.title, "更新后的标题")
        self.assertEqual(updated_record.description, "更新后的描述")
        self.assertEqual(updated_record.duration_seconds, 1500)
    
    def test_exercise_record_serializer_auto_end_time(self) -> None:
        """测试自动计算结束时间。"""
        data = self.valid_data.copy()
        data["ended_at"] = None  # 不提供结束时间
        
        serializer = ExerciseRecordSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # 验证逻辑应该自动计算结束时间
        validated_data = serializer.validated_data
        self.assertIn("ended_at", validated_data)
        
        expected_end_time = data["started_at"] + datetime.timedelta(seconds=data["duration_seconds"])
        self.assertEqual(validated_data["ended_at"], expected_end_time)


# ==================== 运动计划序列化器测试 ====================
class ExercisePlanSerializerTest(TestCase):
    """
    运动计划序列化器测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.user = User.objects.create_user(
            username="planuser",
            email="plan@example.com",
            password="testpass123",
        )
        
        self.exercise_plan = ExercisePlan.objects.create(
            name="测试计划",
            description="测试序列化器",
            user=self.user,
            target_duration_minutes=30,
            target_repetitions=100,
            target_calories=Decimal("200.00"),
            frequency_per_week=5,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + datetime.timedelta(days=30),
            is_active=True,
            completed_count=10,
            success_rate=Decimal("66.67"),
        )
        
        self.valid_data: Dict[str, Any] = {
            "name": "新的运动计划",
            "description": "这是一个新的测试计划",
            "target_duration_minutes": 45,
            "target_repetitions": 200,
            "target_calories": Decimal("300.00"),
            "frequency_per_week": 4,
            "start_date": timezone.now().date(),
            "end_date": timezone.now().date() + datetime.timedelta(days=60),
        }
    
    def test_exercise_plan_serializer_valid_data(self) -> None:
        """测试有效数据的序列化。"""
        serializer = ExercisePlanSerializer(instance=self.exercise_plan)
        data = serializer.data
        
        self.assertEqual(data["name"], "测试计划")
        self.assertEqual(data["target_duration_minutes"], 30)
        self.assertEqual(data["frequency_per_week"], 5)
        self.assertEqual(data["success_rate"], "66.67")
        self.assertIn("remaining_days", data)
        self.assertIn("progress_percentage", data)
        self.assertIn("expected_completion_count", data)
        self.assertIn("can_add_exercise", data)
        self.assertIn("status_display", data)
    
    def test_exercise_plan_serializer_computed_fields(self) -> None:
        """测试计算字段。"""
        serializer = ExercisePlanSerializer(instance=self.exercise_plan)
        data = serializer.data
        
        # 检查计算字段
        self.assertIsNotNone(data["remaining_days"])
        self.assertGreaterEqual(data["progress_percentage"], 0.0)
        self.assertLessEqual(data["progress_percentage"], 100.0)
        self.assertGreater(data["expected_completion_count"], 0)
        self.assertTrue(data["can_add_exercise"])
        self.assertEqual(data["status_display"], "激活")
    
    def test_exercise_plan_serializer_validation(self) -> None:
        """测试序列化器验证。"""
        # 测试名称验证
        invalid_data = self.valid_data.copy()
        invalid_data["name"] = ""  # 空名称
        
        serializer = ExercisePlanSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)
        
        # 测试频率验证
        invalid_data = self.valid_data.copy()
        invalid_data["frequency_per_week"] = 0  # 小于最小值
        
        serializer = ExercisePlanSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("frequency_per_week", serializer.errors)
        
        # 测试日期关系验证
        invalid_data = self.valid_data.copy()
        invalid_data["end_date"] = invalid_data["start_date"]  # 结束日期等于开始日期
        
        serializer = ExercisePlanSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("end_date", serializer.errors)
    
    def test_exercise_plan_serializer_create(self) -> None:
        """测试序列化器创建功能。"""
        request = self.factory.post("/api/exercise/plans/")
        request.user = self.user
        
        serializer = ExercisePlanSerializer(
            data=self.valid_data,
            context={"request": request},
        )
        
        self.assertTrue(serializer.is_valid())
        exercise_plan = serializer.save()
        
        self.assertEqual(exercise_plan.name, "新的运动计划")
        self.assertEqual(exercise_plan.user, self.user)
        self.assertEqual(exercise_plan.target_duration_minutes, 45)
        self.assertEqual(exercise_plan.frequency_per_week, 4)
        self.assertTrue(exercise_plan.is_active)  # 默认激活
    
    def test_exercise_plan_serializer_update(self) -> None:
        """测试序列化器更新功能。"""
        update_data = {
            "name": "更新后的计划",
            "description": "更新后的描述",
            "frequency_per_week": 3,
            "is_active": False,
        }
        
        serializer = ExercisePlanSerializer(
            instance=self.exercise_plan,
            data=update_data,
            partial=True,
        )
        
        self.assertTrue(serializer.is_valid())
        updated_plan = serializer.save()
        
        self.assertEqual(updated_plan.name, "更新后的计划")
        self.assertEqual(updated_plan.description, "更新后的描述")
        self.assertEqual(updated_plan.frequency_per_week, 3)
        self.assertFalse(updated_plan.is_active)


# ==================== 运动分析序列化器测试 ====================
class ExerciseAnalysisSerializerTest(TestCase):
    """
    运动分析序列化器测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.user = User.objects.create_user(
            username="analysisuser",
            email="analysis@example.com",
            password="testpass123",
        )
        
        today = timezone.now().date()
        self.exercise_analysis = ExerciseAnalysis.objects.create(
            user=self.user,
            analysis_period="weekly",
            period_start=today - datetime.timedelta(days=6),
            period_end=today,
            total_duration_minutes=Decimal("180.00"),
            total_calories=Decimal("1200.00"),
            total_repetitions=500,
            exercise_count=6,
            average_duration_minutes=Decimal("30.00"),
            average_calories=Decimal("200.00"),
            consistency_rate=Decimal("85.50"),
            improvement_rate=Decimal("10.20"),
            strengths="优势分析",
            weaknesses="待改进点",
            recommendations="建议内容",
        )
        
        self.valid_data: Dict[str, Any] = {
            "analysis_period": "monthly",
            "period_start": today.replace(day=1),
            "period_end": today,
            "total_duration_minutes": Decimal("720.00"),
            "total_calories": Decimal("4800.00"),
            "total_repetitions": 2000,
            "exercise_count": 24,
            "consistency_rate": Decimal("80.00"),
            "improvement_rate": Decimal("15.00"),
            "strengths": "新的优势分析",
            "weaknesses": "新的待改进点",
            "recommendations": "新的建议",
        }
    
    def test_exercise_analysis_serializer_valid_data(self) -> None:
        """测试有效数据的序列化。"""
        serializer = ExerciseAnalysisSerializer(instance=self.exercise_analysis)
        data = serializer.data
        
        self.assertEqual(data["analysis_period"], "weekly")
        self.assertEqual(data["total_duration_minutes"], "180.00")
        self.assertEqual(data["exercise_count"], 6)
        self.assertEqual(data["consistency_rate"], "85.50")
        self.assertIn("analysis_period_display", data)
        self.assertIn("period_days", data)
        self.assertIn("daily_average_duration", data)
        self.assertIn("daily_average_calories", data)
        self.assertIn("exercise_frequency", data)
        self.assertIn("health_score", data)
    
    def test_exercise_analysis_serializer_computed_fields(self) -> None:
        """测试计算字段。"""
        serializer = ExerciseAnalysisSerializer(instance=self.exercise_analysis)
        data = serializer.data
        
        # 检查计算字段
        self.assertEqual(data["period_days"], 7)
        self.assertAlmostEqual(data["daily_average_duration"], 180.00 / 7, places=2)
        self.assertAlmostEqual(data["daily_average_calories"], 1200.00 / 7, places=2)
        self.assertAlmostEqual(data["exercise_frequency"], 6 / 7, places=2)
        self.assertGreaterEqual(data["health_score"], 0.0)
        self.assertLessEqual(data["health_score"], 100.0)
    
    def test_exercise_analysis_serializer_validation(self) -> None:
        """测试序列化器验证。"""
        # 测试分析周期验证
        invalid_data = self.valid_data.copy()
        invalid_data["analysis_period"] = "invalid"  # 无效的周期
        
        serializer = ExerciseAnalysisSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("analysis_period", serializer.errors)
        
        # 测试坚持率验证
        invalid_data = self.valid_data.copy()
        invalid_data["consistency_rate"] = Decimal("150.00")  # 大于100
        
        serializer = ExerciseAnalysisSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("consistency_rate", serializer.errors)
        
        # 测试日期关系验证
        invalid_data = self.valid_data.copy()
        invalid_data["period_end"] = invalid_data["period_start"]  # 结束日期等于开始日期
        
        serializer = ExerciseAnalysisSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("period_end", serializer.errors)
    
    def test_exercise_analysis_serializer_create(self) -> None:
        """测试序列化器创建功能。"""
        request = self.factory.post("/api/exercise/analyses/")
        request.user = self.user
        
        serializer = ExerciseAnalysisSerializer(
            data=self.valid_data,
            context={"request": request},
        )
        
        self.assertTrue(serializer.is_valid())
        exercise_analysis = serializer.save()
        
        self.assertEqual(exercise_analysis.user, self.user)
        self.assertEqual(exercise_analysis.analysis_period, "monthly")
        self.assertEqual(exercise_analysis.total_duration_minutes, Decimal("720.00"))
        self.assertEqual(exercise_analysis.exercise_count, 24)
        
        # 检查是否自动计算了平均值
        self.assertEqual(exercise_analysis.average_duration_minutes, Decimal("30.00"))
        self.assertEqual(exercise_analysis.average_calories, Decimal("200.00"))
    
    def test_exercise_analysis_serializer_update(self) -> None:
        """测试序列化器更新功能。"""
        update_data = {
            "strengths": "更新后的优势",
            "weaknesses": "更新后的改进点",
            "recommendations": "更新后的建议",
            "consistency_rate": Decimal("90.00"),
        }
        
        serializer = ExerciseAnalysisSerializer(
            instance=self.exercise_analysis,
            data=update_data,
            partial=True,
        )
        
        self.assertTrue(serializer.is_valid())
        updated_analysis = serializer.save()
        
        self.assertEqual(updated_analysis.strengths, "更新后的优势")
        self.assertEqual(updated_analysis.weaknesses, "更新后的改进点")
        self.assertEqual(updated_analysis.recommendations, "更新后的建议")
        self.assertEqual(updated_analysis.consistency_rate, Decimal("90.00"))
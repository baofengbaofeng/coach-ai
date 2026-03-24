"""
运动管理API测试脚本，测试运动记录、运动计划、运动分析等API接口。
"""
from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.exercise.models import ExerciseAnalysis, ExercisePlan, ExerciseRecord
from core.constants import ExerciseType


User = get_user_model()


class ExerciseAPITest(TestCase):
    """
    运动管理API测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.client = APIClient()
        
        # 创建测试用户
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        
        # 认证用户
        self.client.force_authenticate(user=self.user)
        
        # 创建测试数据
        self.exercise_record = ExerciseRecord.objects.create(
            title="API测试记录",
            description="测试API接口",
            user=self.user,
            exercise_type=ExerciseType.RUNNING,
            duration_seconds=1800,
            calories_burned=Decimal("300.00"),
            started_at=timezone.now() - datetime.timedelta(hours=1),
            ended_at=timezone.now() - datetime.timedelta(minutes=30),
        )
        
        self.exercise_plan = ExercisePlan.objects.create(
            name="API测试计划",
            description="测试API接口",
            user=self.user,
            target_duration_minutes=30,
            frequency_per_week=5,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + datetime.timedelta(days=30),
        )
        
        today = timezone.now().date()
        self.exercise_analysis = ExerciseAnalysis.objects.create(
            user=self.user,
            analysis_period="weekly",
            period_start=today - datetime.timedelta(days=6),
            period_end=today,
            total_duration_minutes=Decimal("180.00"),
            total_calories=Decimal("1200.00"),
            exercise_count=6,
        )
    
    def test_exercise_record_list_api(self) -> None:
        """测试运动记录列表API。"""
        response = self.client.get("/api/v1/exercise/records/")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertGreater(len(response.data["results"]), 0)
        
        # 检查返回的数据结构
        record_data = response.data["results"][0]
        self.assertEqual(record_data["title"], "API测试记录")
        self.assertEqual(record_data["exercise_type"], ExerciseType.RUNNING)
        self.assertIn("duration_minutes", record_data)
        self.assertIn("calories_per_minute", record_data)
        self.assertIn("progress_percentage", record_data)
        self.assertIn("is_completed", record_data)
    
    def test_exercise_record_detail_api(self) -> None:
        """测试运动记录详情API。"""
        response = self.client.get(f"/api/v1/exercise/records/{self.exercise_record.id}/")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "API测试记录")
        self.assertEqual(response.data["exercise_type"], ExerciseType.RUNNING)
        self.assertEqual(response.data["duration_seconds"], 1800)
        self.assertEqual(response.data["calories_burned"], "300.00")
    
    def test_exercise_record_create_api(self) -> None:
        """测试运动记录创建API。"""
        data: Dict[str, Any] = {
            "title": "新创建的运动记录",
            "description": "通过API创建",
            "exercise_type": ExerciseType.JUMP_ROPE,
            "duration_seconds": 1200,
            "repetitions": 500,
            "calories_burned": Decimal("200.00"),
            "started_at": timezone.now() - datetime.timedelta(minutes=30),
        }
        
        response = self.client.post("/api/v1/exercise/records/", data, format="json")
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "新创建的运动记录")
        self.assertEqual(response.data["exercise_type"], ExerciseType.JUMP_ROPE)
        self.assertEqual(response.data["duration_seconds"], 1200)
        
        # 验证记录已创建
        record_id = response.data["id"]
        self.assertTrue(ExerciseRecord.objects.filter(id=record_id).exists())
    
    def test_exercise_record_update_api(self) -> None:
        """测试运动记录更新API。"""
        data = {
            "title": "更新后的标题",
            "description": "更新后的描述",
            "duration_seconds": 1500,
        }
        
        response = self.client.patch(
            f"/api/v1/exercise/records/{self.exercise_record.id}/",
            data,
            format="json",
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "更新后的标题")
        self.assertEqual(response.data["description"], "更新后的描述")
        self.assertEqual(response.data["duration_seconds"], 1500)
        
        # 验证数据库已更新
        updated_record = ExerciseRecord.objects.get(id=self.exercise_record.id)
        self.assertEqual(updated_record.title, "更新后的标题")
        self.assertEqual(updated_record.duration_seconds, 1500)
    
    def test_exercise_record_delete_api(self) -> None:
        """测试运动记录删除API。"""
        response = self.client.delete(f"/api/v1/exercise/records/{self.exercise_record.id}/")
        
        self.assertEqual(response.status_code, 204)
        
        # 验证记录已删除
        self.assertFalse(ExerciseRecord.objects.filter(id=self.exercise_record.id).exists())
    
    def test_exercise_record_statistics_api(self) -> None:
        """测试运动记录统计API。"""
        response = self.client.get("/api/v1/exercise/records/statistics/")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_count", response.data)
        self.assertIn("total_duration_minutes", response.data)
        self.assertIn("total_calories", response.data)
        self.assertIn("type_statistics", response.data)
        self.assertIn("daily_trend", response.data)
    
    def test_exercise_record_summary_api(self) -> None:
        """测试运动记录摘要API。"""
        response = self.client.get("/api/v1/exercise/records/summary/")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("today", response.data)
        self.assertIn("this_week", response.data)
        self.assertIn("this_month", response.data)
        self.assertIn("favorite_exercise_type", response.data)
        self.assertIn("user", response.data)
    
    def test_exercise_plan_list_api(self) -> None:
        """测试运动计划列表API。"""
        response = self.client.get("/api/v1/exercise/plans/")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertGreater(len(response.data["results"]), 0)
        
        # 检查返回的数据结构
        plan_data = response.data["results"][0]
        self.assertEqual(plan_data["name"], "API测试计划")
        self.assertIn("remaining_days", plan_data)
        self.assertIn("progress_percentage", plan_data)
        self.assertIn("expected_completion_count", plan_data)
        self.assertIn("can_add_exercise", plan_data)
        self.assertIn("status_display", plan_data)
    
    def test_exercise_plan_detail_api(self) -> None:
        """测试运动计划详情API。"""
        response = self.client.get(f"/api/v1/exercise/plans/{self.exercise_plan.id}/")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "API测试计划")
        self.assertEqual(response.data["target_duration_minutes"], 30)
        self.assertEqual(response.data["frequency_per_week"], 5)
    
    def test_exercise_plan_create_api(self) -> None:
        """测试运动计划创建API。"""
        data: Dict[str, Any] = {
            "name": "新创建的运动计划",
            "description": "通过API创建",
            "target_duration_minutes": 45,
            "target_repetitions": 200,
            "target_calories": Decimal("300.00"),
            "frequency_per_week": 4,
            "start_date": timezone.now().date(),
            "end_date": timezone.now().date() + datetime.timedelta(days=60),
        }
        
        response = self.client.post("/api/v1/exercise/plans/", data, format="json")
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "新创建的运动计划")
        self.assertEqual(response.data["target_duration_minutes"], 45)
        self.assertEqual(response.data["frequency_per_week"], 4)
        self.assertTrue(response.data["is_active"])  # 默认激活
        
        # 验证计划已创建
        plan_id = response.data["id"]
        self.assertTrue(ExercisePlan.objects.filter(id=plan_id).exists())
    
    def test_exercise_plan_update_progress_api(self) -> None:
        """测试运动计划进度更新API。"""
        data = {
            "completed_count": 15,
        }
        
        response = self.client.post(
            f"/api/v1/exercise/plans/{self.exercise_plan.id}/update_progress/",
            data,
            format="json",
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["completed_count"], 15)
        self.assertGreater(float(response.data["success_rate"]), 0)
        
        # 验证数据库已更新
        updated_plan = ExercisePlan.objects.get(id=self.exercise_plan.id)
        self.assertEqual(updated_plan.completed_count, 15)
    
    def test_exercise_plan_activate_api(self) -> None:
        """测试运动计划激活API。"""
        # 先停用计划
        self.exercise_plan.is_active = False
        self.exercise_plan.save()
        
        response = self.client.post(f"/api/v1/exercise/plans/{self.exercise_plan.id}/activate/")
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_active"])
        
        # 验证数据库已更新
        updated_plan = ExercisePlan.objects.get(id=self.exercise_plan.id)
        self.assertTrue(updated_plan.is_active)
    
    def test_exercise_plan_deactivate_api(self) -> None:
        """测试运动计划停用API。"""
        response = self.client.post(f"/api/v1/exercise/plans/{self.exercise_plan.id}/deactivate/")
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["is_active"])
        
        # 验证数据库已更新
        updated_plan = ExercisePlan.objects.get(id=self.exercise_plan.id)
        self.assertFalse(updated_plan.is_active)
    
    def test_exercise_plan_statistics_api(self) -> None:
        """测试运动计划统计API。"""
        response = self.client.get("/api/v1/exercise/plans/statistics/")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_count", response.data)
        self.assertIn("active_count", response.data)
        self.assertIn("completed_count", response.data)
        self.assertIn("average_success_rate", response.data)
        self.assertIn("status_statistics", response.data)
        self.assertIn("monthly_trend", response.data)
    
    def test_exercise_analysis_list_api(self) -> None:
        """测试运动分析列表API。"""
        response = self.client.get("/api/v1/exercise/analyses/")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertGreater(len(response.data["results"]), 0)
        
        # 检查返回的数据结构
        analysis_data = response.data["results"][0]
        self.assertEqual(analysis_data["analysis_period"], "weekly")
        self.assertIn("analysis_period_display", analysis_data)
        self.assertIn("period_days", analysis_data)
        self.assertIn("daily_average_duration", analysis_data)
        self.assertIn("daily_average_calories", analysis_data)
        self.assertIn("exercise_frequency", analysis_data)
        self.assertIn("health_score", analysis_data)
    
    def test_exercise_analysis_detail_api(self) -> None:
        """测试运动分析详情API。"""
        response = self.client.get(f"/api/v1/exercise/analyses/{self.exercise_analysis.id}/")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["analysis_period"], "weekly")
        self.assertEqual(response.data["total_duration_minutes"], "180.00")
        self.assertEqual(response.data["exercise_count"], 6)
    
    def test_exercise_analysis_create_api(self) -> None:
        """测试运动分析创建API。"""
        today = timezone.now().date()
        data: Dict[str, Any] = {
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
        
        response = self.client.post("/api/v1/exercise/analyses/", data, format="json")
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["analysis_period"], "monthly")
        self.assertEqual(response.data["total_duration_minutes"], "720.00")
        self.assertEqual(response.data["exercise_count"], 24)
        
        # 验证分析已创建
        analysis_id = response.data["id"]
        self.assertTrue(ExerciseAnalysis.objects.filter(id=analysis_id).exists())
    
    def test_exercise_analysis_generate_weekly_api(self) -> None:
        """测试生成每周运动分析API。"""
        response = self.client.get("/api/v1/exercise/analyses/generate_weekly/")
        
        # 可能返回200（已存在）或201（新创建）
        self.assertIn(response.status_code, [200, 201])
        
        if response.status_code == 201:
            self.assertEqual(response.data["analysis_period"], "weekly")
            self.assertIn("total_duration_minutes", response.data)
            self.assertIn("total_calories", response.data)
            self.assertIn("exercise_count", response.data)
            self.assertIn("strengths", response.data)
            self.assertIn("weaknesses", response.data)
            self.assertIn("recommendations", response.data)
    
    def test_exercise_analysis_statistics_api(self) -> None:
        """测试运动分析统计API。"""
        response = self.client.get("/api/v1/exercise/analyses/statistics/")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_count", response.data)
        self.assertIn("period_statistics", response.data)
        self.assertIn("health_score_distribution", response.data)
        self.assertIn("monthly_trend", response.data)
    
    def test_api_authentication_required(self) -> None:
        """测试API需要认证。"""
        # 使用未认证的客户端
        unauthenticated_client = APIClient()
        
        response = unauthenticated_client.get("/api/v1/exercise/records/")
        self.assertEqual(response.status_code, 401)  # 未认证
        
        response = unauthenticated_client.post("/api/v1/exercise/records/", {})
        self.assertEqual(response.status_code, 401)  # 未认证
    
    def test_api_permission_control(self) -> None:
        """测试API权限控制。"""
        # 创建另一个用户
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpass123",
        )
        
        # 使用其他用户的客户端
        other_client = APIClient()
        other_client.force_authenticate(user=other_user)
        
        # 其他用户应该看不到当前用户的数据
        response = other_client.get(f"/api/v1/exercise/records/{self.exercise_record.id}/")
        self.assertEqual(response.status_code, 404)  # 找不到
        
        response = other_client.get(f"/api/v1/exercise/plans/{self.exercise_plan.id}/")
        self.assertEqual(response.status_code, 404)  # 找不到
        
        response = other_client.get(f"/api/v1/exercise/analyses/{self.exercise_analysis.id}/")
        self.assertEqual(response.status_code, 404)  # 找不到


if __name__ == "__main__":
    import django
    django.setup()
    
    # 运行测试
    import unittest
    unittest.main()
"""
运动管理模型测试模块，测试运动记录、运动计划、运动分析等数据模型。
按照豆包AI助手最佳实践：使用Django测试框架进行单元测试。
"""
from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.exercise.models import ExerciseAnalysis, ExercisePlan, ExerciseRecord
from core.constants import ExerciseType


User = get_user_model()


# ==================== 运动记录模型测试 ====================
class ExerciseRecordModelTest(TestCase):
    """
    运动记录模型测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        
        self.exercise_record = ExerciseRecord.objects.create(
            title="晨跑训练",
            description="早晨5公里慢跑",
            user=self.user,
            exercise_type=ExerciseType.RUNNING,
            duration_seconds=1800,  # 30分钟
            repetitions=0,
            calories_burned=Decimal("300.00"),
            started_at=timezone.now() - datetime.timedelta(hours=1),
            ended_at=timezone.now() - datetime.timedelta(minutes=30),
        )
    
    def test_exercise_record_creation(self) -> None:
        """测试运动记录创建。"""
        self.assertEqual(self.exercise_record.title, "晨跑训练")
        self.assertEqual(self.exercise_record.user, self.user)
        self.assertEqual(self.exercise_record.exercise_type, ExerciseType.RUNNING)
        self.assertEqual(self.exercise_record.duration_seconds, 1800)
        self.assertEqual(self.exercise_record.calories_burned, Decimal("300.00"))
        self.assertTrue(self.exercise_record.pk)
    
    def test_exercise_record_str_method(self) -> None:
        """测试运动记录的字符串表示。"""
        expected_str = f"晨跑训练 - {self.user.username} (跑步)"
        self.assertEqual(str(self.exercise_record), expected_str)
    
    def test_exercise_record_duration_minutes(self) -> None:
        """测试运动时长（分钟）计算方法。"""
        duration_minutes = self.exercise_record.get_duration_minutes()
        self.assertEqual(duration_minutes, 30.0)
    
    def test_exercise_record_calories_per_minute(self) -> None:
        """测试每分钟卡路里计算方法。"""
        calories_per_minute = self.exercise_record.get_calories_per_minute()
        self.assertAlmostEqual(calories_per_minute, 10.0, places=2)
    
    def test_exercise_record_is_completed(self) -> None:
        """测试运动是否完成检查。"""
        # 已结束的运动应该返回True
        self.assertTrue(self.exercise_record.is_completed())
        
        # 创建未结束的运动记录
        ongoing_record = ExerciseRecord.objects.create(
            title="进行中的运动",
            user=self.user,
            exercise_type=ExerciseType.JUMP_ROPE,
            duration_seconds=600,
            started_at=timezone.now() - datetime.timedelta(minutes=5),
            ended_at=None,
        )
        
        self.assertFalse(ongoing_record.is_completed())
    
    def test_exercise_record_progress_percentage(self) -> None:
        """测试运动进度百分比计算方法。"""
        # 已完成的运动进度应为100%
        progress = self.exercise_record.get_progress_percentage()
        self.assertEqual(progress, 100.0)
        
        # 创建进行中的运动记录
        now = timezone.now()
        ongoing_record = ExerciseRecord.objects.create(
            title="进行中的测试",
            user=self.user,
            exercise_type=ExerciseType.SIT_UP,
            duration_seconds=600,  # 10分钟
            started_at=now - datetime.timedelta(minutes=5),
            ended_at=now + datetime.timedelta(minutes=5),
        )
        
        progress = ongoing_record.get_progress_percentage()
        self.assertGreaterEqual(progress, 0.0)
        self.assertLessEqual(progress, 100.0)
    
    def test_exercise_record_save_auto_end_time(self) -> None:
        """测试保存时自动计算结束时间。"""
        start_time = timezone.now()
        record = ExerciseRecord(
            title="自动结束时间测试",
            user=self.user,
            exercise_type=ExerciseType.PUSH_UP,
            duration_seconds=300,  # 5分钟
            started_at=start_time,
            ended_at=None,
        )
        
        record.save()
        
        # 检查是否自动计算了结束时间
        expected_end_time = start_time + datetime.timedelta(seconds=300)
        self.assertIsNotNone(record.ended_at)
        self.assertAlmostEqual(
            record.ended_at.timestamp(),
            expected_end_time.timestamp(),
            delta=1,  # 允许1秒误差
        )
    
    def test_exercise_record_validation(self) -> None:
        """测试运动记录验证。"""
        # 测试时长最小值验证
        record = ExerciseRecord(
            title="时长过短测试",
            user=self.user,
            exercise_type=ExerciseType.OTHER,
            duration_seconds=0,  # 小于最小值
        )
        
        with self.assertRaises(ValidationError):
            record.full_clean()
        
        # 测试时长最大值验证
        record.duration_seconds = 4000  # 大于最大值（3600）
        
        with self.assertRaises(ValidationError):
            record.full_clean()
    
    def test_exercise_record_ordering(self) -> None:
        """测试运动记录排序。"""
        # 创建第二个记录
        earlier_record = ExerciseRecord.objects.create(
            title="更早的记录",
            user=self.user,
            exercise_type=ExerciseType.YOGA,
            duration_seconds=1200,
            started_at=timezone.now() - datetime.timedelta(days=1),
            ended_at=timezone.now() - datetime.timedelta(days=1) + datetime.timedelta(seconds=1200),
        )
        
        # 默认应该按开始时间倒序排列
        records = ExerciseRecord.objects.all()
        self.assertEqual(records[0], self.exercise_record)  # 较晚的记录在前
        self.assertEqual(records[1], earlier_record)  # 较早的记录在后


# ==================== 运动计划模型测试 ====================
class ExercisePlanModelTest(TestCase):
    """
    运动计划模型测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.user = User.objects.create_user(
            username="planuser",
            email="plan@example.com",
            password="testpass123",
        )
        
        self.exercise_plan = ExercisePlan.objects.create(
            name="减脂计划",
            description="每周5次有氧运动",
            user=self.user,
            target_duration_minutes=30,
            target_repetitions=0,
            target_calories=Decimal("200.00"),
            frequency_per_week=5,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + datetime.timedelta(days=30),
            is_active=True,
        )
    
    def test_exercise_plan_creation(self) -> None:
        """测试运动计划创建。"""
        self.assertEqual(self.exercise_plan.name, "减脂计划")
        self.assertEqual(self.exercise_plan.user, self.user)
        self.assertEqual(self.exercise_plan.target_duration_minutes, 30)
        self.assertEqual(self.exercise_plan.frequency_per_week, 5)
        self.assertTrue(self.exercise_plan.is_active)
        self.assertTrue(self.exercise_plan.pk)
    
    def test_exercise_plan_str_method(self) -> None:
        """测试运动计划的字符串表示。"""
        expected_str = f"减脂计划 - {self.user.username} (激活)"
        self.assertEqual(str(self.exercise_plan), expected_str)
    
    def test_exercise_plan_remaining_days(self) -> None:
        """测试剩余天数计算方法。"""
        remaining_days = self.exercise_plan.get_remaining_days()
        self.assertIsNotNone(remaining_days)
        self.assertGreaterEqual(remaining_days, 0)
        self.assertLessEqual(remaining_days, 30)
    
    def test_exercise_plan_progress_percentage(self) -> None:
        """测试计划进度百分比计算方法。"""
        progress = self.exercise_plan.get_progress_percentage()
        
        # 刚开始的计划进度应该接近0%
        self.assertGreaterEqual(progress, 0.0)
        self.assertLessEqual(progress, 100.0)
        
        # 创建已过期的计划
        expired_plan = ExercisePlan.objects.create(
            name="过期计划",
            user=self.user,
            target_duration_minutes=20,
            frequency_per_week=3,
            start_date=timezone.now().date() - datetime.timedelta(days=60),
            end_date=timezone.now().date() - datetime.timedelta(days=30),
        )
        
        progress = expired_plan.get_progress_percentage()
        self.assertEqual(progress, 100.0)
    
    def test_exercise_plan_expected_completion_count(self) -> None:
        """测试预期完成次数计算方法。"""
        expected_count = self.exercise_plan.get_expected_completion_count()
        
        # 30天，每周5次，大约4周，预期20次
        self.assertGreaterEqual(expected_count, 15)
        self.assertLessEqual(expected_count, 25)
    
    def test_exercise_plan_can_add_exercise(self) -> None:
        """测试是否可以添加运动记录检查。"""
        # 激活的计划应该可以添加运动记录
        self.assertTrue(self.exercise_plan.can_add_exercise())
        
        # 停用的计划不能添加运动记录
        inactive_plan = ExercisePlan.objects.create(
            name="停用计划",
            user=self.user,
            target_duration_minutes=20,
            frequency_per_week=3,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + datetime.timedelta(days=30),
            is_active=False,
        )
        
        self.assertFalse(inactive_plan.can_add_exercise())
    
    def test_exercise_plan_save_success_rate(self) -> None:
        """测试保存时自动计算完成率。"""
        # 设置完成次数
        self.exercise_plan.completed_count = 10
        self.exercise_plan.save()
        
        # 检查是否计算了完成率
        self.assertGreater(self.exercise_plan.success_rate, 0)
        self.assertLessEqual(self.exercise_plan.success_rate, 100)
    
    def test_exercise_plan_validation(self) -> None:
        """测试运动计划验证。"""
        # 测试每周频率验证
        plan = ExercisePlan(
            name="频率错误测试",
            user=self.user,
            target_duration_minutes=30,
            frequency_per_week=0,  # 小于最小值
        )
        
        with self.assertRaises(ValidationError):
            plan.full_clean()
        
        plan.frequency_per_week = 8  # 大于最大值
        
        with self.assertRaises(ValidationError):
            plan.full_clean()


# ==================== 运动分析模型测试 ====================
class ExerciseAnalysisModelTest(TestCase):
    """
    运动分析模型测试类。
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
            strengths="运动频率较高，坚持得很好",
            weaknesses="运动强度可以进一步提高",
            recommendations="建议增加力量训练",
        )
    
    def test_exercise_analysis_creation(self) -> None:
        """测试运动分析创建。"""
        self.assertEqual(self.exercise_analysis.user, self.user)
        self.assertEqual(self.exercise_analysis.analysis_period, "weekly")
        self.assertEqual(self.exercise_analysis.total_duration_minutes, Decimal("180.00"))
        self.assertEqual(self.exercise_analysis.exercise_count, 6)
        self.assertTrue(self.exercise_analysis.pk)
    
    def test_exercise_analysis_str_method(self) -> None:
        """测试运动分析的字符串表示。"""
        expected_str = f"{self.user.username} - 每周分析 ({self.exercise_analysis.period_start} 至 {self.exercise_analysis.period_end})"
        self.assertEqual(str(self.exercise_analysis), expected_str)
    
    def test_exercise_analysis_period_days(self) -> None:
        """测试分析周期天数计算方法。"""
        period_days = self.exercise_analysis.get_period_days()
        self.assertEqual(period_days, 7)  # 一周7天
    
    def test_exercise_analysis_daily_average_duration(self) -> None:
        """测试每日平均运动时长计算方法。"""
        daily_avg = self.exercise_analysis.get_daily_average_duration()
        expected_avg = 180.00 / 7  # 总时长除以天数
        self.assertAlmostEqual(float(daily_avg), expected_avg, places=2)
    
    def test_exercise_analysis_daily_average_calories(self) -> None:
        """测试每日平均卡路里消耗计算方法。"""
        daily_avg = self.exercise_analysis.get_daily_average_calories()
        expected_avg = 1200.00 / 7  # 总卡路里除以天数
        self.assertAlmostEqual(float(daily_avg), expected_avg, places=2)
    
    def test_exercise_analysis_exercise_frequency(self) -> None:
        """测试运动频率计算方法。"""
        frequency = self.exercise_analysis.get_exercise_frequency()
        expected_frequency = 6 / 7  # 运动次数除以天数
        self.assertAlmostEqual(frequency, expected_frequency, places=2)
    
    def test_exercise_analysis_health_score(self) -> None:
        """测试健康评分计算方法。"""
        health_score = self.exercise_analysis.get_health_score()
        
        # 健康评分应该在0-100之间
        self.assertGreaterEqual(health_score, 0.0)
        self.assertLessEqual(health_score, 100.0)
        
        # 具体计算验证
        # 坚持率85.5 * 0.4 = 34.2
        # 进步率10.2（但上限50） * 0.3 = 3.06
        # 运动频率6/7=0.857，目标0.7，得分=0.857/0.7*30=36.73（上限30）
        # 总分 = 34.2 + 3.06 + 30 = 67.26
        expected_score = 34.2 + 3.06 + 30
        self.assertAlmostEqual(health_score, expected_score, places=1)
    
    def test_exercise_analysis_save_averages(self) -> None:
        """测试保存时自动计算平均值。"""
        # 创建新的分析记录，不设置平均值
        new_analysis = ExerciseAnalysis(
            user=self.user,
            analysis_period="daily",
            period_start=timezone.now().date(),
            period_end=timezone.now().date(),
            total_duration_minutes=Decimal("60.00"),
            total_calories=Decimal("400.00"),
            exercise_count=2,
        )
        
        new_analysis.save()
        
        # 检查是否自动计算了平均值
        self.assertEqual(new_analysis.average_duration_minutes, Decimal("30.00"))
        self.assertEqual(new_analysis.average_calories, Decimal("200.00"))
    
    def test_exercise_analysis_unique_constraint(self) -> None:
        """测试唯一性约束。"""
        # 尝试创建重复的分析记录
        duplicate_analysis = ExerciseAnalysis(
            user=self.user,
            analysis_period="weekly",
            period_start=self.exercise_analysis.period_start,
            period_end=self.exercise_analysis.period_end,
            total_duration_minutes=Decimal("100.00"),
            total_calories=Decimal("800.00"),
            exercise_count=4,
        )
        
        # 应该引发唯一性约束错误
        with self.assertRaises(Exception):
            duplicate_analysis.save()
    
    def test_exercise_analysis_validation(self) -> None:
        """测试运动分析验证。"""
        # 测试坚持率验证
        analysis = ExerciseAnalysis(
            user=self.user,
            analysis_period="monthly",
            period_start=timezone.now().date(),
            period_end=timezone.now().date() + datetime.timedelta(days=30),
            consistency_rate=Decimal("150.00"),  # 大于100
        )
        
        with self.assertRaises(ValidationError):
            analysis.full_clean()
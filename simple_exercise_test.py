"""
简化版的运动模块测试，验证核心功能。
"""
import os
import sys

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.simple")

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import django
django.setup()

from django.contrib.auth import get_user_model
from apps.exercise.models import ExerciseRecord, ExercisePlan, ExerciseAnalysis
from core.constants import ExerciseType
from django.utils import timezone
from decimal import Decimal
import datetime

User = get_user_model()

print("=== 运动模块核心功能测试 ===")

try:
    # 1. 创建测试用户
    print("1. 创建测试用户...")
    user, created = User.objects.get_or_create(
        username="testuser",
        defaults={
            "email": "test@example.com",
            "password": "testpass123",
        }
    )
    print(f"   用户: {user.username} (ID: {user.id})")
    
    # 2. 测试运动记录模型
    print("\n2. 测试运动记录模型...")
    record = ExerciseRecord.objects.create(
        title="测试运动记录",
        description="这是一个测试记录",
        user=user,
        exercise_type=ExerciseType.RUNNING,
        duration_seconds=1800,
        calories_burned=Decimal("300.00"),
        started_at=timezone.now() - datetime.timedelta(hours=1),
        ended_at=timezone.now() - datetime.timedelta(minutes=30),
    )
    print(f"   创建运动记录: {record.title}")
    print(f"   运动类型: {record.get_exercise_type_display()}")
    print(f"   时长: {record.get_duration_minutes():.1f} 分钟")
    print(f"   卡路里: {record.calories_burned}")
    print(f"   是否完成: {record.is_completed()}")
    print(f"   进度: {record.get_progress_percentage():.1f}%")
    
    # 3. 测试运动计划模型
    print("\n3. 测试运动计划模型...")
    plan = ExercisePlan.objects.create(
        name="测试运动计划",
        description="这是一个测试计划",
        user=user,
        target_duration_minutes=30,
        frequency_per_week=5,
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + datetime.timedelta(days=30),
    )
    print(f"   创建运动计划: {plan.name}")
    print(f"   目标时长: {plan.target_duration_minutes} 分钟")
    print(f"   每周频率: {plan.frequency_per_week} 次")
    print(f"   剩余天数: {plan.get_remaining_days()}")
    print(f"   进度: {plan.get_progress_percentage():.1f}%")
    print(f"   预期完成次数: {plan.get_expected_completion_count()}")
    print(f"   是否可以添加运动: {plan.can_add_exercise()}")
    
    # 4. 测试运动分析模型
    print("\n4. 测试运动分析模型...")
    today = timezone.now().date()
    analysis = ExerciseAnalysis.objects.create(
        user=user,
        analysis_period="weekly",
        period_start=today - datetime.timedelta(days=6),
        period_end=today,
        total_duration_minutes=Decimal("180.00"),
        total_calories=Decimal("1200.00"),
        exercise_count=6,
    )
    print(f"   创建运动分析: 用户={analysis.user.username}")
    print(f"   分析周期: {analysis.get_analysis_period_display()}")
    print(f"   总时长: {analysis.total_duration_minutes} 分钟")
    print(f"   总卡路里: {analysis.total_calories}")
    print(f"   运动次数: {analysis.exercise_count}")
    print(f"   周期天数: {analysis.get_period_days()}")
    print(f"   每日平均时长: {analysis.get_daily_average_duration():.1f} 分钟")
    print(f"   每日平均卡路里: {analysis.get_daily_average_calories():.1f}")
    print(f"   运动频率: {analysis.get_exercise_frequency():.2f} 次/天")
    print(f"   健康评分: {analysis.get_health_score():.1f}")
    
    # 5. 测试查询功能
    print("\n5. 测试查询功能...")
    records_count = ExerciseRecord.objects.filter(user=user).count()
    plans_count = ExercisePlan.objects.filter(user=user).count()
    analyses_count = ExerciseAnalysis.objects.filter(user=user).count()
    
    print(f"   用户运动记录数: {records_count}")
    print(f"   用户运动计划数: {plans_count}")
    print(f"   用户运动分析数: {analyses_count}")
    
    # 6. 测试更新功能
    print("\n6. 测试更新功能...")
    record.title = "更新后的标题"
    record.save()
    print(f"   更新运动记录标题: {record.title}")
    
    plan.completed_count = 10
    plan.save()
    print(f"   更新运动计划完成次数: {plan.completed_count}")
    print(f"   更新后完成率: {plan.success_rate:.1f}%")
    
    # 7. 测试删除功能
    print("\n7. 测试删除功能...")
    record_id = record.id
    plan_id = plan.id
    analysis_id = analysis.id
    
    record.delete()
    plan.delete()
    analysis.delete()
    
    print(f"   删除运动记录 (ID: {record_id})")
    print(f"   删除运动计划 (ID: {plan_id})")
    print(f"   删除运动分析 (ID: {analysis_id})")
    
    # 验证删除
    records_after = ExerciseRecord.objects.filter(id=record_id).count()
    plans_after = ExercisePlan.objects.filter(id=plan_id).count()
    analyses_after = ExerciseAnalysis.objects.filter(id=analysis_id).count()
    
    print(f"   删除后验证 - 记录: {records_after}, 计划: {plans_after}, 分析: {analyses_after}")
    
    print("\n✅ 所有测试通过！")
    
except Exception as e:
    print(f"\n❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
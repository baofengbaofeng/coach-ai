#!/usr/bin/env python
"""
测试任务模块基本功能
"""
import os
import sys
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.simple")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model
from apps.tasks.models import Task, TaskCategory
from core.constants import TaskPriority, TaskStatus

User = get_user_model()

print("测试任务模块基本功能...")
print("=" * 50)

# 1. 创建测试用户
try:
    user, created = User.objects.get_or_create(
        username="basic_test_user",
        defaults={
            "email": "basic@example.com",
            "password": "test123",
        }
    )
    print(f"✅ 用户: {user.username} (ID: {user.id})")
except Exception as e:
    print(f"❌ 创建用户失败: {e}")
    sys.exit(1)

# 2. 创建任务分类
try:
    category, created = TaskCategory.objects.get_or_create(
        name="基本测试分类",
        defaults={
            "description": "基本功能测试",
            "color": "#0000FF",
            "icon": "test",
            "order": 999,
            "is_active": True,
        }
    )
    print(f"✅ 分类: {category.name} (ID: {category.id})")
except Exception as e:
    print(f"❌ 创建分类失败: {e}")
    sys.exit(1)

# 3. 创建任务
try:
    task = Task.objects.create(
        title="基本测试任务",
        description="测试基本功能",
        user=user,
        category=category,
        status=TaskStatus.PENDING.value,
        priority=TaskPriority.MEDIUM.value,
        estimated_hours=Decimal("2.0"),
        is_recurring=False,
        is_important=False,
        is_urgent=False,
        difficulty_level=3,
    )
    print(f"✅ 任务: {task.title} (ID: {task.id})")
    print(f"   状态: {task.status}")
    print(f"   优先级: {task.priority}")
    print(f"   预估时间: {task.estimated_hours}小时")
except Exception as e:
    print(f"❌ 创建任务失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. 更新任务进度
try:
    task.progress = Decimal("50.0")
    task.progress_percentage = 50
    task.actual_hours = Decimal("1.0")
    task.save()
    print(f"✅ 更新进度: {task.progress}%")
    print(f"   实际时间: {task.actual_hours}小时")
except Exception as e:
    print(f"❌ 更新进度失败: {e}")

# 5. 完成任务
try:
    task.status = TaskStatus.COMPLETED.value
    task.progress = Decimal("100.0")
    task.progress_percentage = 100
    task.save()
    print(f"✅ 完成任务: {task.status}")
except Exception as e:
    print(f"❌ 完成任务失败: {e}")

# 6. 统计
try:
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status=TaskStatus.COMPLETED.value).count()
    pending_tasks = Task.objects.filter(status=TaskStatus.PENDING.value).count()
    
    print(f"\n📊 统计:")
    print(f"   总任务数: {total_tasks}")
    print(f"   已完成: {completed_tasks}")
    print(f"   待处理: {pending_tasks}")
except Exception as e:
    print(f"❌ 统计失败: {e}")

# 7. 清理测试数据
try:
    task.delete()
    category.delete()
    user.delete()
    print("\n🧹 清理测试数据完成")
except Exception as e:
    print(f"⚠️  清理数据失败: {e}")

print("\n" + "=" * 50)
print("基本功能测试完成!")
print("如果所有步骤都显示✅，说明任务模块基本功能正常。")
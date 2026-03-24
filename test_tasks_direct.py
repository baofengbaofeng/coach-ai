#!/usr/bin/env python
"""
直接测试任务模块功能，绕过迁移问题。
"""
import os
import sys
import django
from django.db import connection
from django.db.utils import OperationalError

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.simple")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

print("=" * 60)
print("任务模块直接功能测试")
print("=" * 60)

# 1. 检查数据库连接
print("\n1. 数据库连接检查:")
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("  ✅ 数据库连接正常")
except Exception as e:
    print(f"  ❌ 数据库连接失败: {e}")
    sys.exit(1)

# 2. 检查任务相关表是否存在
print("\n2. 数据库表检查:")
task_tables = [
    'tasks_taskcategory',
    'tasks_task',
    'tasks_taskreminder',
    'tasks_taskcomment',
]

with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    
for table in task_tables:
    if table in existing_tables:
        # 检查表结构
        cursor = connection.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"  ✅ {table}: {len(columns)}列")
    else:
        print(f"  ❌ {table}: 表不存在")

# 3. 尝试导入任务模块
print("\n3. 模块导入检查:")
try:
    from apps.tasks.models import TaskCategory, Task, TaskReminder, TaskComment
    print("  ✅ 成功导入任务模型")
    
    # 检查模型元数据
    print(f"    - TaskCategory: {TaskCategory._meta.db_table}")
    print(f"    - Task: {Task._meta.db_table}")
    print(f"    - TaskReminder: {TaskReminder._meta.db_table}")
    print(f"    - TaskComment: {TaskComment._meta.db_table}")
    
except ImportError as e:
    print(f"  ❌ 导入失败: {e}")
    sys.exit(1)

# 4. 检查序列化器
print("\n4. 序列化器检查:")
try:
    from apps.tasks.serializers import (
        TaskCategorySerializer,
        TaskSerializer,
        TaskCreateSerializer,
        TaskProgressSerializer,
        TaskReminderSerializer,
        TaskCommentSerializer,
        TaskStatisticsSerializer,
    )
    print("  ✅ 成功导入所有序列化器")
    print(f"    - 共导入7个序列化器")
except ImportError as e:
    print(f"  ⚠️  序列化器导入问题: {e}")

# 5. 检查视图
print("\n5. 视图检查:")
try:
    from apps.tasks.views import (
        TaskCategoryViewSet,
        TaskViewSet,
        TaskReminderViewSet,
        TaskCommentViewSet,
    )
    print("  ✅ 成功导入所有视图")
    print(f"    - 共导入4个视图集")
except ImportError as e:
    print(f"  ⚠️  视图导入问题: {e}")

# 6. 检查常量
print("\n6. 常量检查:")
try:
    from core.constants import TaskStatus, TaskPriority
    print("  ✅ 成功导入任务常量")
    print(f"    - TaskStatus: {[s.value for s in TaskStatus]}")
    print(f"    - TaskPriority: {[p.value for p in TaskPriority]}")
except ImportError as e:
    print(f"  ❌ 常量导入失败: {e}")

# 7. 尝试创建测试数据（如果表存在）
print("\n7. 功能测试:")
if 'tasks_taskcategory' in existing_tables:
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # 获取或创建测试用户
        user, created = User.objects.get_or_create(
            username="test_direct",
            defaults={"email": "test@example.com", "password": "test123"}
        )
        
        # 尝试创建任务分类
        category, cat_created = TaskCategory.objects.get_or_create(
            name="测试分类",
            defaults={
                "description": "测试用的分类",
                "color": "#FF0000",
                "icon": "test",
                "order": 99,
                "is_active": True,
            }
        )
        
        if cat_created:
            print(f"  ✅ 创建任务分类: {category.name} (ID: {category.id})")
        else:
            print(f"  ✅ 获取现有分类: {category.name} (ID: {category.id})")
            
        # 尝试创建任务
        task, task_created = Task.objects.get_or_create(
            title="测试任务",
            user=user,
            defaults={
                "description": "这是一个测试任务",
                "category": category,
                "status": TaskStatus.PENDING.value,
                "priority": TaskPriority.MEDIUM.value,
                "due_date": None,
                "estimated_hours": 2.0,
                "actual_hours": 0.0,
                "progress": 0.0,
                "is_recurring": False,
            }
        )
        
        if task_created:
            print(f"  ✅ 创建任务: {task.title} (ID: {task.id})")
        else:
            print(f"  ✅ 获取现有任务: {task.title} (ID: {task.id})")
            
        # 统计
        cat_count = TaskCategory.objects.count()
        task_count = Task.objects.count()
        print(f"  📊 统计: {cat_count}个分类, {task_count}个任务")
        
    except Exception as e:
        print(f"  ⚠️  功能测试失败: {e}")
else:
    print("  ⚠️  跳过功能测试（表不存在）")

print("\n" + "=" * 60)
print("测试完成!")
print("=" * 60)

# 总结建议
print("\n建议下一步:")
if 'tasks_taskcategory' not in existing_tables:
    print("1. 需要创建任务模块的数据库表")
    print("   执行: python manage_simple.py makemigrations tasks")
    print("   然后: python manage_simple.py migrate tasks")
else:
    print("1. 数据库表已存在，可以继续开发")
    
print("2. 检查并完成单元测试文件")
print("3. 验证API端点功能")
print("4. 解决迁移依赖问题（如需要）")
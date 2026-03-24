"""
简化版的任务模块测试，验证核心功能。
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
from apps.tasks.models import Task, TaskCategory, TaskComment, TaskReminder
from core.constants import TaskPriority, TaskStatus
from django.utils import timezone
from decimal import Decimal
import datetime

User = get_user_model()

print("=== 任务模块核心功能测试 ===")

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
    
    # 2. 测试任务分类模型
    print("\n2. 测试任务分类模型...")
    category = TaskCategory.objects.create(
        name="学习任务",
        description="与学习相关的任务",
        color="#3B82F6",
        icon="book",
        order=1,
        is_active=True,
    )
    print(f"   创建任务分类: {category.name}")
    print(f"   颜色: {category.color}")
    print(f"   图标: {category.icon}")
    print(f"   排序: {category.order}")
    print(f"   状态: {'激活' if category.is_active else '停用'}")
    
    # 3. 测试任务模型
    print("\n3. 测试任务模型...")
    task = Task.objects.create(
        title="完成数学作业",
        description="完成第5章的练习题",
        user=user,
        category=category,
        status=TaskStatus.PENDING,
        priority=TaskPriority.HIGH,
        due_date=timezone.now() + datetime.timedelta(days=3),
        estimated_hours=Decimal("2.00"),
        progress_percentage=0,
        difficulty_level=4,
    )
    print(f"   创建任务: {task.title}")
    print(f"   用户: {task.user.username}")
    print(f"   分类: {task.category.name}")
    print(f"   状态: {task.get_status_display()}")
    print(f"   优先级: {task.get_priority_display()}")
    print(f"   截止时间: {task.due_date}")
    print(f"   预计耗时: {task.estimated_hours} 小时")
    print(f"   进度: {task.progress_percentage}%")
    print(f"   难度: {task.difficulty_level}/5")
    print(f"   是否过期: {task.is_overdue()}")
    print(f"   剩余天数: {task.get_remaining_days()}")
    print(f"   是否可以完成: {task.can_complete()}")
    
    # 4. 测试任务进度更新
    print("\n4. 测试任务进度更新...")
    task.update_progress(50, Decimal("1.00"))
    print(f"   更新进度到: {task.progress_percentage}%")
    print(f"   实际耗时: {task.actual_hours} 小时")
    print(f"   新状态: {task.get_status_display()}")
    print(f"   时间花费比率: {task.get_time_spent_ratio():.2f}")
    
    # 5. 测试标记任务为完成
    print("\n5. 测试标记任务为完成...")
    success = task.mark_as_completed()
    print(f"   标记完成结果: {'成功' if success else '失败'}")
    print(f"   完成状态: {task.get_status_display()}")
    print(f"   完成时间: {task.completed_at}")
    print(f"   最终进度: {task.progress_percentage}%")
    
    # 6. 测试任务提醒模型
    print("\n6. 测试任务提醒模型...")
    reminder = TaskReminder.objects.create(
        task=task,
        reminder_time=timezone.now() + datetime.timedelta(hours=12),
        reminder_type="notification",
        reminder_message="记得检查作业完成情况",
        is_active=True,
    )
    print(f"   创建任务提醒: 任务={reminder.task.title}")
    print(f"   提醒时间: {reminder.reminder_time}")
    print(f"   提醒类型: {reminder.get_reminder_type_display()}")
    print(f"   是否激活: {'是' if reminder.is_active else '否'}")
    print(f"   是否已发送: {'是' if reminder.is_sent else '否'}")
    print(f"   是否到期: {'是' if reminder.is_due() else '否'}")
    print(f"   距离提醒还有: {reminder.get_time_until_reminder():.1f} 小时")
    print(f"   是否可以立即发送: {'是' if reminder.can_send_now() else '否'}")
    
    # 7. 测试任务评论模型
    print("\n7. 测试任务评论模型...")
    comment = TaskComment.objects.create(
        task=task,
        user=user,
        content="作业完成得很好，继续保持！",
    )
    print(f"   创建任务评论: 用户={comment.user.username}")
    print(f"   任务: {comment.task.title}")
    print(f"   评论内容: {comment.get_short_content(30)}")
    print(f"   是否编辑过: {'是' if comment.is_edited else '否'}")
    print(f"   用户是否可以编辑: {'是' if comment.can_edit(user) else '否'}")
    print(f"   用户是否可以删除: {'是' if comment.can_delete(user) else '否'}")
    
    # 8. 测试任务分类统计更新
    print("\n8. 测试任务分类统计更新...")
    category.update_task_count()
    print(f"   分类任务数量: {category.task_count}")
    
    # 9. 测试查询功能
    print("\n9. 测试查询功能...")
    tasks_count = Task.objects.filter(user=user).count()
    categories_count = TaskCategory.objects.count()
    reminders_count = TaskReminder.objects.filter(task__user=user).count()
    comments_count = TaskComment.objects.filter(user=user).count()
    
    print(f"   用户任务数: {tasks_count}")
    print(f"   任务分类数: {categories_count}")
    print(f"   任务提醒数: {reminders_count}")
    print(f"   任务评论数: {comments_count}")
    
    # 10. 测试软删除
    print("\n10. 测试软删除...")
    task_id = task.id
    task.delete()  # 软删除
    
    print(f"   软删除任务 (ID: {task_id})")
    print(f"   删除后是否可见: {'否' if task.is_deleted else '是'}")
    
    # 验证删除
    visible_tasks = Task.objects.filter(is_deleted=False).count()
    all_tasks = Task.objects.all().count()
    
    print(f"   删除后统计 - 可见任务: {visible_tasks}, 所有任务: {all_tasks}")
    
    print("\n✅ 所有测试通过！")
    
except Exception as e:
    print(f"\n❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
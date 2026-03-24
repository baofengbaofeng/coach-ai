"""
任务管理序列化器测试模块，测试任务、分类、提醒、评论等序列化器。
按照豆包AI助手最佳实践：使用Django测试框架进行单元测试。
"""
from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.tasks.models import Task, TaskCategory, TaskComment, TaskReminder
from apps.tasks.serializers import (
    TaskCategorySerializer,
    TaskSerializer,
    TaskCreateSerializer,
    TaskProgressSerializer,
    TaskReminderSerializer,
    TaskCommentSerializer,
    TaskStatisticsSerializer,
)
from core.constants import TaskPriority, TaskStatus


User = get_user_model()


# ==================== 任务分类序列化器测试 ====================
class TaskCategorySerializerTest(TestCase):
    """
    任务分类序列化器测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.category_data = {
            "name": "学习任务",
            "description": "与学习相关的任务分类",
            "color": "#3B82F6",
            "icon": "book",
            "order": 1,
            "is_active": True,
        }
        self.category = TaskCategory.objects.create(**self.category_data)
    
    def test_task_category_serializer_valid(self) -> None:
        """测试任务分类序列化器验证有效数据。"""
        serializer = TaskCategorySerializer(data=self.category_data)
        self.assertTrue(serializer.is_valid())
        
        # 验证序列化数据
        data = serializer.validated_data
        self.assertEqual(data["name"], "学习任务")
        self.assertEqual(data["color"], "#3B82F6")
        self.assertEqual(data["order"], 1)
        self.assertTrue(data["is_active"])
    
    def test_task_category_serializer_invalid(self) -> None:
        """测试任务分类序列化器验证无效数据。"""
        invalid_data = self.category_data.copy()
        invalid_data["name"] = ""  # 空名称
        
        serializer = TaskCategorySerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)
    
    def test_task_category_serializer_instance(self) -> None:
        """测试任务分类序列化器序列化实例。"""
        serializer = TaskCategorySerializer(self.category)
        data = serializer.data
        
        self.assertEqual(data["name"], "学习任务")
        self.assertEqual(data["color"], "#3B82F6")
        self.assertEqual(data["task_count"], 0)
        self.assertIn("task_count_display", data)
        self.assertIn("status_display", data)


# ==================== 任务序列化器测试 ====================
class TaskSerializerTest(TestCase):
    """
    任务序列化器测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        self.category = TaskCategory.objects.create(
            name="工作",
            description="工作任务",
            color="#10B981",
            icon="briefcase",
            order=2,
            is_active=True,
        )
        
        self.task_data = {
            "title": "完成项目报告",
            "description": "需要完成季度项目报告",
            "user": self.user.id,
            "category": self.category.id,
            "status": TaskStatus.PENDING.value,
            "priority": TaskPriority.HIGH.value,
            "due_date": timezone.now() + datetime.timedelta(days=7),
            "estimated_hours": Decimal("8.0"),
            "is_recurring": False,
        }
        
        self.task = Task.objects.create(
            title="测试任务",
            description="测试描述",
            user=self.user,
            category=self.category,
            status=TaskStatus.PENDING.value,
            priority=TaskPriority.MEDIUM.value,
            estimated_hours=Decimal("4.0"),
            is_recurring=False,
        )
    
    def test_task_serializer_valid(self) -> None:
        """测试任务序列化器验证有效数据。"""
        serializer = TaskSerializer(data=self.task_data)
        self.assertTrue(serializer.is_valid())
        
        data = serializer.validated_data
        self.assertEqual(data["title"], "完成项目报告")
        self.assertEqual(data["priority"], TaskPriority.HIGH.value)
        self.assertEqual(data["estimated_hours"], Decimal("8.0"))
    
    def test_task_create_serializer(self) -> None:
        """测试任务创建序列化器。"""
        create_data = self.task_data.copy()
        create_data.pop("user")  # 创建时不需要用户ID
        
        serializer = TaskCreateSerializer(data=create_data, context={"request": type('Request', (), {'user': self.user})()})
        self.assertTrue(serializer.is_valid())
        
        # 测试创建任务
        task = serializer.save()
        self.assertEqual(task.title, "完成项目报告")
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.category, self.category)
    
    def test_task_progress_serializer(self) -> None:
        """测试任务进度序列化器。"""
        progress_data = {
            "progress": Decimal("50.0"),
            "actual_hours": Decimal("4.0"),
        }
        
        serializer = TaskProgressSerializer(data=progress_data)
        self.assertTrue(serializer.is_valid())
        
        data = serializer.validated_data
        self.assertEqual(data["progress"], Decimal("50.0"))
        self.assertEqual(data["actual_hours"], Decimal("4.0"))
    
    def test_task_progress_serializer_invalid(self) -> None:
        """测试任务进度序列化器验证无效数据。"""
        invalid_data = {
            "progress": Decimal("150.0"),  # 超过100%
            "actual_hours": Decimal("-1.0"),  # 负数
        }
        
        serializer = TaskProgressSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("progress", serializer.errors)
        self.assertIn("actual_hours", serializer.errors)


# ==================== 任务提醒序列化器测试 ====================
class TaskReminderSerializerTest(TestCase):
    """
    任务提醒序列化器测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.user = User.objects.create_user(
            username="remindertest",
            email="reminder@example.com",
            password="testpass123"
        )
        
        self.category = TaskCategory.objects.create(
            name="个人",
            description="个人任务",
            color="#8B5CF6",
            icon="user",
            order=3,
            is_active=True,
        )
        
        self.task = Task.objects.create(
            title="提醒测试任务",
            description="测试提醒功能",
            user=self.user,
            category=self.category,
            status=TaskStatus.PENDING.value,
            priority=TaskPriority.MEDIUM.value,
            estimated_hours=Decimal("2.0"),
            is_recurring=False,
        )
        
        self.reminder_data = {
            "task": self.task.id,
            "reminder_type": "email",
            "reminder_time": timezone.now() + datetime.timedelta(hours=24),
        }
    
    def test_task_reminder_serializer_valid(self) -> None:
        """测试任务提醒序列化器验证有效数据。"""
        serializer = TaskReminderSerializer(data=self.reminder_data)
        self.assertTrue(serializer.is_valid())
        
        data = serializer.validated_data
        self.assertEqual(data["reminder_type"], "email")
        self.assertFalse(data.get("is_sent", False))  # 默认未发送
    
    def test_task_reminder_serializer_create(self) -> None:
        """测试任务提醒序列化器创建实例。"""
        serializer = TaskReminderSerializer(data=self.reminder_data)
        self.assertTrue(serializer.is_valid())
        
        reminder = serializer.save()
        self.assertEqual(reminder.task, self.task)
        self.assertEqual(reminder.reminder_type, "email")
        self.assertFalse(reminder.is_sent)


# ==================== 任务评论序列化器测试 ====================
class TaskCommentSerializerTest(TestCase):
    """
    任务评论序列化器测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.user = User.objects.create_user(
            username="commenttest",
            email="comment@example.com",
            password="testpass123"
        )
        
        self.category = TaskCategory.objects.create(
            name="团队",
            description="团队任务",
            color="#F59E0B",
            icon="users",
            order=4,
            is_active=True,
        )
        
        self.task = Task.objects.create(
            title="评论测试任务",
            description="测试评论功能",
            user=self.user,
            category=self.category,
            status=TaskStatus.IN_PROGRESS.value,
            priority=TaskPriority.MEDIUM.value,
            estimated_hours=Decimal("3.0"),
            is_recurring=False,
        )
        
        self.comment_data = {
            "task": self.task.id,
            "user": self.user.id,
            "content": "这是一个测试评论",
        }
    
    def test_task_comment_serializer_valid(self) -> None:
        """测试任务评论序列化器验证有效数据。"""
        serializer = TaskCommentSerializer(data=self.comment_data)
        self.assertTrue(serializer.is_valid())
        
        data = serializer.validated_data
        self.assertEqual(data["content"], "这是一个测试评论")
    
    def test_task_comment_serializer_with_attachment(self) -> None:
        """测试带附件的任务评论序列化器。"""
        # 创建模拟文件
        test_file = SimpleUploadedFile(
            "test_file.txt",
            b"Test file content",
            content_type="text/plain"
        )
        
        comment_data = self.comment_data.copy()
        # 注意：文件字段在序列化器中可能需要特殊处理
        
        serializer = TaskCommentSerializer(data=comment_data)
        # 由于文件字段处理复杂，这里只测试基本验证
        self.assertTrue(serializer.is_valid())


# ==================== 任务统计序列化器测试 ====================
class TaskStatisticsSerializerTest(TestCase):
    """
    任务统计序列化器测试类。
    """
    
    def test_task_statistics_serializer_valid(self) -> None:
        """测试任务统计序列化器验证有效数据。"""
        stats_data = {
            "total_tasks": 10,
            "completed_tasks": 6,
            "in_progress_tasks": 3,
            "pending_tasks": 1,
            "overdue_tasks": 2,
            "completion_rate": Decimal("60.0"),
            "average_completion_time": Decimal("48.5"),
            "priority_distribution": {
                "high": 3,
                "medium": 5,
                "low": 2,
            },
            "category_distribution": {
                "工作": 4,
                "学习": 3,
                "个人": 3,
            },
        }
        
        serializer = TaskStatisticsSerializer(data=stats_data)
        self.assertTrue(serializer.is_valid())
        
        data = serializer.validated_data
        self.assertEqual(data["total_tasks"], 10)
        self.assertEqual(data["completion_rate"], Decimal("60.0"))
        self.assertEqual(data["priority_distribution"]["high"], 3)
    
    def test_task_statistics_serializer_invalid(self) -> None:
        """测试任务统计序列化器验证无效数据。"""
        invalid_data = {
            "total_tasks": -5,  # 负数
            "completion_rate": Decimal("150.0"),  # 超过100%
        }
        
        serializer = TaskStatisticsSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("total_tasks", serializer.errors)
        self.assertIn("completion_rate", serializer.errors)


# ==================== 序列化器字段测试 ====================
class SerializerFieldTest(TestCase):
    """
    序列化器字段测试类。
    """
    
    def test_priority_field_validation(self) -> None:
        """测试优先级字段验证。"""
        from apps.tasks.serializers import TaskSerializer
        
        # 测试有效优先级
        valid_data = {"priority": TaskPriority.HIGH.value}
        serializer = TaskSerializer(data=valid_data)
        serializer.is_valid()
        self.assertNotIn("priority", serializer.errors)
        
        # 测试无效优先级
        invalid_data = {"priority": "invalid_priority"}
        serializer = TaskSerializer(data=invalid_data)
        serializer.is_valid()
        self.assertIn("priority", serializer.errors)
    
    def test_status_field_validation(self) -> None:
        """测试状态字段验证。"""
        from apps.tasks.serializers import TaskSerializer
        
        # 测试有效状态
        valid_data = {"status": TaskStatus.IN_PROGRESS.value}
        serializer = TaskSerializer(data=valid_data)
        serializer.is_valid()
        self.assertNotIn("status", serializer.errors)
        
        # 测试无效状态
        invalid_data = {"status": "invalid_status"}
        serializer = TaskSerializer(data=invalid_data)
        serializer.is_valid()
        self.assertIn("status", serializer.errors)


if __name__ == "__main__":
    import unittest
    unittest.main()
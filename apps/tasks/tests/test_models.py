"""
任务管理模型测试模块，测试任务、分类、提醒、评论等数据模型。
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

from apps.tasks.models import Task, TaskCategory, TaskComment, TaskReminder
from core.constants import TaskPriority, TaskStatus


User = get_user_model()


# ==================== 任务分类模型测试 ====================
class TaskCategoryModelTest(TestCase):
    """
    任务分类模型测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.task_category = TaskCategory.objects.create(
            name="学习任务",
            description="与学习相关的任务分类",
            color="#3B82F6",
            icon="book",
            order=1,
            is_active=True,
        )
    
    def test_task_category_creation(self) -> None:
        """测试任务分类创建。"""
        self.assertEqual(self.task_category.name, "学习任务")
        self.assertEqual(self.task_category.color, "#3B82F6")
        self.assertEqual(self.task_category.icon, "book")
        self.assertEqual(self.task_category.order, 1)
        self.assertTrue(self.task_category.is_active)
        self.assertTrue(self.task_category.pk)
    
    def test_task_category_str_method(self) -> None:
        """测试任务分类的字符串表示。"""
        self.assertEqual(str(self.task_category), "学习任务")
    
    def test_task_category_save_color_format(self) -> None:
        """测试保存时自动格式化颜色。"""
        category = TaskCategory.objects.create(
            name="测试颜色",
            color="FF5733",  # 不带#号
        )
        
        self.assertEqual(category.color, "#FF5733")
    
    def test_task_category_update_task_count(self) -> None:
        """测试更新任务数量统计。"""
        # 创建用户和任务
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        
        task = Task.objects.create(
            title="测试任务",
            user=user,
            category=self.task_category,
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
        )
        
        # 更新统计
        self.task_category.update_task_count()
        
        # 刷新从数据库获取最新数据
        self.task_category.refresh_from_db()
        self.assertEqual(self.task_category.task_count, 1)
        
        # 删除任务后更新统计
        task.delete()  # 软删除
        self.task_category.update_task_count()
        self.task_category.refresh_from_db()
        self.assertEqual(self.task_category.task_count, 0)


# ==================== 任务模型测试 ====================
class TaskModelTest(TestCase):
    """
    任务模型测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.user = User.objects.create_user(
            username="taskuser",
            email="task@example.com",
            password="testpass123",
        )
        
        self.category = TaskCategory.objects.create(
            name="测试分类",
            color="#FF5733",
        )
        
        self.task = Task.objects.create(
            title="测试任务",
            description="这是一个测试任务",
            user=self.user,
            category=self.category,
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            due_date=timezone.now() + datetime.timedelta(days=7),
            estimated_hours=Decimal("2.00"),
            progress_percentage=0,
            difficulty_level=3,
        )
    
    def test_task_creation(self) -> None:
        """测试任务创建。"""
        self.assertEqual(self.task.title, "测试任务")
        self.assertEqual(self.task.user, self.user)
        self.assertEqual(self.task.category, self.category)
        self.assertEqual(self.task.status, TaskStatus.PENDING)
        self.assertEqual(self.task.priority, TaskPriority.MEDIUM)
        self.assertEqual(self.task.progress_percentage, 0)
        self.assertTrue(self.task.pk)
    
    def test_task_str_method(self) -> None:
        """测试任务的字符串表示。"""
        expected_str = f"测试任务 - {self.user.username} (待处理)"
        self.assertEqual(str(self.task), expected_str)
    
    def test_task_is_overdue(self) -> None:
        """测试任务是否过期检查。"""
        # 未过期的任务
        self.assertFalse(self.task.is_overdue())
        
        # 创建已过期的任务
        overdue_task = Task.objects.create(
            title="过期任务",
            user=self.user,
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            due_date=timezone.now() - datetime.timedelta(days=1),
        )
        
        self.assertTrue(overdue_task.is_overdue())
        
        # 已完成的任务不过期
        completed_task = Task.objects.create(
            title="已完成任务",
            user=self.user,
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.LOW,
            due_date=timezone.now() - datetime.timedelta(days=1),
        )
        
        self.assertFalse(completed_task.is_overdue())
    
    def test_task_get_remaining_days(self) -> None:
        """测试获取剩余天数。"""
        # 有截止日期的任务
        remaining_days = self.task.get_remaining_days()
        self.assertIsNotNone(remaining_days)
        self.assertGreaterEqual(remaining_days, 0)
        self.assertLessEqual(remaining_days, 7)
        
        # 无截止日期的任务
        no_due_date_task = Task.objects.create(
            title="无截止日期任务",
            user=self.user,
            status=TaskStatus.PENDING,
        )
        
        self.assertIsNone(no_due_date_task.get_remaining_days())
        
        # 已过期的任务
        overdue_task = Task.objects.create(
            title="已过期任务",
            user=self.user,
            status=TaskStatus.PENDING,
            due_date=timezone.now() - datetime.timedelta(days=1),
        )
        
        self.assertIsNone(overdue_task.get_remaining_days())
    
    def test_task_get_time_spent_ratio(self) -> None:
        """测试获取时间花费比率。"""
        # 设置实际耗时
        self.task.actual_hours = Decimal("1.50")
        self.task.save()
        
        ratio = self.task.get_time_spent_ratio()
        expected_ratio = 1.50 / 2.00
        self.assertAlmostEqual(ratio, expected_ratio, places=2)
        
        # 预计耗时为0的情况
        zero_estimated_task = Task.objects.create(
            title="零预计耗时任务",
            user=self.user,
            status=TaskStatus.PENDING,
            estimated_hours=Decimal("0.00"),
        )
        
        self.assertEqual(zero_estimated_task.get_time_spent_ratio(), 0.0)
    
    def test_task_can_complete(self) -> None:
        """测试任务是否可以完成检查。"""
        # 新任务可以完成
        self.assertTrue(self.task.can_complete())
        
        # 已完成的任务不能再完成
        completed_task = Task.objects.create(
            title="已完成任务",
            user=self.user,
            status=TaskStatus.COMPLETED,
        )
        
        self.assertFalse(completed_task.can_complete())
    
    def test_task_mark_as_completed(self) -> None:
        """测试标记任务为完成。"""
        success = self.task.mark_as_completed()
        
        self.assertTrue(success)
        self.assertEqual(self.task.status, TaskStatus.COMPLETED)
        self.assertEqual(self.task.progress_percentage, 100)
        self.assertIsNotNone(self.task.completed_at)
        
        # 刷新从数据库获取最新数据
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, TaskStatus.COMPLETED)
    
    def test_task_mark_as_in_progress(self) -> None:
        """测试标记任务为进行中。"""
        self.task.mark_as_in_progress()
        
        self.assertEqual(self.task.status, TaskStatus.IN_PROGRESS)
        
        # 刷新从数据库获取最新数据
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, TaskStatus.IN_PROGRESS)
    
    def test_task_update_progress(self) -> None:
        """测试更新任务进度。"""
        # 更新进度
        self.task.update_progress(50, Decimal("1.00"))
        
        self.assertEqual(self.task.progress_percentage, 50)
        self.assertEqual(self.task.actual_hours, Decimal("1.00"))
        self.assertEqual(self.task.status, TaskStatus.IN_PROGRESS)
        
        # 更新到100%应该自动标记为完成
        self.task.update_progress(100)
        
        self.assertEqual(self.task.progress_percentage, 100)
        self.assertEqual(self.task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(self.task.completed_at)
    
    def test_task_soft_delete(self) -> None:
        """测试任务软删除。"""
        task_id = self.task.id
        
        # 软删除
        self.task.delete()
        
        # 刷新从数据库获取最新数据
        self.task.refresh_from_db()
        self.assertTrue(self.task.is_deleted)
        
        # 验证任务在普通查询中不可见
        visible_tasks = Task.objects.filter(is_deleted=False)
        self.assertNotIn(self.task, visible_tasks)
        
        # 验证任务在包含已删除的查询中可见
        all_tasks = Task.objects.all()
        self.assertIn(self.task, all_tasks)
    
    def test_task_validation(self) -> None:
        """测试任务验证。"""
        # 测试进度百分比验证
        task = Task(
            title="验证测试",
            user=self.user,
            status=TaskStatus.PENDING,
            progress_percentage=150,  # 超过100
        )
        
        with self.assertRaises(ValidationError):
            task.full_clean()
        
        # 测试难度等级验证
        task.progress_percentage = 50
        task.difficulty_level = 6  # 超过最大值5
        
        with self.assertRaises(ValidationError):
            task.full_clean()


# ==================== 任务提醒模型测试 ====================
class TaskReminderModelTest(TestCase):
    """
    任务提醒模型测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.user = User.objects.create_user(
            username="reminderuser",
            email="reminder@example.com",
            password="testpass123",
        )
        
        self.task = Task.objects.create(
            title="提醒测试任务",
            user=self.user,
            status=TaskStatus.PENDING,
            due_date=timezone.now() + datetime.timedelta(days=3),
        )
        
        self.task_reminder = TaskReminder.objects.create(
            task=self.task,
            reminder_time=timezone.now() + datetime.timedelta(hours=24),
            reminder_type="notification",
            reminder_message="记得完成任务",
            is_active=True,
        )
    
    def test_task_reminder_creation(self) -> None:
        """测试任务提醒创建。"""
        self.assertEqual(self.task_reminder.task, self.task)
        self.assertEqual(self.task_reminder.reminder_type, "notification")
        self.assertEqual(self.task_reminder.reminder_message, "记得完成任务")
        self.assertTrue(self.task_reminder.is_active)
        self.assertFalse(self.task_reminder.is_sent)
        self.assertTrue(self.task_reminder.pk)
    
    def test_task_reminder_str_method(self) -> None:
        """测试任务提醒的字符串表示。"""
        expected_time = self.task_reminder.reminder_time.strftime("%Y-%m-%d %H:%M")
        expected_str = f"{self.task.title} - {expected_time}"
        self.assertEqual(str(self.task_reminder), expected_str)
    
    def test_task_reminder_is_due(self) -> None:
        """测试提醒是否到期检查。"""
        # 未来的提醒未到期
        self.assertFalse(self.task_reminder.is_due())
        
        # 创建已到期的提醒
        due_reminder = TaskReminder.objects.create(
            task=self.task,
            reminder_time=timezone.now() - datetime.timedelta(hours=1),
            reminder_type="notification",
            is_active=True,
        )
        
        self.assertTrue(due_reminder.is_due())
        
        # 已发送的提醒不算到期
        due_reminder.is_sent = True
        due_reminder.save()
        self.assertFalse(due_reminder.is_due())
        
        # 停用的提醒不算到期
        due_reminder.is_sent = False
        due_reminder.is_active = False
        due_reminder.save()
        self.assertFalse(due_reminder.is_due())
    
    def test_task_reminder_mark_as_sent(self) -> None:
        """测试标记提醒为已发送。"""
        self.task_reminder.mark_as_sent()
        
        self.assertTrue(self.task_reminder.is_sent)
        self.assertIsNotNone(self.task_reminder.sent_at)
        
        # 刷新从数据库获取最新数据
        self.task_reminder.refresh_from_db()
        self.assertTrue(self.task_reminder.is_sent)
    
    def test_task_reminder_get_time_until_reminder(self) -> None:
        """测试获取距离提醒还有多少小时。"""
        hours = self.task_reminder.get_time_until_reminder()
        
        self.assertIsNotNone(hours)
        self.assertGreater(hours, 0)
        self.assertLess(hours, 25)  # 24小时内
    
    def test_task_reminder_can_send_now(self) -> None:
        """测试是否可以立即发送提醒。"""
        # 未来的提醒不能立即发送
        self.assertFalse(self.task_reminder.can_send_now())
        
        # 创建已到期的提醒
        due_reminder = TaskReminder.objects.create(
            task=self.task,
            reminder_time=timezone.now() - datetime.timedelta(minutes=30),
            reminder_type="notification",
            is_active=True,
        )
        
        self.assertTrue(due_reminder.can_send_now())
        
        # 已发送的提醒不能再次发送
        due_reminder.mark_as_sent()
        self.assertFalse(due_reminder.can_send_now())
        
        # 停用的提醒不能发送
        inactive_reminder = TaskReminder.objects.create(
            task=self.task,
            reminder_time=timezone.now() - datetime.timedelta(minutes=30),
            reminder_type="notification",
            is_active=False,
        )
        
        self.assertFalse(inactive_reminder.can_send_now())
        
        # 已完成任务的提醒不能发送
        completed_task = Task.objects.create(
            title="已完成任务",
            user=self.user,
            status=TaskStatus.COMPLETED,
        )
        
        reminder_for_completed = TaskReminder.objects.create(
            task=completed_task,
            reminder_time=timezone.now() - datetime.timedelta(minutes=30),
            reminder_type="notification",
            is_active=True,
        )
        
        self.assertFalse(reminder_for_completed.can_send_now())


# ==================== 任务评论模型测试 ====================
class TaskCommentModelTest(TestCase):
    """
    任务评论模型测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.user = User.objects.create_user(
            username="commentuser",
            email="comment@example.com",
            password="testpass123",
        )
        
        self.task = Task.objects.create(
            title="评论测试任务",
            user=self.user,
            status=TaskStatus.PENDING,
        )
        
        self.task_comment = TaskComment.objects.create(
            task=self.task,
            user=self.user,
            content="这是一个测试评论，用于验证评论功能是否正常工作。",
        )
    
    def test_task_comment_creation(self) -> None:
        """测试任务评论创建。"""
        self.assertEqual(self.task_comment.task, self.task)
        self.assertEqual(self.task_comment.user, self.user)
        self.assertEqual(
            self.task_comment.content,
            "这是一个测试评论，用于验证评论功能是否正常工作。"
        )
        self.assertFalse(self.task_comment.is_edited)
        self.assertIsNone(self.task_comment.edited_at)
        self.assertTrue(self.task_comment.pk)
    
    def test_task_comment_str_method(self) -> None:
        """测试任务评论的字符串表示。"""
        expected_str = f"{self.user.username} 评论于 {self.task.title}"
        self.assertEqual(str(self.task_comment), expected_str)
    
    def test_task_comment_get_short_content(self) -> None:
        """测试获取评论内容的简短版本。"""
        # 短内容
        short_comment = TaskComment.objects.create(
            task=self.task,
            user=self.user,
            content="短评论",
        )
        
        self.assertEqual(short_comment.get_short_content(), "短评论")
        
        # 长内容截断
        long_content = "这是一个非常长的评论内容，应该被截断到指定的长度，以便在列表中显示。"
        long_comment = TaskComment.objects.create(
            task=self.task,
            user=self.user,
            content=long_content,
        )
        
        short_version = long_comment.get_short_content(20)
        self.assertEqual(len(short_version), 23)  # 20个字符 + "..."
        self.assertTrue(short_version.endswith("..."))
    
    def test_task_comment_can_edit(self) -> None:
        """测试用户是否可以编辑评论。"""
        # 评论作者可以编辑
        self.assertTrue(self.task_comment.can_edit(self.user))
        
        # 其他用户不能编辑
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpass123",
        )
        
        self.assertFalse(self.task_comment.can_edit(other_user))
        
        # 管理员可以编辑
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        
        self.assertTrue(self.task_comment.can_edit(admin_user))
    
    def test_task_comment_can_delete(self) -> None:
        """测试用户是否可以删除评论。"""
        # 评论作者可以删除
        self.assertTrue(self.task_comment.can_delete(self.user))
        
        # 任务所有者可以删除
        task_owner = self.task.user
        self.assertTrue(self.task_comment.can_delete(task_owner))
        
        # 其他用户不能删除
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpass123",
        )
        
        self.assertFalse(self.task_comment.can_delete(other_user))
        
        # 管理员可以删除
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        
        self.assertTrue(self.task_comment.can_delete(admin_user))
    
    def test_task_comment_save_edit_marking(self) -> None:
        """测试保存时标记编辑状态。"""
        original_content = self.task_comment.content
        
        # 更新内容
        self.task_comment.content = "更新后的评论内容"
        self.task_comment.save()
        
        self.assertTrue(self.task_comment.is_edited)
        self.assertIsNotNone(self.task_comment.edited_at)
        
        # 刷新从数据库获取最新数据
        self.task_comment.refresh_from_db()
        self.assertTrue(self.task_comment.is_edited)
        self.assertNotEqual(self.task_comment.content, original_content)
        
        # 相同内容不标记为编辑
        current_content = self.task_comment.content
        self.task_comment.save()  # 内容未改变
        
        # 注意：由于auto_now=True，updated_at会变化，但is_edited不应该变化
        # 我们主要验证内容相同的情况
    
    def test_task_comment_validation(self) -> None:
        """测试任务评论验证。"""
        # 测试空内容验证
        comment = TaskComment(
            task=self.task,
            user=self.user,
            content="",  # 空内容
        )
        
        with self.assertRaises(ValidationError):
            comment.full_clean()
        
        # 测试内容长度验证
        long_content = "x" * 2001  # 超过2000字符
        comment.content = long_content
        
        with self.assertRaises(ValidationError):
            comment.full_clean()
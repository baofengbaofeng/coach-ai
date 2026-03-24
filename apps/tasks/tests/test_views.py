"""
任务管理视图测试模块，测试任务、分类、提醒、评论等API视图。
按照豆包AI助手最佳实践：使用Django REST Framework测试工具。
"""
from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.tasks.models import Task, TaskCategory, TaskComment, TaskReminder
from core.constants import TaskPriority, TaskStatus


User = get_user_model()


# ==================== 任务分类视图测试 ====================
class TaskCategoryViewSetTest(APITestCase):
    """
    任务分类视图集测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.user = User.objects.create_user(
            username="categorytest",
            email="category@example.com",
            password="testpass123",
            is_staff=True,  # 设置为管理员，有所有权限
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.category = TaskCategory.objects.create(
            name="测试分类",
            description="测试用分类",
            color="#3B82F6",
            icon="test",
            order=1,
            is_active=True,
        )
        
        self.category_data = {
            "name": "新分类",
            "description": "新的测试分类",
            "color": "#10B981",
            "icon": "new",
            "order": 2,
            "is_active": True,
        }
        
        self.list_url = reverse("tasks:taskcategory-list")
        self.detail_url = reverse("tasks:taskcategory-detail", args=[self.category.id])
    
    def test_list_task_categories(self) -> None:
        """测试获取任务分类列表。"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "测试分类")
    
    def test_create_task_category(self) -> None:
        """测试创建任务分类。"""
        response = self.client.post(self.list_url, self.category_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "新分类")
        self.assertEqual(response.data["color"], "#10B981")
        
        # 验证数据库
        self.assertEqual(TaskCategory.objects.count(), 2)
    
    def test_retrieve_task_category(self) -> None:
        """测试获取单个任务分类。"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "测试分类")
        self.assertEqual(response.data["id"], self.category.id)
    
    def test_update_task_category(self) -> None:
        """测试更新任务分类。"""
        update_data = {"name": "更新分类", "color": "#EF4444"}
        response = self.client.patch(self.detail_url, update_data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "更新分类")
        self.assertEqual(response.data["color"], "#EF4444")
        
        # 验证数据库更新
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "更新分类")
    
    def test_delete_task_category(self) -> None:
        """测试删除任务分类。"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 验证数据库
        self.assertEqual(TaskCategory.objects.count(), 0)
    
    def test_task_category_statistics(self) -> None:
        """测试任务分类统计端点。"""
        stats_url = reverse("tasks:taskcategory-statistics", args=[self.category.id])
        response = self.client.get(stats_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("task_count", response.data)
        self.assertIn("completion_rate", response.data)


# ==================== 任务视图测试 ====================
class TaskViewSetTest(APITestCase):
    """
    任务视图集测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.user = User.objects.create_user(
            username="tasktest",
            email="task@example.com",
            password="testpass123",
        )
        
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123",
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.category = TaskCategory.objects.create(
            name="工作",
            description="工作任务",
            color="#10B981",
            icon="briefcase",
            order=1,
            is_active=True,
        )
        
        self.task = Task.objects.create(
            title="测试任务",
            description="测试任务描述",
            user=self.user,
            category=self.category,
            status=TaskStatus.PENDING.value,
            priority=TaskPriority.MEDIUM.value,
            estimated_hours=Decimal("4.0"),
            is_recurring=False,
        )
        
        self.task_data = {
            "title": "新任务",
            "description": "新任务描述",
            "category": self.category.id,
            "status": TaskStatus.PENDING.value,
            "priority": TaskPriority.HIGH.value,
            "estimated_hours": "8.0",
            "is_recurring": False,
        }
        
        self.list_url = reverse("tasks:task-list")
        self.detail_url = reverse("tasks:task-detail", args=[self.task.id])
    
    def test_list_tasks(self) -> None:
        """测试获取任务列表。"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "测试任务")
    
    def test_create_task(self) -> None:
        """测试创建任务。"""
        response = self.client.post(self.list_url, self.task_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "新任务")
        self.assertEqual(response.data["priority"], TaskPriority.HIGH.value)
        
        # 验证数据库
        self.assertEqual(Task.objects.count(), 2)
        new_task = Task.objects.get(title="新任务")
        self.assertEqual(new_task.user, self.user)
    
    def test_retrieve_task(self) -> None:
        """测试获取单个任务。"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "测试任务")
        self.assertEqual(response.data["id"], self.task.id)
    
    def test_update_task(self) -> None:
        """测试更新任务。"""
        update_data = {
            "title": "更新任务",
            "status": TaskStatus.IN_PROGRESS.value,
            "progress": "50.0",
        }
        response = self.client.patch(self.detail_url, update_data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "更新任务")
        self.assertEqual(response.data["status"], TaskStatus.IN_PROGRESS.value)
        self.assertEqual(response.data["progress"], "50.0")
        
        # 验证数据库更新
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "更新任务")
        self.assertEqual(self.task.status, TaskStatus.IN_PROGRESS.value)
        self.assertEqual(self.task.progress, Decimal("50.0"))
    
    def test_delete_task(self) -> None:
        """测试删除任务。"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 验证数据库
        self.assertEqual(Task.objects.count(), 0)
    
    def test_task_permissions(self) -> None:
        """测试任务权限控制。"""
        # 其他用户尝试访问任务
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.detail_url)
        
        # 应该返回404或403，因为用户只能访问自己的任务
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])
    
    def test_task_progress_update(self) -> None:
        """测试任务进度更新端点。"""
        progress_url = reverse("tasks:task-progress", args=[self.task.id])
        progress_data = {"progress": "75.0", "actual_hours": "3.0"}
        
        response = self.client.post(progress_url, progress_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证数据库更新
        self.task.refresh_from_db()
        self.assertEqual(self.task.progress, Decimal("75.0"))
        self.assertEqual(self.task.actual_hours, Decimal("3.0"))
    
    def test_task_statistics(self) -> None:
        """测试任务统计端点。"""
        stats_url = reverse("tasks:task-statistics")
        response = self.client.get(stats_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_tasks", response.data)
        self.assertIn("completion_rate", response.data)
    
    def test_task_dashboard(self) -> None:
        """测试任务仪表板端点。"""
        dashboard_url = reverse("tasks:task-dashboard")
        response = self.client.get(dashboard_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("recent_tasks", response.data)
        self.assertIn("upcoming_deadlines", response.data)


# ==================== 任务提醒视图测试 ====================
class TaskReminderViewSetTest(APITestCase):
    """
    任务提醒视图集测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.user = User.objects.create_user(
            username="remindertest",
            email="reminder@example.com",
            password="testpass123",
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.category = TaskCategory.objects.create(
            name="个人",
            description="个人任务",
            color="#8B5CF6",
            icon="user",
            order=1,
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
        
        self.reminder = TaskReminder.objects.create(
            task=self.task,
            reminder_type="email",
            reminder_time=timezone.now() + datetime.timedelta(hours=24),
            is_sent=False,
        )
        
        self.reminder_data = {
            "task": self.task.id,
            "reminder_type": "notification",
            "reminder_time": (timezone.now() + datetime.timedelta(hours=12)).isoformat(),
        }
        
        self.list_url = reverse("tasks:taskreminder-list")
        self.detail_url = reverse("tasks:taskreminder-detail", args=[self.reminder.id])
    
    def test_list_task_reminders(self) -> None:
        """测试获取任务提醒列表。"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["reminder_type"], "email")
    
    def test_create_task_reminder(self) -> None:
        """测试创建任务提醒。"""
        response = self.client.post(self.list_url, self.reminder_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["reminder_type"], "notification")
        
        # 验证数据库
        self.assertEqual(TaskReminder.objects.count(), 2)
    
    def test_update_reminder_status(self) -> None:
        """测试更新提醒状态端点。"""
        status_url = reverse("tasks:taskreminder-status", args=[self.reminder.id])
        status_data = {"is_sent": True}
        
        response = self.client.post(status_url, status_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证数据库更新
        self.reminder.refresh_from_db()
        self.assertTrue(self.reminder.is_sent)


# ==================== 任务评论视图测试 ====================
class TaskCommentViewSetTest(APITestCase):
    """
    任务评论视图集测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.user = User.objects.create_user(
            username="commenttest",
            email="comment@example.com",
            password="testpass123",
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.category = TaskCategory.objects.create(
            name="团队",
            description="团队任务",
            color="#F59E0B",
            icon="users",
            order=1,
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
        
        self.comment = TaskComment.objects.create(
            task=self.task,
            user=self.user,
            content="初始评论",
        )
        
        self.comment_data = {
            "task": self.task.id,
            "content": "新的测试评论",
        }
        
        self.list_url = reverse("tasks:taskcomment-list")
        self.detail_url = reverse("tasks:taskcomment-detail", args=[self.comment.id])
    
    def test_list_task_comments(self) -> None:
        """测试获取任务评论列表。"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["content"], "初始评论")
    
    def test_create_task_comment(self) -> None:
        """测试创建任务评论。"""
        response = self.client.post(self.list_url, self.comment_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], "新的测试评论")
        
        # 验证数据库
        self.assertEqual(TaskComment.objects.count(), 2)
        new_comment = TaskComment.objects.get(content="新的测试评论")
        self.assertEqual(new_comment.user, self.user)
    
    def test_task_comment_permissions(self) -> None:
        """测试任务评论权限。"""
        # 创建另一个用户
        other_user = User.objects.create_user(
            username="othercomment",
            email="othercomment@example.com",
            password="testpass123",
        )
        
        # 其他用户尝试删除评论
        self.client.force_authenticate(user=other_user)
        response = self.client.delete(self.detail_url)
        
        # 应该返回403或404，因为用户只能删除自己的评论
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])


# ==================== API过滤和搜索测试 ====================
class TaskAPIFilterTest(APITestCase):
    """
    API过滤和搜索测试类。
    """
    
    def setUp(self) -> None:
        """测试前的准备工作。"""
        self.user = User.objects.create_user(
            username="filtertest",
            email="filter@example.com",
            password="testpass123",
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.category = TaskCategory.objects.create(
            name="过滤测试",
            description="过滤测试分类",
            color="#000000",
            icon="filter",
            order=1,
            is_active=True,
        )
        
        # 创建多个测试任务
        self.tasks = [
            Task.objects.create(
                title=f"任务{i}",
                description=f"描述{i}",
                user=self.user,
                category=self.category,
                status=TaskStatus.PENDING.value if i % 2 == 0 else TaskStatus.COMPLETED.value,
                priority=TaskPriority.HIGH.value if i < 3 else TaskPriority.LOW.value,
                estimated_hours=Decimal(f"{i+1}.0"),
                is_recurring=(i % 3 == 0),
            )
            for i in range(5)
        ]
        
        self.list_url = reverse("tasks:task-list")
    
    def test_filter_by_status(self) -> None:
        """测试按状态过滤任务。"""
        response = self.client.get(self.list_url, {"status": TaskStatus.PENDING.value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 应该返回3个待处理任务（索引0,2,4）
        self.assertEqual(len(response.data), 3)
        for task in response.data:
            self.assertEqual(task["status"], TaskStatus.PENDING.value)
    
    def test_filter_by_priority(self) -> None:
        """测试按优先级过滤任务。"""
        response = self.client.get(self.list_url, {"priority": TaskPriority.HIGH.value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 应该返回3个高优先级任务（索引0,1,2）
        self.assertEqual(len(response.data), 3)
        for task in response.data:
            self.assertEqual(task["priority"], TaskPriority.HIGH.value)
    
    def test_search_by_title(self) -> None:
        """测试按标题搜索任务。"""
        response = self.client.get(self.list_url, {"search": "任务1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 应该返回标题包含"任务1"的任务
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "任务1")
    
    def test_ordering(self) -> None:
        """测试任务排序。"""
        response = self.client.get(self.list_url, {"ordering": "-created_at"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证按创建时间降序排列
        titles = [task["title"] for task in response.data]
        self.assertEqual(titles, ["任务4", "任务3", "任务2", "任务1", "任务0"])


# ==================== 测试运行 ====================
if __name__ == "__main__":
    import unittest
    unittest.main()

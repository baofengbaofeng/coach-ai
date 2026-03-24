"""
任务管理视图模块，定义任务相关的API端点和处理逻辑。
按照豆包AI助手最佳实践：使用Django REST Framework视图集。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.db.models import Avg, Count, Q, QuerySet, Sum
from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.tasks.models import Task, TaskCategory, TaskComment, TaskReminder
from apps.tasks.serializers import (
    TaskCategorySerializer,
    TaskCommentSerializer,
    TaskCreateSerializer,
    TaskProgressSerializer,
    TaskReminderSerializer,
    TaskSerializer,
    TaskStatisticsSerializer,
)
from core.constants import TaskPriority, TaskStatus
from core.permissions import IsOwnerOrReadOnly, IsOwnerOrTeacherOrAdmin


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 任务分类视图集 ====================
class TaskCategoryViewSet(viewsets.ModelViewSet):
    """
    任务分类视图集类，提供任务分类的CRUD操作。
    """
    
    serializer_class = TaskCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["order", "name", "task_count", "created_at"]
    ordering = ["order", "name"]
    
    def get_queryset(self) -> QuerySet[TaskCategory]:
        """获取任务分类查询集。"""
        queryset = TaskCategory.objects.all()
        
        # 状态过滤
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=(is_active.lower() == "true"))
        
        return queryset
    
    def perform_create(self, serializer: TaskCategorySerializer) -> None:
        """创建任务分类。"""
        serializer.save()
    
    @action(detail=True, methods=["POST"])
    def activate(self, request: Request, pk: Optional[int] = None) -> Response:
        """激活任务分类。"""
        task_category = self.get_object()
        
        if task_category.is_active:
            return Response(
                {"error": "任务分类已经是激活状态"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        task_category.is_active = True
        task_category.save()
        
        _LOGGER.info("任务分类激活: %s (ID: %s)", task_category.name, task_category.id)
        
        serializer = self.get_serializer(task_category)
        return Response(serializer.data)
    
    @action(detail=True, methods=["POST"])
    def deactivate(self, request: Request, pk: Optional[int] = None) -> Response:
        """停用任务分类。"""
        task_category = self.get_object()
        
        if not task_category.is_active:
            return Response(
                {"error": "任务分类已经是停用状态"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        task_category.is_active = False
        task_category.save()
        
        _LOGGER.info("任务分类停用: %s (ID: %s)", task_category.name, task_category.id)
        
        serializer = self.get_serializer(task_category)
        return Response(serializer.data)
    
    @action(detail=False, methods=["GET"])
    def statistics(self, request: Request) -> Response:
        """获取任务分类统计信息。"""
        queryset = self.get_queryset()
        
        # 基础统计
        total_count = queryset.count()
        active_count = queryset.filter(is_active=True).count()
        
        # 按任务数量排序
        top_categories = (
            queryset.filter(is_active=True)
            .order_by("-task_count")
            .values("id", "name", "task_count")[:10]
        )
        
        # 任务数量分布
        task_count_ranges = [
            (0, 10, "少量"),
            (10, 50, "中等"),
            (50, 100, "较多"),
            (100, None, "大量"),
        ]
        
        count_distribution = []
        for min_count, max_count, label in task_count_ranges:
            if max_count is None:
                filter_q = Q(task_count__gte=min_count)
            else:
                filter_q = Q(task_count__gte=min_count, task_count__lt=max_count)
            
            count = queryset.filter(filter_q).count()
            count_distribution.append({
                "range": f"{min_count}+" if max_count is None else f"{min_count}-{max_count}",
                "label": label,
                "count": count,
                "percentage": (count / total_count * 100) if total_count > 0 else 0,
            })
        
        return Response({
            "total_count": total_count,
            "active_count": active_count,
            "inactive_count": total_count - active_count,
            "active_rate": (active_count / total_count * 100) if total_count > 0 else 0,
            "top_categories": list(top_categories),
            "task_count_distribution": count_distribution,
        })


# ==================== 任务视图集 ====================
class TaskViewSet(viewsets.ModelViewSet):
    """
    任务视图集类，提供任务的CRUD操作。
    """
    
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "notes", "tags"]
    ordering_fields = [
        "created_at",
        "updated_at",
        "due_date",
        "priority",
        "progress_percentage",
        "estimated_hours",
        "actual_hours",
    ]
    ordering = ["-created_at"]
    
    def get_queryset(self) -> QuerySet[Task]:
        """获取任务查询集，根据用户角色和权限过滤。"""
        user = self.request.user
        queryset = Task.objects.select_related("user", "category", "parent_task")
        
        # 用户只能查看自己的任务
        if user.role == "student":
            queryset = queryset.filter(user=user)
        # 老师和家长可以查看所有任务
        elif user.role in ["teacher", "parent"]:
            pass  # 不进行过滤
        # 管理员可以查看所有任务
        elif user.is_superuser:
            pass  # 不进行过滤
        else:
            queryset = queryset.none()
        
        # 排除已删除的任务
        queryset = queryset.filter(is_deleted=False)
        
        # 状态过滤
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 优先级过滤
        priority_filter = self.request.query_params.get("priority")
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        # 分类过滤
        category_id = self.request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # 是否重要过滤
        is_important = self.request.query_params.get("is_important")
        if is_important is not None:
            queryset = queryset.filter(is_important=(is_important.lower() == "true"))
        
        # 是否紧急过滤
        is_urgent = self.request.query_params.get("is_urgent")
        if is_urgent is not None:
            queryset = queryset.filter(is_urgent=(is_urgent.lower() == "true"))
        
        # 是否过期过滤
        is_overdue = self.request.query_params.get("is_overdue")
        if is_overdue is not None:
            if is_overdue.lower() == "true":
                queryset = queryset.filter(
                    due_date__lt=timezone.now(),
                    status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
                )
            elif is_overdue.lower() == "false":
                queryset = queryset.filter(
                    Q(due_date__gte=timezone.now()) | Q(due_date__isnull=True) |
                    Q(status__in=[TaskStatus.COMPLETED, TaskStatus.CANCELLED])
                )
        
        # 时间范围过滤
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            queryset = queryset.filter(due_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(due_date__date__lte=end_date)
        
        # 父任务过滤
        parent_task_id = self.request.query_params.get("parent_task_id")
        if parent_task_id:
            if parent_task_id == "null":
                queryset = queryset.filter(parent_task__isnull=True)
            else:
                queryset = queryset.filter(parent_task_id=parent_task_id)
        
        # 标签过滤
        tag = self.request.query_params.get("tag")
        if tag:
            queryset = queryset.filter(tags__contains=[tag])
        
        return queryset
    
    def get_serializer_class(self):
        """根据动作选择序列化器。"""
        if self.action == "create":
            return TaskCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer: TaskSerializer) -> None:
        """创建任务时自动设置用户。"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=["POST"])
    def update_progress(self, request: Request, pk: Optional[int] = None) -> Response:
        """更新任务进度。"""
        task = self.get_object()
        serializer = TaskProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            updated_task = serializer.save(task_id=task.id)
            
            # 返回更新后的任务信息
            task_serializer = self.get_serializer(updated_task)
            return Response(task_serializer.data)
        except Exception as e:
            _LOGGER.error("更新任务进度失败: %s", str(e))
            return Response(
                {"error": "更新进度失败"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=True, methods=["POST"])
    def mark_as_completed(self, request: Request, pk: Optional[int] = None) -> Response:
        """标记任务为完成。"""
        task = self.get_object()
        
        if not task.can_complete():
            return Response(
                {"error": "任务当前不能标记为完成"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        success = task.mark_as_completed()
        
        if success:
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        else:
            return Response(
                {"error": "标记任务为完成失败"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    @action(detail=True, methods=["POST"])
    def mark_as_in_progress(self, request: Request, pk: Optional[int] = None) -> Response:
        """标记任务为进行中。"""
        task = self.get_object()
        
        if task.status == TaskStatus.IN_PROGRESS:
            return Response(
                {"error": "任务已经是进行中状态"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        task.mark_as_in_progress()
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=["POST"])
    def cancel(self, request: Request, pk: Optional[int] = None) -> Response:
        """取消任务。"""
        task = self.get_object()
        
        if task.status == TaskStatus.CANCELLED:
            return Response(
                {"error": "任务已经是取消状态"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if task.status == TaskStatus.COMPLETED:
            return Response(
                {"error": "已完成的任务不能取消"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        task.status = TaskStatus.CANCELLED
        task.save()
        
        _LOGGER.info("任务取消: %s (ID: %s)", task.title, task.id)
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=["POST"])
    def soft_delete(self, request: Request, pk: Optional[int] = None) -> Response:
        """软删除任务。"""
        task = self.get_object()
        
        if task.is_deleted:
            return Response(
                {"error": "任务已经是删除状态"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        task.delete()  # 调用模型的软删除方法
        
        return Response(
            {"message": "任务已删除"},
            status=status.HTTP_200_OK,
        )
    
    @action(detail=True, methods=["GET"])
    def subtasks(self, request: Request, pk: Optional[int] = None) -> Response:
        """获取任务的子任务列表。"""
        task = self.get_object()
        subtasks = task.subtasks.filter(is_deleted=False)
        
        page = self.paginate_queryset(subtasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(subtasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["GET"])
    def statistics(self, request: Request) -> Response:
        """获取任务统计信息。"""
        user = request.user
        queryset = self.get_queryset()
        
        # 基础统计
        total_tasks = queryset.count()
        completed_tasks = queryset.filter(status=TaskStatus.COMPLETED).count()
        in_progress_tasks = queryset.filter(status=TaskStatus.IN_PROGRESS).count()
        overdue_tasks = queryset.filter(
            due_date__lt=timezone.now(),
            status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
        ).count()
        
        # 计算完成率
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # 计算平均进度
        average_progress = queryset.aggregate(avg=Avg("progress_percentage"))["avg"] or 0
        
        # 优先级分布
        priority_distribution = (
            queryset.values("priority")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        
        # 状态分布
        status_distribution = (
            queryset.values("status")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        
        # 分类分布
        category_distribution = (
            queryset.filter(category__isnull=False)
            .values("category__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
        
        # 周趋势（最近8周）
        eight_weeks_ago = timezone.now() - timezone.timedelta(weeks=8)
        weekly_trend = (
            queryset.filter(created_at__gte=eight_weeks_ago)
            .extra({"week": "strftime('%Y-%W', created_at)"})
            .values("week")
            .annotate(
                count=Count("id"),
                completed=Count("id", filter=Q(status=TaskStatus.COMPLETED)),
            )
            .order_by("week")
        )
        
        # 计算每周完成率
        for week in weekly_trend:
            week["completion_rate"] = (
                (week["completed"] / week["count"] * 100) if week["count"] > 0 else 0
            )
        
        statistics_data = {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "overdue_tasks": overdue_tasks,
            "completion_rate": completion_rate,
            "average_progress": average_progress,
            "priority_distribution": list(priority_distribution),
            "status_distribution": list(status_distribution),
            "category_distribution": list(category_distribution),
            "weekly_trend": list(weekly_trend),
            "user": {
                "username": user.username,
                "role": user.role,
            },
        }
        
        serializer = TaskStatisticsSerializer(data=statistics_data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=["GET"])
    def dashboard(self, request: Request) -> Response:
        """获取任务仪表板数据。"""
        user = request.user
        queryset = self.get_queryset()
        
        # 今日任务
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timezone.timedelta(days=1)
        
        today_tasks = queryset.filter(
            due_date__gte=today_start,
            due_date__lt=today_end,
            status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
        )
        
        # 本周任务
        week_start = today_start - timezone.timedelta(days=today_start.weekday())
        week_tasks = queryset.filter(
            due_date__gte=week_start,
            due_date__lt=week_start + timezone.timedelta(days=7),
            status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
        )
        
        # 重要且紧急的任务（四象限法）
        important_urgent = queryset.filter(
            is_important=True,
            is_urgent=True,
            status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
        ).order_by("due_date")[:10]
        
        important_not_urgent = queryset.filter(
            is_important=True,
            is_urgent=False,
            status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
        ).order_by("due_date")[:10]
        
        not_important_urgent = queryset.filter(
            is_important=False,
            is_urgent=True,
            status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
        ).order_by("due_date")[:10]
        
        not_important_not_urgent = queryset.filter(
            is_important=False,
            is_urgent=False,
            status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
        ).order_by("due_date")[:10]
        
        # 即将过期的任务（3天内）
        three_days_later = timezone.now() + timezone.timedelta(days=3)
        upcoming_deadlines = queryset.filter(
            due_date__gte=timezone.now(),
            due_date__lte=three_days_later,
            status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
        ).order_by("due_date")[:10]
        
        # 最近完成的任务
        recently_completed = queryset.filter(
            status=TaskStatus.COMPLETED,
            completed_at__gte=timezone.now() - timezone.timedelta(days=7),
        ).order_by("-completed_at")[:10]
        
        # 序列化数据
        task_serializer = self.get_serializer
        
        return Response({
            "today": {
                "count": today_tasks.count(),
                "tasks": task_serializer(today_tasks[:10], many=True).data,
            },
            "this_week": {
                "count": week_tasks.count(),
                "tasks": task_serializer(week_tasks[:10], many=True).data,
            },
            "quadrant_1_important_urgent": {
                "count": important_urgent.count(),
                "tasks": task_serializer(important_urgent, many=True).data,
            },
            "quadrant_2_important_not_urgent": {
                "count": important_not_urgent.count(),
                "tasks": task_serializer(important_not_urgent, many=True).data,
            },
            "quadrant_3_not_important_urgent": {
                "count": not_important_urgent.count(),
                "tasks": task_serializer(not_important_urgent, many=True).data,
            },
            "quadrant_4_not_important_not_urgent": {
                "count": not_important_not_urgent.count(),
                "tasks": task_serializer(not_important_not_urgent, many=True).data,
            },
            "upcoming_deadlines": {
                "count": upcoming_deadlines.count(),
                "tasks": task_serializer(upcoming_deadlines, many=True).data,
            },
            "recently_completed": {
                "count": recently_completed.count(),
                "tasks": task_serializer(recently_completed, many=True).data,
            },
            "summary": {
                "total_tasks": queryset.count(),
                "completed_tasks": queryset.filter(status=TaskStatus.COMPLETED).count(),
                "in_progress_tasks": queryset.filter(status=TaskStatus.IN_PROGRESS).count(),
                "overdue_tasks": queryset.filter(
                    due_date__lt=timezone.now(),
                    status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
                ).count(),
            },
        })


# ==================== 任务提醒视图集 ====================
class TaskReminderViewSet(viewsets.ModelViewSet):
    """
    任务提醒视图集类，提供任务提醒的CRUD操作。
    """
    
    serializer_class = TaskReminderSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ["reminder_time", "created_at", "updated_at"]
    ordering = ["reminder_time"]
    
    def get_queryset(self) -> QuerySet[TaskReminder]:
        """获取任务提醒查询集，根据用户权限过滤。"""
        user = self.request.user
        queryset = TaskReminder.objects.select_related("task", "task__user")
        
        # 用户只能查看自己任务的提醒
        if user.role == "student":
            queryset = queryset.filter(task__user=user)
        # 老师和家长可以查看所有提醒
        elif user.role in ["teacher", "parent"]:
            pass  # 不进行过滤
        # 管理员可以查看所有提醒
        elif user.is_superuser:
            pass  # 不进行过滤
        else:
            queryset = queryset.none()
        
        # 状态过滤
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=(is_active.lower() == "true"))
        
        is_sent = self.request.query_params.get("is_sent")
        if is_sent is not None:
            queryset = queryset.filter(is_sent=(is_sent.lower() == "true"))
        
        # 任务过滤
        task_id = self.request.query_params.get("task_id")
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        
        # 时间范围过滤
        start_time = self.request.query_params.get("start_time")
        end_time = self.request.query_params.get("end_time")
        if start_time:
            queryset = queryset.filter(reminder_time__gte=start_time)
        if end_time:
            queryset = queryset.filter(reminder_time__lte=end_time)
        
        return queryset
    
    def perform_create(self, serializer: TaskReminderSerializer) -> None:
        """创建任务提醒。"""
        serializer.save()
    
    @action(detail=True, methods=["POST"])
    def mark_as_sent(self, request: Request, pk: Optional[int] = None) -> Response:
        """标记提醒为已发送。"""
        task_reminder = self.get_object()
        
        if task_reminder.is_sent:
            return Response(
                {"error": "提醒已经是已发送状态"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        task_reminder.mark_as_sent()
        serializer = self.get_serializer(task_reminder)
        return Response(serializer.data)
    
    @action(detail=True, methods=["POST"])
    def activate(self, request: Request, pk: Optional[int] = None) -> Response:
        """激活提醒。"""
        task_reminder = self.get_object()
        
        if task_reminder.is_active:
            return Response(
                {"error": "提醒已经是激活状态"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        task_reminder.is_active = True
        task_reminder.save()
        
        _LOGGER.info("任务提醒激活: ID=%s", task_reminder.id)
        
        serializer = self.get_serializer(task_reminder)
        return Response(serializer.data)
    
    @action(detail=True, methods=["POST"])
    def deactivate(self, request: Request, pk: Optional[int] = None) -> Response:
        """停用提醒。"""
        task_reminder = self.get_object()
        
        if not task_reminder.is_active:
            return Response(
                {"error": "提醒已经是停用状态"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        task_reminder.is_active = False
        task_reminder.save()
        
        _LOGGER.info("任务提醒停用: ID=%s", task_reminder.id)
        
        serializer = self.get_serializer(task_reminder)
        return Response(serializer.data)
    
    @action(detail=False, methods=["GET"])
    def due_reminders(self, request: Request) -> Response:
        """获取到期的提醒。"""
        queryset = self.get_queryset()
        due_reminders = queryset.filter(
            reminder_time__lte=timezone.now(),
            is_active=True,
            is_sent=False,
        ).order_by("reminder_time")
        
        page = self.paginate_queryset(due_reminders)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(due_reminders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["GET"])
    def upcoming_reminders(self, request: Request) -> Response:
        """获取即将到期的提醒（24小时内）。"""
        twenty_four_hours_later = timezone.now() + timezone.timedelta(hours=24)
        
        queryset = self.get_queryset()
        upcoming_reminders = queryset.filter(
            reminder_time__gte=timezone.now(),
            reminder_time__lte=twenty_four_hours_later,
            is_active=True,
            is_sent=False,
        ).order_by("reminder_time")
        
        page = self.paginate_queryset(upcoming_reminders)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(upcoming_reminders, many=True)
        return Response(serializer.data)


# ==================== 任务评论视图集 ====================
class TaskCommentViewSet(viewsets.ModelViewSet):
    """
    任务评论视图集类，提供任务评论的CRUD操作。
    """
    
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["content"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    
    def get_queryset(self) -> QuerySet[TaskComment]:
        """获取任务评论查询集，根据用户权限过滤。"""
        user = self.request.user
        queryset = TaskComment.objects.select_related("task", "user", "task__user")
        
        # 用户只能查看自己任务或自己参与的评论
        if user.role == "student":
            queryset = queryset.filter(
                Q(task__user=user) | Q(user=user)
            )
        # 老师和家长可以查看所有评论
        elif user.role in ["teacher", "parent"]:
            pass  # 不进行过滤
        # 管理员可以查看所有评论
        elif user.is_superuser:
            pass  # 不进行过滤
        else:
            queryset = queryset.none()
        
        # 任务过滤
        task_id = self.request.query_params.get("task_id")
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        
        # 用户过滤
        user_id = self.request.query_params.get("user_id")
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset
    
    def perform_create(self, serializer: TaskCommentSerializer) -> None:
        """创建任务评论时自动设置用户。"""
        serializer.save(user=self.request.user)
    
    def get_permissions(self):
        """根据动作调整权限。"""
        if self.action in ["update", "partial_update", "destroy"]:
            # 对于更新和删除操作，需要额外的权限检查
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return super().get_permissions()
    
    def check_object_permissions(self, request: Request, obj: TaskComment) -> None:
        """检查对象权限。"""
        super().check_object_permissions(request, obj)
        
        # 额外的权限检查
        if self.action in ["update", "partial_update"]:
            if not obj.can_edit(request.user):
                self.permission_denied(
                    request,
                    message="您没有权限编辑此评论",
                    code="no_edit_permission",
                )
        
        elif self.action == "destroy":
            if not obj.can_delete(request.user):
                self.permission_denied(
                    request,
                    message="您没有权限删除此评论",
                    code="no_delete_permission",
                )
    
    @action(detail=False, methods=["GET"])
    def recent_comments(self, request: Request) -> Response:
        """获取最近评论。"""
        queryset = self.get_queryset()
        recent_comments = queryset.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=7),
        ).order_by("-created_at")[:20]
        
        serializer = self.get_serializer(recent_comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["GET"])
    def task_comments(self, request: Request, pk: Optional[int] = None) -> Response:
        """获取特定任务的所有评论。"""
        from apps.tasks.models import Task
        
        try:
            task = Task.objects.get(id=pk)
            
            # 检查权限
            if not self._has_task_permission(request.user, task):
                return Response(
                    {"error": "您没有权限查看此任务的评论"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            
            comments = task.comments.all().order_by("-created_at")
            
            page = self.paginate_queryset(comments)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(comments, many=True)
            return Response(serializer.data)
            
        except Task.DoesNotExist:
            return Response(
                {"error": "任务不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )
    
    def _has_task_permission(self, user, task) -> bool:
        """检查用户是否有任务权限。"""
        if user.role == "student":
            return task.user == user
        elif user.role in ["teacher", "parent"]:
            return True
        elif user.is_superuser:
            return True
        return False

"""
作业管理视图模块，定义作业相关的API端点和处理逻辑。
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

from apps.homework.models import Homework, KnowledgePoint, Question
from apps.homework.serializers import (
    HomeworkCorrectionSerializer,
    HomeworkSerializer,
    HomeworkSubmitSerializer,
    KnowledgePointSerializer,
    QuestionSerializer,
)
from core.constants import HomeworkStatus
from core.permissions import IsOwnerOrReadOnly, IsTeacherOrAdmin


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 知识点视图集 ====================
class KnowledgePointViewSet(viewsets.ModelViewSet):
    """
    知识点视图集类，提供知识点的CRUD操作。
    """
    
    queryset = KnowledgePoint.objects.all()
    serializer_class = KnowledgePointSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "subject"]
    ordering_fields = ["name", "subject", "difficulty_level", "created_at"]
    ordering = ["subject", "difficulty_level", "name"]
    
    def get_queryset(self) -> QuerySet[KnowledgePoint]:
        """获取知识点查询集，支持按科目和难度过滤。"""
        queryset = super().get_queryset()
        
        # 科目过滤
        subject = self.request.query_params.get("subject")
        if subject:
            queryset = queryset.filter(subject=subject)
        
        # 难度等级过滤
        difficulty = self.request.query_params.get("difficulty")
        if difficulty and difficulty.isdigit():
            queryset = queryset.filter(difficulty_level=int(difficulty))
        
        # 最小难度过滤
        min_difficulty = self.request.query_params.get("min_difficulty")
        if min_difficulty and min_difficulty.isdigit():
            queryset = queryset.filter(difficulty_level__gte=int(min_difficulty))
        
        # 最大难度过滤
        max_difficulty = self.request.query_params.get("max_difficulty")
        if max_difficulty and max_difficulty.isdigit():
            queryset = queryset.filter(difficulty_level__lte=int(max_difficulty))
        
        return queryset
    
    @action(detail=True, methods=["GET"])
    def related_homeworks(self, request: Request, pk: Optional[int] = None) -> Response:
        """获取涉及该知识点的所有作业。"""
        knowledge_point = self.get_object()
        homeworks = knowledge_point.get_related_homeworks()
        
        # 分页处理
        page = self.paginate_queryset(homeworks)
        if page is not None:
            serializer = HomeworkSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        
        serializer = HomeworkSerializer(homeworks, many=True, context={"request": request})
        return Response(serializer.data)
    
    @action(detail=True, methods=["GET"])
    def mastery_rate(self, request: Request, pk: Optional[int] = None) -> Response:
        """获取当前用户对该知识点的掌握率。"""
        knowledge_point = self.get_object()
        student_id = request.user.id
        
        try:
            mastery_rate = knowledge_point.get_mastery_rate(student_id)
            return Response({"mastery_rate": mastery_rate})
        except Exception as e:
            _LOGGER.error("获取知识点掌握率失败: %s", str(e))
            return Response(
                {"error": "获取掌握率失败"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ==================== 题目视图集 ====================
class QuestionViewSet(viewsets.ModelViewSet):
    """
    题目视图集类，提供题目的CRUD操作。
    """
    
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["content", "student_answer", "correct_answer", "correction_notes"]
    ordering_fields = ["question_number", "max_score", "actual_score", "created_at"]
    ordering = ["question_number"]
    
    def get_queryset(self) -> QuerySet[Question]:
        """获取题目查询集，根据用户角色和权限过滤。"""
        user = self.request.user
        queryset = Question.objects.select_related("homework", "homework__student")
        
        # 学生只能查看自己的题目
        if user.role == "student":
            queryset = queryset.filter(homework__student=user)
        # 老师和家长可以查看所有题目
        elif user.role in ["teacher", "parent"]:
            pass  # 不进行过滤
        # 管理员可以查看所有题目
        elif user.is_superuser:
            pass  # 不进行过滤
        else:
            queryset = queryset.none()
        
        # 作业ID过滤
        homework_id = self.request.query_params.get("homework_id")
        if homework_id and homework_id.isdigit():
            queryset = queryset.filter(homework_id=int(homework_id))
        
        # 题目类型过滤
        question_type = self.request.query_params.get("question_type")
        if question_type:
            queryset = queryset.filter(question_type=question_type)
        
        # 正确性过滤
        is_correct = self.request.query_params.get("is_correct")
        if is_correct is not None:
            queryset = queryset.filter(is_correct=(is_correct.lower() == "true"))
        
        # 知识点过滤
        knowledge_point_id = self.request.query_params.get("knowledge_point_id")
        if knowledge_point_id and knowledge_point_id.isdigit():
            queryset = queryset.filter(knowledge_points__id=int(knowledge_point_id))
        
        return queryset.distinct()
    
    def get_permissions(self) -> List[Any]:
        """根据动作设置权限。"""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsTeacherOrAdmin()]
        return super().get_permissions()
    
    @action(detail=True, methods=["POST"])
    def recalculate_score(self, request: Request, pk: Optional[int] = None) -> Response:
        """重新计算题目得分。"""
        question = self.get_object()
        
        try:
            question.update_score()
            question.save()
            
            serializer = self.get_serializer(question)
            return Response(serializer.data)
        except Exception as e:
            _LOGGER.error("重新计算题目得分失败: %s", str(e))
            return Response(
                {"error": "重新计算得分失败"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=False, methods=["GET"])
    def statistics(self, request: Request) -> Response:
        """获取题目统计信息。"""
        user = request.user
        queryset = self.get_queryset()
        
        # 基础统计
        total_count = queryset.count()
        correct_count = queryset.filter(is_correct=True).count()
        incorrect_count = total_count - correct_count
        
        # 按题目类型统计
        type_stats = (
            queryset.values("question_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        
        # 按科目统计（通过作业关联）
        subject_stats = (
            queryset.values("homework__subject")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        
        # 计算平均得分率
        avg_score_rate = 0
        if total_count > 0:
            total_max_score = queryset.aggregate(total=Sum("max_score"))["total"] or 0
            total_actual_score = queryset.aggregate(total=Sum("actual_score"))["total"] or 0
            if total_max_score > 0:
                avg_score_rate = (total_actual_score / total_max_score) * 100
        
        return Response({
            "total_count": total_count,
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "correct_rate": (correct_count / total_count * 100) if total_count > 0 else 0,
            "avg_score_rate": avg_score_rate,
            "type_statistics": list(type_stats),
            "subject_statistics": list(subject_stats),
        })


# ==================== 作业视图集 ====================
class HomeworkViewSet(viewsets.ModelViewSet):
    """
    作业视图集类，提供作业的CRUD操作。
    """
    
    serializer_class = HomeworkSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "subject"]
    ordering_fields = [
        "submitted_at",
        "deadline",
        "corrected_at",
        "total_score",
        "accuracy_rate",
        "created_at",
    ]
    ordering = ["-submitted_at"]
    
    def get_queryset(self) -> QuerySet[Homework]:
        """获取作业查询集，根据用户角色和权限过滤。"""
        user = self.request.user
        queryset = Homework.objects.select_related("student").prefetch_related("questions")
        
        # 学生只能查看自己的作业
        if user.role == "student":
            queryset = queryset.filter(student=user)
        # 老师和家长可以查看所有作业
        elif user.role in ["teacher", "parent"]:
            pass  # 不进行过滤
        # 管理员可以查看所有作业
        elif user.is_superuser:
            pass  # 不进行过滤
        else:
            queryset = queryset.none()
        
        # 状态过滤
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 科目过滤
        subject_filter = self.request.query_params.get("subject")
        if subject_filter:
            queryset = queryset.filter(subject=subject_filter)
        
        # 学生ID过滤（老师和家长用）
        student_id = self.request.query_params.get("student_id")
        if student_id and student_id.isdigit() and user.role in ["teacher", "parent", "admin"]:
            queryset = queryset.filter(student_id=int(student_id))
        
        # 时间范围过滤
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            queryset = queryset.filter(submitted_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(submitted_at__lte=end_date)
        
        # 是否过期过滤
        overdue = self.request.query_params.get("overdue")
        if overdue is not None:
            if overdue.lower() == "true":
                queryset = queryset.filter(deadline__lt=timezone.now())
            elif overdue.lower() == "false":
                queryset = queryset.filter(
                    Q(deadline__isnull=True) | Q(deadline__gte=timezone.now())
                )
        
        return queryset
    
    def get_serializer_class(self):
        """根据动作选择序列化器。"""
        if self.action == "submit":
            return HomeworkSubmitSerializer
        elif self.action == "correct":
            return HomeworkCorrectionSerializer
        return super().get_serializer_class()
    
    def get_permissions(self) -> List[Any]:
        """根据动作设置权限。"""
        if self.action in ["create", "submit"]:
            # 学生可以创建和提交作业
            return [IsAuthenticated()]
        elif self.action in ["correct", "process", "retry"]:
            # 只有老师和管理员可以批改和处理作业
            return [IsAuthenticated(), IsTeacherOrAdmin()]
        return super().get_permissions()
    
    def perform_create(self, serializer: HomeworkSerializer) -> None:
        """创建作业时自动设置学生。"""
        serializer.save(student=self.request.user)
    
    @action(detail=False, methods=["POST"])
    def submit(self, request: Request) -> Response:
        """提交作业（从草稿状态转换为已提交状态）。"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            homework = serializer.save()
            _LOGGER.info("作业提交成功: %s (学生: %s)", homework.title, request.user.username)
            
            # 返回完整的作业信息
            full_serializer = HomeworkSerializer(homework, context={"request": request})
            return Response(full_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            _LOGGER.error("作业提交失败: %s", str(e))
            return Response(
                {"error": "作业提交失败"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=True, methods=["POST"])
    def correct(self, request: Request, pk: Optional[int] = None) -> Response:
        """批改作业（批量更新题目得分和批注）。"""
        homework = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                # 保存批改结果
                homework = serializer.save(homework_id=homework.id)
                
                # 更新作业状态为已完成
                homework.status = HomeworkStatus.COMPLETED
                homework.corrected_at = timezone.now()
                homework.save()
                
                _LOGGER.info("作业批改完成: %s (ID: %s)", homework.title, homework.id)
                
                # 返回更新后的作业信息
                full_serializer = HomeworkSerializer(homework, context={"request": request})
                return Response(full_serializer.data)
        except Exception as e:
            _LOGGER.error("作业批改失败: %s", str(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=True, methods=["POST"])
    def process(self, request: Request, pk: Optional[int] = None) -> Response:
        """处理作业（OCR识别和题目提取）。"""
        homework = self.get_object()
        
        # 检查作业状态
        if homework.status != HomeworkStatus.SUBMITTED:
            return Response(
                {"error": f"作业当前状态为 {homework.status}，无法进行处理"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            # 更新状态为处理中
            homework.status = HomeworkStatus.PROCESSING
            homework.save()
            
            # TODO: 调用OCR服务处理作业文件
            # 这里应该调用 services/ocr_service.py 中的功能
            
            _LOGGER.info("作业开始处理: %s (ID: %s)", homework.title, homework.id)
            
            # 模拟处理完成（实际应该使用异步任务）
            # 这里先直接更新状态为批改中
            homework.status = HomeworkStatus.CORRECTING
            homework.save()
            
            # 返回更新后的作业信息
            serializer = self.get_serializer(homework)
            return Response(serializer.data)
        except Exception as e:
            _LOGGER.error("作业处理失败: %s", str(e))
            
            # 更新状态为错误
            homework.status = HomeworkStatus.ERROR
            homework.save()
            
            return Response(
                {"error": "作业处理失败"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=True, methods=["POST"])
    def retry(self, request: Request, pk: Optional[int] = None) -> Response:
        """重试处理出错的作业。"""
        homework = self.get_object()
        
        # 检查作业状态
        if homework.status != HomeworkStatus.ERROR:
            return Response(
                {"error": f"作业当前状态为 {homework.status}，无需重试"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            # 更新状态为已提交，准备重新处理
            homework.status = HomeworkStatus.SUBMITTED
            homework.save()
            
            _LOGGER.info("作业重试准备: %s (ID: %s)", homework.title, homework.id)
            
            # 返回更新后的作业信息
            serializer = self.get_serializer(homework)
            return Response(serializer.data)
        except Exception as e:
            _LOGGER.error("作业重试失败: %s", str(e))
            return Response(
                {"error": "作业重试失败"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=False, methods=["GET"])
    def statistics(self, request: Request) -> Response:
        """获取作业统计信息。"""
        user = request.user
        queryset = self.get_queryset()
        
        # 基础统计
        total_count = queryset.count()
        submitted_count = queryset.filter(status=HomeworkStatus.SUBMITTED).count()
        processing_count = queryset.filter(status=HomeworkStatus.PROCESSING).count()
        correcting_count = queryset.filter(status=HomeworkStatus.CORRECTING).count()
        completed_count = queryset.filter(status=HomeworkStatus.COMPLETED).count()
        error_count = queryset.filter(status=HomeworkStatus.ERROR).count()
        
        # 按科目统计
        subject_stats = (
            queryset.values("subject")
            .annotate(
                count=Count("id"),
                avg_score=Avg("total_score"),
                avg_accuracy=Avg("accuracy_rate"),
            )
            .order_by("-count")
        )
        
        # 按状态统计
        status_stats = (
            queryset.values("status")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        
        # 时间趋势统计（最近30天）
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        daily_stats = (
            queryset.filter(submitted_at__gte=thirty_days_ago)
            .extra({"date": "DATE(submitted_at)"})
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )
        
        return Response({
            "total_count": total_count,
            "status_summary": {
                "submitted": submitted_count,
                "processing": processing_count,
                "correcting": correcting_count,
                "completed": completed_count,
                "error": error_count,
            },
            "completion_rate": (completed_count / total_count * 100) if total_count > 0 else 0,
            "error_rate": (error_count / total_count * 100) if total_count > 0 else 0,
            "subject_statistics": list(subject_stats),
            "status_statistics": list(status_stats),
            "daily_trend": list(daily_stats),
        })
"""
作业管理数据模型模块，定义作业、题目、批改记录等核心数据结构和关系。
按照豆包AI助手最佳实践：使用Django模型实现业务数据持久化。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.constants import BusinessRules, FileTypes, HomeworkStatus, QuestionType


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 作业模型 ====================
class Homework(models.Model):
    """
    作业模型类，表示学生的一次作业提交。
    """
    
    # 基础信息
    title = models.CharField(
        _("作业标题"),
        max_length=BusinessRules.HOMEWORK_TITLE_MAX_LENGTH,
        help_text=_("作业的标题，用于快速识别作业内容"),
    )
    
    description = models.TextField(
        _("作业描述"),
        max_length=BusinessRules.HOMEWORK_DESCRIPTION_MAX_LENGTH,
        blank=True,
        help_text=_("作业的详细描述和要求"),
    )
    
    # 关联信息
    student = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="homeworks",
        verbose_name=_("学生"),
        help_text=_("提交作业的学生"),
    )
    
    subject = models.CharField(
        _("科目"),
        max_length=BusinessRules.SUBJECT_NAME_MAX_LENGTH,
        help_text=_("作业所属的学科，如：数学、语文、英语等"),
    )
    
    # 状态信息
    status = models.CharField(
        _("作业状态"),
        max_length=BusinessRules.STATUS_MAX_LENGTH,
        choices=HomeworkStatus.choices,
        default=HomeworkStatus.SUBMITTED,
        help_text=_("作业的当前处理状态"),
    )
    
    # 时间信息
    submitted_at = models.DateTimeField(
        _("提交时间"),
        default=timezone.now,
        help_text=_("学生提交作业的时间"),
    )
    
    deadline = models.DateTimeField(
        _("截止时间"),
        null=True,
        blank=True,
        help_text=_("作业的截止提交时间"),
    )
    
    corrected_at = models.DateTimeField(
        _("批改时间"),
        null=True,
        blank=True,
        help_text=_("作业被批改完成的时间"),
    )
    
    # 文件信息
    original_file = models.FileField(
        _("原始作业文件"),
        upload_to="homework/original/%Y/%m/%d/",
        validators=[
            FileExtensionValidator(allowed_extensions=FileTypes.IMAGE_EXTENSIONS + FileTypes.PDF_EXTENSIONS),
        ],
        help_text=_("学生提交的原始作业文件（图片或PDF）"),
    )
    
    processed_file = models.FileField(
        _("处理后的作业文件"),
        upload_to="homework/processed/%Y/%m/%d/",
        null=True,
        blank=True,
        help_text=_("经过预处理（如OCR识别）后的作业文件"),
    )
    
    # 统计信息
    total_score = models.DecimalField(
        _("总分"),
        max_digits=BusinessRules.SCORE_MAX_DIGITS,
        decimal_places=BusinessRules.SCORE_DECIMAL_PLACES,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(BusinessRules.MAX_SCORE),
        ],
        help_text=_("作业的总得分"),
    )
    
    accuracy_rate = models.DecimalField(
        _("正确率"),
        max_digits=BusinessRules.PERCENTAGE_MAX_DIGITS,
        decimal_places=BusinessRules.PERCENTAGE_DECIMAL_PLACES,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text=_("作业的正确率（百分比）"),
    )
    
    # 元数据
    created_at = models.DateTimeField(
        _("创建时间"),
        auto_now_add=True,
        help_text=_("记录创建时间"),
    )
    
    updated_at = models.DateTimeField(
        _("更新时间"),
        auto_now=True,
        help_text=_("记录最后更新时间"),
    )
    
    class Meta:
        """作业模型的元数据配置。"""
        
        verbose_name = _("作业")
        verbose_name_plural = _("作业列表")
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["student", "status"]),
            models.Index(fields=["subject", "submitted_at"]),
            models.Index(fields=["status", "corrected_at"]),
        ]
    
    def __str__(self) -> str:
        """返回作业的字符串表示。"""
        return f"{self.title} - {self.student.username} ({self.get_status_display()})"
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """保存作业前的预处理。"""
        is_new: bool = self.pk is None
        
        # 调用父类保存方法
        super().save(*args, **kwargs)
        
        # 记录日志
        if is_new:
            _LOGGER.info("作业创建成功: %s (ID: %s)", self.title, self.id)
        else:
            _LOGGER.debug("作业更新成功: %s (ID: %s)", self.title, self.id)
    
    def get_progress_percentage(self) -> float:
        """获取作业处理进度百分比。"""
        if self.status == HomeworkStatus.SUBMITTED:
            return 25.0
        elif self.status == HomeworkStatus.PROCESSING:
            return 50.0
        elif self.status == HomeworkStatus.CORRECTING:
            return 75.0
        elif self.status == HomeworkStatus.COMPLETED:
            return 100.0
        else:
            return 0.0
    
    def can_be_corrected(self) -> bool:
        """检查作业是否可以被批改。"""
        return self.status in [
            HomeworkStatus.PROCESSING,
            HomeworkStatus.CORRECTING,
        ]
    
    def is_overdue(self) -> bool:
        """检查作业是否已过期。"""
        if not self.deadline:
            return False
        return timezone.now() > self.deadline


# ==================== 题目模型 ====================
class Question(models.Model):
    """
    题目模型类，表示作业中的一个具体题目。
    """
    
    # 基础信息
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name=_("所属作业"),
        help_text=_("题目所属的作业"),
    )
    
    question_number = models.PositiveIntegerField(
        _("题号"),
        help_text=_("题目在作业中的序号"),
    )
    
    content = models.TextField(
        _("题目内容"),
        max_length=BusinessRules.QUESTION_CONTENT_MAX_LENGTH,
        help_text=_("题目的具体内容，从OCR识别结果中提取"),
    )
    
    question_type = models.CharField(
        _("题目类型"),
        max_length=BusinessRules.QUESTION_TYPE_MAX_LENGTH,
        choices=QuestionType.choices,
        default=QuestionType.SINGLE_CHOICE,
        help_text=_("题目的类型，如选择题、填空题、解答题等"),
    )
    
    # 答案信息
    student_answer = models.TextField(
        _("学生答案"),
        max_length=BusinessRules.ANSWER_MAX_LENGTH,
        blank=True,
        help_text=_("学生填写的答案"),
    )
    
    correct_answer = models.TextField(
        _("正确答案"),
        max_length=BusinessRules.ANSWER_MAX_LENGTH,
        blank=True,
        help_text=_("题目的标准正确答案"),
    )
    
    # 评分信息
    max_score = models.DecimalField(
        _("满分"),
        max_digits=BusinessRules.SCORE_MAX_DIGITS,
        decimal_places=BusinessRules.SCORE_DECIMAL_PLACES,
        default=10,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(BusinessRules.MAX_SCORE_PER_QUESTION),
        ],
        help_text=_("该题目的满分值"),
    )
    
    actual_score = models.DecimalField(
        _("实际得分"),
        max_digits=BusinessRules.SCORE_MAX_DIGITS,
        decimal_places=BusinessRules.SCORE_DECIMAL_PLACES,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(BusinessRules.MAX_SCORE_PER_QUESTION),
        ],
        help_text=_("学生在该题目上的实际得分"),
    )
    
    # 批改信息
    correction_notes = models.TextField(
        _("批注"),
        max_length=BusinessRules.CORRECTION_NOTES_MAX_LENGTH,
        blank=True,
        help_text=_("老师或AI对答案的批注和反馈"),
    )
    
    is_correct = models.BooleanField(
        _("是否正确"),
        default=False,
        help_text=_("标记该题目答案是否正确"),
    )
    
    # 元数据
    created_at = models.DateTimeField(
        _("创建时间"),
        auto_now_add=True,
        help_text=_("记录创建时间"),
    )
    
    updated_at = models.DateTimeField(
        _("更新时间"),
        auto_now=True,
        help_text=_("记录最后更新时间"),
    )
    
    class Meta:
        """题目模型的元数据配置。"""
        
        verbose_name = _("题目")
        verbose_name_plural = _("题目列表")
        ordering = ["homework", "question_number"]
        unique_together = [["homework", "question_number"]]
        indexes = [
            models.Index(fields=["homework", "question_type"]),
            models.Index(fields=["is_correct", "actual_score"]),
        ]
    
    def __str__(self) -> str:
        """返回题目的字符串表示。"""
        return f"题目{self.question_number} - {self.homework.title}"
    
    def calculate_score(self) -> Decimal:
        """计算题目的得分（根据答案正确性自动计算）。"""
        from decimal import Decimal
        
        if not self.correct_answer or not self.student_answer:
            return Decimal(0)
        
        # 根据题目类型计算得分
        if self.question_type == QuestionType.SINGLE_CHOICE:
            # 选择题：答案完全匹配则得满分
            if self.student_answer.strip().lower() == self.correct_answer.strip().lower():
                return self.max_score
            else:
                return Decimal(0)
        
        elif self.question_type == QuestionType.MULTIPLE_CHOICE:
            # 多选题：部分得分逻辑（简化版）
            student_answers = set(a.strip().lower() for a in self.student_answer.split(","))
            correct_answers = set(a.strip().lower() for a in self.correct_answer.split(","))
            
            correct_count = len(student_answers.intersection(correct_answers))
            wrong_count = len(student_answers - correct_answers)
            
            if wrong_count > 0:
                # 有错误选项不得分
                return Decimal(0)
            elif correct_count == len(correct_answers):
                # 全部正确得满分
                return self.max_score
            else:
                # 部分正确得部分分
                return self.max_score * Decimal(correct_count) / Decimal(len(correct_answers))
        
        else:
            # 其他类型题目需要AI批改
            return Decimal(0)
    
    def update_score(self) -> None:
        """更新题目的得分并标记正确性。"""
        from decimal import Decimal
        
        calculated_score = self.calculate_score()
        self.actual_score = calculated_score
        self.is_correct = (calculated_score == self.max_score)
        
        _LOGGER.debug(
            "题目得分更新: 作业ID=%s, 题号=%s, 得分=%s, 正确=%s",
            self.homework_id,
            self.question_number,
            calculated_score,
            self.is_correct,
        )


# ==================== 知识点模型 ====================
class KnowledgePoint(models.Model):
    """
    知识点模型类，表示作业题目涉及的知识点。
    """
    
    # 基础信息
    name = models.CharField(
        _("知识点名称"),
        max_length=BusinessRules.KNOWLEDGE_POINT_NAME_MAX_LENGTH,
        unique=True,
        help_text=_("知识点的唯一名称"),
    )
    
    description = models.TextField(
        _("知识点描述"),
        max_length=BusinessRules.KNOWLEDGE_POINT_DESC_MAX_LENGTH,
        blank=True,
        help_text=_("知识点的详细描述和说明"),
    )
    
    subject = models.CharField(
        _("所属科目"),
        max_length=BusinessRules.SUBJECT_NAME_MAX_LENGTH,
        help_text=_("知识点所属的学科"),
    )
    
    difficulty_level = models.PositiveIntegerField(
        _("难度等级"),
        choices=BusinessRules.DIFFICULTY_LEVEL_CHOICES,
        default=BusinessRules.DIFFICULTY_MEDIUM,
        help_text=_("知识点的难度等级（1-5，1最简单，5最难）"),
    )
    
    # 关联信息
    questions = models.ManyToManyField(
        Question,
        related_name="knowledge_points",
        verbose_name=_("关联题目"),
        blank=True,
        help_text=_("涉及该知识点的题目"),
    )
    
    # 元数据
    created_at = models.DateTimeField(
        _("创建时间"),
        auto_now_add=True,
        help_text=_("记录创建时间"),
    )
    
    updated_at = models.DateTimeField(
        _("更新时间"),
        auto_now=True,
        help_text=_("记录最后更新时间"),
    )
    
    class Meta:
        """知识点模型的元数据配置。"""
        
        verbose_name = _("知识点")
        verbose_name_plural = _("知识点列表")
        ordering = ["subject", "difficulty_level", "name"]
        indexes = [
            models.Index(fields=["subject", "difficulty_level"]),
            models.Index(fields=["name"]),
        ]
    
    def __str__(self) -> str:
        """返回知识点的字符串表示。"""
        return f"{self.subject} - {self.name} (难度: {self.difficulty_level})"
    
    def get_related_homeworks(self) -> models.QuerySet[Homework]:
        """获取涉及该知识点的所有作业。"""
        return Homework.objects.filter(
            questions__knowledge_points=self
        ).distinct()
    
    def get_mastery_rate(self, student_id: int) -> float:
        """计算学生对某个知识点的掌握率。"""
        from django.db.models import Avg, Count
        
        # 获取学生所有涉及该知识点的题目
        student_questions = Question.objects.filter(
            homework__student_id=student_id,
            knowledge_points=self,
        )
        
        if not student_questions.exists():
            return 0.0
        
        # 计算平均得分率
        avg_score_rate = student_questions.aggregate(
            avg_rate=Avg(models.F("actual_score") / models.F("max_score") * 100)
        )["avg_rate"] or 0.0
        
        return float(avg_score_rate)
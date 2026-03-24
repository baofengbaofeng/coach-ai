"""
作业管理序列化器模块，定义作业、题目、知识点等数据的序列化和反序列化逻辑。
按照豆包AI助手最佳实践：使用Django REST Framework序列化器。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.core.validators import FileExtensionValidator
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.accounts.models import User
from apps.homework.models import Homework, KnowledgePoint, Question
from core.constants import BusinessRules, FileTypes, HomeworkStatus, QuestionType


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 知识点序列化器 ====================
class KnowledgePointSerializer(serializers.ModelSerializer):
    """
    知识点序列化器类，用于知识点的序列化和反序列化。
    """
    
    subject_display = serializers.CharField(source="get_subject_display", read_only=True)
    difficulty_display = serializers.CharField(source="get_difficulty_level_display", read_only=True)
    
    class Meta:
        """知识点序列化器的元数据配置。"""
        
        model = KnowledgePoint
        fields = [
            "id",
            "name",
            "description",
            "subject",
            "subject_display",
            "difficulty_level",
            "difficulty_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def validate_name(self, value: str) -> str:
        """验证知识点名称。"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("知识点名称不能为空")
        if len(value) > BusinessRules.KNOWLEDGE_POINT_NAME_MAX_LENGTH:
            raise serializers.ValidationError(
                f"知识点名称不能超过{BusinessRules.KNOWLEDGE_POINT_NAME_MAX_LENGTH}个字符"
            )
        return value
    
    def validate_subject(self, value: str) -> str:
        """验证科目名称。"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("科目名称不能为空")
        if len(value) > BusinessRules.SUBJECT_NAME_MAX_LENGTH:
            raise serializers.ValidationError(
                f"科目名称不能超过{BusinessRules.SUBJECT_NAME_MAX_LENGTH}个字符"
            )
        return value
    
    def validate_difficulty_level(self, value: int) -> int:
        """验证难度等级。"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("难度等级必须在1-5之间")
        return value


# ==================== 题目序列化器 ====================
class QuestionSerializer(serializers.ModelSerializer):
    """
    题目序列化器类，用于题目的序列化和反序列化。
    """
    
    question_type_display = serializers.CharField(source="get_question_type_display", read_only=True)
    score_percentage = serializers.SerializerMethodField()
    knowledge_points = KnowledgePointSerializer(many=True, read_only=True)
    knowledge_point_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=KnowledgePoint.objects.all(),
        source="knowledge_points",
        write_only=True,
        required=False,
    )
    
    class Meta:
        """题目序列化器的元数据配置。"""
        
        model = Question
        fields = [
            "id",
            "homework",
            "question_number",
            "content",
            "question_type",
            "question_type_display",
            "student_answer",
            "correct_answer",
            "max_score",
            "actual_score",
            "correction_notes",
            "is_correct",
            "score_percentage",
            "knowledge_points",
            "knowledge_point_ids",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "actual_score",
            "is_correct",
            "created_at",
            "updated_at",
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=Question.objects.all(),
                fields=["homework", "question_number"],
                message="同一作业中题号必须唯一",
            ),
        ]
    
    def get_score_percentage(self, obj: Question) -> float:
        """计算题目的得分百分比。"""
        if obj.max_score == 0:
            return 0.0
        return float((obj.actual_score / obj.max_score) * 100)
    
    def validate_question_number(self, value: int) -> int:
        """验证题号。"""
        if value <= 0:
            raise serializers.ValidationError("题号必须大于0")
        return value
    
    def validate_content(self, value: str) -> str:
        """验证题目内容。"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("题目内容不能为空")
        if len(value) > BusinessRules.QUESTION_CONTENT_MAX_LENGTH:
            raise serializers.ValidationError(
                f"题目内容不能超过{BusinessRules.QUESTION_CONTENT_MAX_LENGTH}个字符"
            )
        return value
    
    def validate_max_score(self, value: float) -> float:
        """验证满分值。"""
        if value <= 0:
            raise serializers.ValidationError("满分必须大于0")
        if value > BusinessRules.MAX_SCORE_PER_QUESTION:
            raise serializers.ValidationError(
                f"单题满分不能超过{BusinessRules.MAX_SCORE_PER_QUESTION}"
            )
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """验证题目数据的整体一致性。"""
        # 检查题目类型与答案格式的匹配
        question_type = attrs.get("question_type", getattr(self.instance, "question_type", None))
        student_answer = attrs.get("student_answer", getattr(self.instance, "student_answer", ""))
        correct_answer = attrs.get("correct_answer", getattr(self.instance, "correct_answer", ""))
        
        if question_type == QuestionType.SINGLE_CHOICE:
            # 单选题：答案应该是单个选项
            if student_answer and "," in student_answer:
                raise serializers.ValidationError({
                    "student_answer": "单选题答案不能包含多个选项"
                })
            if correct_answer and "," in correct_answer:
                raise serializers.ValidationError({
                    "correct_answer": "单选题正确答案不能包含多个选项"
                })
        
        elif question_type == QuestionType.MULTIPLE_CHOICE:
            # 多选题：答案应该是逗号分隔的多个选项
            if student_answer:
                options = [opt.strip() for opt in student_answer.split(",") if opt.strip()]
                if len(options) <= 1:
                    raise serializers.ValidationError({
                        "student_answer": "多选题答案应包含多个选项，用逗号分隔"
                    })
            if correct_answer:
                options = [opt.strip() for opt in correct_answer.split(",") if opt.strip()]
                if len(options) <= 1:
                    raise serializers.ValidationError({
                        "correct_answer": "多选题正确答案应包含多个选项，用逗号分隔"
                    })
        
        return attrs
    
    def update(self, instance: Question, validated_data: Dict[str, Any]) -> Question:
        """更新题目并重新计算得分。"""
        # 处理知识点关联
        knowledge_points = validated_data.pop("knowledge_points", None)
        
        # 更新题目基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # 保存并重新计算得分
        instance.save()
        instance.update_score()
        
        # 更新知识点关联
        if knowledge_points is not None:
            instance.knowledge_points.set(knowledge_points)
        
        return instance


# ==================== 作业序列化器 ====================
class HomeworkSerializer(serializers.ModelSerializer):
    """
    作业序列化器类，用于作业的序列化和反序列化。
    """
    
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    student_name = serializers.CharField(source="student.username", read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()
    correct_question_count = serializers.SerializerMethodField()
    
    class Meta:
        """作业序列化器的元数据配置。"""
        
        model = Homework
        fields = [
            "id",
            "title",
            "description",
            "student",
            "student_name",
            "subject",
            "status",
            "status_display",
            "submitted_at",
            "deadline",
            "corrected_at",
            "original_file",
            "processed_file",
            "total_score",
            "accuracy_rate",
            "progress_percentage",
            "is_overdue",
            "questions",
            "question_count",
            "correct_question_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student_name",
            "status_display",
            "processed_file",
            "total_score",
            "accuracy_rate",
            "progress_percentage",
            "is_overdue",
            "question_count",
            "correct_question_count",
            "created_at",
            "updated_at",
        ]
    
    def get_progress_percentage(self, obj: Homework) -> float:
        """获取作业处理进度百分比。"""
        return obj.get_progress_percentage()
    
    def get_is_overdue(self, obj: Homework) -> bool:
        """检查作业是否已过期。"""
        return obj.is_overdue()
    
    def get_question_count(self, obj: Homework) -> int:
        """获取作业题目数量。"""
        return obj.questions.count()
    
    def get_correct_question_count(self, obj: Homework) -> int:
        """获取作业中正确的题目数量。"""
        return obj.questions.filter(is_correct=True).count()
    
    def validate_title(self, value: str) -> str:
        """验证作业标题。"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("作业标题不能为空")
        if len(value) > BusinessRules.HOMEWORK_TITLE_MAX_LENGTH:
            raise serializers.ValidationError(
                f"作业标题不能超过{BusinessRules.HOMEWORK_TITLE_MAX_LENGTH}个字符"
            )
        return value
    
    def validate_subject(self, value: str) -> str:
        """验证科目名称。"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("科目名称不能为空")
        if len(value) > BusinessRules.SUBJECT_NAME_MAX_LENGTH:
            raise serializers.ValidationError(
                f"科目名称不能超过{BusinessRules.SUBJECT_NAME_MAX_LENGTH}个字符"
            )
        return value
    
    def validate_original_file(self, value: Any) -> Any:
        """验证原始作业文件。"""
        # 检查文件扩展名
        validator = FileExtensionValidator(
            allowed_extensions=FileTypes.IMAGE_EXTENSIONS + FileTypes.PDF_EXTENSIONS
        )
        validator(value)
        
        # 检查文件大小（在视图层处理）
        return value
    
    def validate_deadline(self, value: Optional[timezone.datetime]) -> Optional[timezone.datetime]:
        """验证截止时间。"""
        if value and value < timezone.now():
            raise serializers.ValidationError("截止时间不能早于当前时间")
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """验证作业数据的整体一致性。"""
        # 检查截止时间与提交时间的关系
        deadline = attrs.get("deadline")
        submitted_at = attrs.get("submitted_at", timezone.now())
        
        if deadline and deadline < submitted_at:
            raise serializers.ValidationError({
                "deadline": "截止时间不能早于提交时间"
            })
        
        # 新创建的作业默认状态为草稿
        if self.instance is None:
            attrs.setdefault("status", HomeworkStatus.DRAFT)
        
        return attrs
    
    def create(self, validated_data: Dict[str, Any]) -> Homework:
        """创建作业。"""
        # 确保学生字段存在
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data.setdefault("student", request.user)
        
        # 创建作业
        homework = Homework.objects.create(**validated_data)
        _LOGGER.info("作业创建成功: %s (ID: %s)", homework.title, homework.id)
        
        return homework
    
    def update(self, instance: Homework, validated_data: Dict[str, Any]) -> Homework:
        """更新作业。"""
        # 检查状态转换的合法性
        old_status = instance.status
        new_status = validated_data.get("status", old_status)
        
        if old_status != new_status:
            # 状态转换规则检查
            valid_transitions = {
                HomeworkStatus.DRAFT: [HomeworkStatus.SUBMITTED],
                HomeworkStatus.SUBMITTED: [HomeworkStatus.PROCESSING, HomeworkStatus.ERROR],
                HomeworkStatus.PROCESSING: [HomeworkStatus.CORRECTING, HomeworkStatus.ERROR],
                HomeworkStatus.CORRECTING: [HomeworkStatus.COMPLETED, HomeworkStatus.ERROR],
                HomeworkStatus.COMPLETED: [],  # 已完成状态不可更改
                HomeworkStatus.ERROR: [HomeworkStatus.SUBMITTED],  # 错误状态可重新提交
            }
            
            if new_status not in valid_transitions.get(old_status, []):
                raise serializers.ValidationError({
                    "status": f"不能从 {old_status} 状态转换为 {new_status} 状态"
                })
            
            # 状态特定处理
            if new_status == HomeworkStatus.COMPLETED:
                validated_data["corrected_at"] = timezone.now()
                # 计算总分和正确率
                self._calculate_final_scores(instance)
        
        # 更新作业
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        _LOGGER.info("作业更新成功: %s (ID: %s)", instance.title, instance.id)
        
        return instance
    
    def _calculate_final_scores(self, homework: Homework) -> None:
        """计算作业的最终得分和正确率。"""
        from django.db.models import Sum, Count
        
        # 计算总分
        total_score_result = homework.questions.aggregate(
            total=Sum("actual_score")
        )
        total_score = total_score_result["total"] or 0
        
        # 计算正确率
        question_count = homework.questions.count()
        correct_count = homework.questions.filter(is_correct=True).count()
        accuracy_rate = (correct_count / question_count * 100) if question_count > 0 else 0
        
        # 更新作业
        homework.total_score = total_score
        homework.accuracy_rate = accuracy_rate
        homework.save(update_fields=["total_score", "accuracy_rate"])
        
        _LOGGER.info(
            "作业得分计算完成: %s (ID: %s), 总分: %s, 正确率: %s%%",
            homework.title,
            homework.id,
            total_score,
            accuracy_rate,
        )


# ==================== 作业提交序列化器 ====================
class HomeworkSubmitSerializer(serializers.ModelSerializer):
    """
    作业提交序列化器类，专门用于学生提交作业。
    """
    
    class Meta:
        """作业提交序列化器的元数据配置。"""
        
        model = Homework
        fields = [
            "title",
            "description",
            "subject",
            "deadline",
            "original_file",
        ]
    
    def create(self, validated_data: Dict[str, Any]) -> Homework:
        """提交作业（从草稿状态转换为已提交状态）。"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("用户未认证")
        
        # 设置学生和状态
        validated_data["student"] = request.user
        validated_data["status"] = HomeworkStatus.SUBMITTED
        validated_data["submitted_at"] = timezone.now()
        
        # 创建作业
        homework = Homework.objects.create(**validated_data)
        _LOGGER.info("作业提交成功: %s (学生: %s)", homework.title, request.user.username)
        
        return homework


# ==================== 作业批改序列化器 ====================
class HomeworkCorrectionSerializer(serializers.Serializer):
    """
    作业批改序列化器类，用于批量更新题目得分和批注。
    """
    
    corrections = serializers.ListField(
        child=serializers.DictField(),
        help_text="题目批改列表，每个元素包含题目ID和批改信息",
    )
    
    def validate_corrections(self, value: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """验证批改数据。"""
        if not value:
            raise serializers.ValidationError("批改列表不能为空")
        
        for i, correction in enumerate(value):
            if "question_id" not in correction:
                raise serializers.ValidationError(f"第{i+1}个批改缺少question_id字段")
            if "actual_score" not in correction:
                raise serializers.ValidationError(f"第{i+1}个批改缺少actual_score字段")
            
            # 验证得分范围
            actual_score = correction["actual_score"]
            if actual_score < 0:
                raise serializers.ValidationError(f"第{i+1}个批改的得分不能为负数")
        
        return value
    
    def save(self, homework_id: int) -> Homework:
        """保存批改结果。"""
        from django.db import transaction
        
        corrections = self.validated_data["corrections"]
        
        with transaction.atomic():
            # 获取作业
            try:
                homework = Homework.objects.get(id=homework_id)
            except Homework.DoesNotExist:
                raise serializers.ValidationError(f"作业ID {homework_id} 不存在")
            
            # 检查作业状态
            if not homework.can_be_corrected():
                raise serializers.ValidationError(
                    f"作业当前状态为 {homework.status}，无法进行批改"
                )
            

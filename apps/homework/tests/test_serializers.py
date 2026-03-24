"""
作业序列化器测试模块，测试作业、题目、知识点等序列化器的功能。
按照豆包AI助手最佳实践：每个序列化器都有对应的单元测试。
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from apps.accounts.models import User
from apps.homework.models import Homework, KnowledgePoint, Question
from apps.homework.serializers import (
    HomeworkCorrectionSerializer,
    HomeworkSerializer,
    HomeworkSubmitSerializer,
    KnowledgePointSerializer,
    QuestionSerializer,
)
from core.constants import HomeworkStatus, QuestionType, UserRole


# ==================== 知识点序列化器测试 ====================
class KnowledgePointSerializerTest(TestCase):
    """
    知识点序列化器测试类。
    """
    
    def setUp(self) -> None:
        """测试前置设置。"""
        self.factory = APIRequestFactory()
        self.valid_data = {
            "name": "一元二次方程",
            "description": "形如 ax² + bx + c = 0 的方程",
            "subject": "数学",
            "difficulty_level": 3,
        }
    
    def test_valid_serializer(self) -> None:
        """测试有效的序列化器数据。"""
        serializer = KnowledgePointSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        # 验证序列化后的数据
        self.assertEqual(serializer.validated_data["name"], "一元二次方程")
        self.assertEqual(serializer.validated_data["subject"], "数学")
        self.assertEqual(serializer.validated_data["difficulty_level"], 3)
    
    def test_invalid_name(self) -> None:
        """测试无效的知识点名称。"""
        # 名称为空
        data = self.valid_data.copy()
        data["name"] = ""
        serializer = KnowledgePointSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)
        
        # 名称过长
        data["name"] = "a" * 101
        serializer = KnowledgePointSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)
    
    def test_invalid_subject(self) -> None:
        """测试无效的科目名称。"""
        # 科目为空
        data = self.valid_data.copy()
        data["subject"] = ""
        serializer = KnowledgePointSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("subject", serializer.errors)
        
        # 科目过长
        data["subject"] = "a" * 51
        serializer = KnowledgePointSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("subject", serializer.errors)
    
    def test_invalid_difficulty(self) -> None:
        """测试无效的难度等级。"""
        # 难度过小
        data = self.valid_data.copy()
        data["difficulty_level"] = 0
        serializer = KnowledgePointSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("difficulty_level", serializer.errors)
        
        # 难度过大
        data["difficulty_level"] = 6
        serializer = KnowledgePointSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("difficulty_level", serializer.errors)
    
    def test_create_knowledge_point(self) -> None:
        """测试创建知识点。"""
        serializer = KnowledgePointSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        knowledge_point = serializer.save()
        self.assertEqual(knowledge_point.name, "一元二次方程")
        self.assertEqual(knowledge_point.subject, "数学")
        self.assertEqual(knowledge_point.difficulty_level, 3)
    
    def test_update_knowledge_point(self) -> None:
        """测试更新知识点。"""
        # 创建初始知识点
        knowledge_point = KnowledgePoint.objects.create(**self.valid_data)
        
        # 更新数据
        update_data = {
            "name": "二元一次方程",
            "description": "形如 ax + by = c 的方程",
            "subject": "数学",
            "difficulty_level": 2,
        }
        
        serializer = KnowledgePointSerializer(knowledge_point, data=update_data)
        self.assertTrue(serializer.is_valid())
        
        updated_knowledge_point = serializer.save()
        self.assertEqual(updated_knowledge_point.name, "二元一次方程")
        self.assertEqual(updated_knowledge_point.difficulty_level, 2)


# ==================== 题目序列化器测试 ====================
class QuestionSerializerTest(TestCase):
    """
    题目序列化器测试类。
    """
    
    def setUp(self) -> None:
        """测试前置设置。"""
        # 创建测试用户
        self.student = User.objects.create_user(
            username="test_student",
            email="student@test.com",
            password="testpass123",
            role=UserRole.STUDENT,
        )
        
        # 创建测试作业
        self.homework = Homework.objects.create(
            title="测试作业",
            student=self.student,
            subject="数学",
            status=HomeworkStatus.SUBMITTED,
        )
        
        # 创建测试知识点
        self.knowledge_point = KnowledgePoint.objects.create(
            name="测试知识点",
            subject="数学",
            difficulty_level=3,
        )
        
        self.valid_data = {
            "homework": self.homework.id,
            "question_number": 1,
            "content": "1 + 1 = ?",
            "question_type": QuestionType.SINGLE_CHOICE,
            "student_answer": "2",
            "correct_answer": "2",
            "max_score": Decimal("10.00"),
        }
    
    def test_valid_serializer(self) -> None:
        """测试有效的序列化器数据。"""
        serializer = QuestionSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        # 验证序列化后的数据
        self.assertEqual(serializer.validated_data["question_number"], 1)
        self.assertEqual(serializer.validated_data["content"], "1 + 1 = ?")
        self.assertEqual(serializer.validated_data["question_type"], QuestionType.SINGLE_CHOICE)
    
    def test_invalid_question_number(self) -> None:
        """测试无效的题号。"""
        # 题号为0
        data = self.valid_data.copy()
        data["question_number"] = 0
        serializer = QuestionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("question_number", serializer.errors)
    
    def test_invalid_content(self) -> None:
        """测试无效的题目内容。"""
        # 内容为空
        data = self.valid_data.copy()
        data["content"] = ""
        serializer = QuestionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)
        
        # 内容过长
        data["content"] = "a" * 5001
        serializer = QuestionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)
    
    def test_invalid_max_score(self) -> None:
        """测试无效的满分值。"""
        # 满分为0
        data = self.valid_data.copy()
        data["max_score"] = Decimal("0.00")
        serializer = QuestionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("max_score", serializer.errors)
        
        # 满分过大
        data["max_score"] = Decimal("21.00")
        serializer = QuestionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("max_score", serializer.errors)
    
    def test_question_type_validation(self) -> None:
        """测试题目类型验证。"""
        # 单选题答案包含多个选项
        data = self.valid_data.copy()
        data["student_answer"] = "A,B"
        data["correct_answer"] = "A,B"
        serializer = QuestionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("student_answer", serializer.errors)
        self.assertIn("correct_answer", serializer.errors)
        
        # 多选题答案只有一个选项
        data["question_type"] = QuestionType.MULTIPLE_CHOICE
        data["student_answer"] = "A"
        data["correct_answer"] = "A"
        serializer = QuestionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("student_answer", serializer.errors)
        self.assertIn("correct_answer", serializer.errors)
    
    def test_create_question_with_knowledge_points(self) -> None:
        """测试创建带知识点的题目。"""
        data = self.valid_data.copy()
        data["knowledge_point_ids"] = [self.knowledge_point.id]
        
        serializer = QuestionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        question = serializer.save()
        self.assertEqual(question.knowledge_points.count(), 1)
        self.assertEqual(question.knowledge_points.first(), self.knowledge_point)
    
    def test_update_question_score(self) -> None:
        """测试更新题目得分。"""
        # 创建初始题目
        question = Question.objects.create(**self.valid_data)
        
        # 更新答案
        update_data = {
            "homework": self.homework.id,
            "question_number": 1,
            "content": "1 + 1 = ?",
            "question_type": QuestionType.SINGLE_CHOICE,
            "student_answer": "3",  # 错误答案
            "correct_answer": "2",
            "max_score": Decimal("10.00"),
        }
        
        serializer = QuestionSerializer(question, data=update_data)
        self.assertTrue(serializer.is_valid())
        
        updated_question = serializer.save()
        self.assertEqual(updated_question.actual_score, Decimal("0.00"))
        self.assertFalse(updated_question.is_correct)


# ==================== 作业序列化器测试 ====================
class HomeworkSerializerTest(TestCase):
    """
    作业序列化器测试类。
    """
    
    def setUp(self) -> None:
        """测试前置设置。"""
        self.factory = APIRequestFactory()
        
        # 创建测试用户
        self.student = User.objects.create_user(
            username="test_student",
            email="student@test.com",
            password="testpass123",
            role=UserRole.STUDENT,
        )
        
        self.valid_data = {
            "title": "数学作业",
            "description": "这是一份数学作业",
            "student": self.student.id,
            "subject": "数学",
            "status": HomeworkStatus.DRAFT,
            "deadline": timezone.now() + timezone.timedelta(days=1),
        }
    
    def test_valid_serializer(self) -> None:
        """测试有效的序列化器数据。"""
        request = self.factory.post("/")
        request.user = self.student
        
        serializer = HomeworkSerializer(data=self.valid_data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        
        # 验证序列化后的数据
        self.assertEqual(serializer.validated_data["title"], "数学作业")
        self.assertEqual(serializer.validated_data["subject"], "数学")
        self.assertEqual(serializer.validated_data["status"], HomeworkStatus.DRAFT)
    
    def test_invalid_title(self) -> None:
        """测试无效的作业标题。"""
        # 标题为空
        data = self.valid_data.copy()
        data["title"] = ""
        serializer = HomeworkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)
        
        # 标题过长
        data["title"] = "a" * 201
        serializer = HomeworkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)
    
    def test_invalid_subject(self) -> None:
        """测试无效的科目名称。"""
        # 科目为空
        data = self.valid_data.copy()
        data["subject"] = ""
        serializer = HomeworkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("subject", serializer.errors)
        
        # 科目过长
        data["subject"] = "a" * 51
        serializer = HomeworkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("subject", serializer.errors)
    
    def test_invalid_deadline(self) -> None:
        """测试无效的截止时间。"""
        # 截止时间早于当前时间
        data = self.valid_data.copy()
        data["deadline"] = timezone.now() - timezone.timedelta(days=1)
        serializer = HomeworkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("deadline", serializer.errors)
    
    def test_status_transition_validation(self) -> None:
        """测试状态转换验证。"""
        # 创建初始作业
        homework = Homework.objects.create(
            title="测试作业",
            student=self.student,
            subject="数学",
            status=HomeworkStatus.SUBMITTED,
        )
        
        # 尝试非法状态转换：从已提交直接到已完成
        update_data = {
            "title": "测试作业",
            "subject": "数学",
            "status": HomeworkStatus.COMPLETED,
        }
        
        serializer = HomeworkSerializer(homework, data=update_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)
        
        # 合法状态转换：从已提交到处理中
        update_data["status"] = HomeworkStatus.PROCESSING
        serializer = HomeworkSerializer(homework, data=update_data)
        self.assertTrue(serializer.is_valid())
    
    def test_create_homework(self) -> None:
        """测试创建作业。"""
        request = self.factory.post("/")
        request.user = self.student
        
        serializer = HomeworkSerializer(data=self.valid_data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        
        homework = serializer.save()
        self.assertEqual(homework.title, "数学作业")
        self.assertEqual(homework.student, self.student)
        self.assertEqual(homework.status, HomeworkStatus.DRAFT)
    
    def test_update_homework_to_completed(self) -> None:
        """测试更新作业为已完成状态。"""
        # 创建初始作业
        homework = Homework.objects.create(
            title="测试作业",
            student=self.student,
            subject="数学",
            status=HomeworkStatus.CORRECTING,
        )
        
        # 创建测试题目
        Question.objects.create(
            homework=homework,
            question_number=1,
            content="题目1",
            question_type=QuestionType.SINGLE_CHOICE,
            student_answer="A",
            correct_answer="A",
            max_score=Decimal("10.00"),
            actual_score=Decimal("10.00"),
            is_correct=True,
        )
        
        Question.objects.create(
            homework=homework,
            question_number=2,
            content="题目2",
            question_type=QuestionType.SINGLE_CHOICE,
            student_answer="B",
            correct_answer="A",
            max_score=Decimal("10.00"),
            actual_score=Decimal("0.00"),
            is_correct=False,
        )
        
        # 更新为已完成状态
        update_data = {
            "title": "测试作业",
            "subject": "数学",
            "status": HomeworkStatus.COMPLETED,
        }
        
        serializer = HomeworkSerializer(homework, data=update_data)
        self.assertTrue(serializer.is_valid())
        
        updated_homework = serializer.save()
        self.assertEqual(updated_homework.status, HomeworkStatus.COMPLETED)
        self.assertIsNotNone(updated_homework.corrected_at)
        self.assertEqual(updated_homework.total_score, Decimal("10.00"))
        self.assertEqual(updated_homework.accuracy_rate, Decimal("50.00"))


# ==================== 作业提交序列化器测试 ====================
class HomeworkSubmitSerializerTest(TestCase):
    """
    作业提交序列化器测试类。
    """
    
    def setUp(self) -> None:
        """测试前置设置。"""
        self.factory = APIRequestFactory()
        
        # 创建测试用户
        self.student = User.objects.create_user(
            username="test_student",
            email="student@test.com",
            password="testpass123",
            role=UserRole.STUDENT,
        )
        
        self.valid_data = {
            "title": "数学作业",
            "description": "这是一份数学作业",
            "subject": "数学",
            "deadline": timezone.now() + timezone.timedelta(days=1),
        }
    
    def test_submit_homework(self) -> None:
        """测试提交作业。"""
        request = self.factory.post("/")
        request.user = self.student
        
        serializer = HomeworkSubmitSerializer(data=self.valid_data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        
        homework = serializer.save()
        self.assertEqual(homework.title, "数学作业")
        self.assertEqual(homework.student, self.student)
        self.assertEqual(homework.status, HomeworkStatus.SUBMITTED)
        self.assertIsNotNone(homework.submitted_at)


# ==================== 作业批改序列化器测试 ====================
class HomeworkCorrectionSerializerTest(TestCase):
    """
    作业批改序列化器测试类。
    """
    
    def setUp(self) -> None:
        """测试前置设置。"""
        # 创建测试用户
        self.student = User.objects.create_user(
            username="test_student",
            email="student@test.com",
            password="testpass123",
            role=UserRole.STUDENT,
        )
        
        # 创建测试作业
        self.homework = Homework.objects.create(
            title="测试作业",
            student=self.student,
            subject="数学",
            status=HomeworkStatus.CORRECTING,
        )
        
        # 创建测试题目
        self.question1 = Question.objects.create(
            homework=self.homework,
            question_number=1,
            content="题目1",
            question_type=QuestionType.SINGLE_CHOICE,
            max_score=Decimal("10.00"),
        )
        
        self.question2 = Question.objects.create(
            homework=self.homework,
            question_number=2,
            content="题目2",
            question_type=QuestionType.SINGLE_CHOICE,
            max_score=Decimal("10.00"),
        )
        
        self.valid_data = {
            "corrections": [
                {
                    "question_id": self.question1.id,
                    "actual_score": Decimal("8.00"),
                    "correction_notes": "答案基本正确，但步骤不完整",
                },
                {
                    "question_id": self.question2.id,
                    "actual_score": Decimal("10.00"),
                    "correction_notes": "答案完全正确",
                },
            ]
        }
    
    def test_valid_correction(self) -> None:
        """测试有效的批改数据。"""
        serializer = HomeworkCorrectionSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        # 验证序列化后的数据
        self.assertEqual(len(serializer.validated_data["corrections"]), 2)
        self.assertEqual(serializer.validated_data["corrections"][0]["actual_score"], Decimal("8.00"))
        self.assertEqual(serializer.validated_data["corrections"][1]["actual_score"], Decimal("10.00"))
    
    def test_invalid_correction_empty_list(self) -> None:
        """测试空的批改列表。"""
        data = {"corrections": []}
        serializer = HomeworkCorrectionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("corrections", serializer.errors)
    
    def test_invalid_correction_missing_fields(self) -> None:
        """测试缺少必要字段的批改数据。"""
        # 缺少question_id
        data = {
            "corrections": [
                {
                    "actual_score": Decimal("8.00"),
                }
            ]
        }
        serializer = HomeworkCorrectionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("corrections", serializer.errors)
        
        # 缺少actual_score
        data = {
            "corrections": [
                {
                    "question_id": self.question1.id,
                }
            ]
        }
        serializer = HomeworkCorrectionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("corrections", serializer.errors)
    
    def test_invalid_correction_negative_score(self) -> None:
        """测试负分的批改数据。"""
        data = {
            "corrections": [
                {
                    "question_id": self.question1.id,
                    "actual_score": Decimal("-1.00"),
                }
            ]
        }
        serializer = HomeworkCorrectionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("corrections", serializer.errors)
    
    def test_save_correction(self) -> None:
        """测试保存批改结果。"""
        serializer = HomeworkCorrectionSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        try:
            homework = serializer.save(self.homework.id)
            self.assertEqual(homework.status, HomeworkStatus.COMPLETED)
            self.assertIsNotNone(homework.corrected_at)
            
            # 验证题目得分已更新
            self.question1.refresh_from_db()
            self.question2.refresh_from_db()
            
            self.assertEqual(self.question1.actual_score, Decimal("8.00"))
            self.assertEqual(self.question1.correction_notes, "答案基本正确，但步骤不完整")
            self.assertEqual(self.question2.actual_score, Decimal("10.00"))
            self.assertEqual(self.question2.correction_notes, "答案完全正确")
            
            # 验证作业统计信息
            self.assertEqual(homework.total_score, Decimal("18.00"))
            self.assertEqual(homework.accuracy_rate, Decimal("50.00"))  # 只有第2题完全正确
            
        except ValidationError as e:
            self.fail(f"保存批改结果失败: {e}")
    
    def test_save_correction_invalid_homework_status(self) -> None:
        """测试在无效的作业状态下保存批改结果。"""
        # 将作业状态改为已提交（不可批改）
        self.homework.status = HomeworkStatus.SUBMITTED
        self.homework.save()
        
        serializer = HomeworkCorrectionSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        with self.assertRaises(ValidationError):
            serializer.save(self.homework.id)
    
    def test_save_correction_nonexistent_homework(self) -> None:
        """测试对不存在的作业保存批改结果。"""
        serializer = HomeworkCorrectionSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        with self.assertRaises(ValidationError):
            serializer.save(99999)  # 不存在的作业ID
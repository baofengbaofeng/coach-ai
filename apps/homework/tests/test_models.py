"""
作业模型测试模块，测试作业、题目、知识点等模型的基本功能。
按照豆包AI助手最佳实践：每个模型都有对应的单元测试。
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.homework.models import Homework, KnowledgePoint, Question
from core.constants import HomeworkStatus, QuestionType, UserRole


# ==================== 作业模型测试 ====================
class HomeworkModelTest(TestCase):
    """
    作业模型测试类。
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
        
        self.teacher = User.objects.create_user(
            username="test_teacher",
            email="teacher@test.com",
            password="testpass123",
            role=UserRole.TEACHER,
        )
        
        # 创建测试作业
        self.homework = Homework.objects.create(
            title="数学作业测试",
            description="这是一份测试用的数学作业",
            student=self.student,
            subject="数学",
            status=HomeworkStatus.SUBMITTED,
            submitted_at=timezone.now(),
            deadline=timezone.now() + timezone.timedelta(days=1),
        )
    
    def test_homework_creation(self) -> None:
        """测试作业创建。"""
        self.assertEqual(self.homework.title, "数学作业测试")
        self.assertEqual(self.homework.student, self.student)
        self.assertEqual(self.homework.subject, "数学")
        self.assertEqual(self.homework.status, HomeworkStatus.SUBMITTED)
        self.assertTrue(self.homework.submitted_at is not None)
        self.assertTrue(self.homework.deadline is not None)
    
    def test_homework_string_representation(self) -> None:
        """测试作业的字符串表示。"""
        expected = f"{self.homework.title} - {self.student.username} ({self.homework.get_status_display()})"
        self.assertEqual(str(self.homework), expected)
    
    def test_homework_progress_percentage(self) -> None:
        """测试作业进度百分比计算。"""
        # 测试不同状态下的进度
        test_cases = [
            (HomeworkStatus.DRAFT, 0.0),
            (HomeworkStatus.SUBMITTED, 25.0),
            (HomeworkStatus.PROCESSING, 50.0),
            (HomeworkStatus.CORRECTING, 75.0),
            (HomeworkStatus.COMPLETED, 100.0),
            (HomeworkStatus.ERROR, 0.0),
        ]
        
        for status, expected_percentage in test_cases:
            self.homework.status = status
            self.assertEqual(self.homework.get_progress_percentage(), expected_percentage)
    
    def test_homework_can_be_corrected(self) -> None:
        """测试作业是否可以被批改。"""
        # 处理中和批改中的作业可以被批改
        self.homework.status = HomeworkStatus.PROCESSING
        self.assertTrue(self.homework.can_be_corrected())
        
        self.homework.status = HomeworkStatus.CORRECTING
        self.assertTrue(self.homework.can_be_corrected())
        
        # 其他状态的作业不能被批改
        self.homework.status = HomeworkStatus.SUBMITTED
        self.assertFalse(self.homework.can_be_corrected())
        
        self.homework.status = HomeworkStatus.COMPLETED
        self.assertFalse(self.homework.can_be_corrected())
    
    def test_homework_is_overdue(self) -> None:
        """测试作业是否过期。"""
        # 设置未来的截止时间
        self.homework.deadline = timezone.now() + timezone.timedelta(hours=1)
        self.assertFalse(self.homework.is_overdue())
        
        # 设置过去的截止时间
        self.homework.deadline = timezone.now() - timezone.timedelta(hours=1)
        self.assertTrue(self.homework.is_overdue())
        
        # 没有截止时间
        self.homework.deadline = None
        self.assertFalse(self.homework.is_overdue())


# ==================== 题目模型测试 ====================
class QuestionModelTest(TestCase):
    """
    题目模型测试类。
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
            description="测试用作业",
            student=self.student,
            subject="数学",
            status=HomeworkStatus.SUBMITTED,
        )
        
        # 创建测试题目
        self.question = Question.objects.create(
            homework=self.homework,
            question_number=1,
            content="1 + 1 = ?",
            question_type=QuestionType.SINGLE_CHOICE,
            student_answer="2",
            correct_answer="2",
            max_score=Decimal("10.00"),
        )
    
    def test_question_creation(self) -> None:
        """测试题目创建。"""
        self.assertEqual(self.question.homework, self.homework)
        self.assertEqual(self.question.question_number, 1)
        self.assertEqual(self.question.content, "1 + 1 = ?")
        self.assertEqual(self.question.question_type, QuestionType.SINGLE_CHOICE)
        self.assertEqual(self.question.student_answer, "2")
        self.assertEqual(self.question.correct_answer, "2")
        self.assertEqual(self.question.max_score, Decimal("10.00"))
    
    def test_question_string_representation(self) -> None:
        """测试题目的字符串表示。"""
        expected = f"题目{self.question.question_number} - {self.homework.title}"
        self.assertEqual(str(self.question), expected)
    
    def test_question_score_calculation_single_choice(self) -> None:
        """测试单选题得分计算。"""
        # 答案正确的情况
        self.question.student_answer = "2"
        self.question.correct_answer = "2"
        self.question.max_score = Decimal("10.00")
        
        calculated_score = self.question.calculate_score()
        self.assertEqual(calculated_score, Decimal("10.00"))
        
        # 答案错误的情况
        self.question.student_answer = "3"
        calculated_score = self.question.calculate_score()
        self.assertEqual(calculated_score, Decimal("0.00"))
    
    def test_question_score_calculation_multiple_choice(self) -> None:
        """测试多选题得分计算。"""
        self.question.question_type = QuestionType.MULTIPLE_CHOICE
        self.question.max_score = Decimal("10.00")
        
        # 全部正确的情况
        self.question.student_answer = "A,B,C"
        self.question.correct_answer = "A,B,C"
        calculated_score = self.question.calculate_score()
        self.assertEqual(calculated_score, Decimal("10.00"))
        
        # 部分正确的情况
        self.question.student_answer = "A,B"
        calculated_score = self.question.calculate_score()
        self.assertEqual(calculated_score, Decimal("6.67"))  # 10 * 2/3
        
        # 有错误选项的情况
        self.question.student_answer = "A,B,D"
        calculated_score = self.question.calculate_score()
        self.assertEqual(calculated_score, Decimal("0.00"))
    
    def test_question_update_score(self) -> None:
        """测试题目得分更新。"""
        # 设置正确答案
        self.question.student_answer = "2"
        self.question.correct_answer = "2"
        self.question.max_score = Decimal("10.00")
        
        # 更新得分
        self.question.update_score()
        
        # 验证得分和正确性标记
        self.assertEqual(self.question.actual_score, Decimal("10.00"))
        self.assertTrue(self.question.is_correct)
        
        # 设置错误答案
        self.question.student_answer = "3"
        self.question.update_score()
        
        # 验证得分和正确性标记
        self.assertEqual(self.question.actual_score, Decimal("0.00"))
        self.assertFalse(self.question.is_correct)


# ==================== 知识点模型测试 ====================
class KnowledgePointModelTest(TestCase):
    """
    知识点模型测试类。
    """
    
    def setUp(self) -> None:
        """测试前置设置。"""
        # 创建测试知识点
        self.knowledge_point = KnowledgePoint.objects.create(
            name="一元二次方程",
            description="形如 ax² + bx + c = 0 的方程",
            subject="数学",
            difficulty_level=3,
        )
    
    def test_knowledge_point_creation(self) -> None:
        """测试知识点创建。"""
        self.assertEqual(self.knowledge_point.name, "一元二次方程")
        self.assertEqual(self.knowledge_point.subject, "数学")
        self.assertEqual(self.knowledge_point.difficulty_level, 3)
    
    def test_knowledge_point_string_representation(self) -> None:
        """测试知识点的字符串表示。"""
        expected = f"{self.knowledge_point.subject} - {self.knowledge_point.name} (难度: {self.knowledge_point.difficulty_level})"
        self.assertEqual(str(self.knowledge_point), expected)


# ==================== 模型关系测试 ====================
class ModelRelationshipTest(TestCase):
    """
    模型关系测试类。
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
            title="关系测试作业",
            student=self.student,
            subject="数学",
            status=HomeworkStatus.SUBMITTED,
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
        
        # 创建测试知识点
        self.knowledge_point1 = KnowledgePoint.objects.create(
            name="知识点1",
            subject="数学",
            difficulty_level=2,
        )
        
        self.knowledge_point2 = KnowledgePoint.objects.create(
            name="知识点2",
            subject="数学",
            difficulty_level=3,
        )
    
    def test_homework_question_relationship(self) -> None:
        """测试作业与题目的关系。"""
        # 验证作业包含的题目
        questions = self.homework.questions.all()
        self.assertEqual(questions.count(), 2)
        self.assertIn(self.question1, questions)
        self.assertIn(self.question2, questions)
        
        # 验证题目所属的作业
        self.assertEqual(self.question1.homework, self.homework)
        self.assertEqual(self.question2.homework, self.homework)
    
    def test_question_knowledge_point_relationship(self) -> None:
        """测试题目与知识点的关系。"""
        # 添加知识点关联
        self.question1.knowledge_points.add(self.knowledge_point1, self.knowledge_point2)
        self.question2.knowledge_points.add(self.knowledge_point1)
        
        # 验证题目包含的知识点
        self.assertEqual(self.question1.knowledge_points.count(), 2)
        self.assertEqual(self.question2.knowledge_points.count(), 1)
        
        # 验证知识点关联的题目
        self.assertEqual(self.knowledge_point1.questions.count(), 2)
        self.assertEqual(self.knowledge_point2.questions.count(), 1)
        
        # 验证知识点获取相关作业
        related_homeworks = self.knowledge_point1.get_related_homeworks()
        self.assertEqual(related_homeworks.count(), 1)
        self.assertIn(self.homework, related_homeworks)
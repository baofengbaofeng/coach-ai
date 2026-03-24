"""
测试模型是否正常工作。
"""
import os
import sys
import django
from pathlib import Path
from decimal import Decimal
from django.utils import timezone


def main() -> None:
    """主函数。"""
    # 设置项目根目录
    BASE_DIR = Path(__file__).resolve().parent
    
    # 添加apps目录到Python路径
    sys.path.insert(0, str(BASE_DIR / "apps"))
    
    # 使用简化的设置
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.simple")
    
    # 初始化Django
    django.setup()
    
    from apps.homework.models import Homework, Question, KnowledgePoint
    from apps.accounts.models import User
    from core.constants import HomeworkStatus, QuestionType, UserRole
    
    print("🔍 测试模型功能...")
    
    try:
        # 创建测试用户
        print("\n1. 创建测试用户...")
        user, created = User.objects.get_or_create(
            username="test_user",
            defaults={
                "email": "test@example.com",
                "role": UserRole.STUDENT,
            }
        )
        if created:
            user.set_password("testpass123")
            user.save()
            print(f"✅ 创建用户: {user.username}")
        else:
            print(f"✅ 使用现有用户: {user.username}")
        
        # 创建作业
        print("\n2. 创建作业...")
        homework = Homework.objects.create(
            title="数学作业测试",
            description="这是一份测试用的数学作业",
            student=user,
            subject="数学",
            status=HomeworkStatus.SUBMITTED,
            submitted_at=timezone.now(),
            deadline=timezone.now() + timezone.timedelta(days=1),
            total_score=Decimal("0.00"),
            accuracy_rate=Decimal("0.00"),
        )
        print(f"✅ 创建作业: {homework.title} (ID: {homework.id})")
        print(f"   状态: {homework.get_status_display()}")
        print(f"   进度: {homework.get_progress_percentage()}%")
        print(f"   是否过期: {homework.is_overdue()}")
        
        # 创建题目
        print("\n3. 创建题目...")
        question = Question.objects.create(
            homework=homework,
            question_number=1,
            content="1 + 1 = ?",
            question_type=QuestionType.SINGLE_CHOICE,
            student_answer="2",
            correct_answer="2",
            max_score=Decimal("10.00"),
            actual_score=Decimal("0.00"),
            correction_notes="",
            is_correct=False,
        )
        print(f"✅ 创建题目: 题号{question.question_number}")
        print(f"   题目类型: {question.get_question_type_display()}")
        
        # 计算得分
        print("\n4. 计算题目得分...")
        question.update_score()
        question.save()
        print(f"✅ 得分计算完成:")
        print(f"   实际得分: {question.actual_score}")
        print(f"   是否正确: {question.is_correct}")
        print(f"   得分率: {(question.actual_score / question.max_score * 100) if question.max_score > 0 else 0}%")
        
        # 创建知识点
        print("\n5. 创建知识点...")
        knowledge_point = KnowledgePoint.objects.create(
            name="加法运算",
            description="基本的加法运算规则",
            subject="数学",
            difficulty_level=1,
        )
        print(f"✅ 创建知识点: {knowledge_point.name}")
        print(f"   科目: {knowledge_point.subject}")
        print(f"   难度: {knowledge_point.difficulty_level}")
        
        # 关联知识点和题目
        print("\n6. 关联知识点和题目...")
        question.knowledge_points.add(knowledge_point)
        print(f"✅ 知识点关联完成")
        print(f"   题目关联的知识点数量: {question.knowledge_points.count()}")
        print(f"   知识点关联的题目数量: {knowledge_point.questions.count()}")
        
        # 更新作业统计
        print("\n7. 更新作业统计...")
        # 重新计算所有题目得分
        for q in homework.questions.all():
            q.update_score()
            q.save()
        
        # 计算总分和正确率
        total_score = sum(q.actual_score for q in homework.questions.all())
        correct_count = homework.questions.filter(is_correct=True).count()
        question_count = homework.questions.count()
        accuracy_rate = (correct_count / question_count * 100) if question_count > 0 else 0
        
        homework.total_score = total_score
        homework.accuracy_rate = accuracy_rate
        homework.save()
        
        print(f"✅ 作业统计更新完成:")
        print(f"   总分: {homework.total_score}")
        print(f"   正确率: {homework.accuracy_rate}%")
        print(f"   题目数量: {question_count}")
        print(f"   正确题目数量: {correct_count}")
        
        # 查询测试
        print("\n8. 查询测试...")
        # 查询用户的所有作业
        user_homeworks = Homework.objects.filter(student=user)
        print(f"✅ 用户作业数量: {user_homeworks.count()}")
        
        # 查询数学科目的作业
        math_homeworks = Homework.objects.filter(subject="数学")
        print(f"✅ 数学作业数量: {math_homeworks.count()}")
        
        # 查询已提交的作业
        submitted_homeworks = Homework.objects.filter(status=HomeworkStatus.SUBMITTED)
        print(f"✅ 已提交作业数量: {submitted_homeworks.count()}")
        
        print("\n🎉 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
"""
完整数据库设置脚本。
"""
import os
import sys
import django
from pathlib import Path


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
    
    from django.core.management import call_command
    import io
    
    print("=" * 60)
    print("完整数据库设置")
    print("=" * 60)
    
    # 1. 应用Django内置迁移
    print("\n1. 应用Django内置迁移...")
    out = io.StringIO()
    call_command("migrate", stdout=out, verbosity=1)
    print("✅ Django内置迁移完成")
    
    # 2. 修改homework迁移，移除对accounts的依赖
    print("\n2. 修改homework迁移依赖...")
    
    # 读取homework迁移文件
    migration_file = BASE_DIR / "apps" / "homework" / "migrations" / "0001_initial.py"
    with open(migration_file, 'r') as f:
        content = f.read()
    
    # 移除对AUTH_USER_MODEL的依赖
    new_content = content.replace(
        'dependencies = [\n    migrations.swappable_dependency(settings.AUTH_USER_MODEL),\n]',
        'dependencies = []'
    )
    
    # 将ForeignKey改为IntegerField（临时解决方案）
    new_content = new_content.replace(
        '("student", models.ForeignKey(help_text="提交作业的学生", on_delete=django.db.models.deletion.CASCADE, related_name="homeworks", to=settings.AUTH_USER_MODEL, verbose_name="学生"))',
        '("student_id", models.IntegerField(help_text="学生ID", verbose_name="学生ID"))'
    )
    
    with open(migration_file, 'w') as f:
        f.write(new_content)
    
    print("✅ homework迁移已修改")
    
    # 3. 应用homework迁移
    print("\n3. 应用homework迁移...")
    out = io.StringIO()
    call_command("migrate", "homework", stdout=out, verbosity=1)
    print(out.getvalue())
    print("✅ homework迁移应用完成")
    
    # 4. 创建测试数据
    print("\n4. 创建测试数据...")
    create_test_data()
    
    print("\n" + "=" * 60)
    print("数据库设置完成！")
    print("=" * 60)


def create_test_data() -> None:
    """创建测试数据。"""
    from django.db import connection
    from django.utils import timezone
    from decimal import Decimal
    
    print("  创建测试数据...")
    
    with connection.cursor() as cursor:
        # 创建测试用户
        cursor.execute('''
            INSERT OR IGNORE INTO auth_user 
            (username, password, is_superuser, is_staff, is_active, date_joined, email, first_name, last_name)
            VALUES 
            ('test_student', 'pbkdf2_sha256$600000$test123$testhash', 0, 0, 1, ?, 'student@test.com', 'Test', 'Student')
        ''', [timezone.now().isoformat()])
        
        # 获取用户ID
        cursor.execute("SELECT id FROM auth_user WHERE username = 'test_student'")
        user_id = cursor.fetchone()[0]
        
        # 创建作业
        cursor.execute('''
            INSERT INTO homework_homework 
            (title, description, student_id, subject, status, submitted_at, deadline, total_score, accuracy_rate, created_at, updated_at)
            VALUES 
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [
            '数学作业测试',
            '这是一份测试用的数学作业',
            user_id,
            '数学',
            'submitted',
            timezone.now().isoformat(),
            (timezone.now() + timezone.timedelta(days=1)).isoformat(),
            '0.00',
            '0.00',
            timezone.now().isoformat(),
            timezone.now().isoformat()
        ])
        
        # 获取作业ID
        cursor.execute("SELECT last_insert_rowid()")
        homework_id = cursor.fetchone()[0]
        
        # 创建题目
        cursor.execute('''
            INSERT INTO homework_question 
            (homework_id, question_number, content, question_type, student_answer, correct_answer, max_score, actual_score, correction_notes, is_correct, created_at, updated_at)
            VALUES 
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [
            homework_id,
            1,
            '1 + 1 = ?',
            'single_choice',
            '2',
            '2',
            '10.00',
            '10.00',
            '答案正确',
            1,
            timezone.now().isoformat(),
            timezone.now().isoformat()
        ])
        
        # 创建知识点
        cursor.execute('''
            INSERT INTO homework_knowledgepoint 
            (name, description, subject, difficulty_level, created_at, updated_at)
            VALUES 
            (?, ?, ?, ?, ?, ?)
        ''', [
            '加法运算',
            '基本的加法运算规则',
            '数学',
            1,
            timezone.now().isoformat(),
            timezone.now().isoformat()
        ])
        
        print("  ✅ 测试数据创建完成")
        print(f"     用户ID: {user_id}")
        print(f"     作业ID: {homework_id}")


if __name__ == "__main__":
    main()
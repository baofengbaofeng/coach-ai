"""
测试配置文件，用于在没有完整Django环境的情况下进行代码验证。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置Django配置
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

# 尝试导入Django
try:
    import django
    django.setup()
    print("✅ Django环境配置成功")
except ImportError:
    print("⚠️ Django未安装，跳过Django环境配置")


def validate_models() -> None:
    """验证模型定义。"""
    print("\n🔍 验证模型定义...")
    
    try:
        from apps.homework.models import Homework, Question, KnowledgePoint
        
        # 检查模型类是否存在
        models = [Homework, Question, KnowledgePoint]
        model_names = [model.__name__ for model in models]
        
        print(f"✅ 找到 {len(models)} 个模型: {', '.join(model_names)}")
        
        # 检查模型字段
        homework_fields = [field.name for field in Homework._meta.get_fields()]
        print(f"✅ Homework模型有 {len(homework_fields)} 个字段")
        
        question_fields = [field.name for field in Question._meta.get_fields()]
        print(f"✅ Question模型有 {len(question_fields)} 个字段")
        
        knowledge_point_fields = [field.name for field in KnowledgePoint._meta.get_fields()]
        print(f"✅ KnowledgePoint模型有 {len(knowledge_point_fields)} 个字段")
        
    except Exception as e:
        print(f"❌ 模型验证失败: {e}")


def validate_serializers() -> None:
    """验证序列化器定义。"""
    print("\n🔍 验证序列化器定义...")
    
    try:
        from apps.homework.serializers import (
            HomeworkSerializer,
            QuestionSerializer,
            KnowledgePointSerializer,
            HomeworkSubmitSerializer,
            HomeworkCorrectionSerializer,
        )
        
        serializers = [
            HomeworkSerializer,
            QuestionSerializer,
            KnowledgePointSerializer,
            HomeworkSubmitSerializer,
            HomeworkCorrectionSerializer,
        ]
        
        serializer_names = [serializer.__name__ for serializer in serializers]
        print(f"✅ 找到 {len(serializers)} 个序列化器: {', '.join(serializer_names)}")
        
    except Exception as e:
        print(f"❌ 序列化器验证失败: {e}")


def validate_views() -> None:
    """验证视图定义。"""
    print("\n🔍 验证视图定义...")
    
    try:
        from apps.homework.views import (
            HomeworkViewSet,
            QuestionViewSet,
            KnowledgePointViewSet,
        )
        
        views = [
            HomeworkViewSet,
            QuestionViewSet,
            KnowledgePointViewSet,
        ]
        
        view_names = [view.__name__ for view in views]
        print(f"✅ 找到 {len(views)} 个视图: {', '.join(view_names)}")
        
    except Exception as e:
        print(f"❌ 视图验证失败: {e}")


def validate_admin() -> None:
    """验证管理界面配置。"""
    print("\n🔍 验证管理界面配置...")
    
    try:
        from apps.homework.admin import (
            HomeworkAdmin,
            QuestionAdmin,
            KnowledgePointAdmin,
        )
        
        admin_classes = [
            HomeworkAdmin,
            QuestionAdmin,
            KnowledgePointAdmin,
        ]
        
        admin_names = [admin.__name__ for admin in admin_classes]
        print(f"✅ 找到 {len(admin_classes)} 个管理类: {', '.join(admin_names)}")
        
    except Exception as e:
        print(f"❌ 管理界面验证失败: {e}")


def validate_tests() -> None:
    """验证测试文件。"""
    print("\n🔍 验证测试文件...")
    
    test_files = [
        "apps/homework/tests/test_models.py",
        "apps/homework/tests/test_serializers.py",
    ]
    
    for test_file in test_files:
        file_path = project_root / test_file
        if file_path.exists():
            print(f"✅ 测试文件存在: {test_file}")
        else:
            print(f"❌ 测试文件不存在: {test_file}")


def validate_migrations() -> None:
    """验证迁移文件。"""
    print("\n🔍 验证迁移文件...")
    
    migration_file = "apps/homework/migrations/0001_initial.py"
    file_path = project_root / migration_file
    
    if file_path.exists():
        print(f"✅ 迁移文件存在: {migration_file}")
        
        # 检查文件大小
        file_size = file_path.stat().st_size
        print(f"✅ 迁移文件大小: {file_size} 字节")
    else:
        print(f"❌ 迁移文件不存在: {migration_file}")


def validate_constants() -> None:
    """验证常量定义。"""
    print("\n🔍 验证常量定义...")
    
    try:
        from core.constants import (
            BusinessRules,
            FileTypes,
            HomeworkStatus,
            QuestionType,
        )
        
        # 检查常量类
        constant_classes = [
            BusinessRules,
            FileTypes,
            HomeworkStatus,
            QuestionType,
        ]
        
        class_names = [cls.__name__ for cls in constant_classes]
        print(f"✅ 找到 {len(constant_classes)} 个常量类: {', '.join(class_names)}")
        
        # 检查枚举值
        homework_status_values = [status.value for status in HomeworkStatus]
        print(f"✅ HomeworkStatus枚举有 {len(homework_status_values)} 个值: {', '.join(homework_status_values)}")
        
        question_type_values = [qtype.value for qtype in QuestionType]
        print(f"✅ QuestionType枚举有 {len(question_type_values)} 个值: {', '.join(question_type_values)}")
        
    except Exception as e:
        print(f"❌ 常量验证失败: {e}")


def validate_permissions() -> None:
    """验证权限类。"""
    print("\n🔍 验证权限类...")
    
    try:
        from core.permissions import (
            IsOwnerOrReadOnly,
            IsTeacherOrAdmin,
            IsStudentOrParent,
            IsStudentOnly,
            IsParentOnly,
            IsAdminOnly,
            IsOwnerOrTeacherOrAdmin,
            IsStudentOrTeacherOrAdmin,
            CanViewHomework,
            CanCorrectHomework,
            CanProcessHomework,
        )
        
        permission_classes = [
            IsOwnerOrReadOnly,
            IsTeacherOrAdmin,
            IsStudentOrParent,
            IsStudentOnly,
            IsParentOnly,
            IsAdminOnly,
            IsOwnerOrTeacherOrAdmin,
            IsStudentOrTeacherOrAdmin,
            CanViewHomework,
            CanCorrectHomework,
            CanProcessHomework,
        ]
        
        permission_names = [perm.__name__ for perm in permission_classes]
        print(f"✅ 找到 {len(permission_classes)} 个权限类: {', '.join(permission_names)}")
        
    except Exception as e:
        print(f"❌ 权限验证失败: {e}")


def main() -> None:
    """主验证函数。"""
    print("=" * 60)
    print("CoachAI Homework模块代码质量验证")
    print("=" * 60)
    
    # 执行各项验证
    validate_models()
    validate_serializers()
    validate_views()
    validate_admin()
    validate_tests()
    validate_migrations()
    validate_constants()
    validate_permissions()
    
    print("\n" + "=" * 60)
    print("验证完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
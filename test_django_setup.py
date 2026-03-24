"""
Django环境设置测试脚本。
"""
import os
import sys
import django
from pathlib import Path

# 设置项目根目录
BASE_DIR = Path(__file__).resolve().parent

# 添加apps目录到Python路径
sys.path.insert(0, str(BASE_DIR / "apps"))

# 设置Django设置模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.simple")

try:
    # 初始化Django
    django.setup()
    print("✅ Django环境设置成功")
    
    # 测试导入模型
    from apps.homework.models import Homework, Question, KnowledgePoint
    print("✅ 模型导入成功")
    
    # 测试导入序列化器
    from apps.homework.serializers import HomeworkSerializer
    print("✅ 序列化器导入成功")
    
    # 测试导入视图
    from apps.homework.views import HomeworkViewSet
    print("✅ 视图导入成功")
    
    # 测试导入常量
    from core.constants import BusinessRules, HomeworkStatus, QuestionType
    print("✅ 常量导入成功")
    
    # 测试常量值
    print(f"✅ HomeworkStatus值: {[status.value for status in HomeworkStatus]}")
    print(f"✅ QuestionType值: {[qtype.value for qtype in QuestionType]}")
    
    # 检查BusinessRules常量
    print(f"✅ HOMEWORK_TITLE_MAX_LENGTH: {BusinessRules.HOMEWORK_TITLE_MAX_LENGTH}")
    print(f"✅ HOMEWORK_DESCRIPTION_MAX_LENGTH: {BusinessRules.HOMEWORK_DESCRIPTION_MAX_LENGTH}")
    
except Exception as e:
    print(f"❌ Django环境设置失败: {e}")
    import traceback
    traceback.print_exc()
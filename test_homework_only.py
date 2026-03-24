"""
只测试homework模块的Django环境。
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
    
    # 测试导入homework模型
    from apps.homework.models import Homework, Question, KnowledgePoint
    print("✅ homework模型导入成功")
    
    # 检查模型元数据
    print(f"\n🔍 Homework模型字段:")
    for field in Homework._meta.get_fields():
        print(f"  - {field.name}: {field.__class__.__name__}")
    
    print(f"\n🔍 Question模型字段:")
    for field in Question._meta.get_fields():
        if hasattr(field, 'name'):
            print(f"  - {field.name}: {field.__class__.__name__}")
    
    print(f"\n🔍 KnowledgePoint模型字段:")
    for field in KnowledgePoint._meta.get_fields():
        if hasattr(field, 'name'):
            print(f"  - {field.name}: {field.__class__.__name__}")
    
    # 测试创建迁移
    print("\n🔍 测试迁移生成...")
    from django.core.management import call_command
    import io
    
    # 捕获输出
    out = io.StringIO()
    call_command("makemigrations", "homework", dry_run=True, stdout=out)
    output = out.getvalue()
    
    if "No changes detected" in output:
        print("✅ 迁移文件已是最新")
    else:
        print("⚠️ 检测到模型变更，需要生成新迁移")
        print(output)
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
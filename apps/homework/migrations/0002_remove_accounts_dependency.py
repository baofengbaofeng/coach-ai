"""
修复迁移依赖问题：移除对accounts的依赖。
"""
from django.db import migrations


class Migration(migrations.Migration):
    """
    修复迁移依赖类。
    """
    
    dependencies = [
        ('homework', '0001_initial'),
    ]
    
    operations = [
        # 空操作，只是为了修复依赖关系
    ]
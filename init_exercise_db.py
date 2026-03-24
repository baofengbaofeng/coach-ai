"""
初始化运动模块数据库，创建必要的表结构。
"""
import os
import sys

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.simple")

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import django
django.setup()

from django.core.management import execute_from_command_line

print("=== 初始化运动模块数据库 ===")

try:
    # 1. 创建迁移文件（如果不存在）
    print("1. 检查迁移文件...")
    
    # 2. 应用迁移
    print("2. 应用数据库迁移...")
    execute_from_command_line(["manage.py", "migrate", "exercise"])
    
    print("✅ 数据库初始化完成！")
    
except Exception as e:
    print(f"❌ 初始化失败: {str(e)}")
    import traceback
    traceback.print_exc()
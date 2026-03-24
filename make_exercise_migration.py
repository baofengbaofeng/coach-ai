"""
专门用于生成exercise应用迁移文件的脚本。
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

if __name__ == "__main__":
    # 只生成exercise应用的迁移文件
    execute_from_command_line(["manage.py", "makemigrations", "exercise"])
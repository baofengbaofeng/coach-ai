"""
CoachAI项目包初始化
提供统一的导入路径设置
"""

import sys
import os

# 确保src目录在Python路径中
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 导出常用模块
__all__ = []
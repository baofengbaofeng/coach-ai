#!/usr/bin/env python3
"""
Python环境设置脚本
自动设置PYTHONPATH以便可以直接导入模块
"""

import os
import sys

def setup_environment():
    """设置Python环境"""
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    coding_dir = os.path.join(project_root, "coding")
    
    print(f"项目根目录: {project_root}")
    print(f"代码目录: {coding_dir}")
    
    # 检查目录是否存在
    if not os.path.exists(coding_dir):
        print(f"错误: coding目录不存在: {coding_dir}")
        return False
    
    # 添加到Python路径
    if coding_dir not in sys.path:
        sys.path.insert(0, coding_dir)
        print(f"已添加 {coding_dir} 到 Python路径")
    else:
        print(f"{coding_dir} 已在 Python路径中")
    
    return True

def test_imports():
    """测试导入是否正常工作"""
    
    print("\n测试导入:")
    
    tests = [
        ("import config", "import config"),
        ("from config import config", "from config import config"),
        ("import tornado", "import tornado"),
        ("from tornado.core.application import create_application", 
         "from tornado.core.application import create_application"),
        ("import database", "import database"),
        ("from database.connection import get_db_session", 
         "from database.connection import get_db_session"),
    ]
    
    all_passed = True
    for test_name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✅ {test_name}")
        except ImportError as e:
            print(f"❌ {test_name}: {e}")
            all_passed = False
    
    return all_passed

def main():
    """主函数"""
    print("设置CoachAI项目Python环境")
    print("=" * 50)
    
    if not setup_environment():
        return 1
    
    print("\n当前Python路径:")
    for i, path in enumerate(sys.path[:5]):
        print(f"  [{i}] {path}")
    if len(sys.path) > 5:
        print(f"  ... 还有 {len(sys.path) - 5} 个路径")
    
    if test_imports():
        print("\n✅ 所有导入测试通过！")
        print("\n现在可以直接使用以下导入:")
        print("  from config import config")
        print("  from tornado.core.application import create_application")
        print("  from database.connection import get_db_session")
        return 0
    else:
        print("\n❌ 有些导入测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
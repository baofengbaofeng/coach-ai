#!/usr/bin/env python3
"""
测试导入路径是否正常工作
"""

import sys

def test_imports():
    """测试各种导入方式"""
    
    print("测试1: 直接导入（安装后应该能工作）")
    try:
        # 这些导入应该在项目安装后工作
        import config
        print("✅ import config")
        
        import tornado
        print("✅ import tornado")
        
        import database
        print("✅ import database")
    except ImportError as e:
        print(f"❌ 直接导入失败: {e}")
    
    print("\n测试2: 从模块导入")
    try:
        from config import config as cfg
        print("✅ from config import config")
        
        from tornado.core.application import create_application
        print("✅ from tornado.core.application import create_application")
        
        from database.connection import get_db_session
        print("✅ from database.connection import get_db_session")
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
    
    print("\n测试3: 检查Python路径")
    print(f"Python路径: {sys.path[:5]}...")
    
    print("\n测试4: 检查包信息")
    try:
        import pkg_resources
        dist = pkg_resources.get_distribution("coach-ai")
        print(f"✅ coach-ai 已安装: {dist.version}")
        print(f"   位置: {dist.location}")
    except Exception as e:
        print(f"❌ 无法获取包信息: {e}")

if __name__ == "__main__":
    test_imports()
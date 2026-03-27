#!/usr/bin/env python3
"""
修复剩余的导入问题
"""

import os
import re

def fix_tornado_imports(filepath):
    """修复被错误替换的tornado导入"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_content = content
    
    # 修复被错误替换的tornado导入
    # webapp.httpserver -> tornado.httpserver
    # webapp.ioloop -> tornado.ioloop
    # webapp.web -> tornado.web
    patterns = [
        (r'from webapp\.httpserver import', 'from tornado.httpserver import'),
        (r'from webapp\.ioloop import', 'from tornado.ioloop import'),
        (r'from webapp\.web import', 'from tornado.web import'),
        (r'import webapp\.httpserver', 'import tornado.httpserver'),
        (r'import webapp\.ioloop', 'import tornado.ioloop'),
        (r'import webapp\.web', 'import tornado.web'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    if old_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def fix_coding_imports(filepath):
    """修复剩余的coding.导入"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_content = content
    
    # 修复coding.导入
    patterns = [
        (r'from coding\.config\.', 'from config.'),
        (r'from coding\.config import', 'from config import'),
        (r'import coding\.config', 'import config'),
        (r'from coding\.database\.', 'from database.'),
        (r'from coding\.database import', 'from database import'),
        (r'import coding\.database', 'import database'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    if old_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """主函数"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    coding_dir = os.path.join(project_root, "coding")
    
    print("修复剩余的导入问题")
    print("=" * 50)
    
    fixed_files = []
    
    # 遍历所有Python文件
    for root, dirs, files in os.walk(coding_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                fixed1 = fix_tornado_imports(filepath)
                fixed2 = fix_coding_imports(filepath)
                
                if fixed1 or fixed2:
                    fixed_files.append(filepath)
    
    print(f"修复了 {len(fixed_files)} 个文件:")
    for filepath in fixed_files:
        print(f"  {os.path.relpath(filepath, project_root)}")
    
    # 测试
    print("\n测试导入:")
    test_code = """
import sys
sys.path.insert(0, 'coding')

tests = [
    ('from tornado.httpserver import HTTPServer', 'from tornado.httpserver import HTTPServer'),
    ('from tornado.ioloop import IOLoop', 'from tornado.ioloop import IOLoop'),
    ('from tornado.web import Application', 'from tornado.web import Application'),
    ('from config import init_config', 'from config import init_config'),
    ('from webapp.core.application import create_application', 'from webapp.core.application import create_application'),
    ('from database.connection import get_db_session', 'from database.connection import get_db_session'),
]

all_passed = True
for test_name, import_stmt in tests:
    try:
        exec(import_stmt)
        print(f'✅ {test_name}')
    except ImportError as e:
        print(f'❌ {test_name}: {e}')
        all_passed = False

if all_passed:
    print('\\n✅ 所有导入测试通过！')
else:
    print('\\n❌ 有些导入测试失败')
"""
    
    import subprocess
    result = subprocess.run([sys.executable, "-c", test_code], 
                          cwd=project_root, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("错误输出:")
        print(result.stderr)
    
    return 0 if result.returncode == 0 else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
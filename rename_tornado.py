#!/usr/bin/env python3
"""
重命名tornado目录以避免与Python tornado包冲突
"""

import os
import shutil
import re

def rename_tornado_dir():
    """重命名tornado目录"""
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    coding_dir = os.path.join(project_root, "coding")
    old_tornado_dir = os.path.join(coding_dir, "tornado")
    new_tornado_dir = os.path.join(coding_dir, "webapp")
    
    print(f"项目根目录: {project_root}")
    print(f"旧目录: {old_tornado_dir}")
    print(f"新目录: {new_tornado_dir}")
    
    # 检查目录是否存在
    if not os.path.exists(old_tornado_dir):
        print(f"错误: tornado目录不存在: {old_tornado_dir}")
        return False
    
    if os.path.exists(new_tornado_dir):
        print(f"错误: 新目录已存在: {new_tornado_dir}")
        return False
    
    # 重命名目录
    print(f"重命名目录: tornado -> webapp")
    shutil.move(old_tornado_dir, new_tornado_dir)
    
    return True

def update_imports_in_file(filepath):
    """更新文件中的导入语句"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换导入语句
    # from coding.tornado -> from webapp
    # import coding.tornado -> import webapp
    old_content = content
    
    # 替换各种导入模式
    patterns = [
        (r'from coding\.tornado\.', 'from webapp.'),
        (r'import coding\.tornado', 'import webapp'),
        (r'from tornado\.', 'from webapp.'),
        (r'import tornado$', 'import webapp'),
        (r'import tornado\.', 'import webapp.'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    if old_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def update_all_imports():
    """更新所有文件中的导入语句"""
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    coding_dir = os.path.join(project_root, "coding")
    
    updated_files = []
    
    # 遍历所有Python文件
    for root, dirs, files in os.walk(coding_dir):
        # 跳过新目录
        if "webapp" in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if update_imports_in_file(filepath):
                    updated_files.append(filepath)
    
    # 更新tests目录
    tests_dir = os.path.join(project_root, "tests")
    if os.path.exists(tests_dir):
        for root, dirs, files in os.walk(tests_dir):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    if update_imports_in_file(filepath):
                        updated_files.append(filepath)
    
    # 更新scripts目录
    scripts_dir = os.path.join(project_root, "scripts")
    if os.path.exists(scripts_dir):
        for root, dirs, files in os.walk(scripts_dir):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    if update_imports_in_file(filepath):
                        updated_files.append(filepath)
    
    return updated_files

def main():
    """主函数"""
    print("重命名tornado目录以避免命名冲突")
    print("=" * 50)
    
    # 1. 重命名目录
    if not rename_tornado_dir():
        return 1
    
    # 2. 更新导入语句
    print("\n更新导入语句...")
    updated_files = update_all_imports()
    
    print(f"更新了 {len(updated_files)} 个文件:")
    for filepath in updated_files[:10]:  # 只显示前10个
        print(f"  {os.path.relpath(filepath)}")
    if len(updated_files) > 10:
        print(f"  ... 还有 {len(updated_files) - 10} 个文件")
    
    # 3. 测试导入
    print("\n测试导入...")
    test_code = """
import sys
sys.path.insert(0, 'coding')

try:
    import webapp
    print("✅ import webapp")
    
    from webapp.core.application import create_application
    print("✅ from webapp.core.application import create_application")
    
    from config import config
    print("✅ from config import config")
    
    from database.connection import get_db_session
    print("✅ from database.connection import get_db_session")
    
    print("\n✅ 所有导入测试通过！")
    print("\n现在可以直接使用以下导入:")
    print("  from config import config")
    print("  from webapp.core.application import create_application")
    print("  from database.connection import get_db_session")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    return 1
"""
    
    import subprocess
    project_root = os.path.dirname(os.path.abspath(__file__))
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
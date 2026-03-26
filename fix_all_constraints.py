#!/usr/bin/env python3
"""
修复所有模型约束脚本。
修复Django版本兼容性问题。
"""
import os
import sys
import re
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def fix_check_constraint_in_file(file_path: Path):
    """修复文件中的CheckConstraint语法"""
    if not file_path.exists():
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复 check=models.Q(...) 为 condition=models.Q(...)
    # 同时修复迁移文件中的 check=models.Q(('field__op', value)) 语法
    fixed_content = content
    
    # 修复 check=models.Q( 模式
    fixed_content = re.sub(
        r'check=models\.Q\(',
        'condition=models.Q(',
        fixed_content
    )
    
    # 修复 check=models.Q(('field__op', value)) 模式（迁移文件）
    fixed_content = re.sub(
        r"check=models\.Q\(\(('.*?'),\s*(.*?)\)\)",
        r"condition=models.Q(\1=\2)",
        fixed_content
    )
    
    # 修复更复杂的迁移语法
    fixed_content = re.sub(
        r"check=models\.Q\(\(('.*?'),\s*models\.F\('(.*?)'\)\)",
        r"condition=models.Q(\1=models.F('\2'))",
        fixed_content
    )
    
    if fixed_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        return True
    
    return False

# 修复所有Python文件
print("开始修复模型约束...")

fixed_files = []

# 修复apps目录下的所有模型和迁移文件
for root, dirs, files in os.walk(project_root / "apps"):
    for file in files:
        if file.endswith('.py'):
            file_path = Path(root) / file
            if fix_check_constraint_in_file(file_path):
                fixed_files.append(file_path.relative_to(project_root))

# 修复其他目录
other_dirs = ["config", "core", "services"]
for dir_name in other_dirs:
    dir_path = project_root / dir_name
    if dir_path.exists():
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    if fix_check_constraint_in_file(file_path):
                        fixed_files.append(file_path.relative_to(project_root))

# 输出结果
if fixed_files:
    print(f"\n✅ 已修复 {len(fixed_files)} 个文件:")
    for file in fixed_files:
        print(f"  - {file}")
else:
    print("\n✅ 未发现需要修复的文件")

print("\n注意: 这是临时修复，建议:")
print("1. 升级到兼容的Django版本")
print("2. 或调整项目使用的Django版本")
print("3. 或使用正确的CheckConstraint语法")
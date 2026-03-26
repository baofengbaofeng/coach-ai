#!/usr/bin/env python3
"""
修复模型约束脚本。
临时修复Django版本兼容性问题。
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# 修复accounts/models.py文件
accounts_model_file = project_root / "apps" / "accounts" / "models.py"

if not accounts_model_file.exists():
    print(f"❌ 文件不存在: {accounts_model_file}")
    sys.exit(1)

# 读取文件内容
with open(accounts_model_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 修复CheckConstraint语法（Django 5.x兼容性）
# 将 check=models.Q(...) 改为 condition=models.Q(...)
fixed_content = content.replace(
    'models.CheckConstraint(\n                check=models.Q(points__gte=0),',
    'models.CheckConstraint(\n                condition=models.Q(points__gte=0),'
).replace(
    'models.CheckConstraint(\n                check=models.Q(level__gte=1),',
    'models.CheckConstraint(\n                condition=models.Q(level__gte=1),'
)

# 写回文件
with open(accounts_model_file, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("✅ 已修复accounts/models.py中的CheckConstraint语法")

# 检查其他模型文件
model_files = [
    project_root / "apps" / "tasks" / "models.py",
    project_root / "apps" / "achievements" / "models.py",
    project_root / "apps" / "common" / "models.py",
]

for model_file in model_files:
    if model_file.exists():
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'check=models.Q(' in content:
            fixed_content = content.replace('check=models.Q(', 'condition=models.Q(')
            with open(model_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ 已修复{model_file.relative_to(project_root)}中的CheckConstraint语法")

print("\n✅ 所有模型约束已修复完成")
print("注意: 这是临时修复，建议升级到兼容的Django版本或调整约束语法")
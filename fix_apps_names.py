#!/usr/bin/env python
"""
修复所有应用的apps.py文件中的name配置。
"""
import os
import re
from pathlib import Path


def fix_app_name(file_path: Path) -> bool:
    """修复单个apps.py文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 获取应用目录名
    app_dir = file_path.parent.name
    
    # 替换name配置
    # 从: name: str = "accounts"
    # 到: name: str = "apps.accounts"
    old_pattern = rf'name: str = "{app_dir}"'
    new_content = f'name: str = "apps.{app_dir}"'
    
    if old_pattern in content:
        content = content.replace(old_pattern, new_content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 修复: {file_path} -> name: str = \"apps.{app_dir}\"")
        return True
    else:
        # 检查是否已经是正确的格式
        if f'name: str = "apps.{app_dir}"' in content:
            print(f"✅ 已正确: {file_path}")
            return True
        else:
            print(f"⚠️  未找到匹配: {file_path}")
            return False


def main():
    """主函数"""
    base_dir = Path(__file__).parent
    apps_dir = base_dir / "apps"
    
    print("开始修复应用名称配置...")
    print(f"项目目录: {base_dir}")
    print(f"应用目录: {apps_dir}")
    print("-" * 50)
    
    fixed_count = 0
    total_count = 0
    
    for app_dir in apps_dir.iterdir():
        if app_dir.is_dir() and not app_dir.name.startswith("__"):
            apps_py = app_dir / "apps.py"
            if apps_py.exists():
                total_count += 1
                if fix_app_name(apps_py):
                    fixed_count += 1
    
    print("-" * 50)
    print(f"修复完成: {fixed_count}/{total_count} 个应用")
    
    if fixed_count == total_count:
        print("✅ 所有应用名称配置已修复！")
        return 0
    else:
        print("⚠️  部分应用配置可能有问题")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
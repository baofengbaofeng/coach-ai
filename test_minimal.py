#!/usr/bin/env python
"""
极简测试脚本，验证CoachAI项目基本结构。
"""
import os
import sys
from pathlib import Path


def test_project_structure():
    """测试项目基本结构"""
    print("=" * 60)
    print("CoachAI项目结构验证")
    print("=" * 60)
    
    BASE_DIR = Path(__file__).resolve().parent
    
    # 检查关键目录
    required_dirs = [
        BASE_DIR / "apps",
        BASE_DIR / "config",
        BASE_DIR / "config" / "settings",
        BASE_DIR / "core",
        BASE_DIR / "tests",
    ]
    
    print("\n1. 目录结构检查:")
    all_ok = True
    for dir_path in required_dirs:
        if dir_path.exists():
            print(f"  ✅ {dir_path.relative_to(BASE_DIR)}")
        else:
            print(f"  ❌ {dir_path.relative_to(BASE_DIR)} - 不存在")
            all_ok = False
    
    # 检查关键文件
    required_files = [
        BASE_DIR / "manage.py",
        BASE_DIR / "manage_simple.py",
        BASE_DIR / "pyproject.toml",
        BASE_DIR / "README.md",
        BASE_DIR / "config" / "settings" / "simple.py",
    ]
    
    print("\n2. 关键文件检查:")
    for file_path in required_files:
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✅ {file_path.relative_to(BASE_DIR)} ({size} 字节)")
        else:
            print(f"  ❌ {file_path.relative_to(BASE_DIR)} - 不存在")
            all_ok = False
    
    # 检查应用模块
    print("\n3. 应用模块检查:")
    apps_dir = BASE_DIR / "apps"
    if apps_dir.exists():
        apps = [d for d in apps_dir.iterdir() if d.is_dir() and not d.name.startswith("__")]
        for app in sorted(apps):
            has_models = (app / "models.py").exists()
            has_views = (app / "views.py").exists()
            has_serializers = (app / "serializers.py").exists()
            has_urls = (app / "urls.py").exists()
            
            status = []
            if has_models: status.append("模型")
            if has_views: status.append("视图")
            if has_serializers: status.append("序列化器")
            if has_urls: status.append("URL")
            
            print(f"  📁 {app.name}: {', '.join(status) if status else '空目录'}")
    else:
        print("  ❌ apps目录不存在")
        all_ok = False
    
    # 检查Python文件数量
    print("\n4. 代码文件统计:")
    python_files = list(BASE_DIR.rglob("*.py"))
    print(f"  Python文件总数: {len(python_files)}")
    
    # 按目录统计
    dir_stats = {}
    for py_file in python_files:
        rel_path = py_file.relative_to(BASE_DIR)
        parent_dir = rel_path.parts[0] if len(rel_path.parts) > 1 else "根目录"
        dir_stats[parent_dir] = dir_stats.get(parent_dir, 0) + 1
    
    for dir_name, count in sorted(dir_stats.items()):
        print(f"    {dir_name}: {count}个文件")
    
    # 检查数据库文件
    print("\n5. 数据库检查:")
    db_file = BASE_DIR / "db.sqlite3"
    if db_file.exists():
        size_mb = db_file.stat().st_size / (1024 * 1024)
        print(f"  ✅ SQLite数据库: {size_mb:.1f} MB")
    else:
        print("  ⚠️  无SQLite数据库文件")
    
    # 总结
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ 项目结构验证通过！")
        print("   所有关键目录和文件都存在。")
    else:
        print("⚠️  项目结构存在问题！")
        print("   请检查缺失的目录或文件。")
    
    return all_ok


def test_python_imports():
    """测试Python导入"""
    print("\n" + "=" * 60)
    print("Python导入测试")
    print("=" * 60)
    
    BASE_DIR = Path(__file__).resolve().parent
    
    # 添加apps目录到Python路径
    sys.path.insert(0, str(BASE_DIR / "apps"))
    
    # 测试导入核心模块
    modules_to_test = [
        "config.settings.simple",
        "apps.exercise.models",
        "apps.tasks.models",
        "core.constants",
    ]
    
    all_imports_ok = True
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ 成功导入: {module_name}")
        except ImportError as e:
            print(f"  ❌ 导入失败: {module_name}")
            print(f"     错误: {e}")
            all_imports_ok = False
        except Exception as e:
            print(f"  ⚠️  导入异常: {module_name}")
            print(f"     错误: {e}")
            all_imports_ok = False
    
    print("\n" + "=" * 60)
    if all_imports_ok:
        print("✅ Python导入测试通过！")
    else:
        print("⚠️  Python导入测试失败！")
        print("   可能需要安装依赖或修复导入路径。")
    
    return all_imports_ok


def main():
    """主函数"""
    print("开始验证CoachAI项目...")
    print(f"项目路径: {Path(__file__).resolve().parent}")
    print(f"Python版本: {sys.version.split()[0]}")
    
    structure_ok = test_project_structure()
    imports_ok = test_python_imports()
    
    print("\n" + "=" * 60)
    print("最终验证结果:")
    print("=" * 60)
    
    if structure_ok and imports_ok:
        print("🎉 项目验证完全通过！")
        print("   项目结构完整，可以继续开发。")
        return 0
    elif structure_ok and not imports_ok:
        print("⚠️  项目结构完整，但导入有问题。")
        print("   可能需要安装依赖包。")
        return 1
    elif not structure_ok and imports_ok:
        print("⚠️  导入正常，但项目结构不完整。")
        print("   可能缺少某些目录或文件。")
        return 2
    else:
        print("❌ 项目验证失败！")
        print("   需要修复项目结构和导入问题。")
        return 3


if __name__ == "__main__":
    sys.exit(main())
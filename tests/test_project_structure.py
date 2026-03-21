"""
项目结构测试文件，验证项目按照豆包AI助手最佳实践正确配置。
"""
import os
import sys
from pathlib import Path
from typing import List


def test_project_structure() -> None:
    """
    测试项目结构是否符合豆包AI助手最佳实践。
    
    Returns:
        None: 如果测试失败会抛出 AssertionError
    """
    # 获取项目根目录
    project_root: Path = Path(__file__).resolve().parent.parent
    
    # 1. 验证必须存在的目录（豆包最佳实践）
    required_dirs: List[str] = [
        "config",
        "apps", 
        "core",
        "tests",
        "docs",
    ]
    
    for dir_name in required_dirs:
        dir_path: Path = project_root / dir_name
        assert dir_path.exists() and dir_path.is_dir(), f"必须存在目录: {dir_name}"
        print(f"✅ 目录存在: {dir_name}")
    
    # 2. 验证必须存在的文件
    required_files: List[str] = [
        "manage.py",
        "pyproject.toml",
        "README.md",
        ".env.example",
        ".gitignore",
        "LICENSE",
        "config/__init__.py",
        "config/urls.py",
        "config/wsgi.py",
        "config/asgi.py",
        "config/settings/__init__.py",
        "config/settings/base.py",
        "config/settings/dev.py",
        "config/settings/prod.py",
        "apps/__init__.py",
        "core/__init__.py",
        "core/constants.py",
        "tests/__init__.py",
    ]
    
    for file_path in required_files:
        full_path: Path = project_root / file_path
        assert full_path.exists() and full_path.is_file(), f"必须存在文件: {file_path}"
        print(f"✅ 文件存在: {file_path}")
    
    # 3. 验证配置文件中是否添加了 apps 路径（豆包关键步骤）
    base_settings_path: Path = project_root / "config" / "settings" / "base.py"
    with open(base_settings_path, "r", encoding="utf-8") as f:
        base_settings_content: str = f.read()
    
    # 检查是否包含 apps 路径添加代码
    assert "sys.path.insert(0, os.path.join(BASE_DIR, \"apps\"))" in base_settings_content, \
        "base.py 必须添加 apps 目录到 Python 路径"
    print("✅ base.py 已正确配置 apps 路径")
    
    # 4. 验证 manage.py 使用正确的设置模块
    manage_py_path: Path = project_root / "manage.py"
    with open(manage_py_path, "r", encoding="utf-8") as f:
        manage_py_content: str = f.read()
    
    assert "config.settings.dev" in manage_py_content, \
        "manage.py 必须使用 config.settings.dev 作为默认设置"
    print("✅ manage.py 已正确配置设置模块")
    
    # 5. 验证编码规范文件存在
    coding_style_path: Path = project_root / "convention" / "coding-style.md"
    assert coding_style_path.exists() and coding_style_path.is_file(), \
        "必须存在编码规范文件: convention/coding-style.md"
    print("✅ 编码规范文件存在")
    
    # 6. 验证文档文件已移动到 docs 目录
    required_docs: List[str] = [
        "docs/BRD.md",
        "docs/PRD.md",
        "docs/TECH_ARCHITECTURE_OVERVIEW.md",
        "docs/TECH_DETAILED_DESIGN.md",
    ]
    
    for doc_path in required_docs:
        full_doc_path: Path = project_root / doc_path
        assert full_doc_path.exists() and full_doc_path.is_file(), \
            f"文档文件必须存在: {doc_path}"
        print(f"✅ 文档文件存在: {doc_path}")
    
    print("\n🎉 所有项目结构测试通过！项目符合豆包AI助手最佳实践。")


def test_python_imports() -> None:
    """
    测试 Python 导入是否正确配置。
    
    Returns:
        None: 如果测试失败会抛出 ImportError
    """
    # 将项目根目录添加到 Python 路径
    project_root: Path = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # 将 apps 目录添加到 Python 路径（模拟 base.py 中的配置）
    apps_path: Path = project_root / "apps"
    if str(apps_path) not in sys.path:
        sys.path.insert(0, str(apps_path))
    
    # 测试是否可以导入配置模块
    try:
        # 测试导入配置模块
        import config
        import config.settings
        import config.settings.base
        import config.settings.dev
        import config.settings.prod
        
        print("✅ 配置模块导入成功")
        
        # 测试 Django 设置
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
        
        import django
        django.setup()
        
        print("✅ Django 设置成功")
        
    except ImportError as e:
        raise AssertionError(f"导入失败: {e}")
    except Exception as e:
        raise AssertionError(f"Django 设置失败: {e}")


if __name__ == "__main__":
    """
    主函数，运行所有测试。
    """
    print("=" * 60)
    print("开始测试项目结构（豆包AI助手最佳实践）")
    print("=" * 60)
    
    try:
        test_project_structure()
        print("\n" + "=" * 60)
        print("开始测试 Python 导入")
        print("=" * 60)
        test_python_imports()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！项目结构符合豆包AI助手最佳实践。")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)
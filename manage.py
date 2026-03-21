#!/usr/bin/env python
"""
Django 管理脚本入口点，用于执行 Django 管理命令，如启动开发服务器、运行数据库迁移等。
"""
import os
import sys


def main() -> None:
    """
    主函数，设置 Django 环境并执行管理命令。
    
    Returns:
        None: 此函数不返回值，但会根据命令执行结果设置退出码。
    """
    # 将 apps 目录添加到 Python 路径，确保可以正确导入应用模块（豆包最佳实践）
    project_root = os.path.dirname(os.path.abspath(__file__))
    apps_path = os.path.join(project_root, "apps")
    
    if apps_path not in sys.path:
        sys.path.insert(0, apps_path)
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入 Django 模块，请确保 Django 已正确安装且 PYTHONPATH 包含项目目录。"
        ) from exc
    
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

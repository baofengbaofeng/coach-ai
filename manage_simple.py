#!/usr/bin/env python
"""
简化的Django管理脚本，用于迁移和测试。
"""
import os
import sys
from pathlib import Path


def main() -> None:
    """主函数。"""
    # 设置项目根目录
    BASE_DIR = Path(__file__).resolve().parent
    
    # 添加apps目录到Python路径
    sys.path.insert(0, str(BASE_DIR / "apps"))
    
    # 使用简化的设置
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.simple")
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入Django。请确保已安装Django并激活了虚拟环境。"
        ) from exc
    
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
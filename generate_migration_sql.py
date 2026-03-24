"""
生成迁移SQL脚本。
"""
import os
import sys
import django
from pathlib import Path


def main() -> None:
    """主函数。"""
    # 设置项目根目录
    BASE_DIR = Path(__file__).resolve().parent
    
    # 添加apps目录到Python路径
    sys.path.insert(0, str(BASE_DIR / "apps"))
    
    # 使用简化的设置
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.simple")
    
    # 初始化Django
    django.setup()
    
    # 生成迁移SQL
    from django.core.management import call_command
    import io
    
    print("🔍 检查现有迁移...")
    
    # 列出所有迁移
    out = io.StringIO()
    call_command("showmigrations", "homework", stdout=out)
    print(out.getvalue())
    
    print("\n🔍 生成迁移SQL...")
    
    # 生成SQL
    out = io.StringIO()
    try:
        call_command("sqlmigrate", "homework", "0001", stdout=out)
        print("迁移SQL:")
        print(out.getvalue())
    except Exception as e:
        print(f"生成SQL失败: {e}")
        
        # 尝试生成新迁移
        print("\n🔍 尝试生成新迁移...")
        out = io.StringIO()
        call_command("makemigrations", "homework", dry_run=True, stdout=out)
        print(out.getvalue())


if __name__ == "__main__":
    main()
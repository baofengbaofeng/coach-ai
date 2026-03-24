"""
应用accounts迁移。
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
    
    from django.core.management import call_command
    import io
    
    print("🔍 应用accounts迁移...")
    
    out = io.StringIO()
    try:
        call_command("migrate", "apps.accounts", stdout=out, verbosity=1)
        print(out.getvalue())
        print("✅ accounts迁移应用完成")
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        
        # 检查迁移状态
        print("\n🔍 检查迁移状态...")
        out = io.StringIO()
        call_command("showmigrations", "accounts", stdout=out)
        print(out.getvalue())


if __name__ == "__main__":
    main()
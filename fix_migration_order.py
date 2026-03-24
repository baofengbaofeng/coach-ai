"""
修复迁移顺序问题。
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
    
    print("🔍 修复迁移顺序...")
    
    # 1. 回滚homework迁移
    print("\n1. 回滚homework迁移...")
    out = io.StringIO()
    try:
        call_command("migrate", "homework", "zero", stdout=out, verbosity=1)
        print(out.getvalue())
        print("✅ homework迁移已回滚")
    except Exception as e:
        print(f"❌ 回滚失败: {e}")
    
    # 2. 应用accounts迁移
    print("\n2. 应用accounts迁移...")
    out = io.StringIO()
    try:
        call_command("migrate", "apps.accounts", stdout=out, verbosity=1)
        print(out.getvalue())
        print("✅ accounts迁移应用完成")
    except Exception as e:
        print(f"❌ 应用失败: {e}")
    
    # 3. 重新应用homework迁移
    print("\n3. 重新应用homework迁移...")
    out = io.StringIO()
    try:
        call_command("migrate", "homework", stdout=out, verbosity=1)
        print(out.getvalue())
        print("✅ homework迁移重新应用完成")
    except Exception as e:
        print(f"❌ 重新应用失败: {e}")
    
    # 4. 最终检查
    print("\n4. 最终迁移状态检查...")
    out = io.StringIO()
    call_command("showmigrations", stdout=out)
    print(out.getvalue())


if __name__ == "__main__":
    main()
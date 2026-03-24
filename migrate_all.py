"""
应用所有迁移脚本。
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
    
    print("=" * 60)
    print("Django 迁移管理")
    print("=" * 60)
    
    # 1. 检查迁移状态
    print("\n1. 检查迁移状态...")
    out = io.StringIO()
    call_command("showmigrations", stdout=out)
    migrations_output = out.getvalue()
    print(migrations_output)
    
    # 2. 应用所有迁移
    print("\n2. 应用所有迁移...")
    out = io.StringIO()
    try:
        call_command("migrate", stdout=out, verbosity=1)
        print(out.getvalue())
        print("✅ 所有迁移应用完成")
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        
        # 尝试逐个应用迁移
        print("\n3. 尝试逐个应用迁移...")
        
        # 先应用auth相关迁移
        auth_apps = ["admin", "auth", "contenttypes", "sessions"]
        for app in auth_apps:
            try:
                print(f"\n🔍 应用 {app} 迁移...")
                out = io.StringIO()
                call_command("migrate", app, stdout=out, verbosity=0)
                print(f"✅ {app} 迁移完成")
            except Exception as app_error:
                print(f"⚠️ {app} 迁移失败: {app_error}")
        
        # 应用accounts迁移
        try:
            print(f"\n🔍 应用 accounts 迁移...")
            out = io.StringIO()
            call_command("migrate", "apps.accounts", stdout=out, verbosity=0)
            print(f"✅ accounts 迁移完成")
        except Exception as app_error:
            print(f"⚠️ accounts 迁移失败: {app_error}")
            
            # 尝试创建accounts迁移
            print(f"\n🔍 创建 accounts 迁移...")
            out = io.StringIO()
            call_command("makemigrations", "accounts", stdout=out, verbosity=0)
            print(f"✅ accounts 迁移创建完成")
            print(out.getvalue())
            
            # 再次尝试应用
            out = io.StringIO()
            call_command("migrate", "apps.accounts", stdout=out, verbosity=0)
            print(f"✅ accounts 迁移应用完成")
    
    # 3. 最终检查
    print("\n" + "=" * 60)
    print("最终迁移状态检查")
    print("=" * 60)
    
    out = io.StringIO()
    call_command("showmigrations", stdout=out)
    final_status = out.getvalue()
    
    # 统计已应用和未应用的迁移
    lines = final_status.split('\n')
    applied = 0
    not_applied = 0
    
    for line in lines:
        if '[ ]' in line:
            not_applied += 1
        elif '[X]' in line:
            applied += 1
    
    print(f"\n📊 迁移统计:")
    print(f"   已应用: {applied}")
    print(f"   未应用: {not_applied}")
    print(f"   总计: {applied + not_applied}")
    
    if not_applied == 0:
        print("\n🎉 所有迁移已成功应用！")
    else:
        print(f"\n⚠️ 还有 {not_applied} 个迁移未应用")
        print("\n未应用的迁移:")
        for line in lines:
            if '[ ]' in line:
                print(f"  {line}")


if __name__ == "__main__":
    main()
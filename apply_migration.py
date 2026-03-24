"""
应用迁移脚本。
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
    
    # 应用迁移
    from django.core.management import call_command
    import io
    
    print("🔍 应用迁移...")
    
    out = io.StringIO()
    try:
        # 先检查迁移状态
        call_command("migrate", "homework", "0001", stdout=out, verbosity=1)
        print(out.getvalue())
        print("✅ 迁移应用完成")
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        
        # 尝试创建数据库表
        print("\n🔍 尝试直接创建表...")
        from django.db import connection
        from django.db.backends.base.schema import BaseDatabaseSchemaEditor
        
        with connection.schema_editor() as schema_editor:
            # 这里应该创建表，但需要模型元数据
            print("需要模型元数据来创建表")
        
        # 或者尝试使用原始SQL
        print("\n🔍 使用原始SQL创建表...")
        sql = '''
        CREATE TABLE IF NOT EXISTS homework_homework_test (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            created_at DATETIME NOT NULL
        )
        '''
        with connection.cursor() as cursor:
            cursor.execute(sql)
            print("✅ 测试表创建成功")


if __name__ == "__main__":
    main()
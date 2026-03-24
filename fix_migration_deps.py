#!/usr/bin/env python
"""
修复迁移依赖问题。
"""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.simple")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

print("检查迁移依赖问题...")
print("=" * 50)

# 1. 检查已应用的迁移
print("1. 已应用的迁移:")
print("-" * 30)

try:
    recorder = MigrationRecorder(connection)
    applied = recorder.applied_migrations()
    
    print(f"总迁移数: {len(applied)}")
    
    # 按应用分组
    by_app = {}
    for migration in applied:
        app = migration[0]
        if app not in by_app:
            by_app[app] = []
        by_app[app].append(migration[1])
    
    for app in sorted(by_app.keys()):
        migrations = sorted(by_app[app])
        print(f"  {app}: {len(migrations)}个迁移")
        for mig in migrations[:3]:  # 只显示前3个
            print(f"    - {mig}")
        if len(migrations) > 3:
            print(f"    - ... 还有{len(migrations)-3}个")
    
except Exception as e:
    print(f"❌ 检查迁移失败: {e}")

print()

# 2. 检查数据库表
print("2. 数据库表状态:")
print("-" * 30)

try:
    with connection.cursor() as cursor:
        # 检查django_migrations表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"总表数: {len(tables)}")
        
        # 检查关键表
        key_tables = [
            'django_migrations',
            'accounts_user',
            'exercise_exerciserecord',
            'tasks_task',
            'achievements_achievement',
            'homework_homework',
        ]
        
        for table in key_tables:
            cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table}'")
            exists = cursor.fetchone()[0] > 0
            status = "✅ 存在" if exists else "❌ 缺失"
            print(f"  {table}: {status}")
        
except Exception as e:
    print(f"❌ 检查数据库失败: {e}")

print()

# 3. 尝试修复迁移
print("3. 尝试修复迁移:")
print("-" * 30)

try:
    # 检查homework模块的迁移依赖
    from django.db.migrations.loader import MigrationLoader
    
    loader = MigrationLoader(connection)
    
    # 检查homework的迁移
    homework_migrations = loader.graph.nodes.get(('homework', '0001_initial'), None)
    if homework_migrations:
        print(f"✅ homework迁移找到")
        print(f"   依赖: {homework_migrations.dependencies}")
        print(f"   操作: {len(homework_migrations.operations)}个操作")
    else:
        print(f"❌ homework迁移未找到")
    
    # 检查accounts的迁移
    accounts_migrations = loader.graph.nodes.get(('accounts', '0001_initial'), None)
    if accounts_migrations:
        print(f"✅ accounts迁移找到")
        print(f"   应用状态: {('accounts', '0001_initial') in applied}")
    else:
        print(f"❌ accounts迁移未找到")
    
except Exception as e:
    print(f"❌ 检查迁移依赖失败: {e}")

print()

# 4. 修复方案
print("4. 修复方案:")
print("-" * 30)

print("方案1: 手动标记迁移为已应用")
print("  python manage_simple.py migrate --fake homework")
print("  python manage_simple.py migrate --fake accounts")
print()

print("方案2: 重置迁移并重新生成")
print("  1. 删除所有迁移文件")
print("  2. 重新生成迁移")
print("  3. 重新应用迁移")
print()

print("方案3: 手动修复依赖关系")
print("  1. 修改homework迁移文件的依赖")
print("  2. 重新应用迁移")
print()

print("建议: 先尝试方案1，如果不行再尝试方案3")

print()

# 5. 执行修复（方案1）
print("5. 执行修复（方案1）:")
print("-" * 30)

choice = input("是否执行方案1修复？(y/n): ").strip().lower()

if choice == 'y':
    try:
        print("执行迁移修复...")
        
        # 先确保accounts迁移已应用
        from django.core.management import call_command
        
        print("1. 标记accounts迁移为已应用...")
        call_command('migrate', 'accounts', '--fake')
        
        print("2. 标记homework迁移为已应用...")
        call_command('migrate', 'homework', '--fake')
        
        print("3. 应用其他迁移...")
        call_command('migrate', '--fake')
        
        print("✅ 迁移修复完成")
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
else:
    print("跳过修复，手动执行方案。")

print()

# 6. 验证修复
print("6. 验证修复:")
print("-" * 30)

try:
    # 检查迁移状态
    recorder = MigrationRecorder(connection)
    applied = recorder.applied_migrations()
    
    homework_applied = ('homework', '0001_initial') in applied
    accounts_applied = ('accounts', '0001_initial') in applied
    
    print(f"homework迁移应用状态: {'✅ 已应用' if homework_applied else '❌ 未应用'}")
    print(f"accounts迁移应用状态: {'✅ 已应用' if accounts_applied else '❌ 未应用'}")
    
    if homework_applied and accounts_applied:
        print("✅ 迁移依赖问题已解决")
    else:
        print("❌ 迁移依赖问题仍需处理")
        
except Exception as e:
    print(f"❌ 验证失败: {e}")

print()
print("=" * 50)
print("迁移依赖问题诊断完成")
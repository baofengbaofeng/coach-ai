"""
创建简化的accounts迁移。
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
    
    print("🔍 创建accounts迁移...")
    
    # 生成迁移
    out = io.StringIO()
    try:
        call_command("makemigrations", "accounts", stdout=out, verbosity=1)
        print("✅ accounts迁移创建成功")
        print(out.getvalue())
    except Exception as e:
        print(f"❌ 创建迁移失败: {e}")
        
        # 检查accounts模型
        print("\n🔍 检查accounts模型...")
        try:
            from apps.accounts.models import User
            print(f"✅ User模型存在")
            print(f"   字段数量: {len(User._meta.get_fields())}")
            
            # 尝试手动创建迁移
            print("\n🔍 尝试手动创建迁移...")
            # 创建简单的迁移文件
            migration_content = '''"""
初始迁移文件，创建用户表。
"""
from django.db import migrations, models
import django.contrib.auth.models
import django.utils.timezone


class Migration(migrations.Migration):
    """初始迁移类。"""
    
    initial = True
    
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]
    
    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('student', 'Student'), ('parent', 'Parent'), ('teacher', 'Teacher'), ('admin', 'Admin')], default='student', max_length=20)),
                ('phone_number', models.CharField(blank=True, max_length=20)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
'''
            
            migration_file = BASE_DIR / "apps" / "accounts" / "migrations" / "0001_initial.py"
            with open(migration_file, 'w') as f:
                f.write(migration_content)
            
            print(f"✅ 手动创建迁移文件: {migration_file}")
            
        except Exception as model_error:
            print(f"❌ 检查模型失败: {model_error}")


if __name__ == "__main__":
    main()
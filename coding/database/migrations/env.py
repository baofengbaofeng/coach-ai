"""
Alembic环境配置文件
用于数据库迁移
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入配置和模型
from config import config as app_config
from webapp.modules.auth.models import User, Permission, Role, UserRole, RolePermission
from webapp.modules.tenant.models import Tenant, TenantMember

# Alembic配置对象
config = context.config

# 设置日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置目标元数据
target_metadata = None

# 动态导入所有模型
def import_all_models():
    """导入所有模型以确保元数据完整"""
    # 这里导入所有模型模块
    from webapp.modules.auth import models as auth_models
    from webapp.modules.tenant import models as tenant_models
    
    # 返回合并的元数据
    from sqlalchemy import MetaData
    metadata = MetaData()
    
    # 反射所有模型
    for model in [User, Permission, Role, UserRole, RolePermission, Tenant, TenantMember]:
        model.metadata.create_all = lambda *args, **kwargs: None  # 禁用自动创建
        metadata._add_table(model.__table__.name, model.__table__)
    
    return metadata

target_metadata = import_all_models()

def get_url():
    """获取数据库URL"""
    return app_config.DATABASE_URL

def run_migrations_offline() -> None:
    """在离线模式下运行迁移"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在在线模式下运行迁移"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
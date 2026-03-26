#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表结构和初始数据
"""

import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.migrations import create_tables, check_tables
from database.connection import get_db_session, engine
from database.models import Base, User, Tenant, TenantMember, Permission, Role, RolePermission, UserRole
from tornado.utils.password_utils import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """
    初始化数据库
    """
    logger.info("Starting database initialization...")
    
    # 检查数据库连接
    try:
        with engine.connect() as conn:
            logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return False
    
    # 创建表
    logger.info("Creating database tables...")
    if not create_tables():
        logger.error("Failed to create tables")
        return False
    
    # 检查表
    logger.info("Checking database tables...")
    success, missing = check_tables()
    if not success:
        logger.error(f"Table check failed: {missing}")
        return False
    
    logger.info("Database initialization completed successfully")
    return True


def create_initial_data():
    """
    创建初始数据
    """
    logger.info("Creating initial data...")
    
    try:
        session = get_db_session()
        
        # 创建系统管理员用户
        admin_user = session.query(User).filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@coachai.com',
                password_hash=hash_password('Admin@123'),
                display_name='系统管理员',
                status='active',
                email_verified=True,
                phone_verified=False
            )
            session.add(admin_user)
            session.commit()
            logger.info("Admin user created")
        else:
            logger.info("Admin user already exists")
        
        # 创建系统租户
        system_tenant = session.query(Tenant).filter_by(code='system').first()
        if not system_tenant:
            system_tenant = Tenant(
                name='系统租户',
                code='system',
                description='系统管理租户',
                type='organization',
                owner_id=admin_user.id,
                status='active',
                max_members=100,
                storage_limit_mb=10240,
                subscription_plan='enterprise'
            )
            session.add(system_tenant)
            session.commit()
            logger.info("System tenant created")
        else:
            logger.info("System tenant already exists")
        
        # 将管理员添加到系统租户
        admin_member = session.query(TenantMember).filter_by(
            tenant_id=system_tenant.id,
            user_id=admin_user.id
        ).first()
        
        if not admin_member:
            admin_member = TenantMember(
                tenant_id=system_tenant.id,
                user_id=admin_user.id,
                role='owner',
                status='active',
                joined_at=datetime.utcnow()
            )
            session.add(admin_member)
            session.commit()
            logger.info("Admin added to system tenant")
        
        # 创建系统权限
        system_permissions = [
            {
                'code': 'user:create',
                'name': '创建用户',
                'description': '创建新用户',
                'category': 'user',
                'scope': 'system'
            },
            {
                'code': 'user:read',
                'name': '查看用户',
                'description': '查看用户信息',
                'category': 'user',
                'scope': 'system'
            },
            {
                'code': 'user:update',
                'name': '更新用户',
                'description': '更新用户信息',
                'category': 'user',
                'scope': 'system'
            },
            {
                'code': 'user:delete',
                'name': '删除用户',
                'description': '删除用户',
                'category': 'user',
                'scope': 'system'
            },
            {
                'code': 'tenant:create',
                'name': '创建租户',
                'description': '创建新租户',
                'category': 'tenant',
                'scope': 'system'
            },
            {
                'code': 'tenant:read',
                'name': '查看租户',
                'description': '查看租户信息',
                'category': 'tenant',
                'scope': 'system'
            },
            {
                'code': 'tenant:update',
                'name': '更新租户',
                'description': '更新租户信息',
                'category': 'tenant',
                'scope': 'system'
            },
            {
                'code': 'tenant:delete',
                'name': '删除租户',
                'description': '删除租户',
                'category': 'tenant',
                'scope': 'system'
            },
        ]
        
        for perm_data in system_permissions:
            permission = session.query(Permission).filter_by(code=perm_data['code']).first()
            if not permission:
                permission = Permission(**perm_data)
                session.add(permission)
        
        session.commit()
        logger.info("System permissions created")
        
        # 创建系统角色
        system_roles = [
            {
                'code': 'super_admin',
                'name': '超级管理员',
                'description': '系统超级管理员，拥有所有权限',
                'type': 'system',
                'level': 100,
                'is_system': True,
                'is_default': False
            },
            {
                'code': 'tenant_owner',
                'name': '租户所有者',
                'description': '租户所有者，拥有租户内所有权限',
                'type': 'tenant',
                'level': 90,
                'is_system': True,
                'is_default': False
            },
            {
                'code': 'tenant_admin',
                'name': '租户管理员',
                'description': '租户管理员，可以管理租户成员',
                'type': 'tenant',
                'level': 80,
                'is_system': True,
                'is_default': False
            },
            {
                'code': 'tenant_member',
                'name': '租户成员',
                'description': '普通租户成员',
                'type': 'tenant',
                'level': 50,
                'is_system': True,
                'is_default': True
            },
            {
                'code': 'tenant_guest',
                'name': '租户访客',
                'description': '租户访客，只读权限',
                'type': 'tenant',
                'level': 10,
                'is_system': True,
                'is_default': False
            },
        ]
        
        for role_data in system_roles:
            role = session.query(Role).filter_by(code=role_data['code']).first()
            if not role:
                role = Role(**role_data)
                session.add(role)
        
        session.commit()
        logger.info("System roles created")
        
        # 将超级管理员角色分配给管理员用户
        super_admin_role = session.query(Role).filter_by(code='super_admin').first()
        if super_admin_role:
            user_role = session.query(UserRole).filter_by(
                user_id=admin_user.id,
                role_id=super_admin_role.id
            ).first()
            
            if not user_role:
                user_role = UserRole(
                    user_id=admin_user.id,
                    role_id=super_admin_role.id,
                    is_default=True
                )
                session.add(user_role)
                session.commit()
                logger.info("Super admin role assigned to admin user")
        
        logger.info("Initial data creation completed")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create initial data: {e}")
        session.rollback()
        return False
    finally:
        session.close()


if __name__ == "__main__":
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description="数据库初始化工具")
    parser.add_argument("--init", action="store_true", help="初始化数据库表结构")
    parser.add_argument("--seed", action="store_true", help="创建初始数据")
    parser.add_argument("--all", action="store_true", help="执行所有初始化操作")
    
    args = parser.parse_args()
    
    if args.all or args.init:
        if not init_database():
            sys.exit(1)
    
    if args.all or args.seed:
        if not create_initial_data():
            sys.exit(1)
    
    if not any([args.init, args.seed, args.all]):
        parser.print_help()
"""
数据库初始数据种子脚本
插入系统必需的初始数据
"""

import sys
from pathlib import Path
from loguru import logger

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from database.connection import get_db_session
from tornado.modules.auth.models import (
    User, Permission, Role, UserRole, RolePermission
)
from tornado.modules.tenant.models import Tenant, TenantMember
from tornado.utils.password_utils import hash_password


def create_system_permissions() -> list[Permission]:
    """创建系统权限
    
    Returns:
        list[Permission]: 创建的权限列表
    """
    permissions_data = [
        # 用户管理权限
        {"name": "查看用户", "code": "user:read", "module": "user", "description": "查看用户信息"},
        {"name": "创建用户", "code": "user:create", "module": "user", "description": "创建新用户"},
        {"name": "更新用户", "code": "user:update", "module": "user", "description": "更新用户信息"},
        {"name": "删除用户", "code": "user:delete", "module": "user", "description": "删除用户"},
        {"name": "管理用户角色", "code": "user:manage_roles", "module": "user", "description": "管理用户角色分配"},
        
        # 租户管理权限
        {"name": "查看租户", "code": "tenant:read", "module": "tenant", "description": "查看租户信息"},
        {"name": "创建租户", "code": "tenant:create", "module": "tenant", "description": "创建新租户"},
        {"name": "更新租户", "code": "tenant:update", "module": "tenant", "description": "更新租户信息"},
        {"name": "删除租户", "code": "tenant:delete", "module": "tenant", "description": "删除租户"},
        {"name": "管理租户成员", "code": "tenant:manage_members", "module": "tenant", "description": "管理租户成员"},
        
        # 角色管理权限
        {"name": "查看角色", "code": "role:read", "module": "role", "description": "查看角色信息"},
        {"name": "创建角色", "code": "role:create", "module": "role", "description": "创建新角色"},
        {"name": "更新角色", "code": "role:update", "module": "role", "description": "更新角色信息"},
        {"name": "删除角色", "code": "role:delete", "module": "role", "description": "删除角色"},
        {"name": "管理角色权限", "code": "role:manage_permissions", "module": "role", "description": "管理角色权限分配"},
        
        # 权限管理权限
        {"name": "查看权限", "code": "permission:read", "module": "permission", "description": "查看权限信息"},
        {"name": "创建权限", "code": "permission:create", "module": "permission", "description": "创建新权限"},
        {"name": "更新权限", "code": "permission:update", "module": "permission", "description": "更新权限信息"},
        {"name": "删除权限", "code": "permission:delete", "module": "permission", "description": "删除权限"},
        
        # 教练模块权限
        {"name": "查看教练", "code": "coach:read", "module": "coach", "description": "查看教练信息"},
        {"name": "创建教练", "code": "coach:create", "module": "coach", "description": "创建新教练"},
        {"name": "更新教练", "code": "coach:update", "module": "coach", "description": "更新教练信息"},
        {"name": "删除教练", "code": "coach:delete", "module": "coach", "description": "删除教练"},
        
        # 学员模块权限
        {"name": "查看学员", "code": "student:read", "module": "student", "description": "查看学员信息"},
        {"name": "创建学员", "code": "student:create", "module": "student", "description": "创建新学员"},
        {"name": "更新学员", "code": "student:update", "module": "student", "description": "更新学员信息"},
        {"name": "删除学员", "code": "student:delete", "module": "student", "description": "删除学员"},
        
        # 课程模块权限
        {"name": "查看课程", "code": "course:read", "module": "course", "description": "查看课程信息"},
        {"name": "创建课程", "code": "course:create", "module": "course", "description": "创建新课程"},
        {"name": "更新课程", "code": "course:update", "module": "course", "description": "更新课程信息"},
        {"name": "删除课程", "code": "course:delete", "module": "course", "description": "删除课程"},
        
        # 系统管理权限
        {"name": "系统设置", "code": "system:settings", "module": "system", "description": "管理系统设置"},
        {"name": "查看日志", "code": "system:logs", "module": "system", "description": "查看系统日志"},
        {"name": "备份恢复", "code": "system:backup", "module": "system", "description": "系统备份和恢复"},
    ]
    
    permissions = []
    with get_db_session() as session:
        for perm_data in permissions_data:
            # 检查权限是否已存在
            existing = session.query(Permission).filter_by(code=perm_data["code"]).first()
            if existing:
                logger.info(f"Permission {perm_data['code']} already exists, skipping")
                permissions.append(existing)
                continue
            
            permission = Permission(**perm_data)
            session.add(permission)
            permissions.append(permission)
            logger.info(f"Created permission: {perm_data['code']}")
        
        session.commit()
    
    return permissions


def create_system_roles() -> list[Role]:
    """创建系统角色
    
    Returns:
        list[Role]: 创建的角色列表
    """
    roles_data = [
        {
            "name": "超级管理员",
            "code": "super_admin",
            "description": "系统超级管理员，拥有所有权限",
            "is_system": True
        },
        {
            "name": "租户管理员",
            "code": "tenant_admin",
            "description": "租户管理员，管理租户内所有资源",
            "is_system": True
        },
        {
            "name": "教练",
            "code": "coach",
            "description": "教练角色，可以管理学员和课程",
            "is_system": True
        },
        {
            "name": "学员",
            "code": "student",
            "description": "学员角色，可以查看和参与课程",
            "is_system": True
        },
        {
            "name": "访客",
            "code": "guest",
            "description": "访客角色，只有基本查看权限",
            "is_system": True
        },
    ]
    
    roles = []
    with get_db_session() as session:
        for role_data in roles_data:
            # 检查角色是否已存在
            existing = session.query(Role).filter_by(code=role_data["code"]).first()
            if existing:
                logger.info(f"Role {role_data['code']} already exists, skipping")
                roles.append(existing)
                continue
            
            role = Role(**role_data)
            session.add(role)
            roles.append(role)
            logger.info(f"Created role: {role_data['code']}")
        
        session.commit()
    
    return roles


def assign_permissions_to_roles():
    """为角色分配权限"""
    with get_db_session() as session:
        # 获取所有权限
        permissions = session.query(Permission).all()
        permission_map = {perm.code: perm for perm in permissions}
        
        # 获取所有角色
        roles = session.query(Role).all()
        role_map = {role.code: role for role in roles}
        
        # 超级管理员拥有所有权限
        super_admin = role_map.get("super_admin")
        if super_admin:
            for perm in permissions:
                # 检查是否已分配
                existing = session.query(RolePermission).filter_by(
                    role_id=super_admin.id,
                    permission_id=perm.id
                ).first()
                
                if not existing:
                    role_perm = RolePermission(role_id=super_admin.id, permission_id=perm.id)
                    session.add(role_perm)
                    logger.info(f"Assigned permission {perm.code} to super_admin")
        
        # 租户管理员权限
        tenant_admin = role_map.get("tenant_admin")
        if tenant_admin:
            tenant_permissions = [
                "tenant:read", "tenant:update", "tenant:manage_members",
                "user:read", "user:create", "user:update", "user:delete", "user:manage_roles",
                "role:read", "role:create", "role:update", "role:delete", "role:manage_permissions",
                "coach:read", "coach:create", "coach:update", "coach:delete",
                "student:read", "student:create", "student:update", "student:delete",
                "course:read", "course:create", "course:update", "course:delete",
            ]
            
            for perm_code in tenant_permissions:
                perm = permission_map.get(perm_code)
                if perm:
                    existing = session.query(RolePermission).filter_by(
                        role_id=tenant_admin.id,
                        permission_id=perm.id
                    ).first()
                    
                    if not existing:
                        role_perm = RolePermission(role_id=tenant_admin.id, permission_id=perm.id)
                        session.add(role_perm)
                        logger.info(f"Assigned permission {perm_code} to tenant_admin")
        
        # 教练权限
        coach = role_map.get("coach")
        if coach:
            coach_permissions = [
                "student:read", "student:create", "student:update",
                "course:read", "course:create", "course:update",
            ]
            
            for perm_code in coach_permissions:
                perm = permission_map.get(perm_code)
                if perm:
                    existing = session.query(RolePermission).filter_by(
                        role_id=coach.id,
                        permission_id=perm.id
                    ).first()
                    
                    if not existing:
                        role_perm = RolePermission(role_id=coach.id, permission_id=perm.id)
                        session.add(role_perm)
                        logger.info(f"Assigned permission {perm_code} to coach")
        
        # 学员权限
        student = role_map.get("student")
        if student:
            student_permissions = [
                "course:read",
            ]
            
            for perm_code in student_permissions:
                perm = permission_map.get(perm_code)
                if perm:
                    existing = session.query(RolePermission).filter_by(
                        role_id=student.id,
                        permission_id=perm.id
                    ).first()
                    
                    if not existing:
                        role_perm = RolePermission(role_id=student.id, permission_id=perm.id)
                        session.add(role_perm)
                        logger.info(f"Assigned permission {perm_code} to student")
        
        session.commit()


def create_superuser() -> User:
    """创建超级用户
    
    Returns:
        User: 创建的超级用户
    """
    with get_db_session() as session:
        # 检查超级用户是否已存在
        existing = session.query(User).filter_by(email="admin@coach-ai.com").first()
        if existing:
            logger.info("Superuser already exists")
            return existing
        
        # 创建超级用户
        superuser = User(
            username="admin",
            email="admin@coach-ai.com",
            password_hash=hash_password("Admin@123"),
            full_name="系统管理员",
            is_active=True,
            is_superuser=True
        )
        
        session.add(superuser)
        session.commit()
        session.refresh(superuser)
        
        logger.info(f"Created superuser: {superuser.username} ({superuser.email})")
        
        return superuser


def assign_superuser_role(superuser: User):
    """为超级用户分配角色"""
    with get_db_session() as session:
        # 获取超级管理员角色
        super_admin_role = session.query(Role).filter_by(code="super_admin").first()
        if not super_admin_role:
            logger.error("Super admin role not found")
            return
        
        # 检查是否已分配
        existing = session.query(UserRole).filter_by(
            user_id=superuser.id,
            role_id=super_admin_role.id
        ).first()
        
        if not existing:
            user_role = UserRole(user_id=superuser.id, role_id=super_admin_role.id)
            session.add(user_role)
            session.commit()
            logger.info(f"Assigned super_admin role to user {superuser.username}")


def create_default_tenant(superuser: User) -> Tenant:
    """创建默认租户
    
    Args:
        superuser: 超级用户
        
    Returns:
        Tenant: 创建的租户
    """
    with get_db_session() as session:
        # 检查默认租户是否已存在
        existing = session.query(Tenant).filter_by(slug="default").first()
        if existing:
            logger.info("Default tenant already exists")
            return existing
        
        # 创建默认租户
        tenant = Tenant(
            name="默认租户",
            slug="default",
            description="系统默认租户",
            contact_email="contact@coach-ai.com",
            created_by=superuser.id
        )
        
        session.add(tenant)
        session.commit()
        session.refresh(tenant)
        
        logger.info(f"Created default tenant: {tenant.name} ({tenant.slug})")
        
        # 将超级用户添加到租户
        # 获取租户管理员角色
        tenant_admin_role = session.query(Role).filter_by(code="tenant_admin").first()
        if tenant_admin_role:
            tenant_member = TenantMember(
                tenant_id=tenant.id,
                user_id=superuser.id,
                role_id=tenant_admin_role.id
            )
            session.add(tenant_member)
            session.commit()
            logger.info(f"Added superuser as admin to tenant {tenant.name}")
        
        return tenant


def create_test_users():
    """创建测试用户"""
    test_users = [
        {
            "username": "coach1",
            "email": "coach1@coach-ai.com",
            "password": "Coach@123",
            "full_name": "测试教练一",
            "role": "coach"
        },
        {
            "username": "student1",
            "email": "student1@coach-ai.com",
            "password": "Student@123",
            "full_name": "测试学员一",
            "role": "student"
        },
        {
            "username": "guest1",
            "email": "guest1@coach-ai.com",
            "password": "Guest@123",
            "full_name": "测试访客一",
            "role": "guest"
        },
    ]
    
    with get_db_session() as session:
        # 获取默认租户
        default_tenant = session.query(Tenant).filter_by(slug="default").first()
        if not default_tenant:
            logger.error("Default tenant not found")
            return
        
        for user_data in test_users:
            # 检查用户是否已存在
            existing = session.query(User).filter_by(email=user_data["email"]).first()
            if existing:
                logger.info(f"Test user {user_data['username']} already exists, skipping")
                continue
            
            # 创建用户
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                is_active=True
            )
            
            session.add(user)
            session.commit()
            session.refresh(user)
            
            logger.info(f"Created test user: {user_data['username']}")
            
            # 获取角色
            role = session.query(Role).filter_by(code=user_data["role"]).first()
            if role:
                # 分配用户角色
                user_role = UserRole(user_id=user.id, role_id=role.id)
                session.add(user_role)
                
                # 添加到默认租户
                tenant_member = TenantMember(
                    tenant_id=default_tenant.id,
                    user_id=user.id,
                    role_id=role.id
                )
                session.add(tenant_member)
                
                session.commit()
                logger.info(f"Assigned role {user_data['role']} to user {user_data['username']} and added to default tenant")


def run_seeds() -> bool:
    """运行所有种子脚本
    
    Returns:
        bool: 是否成功
    """
    try:
        logger.info("Starting database seeding...")
        
        # 创建系统权限
        logger.info("Creating system permissions...")
        create_system_permissions()
        
        # 创建系统角色
        logger.info("Creating system roles...")
        create_system_roles()
        
        # 为角色分配权限
        logger.info("Assigning permissions to roles...")
        assign_permissions_to_roles()
        
        # 创建超级用户
        logger.info("Creating superuser...")
        superuser = create_superuser()
        
        # 为超级用户分配角色
        logger.info("Assigning role to superuser...")
        assign_superuser_role(superuser)
        
        # 创建默认租户
        logger.info("Creating default tenant...")
        tenant = create_default_tenant(superuser)
        
        # 创建测试用户
        logger.info("Creating test users...")
        create_test_users()
        
        logger.info("Database seeding completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database seeding failed: {e}")
        return False


if __name__ == "__main__":
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Seed Script")
    parser.add_argument("--skip-users", action="store_true", help="Skip creating test users")
    parser.add_argument("--skip-tenant", action="store_true", help="Skip creating default tenant")
    
    args = parser.parse_args()
    
    # 这里可以添加条件逻辑，但为了简单起见，我们总是运行所有种子
    success = run_seeds()
    
    if success:
        print("Database seeding completed successfully")
        sys.exit(0)
    else:
        print("Database seeding failed")
        sys.exit(1)
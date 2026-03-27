"""
用户领域仓库实现
将DDD实体映射到数据库
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger

from domain.user.entities import User, Tenant, Permission
from domain.user.value_objects import Email, Password, PhoneNumber, UserStatus, VerificationStatus
from .base import Repository


class UserRepository(Repository[User]):
    """用户仓库"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager, "users")
    
    def _entity_to_dict(self, user: User) -> Dict[str, Any]:
        """将用户实体转换为字典"""
        return {
            'id': user.id,
            'username': user.username,
            'email': str(user.email),
            'phone': str(user.phone) if user.phone else None,
            'password_hash': user.password.hashed_value,
            'display_name': user.display_name,
            'avatar_url': user.avatar_url,
            'status': str(user.status),
            'email_verified': user.verification.email_verified,
            'phone_verified': user.verification.phone_verified,
            'last_login_at': user.last_login_at,
            'last_login_ip': user.last_login_ip,
            'failed_login_attempts': user.failed_login_attempts,
            'locked_until': user.locked_until,
            'mfa_enabled': user.mfa_enabled,
            'mfa_secret': user.mfa_secret,
            'tenant_ids': ','.join(user.tenant_ids) if user.tenant_ids else '',
            'owned_tenant_ids': ','.join(user.owned_tenant_ids) if user.owned_tenant_ids else '',
            'created_at': user.created_at,
            'updated_at': user.updated_at,
            'version': user.version,
        }
    
    def _dict_to_entity(self, data: Dict[str, Any]) -> User:
        """将字典转换为用户实体"""
        try:
            # 创建值对象
            email = Email(data['email'])
            
            # 处理密码
            password = Password(hashed_value=data['password_hash'])
            
            # 处理手机号
            phone = None
            if data.get('phone'):
                try:
                    # 解析手机号格式
                    if data['phone'].startswith('+'):
                        # 格式: +8613812345678
                        country_code = data['phone'][:3]
                        number = data['phone'][3:]
                        phone = PhoneNumber(value=number, country_code=country_code)
                    else:
                        # 格式: 13812345678
                        phone = PhoneNumber(value=data['phone'])
                except ValueError:
                    logger.warning(f"无效的手机号格式: {data.get('phone')}")
            
            # 处理状态
            status = UserStatus(data.get('status', 'pending'))
            
            # 处理验证状态
            verification = VerificationStatus(
                email_verified=bool(data.get('email_verified', False)),
                phone_verified=bool(data.get('phone_verified', False)),
                verified_at=data.get('verified_at')
            )
            
            # 处理租户ID列表
            tenant_ids = set()
            if data.get('tenant_ids'):
                tenant_ids = set(data['tenant_ids'].split(',')) if data['tenant_ids'] else set()
            
            owned_tenant_ids = set()
            if data.get('owned_tenant_ids'):
                owned_tenant_ids = set(data['owned_tenant_ids'].split(',')) if data['owned_tenant_ids'] else set()
            
            # 创建用户实体
            user = User(
                id=data['id'],
                username=data['username'],
                email=email,
                password=password,
                phone=phone,
                display_name=data.get('display_name'),
                avatar_url=data.get('avatar_url'),
                status=status,
                verification=verification,
                last_login_at=data.get('last_login_at'),
                last_login_ip=data.get('last_login_ip'),
                failed_login_attempts=data.get('failed_login_attempts', 0),
                locked_until=data.get('locked_until'),
                mfa_enabled=bool(data.get('mfa_enabled', False)),
                mfa_secret=data.get('mfa_secret'),
                tenant_ids=tenant_ids,
                owned_tenant_ids=owned_tenant_ids,
                created_at=data['created_at'],
                updated_at=data.get('updated_at'),
                version=data.get('version', 0),
            )
            
            return user
            
        except Exception as e:
            logger.error(f"转换用户数据失败: {e}, 数据: {data}")
            raise
    
    async def find_by_username(self, username: str) -> Optional[User]:
        """根据用户名查找用户"""
        query = "SELECT * FROM users WHERE username = %s AND is_deleted = 0"
        result = await self.db_manager.execute_query(query, (username,))
        
        if result:
            return self._dict_to_entity(result[0])
        return None
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """根据邮箱查找用户"""
        query = "SELECT * FROM users WHERE email = %s AND is_deleted = 0"
        result = await self.db_manager.execute_query(query, (email,))
        
        if result:
            return self._dict_to_entity(result[0])
        return None
    
    async def find_by_phone(self, phone: str) -> Optional[User]:
        """根据手机号查找用户"""
        query = "SELECT * FROM users WHERE phone = %s AND is_deleted = 0"
        result = await self.db_manager.execute_query(query, (phone,))
        
        if result:
            return self._dict_to_entity(result[0])
        return None
    
    async def find_active_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """查找活跃用户"""
        query = """
            SELECT * FROM users 
            WHERE status = 'active' AND is_deleted = 0
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        results = await self.db_manager.execute_query(query, (limit, offset))
        
        return [self._dict_to_entity(row) for row in results]
    
    async def update_last_login(self, user_id: str, ip_address: Optional[str] = None) -> bool:
        """更新最后登录信息"""
        query = """
            UPDATE users 
            SET last_login_at = %s, last_login_ip = %s, 
                failed_login_attempts = 0, locked_until = NULL,
                updated_at = %s, version = version + 1
            WHERE id = %s
        """
        
        now = datetime.now()
        params = (now, ip_address, now, user_id)
        
        affected = await self.db_manager.execute_update(query, params)
        return affected > 0
    
    async def increment_failed_attempts(self, user_id: str) -> bool:
        """增加登录失败次数"""
        query = """
            UPDATE users 
            SET failed_login_attempts = failed_login_attempts + 1,
                updated_at = %s, version = version + 1
            WHERE id = %s
        """
        
        affected = await self.db_manager.execute_update(query, (datetime.now(), user_id))
        return affected > 0
    
    async def lock_user(self, user_id: str, lock_minutes: int = 30) -> bool:
        """锁定用户"""
        from datetime import timedelta
        
        lock_until = datetime.now() + timedelta(minutes=lock_minutes)
        
        query = """
            UPDATE users 
            SET status = 'blocked', locked_until = %s,
                updated_at = %s, version = version + 1
            WHERE id = %s
        """
        
        affected = await self.db_manager.execute_update(query, (lock_until, datetime.now(), user_id))
        return affected > 0
    
    async def unlock_user(self, user_id: str) -> bool:
        """解锁用户"""
        query = """
            UPDATE users 
            SET status = 'active', locked_until = NULL,
                failed_login_attempts = 0,
                updated_at = %s, version = version + 1
            WHERE id = %s
        """
        
        affected = await self.db_manager.execute_update(query, (datetime.now(), user_id))
        return affected > 0


class TenantRepository(Repository[Tenant]):
    """租户仓库"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager, "tenants")
    
    def _entity_to_dict(self, tenant: Tenant) -> Dict[str, Any]:
        """将租户实体转换为字典"""
        return {
            'id': tenant.id,
            'name': tenant.name,
            'description': tenant.description,
            'owner_id': tenant.owner_id,
            'type': tenant.type,
            'status': tenant.status,
            'settings': str(tenant.settings) if tenant.settings else '{}',
            'member_ids': ','.join(tenant.member_ids) if tenant.member_ids else '',
            'created_at': tenant.created_at,
            'updated_at': tenant.updated_at,
            'version': tenant.version,
        }
    
    def _dict_to_entity(self, data: Dict[str, Any]) -> Tenant:
        """将字典转换为租户实体"""
        try:
            # 处理设置
            import json
            settings = {}
            if data.get('settings'):
                try:
                    settings = json.loads(data['settings'])
                except json.JSONDecodeError:
                    logger.warning(f"无效的租户设置JSON: {data.get('settings')}")
            
            # 处理成员ID列表
            member_ids = set()
            if data.get('member_ids'):
                member_ids = set(data['member_ids'].split(',')) if data['member_ids'] else set()
            
            # 创建租户实体
            tenant = Tenant(
                id=data['id'],
                name=data['name'],
                description=data.get('description'),
                owner_id=data['owner_id'],
                type=data.get('type', 'family'),
                status=data.get('status', 'active'),
                settings=settings,
                member_ids=member_ids,
                created_at=data['created_at'],
                updated_at=data.get('updated_at'),
                version=data.get('version', 0),
            )
            
            return tenant
            
        except Exception as e:
            logger.error(f"转换租户数据失败: {e}, 数据: {data}")
            raise
    
    async def find_by_owner(self, owner_id: str) -> List[Tenant]:
        """根据拥有者查找租户"""
        query = "SELECT * FROM tenants WHERE owner_id = %s AND is_deleted = 0 ORDER BY created_at DESC"
        results = await self.db_manager.execute_query(query, (owner_id,))
        
        return [self._dict_to_entity(row) for row in results]
    
    async def find_by_member(self, user_id: str) -> List[Tenant]:
        """根据成员查找租户"""
        # 注意：这里需要查询租户成员关系表
        # 简化实现：直接查询租户表的member_ids字段
        query = "SELECT * FROM tenants WHERE is_deleted = 0"
        all_tenants = await self.db_manager.execute_query(query)
        
        user_tenants = []
        for tenant_data in all_tenants:
            tenant = self._dict_to_entity(tenant_data)
            if user_id in tenant.member_ids:
                user_tenants.append(tenant)
        
        return user_tenants
    
    async def add_member(self, tenant_id: str, user_id: str) -> bool:
        """添加成员到租户"""
        # 首先获取租户
        tenant = await self.find_by_id(tenant_id)
        if not tenant:
            return False
        
        # 更新成员列表
        if user_id not in tenant.member_ids:
            tenant.member_ids.add(user_id)
            tenant.mark_updated()
            
            # 保存更新
            return await self.save(tenant)
        
        return True
    
    async def remove_member(self, tenant_id: str, user_id: str) -> bool:
        """从租户移除成员"""
        # 首先获取租户
        tenant = await self.find_by_id(tenant_id)
        if not tenant:
            return False
        
        # 不能移除拥有者
        if user_id == tenant.owner_id:
            return False
        
        # 更新成员列表
        if user_id in tenant.member_ids:
            tenant.member_ids.remove(user_id)
            tenant.mark_updated()
            
            # 保存更新
            return await self.save(tenant)
        
        return True


class PermissionRepository(Repository[Permission]):
    """权限仓库"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager, "permissions")
    
    def _entity_to_dict(self, permission: Permission) -> Dict[str, Any]:
        """将权限实体转换为字典"""
        return {
            'id': permission.id,
            'name': permission.name,
            'description': permission.description,
            'resource': permission.resource,
            'action': permission.action,
            'created_at': permission.created_at,
        }
    
    def _dict_to_entity(self, data: Dict[str, Any]) -> Permission:
        """将字典转换为权限实体"""
        try:
            permission = Permission(
                id=data['id'],
                name=data['name'],
                description=data.get('description'),
                resource=data['resource'],
                action=data['action'],
                created_at=data['created_at'],
            )
            
            return permission
            
        except Exception as e:
            logger.error(f"转换权限数据失败: {e}, 数据: {data}")
            raise
    
    async def find_by_resource(self, resource: str) -> List[Permission]:
        """根据资源查找权限"""
        query = "SELECT * FROM permissions WHERE resource = %s ORDER BY name"
        results = await self.db_manager.execute_query(query, (resource,))
        
        return [self._dict_to_entity(row) for row in results]
    
    async def find_by_resource_action(self, resource: str, action: str) -> Optional[Permission]:
        """根据资源和操作查找权限"""
        query = "SELECT * FROM permissions WHERE resource = %s AND action = %s"
        results = await self.db_manager.execute_query(query, (resource, action))
        
        if results:
            return self._dict_to_entity(results[0])
        return None
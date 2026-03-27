"""
租户应用服务
处理租户管理相关的业务逻辑
"""

import asyncio
from typing import Dict, Any, List, Optional
from loguru import logger

from src.domain.user.services import TenantService as DomainTenantService
from src.domain.user.entities import Tenant, Permission


class TenantService:
    """租户应用服务"""
    
    def __init__(self):
        self.domain_service = DomainTenantService()
    
    async def create_tenant(
        self,
        owner_id: str,
        name: str,
        code: str,
        description: Optional[str] = None,
        tenant_type: str = "individual",
        domain: Optional[str] = None,
        logo_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """创建新租户"""
        try:
            # 验证租户代码
            validation_result = self._validate_tenant_code(code)
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'error': '; '.join(validation_result['errors'])
                }
            
            # 检查租户代码是否已存在
            code_exists = await self._check_tenant_code_exists(code)
            if code_exists:
                return {
                    'success': False,
                    'error': 'Tenant code already exists'
                }
            
            # 检查域名是否已存在
            if domain:
                domain_exists = await self._check_domain_exists(domain)
                if domain_exists:
                    return {
                        'success': False,
                        'error': 'Domain already exists'
                    }
            
            # 创建租户实体
            tenant = self.domain_service.create_tenant(
                name=name,
                code=code,
                owner_id=owner_id,
                description=description,
                tenant_type=tenant_type,
                domain=domain,
                logo_url=logo_url,
                config=config or {},
                metadata=metadata or {}
            )
            
            # 保存租户（需要持久化）
            # tenant_repository.save(tenant)
            
            # 创建所有者权限
            owner_permission = self._create_owner_permission(tenant.id, owner_id)
            # permission_repository.save(owner_permission)
            
            # 发送通知（异步）
            asyncio.create_task(self._send_tenant_created_notification(owner_id, tenant))
            
            return {
                'success': True,
                'data': {
                    'tenant': {
                        'id': tenant.id,
                        'name': tenant.name,
                        'code': tenant.code,
                        'type': tenant.tenant_type,
                        'status': str(tenant.status),
                        'owner_id': tenant.owner_id,
                        'created_at': tenant.created_at.isoformat()
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Create tenant error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_tenant(self, tenant_id: str, user_id: str) -> Dict[str, Any]:
        """获取租户信息"""
        try:
            # 检查用户是否有权限访问租户
            has_access = await self._check_user_tenant_access(user_id, tenant_id)
            if not has_access:
                return {
                    'success': False,
                    'error': 'Access denied'
                }
            
            # 查找租户
            # tenant = tenant_repository.find_by_id(tenant_id)
            # if not tenant:
            #     return {
            #         'success': False,
            #         'error': 'Tenant not found'
            #     }
            
            # 暂时返回模拟数据
            return {
                'success': True,
                'data': {
                    'tenant': {
                        'id': tenant_id,
                        'name': 'Test Tenant',
                        'code': 'test_tenant',
                        'type': 'organization',
                        'status': 'active',
                        'owner_id': user_id,
                        'member_count': 5,
                        'created_at': '2026-03-27T00:00:00Z'
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Get tenant error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def update_tenant(
        self,
        tenant_id: str,
        user_id: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新租户信息"""
        try:
            # 检查用户是否有权限更新租户
            has_permission = await self._check_tenant_update_permission(user_id, tenant_id)
            if not has_permission:
                return {
                    'success': False,
                    'error': 'Permission denied'
                }
            
            # 验证更新数据
            validation_result = self._validate_tenant_update_data(update_data)
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'error': '; '.join(validation_result['errors'])
                }
            
            # 查找租户
            # tenant = tenant_repository.find_by_id(tenant_id)
            # if not tenant:
            #     return {
            #         'success': False,
            #         'error': 'Tenant not found'
            #     }
            
            # 更新租户信息
            # if 'name' in update_data:
            #     tenant.update_name(update_data['name'])
            # if 'description' in update_data:
            #     tenant.update_description(update_data['description'])
            # if 'logo_url' in update_data:
            #     tenant.update_logo_url(update_data['logo_url'])
            # if 'config' in update_data:
            #     tenant.update_config(update_data['config'])
            
            # tenant_repository.save(tenant)
            
            return {
                'success': True,
                'data': {
                    'message': 'Tenant updated successfully'
                }
            }
            
        except Exception as e:
            logger.error(f"Update tenant error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def list_user_tenants(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """列出用户的所有租户"""
        try:
            # 计算分页
            offset = (page - 1) * limit
            
            # 查找用户租户（需要持久化支持）
            # tenants = tenant_repository.find_by_user_id(user_id, status, offset, limit)
            # total = tenant_repository.count_by_user_id(user_id, status)
            
            # 暂时返回模拟数据
            tenants = [
                {
                    'id': 'tenant_1',
                    'name': 'Personal Workspace',
                    'code': 'personal',
                    'type': 'individual',
                    'status': 'active',
                    'role': 'owner',
                    'created_at': '2026-03-27T00:00:00Z'
                },
                {
                    'id': 'tenant_2',
                    'name': 'Team Project',
                    'code': 'team_project',
                    'type': 'team',
                    'status': 'active',
                    'role': 'admin',
                    'created_at': '2026-03-27T00:00:00Z'
                }
            ]
            
            total = len(tenants)
            
            return {
                'success': True,
                'data': {
                    'tenants': tenants,
                    'total': total
                },
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
            }
            
        except Exception as e:
            logger.error(f"List user tenants error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def invite_user_to_tenant(
        self,
        tenant_id: str,
        inviter_id: str,
        email: str,
        role: str,
        permissions: List[str] = None
    ) -> Dict[str, Any]:
        """邀请用户加入租户"""
        try:
            # 检查邀请者权限
            can_invite = await self._check_invite_permission(inviter_id, tenant_id)
            if not can_invite:
                return {
                    'success': False,
                    'error': 'Permission denied'
                }
            
            # 验证角色
            valid_roles = ['owner', 'admin', 'member', 'guest']
            if role not in valid_roles:
                return {
                    'success': False,
                    'error': f'Invalid role. Valid roles: {", ".join(valid_roles)}'
                }
            
            # 查找用户（通过邮箱）
            # invited_user = user_repository.find_by_email(email)
            # if not invited_user:
            #     # 用户不存在，发送邀请邮件
            #     asyncio.create_task(self._send_tenant_invitation_email(email, tenant_id, role))
            #     return {
            #         'success': True,
            #         'data': {
            #             'message': 'Invitation sent to email',
            #             'requires_registration': True
            #         }
            #     }
            
            # 检查用户是否已经在租户中
            # already_member = permission_repository.check_user_tenant_membership(invited_user.id, tenant_id)
            # if already_member:
            #     return {
            #         'success': False,
            #         'error': 'User is already a member of this tenant'
            #     }
            
            # 创建权限记录
            # permission = self._create_tenant_permission(
            #     tenant_id=tenant_id,
            #     user_id=invited_user.id,
            #     role=role,
            #     permissions=permissions or []
            # )
            # permission_repository.save(permission)
            
            # 发送加入通知（异步）
            # asyncio.create_task(self._send_tenant_joined_notification(invited_user.id, tenant_id, role))
            
            return {
                'success': True,
                'data': {
                    'message': 'User invited successfully',
                    'requires_registration': False
                }
            }
            
        except Exception as e:
            logger.error(f"Invite user error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def remove_user_from_tenant(
        self,
        tenant_id: str,
        remover_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """从租户中移除用户"""
        try:
            # 检查移除者权限
            can_remove = await self._check_remove_permission(remover_id, tenant_id, user_id)
            if not can_remove:
                return {
                    'success': False,
                    'error': 'Permission denied'
                }
            
            # 不能移除自己（如果是最后一个所有者）
            # if remover_id == user_id:
            #     # 检查是否是最后一个所有者
            #     is_last_owner = await self._is_last_owner(tenant_id, user_id)
            #     if is_last_owner:
            #         return {
            #             'success': False,
            #             'error': 'Cannot remove the last owner from tenant'
            #         }
            
            # 移除权限
            # permission_repository.remove_user_from_tenant(user_id, tenant_id)
            
            # 发送移除通知（异步）
            # asyncio.create_task(self._send_tenant_removed_notification(user_id, tenant_id))
            
            return {
                'success': True,
                'data': {
                    'message': 'User removed successfully'
                }
            }
            
        except Exception as e:
            logger.error(f"Remove user error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # 验证方法
    def _validate_tenant_code(self, code: str) -> Dict[str, Any]:
        """验证租户代码"""
        result = {
            'is_valid': True,
            'errors': []
        }
        
        if len(code) < 3:
            result['is_valid'] = False
            result['errors'].append("Tenant code must be at least 3 characters")
        
        if len(code) > 50:
            result['is_valid'] = False
            result['errors'].append("Tenant code must be at most 50 characters")
        
        if not code.replace('_', '').replace('-', '').isalnum():
            result['is_valid'] = False
            result['errors'].append("Tenant code can only contain letters, numbers, underscores and hyphens")
        
        return result
    
    def _validate_tenant_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证租户更新数据"""
        result = {
            'is_valid': True,
            'errors': []
        }
        
        if 'name' in data and (not data['name'] or len(data['name'].strip()) < 2):
            result['is_valid'] = False
            result['errors'].append("Tenant name must be at least 2 characters")
        
        if 'code' in data:
            code_validation = self._validate_tenant_code(data['code'])
            if not code_validation['is_valid']:
                result['is_valid'] = False
                result['errors'].extend(code_validation['errors'])
        
        return result
    
    # 权限检查方法（需要持久化支持）
    async def _check_user_tenant_access(self, user_id: str, tenant_id: str) -> bool:
        """检查用户是否有权限访问租户"""
        # 需要持久化实现
        # return permission_repository.check_user_tenant_access(user_id, tenant_id)
        return True  # 暂时返回True
    
    async def _check_tenant_update_permission(self, user_id: str, tenant_id: str) -> bool:
        """检查用户是否有权限更新租户"""
        # 需要持久化实现
        # return permission_repository.check_tenant_update_permission(user_id, tenant_id)
        return True  # 暂时返回True
    
    async def _check_invite_permission(self, user_id: str, tenant_id: str) -> bool:
        """检查用户是否有权限邀请其他人"""
        # 需要持久化实现
        # return permission_repository.check_invite_permission(user_id, tenant_id)
        return True  # 暂时返回True
    
    async def _check_remove_permission(self, remover_id: str, tenant_id: str, user_id: str) -> bool:
        """检查用户是否有权限移除其他人"""
        # 需要持久化实现
        # return permission_repository.check_remove_permission(remover_id, tenant_id, user_id)
        return True  # 暂时返回True
    
    # 数据检查方法（需要持久化支持）
    async def _check_tenant_code_exists(self, code: str) -> bool:
        """检查租户代码是否已存在"""
        # 需要持久化实现
        # return tenant_repository.check_code_exists(code)
        return False  # 暂时返回False
    
    async def _check_domain_exists(self, domain: str) -> bool:
        """检查域名是否已存在"""
        # 需要持久化实现
        # return tenant_repository.check_domain_exists(domain)
        return False  # 暂时返回False
    
    # 创建实体方法
    def _create_owner_permission(self, tenant_id: str, owner_id: str) -> Permission:
        """创建所有者权限"""
        # 需要领域服务支持
        # return self.domain_service.create_owner_permission(tenant_id, owner_id)
        return Permission(
            user_id=owner_id,
            tenant_id=tenant_id,
            role='owner',
            permissions=['*']
        )
    
    def _create_tenant_permission(
        self,
        tenant_id: str,
        user_id: str,
        role: str,
        permissions: List[str]
    ) -> Permission:
        """创建租户权限"""
        # 需要领域服务支持
        # return self.domain_service.create_tenant_permission(tenant_id, user_id, role, permissions)
        return Permission(
            user_id=user_id,
            tenant_id=tenant_id,
            role=role,
            permissions=permissions
        )
    
    # 异步通知方法
    async def _send_tenant_created_notification(self, owner_id: str, tenant: Tenant):
        """发送租户创建通知"""
        try:
            logger.info(f"Tenant created notification would be sent to owner {owner_id} for tenant {tenant.name}")
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Failed to send tenant created notification: {e}")
    
    async def _send_tenant_invitation_email(self, email: str, tenant_id: str, role: str):
        """发送租户邀请邮件"""
        try:
            logger.info(f"Tenant invitation email would be sent to {email} for tenant {tenant_id} with role {role}")
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Failed to send tenant invitation email: {e}")
    
    async def _send_tenant_joined_notification(self, user_id: str, tenant_id: str, role: str):
        """发送用户加入租户通知"""
        try:
            logger.info(f"Tenant joined notification would be sent to user {user_id} for tenant {tenant_id}")
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Failed to send tenant joined notification: {e}")
    
    async def _send_tenant_removed_notification(self, user_id: str, tenant_id: str):
        """发送用户从租户移除通知"""
        try:
            logger.info(f"Tenant removed notification would be sent to user {user_id} for tenant {tenant_id}")
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Failed to send tenant removed notification: {e}")
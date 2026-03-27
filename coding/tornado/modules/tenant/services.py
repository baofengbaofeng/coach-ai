"""
租户服务
处理租户管理相关的业务逻辑
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple, List

from coding.database.connection import get_db_session
from coding.database.models.tenant import Tenant, TenantMember
from coding.database.models.user import User
from coding.tornado.utils.jwt_utils import create_jwt_token

logger = logging.getLogger(__name__)


class TenantService:
    """
    租户服务类
    处理租户创建、管理、成员管理等业务逻辑
    """
    
    def __init__(self):
        self.jwt_secret = "your-secret-key-change-in-production"  # TODO: 从配置读取
        self.invite_expire_hours = 72  # 邀请链接72小时过期
    
    async def create_tenant(self, owner_id: str, tenant_data: Dict[str, Any]) -> Tuple[bool, Optional[Tenant], Optional[str]]:
        """
        创建新租户
        
        Args:
            owner_id: 所有者用户ID
            tenant_data: 租户数据
            
        Returns:
            (success, tenant, error_message)
        """
        try:
            session = get_db_session()
            
            # 检查用户是否存在
            owner = session.query(User).filter_by(id=owner_id).first()
            if not owner or not owner.is_active():
                return False, None, "Owner not found or inactive"
            
            # 检查租户代码是否已存在
            existing_tenant = session.query(Tenant).filter_by(code=tenant_data['code']).first()
            if existing_tenant:
                return False, None, "Tenant code already exists"
            
            # 检查域名是否已存在（如果提供）
            if 'domain' in tenant_data and tenant_data['domain']:
                existing_domain = session.query(Tenant).filter_by(domain=tenant_data['domain']).first()
                if existing_domain:
                    return False, None, "Domain already in use"
            
            # 创建租户
            tenant = Tenant(
                name=tenant_data['name'],
                code=tenant_data['code'],
                description=tenant_data.get('description'),
                type=tenant_data.get('type', 'family'),
                owner_id=owner_id,
                config=tenant_data.get('config', {}),
                metadata=tenant_data.get('metadata', {}),
                max_members=tenant_data.get('max_members', 10),
                storage_limit_mb=tenant_data.get('storage_limit_mb', 1024),
                subscription_plan=tenant_data.get('subscription_plan', 'free'),
                domain=tenant_data.get('domain'),
                logo_url=tenant_data.get('logo_url'),
                cover_url=tenant_data.get('cover_url')
            )
            
            session.add(tenant)
            session.commit()
            
            # 将所有者添加为租户成员（角色为owner）
            tenant_member = TenantMember(
                tenant_id=tenant.id,
                user_id=owner_id,
                role='owner',
                status='active',
                joined_at=datetime.utcnow(),
                permissions={},  # 所有者拥有所有权限
                config={}
            )
            
            session.add(tenant_member)
            session.commit()
            
            logger.info(f"Tenant created: {tenant.name} ({tenant.code}) by user: {owner.username}")
            return True, tenant, None
            
        except Exception as e:
            logger.error(f"Error creating tenant: {str(e)}")
            return False, None, "Failed to create tenant"
    
    async def get_tenant(self, tenant_id: str, user_id: str = None) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        获取租户信息
        
        Args:
            tenant_id: 租户ID
            user_id: 用户ID（可选，用于检查访问权限）
            
        Returns:
            (success, tenant_data, error_message)
        """
        try:
            session = get_db_session()
            tenant = session.query(Tenant).filter_by(id=tenant_id).first()
            
            if not tenant or tenant.is_deleted:
                return False, None, "Tenant not found"
            
            # 检查用户是否有权限访问（如果提供了user_id）
            if user_id:
                member = session.query(TenantMember).filter_by(
                    tenant_id=tenant_id, 
                    user_id=user_id,
                    status='active'
                ).first()
                
                if not member:
                    return False, None, "Access denied"
            
            tenant_data = tenant.to_public_dict()
            
            # 添加成员数量信息
            member_count = session.query(TenantMember).filter_by(
                tenant_id=tenant_id,
                status='active',
                is_deleted=False
            ).count()
            
            tenant_data['member_count'] = member_count
            tenant_data['can_add_member'] = member_count < tenant.max_members
            
            return True, tenant_data, None
            
        except Exception as e:
            logger.error(f"Error getting tenant: {str(e)}")
            return False, None, "Failed to get tenant"
    
    async def update_tenant(self, tenant_id: str, user_id: str, update_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        更新租户信息
        
        Args:
            tenant_id: 租户ID
            user_id: 用户ID（执行更新的用户）
            update_data: 更新数据
            
        Returns:
            (success, updated_tenant, error_message)
        """
        try:
            session = get_db_session()
            
            # 检查租户是否存在
            tenant = session.query(Tenant).filter_by(id=tenant_id).first()
            if not tenant or tenant.is_deleted:
                return False, None, "Tenant not found"
            
            # 检查用户权限（必须是所有者或管理员）
            member = session.query(TenantMember).filter_by(
                tenant_id=tenant_id,
                user_id=user_id,
                status='active'
            ).first()
            
            if not member or member.role not in ['owner', 'admin']:
                return False, None, "Permission denied"
            
            # 允许更新的字段
            allowed_fields = [
                'name', 'description', 'config', 'metadata',
                'logo_url', 'cover_url', 'max_members', 'storage_limit_mb'
            ]
            
            for field in allowed_fields:
                if field in update_data:
                    setattr(tenant, field, update_data[field])
            
            # 特殊处理：域名更新需要检查唯一性
            if 'domain' in update_data and update_data['domain'] != tenant.domain:
                if update_data['domain']:
                    existing = session.query(Tenant).filter_by(domain=update_data['domain']).first()
                    if existing and existing.id != tenant_id:
                        return False, None, "Domain already in use"
                tenant.domain = update_data['domain']
            
            tenant.updated_by = user_id
            session.commit()
            
            # 返回更新后的租户信息
            return await self.get_tenant(tenant_id, user_id)
            
        except Exception as e:
            logger.error(f"Error updating tenant: {str(e)}")
            return False, None, "Failed to update tenant"
    
    async def delete_tenant(self, tenant_id: str, user_id: str) -> Tuple[bool, Optional[str]]:
        """
        删除租户（软删除）
        
        Args:
            tenant_id: 租户ID
            user_id: 用户ID
            
        Returns:
            (success, error_message)
        """
        try:
            session = get_db_session()
            
            # 检查租户是否存在
            tenant = session.query(Tenant).filter_by(id=tenant_id).first()
            if not tenant or tenant.is_deleted:
                return False, "Tenant not found"
            
            # 检查用户权限（必须是所有者）
            member = session.query(TenantMember).filter_by(
                tenant_id=tenant_id,
                user_id=user_id,
                status='active',
                role='owner'
            ).first()
            
            if not member:
                return False, "Permission denied"
            
            # 软删除租户
            tenant.soft_delete(user_id)
            
            # 软删除所有租户成员
            members = session.query(TenantMember).filter_by(tenant_id=tenant_id).all()
            for member in members:
                member.soft_delete(user_id)
            
            session.commit()
            
            logger.info(f"Tenant deleted: {tenant.name} ({tenant.code}) by user: {user_id}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error deleting tenant: {str(e)}")
            return False, "Failed to delete tenant"
    
    async def get_tenant_members(self, tenant_id: str, user_id: str) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        获取租户成员列表
        
        Args:
            tenant_id: 租户ID
            user_id: 请求用户ID
            
        Returns:
            (success, members_list, error_message)
        """
        try:
            session = get_db_session()
            
            # 检查用户是否有权限访问租户
            requester_member = session.query(TenantMember).filter_by(
                tenant_id=tenant_id,
                user_id=user_id,
                status='active'
            ).first()
            
            if not requester_member:
                return False, None, "Access denied"
            
            # 获取租户成员
            members = session.query(TenantMember).filter_by(
                tenant_id=tenant_id,
                is_deleted=False
            ).all()
            
            members_list = []
            for member in members:
                user = session.query(User).filter_by(id=member.user_id).first()
                if user:
                    member_data = {
                        'id': member.id,
                        'user_id': member.user_id,
                        'username': user.username,
                        'email': user.email,
                        'display_name': user.display_name,
                        'avatar_url': user.avatar_url,
                        'role': member.role,
                        'status': member.status,
                        'joined_at': member.joined_at.isoformat() if member.joined_at else None,
                        'permissions': member.permissions or {},
                        'created_at': member.created_at.isoformat()
                    }
                    members_list.append(member_data)
            
            return True, members_list, None
            
        except Exception as e:
            logger.error(f"Error getting tenant members: {str(e)}")
            return False, None, "Failed to get tenant members"
    
    async def invite_member(self, tenant_id: str, inviter_id: str, invite_data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        邀请用户加入租户
        
        Args:
            tenant_id: 租户ID
            inviter_id: 邀请人ID
            invite_data: 邀请数据
            
        Returns:
            (success, invite_token, error_message)
        """
        try:
            session = get_db_session()
            
            # 检查租户是否存在
            tenant = session.query(Tenant).filter_by(id=tenant_id).first()
            if not tenant or not tenant.is_active() or tenant.is_deleted:
                return False, None, "Tenant not found or inactive"
            
            # 检查邀请人权限
            inviter_member = session.query(TenantMember).filter_by(
                tenant_id=tenant_id,
                user_id=inviter_id,
                status='active',
                role__in=['owner', 'admin']
            ).first()
            
            if not inviter_member:
                return False, None, "Permission denied"
            
            # 检查租户成员数量限制
            current_count = session.query(TenantMember).filter_by(
                tenant_id=tenant_id,
                status='active',
                is_deleted=False
            ).count()
            
            if current_count >= tenant.max_members:
                return False, None, "Tenant has reached maximum member limit"
            
            # 查找被邀请用户
            invitee_email = invite_data.get('email')
            invitee_user = session.query(User).filter_by(email=invitee_email).first()
            
            # 如果用户不存在，可以创建待激活用户或仅发送邀请
            # 这里我们假设用户必须已注册
            if not invitee_user:
                return False, None, "User not found"
            
            # 检查用户是否已经是成员
            existing_member = session.query(TenantMember).filter_by(
                tenant_id=tenant_id,
                user_id=invitee_user.id
            ).first()
            
            if existing_member:
                if existing_member.status == 'active':
                    return False, None, "User is already a member"
                elif existing_member.status == 'pending':
                    return False, None, "Invitation already sent"
            
            # 生成邀请令牌
            invite_token = str(uuid.uuid4())
            
            # 创建租户成员记录（状态为pending）
            tenant_member = TenantMember(
                tenant_id=tenant_id,
                user_id=invitee_user.id,
                role=invite_data.get('role', 'member'),
                status='pending',
                invite_token=invite_token,
                invite_expires_at=datetime.utcnow() + timedelta(hours=self.invite_expire_hours),
                invited_by=inviter_id,
                permissions=invite_data.get('permissions', {}),
                config=invite_data.get('config', {})
            )
            
            session.add(tenant_member)
            session.commit()
            
            logger.info(f"Member invited to tenant {tenant.name}: {invitee_email} by user: {inviter_id}")
            return True, invite_token, None
            
        except Exception as e:
            logger.error(f"Error inviting member: {str(e)}")
            return False, None, "Failed to invite member"
    
    async def accept_invitation(self, invite_token: str, user_id: str) -> Tuple[bool, Optional[str]]:
        """
        接受租户邀请
        
        Args:
            invite_token: 邀请令牌
            user_id: 用户ID
            
        Returns:
            (success, error_message)
        """
        try:
            session = get_db_session()
            
            # 查找邀请记录
            tenant_member = session.query(TenantMember).filter_by(
                invite_token=invite_token,
                user_id=user_id,
                status='pending'
            ).first()
            
            if not tenant_member:
                return False, "Invalid invitation"
            
            # 检查邀请是否过期
            if tenant_member.invite_expires_at and tenant_member.invite_expires_at < datetime.utcnow():
                return False, "Invitation expired"
            
            # 检查租户是否活跃
            tenant = session.query(Tenant).filter_by(id=tenant_member.tenant_id).first()
            if not tenant or not tenant.is_active() or tenant.is_deleted:
                return False, "Tenant not found or inactive"
            
            # 接受邀请
            tenant_member.accept_invitation()
            session.commit()
            
            logger.info(f"User {user_id} accepted invitation to tenant {tenant.name}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error accepting invitation: {str(e)}")
            return False, "Failed to accept invitation"
    
    async def update_member_role(self, tenant_id: str, admin_id: str, member_id: str, new_role: str) -> Tuple[bool, Optional[str]]:
        """
        更新租户成员角色
        
        Args:
            tenant_id: 租户ID
            admin_id: 管理员ID
            member_id: 成员ID
            new_role: 新角色
            
        Returns:
            (success, error_message)
        """
        try:
            session = get_db_session()
            
            # 检查管理员权限
            admin_member = session.query(TenantMember).filter_by(
                tenant_id=tenant_id,
                user_id=admin_id,
                status='active',
                role__in=['owner', 'admin']
            ).first()
            
            if not admin_member:
                return False, "Permission denied"
            
            # 不能修改所有者的角色
            if admin_member.role != 'owner' and new_role == 'owner':
                return False, "Only owners can assign owner role"
            
            # 查找要修改的成员
            target_member = session.query(TenantMember).filter_by(
                tenant_id=tenant_id,
                id=member_id,
                status='active'
            ).first()
            
            if not target_member:
                return False, "Member not found"
            
            # 不能修改自己的角色（除非是所有者）
            if target_member.user_id == admin_id and admin_member.role != 'owner':
                return False, "Cannot change your own role"
            
            # 更新角色
            target_member.role = new_role
            session.commit()
            
            logger.info(f"Member role updated: {member_id} -> {new_role} by admin: {admin_id}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error updating member role: {str(e)}")
            return False, "Failed to update member role"
    
    async def remove_member(self, tenant_id: str, admin_id: str, member_id: str) -> Tuple[bool, Optional[str]]:
        """
        移除租户成员
        
        Args:
            tenant_id: 租户ID
            admin_id: 管理员ID
            member_id: 成员ID
            
        Returns:
            (success, error_message)
        """
        try:
            session = get_db_session()
            
            # 检查管理员权限
            admin_member = session.query(TenantMember).filter_by(
                tenant_id=tenant_id,
                user_id=admin_id,
                status='active',
                role__in=['owner', 'admin']
            ).first()
            
            if not admin_member:
                return False, "Permission denied"
            
            # 查找要移除的成员
            target_member = session.query(TenantMember).filter_by(
                tenant_id=tenant_id,
                id=member_id,
                status='active'
            ).first()
            
            if not target_member:
                return False, "Member not found"
            
            # 不能移除所有者（除非是所有者自己）
            if target_member.role == 'owner' and target_member.user_id != admin_id:
                return False, "Cannot remove owner"
            
            # 不能移除自己（除非是所有者）
            if target_member.user_id == admin_id and admin_member.role != 'owner':
                return False, "Cannot remove yourself"
            
            # 软删除成员
            target_member.soft_delete(admin_id)
            session.commit()
            
            logger.info(f"Member removed from tenant {tenant_id}: {member_id} by admin: {admin_id}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error removing member: {str(e)}")
            return False, "Failed to remove member"
    
    async def get_user_tenants(self, user_id: str) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        获取用户的所有租户
        
        Args:
            user_id: 用户ID
            
        Returns:
            (success, tenants_list, error_message)
        """
        try:
            session = get_db_session()
            
            # 获取用户的所有租户成员关系
            members = session.query(TenantMember).filter_by(
                user_id=user_id,
                status='active',
                is_deleted=False
            ).all()
            
            tenants_list = []
            for member in members:
                tenant = session.query(Tenant).filter_by(id=member.tenant_id).first()
                if tenant and tenant.is_active() and not tenant.is_deleted:
                    tenant_data = tenant.to_public_dict()
                    tenant_data['role'] = member.role
                    tenant_data['joined_at'] = member.joined_at.isoformat() if member.joined_at else None
                    
                    # 添加成员数量
                    member_count = session.query(TenantMember).filter_by(
                        tenant_id=tenant.id,
                        status='active',
                        is_deleted=False
                    ).count()
                    
                    tenant_data['member_count'] = member_count
                    tenants_list.append(tenant_data)
            
            return True, tenants_list, None
            
        except Exception as e:
            logger.error(f"Error getting user tenants: {str(e)}")
            return False, None, "Failed to get user tenants"
    
    async def search_tenants(self, query: str, user_id: str = None, limit: int = 20) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        搜索租户
        
        Args:
            query: 搜索关键词
            user_id: 用户ID（可选，用于过滤可访问的租户）
            limit: 结果数量限制
            
        Returns:
            (success, tenants_list, error_message)
        """
        try:
            session = get_db_session()
            
            # 构建搜索查询
            search_query = session.query(Tenant).filter(
                Tenant.is_deleted == False,
                Tenant.status == 'active',
                (Tenant.name.ilike(f"%{query}%")) | (Tenant.code.ilike(f"%{query}%")) | (Tenant.description.ilike(f"%{query}%"))
            )
            
            # 如果提供了用户ID，只返回用户有权限访问的租户
            if user_id:
                user_tenant_ids = [
                    m.tenant_id for m in session.query(TenantMember).filter_by(
                        user_id=user_id,
                        status='active'
                    ).all()
                ]
                search_query = search_query.filter(Tenant.id.in_(user_tenant_ids))
            
            # 执行查询
            tenants = search_query.limit(limit).all()
            
            tenants_list = []
            for tenant in tenants:
                tenant_data = tenant.to_public_dict()
                
                # 添加成员数量
                member_count = session.query(TenantMember).filter_by(
                    tenant_id=tenant.id,
                    status='active',
                    is_deleted=False
                ).count()
                
                tenant_data['member_count'] = member_count
                tenants_list.append(tenant_data)
            
            return True, tenants_list, None
            
        except Exception as e:
            logger.error(f"Error searching tenants: {str(e)}")
            return False, None, "Failed to search tenants"


# 全局租户服务实例
tenant_service = TenantService()

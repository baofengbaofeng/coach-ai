"""
租户处理器
处理租户管理相关的HTTP请求
"""

import logging
from typing import Dict, Any

from tornado.web import RequestHandler
from coding.tornado.core.base_handler import BaseHandler
from coding.tornado.core.exceptions import ValidationError, AuthenticationError, PermissionError
from coding.tornado.core.error_handler import handle_error

from .services import tenant_service

logger = logging.getLogger(__name__)


class CreateTenantHandler(BaseHandler):
    """
    创建租户处理器
    """
    
    async def post(self):
        """
        创建新租户
        POST /api/tenants
        
        Headers:
        Authorization: Bearer <token>
        
        Request Body:
        {
            "name": "string",          # 租户名称
            "code": "string",          # 租户代码（唯一）
            "description": "string",   # 描述（可选）
            "type": "family",          # 类型：family, organization, team, individual
            "domain": "string",        # 域名（可选，唯一）
            "logo_url": "string",      # Logo URL（可选）
            "cover_url": "string",     # 封面图片URL（可选）
            "config": {},              # 配置（可选）
            "metadata": {}             # 元数据（可选）
        }
        
        Response:
        {
            "success": true,
            "data": {
                "tenant": {
                    "id": "string",
                    "name": "string",
                    "code": "string",
                    "type": "string",
                    "status": "string",
                    "owner_id": "string",
                    "created_at": "string"
                },
                "message": "Tenant created successfully"
            }
        }
        """
        try:
            # 验证用户身份
            user_id = self.get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            # 验证请求数据
            data = self.get_json_body()
            required_fields = ['name', 'code']
            
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValidationError(f"Field '{field}' is required")
            
            # 验证租户代码格式
            if not data['code'].replace('_', '').replace('-', '').isalnum():
                raise ValidationError("Tenant code can only contain letters, numbers, underscores and hyphens")
            
            # 调用服务创建租户
            success, tenant, error = await tenant_service.create_tenant(user_id, data)
            
            if not success:
                raise ValidationError(error)
            
            # 准备响应数据
            response_data = {
                'tenant': tenant.to_public_dict(),
                'message': 'Tenant created successfully'
            }
            
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class GetTenantHandler(BaseHandler):
    """
    获取租户信息处理器
    """
    
    async def get(self, tenant_id):
        """
        获取租户信息
        GET /api/tenants/{tenant_id}
        
        Headers:
        Authorization: Bearer <token>
        
        Response:
        {
            "success": true,
            "data": {
                "id": "string",
                "name": "string",
                "code": "string",
                "description": "string",
                "type": "string",
                "status": "string",
                "owner_id": "string",
                "member_count": 1,
                "can_add_member": true,
                "created_at": "string",
                "updated_at": "string"
            }
        }
        """
        try:
            # 验证用户身份
            user_id = self.get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            # 调用服务获取租户信息
            success, tenant_data, error = await tenant_service.get_tenant(tenant_id, user_id)
            
            if not success:
                raise ValidationError(error)
            
            self.write_success(tenant_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class UpdateTenantHandler(BaseHandler):
    """
    更新租户信息处理器
    """
    
    async def put(self, tenant_id):
        """
        更新租户信息
        PUT /api/tenants/{tenant_id}
        
        Headers:
        Authorization: Bearer <token>
        
        Request Body:
        {
            "name": "string",          # 租户名称（可选）
            "description": "string",   # 描述（可选）
            "domain": "string",        # 域名（可选）
            "logo_url": "string",      # Logo URL（可选）
            "cover_url": "string",     # 封面图片URL（可选）
            "config": {},              # 配置（可选）
            "metadata": {}             # 元数据（可选）
        }
        
        Response:
        {
            "success": true,
            "data": {
                "tenant": {
                    // 更新后的租户信息
                },
                "message": "Tenant updated successfully"
            }
        }
        """
        try:
            # 验证用户身份
            user_id = self.get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            # 获取更新数据
            data = self.get_json_body()
            if not data:
                raise ValidationError("No data provided for update")
            
            # 调用服务更新租户
            success, updated_tenant, error = await tenant_service.update_tenant(tenant_id, user_id, data)
            
            if not success:
                raise ValidationError(error)
            
            response_data = {
                'tenant': updated_tenant,
                'message': 'Tenant updated successfully'
            }
            
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class DeleteTenantHandler(BaseHandler):
    """
    删除租户处理器
    """
    
    async def delete(self, tenant_id):
        """
        删除租户
        DELETE /api/tenants/{tenant_id}
        
        Headers:
        Authorization: Bearer <token>
        
        Response:
        {
            "success": true,
            "data": {
                "message": "Tenant deleted successfully"
            }
        }
        """
        try:
            # 验证用户身份
            user_id = self.get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            # 调用服务删除租户
            success, error = await tenant_service.delete_tenant(tenant_id, user_id)
            
            if not success:
                raise ValidationError(error)
            
            response_data = {'message': 'Tenant deleted successfully'}
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class GetTenantMembersHandler(BaseHandler):
    """
    获取租户成员列表处理器
    """
    
    async def get(self, tenant_id):
        """
        获取租户成员列表
        GET /api/tenants/{tenant_id}/members
        
        Headers:
        Authorization: Bearer <token>
        
        Response:
        {
            "success": true,
            "data": {
                "members": [
                    {
                        "id": "string",
                        "user_id": "string",
                        "username": "string",
                        "email": "string",
                        "display_name": "string",
                        "avatar_url": "string",
                        "role": "string",
                        "status": "string",
                        "joined_at": "string",
                        "permissions": {},
                        "created_at": "string"
                    }
                ],
                "total": 1
            }
        }
        """
        try:
            # 验证用户身份
            user_id = self.get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            # 调用服务获取成员列表
            success, members_list, error = await tenant_service.get_tenant_members(tenant_id, user_id)
            
            if not success:
                raise ValidationError(error)
            
            response_data = {
                'members': members_list,
                'total': len(members_list) if members_list else 0
            }
            
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class InviteMemberHandler(BaseHandler):
    """
    邀请成员处理器
    """
    
    async def post(self, tenant_id):
        """
        邀请用户加入租户
        POST /api/tenants/{tenant_id}/members/invite
        
        Headers:
        Authorization: Bearer <token>
        
        Request Body:
        {
            "email": "string",         # 被邀请用户邮箱
            "role": "member",          # 角色：owner, admin, member, guest
            "permissions": {},         # 权限配置（可选）
            "config": {}               # 成员配置（可选）
        }
        
        Response:
        {
            "success": true,
            "data": {
                "invite_token": "string",
                "message": "Invitation sent successfully"
            }
        }
        """
        try:
            # 验证用户身份
            user_id = self.get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            # 验证请求数据
            data = self.get_json_body()
            required_fields = ['email']
            
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValidationError(f"Field '{field}' is required")
            
            # 验证邮箱格式
            if '@' not in data['email']:
                raise ValidationError("Invalid email format")
            
            # 验证角色
            valid_roles = ['owner', 'admin', 'member', 'guest']
            if 'role' in data and data['role'] not in valid_roles:
                raise ValidationError(f"Role must be one of: {', '.join(valid_roles)}")
            
            # 调用服务邀请成员
            success, invite_token, error = await tenant_service.invite_member(tenant_id, user_id, data)
            
            if not success:
                raise ValidationError(error)
            
            response_data = {
                'invite_token': invite_token,
                'message': 'Invitation sent successfully'
            }
            
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class AcceptInvitationHandler(BaseHandler):
    """
    接受邀请处理器
    """
    
    async def post(self):
        """
        接受租户邀请
        POST /api/tenants/invitations/accept
        
        Headers:
        Authorization: Bearer <token>
        
        Request Body:
        {
            "invite_token": "string"   # 邀请令牌
        }
        
        Response:
        {
            "success": true,
            "data": {
                "message": "Invitation accepted successfully"
            }
        }
        """
        try:
            # 验证用户身份
            user_id = self.get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            # 验证请求数据
            data = self.get_json_body()
            if 'invite_token' not in data or not data['invite_token']:
                raise ValidationError("Invite token is required")
            
            # 调用服务接受邀请
            success, error = await tenant_service.accept_invitation(data['invite_token'], user_id)
            
            if not success:
                raise ValidationError(error)
            
            response_data = {'message': 'Invitation accepted successfully'}
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class UpdateMemberRoleHandler(BaseHandler):
    """
    更新成员角色处理器
    """
    
    async def put(self, tenant_id, member_id):
        """
        更新租户成员角色
        PUT /api/tenants/{tenant_id}/members/{member_id}/role
        
        Headers:
        Authorization: Bearer <token>
        
        Request Body:
        {
            "role": "string"  # 新角色：owner, admin, member, guest
        }
        
        Response:
        {
            "success": true,
            "data": {
                "message": "Member role updated successfully"
            }
        }
        """
        try:
            # 验证用户身份
            user_id = self.get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            # 验证请求数据
            data = self.get_json_body()
            if 'role' not in data or not data['role']:
                raise ValidationError("Role is required")
            
            # 验证角色
            valid_roles = ['owner', 'admin', 'member', 'guest']
            if data['role'] not in valid_roles:
                raise ValidationError(f"Role must be one of: {', '.join(valid_roles)}")
            
            # 调用服务更新成员角色
            success, error = await tenant_service.update_member_role(tenant_id, user_id, member_id, data['role'])
            
            if not success:
                raise ValidationError(error)
            
            response_data = {'message': 'Member role updated successfully'}
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class RemoveMemberHandler(BaseHandler):
    """
    移除成员处理器
    """
    
    async def delete(self, tenant_id, member_id):
        """
        移除租户成员
        DELETE /api/tenants/{tenant_id}/members/{member_id}
        
        Headers:
        Authorization: Bearer <token>
        
        Response:
        {
            "success": true,
            "data": {
                "message": "Member removed successfully"
            }
        }
        """
        try:
            # 验证用户身份
            user_id = self.get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            # 调用服务移除成员
            success, error = await tenant_service.remove_member(tenant_id, user_id, member_id)
            
            if not success:
                raise ValidationError(error)
            
            response_data = {'message': 'Member removed successfully'}
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class GetUserTenantsHandler(BaseHandler):
    """
    获取用户租户列表处理器
    """
    
    async def get(self):
        """
        获取用户的所有租户
        GET /api/tenants/my
        
        Headers:
        Authorization: Bearer <token>
        
        Response:
        {
            "success": true,
            "data": {
                "tenants": [
                    {
                        "id": "string",
                        "name": "string",
                        "code": "string",
                        "type": "string",
                        "status": "string",
                        "role": "string",
                        "member_count": 1,
                        "joined_at": "string",
                        "created_at": "string"
                    }
                ],
                "total": 1
            }
        }
        """
        try:
            # 验证用户身份
            user_id = self.get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            # 调用服务获取用户租户
            success, tenants_list, error = await tenant_service.get_user_tenants(user_id)
            
            if not success:
                raise ValidationError(error)
            
            response_data = {
                'tenants': tenants_list,
                'total': len(tenants_list) if tenants_list else 0
            }
            
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)


class SearchTenantsHandler(BaseHandler):
    """
    搜索租户处理器
    """
    
    async def get(self):
        """
        搜索租户
        GET /api/tenants/search?q=<query>&limit=<limit>
        
        Headers:
        Authorization: Bearer <token>（可选）
        
        Query Parameters:
        - q: 搜索关键词
        - limit: 结果数量限制（默认20，最大100）
        
        Response:
        {
            "success": true,
            "data": {
                "tenants": [
                    {
                        "id": "string",
                        "name": "string",
                        "code": "string",
                        "description": "string",
                        "type": "string",
                        "status": "string",
                        "member_count": 1,
                        "created_at": "string"
                    }
                ],
                "total": 1
            }
        }
        """
        try:
            # 获取查询参数
            query = self.get_argument('q', '').strip()
            if not query:
                raise ValidationError("Search query is required")
            
            limit = min(int(self.get_argument('limit', 20)), 100)
            
            # 获取用户ID（如果已认证）
            user_id = self.get_current_user_id()
            
            # 调用服务搜索租户
            success, tenants_list, error = await tenant_service.search_tenants(query, user_id, limit)
            
            if not success:
                raise ValidationError(error)
            
            response_data = {
                'tenants': tenants_list,
                'total': len(tenants_list) if tenants_list else 0
            }
            
            self.write_success(response_data)
            
        except Exception as e:
            handle_error(self, e, logger)
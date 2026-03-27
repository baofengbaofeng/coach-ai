"""
租户处理器（简化迁移版）
处理租户管理相关的HTTP请求
"""

import logging
from typing import Dict, Any

from tornado.web import RequestHandler
from src.interfaces.api.middleware.exceptions import ValidationError, AuthenticationError
from src.interfaces.api.middleware.auth_middleware import auth_required
from src.application.services.tenant_service import TenantService

logger = logging.getLogger(__name__)


class CreateTenantHandler(RequestHandler):
    """
    创建租户处理器
    """
    
    @auth_required
    async def post(self):
        """
        创建新租户
        POST /api/tenants
        """
        try:
            # 获取当前用户
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            # 验证请求数据
            import json
            data = json.loads(self.request.body.decode('utf-8'))
            
            required_fields = ['name', 'code']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValidationError(f"Field '{field}' is required")
            
            # 验证租户代码格式
            code = data['code']
            if not code.replace('_', '').replace('-', '').isalnum():
                raise ValidationError("Tenant code can only contain letters, numbers, underscores and hyphens")
            
            # 调用应用服务创建租户
            tenant_service = TenantService()
            result = await tenant_service.create_tenant(
                owner_id=user_id,
                name=data['name'],
                code=code,
                description=data.get('description'),
                tenant_type=data.get('type', 'individual'),
                domain=data.get('domain'),
                logo_url=data.get('logo_url'),
                config=data.get('config', {}),
                metadata=data.get('metadata', {})
            )
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to create tenant'))
            
            self.write({
                "success": True,
                "data": result.get('data'),
                "message": "Tenant created successfully"
            })
            
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({
                "success": False,
                "error": {"message": "Invalid JSON format"}
            })
        except Exception as e:
            logger.error(f"Create tenant error: {e}")
            self.set_status(400)
            self.write({
                "success": False,
                "error": {"message": str(e)}
            })


class GetTenantHandler(RequestHandler):
    """
    获取租户信息处理器
    """
    
    @auth_required
    async def get(self, tenant_id: str = None):
        """
        获取租户信息
        GET /api/tenants/{tenant_id}
        GET /api/tenants/current
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            # 如果没有提供tenant_id，获取当前用户的租户
            if not tenant_id or tenant_id == 'current':
                tenant_id = self.current_user.get('tenant_id')
                if not tenant_id:
                    raise ValidationError("User is not associated with any tenant")
            
            # 调用应用服务获取租户信息
            tenant_service = TenantService()
            result = await tenant_service.get_tenant(tenant_id, user_id)
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to get tenant'))
            
            self.write({
                "success": True,
                "data": result.get('data'),
                "message": "Tenant retrieved successfully"
            })
            
        except Exception as e:
            logger.error(f"Get tenant error: {e}")
            self.set_status(400)
            self.write({
                "success": False,
                "error": {"message": str(e)}
            })


class UpdateTenantHandler(RequestHandler):
    """
    更新租户信息处理器
    """
    
    @auth_required
    async def put(self, tenant_id: str):
        """
        更新租户信息
        PUT /api/tenants/{tenant_id}
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            # 验证请求数据
            import json
            data = json.loads(self.request.body.decode('utf-8'))
            
            # 调用应用服务更新租户
            tenant_service = TenantService()
            result = await tenant_service.update_tenant(
                tenant_id=tenant_id,
                user_id=user_id,
                update_data=data
            )
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to update tenant'))
            
            self.write({
                "success": True,
                "data": result.get('data'),
                "message": "Tenant updated successfully"
            })
            
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({
                "success": False,
                "error": {"message": "Invalid JSON format"}
            })
        except Exception as e:
            logger.error(f"Update tenant error: {e}")
            self.set_status(400)
            self.write({
                "success": False,
                "error": {"message": str(e)}
            })


class ListTenantsHandler(RequestHandler):
    """
    列出用户租户处理器
    """
    
    @auth_required
    async def get(self):
        """
        列出用户的所有租户
        GET /api/tenants
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            # 获取查询参数
            page = int(self.get_argument('page', 1))
            limit = int(self.get_argument('limit', 20))
            status = self.get_argument('status', None)
            
            # 调用应用服务列出租户
            tenant_service = TenantService()
            result = await tenant_service.list_user_tenants(
                user_id=user_id,
                page=page,
                limit=limit,
                status=status
            )
            
            self.write({
                "success": True,
                "data": result.get('data'),
                "pagination": result.get('pagination', {}),
                "message": "Tenants listed successfully"
            })
            
        except Exception as e:
            logger.error(f"List tenants error: {e}")
            self.set_status(400)
            self.write({
                "success": False,
                "error": {"message": str(e)}
            })


class InviteUserHandler(RequestHandler):
    """
    邀请用户加入租户处理器
    """
    
    @auth_required
    async def post(self, tenant_id: str):
        """
        邀请用户加入租户
        POST /api/tenants/{tenant_id}/invite
        """
        try:
            user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            if not user_id:
                raise AuthenticationError("Authentication required")
            
            # 验证请求数据
            import json
            data = json.loads(self.request.body.decode('utf-8'))
            
            required_fields = ['email', 'role']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValidationError(f"Field '{field}' is required")
            
            # 调用应用服务邀请用户
            tenant_service = TenantService()
            result = await tenant_service.invite_user_to_tenant(
                tenant_id=tenant_id,
                inviter_id=user_id,
                email=data['email'],
                role=data['role'],
                permissions=data.get('permissions', [])
            )
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to invite user'))
            
            self.write({
                "success": True,
                "data": result.get('data'),
                "message": "User invited successfully"
            })
            
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({
                "success": False,
                "error": {"message": "Invalid JSON format"}
            })
        except Exception as e:
            logger.error(f"Invite user error: {e}")
            self.set_status(400)
            self.write({
                "success": False,
                "error": {"message": str(e)}
            })


class RemoveUserHandler(RequestHandler):
    """
    移除用户从租户处理器
    """
    
    @auth_required
    async def delete(self, tenant_id: str, user_id: str):
        """
        从租户中移除用户
        DELETE /api/tenants/{tenant_id}/users/{user_id}
        """
        try:
            current_user_id = self.current_user.get('id') if hasattr(self, 'current_user') else None
            if not current_user_id:
                raise AuthenticationError("Authentication required")
            
            # 调用应用服务移除用户
            tenant_service = TenantService()
            result = await tenant_service.remove_user_from_tenant(
                tenant_id=tenant_id,
                remover_id=current_user_id,
                user_id=user_id
            )
            
            if not result.get('success'):
                raise ValidationError(result.get('error', 'Failed to remove user'))
            
            self.write({
                "success": True,
                "data": result.get('data'),
                "message": "User removed successfully"
            })
            
        except Exception as e:
            logger.error(f"Remove user error: {e}")
            self.set_status(400)
            self.write({
                "success": False,
                "error": {"message": str(e)}
            })
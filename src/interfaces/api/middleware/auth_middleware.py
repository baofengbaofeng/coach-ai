"""
JWT认证中间件（简化迁移版）
处理请求的JWT认证和授权
"""

import jwt
from typing import Optional, Dict, Any, List
from loguru import logger
from tornado.web import RequestHandler, HTTPError

from src.settings import settings
from src.infrastructure.security.jwt_utils import JWTUtils
from src.interfaces.api.middleware.exceptions import AuthenticationError, AuthorizationError


class JWTAuthMiddleware:
    """JWT认证中间件"""
    
    def __init__(self, handler: RequestHandler):
        """
        初始化JWT认证中间件
        
        Args:
            handler: RequestHandler实例
        """
        self.handler = handler
        self.current_user: Optional[Dict[str, Any]] = None
        self.token_payload: Optional[Dict[str, Any]] = None
    
    async def prepare(self) -> None:
        """在请求处理前执行，验证JWT令牌"""
        # 检查是否需要认证
        if self._should_skip_auth():
            return
        
        # 提取和验证令牌
        token = self._extract_token()
        if not token:
            raise AuthenticationError("Missing authentication token", "MISSING_TOKEN")
        
        try:
            # 解码令牌
            payload = JWTUtils.verify_token(token)
            if not payload:
                raise AuthenticationError("Invalid token", "INVALID_TOKEN")
            
            # 验证令牌类型
            token_type = payload.get("type")
            if token_type != "access":
                raise AuthenticationError("Invalid token type", "INVALID_TOKEN_TYPE")
            
            # 设置当前用户和令牌载荷
            self.current_user = {
                "id": payload.get("user_id"),
                "username": payload.get("username"),
                "email": payload.get("email"),
                "tenant_id": payload.get("tenant_id"),
                "roles": payload.get("roles", []),
                "permissions": payload.get("permissions", [])
            }
            self.token_payload = payload
            
            # 设置到handler
            self.handler.current_user = self.current_user
            self.handler.token_payload = payload
            
            # 记录认证信息
            logger.debug(f"User authenticated: {self.current_user['username']} (ID: {self.current_user['id']})")
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired", "TOKEN_EXPIRED")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}", "INVALID_TOKEN")
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise AuthenticationError("Authentication failed", "AUTH_FAILED")
    
    def _should_skip_auth(self) -> bool:
        """
        检查是否应该跳过认证
        
        Returns:
            bool: 如果应该跳过认证返回True
        """
        # 检查handler是否标记为不需要认证
        if getattr(self.handler, "skip_auth", False):
            return True
        
        # 检查请求方法是否为OPTIONS（预检请求）
        if self.handler.request.method == "OPTIONS":
            return True
        
        # 检查是否为公开端点
        public_endpoints = [
            "/api/health",
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh",
            "/api/auth/verify-email",
            "/api/auth/reset-password",
            "/api/auth/forgot-password",
            "/api/docs",
            "/api/openapi.json",
            "/api/swagger"
        ]
        
        request_path = self.handler.request.path
        for endpoint in public_endpoints:
            if request_path.startswith(endpoint):
                return True
        
        return False
    
    def _extract_token(self) -> Optional[str]:
        """
        从请求中提取JWT令牌
        
        Returns:
            str: JWT令牌或None
        """
        # 从Authorization头提取
        auth_header = self.handler.request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # 移除"Bearer "前缀
        
        # 从查询参数提取
        token_param = self.handler.get_argument("token", None)
        if token_param:
            return token_param
        
        # 从cookie提取
        token_cookie = self.handler.get_cookie("access_token")
        if token_cookie:
            return token_cookie
        
        return None
    
    def check_permission(self, permission: str) -> bool:
        """
        检查用户是否具有指定权限
        
        Args:
            permission: 权限标识符
            
        Returns:
            bool: 是否具有权限
        """
        if not self.current_user:
            return False
        
        user_permissions = self.current_user.get("permissions", [])
        return permission in user_permissions
    
    def require_permission(self, permission: str) -> None:
        """
        要求用户具有指定权限，否则抛出异常
        
        Args:
            permission: 权限标识符
            
        Raises:
            AuthorizationError: 如果用户没有权限
        """
        if not self.check_permission(permission):
            raise AuthorizationError(
                f"Permission denied: {permission}",
                "PERMISSION_DENIED"
            )
    
    def check_role(self, role: str) -> bool:
        """
        检查用户是否具有指定角色
        
        Args:
            role: 角色标识符
            
        Returns:
            bool: 是否具有角色
        """
        if not self.current_user:
            return False
        
        user_roles = self.current_user.get("roles", [])
        return role in user_roles
    
    def require_role(self, role: str) -> None:
        """
        要求用户具有指定角色，否则抛出异常
        
        Args:
            role: 角色标识符
            
        Raises:
            AuthorizationError: 如果用户没有角色
        """
        if not self.check_role(role):
            raise AuthorizationError(
                f"Role required: {role}",
                "ROLE_REQUIRED"
            )
    
    def get_user_id(self) -> Optional[str]:
        """
        获取当前用户ID
        
        Returns:
            str: 用户ID或None
        """
        if self.current_user:
            return self.current_user.get("id")
        return None
    
    def get_tenant_id(self) -> Optional[str]:
        """
        获取当前租户ID
        
        Returns:
            str: 租户ID或None
        """
        if self.current_user:
            return self.current_user.get("tenant_id")
        return None
    
    def is_authenticated(self) -> bool:
        """
        检查用户是否已认证
        
        Returns:
            bool: 是否已认证
        """
        return self.current_user is not None


def auth_required(handler_class):
    """
    装饰器：要求认证
    
    Args:
        handler_class: RequestHandler类
        
    Returns:
        装饰后的类
    """
    original_prepare = handler_class.prepare
    
    async def new_prepare(self):
        # 创建中间件实例
        middleware = JWTAuthMiddleware(self)
        await middleware.prepare()
        
        # 调用原始的prepare方法
        if original_prepare:
            await original_prepare(self)
    
    handler_class.prepare = new_prepare
    return handler_class


def permission_required(permission: str):
    """
    装饰器工厂：要求特定权限
    
    Args:
        permission: 权限标识符
        
    Returns:
        装饰器函数
    """
    def decorator(handler_class):
        original_prepare = handler_class.prepare
        
        async def new_prepare(self):
            # 创建中间件实例
            middleware = JWTAuthMiddleware(self)
            await middleware.prepare()
            
            # 检查权限
            middleware.require_permission(permission)
            
            # 调用原始的prepare方法
            if original_prepare:
                await original_prepare(self)
        
        handler_class.prepare = new_prepare
        return handler_class
    
    return decorator


def role_required(role: str):
    """
    装饰器工厂：要求特定角色
    
    Args:
        role: 角色标识符
        
    Returns:
        装饰器函数
    """
    def decorator(handler_class):
        original_prepare = handler_class.prepare
        
        async def new_prepare(self):
            # 创建中间件实例
            middleware = JWTAuthMiddleware(self)
            await middleware.prepare()
            
            # 检查角色
            middleware.require_role(role)
            
            # 调用原始的prepare方法
            if original_prepare:
                await original_prepare(self)
        
        handler_class.prepare = new_prepare
        return handler_class
    
    return decorator
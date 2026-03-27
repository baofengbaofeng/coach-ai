"""
JWT认证中间件
处理请求的JWT认证和授权
"""

import jwt
from typing import Optional, Dict, Any
from loguru import logger
from tornado.web import RequestHandler, HTTPError

from coding.config import config
from tornado.utils.jwt_utils import decode_token, TokenType
from tornado.core.exceptions import AuthenticationError, AuthorizationError


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
            payload = decode_token(token)
            
            # 验证令牌类型
            token_type = payload.get("type")
            if token_type != TokenType.ACCESS.value:
                raise AuthenticationError("Invalid token type", "INVALID_TOKEN_TYPE")
            
            # 检查令牌是否在黑名单中（需要Redis支持）
            if self._is_token_blacklisted(token):
                raise AuthenticationError("Token has been revoked", "TOKEN_REVOKED")
            
            # 设置当前用户和令牌载荷
            self.current_user = {
                "id": payload.get("sub"),
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
            
            # 记录认证信息（英文日志）
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
        ]
        
        if self.handler.request.path in public_endpoints:
            return True
        
        # 检查路径前缀
        public_prefixes = [
            "/api/public/",
            "/docs/",
            "/swagger/",
        ]
        
        for prefix in public_prefixes:
            if self.handler.request.path.startswith(prefix):
                return True
        
        return False
    
    def _extract_token(self) -> Optional[str]:
        """
        从请求中提取JWT令牌
        
        Returns:
            Optional[str]: 提取到的令牌，如果未找到返回None
        """
        # 从Authorization头提取
        auth_header = self.handler.request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # 移除"Bearer "前缀
        
        # 从查询参数提取
        token = self.handler.get_argument("token", None)
        if token:
            return token
        
        # 从cookie提取
        token = self.handler.get_cookie("access_token")
        if token:
            return token
        
        return None
    
    def _is_token_blacklisted(self, token: str) -> bool:
        """
        检查令牌是否在黑名单中
        
        Args:
            token: JWT令牌
            
        Returns:
            bool: 如果在黑名单中返回True
        """
        # 这里需要Redis支持来检查令牌黑名单
        # 暂时返回False，实际项目中需要实现
        return False


class PermissionMiddleware:
    """权限检查中间件"""
    
    def __init__(self, handler: RequestHandler):
        """
        初始化权限检查中间件
        
        Args:
            handler: RequestHandler实例
        """
        self.handler = handler
    
    async def prepare(self) -> None:
        """在请求处理前执行，检查权限"""
        # 检查是否需要权限检查
        if self._should_skip_permission_check():
            return
        
        # 确保用户已认证
        if not hasattr(self.handler, "current_user") or not self.handler.current_user:
            raise AuthenticationError("Authentication required", "AUTH_REQUIRED")
        
        # 获取需要的权限
        required_permissions = getattr(self.handler, "required_permissions", [])
        required_roles = getattr(self.handler, "required_roles", [])
        
        # 检查角色
        if required_roles:
            user_roles = self.handler.current_user.get("roles", [])
            if not any(role in user_roles for role in required_roles):
                raise AuthorizationError(
                    f"Required roles: {required_roles}",
                    "INSUFFICIENT_ROLES"
                )
        
        # 检查权限
        if required_permissions:
            user_permissions = self.handler.current_user.get("permissions", [])
            if not any(perm in user_permissions for perm in required_permissions):
                raise AuthorizationError(
                    f"Required permissions: {required_permissions}",
                    "INSUFFICIENT_PERMISSIONS"
                )
        
        # 记录权限检查（英文日志）
        logger.debug(
            f"Permission check passed for user {self.handler.current_user['username']} "
            f"on {self.handler.request.method} {self.handler.request.path}"
        )
    
    def _should_skip_permission_check(self) -> bool:
        """
        检查是否应该跳过权限检查
        
        Returns:
            bool: 如果应该跳过权限检查返回True
        """
        # 检查handler是否标记为不需要权限检查
        if getattr(self.handler, "skip_permission_check", False):
            return True
        
        # 公开端点不需要权限检查
        auth_middleware = JWTAuthMiddleware(self.handler)
        if auth_middleware._should_skip_auth():
            return True
        
        return False


class RateLimitMiddleware:
    """速率限制中间件"""
    
    def __init__(self, handler: RequestHandler):
        """
        初始化速率限制中间件
        
        Args:
            handler: RequestHandler实例
        """
        self.handler = handler
    
    async def prepare(self) -> None:
        """在请求处理前执行，检查速率限制"""
        # 检查是否应该跳过速率限制
        if self._should_skip_rate_limit():
            return
        
        # 获取客户端标识
        client_id = self._get_client_id()
        
        # 检查速率限制（需要Redis支持）
        if self._is_rate_limited(client_id):
            raise HTTPError(
                429,
                "Too many requests. Please try again later."
            )
        
        # 记录请求（实际项目中需要Redis记录）
        self._record_request(client_id)
    
    def _should_skip_rate_limit(self) -> bool:
        """
        检查是否应该跳过速率限制
        
        Returns:
            bool: 如果应该跳过速率限制返回True
        """
        # 检查handler是否标记为不需要速率限制
        if getattr(self.handler, "skip_rate_limit", False):
            return True
        
        # 健康检查端点不需要速率限制
        if self.handler.request.path == "/api/health":
            return True
        
        return False
    
    def _get_client_id(self) -> str:
        """
        获取客户端标识
        
        Returns:
            str: 客户端标识
        """
        # 优先使用用户ID（如果已认证）
        if hasattr(self.handler, "current_user") and self.handler.current_user:
            return f"user:{self.handler.current_user['id']}"
        
        # 使用IP地址
        return f"ip:{self.handler.request.remote_ip}"
    
    def _is_rate_limited(self, client_id: str) -> bool:
        """
        检查是否超过速率限制
        
        Args:
            client_id: 客户端标识
            
        Returns:
            bool: 如果超过限制返回True
        """
        # 这里需要Redis支持来实现速率限制
        # 暂时返回False，实际项目中需要实现
        return False
    
    def _record_request(self, client_id: str) -> None:
        """
        记录请求
        
        Args:
            client_id: 客户端标识
        """
        # 这里需要Redis支持来记录请求
        # 实际项目中需要实现
        pass


# 装饰器函数
def skip_auth(handler_class):
    """
    装饰器：标记Handler不需要认证
    
    Args:
        handler_class: Handler类
        
    Returns:
        装饰后的Handler类
    """
    handler_class.skip_auth = True
    return handler_class


def skip_permission_check(handler_class):
    """
    装饰器：标记Handler不需要权限检查
    
    Args:
        handler_class: Handler类
        
    Returns:
        装饰后的Handler类
    """
    handler_class.skip_permission_check = True
    return handler_class


def skip_rate_limit(handler_class):
    """
    装饰器：标记Handler不需要速率限制
    
    Args:
        handler_class: Handler类
        
    Returns:
        装饰后的Handler类
    """
    handler_class.skip_rate_limit = True
    return handler_class


def require_permissions(*permissions):
    """
    装饰器：要求特定权限
    
    Args:
        *permissions: 需要的权限列表
        
    Returns:
        装饰器函数
    """
    def decorator(handler_class):
        handler_class.required_permissions = permissions
        return handler_class
    return decorator


def require_roles(*roles):
    """
    装饰器：要求特定角色
    
    Args:
        *roles: 需要的角色列表
        
    Returns:
        装饰器函数
    """
    def decorator(handler_class):
        handler_class.required_roles = roles
        return handler_class
    return decorator


# 更新中间件管理器
def update_middleware_classes():
    """
    更新中间件类列表，添加认证相关中间件
    
    Returns:
        list: 更新后的中间件类列表
    """
    from tornado.core.middleware import MiddlewareManager
    
    # 在适当位置插入认证中间件
    middleware_classes = MiddlewareManager.MIDDLEWARE_CLASSES.copy()
    
    # 在TenantMiddleware之后插入认证中间件
    tenant_index = next(
        i for i, cls in enumerate(middleware_classes) 
        if cls.__name__ == "TenantMiddleware"
    )
    
    # 插入认证相关中间件
    middleware_classes.insert(tenant_index + 1, JWTAuthMiddleware)
    middleware_classes.insert(tenant_index + 2, PermissionMiddleware)
    middleware_classes.insert(tenant_index + 3, RateLimitMiddleware)
    
    return middleware_classes
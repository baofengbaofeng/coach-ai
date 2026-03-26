"""
应用工厂模块
创建Tornado应用实例
"""

from typing import List, Tuple
from tornado.web import Application, url
from loguru import logger

from config import config
from .base_handler import BaseHandler


def create_application() -> Application:
    """
    创建Tornado应用实例
    
    Returns:
        Tornado应用实例
    """
    # 导入路由
    from tornado.modules import get_routes
    
    # 获取路由列表
    routes = get_routes()
    
    # 应用设置
    settings = {
        "debug": config.APP_DEBUG,
        "autoreload": config.APP_DEBUG,
        "compress_response": True,
        "cookie_secret": config.APP_SECRET_KEY,
        "xsrf_cookies": True,
        "login_url": "/api/auth/login",
        "default_handler_class": NotFoundHandler,
    }
    
    # 创建应用实例
    app = Application(routes, **settings)
    
    logger.info(f"Application created with {len(routes)} routes")
    logger.info(f"Debug mode: {config.APP_DEBUG}")
    
    return app


def get_routes() -> List[Tuple]:
    """
    获取所有路由
    
    Returns:
        路由列表
    """
    # 基础健康检查路由
    routes = [
        url(r"/api/health", HealthCheckHandler, name="health_check"),
        url(r"/api/health/db", DatabaseHealthHandler, name="db_health"),
        url(r"/api/health/redis", RedisHealthHandler, name="redis_health"),
    ]
    
    # 认证模块路由
    from tornado.modules.auth.handlers import (
        RegisterHandler,
        LoginHandler,
        LogoutHandler,
        RefreshTokenHandler,
        VerifyTokenHandler,
        RequestPasswordResetHandler,
        ResetPasswordHandler,
        VerifyEmailHandler,
        ProfileHandler
    )
    
    auth_routes = [
        url(r"/api/auth/register", RegisterHandler, name="register"),
        url(r"/api/auth/login", LoginHandler, name="login"),
        url(r"/api/auth/logout", LogoutHandler, name="logout"),
        url(r"/api/auth/refresh", RefreshTokenHandler, name="refresh_token"),
        url(r"/api/auth/verify", VerifyTokenHandler, name="verify_token"),
        url(r"/api/auth/password/reset/request", RequestPasswordResetHandler, name="request_password_reset"),
        url(r"/api/auth/password/reset", ResetPasswordHandler, name="reset_password"),
        url(r"/api/auth/email/verify", VerifyEmailHandler, name="verify_email"),
        url(r"/api/auth/profile", ProfileHandler, name="profile"),
    ]
    
    routes.extend(auth_routes)
    
    # 租户模块路由
    from tornado.modules.tenant.handlers import (
        CreateTenantHandler,
        GetTenantHandler,
        UpdateTenantHandler,
        DeleteTenantHandler,
        GetTenantMembersHandler,
        InviteMemberHandler,
        AcceptInvitationHandler,
        UpdateMemberRoleHandler,
        RemoveMemberHandler,
        GetUserTenantsHandler,
        SearchTenantsHandler
    )
    
    tenant_routes = [
        url(r"/api/tenants", CreateTenantHandler, name="create_tenant"),
        url(r"/api/tenants/my", GetUserTenantsHandler, name="get_user_tenants"),
        url(r"/api/tenants/search", SearchTenantsHandler, name="search_tenants"),
        url(r"/api/tenants/([^/]+)", GetTenantHandler, name="get_tenant"),
        url(r"/api/tenants/([^/]+)", UpdateTenantHandler, name="update_tenant"),
        url(r"/api/tenants/([^/]+)", DeleteTenantHandler, name="delete_tenant"),
        url(r"/api/tenants/([^/]+)/members", GetTenantMembersHandler, name="get_tenant_members"),
        url(r"/api/tenants/([^/]+)/members/invite", InviteMemberHandler, name="invite_member"),
        url(r"/api/tenants/([^/]+)/members/([^/]+)/role", UpdateMemberRoleHandler, name="update_member_role"),
        url(r"/api/tenants/([^/]+)/members/([^/]+)", RemoveMemberHandler, name="remove_member"),
        url(r"/api/tenants/invitations/accept", AcceptInvitationHandler, name="accept_invitation"),
    ]
    
    routes.extend(tenant_routes)
    
    # 运动模块路由
    from tornado.modules.exercise import routes as exercise_routes
    
    routes.extend(exercise_routes)
    
    logger.info(f"Loaded {len(auth_routes)} auth routes, {len(tenant_routes)} tenant routes, and {len(exercise_routes)} exercise routes")
    return routes


class HealthCheckHandler(BaseHandler):
    """健康检查处理器"""
    
    async def get(self):
        """健康检查端点"""
        self.success({
            "status": "healthy",
            "service": "coach-ai",
            "version": "1.0.0",
            "environment": config.APP_ENV,
            "timestamp": self.request.request_time()
        })


class DatabaseHealthHandler(BaseHandler):
    """数据库健康检查处理器"""
    
    async def get(self):
        """数据库健康检查"""
        try:
            from database.connection import get_db_session
            import asyncio
            
            # 异步执行数据库检查
            def check_db():
                with get_db_session() as session:
                    result = session.execute("SELECT 1").scalar()
                    return result == 1
            
            # 在线程池中执行同步数据库操作
            loop = asyncio.get_event_loop()
            db_healthy = await loop.run_in_executor(None, check_db)
            
            if db_healthy:
                self.success({
                    "status": "healthy",
                    "service": "database",
                    "message": "Database connection is healthy"
                })
            else:
                self.error(
                    error_code="DATABASE_ERROR",
                    message="Database connection failed",
                    status_code=503
                )
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            self.error(
                error_code="DATABASE_ERROR",
                message="Database health check failed",
                status_code=503
            )


class RedisHealthHandler(BaseHandler):
    """Redis健康检查处理器"""
    
    async def get(self):
        """Redis健康检查"""
        try:
            from database.redis_client import get_redis_client
            
            redis_client = get_redis_client()
            redis_healthy = redis_client.ping()
            
            if redis_healthy:
                self.success({
                    "status": "healthy",
                    "service": "redis",
                    "message": "Redis connection is healthy"
                })
            else:
                self.error(
                    error_code="REDIS_ERROR",
                    message="Redis connection failed",
                    status_code=503
                )
                
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            self.error(
                error_code="REDIS_ERROR",
                message="Redis health check failed",
                status_code=503
            )


class NotFoundHandler(BaseHandler):
    """404处理器"""
    
    async def prepare(self):
        """处理未找到的路由"""
        self.set_status(404)
        self.error(
            error_code="NOT_FOUND",
            message="The requested resource was not found",
            status_code=404
        )
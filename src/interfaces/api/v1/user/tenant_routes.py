"""
租户路由配置
"""

from .tenant_handlers import (
    CreateTenantHandler,
    GetTenantHandler,
    UpdateTenantHandler,
    ListTenantsHandler,
    InviteUserHandler,
    RemoveUserHandler
)


def get_tenant_routes():
    """获取租户路由配置"""
    return [
        (r"/api/tenants", CreateTenantHandler),
        (r"/api/tenants", ListTenantsHandler),
        (r"/api/tenants/current", GetTenantHandler),
        (r"/api/tenants/([^/]+)", GetTenantHandler),
        (r"/api/tenants/([^/]+)", UpdateTenantHandler),
        (r"/api/tenants/([^/]+)/invite", InviteUserHandler),
        (r"/api/tenants/([^/]+)/users/([^/]+)", RemoveUserHandler),
    ]
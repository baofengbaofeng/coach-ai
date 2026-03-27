"""
租户模块路由配置
"""

from typing import List, Tuple
from tornado.web import url
from .handlers import (
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
    LeaveTenantHandler,
    GetTenantInvitationsHandler,
    CancelInvitationHandler,
    GetTenantStatisticsHandler
)


def get_tenant_routes() -> List[Tuple]:
    """
    获取租户模块路由
    
    Returns:
        路由列表
    """
    return [
        url(r"/api/tenants", CreateTenantHandler, name="create_tenant"),
        url(r"/api/tenants/([^/]+)", GetTenantHandler, name="get_tenant"),
        url(r"/api/tenants/([^/]+)/update", UpdateTenantHandler, name="update_tenant"),
        url(r"/api/tenants/([^/]+)/delete", DeleteTenantHandler, name="delete_tenant"),
        url(r"/api/tenants/([^/]+)/members", GetTenantMembersHandler, name="get_tenant_members"),
        url(r"/api/tenants/([^/]+)/invite", InviteMemberHandler, name="invite_member"),
        url(r"/api/tenants/([^/]+)/invitations", GetTenantInvitationsHandler, name="get_tenant_invitations"),
        url(r"/api/tenants/([^/]+)/invitations/([^/]+)/cancel", CancelInvitationHandler, name="cancel_invitation"),
        url(r"/api/tenants/([^/]+)/invitations/([^/]+)/accept", AcceptInvitationHandler, name="accept_invitation"),
        url(r"/api/tenants/([^/]+)/members/([^/]+)/role", UpdateMemberRoleHandler, name="update_member_role"),
        url(r"/api/tenants/([^/]+)/members/([^/]+)/remove", RemoveMemberHandler, name="remove_member"),
        url(r"/api/user/tenants", GetUserTenantsHandler, name="get_user_tenants"),
        url(r"/api/tenants/([^/]+)/leave", LeaveTenantHandler, name="leave_tenant"),
        url(r"/api/tenants/([^/]+)/statistics", GetTenantStatisticsHandler, name="get_tenant_statistics"),
    ]
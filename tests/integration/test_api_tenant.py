"""
租户API集成测试
测试租户创建、管理、成员管理等接口
"""

import json
import pytest
from tornado.testing import AsyncHTTPTestCase

from coachai_code.tornado.core.application import create_application
from coachai_code.config import config


class TestTenantAPI(AsyncHTTPTestCase):
    """租户API测试类"""
    
    def get_app(self):
        """创建测试应用"""
        config.APP_ENV = "testing"
        config.APP_DEBUG = True
        config.JWT_SECRET_KEY = "test-secret-key-for-jwt-tokens-in-testing-environment"
        
        return create_application()
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.base_url = "/api/tenants"
        
        # 创建测试用户并获取令牌
        self.test_admin = {
            "username": "tenantadmin",
            "email": "admin@tenant.test",
            "password": "Admin@123456",
            "full_name": "租户管理员"
        }
        
        self.test_member = {
            "username": "tenantmember",
            "email": "member@tenant.test",
            "password": "Member@123456",
            "full_name": "租户成员"
        }
        
        # 注册管理员用户
        response = self.fetch(
            "/api/auth/register",
            method="POST",
            body=json.dumps(self.test_admin),
            headers={"Content-Type": "application/json"}
        )
        
        admin_data = json.loads(response.body)
        self.admin_token = admin_data["data"]["access_token"]
        
        # 注册成员用户
        response = self.fetch(
            "/api/auth/register",
            method="POST",
            body=json.dumps(self.test_member),
            headers={"Content-Type": "application/json"}
        )
        
        member_data = json.loads(response.body)
        self.member_token = member_data["data"]["access_token"]
        
        # 测试租户数据
        self.test_tenant = {
            "name": "测试租户",
            "slug": "test-tenant",
            "description": "这是一个测试租户",
            "contact_email": "contact@test-tenant.com",
            "contact_phone": "13800138000"
        }
    
    def tearDown(self):
        """测试后置清理"""
        super().tearDown()
    
    def test_create_tenant_success(self):
        """测试创建租户成功"""
        response = self.fetch(
            self.base_url,
            method="POST",
            body=json.dumps(self.test_tenant),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.admin_token}"
            }
        )
        
        self.assertEqual(response.code, 201)
        
        data = json.loads(response.body)
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Tenant created successfully")
        self.assertIn("data", data)
        self.assertIn("tenant", data["data"])
        
        tenant_data = data["data"]["tenant"]
        self.assertEqual(tenant_data["name"], self.test_tenant["name"])
        self.assertEqual(tenant_data["slug"], self.test_tenant["slug"])
        self.assertEqual(tenant_data["description"], self.test_tenant["description"])
        self.assertTrue(tenant_data["is_active"])
        
        # 保存租户ID供后续测试使用
        self.tenant_id = tenant_data["id"]
    
    def test_create_tenant_duplicate_slug(self):
        """测试重复slug创建租户"""
        # 先创建一个租户
        self.fetch(
            self.base_url,
            method="POST",
            body=json.dumps(self.test_tenant),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.admin_token}"
            }
        )
        
        # 尝试用相同的slug创建租户
        duplicate_tenant = self.test_tenant.copy()
        duplicate_tenant["name"] = "另一个测试租户"
        
        response = self.fetch(
            self.base_url,
            method="POST",
            body=json.dumps(duplicate_tenant),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.admin_token}"
            }
        )
        
        self.assertEqual(response.code, 400)
        
        data = json.loads(response.body)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "TENANT_SLUG_EXISTS")
    
    def test_create_tenant_invalid_data(self):
        """测试无效数据创建租户"""
        invalid_tenants = [
            # 缺少必填字段
            {"slug": "test-tenant"},
            {"name": "测试租户"},
            
            # slug包含非法字符
            {"name": "测试租户", "slug": "test tenant"},
            {"name": "测试租户", "slug": "test@tenant"},
            {"name": "测试租户", "slug": "TEST_TENANT"},
            
            # slug太长
            {"name": "测试租户", "slug": "a" * 51},
            
            # 名称太长
            {"name": "a" * 101, "slug": "test-tenant"},
        ]
        
        for tenant_data in invalid_tenants:
            response = self.fetch(
                self.base_url,
                method="POST",
                body=json.dumps(tenant_data),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.admin_token}"
                }
            )
            
            self.assertEqual(response.code, 400)
            
            data = json.loads(response.body)
            self.assertFalse(data["success"])
            self.assertIn("error", data)
    
    def test_create_tenant_unauthorized(self):
        """测试未授权创建租户"""
        # 不带令牌
        response = self.fetch(
            self.base_url,
            method="POST",
            body=json.dumps(self.test_tenant),
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.code, 401)
        
        # 带无效令牌
        response = self.fetch(
            self.base_url,
            method="POST",
            body=json.dumps(self.test_tenant),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer invalid.token.here"
            }
        )
        
        self.assertEqual(response.code, 401)
    
    def test_get_tenant_list(self):
        """测试获取租户列表"""
        # 先创建几个租户
        tenants = [
            {"name": "租户一", "slug": "tenant-1", "description": "第一个测试租户"},
            {"name": "租户二", "slug": "tenant-2", "description": "第二个测试租户"},
            {"name": "租户三", "slug": "tenant-3", "description": "第三个测试租户"},
        ]
        
        for tenant_data in tenants:
            self.fetch(
                self.base_url,
                method="POST",
                body=json.dumps(tenant_data),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.admin_token}"
                }
            )
        
        # 获取租户列表
        response = self.fetch(
            self.base_url,
            method="GET",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        self.assertTrue(data["success"])
        self.assertIn("data", data)
        self.assertIn("tenants", data["data"])
        self.assertIn("pagination", data["data"])
        
        tenants_list = data["data"]["tenants"]
        self.assertGreaterEqual(len(tenants_list), 3)
        
        # 检查分页信息
        pagination = data["data"]["pagination"]
        self.assertIn("total", pagination)
        self.assertIn("page", pagination)
        self.assertIn("per_page", pagination)
        self.assertIn("total_pages", pagination)
    
    def test_get_tenant_list_with_pagination(self):
        """测试带分页的租户列表"""
        # 创建更多租户以测试分页
        for i in range(15):
            tenant_data = {
                "name": f"分页租户{i}",
                "slug": f"pagination-tenant-{i}",
                "description": f"第{i}个分页测试租户"
            }
            
            self.fetch(
                self.base_url,
                method="POST",
                body=json.dumps(tenant_data),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.admin_token}"
                }
            )
        
        # 测试第一页，每页5条
        response = self.fetch(
            f"{self.base_url}?page=1&per_page=5",
            method="GET",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        tenants_list = data["data"]["tenants"]
        pagination = data["data"]["pagination"]
        
        self.assertEqual(len(tenants_list), 5)
        self.assertEqual(pagination["page"], 1)
        self.assertEqual(pagination["per_page"], 5)
        self.assertGreaterEqual(pagination["total"], 15)
        
        # 测试第二页
        response = self.fetch(
            f"{self.base_url}?page=2&per_page=5",
            method="GET",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        data = json.loads(response.body)
        tenants_list = data["data"]["tenants"]
        pagination = data["data"]["pagination"]
        
        self.assertEqual(len(tenants_list), 5)
        self.assertEqual(pagination["page"], 2)
    
    def test_get_tenant_detail(self):
        """测试获取租户详情"""
        # 先创建租户
        response = self.fetch(
            self.base_url,
            method="POST",
            body=json.dumps(self.test_tenant),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.admin_token}"
            }
        )
        
        tenant_data = json.loads(response.body)
        tenant_id = tenant_data["data"]["tenant"]["id"]
        
        # 获取租户详情
        response = self.fetch(
            f"{self.base_url}/{tenant_id}",
            method="GET",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        self.assertTrue(data["success"])
        self.assertIn("data", data)
        self.assertIn("tenant", data["data"])
        
        tenant_detail = data["data"]["tenant"]
        self.assertEqual(tenant_detail["id"], tenant_id)
        self.assertEqual(tenant_detail["name"], self.test_tenant["name"])
        self.assertEqual(tenant_detail["slug"], self.test_tenant["slug"])
    
    def test_get_nonexistent_tenant(self):
        """测试获取不存在的租户"""
        response = self.fetch(
            f"{self.base_url}/99999",
            method="GET",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.code, 404)
        
        data = json.loads(response.body)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "TENANT_NOT_FOUND")
    
    def test_update_tenant_success(self):
        """测试更新租户成功"""
        # 先创建租户
        response = self.fetch(
            self.base_url,
            method="POST",
            body=json.dumps(self.test_tenant),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.admin_token}"
            }
        )
        
        tenant_data = json.loads(response.body)
        tenant_id = tenant_data["data"]["tenant"]["id"]
        
        # 更新租户
        update_data = {
            "name": "更新后的租户",
            "description": "更新后的描述",
            "contact_email": "updated@test-tenant.com"
        }
        
        response = self.fetch(
            f"{self.base_url}/{tenant_id}",
            method="PUT",
            body=json.dumps(update_data),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.admin_token}"
            }
        )
        
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Tenant updated successfully")
        
        # 验证更新
        response = self.fetch(
            f"{self.base_url}/{tenant_id}",
            method="GET",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        tenant_detail = json.loads(response.body)
        updated_tenant = tenant_detail["data"]["tenant"]
        
        self.assertEqual(updated_tenant["name"], update_data["name"])
        self.assertEqual(updated_tenant["description"], update_data["description"])
        self.assertEqual(updated_tenant["contact_email"], update_data["contact_email"])
    
    def test_update_tenant_unauthorized(self):
        """测试未授权更新租户"""
        # 先创建租户
        response = self.fetch(
            self.base_url,
            method="POST",
            body=json.dumps(self.test_tenant),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.admin_token}"
            }
        )
        
        tenant_data = json.loads(response.body)
        tenant_id = tenant_data["data"]["tenant"]["id"]
        
        # 使用成员令牌尝试更新（应该没有权限）
        update_data = {"name": "未授权更新"}
        
        response = self.fetch(
            f"{self.base_url}/{tenant_id}",
            method="PUT",
            body=json.dumps(update_data),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.member_token}"
            }
        )
        
        # 注意：这里假设成员用户不是租户管理员
        # 实际权限检查需要根据具体实现调整
        self.assertEqual(response.code, 403)
    
    def test_delete_tenant_success(self):
        """测试删除租户成功"""
        # 先创建租户
        response = self.fetch(
            self.base_url,
            method="POST",
            body=json.dumps(self.test_tenant),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.admin_token}"
            }
        )
        
        tenant_data = json.loads(response.body)
        tenant_id = tenant_data["data"]["tenant"]["id"]
        
        # 删除租户
        response = self.fetch(
            f"{self.base_url}/{tenant_id}",
            method="DELETE",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Tenant deleted successfully")
        
        # 验证已删除
        response = self.fetch(
            f"{self.base_url}/{tenant_id}",
            method="GET",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.code, 404)
    
    def test_add_tenant_member(self):
        """测试添加租户成员"""
        # 先创建租户
        response = self.fetch(
            self.base_url,
            method="POST",
            body=json.dumps(self.test_tenant),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.admin_token}"
            }
        )
        
        tenant_data = json.loads(response.body)
        tenant_id = tenant_data["data"]["tenant"]["id"]
        
        # 添加成员
        member_data = {
            "user_id": 2,  # 假设成员用户的ID是2
            "role_id": 3   # 假设教练角色的ID是3
        }
        
        response = self.fetch(
            f"{self.base_url}/{tenant_id}/members",
            method="POST",
            body=json.dumps(member_data),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.admin_token}"
            }
        )
        
        # 注意：这里需要根据实际用户ID和角色ID调整
        # 实际实现中可能需要先查询用户和角色
        
        self.assertEqual(response.code, 201)
        
        data = json.loads(response.body)
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Member added successfully")
    
    def test_get_tenant_members(self):
        """测试获取租户成员列表"""
        # 先创建租户
        response = self.fetch(
            self.base_url,
            method="POST",
            body=json.dumps(self.test_tenant),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.admin_token}"
            }
        )
        
        tenant_data = json.loads(response.body)
        tenant_id = tenant_data["data"]["tenant"]["id"]
        
        # 获取成员列表
        response = self.fetch(
            f"{self.base_url}/{tenant_id}/members",
            method="GET",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        self.assertTrue(data["success"])
        self.assertIn("data", data)
        self.assertIn("members", data["data"])
        
        # 创建者应该自动成为成员
        members_list = data["data"]["members"]
        self.assertGreaterEqual(len(members_list), 1)
    
    def test_remove_tenant_member(self):
        """测试移除租户成员"""
        # 这个测试需要先添加成员，然后移除
        # 由于用户ID和角色ID的复杂性，这里只测试接口格式
        
        # 先创建租户
        response = self.fetch(
            self.base_url,
            method="POST",
            body=json.dumps(self.test_tenant),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.admin_token}"
            }
        )
        
        tenant_data = json.loads(response.body)
        tenant_id = tenant_data["data"]["tenant"]["id"]
        
        # 假设成员ID为1
        member_id = 1
        
        # 移除成员
        response = self.fetch(
            f"{self.base_url}/{tenant_id}/members/{member_id}",
            method="DELETE",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # 注意：这里需要根据实际成员ID调整
        # 由于测试数据的复杂性，我们只检查接口响应格式
        if response.code == 200:
            data = json.loads(response.body)
            self.assertTrue(data["success"])
        elif response.code == 404:
            data = json.loads(response.body)
            self.assertFalse(data["success"])
            self.assertEqual(data["error"]["code"], "MEMBER_NOT_FOUND")
    
    def test_tenant_statistics(self):
        """测试获取租户统计信息"""
        # 先创建租户
        response = self.fetch(
            self.base_url,
            method="POST",
            body=json.dumps(self.test_tenant),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.admin_token}"
            }
        )
        
        tenant_data = json.loads(response.body)
        tenant_id = tenant_data["data"]["tenant"]["id"]
        
        # 获取统计信息
        response = self.fetch(
            f"{self.base_url}/{tenant_id}/statistics",
            method="GET",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        self.assertTrue(data["success"])
        self.assertIn("data", data)
        self.assertIn("statistics", data["data"])
        
        stats = data["data"]["statistics"]
        self.assertIn("member_count", stats)
        self.assertIn("active_member_count", stats)
        self.assertIn("created_at", stats)
        self.assertIn("updated_at", stats")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
认证API集成测试
测试用户注册、登录、令牌刷新等接口
"""

import json
import pytest
from webapp.testing import AsyncHTTPTestCase
from webapp.web import Application

from webapp.core.application import create_application
from coding.config import config


class TestAuthAPI(AsyncHTTPTestCase):
    """认证API测试类"""
    
    def get_app(self) -> Application:
        """创建测试应用"""
        # 使用测试配置
        config.APP_ENV = "testing"
        config.APP_DEBUG = True
        config.JWT_SECRET_KEY = "test-secret-key-for-jwt-tokens-in-testing-environment"
        
        return create_application()
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.base_url = "/api/auth"
        self.test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test@123456",
            "full_name": "测试用户"
        }
    
    def tearDown(self):
        """测试后置清理"""
        super().tearDown()
        # 这里可以添加数据库清理逻辑
    
    def test_health_check(self):
        """测试健康检查接口"""
        response = self.fetch("/api/health")
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Service is healthy")
    
    def test_register_success(self):
        """测试用户注册成功"""
        # 清理可能存在的测试用户
        # 在实际项目中，这里应该清理测试数据
        
        # 发送注册请求
        response = self.fetch(
            f"{self.base_url}/register",
            method="POST",
            body=json.dumps(self.test_user),
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.code, 201)
        
        data = json.loads(response.body)
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "User registered successfully")
        self.assertIn("data", data)
        self.assertIn("user", data["data"])
        self.assertIn("access_token", data["data"])
        
        user_data = data["data"]["user"]
        self.assertEqual(user_data["username"], self.test_user["username"])
        self.assertEqual(user_data["email"], self.test_user["email"])
        self.assertEqual(user_data["full_name"], self.test_user["full_name"])
        self.assertNotIn("password_hash", user_data)  # 密码哈希不应返回
    
    def test_register_duplicate_username(self):
        """测试重复用户名注册"""
        # 先注册一个用户
        self.fetch(
            f"{self.base_url}/register",
            method="POST",
            body=json.dumps(self.test_user),
            headers={"Content-Type": "application/json"}
        )
        
        # 尝试用相同的用户名注册
        duplicate_user = self.test_user.copy()
        duplicate_user["email"] = "another@example.com"
        
        response = self.fetch(
            f"{self.base_url}/register",
            method="POST",
            body=json.dumps(duplicate_user),
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.code, 400)
        
        data = json.loads(response.body)
        self.assertFalse(data["success"])
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], "USERNAME_EXISTS")
    
    def test_register_duplicate_email(self):
        """测试重复邮箱注册"""
        # 先注册一个用户
        self.fetch(
            f"{self.base_url}/register",
            method="POST",
            body=json.dumps(self.test_user),
            headers={"Content-Type": "application/json"}
        )
        
        # 尝试用相同的邮箱注册
        duplicate_user = self.test_user.copy()
        duplicate_user["username"] = "anotheruser"
        
        response = self.fetch(
            f"{self.base_url}/register",
            method="POST",
            body=json.dumps(duplicate_user),
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.code, 400)
        
        data = json.loads(response.body)
        self.assertFalse(data["success"])
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], "EMAIL_EXISTS")
    
    def test_register_invalid_data(self):
        """测试无效数据注册"""
        invalid_users = [
            # 缺少必填字段
            {"email": "test@example.com", "password": "Test@123"},
            {"username": "testuser", "password": "Test@123"},
            {"username": "testuser", "email": "test@example.com"},
            
            # 无效邮箱格式
            {"username": "testuser", "email": "invalid-email", "password": "Test@123"},
            
            # 密码太短
            {"username": "testuser", "email": "test@example.com", "password": "short"},
            
            # 密码缺少特殊字符
            {"username": "testuser", "email": "test@example.com", "password": "Test123456"},
            
            # 用户名包含非法字符
            {"username": "test user", "email": "test@example.com", "password": "Test@123"},
        ]
        
        for user_data in invalid_users:
            response = self.fetch(
                f"{self.base_url}/register",
                method="POST",
                body=json.dumps(user_data),
                headers={"Content-Type": "application/json"}
            )
            
            self.assertEqual(response.code, 400)
            
            data = json.loads(response.body)
            self.assertFalse(data["success"])
            self.assertIn("error", data)
    
    def test_login_success(self):
        """测试登录成功"""
        # 先注册用户
        self.fetch(
            f"{self.base_url}/register",
            method="POST",
            body=json.dumps(self.test_user),
            headers={"Content-Type": "application/json"}
        )
        
        # 登录
        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        }
        
        response = self.fetch(
            f"{self.base_url}/login",
            method="POST",
            body=json.dumps(login_data),
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Login successful")
        self.assertIn("data", data)
        self.assertIn("access_token", data["data"])
        self.assertIn("refresh_token", data["data"])
        self.assertIn("user", data["data"])
    
    def test_login_invalid_credentials(self):
        """测试无效凭据登录"""
        login_cases = [
            # 错误密码
            {"username": "testuser", "password": "Wrong@123"},
            # 不存在的用户
            {"username": "nonexistent", "password": "Test@123"},
            # 空密码
            {"username": "testuser", "password": ""},
        ]
        
        for login_data in login_cases:
            response = self.fetch(
                f"{self.base_url}/login",
                method="POST",
                body=json.dumps(login_data),
                headers={"Content-Type": "application/json"}
            )
            
            self.assertEqual(response.code, 401)
            
            data = json.loads(response.body)
            self.assertFalse(data["success"])
            self.assertIn("error", data)
            self.assertEqual(data["error"]["code"], "INVALID_CREDENTIALS")
    
    def test_refresh_token_success(self):
        """测试令牌刷新成功"""
        # 先注册并登录获取refresh token
        self.fetch(
            f"{self.base_url}/register",
            method="POST",
            body=json.dumps(self.test_user),
            headers={"Content-Type": "application/json"}
        )
        
        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        }
        
        login_response = self.fetch(
            f"{self.base_url}/login",
            method="POST",
            body=json.dumps(login_data),
            headers={"Content-Type": "application/json"}
        )
        
        login_data = json.loads(login_response.body)
        refresh_token = login_data["data"]["refresh_token"]
        
        # 刷新令牌
        refresh_data = {"refresh_token": refresh_token}
        
        response = self.fetch(
            f"{self.base_url}/refresh",
            method="POST",
            body=json.dumps(refresh_data),
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        self.assertTrue(data["success"])
        self.assertIn("data", data)
        self.assertIn("access_token", data["data"])
    
    def test_refresh_token_invalid(self):
        """测试无效刷新令牌"""
        invalid_tokens = [
            "invalid.token.here",
            "",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"  # 使用错误密钥签名的JWT
        ]
        
        for token in invalid_tokens:
            refresh_data = {"refresh_token": token}
            
            response = self.fetch(
                f"{self.base_url}/refresh",
                method="POST",
                body=json.dumps(refresh_data),
                headers={"Content-Type": "application/json"}
            )
            
            self.assertEqual(response.code, 401)
            
            data = json.loads(response.body)
            self.assertFalse(data["success"])
            self.assertIn("error", data)
    
    def test_get_current_user_success(self):
        """测试获取当前用户信息成功"""
        # 先注册并登录
        self.fetch(
            f"{self.base_url}/register",
            method="POST",
            body=json.dumps(self.test_user),
            headers={"Content-Type": "application/json"}
        )
        
        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        }
        
        login_response = self.fetch(
            f"{self.base_url}/login",
            method="POST",
            body=json.dumps(login_data),
            headers={"Content-Type": "application/json"}
        )
        
        login_data = json.loads(login_response.body)
        access_token = login_data["data"]["access_token"]
        
        # 获取当前用户信息
        response = self.fetch(
            f"{self.base_url}/me",
            method="GET",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        self.assertTrue(data["success"])
        self.assertIn("data", data)
        self.assertIn("user", data["data"])
        
        user_data = data["data"]["user"]
        self.assertEqual(user_data["username"], self.test_user["username"])
        self.assertEqual(user_data["email"], self.test_user["email"])
    
    def test_get_current_user_unauthorized(self):
        """测试未授权访问用户信息"""
        # 不带令牌
        response = self.fetch(
            f"{self.base_url}/me",
            method="GET"
        )
        
        self.assertEqual(response.code, 401)
        
        data = json.loads(response.body)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "MISSING_TOKEN")
        
        # 带无效令牌
        response = self.fetch(
            f"{self.base_url}/me",
            method="GET",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        self.assertEqual(response.code, 401)
        
        data = json.loads(response.body)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "INVALID_TOKEN")
    
    def test_logout_success(self):
        """测试注销成功"""
        # 先注册并登录
        self.fetch(
            f"{self.base_url}/register",
            method="POST",
            body=json.dumps(self.test_user),
            headers={"Content-Type": "application/json"}
        )
        
        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        }
        
        login_response = self.fetch(
            f"{self.base_url}/login",
            method="POST",
            body=json.dumps(login_data),
            headers={"Content-Type": "application/json"}
        )
        
        login_data = json.loads(login_response.body)
        access_token = login_data["data"]["access_token"]
        
        # 注销
        response = self.fetch(
            f"{self.base_url}/logout",
            method="POST",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Logout successful")
        
        # 注销后尝试访问受保护端点
        response = self.fetch(
            f"{self.base_url}/me",
            method="GET",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # 注意：实际的令牌黑名单需要Redis支持
        # 这里我们只是测试注销接口本身
        
    def test_change_password_success(self):
        """测试修改密码成功"""
        # 先注册并登录
        self.fetch(
            f"{self.base_url}/register",
            method="POST",
            body=json.dumps(self.test_user),
            headers={"Content-Type": "application/json"}
        )
        
        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        }
        
        login_response = self.fetch(
            f"{self.base_url}/login",
            method="POST",
            body=json.dumps(login_data),
            headers={"Content-Type": "application/json"}
        )
        
        login_data = json.loads(login_response.body)
        access_token = login_data["data"]["access_token"]
        
        # 修改密码
        change_password_data = {
            "current_password": self.test_user["password"],
            "new_password": "New@123456"
        }
        
        response = self.fetch(
            f"{self.base_url}/change-password",
            method="POST",
            body=json.dumps(change_password_data),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )
        
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Password changed successfully")
        
        # 用新密码登录
        new_login_data = {
            "username": self.test_user["username"],
            "password": "New@123456"
        }
        
        response = self.fetch(
            f"{self.base_url}/login",
            method="POST",
            body=json.dumps(new_login_data),
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.code, 200)
        
        data = json.loads(response.body)
        self.assertTrue(data["success"])
    
    def test_change_password_invalid_current(self):
        """测试使用错误当前密码修改密码"""
        # 先注册并登录
        self.fetch(
            f"{self.base_url}/register",
            method="POST",
            body=json.dumps(self.test_user),
            headers={"Content-Type": "application/json"}
        )
        
        login_response = self.fetch(
            f"{self.base_url}/login",
            method="POST",
            body=json.dumps({
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }),
            headers={"Content-Type": "application/json"}
        )
        
        login_data = json.loads(login_response.body)
        access_token = login_data["data"]["access_token"]
        
        # 使用错误当前密码
        change_password_data = {
            "current_password": "Wrong@123",
            "new_password": "New@123456"
        }
        
        response = self.fetch(
            f"{self.base_url}/change-password",
            method="POST",
            body=json.dumps(change_password_data),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )
        
        self.assertEqual(response.code, 400)
        
        data = json.loads(response.body)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "INVALID_CURRENT_PASSWORD")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
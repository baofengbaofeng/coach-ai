"""
框架测试脚本
验证基础框架功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from tornado.core.exceptions import ValidationError, AuthenticationError
from tornado.utils.password_utils import PasswordUtils
from tornado.utils.jwt_utils import JWTUtils


def test_config():
    """测试配置加载"""
    print("🔧 测试配置加载...")
    
    assert config.APP_ENV == "development", f"APP_ENV应为development，实际为{config.APP_ENV}"
    assert config.APP_PORT == 8888, f"APP_PORT应为8888，实际为{config.APP_PORT}"
    assert config.DB_HOST == "localhost", f"DB_HOST应为localhost，实际为{config.DB_HOST}"
    
    print("✅ 配置加载测试通过")
    return True


def test_exceptions():
    """测试异常类"""
    print("🔧 测试异常类...")
    
    # 测试ValidationError
    try:
        raise ValidationError("测试验证错误", {"field": "username"})
    except ValidationError as e:
        assert e.status_code == 400
        assert e.error_code == "VALIDATION_ERROR"
        assert e.message == "测试验证错误"
        assert e.details == {"field": "username"}
    
    # 测试AuthenticationError
    try:
        raise AuthenticationError("测试认证错误")
    except AuthenticationError as e:
        assert e.status_code == 401
        assert e.error_code == "AUTHENTICATION_ERROR"
    
    print("✅ 异常类测试通过")
    return True


def test_password_utils():
    """测试密码工具"""
    print("🔧 测试密码工具...")
    
    # 测试密码哈希和验证
    password = "TestPassword123!"
    hashed = PasswordUtils.hash_password(password)
    
    assert PasswordUtils.verify_password(password, hashed), "密码验证失败"
    assert not PasswordUtils.verify_password("WrongPassword", hashed), "错误密码不应通过验证"
    
    # 测试密码强度验证
    strength_result = PasswordUtils.validate_password_strength(password)
    assert strength_result["is_valid"], "密码强度验证失败"
    
    # 测试随机密码生成
    random_password = PasswordUtils.generate_random_password()
    assert len(random_password) == 12, "随机密码长度不正确"
    
    print("✅ 密码工具测试通过")
    return True


def test_jwt_utils():
    """测试JWT工具"""
    print("🔧 测试JWT工具...")
    
    # 测试数据
    user_data = {
        "user_id": "123",
        "username": "testuser",
        "tenant_id": "default"
    }
    
    # 测试创建访问令牌
    access_token = JWTUtils.create_access_token(user_data)
    assert access_token, "访问令牌创建失败"
    
    # 测试验证令牌
    payload = JWTUtils.verify_token(access_token)
    assert payload, "令牌验证失败"
    assert payload["user_id"] == "123", "用户ID不匹配"
    assert payload["type"] == "access", "令牌类型不正确"
    
    # 测试创建刷新令牌
    refresh_token = JWTUtils.create_refresh_token(user_data)
    assert refresh_token, "刷新令牌创建失败"
    
    # 测试刷新令牌验证
    refresh_payload = JWTUtils.verify_token(refresh_token, "refresh")
    assert refresh_payload, "刷新令牌验证失败"
    assert refresh_payload["type"] == "refresh", "刷新令牌类型不正确"
    
    # 测试令牌刷新
    new_access_token = JWTUtils.refresh_access_token(refresh_token)
    assert new_access_token, "令牌刷新失败"
    
    print("✅ JWT工具测试通过")
    return True


def main():
    """主测试函数"""
    print("🚀 开始框架测试...")
    print("=" * 50)
    
    tests = [
        test_config,
        test_exceptions,
        test_password_utils,
        test_jwt_utils,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} 测试失败: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"📊 测试结果: 通过 {passed}/{len(tests)}，失败 {failed}/{len(tests)}")
    
    if failed == 0:
        print("🎉 所有测试通过！框架基础功能正常。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查框架实现。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
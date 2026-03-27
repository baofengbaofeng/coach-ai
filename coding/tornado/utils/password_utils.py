"""
密码工具模块
处理密码哈希和验证
"""

import bcrypt
from loguru import logger


class PasswordUtils:
    """密码工具类"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        哈希密码
        
        Args:
            password: 明文密码
            
        Returns:
            哈希后的密码字符串
        """
        try:
            # 生成盐值并哈希密码
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed_password.decode('utf-8')
        except Exception as e:
            logger.error(f"Password hashing error: {e}")
            raise
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        验证密码
        
        Args:
            plain_password: 明文密码
            hashed_password: 哈希后的密码
            
        Returns:
            密码是否匹配
        """
        try:
            # 验证密码
            is_valid = bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
            return is_valid
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        """
        生成随机密码
        
        Args:
            length: 密码长度
            
        Returns:
            随机密码字符串
        """
        import secrets
        import string
        
        # 定义字符集
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        
        # 生成随机密码
        password = ''.join(secrets.choice(characters) for _ in range(length))
        
        return password
    
    @staticmethod
    def validate_password_strength(password: str) -> dict:
        """
        验证密码强度
        
        Args:
            password: 密码字符串
            
        Returns:
            包含验证结果的字典
        """
        import re
        
        result = {
            "is_valid": True,
            "errors": [],
            "score": 0
        }
        
        # 检查长度
        if len(password) < 8:
            result["is_valid"] = False
            result["errors"].append("Password must be at least 8 characters long")
        elif len(password) >= 12:
            result["score"] += 2
        
        # 检查大写字母
        if not re.search(r'[A-Z]', password):
            result["is_valid"] = False
            result["errors"].append("Password must contain at least one uppercase letter")
        else:
            result["score"] += 1
        
        # 检查小写字母
        if not re.search(r'[a-z]', password):
            result["is_valid"] = False
            result["errors"].append("Password must contain at least one lowercase letter")
        else:
            result["score"] += 1
        
        # 检查数字
        if not re.search(r'\d', password):
            result["is_valid"] = False
            result["errors"].append("Password must contain at least one digit")
        else:
            result["score"] += 1
        
        # 检查特殊字符
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result["errors"].append("Consider adding special characters for better security")
        else:
            result["score"] += 2
        
        # 评估密码强度
        if result["score"] >= 5:
            result["strength"] = "strong"
        elif result["score"] >= 3:
            result["strength"] = "medium"
        else:
            result["strength"] = "weak"
        
        return result
    
    @staticmethod
    def generate_password_reset_token() -> str:
        """
        生成密码重置令牌
        
        Returns:
            密码重置令牌字符串
        """
        import secrets
        import string
        
        # 生成安全的随机令牌
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        return token
    
    @staticmethod
    def create_password_reset_link(base_url: str, token: str) -> str:
        """
        创建密码重置链接
        
        Args:
            base_url: 基础URL
            token: 重置令牌
            
        Returns:
            完整的密码重置链接
        """
        return f"{base_url}/reset-password?token={token}"
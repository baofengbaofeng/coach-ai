"""
用户领域值对象
包含Email、Password等不可变的值对象
"""

import re
import hashlib
import bcrypt
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from ..base import ValueObject


@dataclass(frozen=True)
class Email(ValueObject):
    """邮箱值对象"""
    
    value: str
    
    def __post_init__(self):
        """验证邮箱格式"""
        if not self.is_valid():
            raise ValueError(f"无效的邮箱地址: {self.value}")
    
    def is_valid(self) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, self.value))
    
    def get_domain(self) -> str:
        """获取邮箱域名"""
        return self.value.split('@')[1]
    
    def get_local_part(self) -> str:
        """获取邮箱本地部分"""
        return self.value.split('@')[0]
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Password(ValueObject):
    """密码值对象"""
    
    hashed_value: str  # 存储哈希值，不存储明文
    
    @classmethod
    def create(cls, plain_password: str) -> 'Password':
        """
        从明文密码创建
        
        Args:
            plain_password: 明文密码
            
        Returns:
            密码值对象
        """
        if not plain_password or len(plain_password) < 8:
            raise ValueError("密码长度必须至少8个字符")
        
        # 使用bcrypt哈希密码
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
        return cls(hashed_value=hashed.decode('utf-8'))
    
    def verify(self, plain_password: str) -> bool:
        """
        验证密码
        
        Args:
            plain_password: 要验证的明文密码
            
        Returns:
            是否匹配
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                self.hashed_value.encode('utf-8')
            )
        except (ValueError, TypeError):
            return False
    
    def is_strong(self) -> bool:
        """
        检查密码强度
        
        Returns:
            是否强密码
        """
        # 这里可以添加更复杂的密码强度检查
        return len(self.hashed_value) >= 60  # bcrypt哈希长度
    
    def __str__(self) -> str:
        return "***"  # 不暴露哈希值


@dataclass(frozen=True)
class PhoneNumber(ValueObject):
    """手机号值对象"""
    
    value: str
    country_code: str = "+86"  # 默认中国
    
    def __post_init__(self):
        """验证手机号格式"""
        if not self.is_valid():
            raise ValueError(f"无效的手机号: {self.value}")
    
    def is_valid(self) -> bool:
        """验证手机号格式"""
        # 简单的中国手机号验证
        if self.country_code == "+86":
            pattern = r'^1[3-9]\d{9}$'
            return bool(re.match(pattern, self.value))
        # 其他国家的验证可以在这里扩展
        return True
    
    def get_full_number(self) -> str:
        """获取完整号码（包含国家代码）"""
        return f"{self.country_code}{self.value}"
    
    def __str__(self) -> str:
        return self.get_full_number()


@dataclass(frozen=True)
class UserStatus(ValueObject):
    """用户状态值对象"""
    
    value: str
    
    VALID_STATUSES = {'active', 'inactive', 'blocked', 'pending'}
    
    def __post_init__(self):
        """验证状态值"""
        if self.value not in self.VALID_STATUSES:
            raise ValueError(f"无效的用户状态: {self.value}")
    
    def is_active(self) -> bool:
        """是否活跃"""
        return self.value == 'active'
    
    def is_blocked(self) -> bool:
        """是否被锁定"""
        return self.value == 'blocked'
    
    def can_login(self) -> bool:
        """是否可以登录"""
        return self.value in {'active', 'pending'}
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class VerificationStatus(ValueObject):
    """验证状态值对象"""
    
    email_verified: bool = False
    phone_verified: bool = False
    verified_at: Optional[datetime] = None
    
    def is_fully_verified(self) -> bool:
        """是否完全验证"""
        return self.email_verified and self.phone_verified
    
    def verify_email(self) -> 'VerificationStatus':
        """验证邮箱"""
        return VerificationStatus(
            email_verified=True,
            phone_verified=self.phone_verified,
            verified_at=datetime.now()
        )
    
    def verify_phone(self) -> 'VerificationStatus':
        """验证手机"""
        return VerificationStatus(
            email_verified=self.email_verified,
            phone_verified=True,
            verified_at=datetime.now()
        )
    
    def __str__(self) -> str:
        status = []
        if self.email_verified:
            status.append("邮箱已验证")
        if self.phone_verified:
            status.append("手机已验证")
        return " | ".join(status) if status else "未验证"
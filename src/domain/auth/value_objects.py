"""
认证领域值对象
包含TokenType、AuthMethod等不可变的值对象
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta
from ..base import ValueObject


@dataclass(frozen=True)
class TokenType(ValueObject):
    """令牌类型值对象"""
    
    value: str
    
    VALID_TYPES = {'access', 'refresh', 'reset', 'verify', 'api'}
    
    def __post_init__(self):
        """验证令牌类型"""
        if self.value not in self.VALID_TYPES:
            raise ValueError(f"无效的令牌类型: {self.value}")
    
    def is_access_token(self) -> bool:
        """是否为访问令牌"""
        return self.value == 'access'
    
    def is_refresh_token(self) -> bool:
        """是否为刷新令牌"""
        return self.value == 'refresh'
    
    def is_reset_token(self) -> bool:
        """是否为重置令牌"""
        return self.value == 'reset'
    
    def get_expiry_duration(self) -> timedelta:
        """获取过期时长"""
        durations = {
            'access': timedelta(minutes=30),
            'refresh': timedelta(days=7),
            'reset': timedelta(hours=1),
            'verify': timedelta(hours=24),
            'api': timedelta(days=30),
        }
        return durations.get(self.value, timedelta(minutes=30))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class AuthMethod(ValueObject):
    """认证方法值对象"""
    
    value: str
    
    VALID_METHODS = {
        'password',      # 密码认证
        'token',         # 令牌认证
        'social',        # 社交登录
        'mfa',          # 多因素认证
        'biometric',     # 生物识别
        'sso',          # 单点登录
    }
    
    def __post_init__(self):
        """验证认证方法"""
        if self.value not in self.VALID_METHODS:
            raise ValueError(f"无效的认证方法: {self.value}")
    
    def requires_password(self) -> bool:
        """是否需要密码"""
        return self.value == 'password'
    
    def requires_mfa(self) -> bool:
        """是否需要MFA"""
        return self.value == 'mfa'
    
    def is_social_login(self) -> bool:
        """是否为社交登录"""
        return self.value == 'social'
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SessionStatus(ValueObject):
    """会话状态值对象"""
    
    value: str
    
    VALID_STATUSES = {
        'active',      # 活跃
        'inactive',    # 不活跃
        'expired',     # 已过期
        'revoked',     # 已撤销
        'suspended',   # 已暂停
    }
    
    def __post_init__(self):
        """验证会话状态"""
        if self.value not in self.VALID_STATUSES:
            raise ValueError(f"无效的会话状态: {self.value}")
    
    def is_active(self) -> bool:
        """是否活跃"""
        return self.value == 'active'
    
    def can_be_used(self) -> bool:
        """是否可以使用"""
        return self.value in {'active', 'inactive'}
    
    def is_terminated(self) -> bool:
        """是否已终止"""
        return self.value in {'expired', 'revoked', 'suspended'}
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class AuthResult(ValueObject):
    """认证结果值对象"""
    
    success: bool
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    token: Optional[str] = None
    message: Optional[str] = None
    requires_mfa: bool = False
    mfa_challenge: Optional[str] = None
    
    def __str__(self) -> str:
        if self.success:
            return f"认证成功: 用户 {self.user_id}"
        else:
            return f"认证失败: {self.message}"


@dataclass(frozen=True)
class IPAddress(ValueObject):
    """IP地址值对象"""
    
    value: str
    
    def __post_init__(self):
        """验证IP地址格式"""
        if not self.is_valid():
            raise ValueError(f"无效的IP地址: {self.value}")
    
    def is_valid(self) -> bool:
        """验证IP地址格式"""
        import ipaddress
        try:
            ipaddress.ip_address(self.value)
            return True
        except ValueError:
            return False
    
    def is_ipv4(self) -> bool:
        """是否为IPv4地址"""
        import ipaddress
        try:
            return isinstance(ipaddress.ip_address(self.value), ipaddress.IPv4Address)
        except ValueError:
            return False
    
    def is_ipv6(self) -> bool:
        """是否为IPv6地址"""
        import ipaddress
        try:
            return isinstance(ipaddress.ip_address(self.value), ipaddress.IPv6Address)
        except ValueError:
            return False
    
    def get_country_code(self) -> Optional[str]:
        """获取国家代码（简化实现）"""
        # 在实际应用中，这里可以调用IP地理位置服务
        # 这里返回一个简化的实现
        return None
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class UserAgent(ValueObject):
    """用户代理值对象"""
    
    value: str
    
    def get_browser(self) -> Optional[str]:
        """获取浏览器信息"""
        # 简化的浏览器检测
        ua_lower = self.value.lower()
        
        if 'chrome' in ua_lower and 'chromium' not in ua_lower:
            return 'Chrome'
        elif 'firefox' in ua_lower:
            return 'Firefox'
        elif 'safari' in ua_lower and 'chrome' not in ua_lower:
            return 'Safari'
        elif 'edge' in ua_lower:
            return 'Edge'
        elif 'opera' in ua_lower:
            return 'Opera'
        elif 'msie' in ua_lower or 'trident' in ua_lower:
            return 'Internet Explorer'
        
        return None
    
    def get_os(self) -> Optional[str]:
        """获取操作系统信息"""
        ua_lower = self.value.lower()
        
        if 'windows' in ua_lower:
            return 'Windows'
        elif 'mac os' in ua_lower:
            return 'macOS'
        elif 'linux' in ua_lower:
            return 'Linux'
        elif 'android' in ua_lower:
            return 'Android'
        elif 'iphone' in ua_lower or 'ipad' in ua_lower:
            return 'iOS'
        
        return None
    
    def is_mobile(self) -> bool:
        """是否为移动设备"""
        ua_lower = self.value.lower()
        mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'windows phone']
        return any(keyword in ua_lower for keyword in mobile_keywords)
    
    def is_bot(self) -> bool:
        """是否为爬虫/机器人"""
        ua_lower = self.value.lower()
        bot_keywords = ['bot', 'crawler', 'spider', 'scraper']
        return any(keyword in ua_lower for keyword in bot_keywords)
    
    def __str__(self) -> str:
        return self.value[:100]  # 限制长度
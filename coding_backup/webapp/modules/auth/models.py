"""
认证模型
定义认证相关的数据模型和验证规则
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator


class RegisterRequest(BaseModel):
    """
    注册请求模型
    """
    username: str
    email: EmailStr
    password: str
    display_name: Optional[str] = None
    phone: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        """验证用户名格式"""
        # 只允许字母、数字、下划线和连字符
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores and hyphens')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """验证手机号格式"""
        if v is not None:
            # 简单的手机号验证，可根据需要调整
            if not v.replace('+', '').replace(' ', '').isdigit():
                raise ValueError('Phone number must contain only digits, plus sign and spaces')
            if len(v.replace('+', '').replace(' ', '')) < 10:
                raise ValueError('Phone number is too short')
        return v


class LoginRequest(BaseModel):
    """
    登录请求模型
    """
    identifier: str
    password: str


class PasswordResetRequest(BaseModel):
    """
    密码重置请求模型
    """
    email: EmailStr 


class PasswordResetConfirmRequest(BaseModel):
    """
    密码重置确认请求模型
    """
    token: str
    password: str


class ProfileUpdateRequest(BaseModel):
    """
    资料更新请求模型
    """
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        """验证手机号格式"""
        if v is not None:
            if not v.replace('+', '').replace(' ', '').isdigit():
                raise ValueError('Phone number must contain only digits, plus sign and spaces')
            if len(v.replace('+', '').replace(' ', '')) < 10:
                raise ValueError('Phone number is too short')
        return v


class UserResponse(BaseModel):
    """
    用户响应模型
    """
    id: str
    username: str
    email: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    email_verified: bool 
    phone_verified: bool 
    status: str
    created_at: datetime 
    updated_at: datetime 


class TenantInfoResponse(BaseModel):
    """
    租户信息响应模型
    """
    id: str
    name: str
    code: str
    role: str
    joined_at: Optional[datetime] = None


class LoginResponse(BaseModel):
    """
    登录响应模型
    """
    token: str
    user: UserResponse 
    tenants: List[TenantInfoResponse] 
    expires_in: int 


class RegisterResponse(BaseModel):
    """
    注册响应模型
    """
    user: UserResponse 
    message: str


class ProfileResponse(BaseModel):
    """
    资料响应模型
    """
    user: UserResponse 
    tenants: List[TenantInfoResponse] 


class TokenVerifyResponse(BaseModel):
    """
    令牌验证响应模型
    """
    valid: bool 
    user: Optional[UserResponse] = None


class TokenRefreshResponse(BaseModel):
    """
    令牌刷新响应模型
    """
    token: str
    expires_in: int 


class MessageResponse(BaseModel):
    """
    通用消息响应模型
    """
    message: str


class ErrorResponse(BaseModel):
    """
    错误响应模型
    """
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


# API文档标签和描述
AUTH_TAGS = ["Authentication"]
AUTH_DESCRIPTION = """
用户认证相关API，包括注册、登录、令牌管理等功能。

## 认证流程
1. 用户注册 (`POST /api/auth/register`)
2. 邮箱验证 (`GET /api/auth/email/verify`)
3. 用户登录 (`POST /api/auth/login`)
4. 使用Bearer令牌访问受保护API

## 令牌管理
- JWT令牌在登录时颁发
- 令牌默认24小时过期
- 可以使用刷新令牌API延长有效期
- 登出API标记令牌失效（需要实现令牌黑名单）

## 安全注意事项
- 所有密码传输必须使用HTTPS
- 密码在服务器端进行哈希存储
- 登录失败有次数限制和账户锁定机制
- 敏感操作需要二次验证
"""
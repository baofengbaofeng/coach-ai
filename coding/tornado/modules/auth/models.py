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
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=8, max_length=100, description="密码")
    display_name: Optional[str] = Field(None, max_length=100, description="显示名称")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    
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
    identifier: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class PasswordResetRequest(BaseModel):
    """
    密码重置请求模型
    """
    email: EmailStr = Field(..., description="邮箱地址")


class PasswordResetConfirmRequest(BaseModel):
    """
    密码重置确认请求模型
    """
    token: str = Field(..., description="密码重置令牌")
    password: str = Field(..., min_length=8, max_length=100, description="新密码")


class ProfileUpdateRequest(BaseModel):
    """
    资料更新请求模型
    """
    display_name: Optional[str] = Field(None, max_length=100, description="显示名称")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    
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
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    display_name: Optional[str] = Field(None, description="显示名称")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    phone: Optional[str] = Field(None, description="手机号")
    email_verified: bool = Field(..., description="邮箱验证状态")
    phone_verified: bool = Field(..., description="手机验证状态")
    status: str = Field(..., description="用户状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class TenantInfoResponse(BaseModel):
    """
    租户信息响应模型
    """
    id: str = Field(..., description="租户ID")
    name: str = Field(..., description="租户名称")
    code: str = Field(..., description="租户代码")
    role: str = Field(..., description="用户角色")
    joined_at: Optional[datetime] = Field(None, description="加入时间")


class LoginResponse(BaseModel):
    """
    登录响应模型
    """
    token: str = Field(..., description="JWT令牌")
    user: UserResponse = Field(..., description="用户信息")
    tenants: List[TenantInfoResponse] = Field(default_factory=list, description="租户列表")
    expires_in: int = Field(..., description="令牌过期时间（秒）")


class RegisterResponse(BaseModel):
    """
    注册响应模型
    """
    user: UserResponse = Field(..., description="用户信息")
    message: str = Field(..., description="提示消息")


class ProfileResponse(BaseModel):
    """
    资料响应模型
    """
    user: UserResponse = Field(..., description="用户信息")
    tenants: List[TenantInfoResponse] = Field(default_factory=list, description="租户列表")


class TokenVerifyResponse(BaseModel):
    """
    令牌验证响应模型
    """
    valid: bool = Field(..., description="令牌是否有效")
    user: Optional[UserResponse] = Field(None, description="用户信息")


class TokenRefreshResponse(BaseModel):
    """
    令牌刷新响应模型
    """
    token: str = Field(..., description="新的JWT令牌")
    expires_in: int = Field(..., description="令牌过期时间（秒）")


class MessageResponse(BaseModel):
    """
    通用消息响应模型
    """
    message: str = Field(..., description="消息内容")


class ErrorResponse(BaseModel):
    """
    错误响应模型
    """
    error: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")


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
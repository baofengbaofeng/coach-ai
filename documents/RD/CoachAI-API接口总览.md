# CoachAI API 文档

## 概述

CoachAI 是一个基于多租户架构的家庭教练AI平台，提供用户认证、租户管理、数据隔离等功能。

## 基础信息

- **Base URL**: `http://localhost:8888/api`
- **认证方式**: Bearer Token (JWT)
- **响应格式**: JSON
- **错误处理**: 统一错误响应格式

## 统一响应格式

### 成功响应
```json
{
  "success": true,
  "data": {
    // 具体数据
  }
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```

## 认证 API

### 用户注册
注册新用户账户。

**Endpoint**: `POST /auth/register`

**请求体**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "display_name": "string",
  "phone": "string"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "string",
      "username": "string",
      "email": "string",
      "display_name": "string",
      "status": "string"
    },
    "message": "Registration successful. Please verify your email."
  }
}
```

### 用户登录
用户登录获取访问令牌。

**Endpoint**: `POST /auth/login`

**请求体**:
```json
{
  "identifier": "string",
  "password": "string"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "token": "string",
    "user": {
      "id": "string",
      "username": "string",
      "email": "string",
      "display_name": "string"
    },
    "tenants": [
      {
        "id": "string",
        "name": "string",
        "code": "string",
        "role": "string"
      }
    ],
    "expires_in": 86400
  }
}
```

### 用户登出
用户登出，使令牌失效。

**Endpoint**: `POST /auth/logout`

**Headers**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "message": "Logged out successfully"
  }
}
```

### 刷新令牌
刷新过期的JWT令牌。

**Endpoint**: `POST /auth/refresh`

**Headers**:
```
Authorization: Bearer <old_token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "token": "string",
    "expires_in": 86400
  }
}
```

### 验证令牌
验证JWT令牌的有效性。

**Endpoint**: `POST /auth/verify`

**Headers**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "valid": true,
    "user": {
      "id": "string",
      "username": "string",
      "email": "string"
    }
  }
}
```

### 请求密码重置
请求密码重置邮件。

**Endpoint**: `POST /auth/password/reset/request`

**请求体**:
```json
{
  "email": "string"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "message": "If the email exists, a reset link will be sent"
  }
}
```

### 重置密码
使用重置令牌设置新密码。

**Endpoint**: `POST /auth/password/reset`

**请求体**:
```json
{
  "token": "string",
  "password": "string"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "message": "Password reset successfully"
  }
}
```

### 验证邮箱
验证用户邮箱地址。

**Endpoint**: `GET /auth/email/verify?token=<verification_token>`

**响应**:
```json
{
  "success": true,
  "data": {
    "message": "Email verified successfully"
  }
}
```

### 获取用户资料
获取当前用户的资料信息。

**Endpoint**: `GET /auth/profile`

**Headers**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "string",
      "username": "string",
      "email": "string",
      "display_name": "string",
      "avatar_url": "string",
      "phone": "string",
      "email_verified": true,
      "phone_verified": false,
      "status": "string",
      "created_at": "string"
    },
    "tenants": [
      {
        "id": "string",
        "name": "string",
        "code": "string",
        "role": "string",
        "joined_at": "string"
      }
    ]
  }
}
```

### 更新用户资料
更新当前用户的资料信息。

**Endpoint**: `PUT /auth/profile`

**Headers**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "display_name": "string",
  "avatar_url": "string",
  "phone": "string"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "user": {
      // 更新后的用户资料
    },
    "message": "Profile updated successfully"
  }
}
```

## 租户管理 API

### 创建租户
创建新的租户（家庭/组织）。

**Endpoint**: `POST /tenants`

**Headers**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "name": "string",
  "code": "string",
  "description": "string",
  "type": "family",
  "domain": "string",
  "logo_url": "string",
  "cover_url": "string",
  "config": {},
  "metadata": {}
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "tenant": {
      "id": "string",
      "name": "string",
      "code": "string",
      "type": "string",
      "status": "string",
      "owner_id": "string",
      "created_at": "string"
    },
    "message": "Tenant created successfully"
  }
}
```

### 获取租户信息
获取指定租户的详细信息。

**Endpoint**: `GET /tenants/{tenant_id}`

**Headers**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": "string",
    "name": "string",
    "code": "string",
    "description": "string",
    "type": "string",
    "status": "string",
    "owner_id": "string",
    "member_count": 1,
    "can_add_member": true,
    "created_at": "string",
    "updated_at": "string"
  }
}
```

### 更新租户信息
更新指定租户的信息。

**Endpoint**: `PUT /tenants/{tenant_id}`

**Headers**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "name": "string",
  "description": "string",
  "domain": "string",
  "logo_url": "string",
  "cover_url": "string",
  "config": {},
  "metadata": {}
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "tenant": {
      // 更新后的租户信息
    },
    "message": "Tenant updated successfully"
  }
}
```

### 删除租户
删除指定租户（软删除）。

**Endpoint**: `DELETE /tenants/{tenant_id}`

**Headers**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "message": "Tenant deleted successfully"
  }
}
```

### 获取租户成员列表
获取指定租户的所有成员。

**Endpoint**: `GET /tenants/{tenant_id}/members`

**Headers**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "members": [
      {
        "id": "string",
        "user_id": "string",
        "username": "string",
        "email": "string",
        "display_name": "string",
        "avatar_url": "string",
        "role": "string",
        "status": "string",
        "joined_at": "string",
        "permissions": {},
        "created_at": "string"
      }
    ],
    "total": 1
  }
}
```

### 邀请成员
邀请用户加入租户。

**Endpoint**: `POST /tenants/{tenant_id}/members/invite`

**Headers**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "email": "string",
  "role": "member",
  "permissions": {},
  "config": {}
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "invite_token": "string",
    "message": "Invitation sent successfully"
  }
}
```

### 接受邀请
接受租户邀请。

**Endpoint**: `POST /tenants/invitations/accept`

**Headers**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "invite_token": "string"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "message": "Invitation accepted successfully"
  }
}
```

### 更新成员角色
更新租户成员的角色。

**Endpoint**: `PUT /tenants/{tenant_id}/members/{member_id}/role`

**Headers**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "role": "string"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "message": "Member role updated successfully"
  }
}
```

### 移除成员
从租户中移除成员。

**Endpoint**: `DELETE /tenants/{tenant_id}/members/{member_id}`

**Headers**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "message": "Member removed successfully"
  }
}
```

### 获取用户的所有租户
获取当前用户所属的所有租户。

**Endpoint**: `GET /tenants/my`

**Headers**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "tenants": [
      {
        "id": "string",
        "name": "string",
        "code": "string",
        "type": "string",
        "status": "string",
        "role": "string",
        "member_count": 1,
        "joined_at": "string",
        "created_at": "string"
      }
    ],
    "total": 1
  }
}
```

### 搜索租户
搜索租户（支持名称、代码、描述搜索）。

**Endpoint**: `GET /tenants/search?q=<query>&limit=<limit>`

**Headers**:
```
Authorization: Bearer <token>（可选）
```

**查询参数**:
- `q`: 搜索关键词（必需）
- `limit`: 结果数量限制（默认20，最大100）

**响应**:
```json
{
  "success": true,
  "data": {
    "tenants": [
      {
        "id": "string",
        "name": "string",
        "code": "string",
        "description": "string",
        "type": "string",
        "status": "string",
        "member_count": 1,
        "created_at": "string"
      }
    ],
    "total": 1
  }
}
```

## 健康检查 API

### 基础健康检查
检查服务是否正常运行。

**Endpoint**: `GET /health`

**响应**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "coach-ai",
    "version": "1.0.0",
    "environment": "development",
    "timestamp": 1700000000.0
  }
}
```

### 数据库健康检查
检查数据库连接状态。

**Endpoint**: `GET /health/db`

**响应**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "database",
    "message": "Database connection is healthy"
  }
}
```

### Redis健康检查
检查Redis连接状态。

**Endpoint**: `GET /health/redis`

**响应**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "redis",
    "message": "Redis connection is healthy"
  }
}
```

## 错误代码

### 认证错误
- `AUTH_REQUIRED`: 需要认证
- `INVALID_TOKEN`: 无效的令牌
- `EXPIRED_TOKEN`: 过期的令牌
- `INVALID_CREDENTIALS`: 无效的凭据
- `ACCOUNT_LOCKED`: 账户被锁定
- `ACCOUNT_INACTIVE`: 账户未激活

### 验证错误
- `VALIDATION_ERROR`: 数据验证失败
- `REQUIRED_FIELD`: 缺少必填字段
- `INVALID_FORMAT`: 格式无效
- `UNIQUE_CONSTRAINT`: 唯一性约束冲突

### 权限错误
- `PERMISSION_DENIED`: 权限不足
- `ACCESS_DENIED`: 访问被拒绝
- `ROLE_REQUIRED`: 需要特定角色

### 资源错误
- `NOT_FOUND`: 资源未找到
- `ALREADY_EXISTS`: 资源已存在
- `CONFLICT`: 资源冲突

### 系统错误
- `INTERNAL_ERROR`: 内部服务器错误
- `DATABASE_ERROR`: 数据库错误
- `REDIS_ERROR`: Redis错误
- `SERVICE_UNAVAILABLE`: 服务不可用

## 使用示例

### Python 示例
```python
import requests

# 1. 用户注册
register_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test@123456",
    "display_name": "测试用户"
}

response = requests.post("http://localhost:8888/api/auth/register", json=register_data)
print(response.json())

# 2. 用户登录
login_data = {
    "identifier": "testuser",
    "password": "Test@123456"
}

response = requests.post("http://localhost:8888/api/auth/login", json=login_data)
auth_data = response.json()["data"]
token = auth_data["token"]

# 3. 创建租户
headers = {"Authorization": f"Bearer {token}"}
tenant_data = {
    "name": "我的家庭",
    "code": "my-family",
    "description": "这是我的家庭租户",
    "type": "family"
}

response = requests.post("http://localhost:8888/api/tenants", json=tenant_data, headers=headers)
print(response.json())
```

### cURL 示例
```bash
# 用户登录
curl -X POST http://localhost:8888/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "testuser", "password": "Test@123456"}'

# 获取用户资料
curl -X GET http://localhost:8888/api/auth/profile \
  -H "Authorization: Bearer <your_token>"

# 创建租户
curl -X POST http://localhost:8888/api/tenants \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "我的家庭", "code": "my-family", "type": "family"}'
```

## 版本历史

### v1.0.0 (2026-03-28)
- 初始版本发布
- 用户认证模块
- 多租户管理模块
- 基础健康检查
- 数据库模型设计

## 注意事项

1. 所有API请求都应使用HTTPS（生产环境）
2. 密码必须至少8个字符，包含大小写字母和数字
3. JWT令牌默认24小时过期
4. 租户代码必须唯一且只包含字母、数字、下划线和连字符
5. 敏感操作需要二次验证（待实现）
6. API有速率限制（待实现）
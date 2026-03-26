# CoachAI API接口设计

## 📋 文档信息

| 项目 | 内容 |
|------|------|
| **文档名称** | CoachAI API接口设计 |
| **文档版本** | 1.0.0 |
| **创建日期** | 2026-03-26 |
| **最后更新** | 2026-03-26 |
| **文档状态** | 正式版 |
| **作者** | CoachAI-RD (后端研发专家) |
| **审核人** | 待定 |
| **关联文档** | [技术架构概要设计.md](./CoachAI技术架构概要设计.md) |
| **目标读者** | 前端开发人员、后端开发人员、测试人员 |

## 🎯 API设计原则

### 1.1 核心设计原则
1. **RESTful风格**：使用标准的HTTP方法和状态码
2. **版本控制**：API版本通过URL路径或请求头控制
3. **一致性**：统一的请求响应格式和错误处理
4. **安全性**：HTTPS、认证授权、输入验证
5. **文档化**：提供完整的API文档和示例

### 1.2 通用约定
- **基础URL**：`https://api.coachai.com/api/v1`
- **认证方式**：Bearer Token（JWT）
- **请求格式**：JSON
- **响应格式**：JSON
- **字符编码**：UTF-8
- **时区**：UTC
- **代码规范**：遵循`.rules/coding-style.md`，中文注释
- **开源协议**：GPL V3，衍生代码需保持开源

### 1.3 通用响应格式
```json
{
  "code": "SUCCESS",
  "message": "操作成功",
  "data": {
    // 业务数据
  },
  "meta": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  },
  "timestamp": "2026-03-26T05:26:00Z"
}
```

### 1.4 通用错误格式
```json
{
  "code": "VALIDATION_ERROR",
  "message": "数据验证失败",
  "details": {
    "field_errors": {
      "email": ["邮箱格式不正确"],
      "password": ["密码长度至少8位"]
    }
  },
  "timestamp": "2026-03-26T05:26:00Z"
}
```

## 🔐 认证授权API

### 2.1 用户注册

#### 请求
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "phone": "+8613800138000",
  "password": "SecurePassword123!",
  "nickname": "用户昵称",
  "real_name": "真实姓名",
  "gender": "male",
  "birth_date": "2000-01-01"
}
```

#### 响应
```json
{
  "code": "SUCCESS",
  "message": "注册成功",
  "data": {
    "user": {
      "id": 1,
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "phone": "+8613800138000",
      "nickname": "用户昵称",
      "real_name": "真实姓名",
      "avatar_url": null,
      "gender": "male",
      "birth_date": "2000-01-01",
      "is_active": true,
      "is_verified": false,
      "created_at": "2026-03-26T05:26:00Z",
      "updated_at": "2026-03-26T05:26:00Z"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400
  },
  "timestamp": "2026-03-26T05:26:00Z"
}
```

#### 错误码
- `VALIDATION_ERROR`：数据验证失败
- `EMAIL_EXISTS`：邮箱已存在
- `PHONE_EXISTS`：手机号已存在
- `USERNAME_EXISTS`：用户名已存在

### 2.2 用户登录

#### 请求
```http
POST /auth/login
Content-Type: application/json

{
  "login": "user@example.com",  // 邮箱、手机号或用户名
  "password": "SecurePassword123!",
  "remember_me": false
}
```

#### 响应
```json
{
  "code": "SUCCESS",
  "message": "登录成功",
  "data": {
    "user": {
      "id": 1,
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "phone": "+8613800138000",
      "nickname": "用户昵称",
      "real_name": "真实姓名",
      "avatar_url": "https://example.com/avatar.jpg",
      "gender": "male",
      "birth_date": "2000-01-01",
      "is_active": true,
      "is_verified": true,
      "last_login_at": "2026-03-26T05:26:00Z",
      "created_at": "2026-03-26T05:20:00Z",
      "updated_at": "2026-03-26T05:26:00Z"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400
  },
  "timestamp": "2026-03-26T05:26:00Z"
}
```

#### 错误码
- `INVALID_CREDENTIALS`：用户名或密码错误
- `ACCOUNT_LOCKED`：账户被锁定
- `ACCOUNT_INACTIVE`：账户未激活
- `MFA_REQUIRED`：需要多因素认证

### 2.3 刷新Token

#### 请求
```http
POST /auth/refresh
Content-Type: application/json
Authorization: Bearer <refresh_token>

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 响应
```json
{
  "code": "SUCCESS",
  "message": "Token刷新成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400
  },
  "timestamp": "2026-03-26T05:26:00Z"
}
```

#### 错误码
- `INVALID_TOKEN`：Token无效
- `EXPIRED_TOKEN`：Token已过期
- `REFRESH_TOKEN_REQUIRED`：需要刷新Token

## 🏠 租户管理API

### 3.1 创建租户（家庭）

#### 请求
```http
POST /tenants
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "name": "张氏家庭",
  "family_type": "core",
  "description": "这是一个核心家庭，有父母和一个孩子",
  "subscription_plan": "basic",
  "contact_email": "family@example.com",
  "contact_phone": "+8613800138000",
  "settings": {
    "language": "zh-CN",
    "timezone": "Asia/Shanghai",
    "notification_enabled": true
  }
}
```

#### 响应
```json
{
  "code": "SUCCESS",
  "message": "租户创建成功",
  "data": {
    "tenant": {
      "id": 1,
      "uuid": "550e8400-e29b-41d4-a716-446655440001",
      "name": "张氏家庭",
      "family_type": "core",
      "description": "这是一个核心家庭，有父母和一个孩子",
      "subscription_plan": "basic",
      "subscription_status": "active",
      "max_members": 5,
      "storage_quota": 10737418240,
      "contact_email": "family@example.com",
      "contact_phone": "+8613800138000",
      "settings": {
        "language": "zh-CN",
        "timezone": "Asia/Shanghai",
        "notification_enabled": true
      },
      "created_at": "2026-03-26T05:26:00Z",
      "updated_at": "2026-03-26T05:26:00Z",
      "subscription_start_at": "2026-03-26T05:26:00Z"
    },
    "family_member": {
      "id": 1,
      "uuid": "550e8400-e29b-41d4-a716-446655440002",
      "role": "admin",
      "relationship": "admin",
      "nickname_in_family": "管理员",
      "permissions": {
        "all": true
      },
      "is_active": true,
      "joined_at": "2026-03-26T05:26:00Z",
      "created_at": "2026-03-26T05:26:00Z",
      "updated_at": "2026-03-26T05:26:00Z"
    }
  },
  "timestamp": "2026-03-26T05:26:00Z"
}
```

#### 错误码
- `TENANT_LIMIT_REACHED`：租户数量达到限制
- `INVALID_SUBSCRIPTION_PLAN`：无效的订阅计划
- `STORAGE_QUOTA_EXCEEDED`：存储配额不足

### 3.2 获取租户列表

#### 请求
```http
GET /tenants?page=1&page_size=20&sort_by=created_at&sort_order=desc
Authorization: Bearer <access_token>
```

#### 响应
```json
{
  "code": "SUCCESS",
  "message": "获取租户列表成功",
  "data": {
    "tenants": [
      {
        "id": 1,
        "uuid": "550e8400-e29b-41d4-a716-446655440001",
        "name": "张氏家庭",
        "family_type": "core",
        "subscription_plan": "basic",
        "subscription_status": "active",
        "max_members": 5,
        "current_members": 3,
        "storage_used": 1073741824,
        "storage_quota": 10737418240,
        "created_at": "2026-03-26T05:26:00Z",
        "updated_at": "2026-03-26T05:26:00Z"
      }
    ]
  },
  "meta": {
    "total": 1,
    "page": 1,
    "page_size": 20,
    "total_pages": 1
  },
  "timestamp": "2026-03-26T05:26:00Z"
}
```

### 3.3 获取租户详情

#### 请求
```http
GET /tenants/{tenant_id}
Authorization: Bearer <access_token>
```

#### 响应
```json
{
  "code": "SUCCESS",
  "message": "获取租户详情成功",
  "data": {
    "tenant": {
      "id": 1,
      "uuid": "550e8400-e29b-41d4-a716-446655440001",
      "name": "张氏家庭",
      "family_type": "core",
      "description": "这是一个核心家庭，有父母和一个孩子",
      "subscription_plan": "basic",
      "subscription_status": "active",
      "max_members": 5,
      "storage_quota": 10737418240,
      "storage_used": 1073741824,
      "contact_email": "family@example.com",
      "contact_phone": "+8613800138000",
      "settings": {
        "language": "zh-CN",
        "timezone": "Asia/Shanghai",
        "notification_enabled": true,
        "homework_auto_correction": true,
        "exercise_auto_counting": true
      },
      "metadata": {
        "created_by": 1,
        "billing_cycle": "monthly"
      },
      "created_at": "2026-03-26T05:26:00Z",
      "updated_at": "2026-03-26T05:26:00Z",
      "subscription_start_at": "2026-03-26T05:26:00Z",
      "subscription_end_at": "2026-04-26T05:26:00Z"
    },
    "statistics": {
      "total_members": 3,
      "active_members": 3,
      "total_homeworks": 15,
      "pending_homeworks": 2,
      "total_exercises": 45,
      "total_achievements": 8,
      "storage_usage_percentage": 10.0
    }
  },
  "timestamp": "2026-03-26T05:26:00Z"
}
```

## 👨‍👩‍👧‍👦 家庭成员管理API

### 4.1 添加家庭成员

#### 请求
```http
POST /tenants/{tenant_id}/members
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "user_id": 2,
  "role": "student",
  "relationship": "儿子",
  "nickname_in_family": "小明",
  "permissions": {
    "homework": ["read", "create"],
    "exercise": ["read", "create"],
    "achievement": ["read"]
  }
}
```

#### 响应
```json
{
  "code": "SUCCESS",
  "message": "添加家庭成员成功",
  "data": {
    "family_member": {
      "id": 2,
      "uuid": "550e8400-e29b-41d4-a716-446655440003",
      "user_id": 2,
      "role": "student",
      "relationship": "儿子",
      "nickname_in_family": "小明",
      "permissions": {
        "homework": ["read", "create"],
        "exercise": ["read", "create"],
        "achievement": ["read"]
      },
      "is_active": true,
      "is_default": false,
      "joined_at": "2026-03-26T05:26:00Z",
      "created_at": "2026-03-26T05:26:00Z",
      "updated_at": "2026-03-26T05:26:00Z"
    },
    "user": {
      "id": 2,
      "uuid": "550e8400-e29b-41d4-a716-446655440004",
      "email": "xiaoming@example.com",
      "phone": "+8613800138001",
      "nickname": "小明",
      "real_name": "张小明",
      "avatar_url": "https://example.com/avatar_xiaoming.jpg",
      "gender": "male",
      "birth_date": "2015-06-15"
    }
  },
  "timestamp": "2026-03-26T05:26:00Z"
}
```

#### 错误码
- `MEMBER_LIMIT_REACHED`：成员数量达到限制
- `USER_ALREADY_MEMBER`：用户已是家庭成员
- `INVALID_ROLE`：无效的角色
- `PERMISSION_DENIED`：权限不足

### 4.2 获取家庭成员列表

#### 请求
```http
GET /tenants/{tenant_id}/members?role=student&is_active=true
Authorization: Bearer <access_token>
```

#### 响应
```json
{
  "code": "SUCCESS",
  "message": "获取家庭成员列表成功",
  "data": {
    "members": [
      {
        "id": 1,
        "uuid": "550e8400-e29b-41d4-a716-446655440002",
        "user_id": 1,
        "role": "admin",
        "relationship": "admin",
        "nickname_in_family": "管理员",
        "permissions": {
          "all": true
        },
        "is_active": true,
        "is_default": true,
        "joined_at": "2026-03-26T05:26:00Z",
        "created_at": "2026-03-26T05:26:00Z",
        "updated_at": "2026-03-26T05:26:00Z",
        "user": {
          "id": 1,
          "uuid": "550e8400-e29b-41d4-a716-446655440000",
          "email": "user@example.com",
          "phone": "+8613800138000",
          "nickname": "用户昵称",
          "real_name": "真实姓名",
          "avatar_url": "https://example.com/avatar.jpg",
          "gender": "male",
          "birth_date": "2000-01-01"
        }
      },
      {
        "id": 2,
        "uuid": "550e8400-e29b-41d4-a716-446655440003",
        "user_id": 2
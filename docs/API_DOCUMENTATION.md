  "success",
  "data": {
    "task": {
      "id": "string, 任务ID",
      "assignee_id": "string, 分配者ID",
      "status": "string, 状态 (assigned)",
      "updated_at": "string, 更新时间"
    }
  }
}
```

### 完成任务
标记任务为完成状态。

**端点**: `POST /api/v1/tasks/{task_id}/complete`

**请求头**:
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
X-Tenant-ID: TENANT_ID
```

**路径参数**:
- `task_id`: 任务ID

**请求体**:
```json
{
  "completion_notes": "string, 可选, 完成说明"
}
```

**响应** (成功: 200):
```json
{
  "status": "success",
  "data": {
    "task": {
      "id": "string, 任务ID",
      "status": "string, 状态 (completed)",
      "completed_at": "string, 完成时间",
      "updated_at": "string, 更新时间"
    }
  }
}
```

### 删除任务
删除指定任务。

**端点**: `DELETE /api/v1/tasks/{task_id}`

**请求头**:
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
X-Tenant-ID: TENANT_ID
```

**路径参数**:
- `task_id`: 任务ID

**响应** (成功: 200):
```json
{
  "status": "success",
  "message": "任务删除成功"
}
```

---

## 运动 API

### 创建运动记录
创建运动记录。

**端点**: `POST /api/v1/exercises/records`

**请求头**:
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
X-Tenant-ID: TENANT_ID
```

**请求体**:
```json
{
  "type": "string, 必填, 运动类型 (jump_rope/running/swimming/yoga)",
  "duration": "number, 必填, 运动时长 (秒)",
  "count": "number, 可选, 运动次数",
  "calories": "number, 可选, 消耗卡路里",
  "notes": "string, 可选, 运动备注"
}
```

**响应** (成功: 201):
```json
{
  "status": "success",
  "data": {
    "record": {
      "id": "string, 记录ID",
      "type": "string, 运动类型",
      "duration": "number, 运动时长",
      "count": "number, 运动次数",
      "calories": "number, 消耗卡路里",
      "user_id": "string, 用户ID",
      "created_at": "string, 创建时间"
    }
  }
}
```

### 获取运动记录详情
获取指定运动记录的详细信息。

**端点**: `GET /api/v1/exercises/records/{record_id}`

**请求头**:
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
X-Tenant-ID: TENANT_ID
```

**路径参数**:
- `record_id`: 运动记录ID

**响应** (成功: 200):
```json
{
  "status": "success",
  "data": {
    "record": {
      "id": "string, 记录ID",
      "type": "string, 运动类型",
      "duration": "number, 运动时长",
      "count": "number, 运动次数",
      "calories": "number, 消耗卡路里",
      "notes": "string, 运动备注",
      "user_id": "string, 用户ID",
      "created_at": "string, 创建时间"
    }
  }
}
```

### 获取运动记录列表
获取用户的运动记录列表。

**端点**: `GET /api/v1/exercises/records`

**请求头**:
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
X-Tenant-ID: TENANT_ID
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `limit`: 每页数量 (默认: 20, 最大: 100)
- `type`: 运动类型过滤
- `date_from`: 开始日期 (YYYY-MM-DD)
- `date_to`: 结束日期 (YYYY-MM-DD)
- `sort_by`: 排序字段 (created_at/duration/calories)
- `sort_order`: 排序顺序 (asc/desc)

**响应** (成功: 200):
```json
{
  "status": "success",
  "data": {
    "records": [
      {
        "id": "string, 记录ID",
        "type": "string, 运动类型",
        "duration": "number, 运动时长",
        "calories": "number, 消耗卡路里",
        "created_at": "string, 创建时间"
      }
    ],
    "pagination": {
      "page": "number, 当前页码",
      "limit": "number, 每页数量",
      "total": "number, 总数量",
      "pages": "number, 总页数"
    }
  }
}
```

### 获取运动统计
获取用户的运动统计信息。

**端点**: `GET /api/v1/exercises/stats`

**请求头**:
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
X-Tenant-ID: TENANT_ID
```

**查询参数**:
- `period`: 统计周期 (day/week/month/year), 默认: month
- `date`: 基准日期 (YYYY-MM-DD), 默认: 今天

**响应** (成功: 200):
```json
{
  "status": "success",
  "data": {
    "stats": {
      "total_duration": "number, 总运动时长(秒)",
      "total_calories": "number, 总消耗卡路里",
      "total_sessions": "number, 总运动次数",
      "average_duration": "number, 平均运动时长",
      "most_common_type": "string, 最常见运动类型",
      "period": "string, 统计周期",
      "start_date": "string, 统计开始日期",
      "end_date": "string, 统计结束日期"
    },
    "daily_stats": [
      {
        "date": "string, 日期",
        "duration": "number, 运动时长",
        "calories": "number, 消耗卡路里",
        "sessions": "number, 运动次数"
      }
    ]
  }
}
```

### 创建运动计划
创建运动计划。

**端点**: `POST /api/v1/exercises/plans`

**请求头**:
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
X-Tenant-ID: TENANT_ID
```

**请求体**:
```json
{
  "name": "string, 必填, 计划名称",
  "description": "string, 可选, 计划描述",
  "type": "string, 必填, 运动类型",
  "target_duration": "number, 必填, 目标时长(秒)",
  "target_calories": "number, 可选, 目标卡路里",
  "frequency": "string, 可选, 频率 (daily/weekly)",
  "start_date": "string, 可选, 开始日期",
  "end_date": "string, 可选, 结束日期"
}
```

**响应** (成功: 201):
```json
{
  "status": "success",
  "data": {
    "plan": {
      "id": "string, 计划ID",
      "name": "string, 计划名称",
      "type": "string, 运动类型",
      "target_duration": "number, 目标时长",
      "frequency": "string, 频率",
      "status": "string, 状态 (active/completed)",
      "progress": "number, 进度百分比",
      "created_at": "string, 创建时间",
      "updated_at": "string, 更新时间"
    }
  }
}
```

### 获取运动推荐
获取个性化运动推荐。

**端点**: `GET /api/v1/exercises/recommendations`

**请求头**:
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
X-Tenant-ID: TENANT_ID
```

**查询参数**:
- `limit`: 推荐数量 (默认: 3, 最大: 10)

**响应** (成功: 200):
```json
{
  "status": "success",
  "data": {
    "recommendations": [
      {
        "type": "string, 推荐运动类型",
        "duration": "number, 推荐时长",
        "reason": "string, 推荐理由",
        "difficulty": "string, 难度级别",
        "estimated_calories": "number, 预计卡路里"
      }
    ]
  }
}
```

---

## 成就 API

### 获取成就列表
获取所有成就列表。

**端点**: `GET /api/v1/achievements`

**请求头**:
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
X-Tenant-ID: TENANT_ID
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `limit`: 每页数量 (默认: 20, 最大: 100)
- `type`: 成就类型过滤
- `difficulty`: 难度过滤 (easy/medium/hard)

**响应** (成功: 200):
```json
{
  "status": "success",
  "data": {
    "achievements": [
      {
        "id": "string, 成就ID",
        "name": "string, 成就名称",
        "description": "string, 成就描述",
        "type": "string, 成就类型",
        "difficulty": "string, 难度",
        "target_value": "number, 目标值",
        "reward_points": "number, 奖励积分",
        "badge_url": "string, 徽章URL"
      }
    ],
    "pagination": {
      "page": "number, 当前页码",
      "limit": "number, 每页数量",
      "total": "number, 总数量",
      "pages": "number, 总页数"
    }
  }
}
```

### 获取成就详情
获取指定成就的详细信息。

**端点**: `GET /api/v1/achievements/{achievement_id}`

**请求头**:
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
X-Tenant-ID: TENANT_ID
```

**路径参数**:
- `achievement_id`: 成就ID

**响应** (成功: 200):
```json
{
  "status": "success",
  "data": {
    "achievement": {
      "id": "string, 成就ID",
      "name": "string, 成就名称",
      "description": "string, 成就描述",
      "type": "string, 成就类型",
      "difficulty": "string, 难度",
      "target_value": "number, 目标值",
      "reward_points": "number, 奖励积分",
      "badge_url": "string, 徽章URL",
      "created_at": "string, 创建时间",
      "updated_at": "string, 更新时间"
    }
  }
}
```

### 获取用户成就
获取用户的成就解锁情况。

**端点**: `GET /api/v1/achievements/user`

**请求头**:
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
X-Tenant-ID: TENANT_ID
```

**查询参数**:
- `status`: 状态过滤 (unlocked/locked/in_progress)

**响应** (成功: 200):
```json
{
  "status": "success",
  "data": {
    "user_achievements": [
      {
        "achievement_id": "string, 成就ID",
        "name": "string, 成就名称",
        "description": "string, 成就描述",
        "status": "string, 状态",
        "progress": "number, 当前进度",
        "target_value": "number, 目标值",
        "unlocked_at": "string, 解锁时间",
        "reward_points": "number, 奖励积分"
      }
    ],
    "summary": {
      "total_achievements": "number, 总成就数",
      "unlocked_achievements": "number, 已解锁成就数",
      "total_points": "number, 总积分",
      "completion_rate": "number, 完成率"
    }
  }
}
```

### 获取用户徽章
获取用户的徽章收集情况。

**端点**: `GET /api/v1/achievements/badges`

**请求头**:
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
X-Tenant-ID: TENANT_ID
```

**响应** (成功: 200):
```json
{
  "status": "success",
  "data": {
    "badges": [
      {
        "id": "string, 徽章ID",
        "name": "string, 徽章名称",
        "description": "string, 徽章描述",
        "image_url": "string, 徽章图片URL",
        "achievement_id": "string, 关联成就ID",
        "unlocked_at": "string, 解锁时间"
      }
    ],
    "total_badges": "number, 总徽章数",
    "unlocked_badges": "number, 已解锁徽章数"
  }
}
```

### 获取成就进度
获取用户特定成就的进度。

**端点**: `GET /api/v1/achievements/{achievement_id}/progress`

**请求头**:
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
X-Tenant-ID: TENANT_ID
```

**路径参数**:
- `achievement_id`: 成就ID

**响应** (成功: 200):
```json
{
  "status": "success",
  "data": {
    "progress": {
      "achievement_id": "string, 成就ID",
      "achievement_name": "string, 成就名称",
      "current_value": "number, 当前值",
      "target_value": "number, 目标值",
      "progress_percentage": "number, 进度百分比",
      "status": "string, 状态",
      "last_updated": "string, 最后更新时间"
    }
  }
}
```

---

## 系统 API

### 健康检查
检查系统健康状态。

**端点**: `GET /api/health`

**请求头**:
```
Content-Type: application/json
```

**响应** (成功: 200):
```json
{
  "status": "healthy",
  "timestamp": "string, 当前时间",
  "version": "string, 应用版本",
  "services": {
    "database": {
      "status": "string, 状态",
      "message": "string, 消息"
    },
    "redis": {
      "status": "string, 状态",
      "message": "string, 消息"
    },
    "application": {
      "status": "string, 状态",
      "message": "string, 消息"
    }
  }
}
```

### 系统信息
获取系统信息。

**端点**: `GET /api/info`

**请求头**:
```
Content-Type: application/json
```

**响应** (成功: 200):
```json
{
  "status": "success",
  "data": {
    "application": {
      "name": "CoachAI",
      "version": "string, 版本号",
      "environment": "string, 环境",
      "uptime": "number, 运行时间(秒)"
    },
    "server": {
      "host": "string, 主机",
      "port": "number, 端口",
      "protocol": "string, 协议"
    },
    "database": {
      "type": "string, 数据库类型",
      "version": "string, 数据库版本"
    },
    "limits": {
      "max_upload_size": "number, 最大上传大小",
      "rate_limit": "string, 速率限制"
    }
  }
}
```

### API文档
获取API文档（Swagger/OpenAPI）。

**端点**: `GET /api/docs`

**请求头**:
```
Content-Type: application/json
```

**响应**: HTML格式的API文档页面

---

## 错误处理

### 错误响应格式
所有错误响应都遵循以下格式：

```json
{
  "status": "error",
  "error": {
    "code": "string, 错误代码",
    "message": "string, 错误消息",
    "details": "object, 错误详情 (可选)"
  },
  "timestamp": "string, 错误时间"
}
```

### 常见错误代码

| 状态码 | 错误代码 | 描述 |
|--------|----------|------|
| 400 | VALIDATION_ERROR | 请求数据验证失败 |
| 401 | AUTHENTICATION_ERROR | 认证失败 |
| 403 | AUTHORIZATION_ERROR | 权限不足 |
| 404 | NOT_FOUND | 资源不存在 |
| 409 | CONFLICT | 资源冲突 |
| 422 | UNPROCESSABLE_ENTITY | 无法处理的实体 |
| 429 | RATE_LIMIT_EXCEEDED | 请求频率超限 |
| 500 | INTERNAL_SERVER_ERROR | 服务器内部错误 |
| 503 | SERVICE_UNAVAILABLE | 服务不可用 |

### 错误示例

#### 认证错误
```json
{
  "status": "error",
  "error": {
    "code": "AUTHENTICATION_ERROR",
    "message": "Invalid credentials"
  },
  "timestamp": "2026-03-27T10:00:00Z"
}
```

#### 验证错误
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "email": ["Invalid email format"],
      "password": ["Password must be at least 8 characters"]
    }
  },
  "timestamp": "2026-
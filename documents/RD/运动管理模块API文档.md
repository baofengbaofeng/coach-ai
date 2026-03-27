# 运动管理模块 API 文档

## 概述

运动管理模块提供运动类型管理、运动记录、运动计划、摄像头集成和姿势分析等功能。

## 基础信息

- **基础路径**: `/api/exercise`
- **认证**: 所有API都需要Bearer Token认证（除了部分公共接口）
- **内容类型**: `application/json`

## API 端点

### 运动类型管理

#### 获取运动类型列表
```
GET /api/exercise/types
```

**查询参数**:
- `category` (可选): 运动分类 (strength, cardio, flexibility, balance, mixed)
- `difficulty` (可选): 难度级别 (beginner, intermediate, advanced, expert)
- `is_active` (可选): 是否启用 (true/false)
- `search` (可选): 搜索关键词
- `page` (可选): 页码，默认1
- `page_size` (可选): 每页大小，默认20

**响应示例**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "11111111-1111-1111-1111-111111111111",
        "name_zh": "俯卧撑",
        "name_en": "Push-up",
        "code": "pushup",
        "category": "strength",
        "difficulty": "beginner",
        "description": "经典的上肢力量训练动作",
        "standard_repetitions": 15,
        "standard_sets": 3,
        "calorie_factor": 0.12,
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "total_pages": 1
  }
}
```

#### 获取单个运动类型
```
GET /api/exercise/types/{exercise_type_id}
```

#### 创建运动类型（管理员）
```
POST /api/exercise/types
```

**请求体**:
```json
{
  "name_zh": "新运动",
  "name_en": "New Exercise",
  "code": "new_exercise",
  "category": "strength",
  "difficulty": "beginner",
  "description": "运动描述",
  "standard_repetitions": 10,
  "standard_sets": 3,
  "calorie_factor": 0.1,
  "target_muscles": ["chest", "arms"],
  "secondary_muscles": ["core"]
}
```

#### 更新运动类型（管理员）
```
PUT /api/exercise/types/{exercise_type_id}
```

#### 删除运动类型（管理员）
```
DELETE /api/exercise/types/{exercise_type_id}
```

### 运动记录管理

#### 获取运动记录列表
```
GET /api/exercise/records
```

**查询参数**:
- `exercise_type_id` (可选): 运动类型ID
- `status` (可选): 状态 (completed, in_progress, paused, cancelled)
- `mode` (可选): 模式 (manual, camera_auto, sensor_auto)
- `start_date` (可选): 开始日期 (ISO格式)
- `end_date` (可选): 结束日期 (ISO格式)
- `is_verified` (可选): 是否已验证 (true/false)
- `page` (可选): 页码
- `page_size` (可选): 每页大小

**响应示例**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "22222222-2222-2222-2222-222222222222",
        "user_id": "user-id-here",
        "exercise_type_id": "11111111-1111-1111-1111-111111111111",
        "start_time": "2024-01-01T10:00:00Z",
        "end_time": "2024-01-01T10:05:00Z",
        "status": "completed",
        "mode": "manual",
        "total_repetitions": 20,
        "total_sets": 3,
        "duration_minutes": 5.0,
        "estimated_calories": 50.5,
        "quality_score": 85,
        "created_at": "2024-01-01T10:06:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "total_pages": 1
  }
}
```

#### 获取单个运动记录
```
GET /api/exercise/records/{exercise_record_id}
```

#### 创建运动记录
```
POST /api/exercise/records
```

**请求体**:
```json
{
  "exercise_type_id": "11111111-1111-1111-1111-111111111111",
  "start_time": "2024-01-01T10:00:00Z",
  "end_time": "2024-01-01T10:05:00Z",
  "total_repetitions": 20,
  "total_sets": 3,
  "user_weight_kg": 70.0,
  "notes": "训练备注"
}
```

#### 开始运动
```
POST /api/exercise/start
```

**请求体**:
```json
{
  "exercise_type_id": "11111111-1111-1111-1111-111111111111",
  "user_weight_kg": 70.0,
  "camera_device_id": "33333333-3333-3333-3333-333333333333"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "exercise_record_id": "22222222-2222-2222-2222-222222222222",
    "start_time": "2024-01-01T10:00:00Z",
    "status": "in_progress",
    "message": "Exercise started successfully"
  }
}
```

#### 完成运动
```
POST /api/exercise/complete/{exercise_record_id}
```

**请求体**:
```json
{
  "total_repetitions": 25,
  "total_sets": 3,
  "notes": "完成训练"
}
```

### 运动统计

#### 获取运动统计数据
```
GET /api/exercise/statistics
```

**查询参数**:
- `period` (可选): 统计周期 (daily, weekly, monthly, yearly)，默认daily
- `start_date` (可选): 开始日期 (ISO格式)
- `end_date` (可选): 结束日期 (ISO格式)

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user_id": "user-id-here",
    "period": "weekly",
    "start_date": "2024-01-01",
    "end_date": "2024-01-07",
    "total_exercises": 5,
    "total_duration_minutes": 125.5,
    "total_calories": 625.0,
    "total_repetitions": 150,
    "total_sets": 15,
    "avg_quality_score": 82.5,
    "avg_posture_accuracy": 85.0,
    "exercise_type_distribution": {
      "11111111-1111-1111-1111-111111111111": 3,
      "22222222-2222-2222-2222-222222222222": 2
    },
    "daily_completion_rate": 71.4,
    "streak_days": 7,
    "most_frequent_exercise": "11111111-1111-1111-1111-111111111111",
    "best_quality_exercise": "44444444-4444-4444-4444-444444444444",
    "recent_activities": [
      {
        "id": "55555555-5555-5555-5555-555555555555",
        "exercise_type_id": "11111111-1111-1111-1111-111111111111",
        "start_time": "2024-01-07T10:00:00Z",
        "duration_minutes": 25.0,
        "total_repetitions": 30,
        "quality_score": 88
      }
    ]
  }
}
```

### 运动计划管理

#### 获取今日运动计划
```
GET /api/exercise/plans
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "todays_plans": [
      {
        "id": "66666666-6666-6666-6666-666666666666",
        "user_id": "user-id-here",
        "exercise_type_id": "11111111-1111-1111-1111-111111111111",
        "plan_name": "每日俯卧撑",
        "plan_type": "daily",
        "status": "active",
        "start_date": "2024-01-01",
        "target_repetitions": 30,
        "target_sets": 3,
        "weekly_frequency": 7,
        "priority": 5,
        "progress": 66,
        "completed_count": 2,
        "streak_days": 2,
        "is_active": true,
        "is_due_today": true,
        "next_due_date": "2024-01-02"
      }
    ],
    "total": 1
  }
}
```

#### 获取单个运动计划
```
GET /api/exercise/plans/{exercise_plan_id}
```

#### 创建运动计划
```
POST /api/exercise/plans
```

**请求体**:
```json
{
  "exercise_type_id": "11111111-1111-1111-1111-111111111111",
  "plan_name": "每周训练计划",
  "plan_type": "weekly",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "target_repetitions": 30,
  "target_sets": 3,
  "weekly_frequency": 3,
  "weekly_days": [1, 3, 5],
  "daily_time": "19:00:00",
  "priority": 8,
  "enable_reminder": true,
  "reminder_minutes_before": 15
}
```

### 摄像头设备管理

#### 获取可用摄像头列表
```
GET /api/exercise/cameras
```

**查询参数**:
- `tenant_id` (可选): 租户ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "77777777-7777-7777-7777-777777777777",
        "device_name": "客厅摄像头",
        "serial_number": "CAM-001",
        "device_type": "ip_camera",
        "connection_status": "online",
        "ip_address": "192.168.1.100",
        "resolution": "1920x1080",
        "frame_rate": 30,
        "is_enabled": true,
        "is_in_use": false,
        "is_available": true,
        "uptime_minutes": 120.5,
        "webrtc_config": {
          "peer_id": "peer-123",
          "signaling_url": "ws://localhost:8080/signal",
          "video": {
            "width": 1920,
            "height": 1080,
            "frameRate": 30,
            "codec": "h264"
          }
        }
      }
    ],
    "total": 1
  }
}
```

#### 注册摄像头设备（管理员）
```
POST /api/exercise/cameras
```

**请求体**:
```json
{
  "device_name": "新摄像头",
  "serial_number": "CAM-NEW-001",
  "device_type": "webcam",
  "brand": "品牌",
  "model": "型号",
  "ip_address": "192.168.1.101",
  "port": 8080,
  "resolution_width": 1920,
  "resolution_height": 1080,
  "frame_rate": 30,
  "video_codec": "h264"
}
```

### 姿势分析

#### 分析姿势
```
POST /api/exercise/analyze/{exercise_record_id}
```

**请求体**:
```json
{
  "landmarks": [
    {
      "x": 0.5,
      "y": 0.5,
      "z": 0.0,
      "visibility": 0.9
    },
    {
      "x": 0.6,
      "y": 0.6,
      "z": 0.0,
      "visibility": 0.8
    }
  ]
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "exercise_record_id": "22222222-2222-2222-2222-222222222222",
    "timestamp": "2024-01-01T10:01:00Z",
    "landmarks": [...],
    "angles": {
      "elbow": 90,
      "shoulder": 45
    },
    "posture_score": 85,
    "alignment_errors": [
      {
        "type": "body_alignment",
        "severity": "medium",
        "message": "身体未保持直线"
      }
    ],
    "movement_quality": 80,
    "repetition_count": 1,
    "repetition_phase": "down",
    "feedback_messages": [
      {
        "message": "保持身体直线",
        "severity": "warning",
        "timestamp": "2024-01-01T10:01:00Z"
      }
    ],
    "is_correct_posture": true,
    "confidence": 0.9
  }
}
```

### WebRTC信令

#### WebRTC信令交换
```
POST /api/exercise/webrtc/{camera_device_id}/signal
```

**请求体**:
```json
{
  "type": "offer",
  "sdp": "v=0\no=- 123456789 2 IN IP4 127.0.0.1\ns=-\nt=0 0\na=group:BUNDLE 0\na=msid-semantic: WMS\nm=application 9 UDP/DTLS/SCTP webrtc-datachannel\nc=IN IP4 0.0.0.0\na=ice-ufrag:abc123\na=ice-pwd:def456\na=ice-options:trickle\na=fingerprint:sha-256 AA:BB:CC:DD:EE:FF\na=setup:actpass\na=mid:0\na=sctp-port:5000\na=max-message-size:262144\n"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "type": "answer",
    "camera_device_id": "77777777-7777-7777-7777-777777777777",
    "timestamp": "2024-01-01T10:00:00Z",
    "sdp": "v=0\no=- 987654321 2 IN IP4 127.0.0.1\ns=-\nt=0 0\na=group:BUNDLE 0\na=msid-semantic: WMS\nm=application 9 UDP/DTLS/SCTP webrtc-datachannel\nc=IN IP4 0.0.0.0\na=ice-ufrag:xyz789\na=ice-pwd:uvw012\na=ice-options:trickle\na=fingerprint:sha-256 FF:EE:DD:CC:BB:AA\na=setup:active\na=mid:0\na=sctp-port:5000\na=max-message-size:262144\n"
  }
}
```

## 错误响应

所有API错误都遵循统一的错误响应格式：

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

**常见错误码**:
- `VALIDATION_ERROR`: 请求数据验证失败
- `UNAUTHORIZED`: 未认证或Token无效
- `FORBIDDEN`: 权限不足
- `NOT_FOUND`: 资源未找到
- `EXERCISE_TYPE_EXISTS`: 运动类型已存在
- `CAMERA_NOT_AVAILABLE`: 摄像头不可用
- `EXERCISE_IN_PROGRESS`: 运动正在进行中
- `EXERCISE_ALREADY_COMPLETED`: 运动已完成

## 数据模型

### 运动类型 (ExerciseType)
```json
{
  "id": "UUID",
  "name_zh": "运动中文名",
  "name_en": "运动英文名",
  "code": "唯一代码",
  "category": "分类",
  "difficulty": "难度",
  "description": "描述",
  "standard_movement": "标准动作说明",
  "target_muscles": ["目标肌肉群"],
  "secondary_muscles": ["辅助肌肉群"],
  "standard_duration": 0,
  "standard_repetitions": 10,
  "standard_sets": 3,
  "calorie_factor": 0.1,
  "is_active": true
}
```

### 运动记录 (ExerciseRecord)
```json
{
  "id": "UUID",
  "user_id": "用户ID",
  "exercise_type_id": "运动类型ID",
  "start_time": "开始时间",
  "end_time": "结束时间",
  "status": "状态",
  "mode": "模式",
  "total_repetitions": 0,
  "total_sets": 0,
  "duration_minutes": 5.0,
  "estimated_calories": 50.5,
  "quality_score": 85,
  "posture_accuracy": 90,
  "sensor_data": {},
  "video_analysis_data": {}
}
```

### 运动计划 (ExercisePlan)
```json
{
  "id": "UUID",
  "user_id": "用户ID",
  "exercise_type_id": "运动类型ID",
  "plan_name": "计划名称",
  "plan_type": "计划类型",
  "status": "状态",
  "start_date": "开始日期",
  "end_date": "结束日期",
  "target_repetitions": 30,
  "target_sets": 3,
  "weekly_frequency": 7,
  "weekly_days": [1, 3, 5],
  "daily_time": "19:00:00",
  "priority": 5,
  "progress": 66,
  "completed_count": 2,
  "streak_days": 2,
  "is_active": true,
  "is_due_today": true,
  "next_due_date": "2024-01-02"
}
```

### 摄像头设备 (CameraDevice)
```json
{
  "id": "UUID",
  "device_name": "设备名称",
  "serial_number": "序列号",
  "device_type": "设备类型",
  "connection_status": "连接状态",
  "ip_address": "IP地址",
  "port": 8080,
  "resolution": "1920x1080",
  "frame_rate": 30,
  "is_enabled": true,
  "is_in_use": false,
  "is_available": true,
  "webrtc_config": {
    "peer_id": "peer-123",
    "signaling_url": "ws://localhost:8080/signal"
  }
}
```

## 使用示例

### 1. 开始使用摄像头进行运动
```bash
# 1. 获取可用摄像头
GET /api/exercise/cameras

# 2. 开始运动（使用摄像头）
POST /api/exercise/start
{
  "exercise_type_id": "11111111-1111-1111-1111-111111111111",
  "camera_device_id": "77777777-7777-7777-7777-777777777777"
}

# 3. WebRTC连接建立后，实时发送姿势数据进行分析
POST /api/exercise/analyze/{exercise_record_id}
{
  "landmarks": [...]
}

# 4. 完成运动
POST /api/exercise/complete/{exercise_record_id}
{
  "total_repetitions": 25,
  "total_sets": 3
}
```

### 2. 查看运动统计
```bash
# 查看本周运动统计
GET /api/exercise/statistics?period=weekly

# 查看自定义日期范围统计
GET /api/exercise/statistics?start_date=2024-01-01&end_date=2024-01-31
```

### 3. 管理运动计划
```bash
# 创建每周一、三、五的训练计划
POST /api/exercise/plans
{
  "exercise_type_id": "11111111-1111-1111-1111-111111111111",
  "plan_name": "每周俯卧撑训练",
  "plan_type": "weekly",
  "start_date": "2024-01-01",
  "weekly_days": [1, 3, 5],
  "daily_time": "19:00:00",
  "target_repetitions": 30,
  "target_sets": 3
}

# 查看今日计划
GET /api/exercise/plans
```

## 注意事项

1. **权限控制**:
   - 普通用户只能管理自己的运动记录和计划
   - 管理员可以管理所有运动类型和摄像头设备
   - 摄像头使用需要先检查可用性

2. **数据验证**:
   - 所有时间字段必须使用ISO 8601格式
   - 运动类型代码必须唯一
   - 摄像头序列号必须唯一

3. **性能考虑**:
   - 姿势分析API可能消耗较多计算资源
   - 大量运动记录查询建议使用分页
   - 实时视频流使用WebRTC以减少延迟

4. **错误处理**:
   - 所有API都包含适当的错误处理
   - 建议客户端实现重试机制
   - 网络超时设置为合理值

## 版本历史

- v1.0.0 (2024-01-01): 初始版本，包含基本运动管理功能
- v1.1.0 (计划): 添加运动成就系统、社交功能、高级分析
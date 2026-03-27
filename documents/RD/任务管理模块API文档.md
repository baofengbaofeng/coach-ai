# 任务管理模块 API 文档

## 概述

任务管理模块提供完整的任务生命周期管理功能，包括任务创建、分配、提交、评价和智能调度。

## 数据库表结构

### 1. 任务表 (tasks)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | CHAR(36) | 主键，UUID |
| title | VARCHAR(200) | 任务标题 |
| description | TEXT | 任务描述 |
| task_type | ENUM | 任务类型：homework, exercise, custom |
| status | ENUM | 任务状态：draft, active, completed, cancelled, archived |
| priority | ENUM | 任务优先级：low, medium, high, urgent |
| difficulty | ENUM | 任务难度：beginner, intermediate, advanced, expert |
| tags | JSON | 任务标签数组 |
| content | JSON | 任务内容（根据类型不同） |
| start_time | DATETIME | 任务开始时间 |
| deadline | DATETIME | 任务截止时间 |
| estimated_duration | INT | 预计完成时间（分钟） |
| actual_duration | INT | 实际完成时间（分钟） |
| creator_id | CHAR(36) | 创建者ID |
| tenant_id | CHAR(36) | 租户ID |
| exercise_type_id | CHAR(36) | 关联的运动类型ID |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| deleted_at | DATETIME | 删除时间 |

### 2. 任务分配表 (task_assignments)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | CHAR(36) | 主键，UUID |
| task_id | CHAR(36) | 任务ID |
| student_id | CHAR(36) | 学员ID |
| assigner_id | CHAR(36) | 分配者ID |
| status | ENUM | 分配状态：assigned, in_progress, completed, cancelled, overdue |
| progress | FLOAT | 进度百分比（0-100） |
| assigned_at | DATETIME | 分配时间 |
| started_at | DATETIME | 开始时间 |
| completed_at | DATETIME | 完成时间 |
| expected_completion_at | DATETIME | 预计完成时间 |
| actual_completion_at | DATETIME | 实际完成时间 |
| tenant_id | CHAR(36) | 租户ID |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 3. 任务提交表 (task_submissions)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | CHAR(36) | 主键，UUID |
| assignment_id | CHAR(36) | 任务分配ID |
| submitter_id | CHAR(36) | 提交者ID |
| status | ENUM | 提交状态：submitted, reviewed, returned, accepted, rejected |
| content | JSON | 提交内容 |
| submitted_at | DATETIME | 提交时间 |
| reviewed_at | DATETIME | 审核时间 |
| reviewer_id | CHAR(36) | 审核者ID |
| version | INT | 版本号 |
| is_final | BOOLEAN | 是否为最终提交 |
| tenant_id | CHAR(36) | 租户ID |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 4. 任务评价表 (task_evaluations)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | CHAR(36) | 主键，UUID |
| assignment_id | CHAR(36) | 任务分配ID |
| submission_id | CHAR(36) | 任务提交ID |
| evaluator_id | CHAR(36) | 评价者ID |
| student_id | CHAR(36) | 被评价者ID |
| overall_score | FLOAT | 总体评分（0-100） |
| score_details | JSON | 评分详情 |
| comments | TEXT | 评语 |
| evaluated_at | DATETIME | 评价时间 |
| status | ENUM | 评价状态：draft, published, archived |
| tenant_id | CHAR(36) | 租户ID |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

## API 接口

### 任务管理

#### 1. 创建任务
- **URL**: `POST /api/v1/tasks`
- **认证**: 需要
- **请求体**:
```json
{
  "title": "数学作业",
  "description": "完成第一章练习题",
  "task_type": "homework",
  "priority": "medium",
  "difficulty": "beginner",
  "tags": ["数学", "作业"],
  "estimated_duration": 60,
  "start_time": "2024-01-01T09:00:00Z",
  "deadline": "2024-01-07T23:59:59Z"
}
```

#### 2. 获取任务列表
- **URL**: `GET /api/v1/tasks`
- **认证**: 需要
- **查询参数**:
  - `page`: 页码（默认1）
  - `page_size`: 每页大小（默认20）
  - `task_type`: 任务类型过滤
  - `status`: 状态过滤
  - `priority`: 优先级过滤
  - `search`: 搜索关键词

#### 3. 获取单个任务
- **URL**: `GET /api/v1/tasks/{task_id}`
- **认证**: 需要

#### 4. 更新任务
- **URL**: `PUT /api/v1/tasks/{task_id}`
- **认证**: 需要
- **请求体**: 同创建任务，但所有字段可选

#### 5. 删除任务
- **URL**: `DELETE /api/v1/tasks/{task_id}`
- **认证**: 需要

#### 6. 激活任务
- **URL**: `PATCH /api/v1/tasks/{task_id}/activate`
- **认证**: 需要

### 任务分配

#### 1. 分配任务
- **URL**: `POST /api/v1/task-assignments`
- **认证**: 需要
- **请求体**:
```json
{
  "task_id": "task-uuid",
  "student_id": "student-uuid",
  "assignment_notes": "请认真完成",
  "expected_completion_at": "2024-01-07T23:59:59Z"
}
```

#### 2. 获取分配列表
- **URL**: `GET /api/v1/task-assignments`
- **认证**: 需要
- **查询参数**:
  - `task_id`: 任务ID过滤
  - `student_id`: 学员ID过滤
  - `status`: 状态过滤
  - `is_overdue`: 是否过期

#### 3. 获取学员的分配
- **URL**: `GET /api/v1/students/{student_id}/task-assignments`
- **认证**: 需要

#### 4. 更新分配进度
- **URL**: `PUT /api/v1/task-assignments/{assignment_id}`
- **认证**: 需要
- **请求体**:
```json
{
  "progress": 50.0,
  "status": "in_progress",
  "student_notes": "已完成一半"
}
```

### 任务提交

#### 1. 提交任务
- **URL**: `POST /api/v1/task-submissions`
- **认证**: 需要（学员）
- **请求体**:
```json
{
  "assignment_id": "assignment-uuid",
  "content": {
    "type": "text",
    "text": "这是我的作业内容"
  },
  "submission_notes": "请查收",
  "is_final": true
}
```

#### 2. 审核提交
- **URL**: `PATCH /api/v1/task-submissions/{submission_id}/review`
- **认证**: 需要（教练/管理员）
- **请求体**:
```json
{
  "status": "accepted",
  "review_notes": "作业完成得很好"
}
```

### 任务评价

#### 1. 创建评价
- **URL**: `POST /api/v1/task-evaluations`
- **认证**: 需要（教练/管理员）
- **请求体**:
```json
{
  "assignment_id": "assignment-uuid",
  "overall_score": 85.5,
  "score_details": {
    "完成度": 90.0,
    "准确性": 85.0
  },
  "comments": "作业完成得很好",
  "recommended_for_advancement": true
}
```

#### 2. 发布评价
- **URL**: `PATCH /api/v1/task-evaluations/{evaluation_id}/publish`
- **认证**: 需要（评价者）

### 智能调度

#### 1. 智能调度任务
- **URL**: `POST /api/v1/task-scheduler/schedule`
- **认证**: 需要
- **请求体**:
```json
{
  "student_id": "student-uuid",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z",
  "max_tasks_per_day": 3,
  "consider_difficulty": true,
  "consider_priority": true
}
```

### 任务分析

#### 1. 获取分析数据
- **URL**: `POST /api/v1/task-analytics`
- **认证**: 需要
- **请求体**:
```json
{
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z",
  "group_by": "task_type",
  "student_id": "student-uuid"
}
```

## 智能调度算法

### 调度规则

1. **优先级规则**: 紧急任务优先安排
2. **难度适配**: 根据学员能力匹配合适难度的任务
3. **时间窗口**: 考虑任务的开始时间和截止时间
4. **依赖关系**: 处理任务之间的依赖关系
5. **负载均衡**: 避免单日任务过多

### 调度流程

1. 分析学员历史表现和能力水平
2. 筛选适合学员能力的任务
3. 根据优先级和截止时间排序
4. 分配到合适的时间窗口
5. 考虑依赖关系和前置条件

## 数据分析指标

### 1. 完成率统计
- 总体完成率
- 按任务类型完成率
- 按难度完成率
- 按时完成率

### 2. 质量评估
- 平均评分
- 评分分布
- 进步趋势
- 能力成长

### 3. 效率分析
- 平均完成时间
- 延期率分析
- 资源利用率
- 瓶颈识别

## 使用示例

### 创建并分配任务
```bash
# 1. 创建任务
curl -X POST http://localhost:8888/api/v1/tasks \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "数学作业",
    "task_type": "homework",
    "priority": "medium"
  }'

# 2. 激活任务
curl -X PATCH http://localhost:8888/api/v1/tasks/{task_id}/activate \
  -H "Authorization: Bearer {token}"

# 3. 分配任务给学员
curl -X POST http://localhost:8888/api/v1/task-assignments \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "{task_id}",
    "student_id": "{student_id}"
  }'
```

### 学员提交任务
```bash
# 1. 学员提交任务
curl -X POST http://localhost:8888/api/v1/task-submissions \
  -H "Authorization: Bearer {student_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "assignment_id": "{assignment_id}",
    "content": {"type": "text", "text": "作业内容"},
    "is_final": true
  }'

# 2. 教练审核
curl -X PATCH http://localhost:8888/api/v1/task-submissions/{submission_id}/review \
  -H "Authorization: Bearer {coach_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "accepted",
    "review_notes": "很好"
  }'

# 3. 教练评价
curl -X POST http://localhost:8888/api/v1/task-evaluations \
  -H "Authorization: Bearer {coach_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "assignment_id": "{assignment_id}",
    "overall_score": 90.0,
    "comments": "优秀"
  }'
```

## 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 资源冲突（如重复分配） |
| 500 | 服务器内部错误 |

## 注意事项

1. **权限控制**: 不同角色有不同的操作权限
2. **数据隔离**: 租户数据完全隔离
3. **并发处理**: 支持高并发访问
4. **事务保证**: 关键操作使用数据库事务
5. **日志记录**: 所有操作都有详细日志
# CoachAI 成就系统文档

## 概述

成就系统是CoachAI平台的核心激励模块，用于鼓励用户持续参与运动、完成任务和保持良好习惯。系统通过成就、徽章和奖励三个核心组件，为用户提供可视化的进度跟踪和正向反馈。

## 系统架构

### 核心组件

1. **成就 (Achievement)**
   - 定义用户需要完成的目标
   - 包含触发条件、难度等级和奖励

2. **徽章 (Badge)**
   - 可视化成就的象征
   - 具有稀有度等级和授予条件

3. **奖励 (Reward)**
   - 成就完成的实质性回报
   - 包括积分、物品、权限等

### 数据模型

#### 1. 成就模型 (Achievement)
```python
class Achievement:
    - id: 唯一标识
    - name: 成就名称
    - description: 成就描述
    - achievement_type: 成就类型（运动/任务/连续打卡等）
    - difficulty: 难度等级（简单/中等/困难/传奇）
    - trigger_type: 触发类型
    - trigger_config: 触发条件配置
    - target_value: 目标值
    - reward_points: 奖励积分
    - reward_badge_id: 奖励徽章ID
    - status: 状态（活跃/未激活/已归档）
```

#### 2. 用户成就模型 (UserAchievement)
```python
class UserAchievement:
    - user_id: 用户ID
    - achievement_id: 成就ID
    - status: 状态（未解锁/进行中/已解锁/已完成）
    - progress: 当前进度
    - target_value: 目标值
    - progress_percentage: 进度百分比
    - unlocked_at: 解锁时间
```

#### 3. 徽章模型 (Badge)
```python
class Badge:
    - id: 唯一标识
    - name: 徽章名称
    - description: 徽章描述
    - badge_type: 徽章类型（成就/里程碑/特殊等）
    - rarity: 稀有度（普通/稀有/罕见/史诗/传奇）
    - icon_url: 图标URL
    - grant_condition: 授予条件
```

#### 4. 用户徽章模型 (UserBadge)
```python
class UserBadge:
    - user_id: 用户ID
    - badge_id: 徽章ID
    - granted_at: 授予时间
    - is_equipped: 是否装备
    - is_favorite: 是否收藏
```

#### 5. 奖励模型 (Reward)
```python
class Reward:
    - id: 唯一标识
    - name: 奖励名称
    - description: 奖励描述
    - reward_type: 奖励类型（积分/徽章/物品等）
    - reward_config: 奖励配置
    - value: 奖励价值
    - max_claims: 最大领取次数
    - per_user_limit: 每用户限制次数
```

#### 6. 用户奖励模型 (UserReward)
```python
class UserReward:
    - user_id: 用户ID
    - reward_id: 奖励ID
    - claimed_at: 领取时间
    - reward_data: 奖励数据
    - status: 状态（已领取/已使用/已过期/已撤销）
```

## API接口

### 成就管理

#### 1. 获取成就列表
```
GET /api/v1/achievements
参数:
  - type: 成就类型（可选）
  - difficulty: 难度等级（可选）
  - status: 状态（可选）
  - limit: 每页数量（默认100）
  - offset: 偏移量（默认0）
```

#### 2. 创建成就
```
POST /api/v1/achievements
请求体:
{
  "name": "成就名称",
  "description": "成就描述",
  "achievement_type": "exercise",
  "difficulty": "easy",
  "trigger_type": "exercise_completed",
  "trigger_config": {"min_count": 1},
  "target_value": 1,
  "reward_points": 100
}
```

#### 3. 获取成就详情
```
GET /api/v1/achievements/{achievement_id}
```

#### 4. 更新成就
```
PUT /api/v1/achievements/{achievement_id}
```

#### 5. 删除成就
```
DELETE /api/v1/achievements/{achievement_id}
```

### 用户成就

#### 1. 获取用户成就列表
```
GET /api/v1/user-achievements
GET /api/v1/users/{user_id}/achievements
参数:
  - status: 状态（可选）
  - limit: 每页数量（默认100）
  - offset: 偏移量（默认0）
```

#### 2. 获取用户成就详情
```
GET /api/v1/users/{user_id}/achievements/{achievement_id}
```

#### 3. 更新成就进度
```
POST /api/v1/achievement-progress
请求体:
{
  "user_id": "用户ID",
  "achievement_id": "成就ID",
  "progress_delta": 1,
  "event_type": "exercise_completed",
  "event_data": {"exercise_type": "pushup"}
}
```

#### 4. 获取用户成就统计
```
GET /api/v1/achievement-stats
GET /api/v1/users/{user_id}/achievement-stats
```

### 成就触发

#### 1. 触发成就事件
```
POST /api/v1/achievement-trigger
请求体:
{
  "event_type": "exercise_completed",
  "user_id": "用户ID",
  "event_data": {
    "exercise_type": "pushup",
    "count": 10
  }
}
```

### 徽章管理

#### 1. 授予徽章
```
POST /api/v1/badge-grant
请求体:
{
  "user_id": "用户ID",
  "badge_id": "徽章ID",
  "grant_reason": "授予原因"
}
```

#### 2. 获取用户徽章列表
```
GET /api/v1/user-badges
GET /api/v1/users/{user_id}/badges
```

### 奖励管理

#### 1. 领取奖励
```
POST /api/v1/reward-claim
请求体:
{
  "user_id": "用户ID",
  "reward_id": "奖励ID",
  "claim_reason": "领取原因"
}
```

## 事件类型

系统支持以下事件类型：

### 运动相关事件
- `exercise_completed`: 运动完成
- `exercise_goal_reached`: 运动目标达成
- `exercise_streak_updated`: 运动连续打卡更新

### 任务相关事件
- `task_completed`: 任务完成
- `task_assigned`: 任务分配
- `task_evaluated`: 任务评价完成

### 社交相关事件
- `social_interaction`: 社交互动
- `friend_added`: 添加好友
- `share_completed`: 分享完成

### 系统事件
- `level_up`: 等级提升
- `milestone_reached`: 里程碑达成
- `system_achievement`: 系统成就

## 成就类型

### 1. 运动成就 (Exercise)
- 第一次运动
- 运动爱好者（完成10次运动）
- 运动达人（完成100次运动）
- 特定运动类型专家

### 2. 任务成就 (Task)
- 任务新手（完成第一个任务）
- 任务大师（完成10个任务）
- 高效执行者（连续完成任务）
- 高质量完成者（任务评价优秀）

### 3. 连续打卡成就 (Streak)
- 连续打卡3天
- 连续打卡7天
- 连续打卡30天
- 连续打卡100天

### 4. 里程碑成就 (Milestone)
- 总运动次数里程碑
- 总任务完成里程碑
- 总积分里程碑
- 总徽章收集里程碑

### 5. 特殊成就 (Special)
- 节日限定成就
- 活动限定成就
- 隐藏成就
- 彩蛋成就

## 徽章系统

### 徽章稀有度

1. **普通 (Common)**
   - 基础成就徽章
   - 易于获得
   - 显示基础参与度

2. **稀有 (Uncommon)**
   - 中级成就徽章
   - 需要一定努力
   - 显示进阶参与度

3. **罕见 (Rare)**
   - 高级成就徽章
   - 需要持续努力
   - 显示专业参与度

4. **史诗 (Epic)**
   - 顶级成就徽章
   - 需要卓越表现
   - 显示专家级参与度

5. **传奇 (Legendary)**
   - 传说级徽章
   - 极难获得
   - 显示大师级参与度

### 徽章类型

1. **成就徽章 (Achievement)**
   - 对应具体成就
   - 自动授予

2. **里程碑徽章 (Milestone)**
   - 对应重要里程碑
   - 阶段性奖励

3. **特殊徽章 (Special)**
   - 特殊活动授予
   - 限时获取

4. **活动徽章 (Event)**
   - 活动参与奖励
   - 季节性获取

5. **季节徽章 (Seasonal)**
   - 季节限定
   - 每年重复

## 奖励系统

### 奖励类型

1. **积分奖励 (Points)**
   - 平台通用积分
   - 可用于兑换物品
   - 显示用户等级

2. **徽章奖励 (Badge)**
   - 可视化荣誉
   - 永久收藏
   - 社交展示

3. **物品奖励 (Item)**
   - 虚拟物品
   - 功能增强
   - 个性化装饰

4. **折扣奖励 (Discount)**
   - 平台服务折扣
   - 合作伙伴优惠
   - 限时特权

5. **权限奖励 (Access)**
   - 高级功能权限
   - 专属内容访问
   - 优先服务

### 奖励发放机制

1. **自动发放**
   - 成就解锁时自动发放
   - 无需用户操作
   - 实时到账

2. **手动领取**
   - 需要用户主动领取
   - 有时限要求
   - 可批量领取

3. **条件限制**
   - 最大领取次数限制
   - 每用户限制次数
   - 时间限制

## 触发机制

### 事件驱动架构

成就系统采用事件驱动架构，通过监听平台事件来触发成就进度更新：

```python
# 事件处理流程
1. 用户执行动作（如完成运动）
2. 系统发布事件（exercise_completed）
3. 成就触发器监听事件
4. 匹配相关成就的触发条件
5. 更新用户成就进度
6. 检查是否解锁成就
7. 发放相应奖励
8. 发送通知
```

### 触发条件配置

触发条件使用JSON格式配置，支持灵活的条件组合：

```json
{
  "event_type": "exercise_completed",
  "exercise_type": "pushup",
  "min_count": 10,
  "max_duration": 3600,
  "required_equipment": ["mat"],
  "time_of_day": "morning"
}
```

## 进度计算

### 进度更新算法

```python
def update_progress(user_achievement, progress_delta):
    # 更新当前进度
    user_achievement.progress += progress_delta
    
    # 计算进度百分比
    if user_achievement.target_value > 0:
        percentage = (user_achievement.progress / user_achievement.target_value) * 100
        user_achievement.progress_percentage = min(100, int(percentage))
    
    # 更新状态
    if user_achievement.status == "locked" and user_achievement.progress > 0:
        user_achievement.status = "in_progress"
    
    if user_achievement.progress >= user_achievement.target_value:
        user_achievement.status = "completed"
        user_achievement.completed_at = datetime.now()
```

### 多条件进度

对于需要满足多个条件的成就，系统支持并行进度跟踪：

```json
{
  "conditions": [
    {"type": "exercise_count", "target": 10},
    {"type": "exercise_types", "target": 3, "required": ["pushup", "squat", "plank"]},
    {"type": "streak_days", "target": 7}
  ],
  "logic": "AND"  # 或 "OR"
}
```

## 通知系统

### 成就解锁通知

当用户解锁成就时，系统会发送实时通知：

```json
{
  "type": "achievement_unlocked",
  "user_id": "用户ID",
  "achievement": {
    "id": "成就ID",
    "name": "成就名称",
    "description": "成就描述",
    "icon_url": "图标URL"
  },
  "reward": {
    "points": 100,
    "badge": {
      "id": "徽章ID",
      "name": "徽章名称",
      "icon_url": "徽章图标URL"
    }
  },
  "timestamp": "解锁时间"
}
```

### 通知渠道

1. **应用内通知**
   - 实时弹窗
   - 消息中心
   - 成就页面更新

2. **推送通知**
   - 移动端推送
   - 桌面通知
   - 邮件通知

3. **社交分享**
   - 自动生成分享卡片
   - 社交媒体分享
   - 好友通知

## 数据分析

### 用户成就统计

系统提供详细的用户成就统计数据：

```json
{
  "user_id": "用户ID",
  "stats": {
    "total_achievements": 50,
    "unlocked_achievements": 15,
    "in_progress_achievements": 10,
    "locked_achievements": 25,
    "total_points": 2500,
    "total_badges": 8,
    "completion_rate": 30.0,
    "by_type": {
      "exercise": {"total": 20, "unlocked": 8},
      "task": {"total": 15, "unlocked": 4},
      "streak": {"total": 10, "unlocked": 3},
      "milestone": {"total": 5, "unlocked": 0}
    },
    "by_difficulty": {
      "easy": {"total": 25, "unlocked": 12},
      "medium": {"total": 15, "unlocked": 3},
      "hard": {"total": 8, "unlocked": 0},
      "legendary": {"total": 2, "unlocked": 0}
    }
  }
}
```

### 趋势分析

1. **解锁趋势**
   - 每日/每周/每月解锁数量
   - 解锁速度变化
   - 活跃时间段

2. **难度分布**
   - 各难度成就解锁比例
   - 用户挑战偏好
   - 难度平衡分析

3. **类型分布**
   - 各类成就参与度
   - 用户兴趣分析
   - 内容优化建议

## 性能优化

### 数据库优化

1. **索引策略**
   - 用户ID + 成就ID 复合索引
   - 状态字段索引
   - 时间字段索引

2. **查询优化**
   - 分页查询
   - 延迟加载
   - 缓存策略

3. **批量操作**
   - 批量进度更新
   - 批量奖励发放
   - 批量通知发送

### 缓存策略

1. **成就数据缓存**
   - 热门成就缓存
   - 用户成就状态缓存
   - 徽章数据缓存

2. **统计结果缓存**
   - 用户统计缓存
   - 全局统计缓存
   - 排行榜缓存

## 安全考虑

### 数据安全

1. **权限控制**
   - 用户只能访问自己的成就数据
   - 管理员权限分级
   - API访问控制

2. **数据验证**
   - 输入数据验证
   - 进度更新验证
   - 奖励发放验证

### 防作弊机制

1. **进度验证**
   - 事件来源验证
   - 进度合理性检查
   - 时间间隔限制

2. **奖励防重**
   - 唯一性检查
   - 领取次数限制
   - 时间窗口限制

## 部署指南

### 环境要求

1. **数据库**
   - MySQL 5.7+ 或 PostgreSQL 10+
   - 支持JSON字段
   - 足够的存储空间

2. **应用服务器**
   - Python 3.8+
   - Tornado 6.0+
   - 足够的内存和CPU

3. **缓存服务器**
   - Redis 5.0+
   - 用于会话和缓存

### 配置步骤

1. **数据库迁移**
   ```bash
   python scripts/create_achievement_tables.py
   ```

2. **示例数据**
   ```bash
   python scripts/create_achievement_tables.py
   ```

3. **服务启动**
   ```bash
   python main.py
   ```

## 监控和维护

### 监控指标

1. **性能指标**
   - API响应时间
   - 数据库查询性能
   - 缓存命中率

2. **业务指标**
   - 成就解锁率
   - 用户参与度
   - 奖励发放量

3. **错误监控**
   - API错误率
   - 数据库错误
   - 系统异常

### 维护任务

1. **定期清理**
   - 过期奖励清理
   - 日志文件清理
   - 缓存数据清理

2. **数据备份**
   - 成就数据备份
   - 用户数据备份
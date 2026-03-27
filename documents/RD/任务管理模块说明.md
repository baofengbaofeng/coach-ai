# 任务管理模块

## 模块概述

任务管理模块是CoachAI系统的核心模块之一，负责管理学员的任务生命周期，包括任务创建、分配、提交、评价和智能调度。

## 功能特性

### 1. 任务管理
- 创建、查看、更新、删除任务
- 任务分类：作业任务、运动任务、自定义任务
- 任务状态管理：草稿、活跃、完成、取消、归档
- 优先级和难度设置

### 2. 任务分配
- 将任务分配给学员
- 进度跟踪和更新
- 分配状态管理：已分配、进行中、已完成、已取消、已过期

### 3. 任务提交
- 学员提交任务成果
- 多版本提交支持
- 提交内容多样化：文本、文件、运动数据等
- 提交状态管理：已提交、已审核、已返回、已接受、已拒绝

### 4. 任务评价
- 教练对任务完成情况进行评价
- 多维度评分系统
- 评语和改进建议
- 评价状态管理：草稿、已发布、已归档

### 5. 智能调度
- 基于学员能力的任务推荐
- 考虑时间、优先级、依赖关系的调度算法
- 自动任务分配
- 进度预测和提醒

### 6. 数据分析
- 任务完成率统计
- 学员能力成长跟踪
- 任务质量评估
- 效率分析和优化建议

## 技术架构

### 数据库设计
- **tasks**: 任务主表
- **task_assignments**: 任务分配表
- **task_submissions**: 任务提交表
- **task_evaluations**: 任务评价表

### 服务层
- **TaskService**: 任务管理服务
- **TaskAssignmentService**: 任务分配服务
- **TaskSubmissionService**: 任务提交服务
- **TaskEvaluationService**: 任务评价服务
- **TaskSchedulerService**: 智能调度服务
- **TaskAnalyticsService**: 数据分析服务

### API接口
- RESTful API设计
- JWT认证和授权
- 请求验证和错误处理
- 分页和过滤支持

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 创建数据库表
```bash
python scripts/create_task_tables.py
```

### 3. 运行测试
```bash
# 单元测试
pytest tests/unit/tasks/test_task_models.py -v

# 集成测试
pytest tests/integration/tasks/test_task_api.py -v
```

### 4. 启动服务
```bash
python code/main.py
```

## API使用示例

### 创建任务
```python
import requests

# 认证
headers = {"Authorization": "Bearer {token}"}

# 创建任务
task_data = {
    "title": "数学作业",
    "description": "完成第一章练习题",
    "task_type": "homework",
    "priority": "medium",
    "difficulty": "beginner"
}

response = requests.post(
    "http://localhost:8888/api/v1/tasks",
    json=task_data,
    headers=headers
)

print(response.json())
```

### 分配任务
```python
assignment_data = {
    "task_id": "task-uuid",
    "student_id": "student-uuid",
    "assignment_notes": "请认真完成"
}

response = requests.post(
    "http://localhost:8888/api/v1/task-assignments",
    json=assignment_data,
    headers=headers
)

print(response.json())
```

### 提交任务
```python
submission_data = {
    "assignment_id": "assignment-uuid",
    "content": {
        "type": "text",
        "text": "这是我的作业"
    },
    "is_final": True
}

response = requests.post(
    "http://localhost:8888/api/v1/task-submissions",
    json=submission_data,
    headers=headers
)

print(response.json())
```

## 智能调度算法

### 调度规则
1. **能力匹配**: 根据学员历史表现匹配合适难度的任务
2. **优先级排序**: 紧急和高优先级任务优先安排
3. **时间优化**: 考虑任务截止时间和学员可用时间
4. **负载均衡**: 避免单日任务过多，合理分配工作量

### 调度流程
```
1. 分析学员能力水平
2. 筛选适合的任务池
3. 根据规则排序任务
4. 分配到时间窗口
5. 生成调度计划
```

## 数据分析指标

### 1. 完成率分析
- 总体完成率
- 按时完成率
- 按类型完成率
- 按难度完成率

### 2. 质量评估
- 平均评分
- 评分趋势
- 能力成长曲线
- 薄弱环节识别

### 3. 效率分析
- 平均完成时间
- 延期分析
- 资源利用率
- 瓶颈识别

## 开发指南

### 1. 添加新字段
```python
# 在相应的模型文件中添加字段
class Task(BaseModel):
    # 添加新字段
    new_field = Column(String(100), nullable=True)
```

### 2. 添加新API
```python
# 在handlers.py中添加新的处理器方法
class TaskHandler(BaseHandler):
    @auth_required
    async def new_endpoint(self):
        # 实现新的端点逻辑
        pass
```

### 3. 添加新服务
```python
# 在services.py中添加新的服务类
class NewService:
    def __init__(self, db: Session):
        self.db = db
    
    def new_method(self):
        # 实现新的业务逻辑
        pass
```

## 测试指南

### 1. 单元测试
```bash
# 运行所有单元测试
pytest tests/unit/tasks/ -v

# 运行特定测试
pytest tests/unit/tasks/test_task_models.py::TestTaskModel -v
```

### 2. 集成测试
```bash
# 运行所有集成测试
pytest tests/integration/tasks/ -v

# 运行API测试
pytest tests/integration/tasks/test_task_api.py::TestTaskAPI -v
```

### 3. 测试覆盖率
```bash
# 生成覆盖率报告
pytest --cov=code.tornado.modules.tasks tests/ -v
```

## 部署说明

### 1. 环境要求
- Python 3.8+
- MySQL 5.7+
- Redis（可选，用于缓存）

### 2. 配置说明
```env
# 数据库配置
DATABASE_URL=mysql://user:password@localhost/coachai

# 应用配置
APP_DEBUG=false
APP_SECRET_KEY=your-secret-key

# 任务调度配置
TASK_SCHEDULER_ENABLED=true
MAX_TASKS_PER_DAY=5
```

### 3. 性能优化
- 数据库索引优化
- 查询缓存
- 异步处理
- 负载均衡

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否运行
   - 验证连接字符串
   - 检查网络连接

2. **认证失败**
   - 检查token是否有效
   - 验证用户权限
   - 检查认证中间件配置

3. **性能问题**
   - 检查数据库索引
   - 优化查询语句
   - 启用缓存

### 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log
```

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送分支
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。详见LICENSE文件。
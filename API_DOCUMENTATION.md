# CoachAI API 文档

## 📋 概述

CoachAI是一个智能教练系统，提供运动管理、任务管理、成就系统和AI智能服务。本文档描述了系统的RESTful API接口。

## 🚀 快速开始

### 基础URL
- 开发环境: `http://localhost:8000/api/v1`
- 生产环境: `https://api.coachai.example.com/api/v1`

### 认证方式
所有受保护的API端点都需要认证。支持以下认证方式：

1. **JWT Token认证** (推荐)
   ```http
   Authorization: Bearer <your_jwt_token>
   ```

2. **Session认证**
   ```http
   Cookie: sessionid=<your_session_id>
   ```

3. **Basic认证**
   ```http
   Authorization: Basic <base64_encoded_credentials>
   ```

### 响应格式
所有API响应都遵循统一的JSON格式：

**成功响应**:
```json
{
  "success": true,
  "data": {...},
  "message": "操作成功",
  "timestamp": "2026-03-24T10:30:00Z"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "validation_error",
    "message": "请求数据验证失败",
    "details": {...}
  },
  "timestamp": "2026-03-24T10:30:00Z"
}
```

## 📊 API端点

### AI服务端点

#### 1. 获取AI推荐
```http
POST /api/v1/ai/recommendation/
```

**请求参数**:
```json
{
  "recommendation_type": "all",
  "max_recommendations": 5,
  "similarity_threshold": 0.6,
  "diversity_factor": 0.3
}
```

**响应示例**:
```json
{
  "success": true,
  "user_id": 1,
  "username": "test_user",
  "recommendation_type": "all",
  "total_count": 5,
  "generated_at": "2026-03-24T10:30:00Z",
  "recommendations": [
    {
      "id": "rec_001",
      "title": "晨跑30分钟",
      "description": "基于您的运动习惯推荐",
      "type": "exercise",
      "score": 0.85,
      "confidence": 0.8
    }
  ]
}
```

#### 2. 获取AI分析
```http
POST /api/v1/ai/analysis/
```

**请求参数**:
```json
{
  "analysis_type": "comprehensive",
  "period_days": 30
}
```

#### 3. 获取AI预测
```http
POST /api/v1/ai/prediction/
```

**请求参数**:
```json
{
  "prediction_type": "all",
  "horizon_days": 7
}
```

#### 4. 获取AI服务状态
```http
GET /api/v1/ai/status/
```

### 系统服务端点

#### 1. 健康检查
```http
GET /api/v1/health/
```

**响应示例**:
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2026-03-24T10:30:00Z",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "api": "healthy"
  }
}
```

#### 2. 系统状态
```http
GET /api/v1/status/
```

#### 3. API信息
```http
GET /api/v1/info/
```

## 🔧 开发指南

### 环境设置
1. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

2. 配置环境变量:
   ```bash
   cp .env.example .env
   # 编辑.env文件配置数据库和密钥
   ```

3. 运行开发服务器:
   ```bash
   python manage.py runserver
   ```

### 代码示例

**Python示例**:
```python
import requests

# 获取AI推荐
response = requests.post(
    'http://localhost:8000/api/v1/ai/recommendation/',
    json={'recommendation_type': 'all', 'max_recommendations': 5},
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
print(response.json())
```

**JavaScript示例**:
```javascript
fetch('http://localhost:8000/api/v1/ai/recommendation/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: JSON.stringify({
    recommendation_type: 'all',
    max_recommendations: 5
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

**cURL示例**:
```bash
curl -X POST \
  http://localhost:8000/api/v1/ai/recommendation/ \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"recommendation_type": "all", "max_recommendations": 5}'
```

## 🛡️ 安全指南

### 认证和授权
1. 所有敏感操作都需要认证
2. 使用HTTPS在生产环境
3. 定期轮换JWT密钥

### 速率限制
- 默认限制: 1000请求/小时
- 认证用户: 5000请求/小时
- 管理员: 10000请求/小时

### 数据验证
- 所有输入数据都经过验证
- 使用类型安全的序列化器
- 防止SQL注入和XSS攻击

## 📈 性能指标

### 响应时间
- AI推荐: < 100ms
- AI分析: < 200ms
- AI预测: < 150ms
- 健康检查: < 50ms

### 可用性
- 目标: 99.9%可用性
- 监控: 实时性能监控
- 告警: 自动故障检测

## 🔍 故障排除

### 常见问题

1. **401未授权错误**
   - 检查Token是否有效
   - 确认Token未过期
   - 验证认证头格式

2. **400请求参数错误**
   - 检查请求参数格式
   - 验证参数类型和范围
   - 查看错误详情

3. **500服务器内部错误**
   - 检查服务器日志
   - 确认数据库连接
   - 验证服务配置

### 调试工具
1. API日志: `/var/log/coachai/api.log`
2. 错误跟踪: Sentry集成
3. 性能监控: NewRelic集成

## 📚 相关资源

### 文档
- [OpenAPI规范](openapi_spec.json)
- [数据库设计](docs/database.md)
- [部署指南](docs/deployment.md)

### 工具
- [API测试工具](tools/api_tester.py)
- [性能测试脚本](tools/performance_test.py)
- [数据迁移工具](tools/migration_tool.py)

### 支持
- 问题反馈: GitHub Issues
- 技术支持: support@coachai.example.com
- 社区讨论: Discord社区

## 🎯 版本历史

### v1.0.0 (2026-03-24)
- 初始版本发布
- 完整的AI服务API
- 系统管理API
- 完整的文档

### v0.9.0 (2026-03-23)
- Beta版本
- 基础AI功能
- 初步API设计

## 📄 许可证

本项目采用MIT许可证。详见[LICENSE](LICENSE)文件。

---

**最后更新**: 2026-03-24  
**文档版本**: 1.0.0  
**API版本**: 1.0.0
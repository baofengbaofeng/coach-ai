# CoachAI - 智能伴读AI系统

![CoachAI Logo](docs/images/logo.png)

## 项目简介

CoachAI 是一个集智能作业批改、动作识别计数、语音交互和任务管理于一体的智能伴读AI系统。通过摄像头和麦克风等外设，为学生提供个性化、互动式的学习陪伴体验。

## 核心功能

### 1. 智能作业批改
- 通过摄像头拍摄作业，自动识别题目和答案
- 智能批改与知识点分析
- 生成学习报告和薄弱点分析

### 2. 动作识别计数
- 实时识别跳绳、俯卧撑等运动动作
- 自动计数和姿势纠正
- 运动数据统计和分析

### 3. 语音交互系统
- 语音唤醒和自然语言指令
- 语音反馈和交互
- 支持多轮对话

### 4. 任务管理系统
- 每日TODO列表管理
- 任务进度跟踪
- 成就系统和激励机制

## 技术架构 (简化版本)

### 前端
- React 18 + TypeScript
- Ant Design / Chakra UI
- Vite 构建工具

### 后端
- Python + Django 5.0
- MySQL 8.0 (主数据库)
- 无中间件架构 (简化部署)
- Docker 容器化

### AI服务
- PaddleOCR / EasyOCR (OCR识别)
- OpenCV + MediaPipe (计算机视觉)
- Whisper / SpeechRecognition (语音识别)
- 基于数据库的异步任务处理

## 项目结构 (标准 src 布局)

```
coach-ai/
├── src/                         # 所有源代码
│   ├── coachai/                 # Django项目配置
│   │   ├── settings/           # 多环境配置
│   │   ├── urls.py             # URL路由
│   │   ├── wsgi.py             # WSGI配置
│   │   └── asgi.py             # ASGI配置
│   ├── apps/                   # Django应用
│   │   ├── accounts/           # 用户管理
│   │   ├── homework/           # 作业管理
│   │   ├── exercise/           # 运动管理
│   │   ├── tasks/              # 任务管理
│   │   ├── achievements/       # 成就系统
│   │   └── common/             # 公共组件
│   ├── services/               # AI服务层
│   └── utils/                  # 工具函数
├── tests/                       # 测试代码
│   ├── unit/                   # 单元测试
│   ├── integration/            # 集成测试
│   └── performance/            # 性能测试
├── documents/                   # 项目文档
├── convention/                  # 编码规范
├── scripts/                     # 部署脚本
├── pyproject.toml              # 依赖管理 (Poetry)
├── manage.py                   # Django管理脚本
├── .env.example                # 环境变量示例
├── .gitignore                  # Git忽略文件
├── README.md                   # 项目说明
└── LICENSE                     # GPL v3许可证
```

## 快速开始

### 环境要求
- Python 3.11+
- Poetry 1.7+
- MySQL 8.0+ (可选，开发环境可用SQLite)
- Redis 7.0+ (可选，开发环境可用虚拟缓存)

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/your-username/coach-ai.git
cd coach-ai

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell

# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件配置环境变量
# 注意：开发环境可以使用默认值

# 运行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

### 访问应用
- Web界面: http://localhost:8000
- API文档: http://localhost:8000/swagger/
- Admin后台: http://localhost:8000/admin/

## 开发指南

### 代码规范
本项目采用严格的编码规范，详见 [convention/coding-style.md](convention/coding-style.md)。

主要规范包括：
- 标准 src 源码布局
- 严格的类型注解
- 完整的文档字符串
- 统一的导入顺序
- 详细的错误处理

### 测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/unit/test_models.py

# 生成测试覆盖率报告
pytest --cov=src --cov-report=html

# 运行性能测试
locust -f tests/performance/test_load.py
```

### 代码质量检查
```bash
# 代码格式化
black .

# 代码检查
flake8

# 类型检查 (需要安装 mypy)
mypy src
```

### 代码提交
```bash
# 格式化代码
black .

# 检查代码质量
flake8

# 运行测试
pytest

# 提交代码
git add .
git commit -m "feat: 添加新功能"
git push
```

## 部署指南

### 生产环境部署
1. 配置生产环境变量
2. 设置SSL证书
3. 配置域名和DNS
4. 使用Docker Compose部署

### Docker 部署
```bash
# 构建镜像
docker build -t coachai .

# 使用 Docker Compose
docker-compose up -d
```

### 监控和维护
- 日志查看: `docker-compose logs -f`
- 数据库备份: `./scripts/backup_database.sh`
- 服务重启: `docker-compose restart`

## 贡献指南

我们欢迎各种形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与项目开发。

### 开发流程
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

### 代码规范
- 遵循PEP 8 Python代码规范
- 使用类型提示(Type Hints)
- 编写清晰的文档字符串
- 添加适当的测试用例

## 许可证

本项目采用 [GNU General Public License v3.0](LICENSE)。

### 开源要求
- 本项目代码必须持续开源
- 任何基于本项目的衍生作品也必须开源
- 禁止将本项目用于闭源商业用途

## 联系方式

- 项目发起人: baofengbaofeng
- 项目仓库: https://github.com/your-username/coach-ai
- 问题反馈: 请使用 [GitHub Issues](https://github.com/your-username/coach-ai/issues)

## 相关链接

- [项目文档](documents/)
- [API文档](http://localhost:8000/swagger/)
- [部署指南](docs/deployment.md)
- [开发指南](docs/development.md)

---

**CoachAI - Your Personal AI Learning Coach**

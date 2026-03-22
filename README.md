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

## 技术架构 (豆包AI助手最佳实践)

### 前端
- React 18 + TypeScript
- Ant Design / Chakra UI
- Vite 构建工具

### 后端 (豆包最佳实践)
- **Python + Django 5.0** - 企业级Web框架
- **MySQL 8.0** - 主数据库，支持事务和复杂查询
- **无中间件架构** - 简化部署，使用数据库表实现缓存和队列功能
- **豆包标准结构** - 遵循豆包AI助手推荐的Django项目结构最佳实践
- **多环境配置** - 开发/生产环境分离，安全配置管理

### AI服务
- **PaddleOCR / EasyOCR** - OCR识别，支持中英文作业批改
- **OpenCV + MediaPipe** - 计算机视觉，实时动作识别和姿势评估
- **Whisper / SpeechRecognition** - 语音识别，支持语音唤醒和交互
- **数据库驱动异步** - 基于数据库表的异步任务处理，简化架构

### 架构特点
1. **企业级标准** - 大厂通用、可直接落地、支持大型项目迭代
2. **松耦合设计** - 配置拆分、应用集中、全局公共层分离
3. **高可维护性** - 结构清晰，新人快速上手，便于团队协作
4. **易测试扩展** - 业务逻辑与视图分离，便于单元测试和功能扩展
5. **安全规范** - 环境变量管理，敏感信息不硬编码，生产环境安全配置

## 项目结构 (豆包AI助手最佳实践)

```
coach-ai/                      # 项目根目录（Git 仓库根目录）
├── .env                      # 环境变量（本地开发，不上传 Git）
├── .env.example              # 环境变量模板（上传 Git）
├── .gitignore                # Git 忽略文件
├── manage.py                 # Django 管理脚本
├── pyproject.toml            # 依赖管理（替代 requirements.txt）
├── README.md                 # 项目说明
├── config/                   # 项目核心配置（重命名默认的 project 目录）
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py               # 根路由（只做分发，不写业务路由）
│   ├── settings/             # 拆分配置文件（核心优化）
│   │   ├── __init__.py
│   │   ├── base.py           # 公共基础配置
│   │   ├── dev.py            # 开发环境配置
│   │   └── prod.py           # 生产环境配置
├── apps/                     # 所有业务应用统一存放（核心优化）
│   ├── __init__.py
│   ├── accounts/             # 用户账户模块
│   ├── homework/             # 作业管理模块
│   ├── exercise/             # 运动管理模块
│   ├── tasks/                # 任务管理模块
│   ├── achievements/         # 成就系统模块
│   └── common/               # 公共核心模块（基类、工具）
├── core/                     # 项目全局公共层
│   ├── __init__.py
│   ├── constants.py          # 全局常量
│   ├── exceptions.py         # 全局异常处理
│   ├── middlewares.py        # 自定义中间件
│   ├── paginations.py        # 通用分页
│   ├── responses.py          # 统一返回格式
│   └── utils.py              # 全局工具函数
├── services/                 # AI 服务层
├── utils/                    # 工具函数层
├── templates/                # 全局模板（前后端分离可删除）
├── static/                   # 全局静态文件
├── media/                    # 用户上传文件（自动生成）
├── logs/                     # 日志文件（自动生成）
├── tests/                    # 全局测试用例
├── docs/                     # 项目文档
└── .rules/                  # 编码规范和项目规则
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
本项目采用严格的编码规范，详见 [.rules/coding-style.md](.rules/coding-style.md)。

主要规范包括：
- **豆包最佳实践结构** - 遵循豆包AI助手推荐的Django项目结构
- **严格的类型注解** - 所有函数必须标注参数类型和返回类型
- **完整的文档字符串** - 包含Args、Returns、Raises部分，注释长度规范
- **统一的导入顺序** - Python标准库 → 第三方库 → 项目内部
- **详细的错误处理** - 禁止裸except，使用异常链，资源自动释放
- **安全开发规范** - 禁止硬编码敏感信息，输入验证和转义
- **性能优化要求** - 禁止循环内IO操作，使用批量处理和生成器

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

- [项目文档](docs/)
- [API文档](http://localhost:8000/swagger/)
- [部署指南](docs/deployment.md) (待创建)
- [开发指南](docs/development.md) (待创建)
- [技术设计文档](docs/TECH_DETAILED_DESIGN.md)
- [产品需求文档](docs/PRD.md)
- [商业需求文档](docs/BRD.md)

---

**CoachAI - Your Personal AI Learning Coach**

# CoachAI Makefile

.PHONY: help install dev test lint format type-check clean run setup-db

# 默认目标
help:
	@echo "CoachAI 项目管理命令"
	@echo ""
	@echo "可用命令:"
	@echo "  make install     安装Python依赖"
	@echo "  make dev         安装开发依赖"
	@echo "  make run         启动开发服务器"
	@echo "  make test        运行测试"
	@echo "  make lint        代码质量检查"
	@echo "  make format      代码格式化"
	@echo "  make type-check  类型检查"
	@echo "  make clean       清理临时文件"
	@echo "  make setup-db    设置数据库（需要手动配置）"
	@echo "  make help        显示此帮助信息"

# 安装生产依赖
install:
	pip install -r requirements.txt

# 安装开发依赖
dev:
	pip install -r requirements.txt
	pip install black flake8 mypy isort pytest pytest-asyncio pytest-cov

# 启动开发服务器
run:
	python code/main.py

# 运行测试
test:
	pytest tests/ -v

# 运行测试并生成覆盖率报告
test-cov:
	pytest tests/ --cov=code --cov-report=html --cov-report=term

# 代码质量检查
lint:
	flake8 code/
	black --check code/

# 代码格式化
format:
	black code/
	isort code/

# 类型检查
type-check:
	mypy code/

# 清理临时文件
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/ .coverage

# 数据库设置（需要手动执行SQL）
setup-db:
	@echo "请手动执行以下SQL命令："
	@echo ""
	@echo "1. 创建数据库："
	@echo "   mysql -u root -p -e \"CREATE DATABASE coach_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\""
	@echo ""
	@echo "2. 创建用户（根据.env配置）："
	@echo "   mysql -u root -p -e \"CREATE USER 'coach_ai_user'@'localhost' IDENTIFIED BY 'your_password';\""
	@echo "   mysql -u root -p -e \"GRANT ALL PRIVILEGES ON coach_ai.* TO 'coach_ai_user'@'localhost';\""
	@echo "   mysql -u root -p -e \"FLUSH PRIVILEGES;\""
	@echo ""
	@echo "3. 初始化数据库表（待实现）"

# 预提交检查
pre-commit: lint type-check

# 开发环境完整设置
setup: dev format lint type-check
	@echo "开发环境设置完成！"
	@echo "请确保："
	@echo "1. 已配置 .env 文件"
	@echo "2. 数据库已创建"
	@echo "3. Redis和RabbitMQ服务已启动"
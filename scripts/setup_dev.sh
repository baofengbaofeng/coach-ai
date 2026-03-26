#!/bin/bash

# CoachAI开发环境设置脚本

set -e

echo "🚀 开始设置CoachAI开发环境..."

# 检查Python版本
echo "🔍 检查Python版本..."
python_version=$(python3 --version | cut -d' ' -f2)
required_version="3.8.0"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python版本满足要求: $python_version"
else
    echo "❌ Python版本过低: $python_version，需要 >= $required_version"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "🔧 创建虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "🔧 升级pip..."
pip install --upgrade pip

# 安装依赖
echo "📦 安装Python依赖..."
pip install -r requirements.txt

# 检查MySQL
echo "🔍 检查MySQL..."
if command -v mysql &> /dev/null; then
    echo "✅ MySQL已安装"
else
    echo "⚠️  MySQL未安装，请手动安装MySQL 5.8+"
fi

# 检查Redis
echo "🔍 检查Redis..."
if command -v redis-cli &> /dev/null; then
    echo "✅ Redis已安装"
    
    # 测试Redis连接
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis服务运行正常"
    else
        echo "⚠️  Redis服务未运行，请启动Redis服务"
    fi
else
    echo "⚠️  Redis未安装，请手动安装Redis"
fi

# 检查RabbitMQ
echo "🔍 检查RabbitMQ..."
if command -v rabbitmqctl &> /dev/null; then
    echo "✅ RabbitMQ已安装"
    
    # 检查RabbitMQ状态
    if rabbitmqctl status &> /dev/null; then
        echo "✅ RabbitMQ服务运行正常"
    else
        echo "⚠️  RabbitMQ服务未运行，请启动RabbitMQ服务"
    fi
else
    echo "⚠️  RabbitMQ未安装，请手动安装RabbitMQ"
fi

# 创建环境配置文件
echo "📝 创建环境配置文件..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ 环境配置文件已创建 (.env)"
    echo "⚠️  请编辑 .env 文件配置数据库连接等信息"
else
    echo "✅ 环境配置文件已存在 (.env)"
fi

# 创建日志目录
echo "📁 创建日志目录..."
mkdir -p logs
echo "✅ 日志目录创建成功"

# 安装开发工具
echo "🔧 安装开发工具..."
pip install black flake8 mypy isort pytest pytest-asyncio pytest-cov

# 创建git hooks
echo "🔧 配置git hooks..."
if [ -d ".git" ]; then
    # 创建pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

echo "🔍 运行代码检查..."

# 运行black检查格式
echo "📝 检查代码格式..."
black --check code/

if [ $? -ne 0 ]; then
    echo "❌ 代码格式检查失败，请运行 'black code/' 修复格式"
    exit 1
fi

# 运行flake8检查代码质量
echo "🔬 检查代码质量..."
flake8 code/

if [ $? -ne 0 ]; then
    echo "❌ 代码质量检查失败"
    exit 1
fi

# 运行mypy检查类型
echo "📊 检查类型注解..."
mypy code/

if [ $? -ne 0 ]; then
    echo "⚠️  类型检查有警告，但允许提交"
fi

echo "✅ 所有检查通过"
EOF

    chmod +x .git/hooks/pre-commit
    echo "✅ Git pre-commit hook配置成功"
else
    echo "⚠️  Git仓库未初始化，跳过git hooks配置"
fi

echo ""
echo "🎉 开发环境设置完成！"
echo ""
echo "下一步："
echo "1. 编辑 .env 文件配置数据库连接"
echo "2. 创建数据库: mysql -u root -p -e \"CREATE DATABASE coach_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\""
echo "3. 启动服务: python code/main.py"
echo "4. 访问健康检查: curl http://localhost:8888/api/health"
echo ""
echo "常用命令："
echo "  • 启动服务: python code/main.py"
echo "  • 运行测试: pytest"
echo "  • 代码格式化: black code/"
echo "  • 代码检查: flake8 code/"
echo "  • 类型检查: mypy code/"
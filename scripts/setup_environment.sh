#!/bin/bash
# CoachAI 环境设置脚本（DDD迁移版）
# 设置开发环境和依赖

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "CoachAI环境设置脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示此帮助信息"
    echo "  -e, --env ENV       环境类型 (dev, test, prod)"
    echo "  -i, --install       安装Python依赖"
    echo "  -v, --venv          创建Python虚拟环境"
    echo "  -d, --db            初始化数据库"
    echo "  -t, --test          运行测试"
    echo "  -c, --clean         清理临时文件"
    echo "  --all               执行所有设置步骤"
    echo ""
    echo "示例:"
    echo "  $0 --all            # 完整设置环境"
    echo "  $0 -i -d            # 安装依赖并初始化数据库"
    echo "  $0 --test           # 运行测试"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "命令 $1 未找到，请先安装"
        exit 1
    fi
}

# 获取项目根目录
get_project_root() {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
}

# 创建Python虚拟环境
create_virtualenv() {
    log_info "创建Python虚拟环境..."
    
    local project_root=$(get_project_root)
    local venv_dir="$project_root/venv"
    
    if [[ -d "$venv_dir" ]]; then
        log_warning "虚拟环境已存在: $venv_dir"
        read -p "是否重新创建？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return 0
        fi
        rm -rf "$venv_dir"
    fi
    
    check_command python3
    
    # 检查Python版本
    python_version=$(python3 --version | cut -d' ' -f2)
    log_info "Python版本: $python_version"
    
    # 创建虚拟环境
    python3 -m venv "$venv_dir"
    
    if [[ $? -eq 0 ]]; then
        log_success "虚拟环境创建完成: $venv_dir"
        echo ""
        echo "激活虚拟环境:"
        echo "  source $venv_dir/bin/activate"
    else
        log_error "虚拟环境创建失败"
        exit 1
    fi
}

# 安装Python依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    local project_root=$(get_project_root)
    local requirements_file="$project_root/src/requirements.txt"
    
    if [[ ! -f "$requirements_file" ]]; then
        log_error "依赖文件不存在: $requirements_file"
        exit 1
    fi
    
    # 检查是否在虚拟环境中
    if [[ -z "$VIRTUAL_ENV" ]]; then
        log_warning "未在虚拟环境中，建议先激活虚拟环境"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
    fi
    
    # 升级pip
    log_info "升级pip..."
    pip install --upgrade pip
    
    # 安装依赖
    log_info "安装依赖包..."
    pip install -r "$requirements_file"
    
    if [[ $? -eq 0 ]]; then
        log_success "依赖安装完成"
        
        # 显示已安装的包
        echo ""
        log_info "已安装的主要包:"
        pip list | grep -E "(tornado|sqlalchemy|mysql|redis|loguru|pydantic|jwt|bcrypt)"
    else
        log_error "依赖安装失败"
        exit 1
    fi
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    local project_root=$(get_project_root)
    
    # 检查数据库配置
    if [[ ! -f "$project_root/.env" ]]; then
        log_warning "环境配置文件不存在，创建示例配置..."
        cp "$project_root/.env.example" "$project_root/.env"
        log_info "请编辑 $project_root/.env 文件配置数据库连接"
        return 1
    fi
    
    # 加载环境变量
    source "$project_root/.env"
    
    # 检查MySQL客户端
    check_command mysql
    
    log_info "创建数据库: ${DB_NAME:-coach_ai}"
    
    # 创建数据库
    mysql -u "${DB_USER:-root}" -p"${DB_PASSWORD:-}" -e "
        CREATE DATABASE IF NOT EXISTS ${DB_NAME:-coach_ai} 
        CHARACTER SET utf8mb4 
        COLLATE utf8mb4_unicode_ci;
        
        CREATE USER IF NOT EXISTS '${DB_USER:-coach_ai_user}'@'localhost' 
        IDENTIFIED BY '${DB_PASSWORD:-coach_ai_password}';
        
        GRANT ALL PRIVILEGES ON ${DB_NAME:-coach_ai}.* 
        TO '${DB_USER:-coach_ai_user}'@'localhost';
        
        FLUSH PRIVILEGES;
    "
    
    if [[ $? -eq 0 ]]; then
        log_success "数据库创建完成"
        
        # 运行数据库迁移
        log_info "运行数据库迁移..."
        cd "$project_root"
        python -c "
from src.infrastructure.db.connection import init_database
from src.infrastructure.db.migrations import run_migrations

db_manager = init_database()
run_migrations(db_manager)
print('数据库迁移完成')
        "
        
        if [[ $? -eq 0 ]]; then
            log_success "数据库迁移完成"
        else
            log_error "数据库迁移失败"
            return 1
        fi
    else
        log_error "数据库创建失败"
        return 1
    fi
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    local project_root=$(get_project_root)
    
    check_command pytest
    
    cd "$project_root"
    
    # 运行单元测试
    log_info "运行单元测试..."
    pytest tests/unit/ -v
    
    # 运行集成测试
    log_info "运行集成测试..."
    pytest tests/integration/ -v
    
    # 运行API测试
    log_info "运行API测试..."
    pytest tests/api/ -v
    
    log_success "测试完成"
}

# 清理临时文件
cleanup() {
    log_info "清理临时文件..."
    
    local project_root=$(get_project_root)
    
    # 清理Python缓存文件
    find "$project_root" -type f -name "*.pyc" -delete
    find "$project_root" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    # 清理测试缓存
    rm -rf "$project_root/.pytest_cache"
    rm -rf "$project_root/.coverage"
    
    # 清理日志文件
    rm -f "$project_root"/*.log 2>/dev/null || true
    
    # 清理上传文件
    rm -rf "$project_root/uploads/*" 2>/dev/null || true
    
    log_success "清理完成"
}

# 显示环境信息
show_environment() {
    log_info "环境信息:"
    
    local project_root=$(get_project_root)
    
    echo "项目根目录: $project_root"
    echo "Python路径: $(which python3)"
    echo "Python版本: $(python3 --version 2>/dev/null || echo '未安装')"
    echo "虚拟环境: ${VIRTUAL_ENV:-未激活}"
    echo ""
    
    # 检查主要依赖
    log_info "检查主要依赖:"
    
    local deps=("tornado" "sqlalchemy" "mysql-connector-python" "redis" "loguru" "pydantic")
    
    for dep in "${deps[@]}"; do
        if python3 -c "import $dep" 2>/dev/null; then
            echo "  ✅ $dep"
        else
            echo "  ❌ $dep"
        fi
    done
    
    echo ""
    
    # 检查数据库连接
    log_info "检查数据库连接:"
    if [[ -f "$project_root/.env" ]]; then
        source "$project_root/.env"
        if mysql -u "${DB_USER:-root}" -p"${DB_PASSWORD:-}" -e "SELECT 1" 2>/dev/null; then
            echo "  ✅ MySQL连接正常"
        else
            echo "  ❌ MySQL连接失败"
        fi
    else
        echo "  ⚠️  未找到环境配置文件"
    fi
}

# 启动开发服务器
start_dev_server() {
    log_info "启动开发服务器..."
    
    local project_root=$(get_project_root)
    
    cd "$project_root"
    
    # 检查是否在虚拟环境中
    if [[ -z "$VIRTUAL_ENV" ]]; then
        log_warning "建议在虚拟环境中运行"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
    fi
    
    # 启动服务器
    log_info "启动CoachAI服务器..."
    echo "访问地址: http://localhost:8888"
    echo "API文档: http://localhost:8888/api/docs"
    echo "健康检查: http://localhost:8888/api/health"
    echo ""
    echo "按 Ctrl+C 停止服务器"
    echo ""
    
    python src/main.py
}

# 主函数
main() {
    local do_venv=false
    local do_install=false
    local do_db=false
    local do_test=false
    local do_clean=false
    local do_all=false
    local do_server=false
    local env_type="dev"
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -e|--env)
                env_type="$2"
                shift 2
                ;;
            -v|--venv)
                do_venv=true
                shift
                ;;
            -i|--install)
                do_install=true
                shift
                ;;
            -d|--db)
                do_db=true
                shift
                ;;
            -t|--test)
                do_test=true
                shift
                ;;
            -c|--clean)
                do_clean=true
                shift
                ;;
            --all)
                do_all=true
                shift
                ;;
            --server)
                do_server=true
                shift
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 如果指定了--all，执行所有步骤
    if $do_all; then
        do_venv=true
        do_install=true
        do_db=true
        do_test=true
    fi
    
    # 显示欢迎信息
    log_info "CoachAI环境设置脚本"
    log_info "环境类型: $env_type"
    echo ""
    
    # 执行各步骤
    if $do_venv; then
        create_virtualenv
        echo ""
    fi
    
    if $do_install; then
        install_dependencies
        echo ""
    fi
    
    if $do_db; then
        init_database
        echo ""
    fi
    
    if $do_test; then
        run_tests
        echo ""
    fi
    
    if $do_clean; then
        cleanup
        echo ""
    fi
    
    if $do_server; then
        start_dev_server
        exit 0
    fi
    
    # 显示环境信息
    show_environment
    
    echo ""
    log_success "环境设置完成!"
    echo ""
    echo "下一步:"
    echo "  1. 激活虚拟环境: source venv/bin/activate"
    echo "  2. 启动开发服务器: $0 --server"
    echo "  3. 运行测试: $0 --test"
    echo ""
    echo "常用命令:"
    echo "  $0 --all            # 完整设置环境"
    echo "  $0 --server         # 启动开发服务器"
    echo "  $0 --test           # 运行测试"
    echo "  $0 --clean          # 清理临时文件"
}

# 执行主函数
main "$@"
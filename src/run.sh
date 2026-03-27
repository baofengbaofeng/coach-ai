#!/bin/bash
# CoachAI 项目启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$PROJECT_ROOT/src"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}      CoachAI 项目启动脚本${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查Python环境
check_python() {
    echo -e "${YELLOW}[1/5] 检查Python环境...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误: 未找到python3命令${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo -e "${GREEN}✓ Python版本: $PYTHON_VERSION${NC}"
}

# 检查虚拟环境
check_venv() {
    echo -e "${YELLOW}[2/5] 检查虚拟环境...${NC}"
    
    if [ -d "$PROJECT_ROOT/venv" ]; then
        echo -e "${GREEN}✓ 虚拟环境已存在${NC}"
        source "$PROJECT_ROOT/venv/bin/activate"
    else
        echo -e "${YELLOW}⚠ 虚拟环境不存在，正在创建...${NC}"
        python3 -m venv "$PROJECT_ROOT/venv"
        source "$PROJECT_ROOT/venv/bin/activate"
        echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
    fi
}

# 安装依赖
install_deps() {
    echo -e "${YELLOW}[3/5] 安装依赖包...${NC}"
    
    if [ -f "$SRC_DIR/requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r "$SRC_DIR/requirements.txt"
        echo -e "${GREEN}✓ 依赖安装完成${NC}"
    else
        echo -e "${RED}错误: 未找到requirements.txt${NC}"
        exit 1
    fi
}

# 设置环境变量
setup_env() {
    echo -e "${YELLOW}[4/5] 设置环境变量...${NC}"
    
    # 添加src目录到Python路径
    export PYTHONPATH="$SRC_DIR:$PYTHONPATH"
    echo -e "${GREEN}✓ 已添加 $SRC_DIR 到 PYTHONPATH${NC}"
    
    # 设置默认环境变量
    export APP_ENV=${APP_ENV:-"development"}
    export APP_DEBUG=${APP_DEBUG:-"true"}
    export APP_PORT=${APP_PORT:-"8888"}
    
    echo -e "${GREEN}✓ 环境变量设置完成:${NC}"
    echo -e "  APP_ENV: $APP_ENV"
    echo -e "  APP_DEBUG: $APP_DEBUG"
    echo -e "  APP_PORT: $APP_PORT"
}

# 启动应用
start_app() {
    echo -e "${YELLOW}[5/5] 启动应用...${NC}"
    
    # 检查主入口文件
    if [ ! -f "$SRC_DIR/main.py" ]; then
        echo -e "${RED}错误: 未找到主入口文件 $SRC_DIR/main.py${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ 正在启动CoachAI服务器...${NC}"
    echo -e "${BLUE}----------------------------------------${NC}"
    echo -e "${GREEN}访问地址: http://localhost:$APP_PORT${NC}"
    echo -e "${GREEN}健康检查: http://localhost:$APP_PORT/api/health${NC}"
    echo -e "${BLUE}----------------------------------------${NC}"
    
    # 启动服务器
    cd "$SRC_DIR"
    python -m main
}

# 显示帮助信息
show_help() {
    echo -e "${BLUE}使用说明:${NC}"
    echo -e "  $0 [选项]"
    echo -e ""
    echo -e "${BLUE}选项:${NC}"
    echo -e "  start     启动应用（默认）"
    echo -e "  install   仅安装依赖，不启动"
    echo -e "  test      运行测试"
    echo -e "  clean     清理虚拟环境和缓存"
    echo -e "  help      显示此帮助信息"
    echo -e ""
    echo -e "${BLUE}环境变量:${NC}"
    echo -e "  APP_ENV    应用环境 (development|production|testing)"
    echo -e "  APP_DEBUG  调试模式 (true|false)"
    echo -e "  APP_PORT   服务端口 (默认: 8888)"
}

# 清理命令
clean_up() {
    echo -e "${YELLOW}清理项目...${NC}"
    
    # 删除虚拟环境
    if [ -d "$PROJECT_ROOT/venv" ]; then
        rm -rf "$PROJECT_ROOT/venv"
        echo -e "${GREEN}✓ 虚拟环境已删除${NC}"
    fi
    
    # 删除缓存文件
    find "$PROJECT_ROOT" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$PROJECT_ROOT" -name "*.pyc" -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -name "*.pyo" -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    
    echo -e "${GREEN}✓ 清理完成${NC}"
}

# 运行测试
run_tests() {
    echo -e "${YELLOW}运行测试...${NC}"
    
    check_venv
    setup_env
    
    cd "$PROJECT_ROOT"
    
    # 运行单元测试
    echo -e "${BLUE}运行单元测试...${NC}"
    python -m pytest src/tests/unit/ -v
    
    # 运行集成测试
    echo -e "${BLUE}运行集成测试...${NC}"
    python -m pytest src/tests/integration/ -v
    
    # 运行系统测试
    echo -e "${BLUE}运行系统测试...${NC}"
    python -m pytest src/tests/system/ -v
    
    echo -e "${GREEN}✓ 测试完成${NC}"
}

# 主函数
main() {
    local command=${1:-"start"}
    
    case $command in
        "start")
            check_python
            check_venv
            install_deps
            setup_env
            start_app
            ;;
        "install")
            check_python
            check_venv
            install_deps
            echo -e "${GREEN}✓ 依赖安装完成${NC}"
            ;;
        "test")
            run_tests
            ;;
        "clean")
            clean_up
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo -e "${RED}错误: 未知命令 '$command'${NC}"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
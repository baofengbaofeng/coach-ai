#!/bin/bash

# CoachAI部署脚本
# 用于部署CoachAI应用到生产环境

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

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "命令 $1 未找到，请先安装"
        exit 1
    fi
}

# 显示帮助信息
show_help() {
    echo "CoachAI部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示此帮助信息"
    echo "  -e, --env ENV       部署环境 (development, staging, production)"
    echo "  -c, --config FILE   配置文件路径"
    echo "  --migrate           运行数据库迁移"
    echo "  --seed              运行数据库种子"
    echo "  --build             重新构建Docker镜像"
    echo "  --restart           重启服务"
    echo "  --stop              停止服务"
    echo "  --logs              查看日志"
    echo "  --status            查看服务状态"
    echo ""
    echo "示例:"
    echo "  $0 -e production --migrate --build"
    echo "  $0 --status"
}

# 解析命令行参数
parse_args() {
    ENV="production"
    CONFIG_FILE=""
    DO_MIGRATE=false
    DO_SEED=false
    DO_BUILD=false
    DO_RESTART=false
    DO_STOP=false
    DO_LOGS=false
    DO_STATUS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -e|--env)
                ENV="$2"
                shift 2
                ;;
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            --migrate)
                DO_MIGRATE=true
                shift
                ;;
            --seed)
                DO_SEED=true
                shift
                ;;
            --build)
                DO_BUILD=true
                shift
                ;;
            --restart)
                DO_RESTART=true
                shift
                ;;
            --stop)
                DO_STOP=true
                shift
                ;;
            --logs)
                DO_LOGS=true
                shift
                ;;
            --status)
                DO_STATUS=true
                shift
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 加载环境配置
load_config() {
    local env=$1
    local config_file=$2
    
    if [[ -n "$config_file" && -f "$config_file" ]]; then
        log_info "加载配置文件: $config_file"
        source "$config_file"
    elif [[ -f "deploy/config/$env.env" ]]; then
        log_info "加载环境配置文件: deploy/config/$env.env"
        source "deploy/config/$env.env"
    elif [[ -f ".env.$env" ]]; then
        log_info "加载环境配置文件: .env.$env"
        source ".env.$env"
    else
        log_warning "未找到配置文件，使用默认值"
    fi
    
    # 设置环境变量
    export APP_ENV=${APP_ENV:-$env}
}

# 检查部署环境
check_environment() {
    log_info "检查部署环境..."
    
    # 检查必要命令
    check_command docker
    check_command docker-compose
    
    # 检查Docker服务
    if ! docker info &> /dev/null; then
        log_error "Docker服务未运行"
        exit 1
    fi
    
    # 检查配置文件
    if [[ ! -f "docker-compose.yml" && ! -f "deploy/docker/docker-compose.yml" ]]; then
        log_error "未找到docker-compose.yml文件"
        exit 1
    fi
    
    log_success "环境检查通过"
}

# 构建Docker镜像
build_images() {
    log_info "构建Docker镜像..."
    
    local compose_file="deploy/docker/docker-compose.yml"
    if [[ -f "docker-compose.yml" ]]; then
        compose_file="docker-compose.yml"
    fi
    
    docker-compose -f "$compose_file" build --no-cache
    
    if [[ $? -eq 0 ]]; then
        log_success "Docker镜像构建完成"
    else
        log_error "Docker镜像构建失败"
        exit 1
    fi
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    local compose_file="deploy/docker/docker-compose.yml"
    if [[ -f "docker-compose.yml" ]]; then
        compose_file="docker-compose.yml"
    fi
    
    docker-compose -f "$compose_file" up -d
    
    if [[ $? -eq 0 ]]; then
        log_success "服务启动完成"
    else
        log_error "服务启动失败"
        exit 1
    fi
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    local compose_file="deploy/docker/docker-compose.yml"
    if [[ -f "docker-compose.yml" ]]; then
        compose_file="docker-compose.yml"
    fi
    
    docker-compose -f "$compose_file" down
    
    log_success "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    
    local compose_file="deploy/docker/docker-compose.yml"
    if [[ -f "docker-compose.yml" ]]; then
        compose_file="docker-compose.yml"
    fi
    
    docker-compose -f "$compose_file" restart
    
    log_success "服务重启完成"
}

# 查看服务状态
show_status() {
    log_info "服务状态:"
    
    local compose_file="deploy/docker/docker-compose.yml"
    if [[ -f "docker-compose.yml" ]]; then
        compose_file="docker-compose.yml"
    fi
    
    docker-compose -f "$compose_file" ps
    
    echo ""
    log_info "容器资源使用情况:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" | head -6
}

# 查看日志
show_logs() {
    log_info "查看日志..."
    
    local compose_file="deploy/docker/docker-compose.yml"
    if [[ -f "docker-compose.yml" ]]; then
        compose_file="docker-compose.yml"
    fi
    
    docker-compose -f "$compose_file" logs -f --tail=100
}

# 运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    local compose_file="deploy/docker/docker-compose.yml"
    if [[ -f "docker-compose.yml" ]]; then
        compose_file="docker-compose.yml"
    fi
    
    # 等待数据库就绪
    log_info "等待数据库就绪..."
    sleep 10
    
    # 运行迁移
    docker-compose -f "$compose_file" exec -T app python -m database.migration_manager upgrade
    
    if [[ $? -eq 0 ]]; then
        log_success "数据库迁移完成"
    else
        log_error "数据库迁移失败"
        exit 1
    fi
}

# 运行数据库种子
run_seeds() {
    log_info "运行数据库种子..."
    
    local compose_file="deploy/docker/docker-compose.yml"
    if [[ -f "docker-compose.yml" ]]; then
        compose_file="docker-compose.yml"
    fi
    
    # 运行种子
    docker-compose -f "$compose_file" exec -T app python -m database.seeds.initial_data
    
    if [[ $? -eq 0 ]]; then
        log_success "数据库种子完成"
    else
        log_error "数据库种子失败"
        exit 1
    fi
}

# 备份数据库
backup_database() {
    log_info "备份数据库..."
    
    local backup_dir="backups"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$backup_dir/backup_$timestamp.sql"
    
    mkdir -p "$backup_dir"
    
    local compose_file="deploy/docker/docker-compose.yml"
    if [[ -f "docker-compose.yml" ]]; then
        compose_file="docker-compose.yml"
    fi
    
    docker-compose -f "$compose_file" exec -T db mysqldump \
        -u ${DB_USER:-coach_ai_user} \
        -p${DB_PASSWORD:-coach_ai_password} \
        ${DB_NAME:-coach_ai} > "$backup_file"
    
    if [[ $? -eq 0 ]]; then
        log_success "数据库备份完成: $backup_file"
        
        # 压缩备份文件
        gzip "$backup_file"
        log_info "备份文件已压缩: ${backup_file}.gz"
        
        # 清理旧备份（保留最近7天）
        find "$backup_dir" -name "*.gz" -mtime +7 -delete
    else
        log_error "数据库备份失败"
        exit 1
    fi
}

# 主函数
main() {
    parse_args "$@"
    
    log_info "开始部署CoachAI (环境: $ENV)"
    
    # 加载配置
    load_config "$ENV" "$CONFIG_FILE"
    
    # 检查环境
    check_environment
    
    # 执行操作
    if $DO_STOP; then
        stop_services
        exit 0
    fi
    
    if $DO_STATUS; then
        show_status
        exit 0
    fi
    
    if $DO_LOGS; then
        show_logs
        exit 0
    fi
    
    # 备份数据库（生产环境）
    if [[ "$ENV" == "production" ]]; then
        backup_database
    fi
    
    # 构建镜像
    if $DO_BUILD; then
        build_images
    fi
    
    # 启动服务
    start_services
    
    # 运行迁移
    if $DO_MIGRATE; then
        run_migrations
    fi
    
    # 运行种子
    if $DO_SEED; then
        run_seeds
    fi
    
    # 重启服务
    if $DO_RESTART; then
        restart_services
    fi
    
    # 显示状态
    show_status
    
    log_success "部署完成!"
    log_info "应用地址: http://localhost:${APP_PORT:-8000}"
    log_info "健康检查: http://localhost:${APP_PORT:-8000}/api/health"
}

# 执行主函数
main "$@"
#!/bin/bash
# CoachAI部署脚本（DDD迁移版）
# 用于部署CoachAI应用到不同环境

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

# 获取项目根目录
get_project_root() {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
}

# 显示帮助信息
show_help() {
    echo "CoachAI部署脚本"
    echo ""
    echo "用法: $0 [选项] [环境]"
    echo ""
    echo "环境:"
    echo "  dev         开发环境"
    echo "  staging     预发布环境"
    echo "  production  生产环境"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示此帮助信息"
    echo "  -b, --build         构建Docker镜像"
    echo "  -u, --up            启动服务"
    echo "  -d, --down          停止服务"
    echo "  -r, --restart       重启服务"
    echo "  -l, --logs          查看日志"
    echo "  -s, --status        查看服务状态"
    echo "  -m, --migrate       运行数据库迁移"
    echo "  -t, --test          运行部署测试"
    echo "  -c, --clean         清理部署资源"
    echo "  --backup            备份数据库"
    echo "  --restore FILE      恢复数据库备份"
    echo "  --monitor           启动监控服务"
    echo ""
    echo "示例:"
    echo "  $0 dev -b -u        # 开发环境构建并启动"
    echo "  $0 production -u    # 生产环境启动"
    echo "  $0 -l               # 查看日志"
    echo "  $0 -s               # 查看状态"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "命令 $1 未找到，请先安装"
        exit 1
    fi
}

# 加载环境配置
load_environment() {
    local env=$1
    local project_root=$(get_project_root)
    
    log_info "加载 $env 环境配置"
    
    # 检查环境配置文件
    local env_file="$project_root/.env.$env"
    if [[ ! -f "$env_file" ]]; then
        log_warning "环境配置文件不存在: $env_file"
        log_info "创建示例配置文件..."
        cp "$project_root/.env.example" "$env_file"
        log_warning "请编辑 $env_file 文件配置环境变量"
    fi
    
    # 加载环境变量
    if [[ -f "$env_file" ]]; then
        export $(grep -v '^#' "$env_file" | xargs)
        log_info "环境变量已加载: $env_file"
    fi
    
    # 设置环境类型
    export APP_ENV=$env
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
    
    # 检查Docker Compose文件
    local project_root=$(get_project_root)
    if [[ ! -f "$project_root/docker-compose.yml" ]]; then
        log_error "docker-compose.yml文件不存在"
        exit 1
    fi
    
    log_success "环境检查通过"
}

# 构建Docker镜像
build_images() {
    log_info "构建Docker镜像..."
    
    local project_root=$(get_project_root)
    
    docker-compose -f "$project_root/docker-compose.yml" build --no-cache
    
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
    
    local project_root=$(get_project_root)
    
    docker-compose -f "$project_root/docker-compose.yml" up -d
    
    if [[ $? -eq 0 ]]; then
        log_success "服务启动完成"
        
        # 显示服务信息
        sleep 2
        show_status
    else
        log_error "服务启动失败"
        exit 1
    fi
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    local project_root=$(get_project_root)
    
    docker-compose -f "$project_root/docker-compose.yml" down
    
    log_success "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    
    local project_root=$(get_project_root)
    
    docker-compose -f "$project_root/docker-compose.yml" restart
    
    log_success "服务重启完成"
}

# 查看服务状态
show_status() {
    log_info "服务状态:"
    
    local project_root=$(get_project_root)
    
    docker-compose -f "$project_root/docker-compose.yml" ps
    
    echo ""
    log_info "容器资源使用情况:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" | head -6
    
    echo ""
    log_info "应用信息:"
    echo "  应用地址: http://localhost:${APP_PORT:-8888}"
    echo "  健康检查: http://localhost:${APP_PORT:-8888}/api/health"
    echo "  API文档: http://localhost:${APP_PORT:-8888}/api/docs"
    
    if [[ "$APP_ENV" == "production" ]]; then
        echo ""
        log_info "生产环境注意事项:"
        echo "  - 确保所有密码已更改"
        echo "  - 启用HTTPS"
        echo "  - 配置防火墙规则"
        echo "  - 设置监控和告警"
    fi
}

# 查看日志
show_logs() {
    log_info "查看日志..."
    
    local project_root=$(get_project_root)
    
    docker-compose -f "$project_root/docker-compose.yml" logs -f --tail=100
}

# 运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    local project_root=$(get_project_root)
    
    # 等待数据库就绪
    log_info "等待数据库就绪..."
    sleep 10
    
    # 运行迁移
    docker-compose -f "$project_root/docker-compose.yml" exec -T app python -c "
from src.infrastructure.db.connection import init_database
from src.infrastructure.db.migrations import run_migrations

try:
    db_manager = init_database()
    run_migrations(db_manager)
    print('数据库迁移完成')
except Exception as e:
    print(f'数据库迁移失败: {e}')
    exit(1)
    "
    
    if [[ $? -eq 0 ]]; then
        log_success "数据库迁移完成"
    else
        log_error "数据库迁移失败"
        exit 1
    fi
}

# 运行部署测试
run_tests() {
    log_info "运行部署测试..."
    
    local project_root=$(get_project_root)
    
    # 测试数据库连接
    log_info "测试数据库连接..."
    docker-compose -f "$project_root/docker-compose.yml" exec -T db mysql \
        -u "${DB_USER:-coach_ai_user}" \
        -p"${DB_PASSWORD:-coach_ai_password}" \
        -e "SELECT 1" > /dev/null 2>&1
    
    if [[ $? -eq 0 ]]; then
        log_success "数据库连接正常"
    else
        log_error "数据库连接失败"
        exit 1
    fi
    
    # 测试Redis连接
    log_info "测试Redis连接..."
    docker-compose -f "$project_root/docker-compose.yml" exec -T redis \
        redis-cli -a "${REDIS_PASSWORD:-redispassword}" ping > /dev/null 2>&1
    
    if [[ $? -eq 0 ]]; then
        log_success "Redis连接正常"
    else
        log_error "Redis连接失败"
        exit 1
    fi
    
    # 测试应用健康检查
    log_info "测试应用健康检查..."
    sleep 5
    curl -f "http://localhost:${APP_PORT:-8888}/api/health" > /dev/null 2>&1
    
    if [[ $? -eq 0 ]]; then
        log_success "应用健康检查正常"
    else
        log_error "应用健康检查失败"
        exit 1
    fi
    
    log_success "所有部署测试通过"
}

# 备份数据库
backup_database() {
    log_info "备份数据库..."
    
    local project_root=$(get_project_root)
    local backup_dir="$project_root/backups"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$backup_dir/backup_$timestamp.sql"
    
    mkdir -p "$backup_dir"
    
    docker-compose -f "$project_root/docker-compose.yml" exec -T db mysqldump \
        -u "${DB_USER:-coach_ai_user}" \
        -p"${DB_PASSWORD:-coach_ai_password}" \
        "${DB_NAME:-coach_ai}" > "$backup_file"
    
    if [[ $? -eq 0 ]]; then
        log_success "数据库备份完成: $backup_file"
        
        # 压缩备份文件
        gzip "$backup_file"
        log_info "备份文件已压缩: ${backup_file}.gz"
        
        # 清理旧备份（保留最近7天）
        find "$backup_dir" -name "*.gz" -mtime +7 -delete
        log_info "已清理7天前的旧备份"
    else
        log_error "数据库备份失败"
        exit 1
    fi
}

# 恢复数据库备份
restore_database() {
    local backup_file=$1
    
    if [[ ! -f "$backup_file" ]]; then
        log_error "备份文件不存在: $backup_file"
        exit 1
    fi
    
    log_info "恢复数据库备份: $backup_file"
    
    local project_root=$(get_project_root)
    
    # 解压备份文件（如果是.gz格式）
    local restore_file="$backup_file"
    if [[ "$backup_file" == *.gz ]]; then
        restore_file="${backup_file%.gz}"
        gunzip -c "$backup_file" > "$restore_file"
    fi
    
    # 恢复数据库
    docker-compose -f "$project_root/docker-compose.yml" exec -T db mysql \
        -u "${DB_USER:-coach_ai_user}" \
        -p"${DB_PASSWORD:-coach_ai_password}" \
        "${DB_NAME:-coach_ai}" < "$restore_file"
    
    if [[ $? -eq 0 ]]; then
        log_success "数据库恢复完成"
        
        # 清理临时文件
        if [[ "$backup_file" == *.gz ]]; then
            rm -f "$restore_file"
        fi
    else
        log_error "数据库恢复失败"
        exit 1
    fi
}

# 清理部署资源
cleanup_resources() {
    log_info "清理部署资源..."
    
    local project_root=$(get_project_root)
    
    # 停止并删除容器
    docker-compose -f "$project_root/docker-compose.yml" down -v
    
    # 删除未使用的镜像
    docker image prune -f
    
    # 删除未使用的卷
    docker volume prune -f
    
    log_success "部署资源清理完成"
}

# 启动监控服务
start_monitor() {
    log_info "启动监控服务..."
    
    local project_root=$(get_project_root)
    
    # 检查监控配置
    if [[ ! -d "$project_root/deploy/grafana" ]]; then
        log_warning "监控配置目录不存在，跳过监控服务"
        return 0
    fi
    
    # 启动监控服务
    docker-compose -f "$project_root/docker-compose.yml" up -d monitor
    
    log_success "监控服务已启动"
    echo "  Grafana地址: http://localhost:3000"
    echo "  用户名: admin"
    echo "  密码: ${GRAFANA_PASSWORD:-admin}"
}

# 主函数
main() {
    local env="dev"
    local do_build=false
    local do_up=false
    local do_down=false
    local do_restart=false
    local do_logs=false
    local do_status=false
    local do_migrate=false
    local do_test=false
    local do_clean=false
    local do_backup=false
    local do_monitor=false
    local restore_file=""
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -b|--build)
                do_build=true
                shift
                ;;
            -u|--up)
                do_up=true
                shift
                ;;
            -d|--down)
                do_down=true
                shift
                ;;
            -r|--restart)
                do_restart=true
                shift
                ;;
            -l|--logs)
                do_logs=true
                shift
                ;;
            -s|--status)
                do_status=true
                shift
                ;;
            -m|--migrate)
                do_migrate=true
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
            --backup)
                do_backup=true
                shift
                ;;
            --restore)
                restore_file="$2"
                shift 2
                ;;
            --monitor)
                do_monitor=true
                shift
                ;;
            dev|staging|production)
                env="$1"
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 如果没有指定操作，显示帮助
    if [[ $do_build == false && $do_up == false && $do_down == false && \
          $do_restart == false && $do_logs == false && $do_status == false && \
          $do_migrate == false && $do_test == false && $do_clean == false && \
          $do_backup == false && -z "$restore_file" && $do_monitor == false ]]; then
        show_help
        exit 0
    fi
    
    # 显示部署信息
    log_info "CoachAI部署脚本"
    log_info "环境: $env"
    echo ""
    
    # 加载环境配置
    load_environment "$env"
    
    # 检查环境
    check_environment
    
    # 执行操作
    if $do_clean; then
        cleanup_resources
        exit 0
    fi
    
    if $do_down; then
        stop_services
        exit 0
    fi
    
    if $do_status; then
        show_status
        exit 0
    fi
    
    if $do_logs; then
        show_logs
        exit 0
    fi
    
    if [[ -n "$restore_file" ]]; then
        restore_database "$restore_file"
        exit 0
    fi
    
    if $do_backup; then
        backup_database
        exit 0
    fi
    
    if $do_build; then
        build_images
    fi
    
    if $do_up; then
        start_services
    fi
    
    if $do_migrate; then
        run_migrations
    fi
    
    if $do_test; then
        run_tests
    fi
    
    if $do_restart; then
        restart_services
    fi
    
    if $do_monitor; then
        start_monitor
    fi
    
    log_success "部署操作完成!"
}

# 执行主函数
main "$@"
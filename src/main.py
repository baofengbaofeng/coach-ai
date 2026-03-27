"""
CoachAI应用主入口（DDD迁移版）
应用启动和初始化
"""

import sys
import os
from loguru import logger

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 配置日志
logger.remove()  # 移除默认处理器
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# 添加文件日志（如果配置了日志文件）
from src.settings import settings
if settings.LOG_FILE:
    logger.add(
        settings.LOG_FILE,
        rotation="500 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL
    )


def init_application():
    """初始化应用"""
    logger.info("=" * 60)
    logger.info("CoachAI Application Initialization")
    logger.info("=" * 60)
    
    try:
        # 初始化数据库
        logger.info("Initializing database...")
        from src.infrastructure.db.connection import init_database
        db_manager = init_database()
        
        # 数据库健康检查
        db_health = db_manager.health_check()
        logger.info(f"Database health: {db_health['status']}")
        
        # 初始化Redis
        logger.info("Initializing Redis...")
        from src.infrastructure.cache.redis_client import init_redis
        redis_manager = init_redis()
        
        # Redis健康检查
        redis_health = redis_manager.health_check()
        logger.info(f"Redis health: {redis_health['status']}")
        
        # 初始化事件总线
        logger.info("Initializing event bus...")
        from src.application.events.bus import init_event_bus
        event_bus = init_event_bus()
        logger.info(f"Event bus initialized: {settings.EVENT_BUS_TYPE}")
        
        # 显示配置信息
        logger.info("Configuration:")
        logger.info(f"  Environment: {settings.APP_ENV}")
        logger.info(f"  Debug mode: {settings.APP_DEBUG}")
        logger.info(f"  Host: {settings.APP_HOST}")
        logger.info(f"  Port: {settings.APP_PORT}")
        logger.info(f"  Database: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
        logger.info(f"  Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}")
        
        logger.info("Application initialization completed successfully")
        logger.info("=" * 60)
        
        return {
            'db_manager': db_manager,
            'redis_manager': redis_manager,
            'event_bus': event_bus
        }
        
    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        logger.error("Shutting down...")
        raise


def cleanup_application():
    """清理应用资源"""
    logger.info("Cleaning up application resources...")
    
    try:
        # 关闭Redis连接
        from src.infrastructure.cache.redis_client import close_redis
        close_redis()
        logger.info("Redis connections closed")
        
        # 关闭数据库连接
        from src.infrastructure.db.connection import close_database
        close_database()
        logger.info("Database connections closed")
        
        # 关闭事件总线
        from src.application.events.bus import close_event_bus
        close_event_bus()
        logger.info("Event bus closed")
        
        logger.info("Application cleanup completed")
        
    except Exception as e:
        logger.error(f"Application cleanup failed: {e}")


def start_server():
    """启动服务器"""
    try:
        # 初始化应用
        init_result = init_application()
        
        # 创建Tornado应用
        logger.info("Creating Tornado application...")
        from src.interfaces.web.application import create_application, start_server as tornado_start_server
        
        app = create_application()
        
        # 显示路由信息
        logger.info(f"Application created with {len(app.handlers)} handlers")
        
        # 启动服务器
        logger.info("Starting Tornado server...")
        tornado_start_server()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise
    finally:
        # 清理资源
        cleanup_application()


if __name__ == "__main__":
    start_server()
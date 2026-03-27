"""
CoachAI应用入口文件
启动Tornado Web服务器
"""

import asyncio
import signal
import sys
from loguru import logger
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application

from config import init_config, get_config
from webapp.core.application import create_application


def setup_logging():
    """配置日志系统"""
    logger.remove()  # 移除默认处理器
    
    # 初始化配置
    config = init_config()
    
    # 添加控制台输出（英文日志）
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if config.APP_DEBUG else "INFO",
        colorize=True
    )
    
    # 添加文件输出
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # 每天轮转
        retention="30 days",  # 保留30天
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO"
    )
    
    logger.info("Logging system initialized")


def setup_signal_handlers(server: HTTPServer):
    """设置信号处理器"""
    
    def shutdown_handler(signum, frame):
        """优雅关闭服务器"""
        logger.info(f"Received signal {signum}, shutting down...")
        
        # 停止接受新连接
        server.stop()
        
        def stop_loop():
            """停止IOLoop"""
            IOLoop.current().stop()
            logger.info("Server stopped gracefully")
        
        # 给现有连接2秒时间完成
        IOLoop.current().add_timeout(IOLoop.current().time() + 2, stop_loop)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)


async def main():
    """主函数"""
    # 配置日志
    setup_logging()
    
    config = get_config()
    logger.info(f"Starting CoachAI server in {config.APP_ENV} mode")
    logger.info(f"Database URL: {config.DATABASE_URL}")
    logger.info(f"Redis URL: {config.REDIS_URL}")
    logger.info(f"RabbitMQ URL: {config.RABBITMQ_URL}")
    
    try:
        # 创建Tornado应用
        app: Application = create_application()
        
        # 创建HTTP服务器
        server = HTTPServer(app)
        
        # 设置信号处理器
        setup_signal_handlers(server)
        
        # 启动服务器
        server.listen(config.APP_PORT)
        logger.info(f"Server started on port {config.APP_PORT}")
        
        # 保持运行
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 启动应用
    asyncio.run(main())
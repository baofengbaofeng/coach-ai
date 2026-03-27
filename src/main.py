"""
CoachAI 主入口文件
DDD架构 + EDA事件驱动架构
"""

import asyncio
import signal
import sys
from typing import Optional
from loguru import logger

"""
CoachAI 主入口文件 - 简化版
"""

import sys
import os

# 确保可以导入同级模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 直接导入模块
import settings

# 配置
config = settings.config
init_config = settings.init_config

# 由于导入问题，我们暂时简化
# 在实际使用时会动态导入


class Application:
    """应用主类"""
    
    def __init__(self):
        self._is_running = False
        self._shutdown_event = asyncio.Event()
    
    async def setup(self) -> None:
        """应用初始化"""
        logger.info("=" * 50)
        logger.info("CoachAI 应用初始化")
        logger.info("=" * 50)
        
        # 1. 初始化配置
        logger.info("[1/5] 初始化配置...")
        cfg = init_config()
        logger.info(f"环境: {cfg.APP_ENV}, 调试: {cfg.APP_DEBUG}, 端口: {cfg.APP_PORT}")
        
        # 2. 初始化数据库
        logger.info("[2/5] 初始化数据库...")
        init_database()
        if db_manager.health_check():
            logger.info("✅ 数据库连接正常")
        else:
            logger.error("❌ 数据库连接失败")
            raise RuntimeError("数据库连接失败")
        
        # 3. 初始化Redis
        logger.info("[3/5] 初始化Redis...")
        init_redis()
        if redis_client.health_check():
            logger.info("✅ Redis连接正常")
        else:
            logger.warning("⚠️ Redis连接失败，缓存功能将不可用")
        
        # 4. 初始化事件总线
        logger.info("[4/5] 初始化事件总线...")
        await EventBusFactory.start_event_bus()
        logger.info(f"✅ 事件总线已启动 ({config.EVENT_BUS_TYPE})")
        
        # 5. 注册信号处理器
        logger.info("[5/5] 注册信号处理器...")
        self._setup_signal_handlers()
        
        logger.info("✅ 应用初始化完成")
    
    def _setup_signal_handlers(self) -> None:
        """设置信号处理器"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame) -> None:
        """信号处理函数"""
        logger.info(f"收到信号 {signum}，开始优雅关闭...")
        self._shutdown_event.set()
    
    async def run(self) -> None:
        """运行应用主循环"""
        self._is_running = True
        
        try:
            logger.info("=" * 50)
            logger.info("CoachAI 应用启动")
            logger.info("=" * 50)
            
            # 这里可以启动Web服务器、定时任务等
            # 暂时使用简单的事件循环
            
            logger.info(f"应用运行在: http://{config.APP_HOST}:{config.APP_PORT}")
            logger.info(f"健康检查: http://{config.APP_HOST}:{config.APP_PORT}/api/health")
            
            # 等待关闭信号
            await self._shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"应用运行异常: {e}")
            raise
        
        finally:
            await self.shutdown()
    
    async def shutdown(self) -> None:
        """应用关闭"""
        if not self._is_running:
            return
        
        self._is_running = False
        
        logger.info("=" * 50)
        logger.info("CoachAI 应用关闭")
        logger.info("=" * 50)
        
        try:
            # 1. 停止事件总线
            logger.info("[1/4] 停止事件总线...")
            await EventBusFactory.stop_event_bus()
            logger.info("✅ 事件总线已停止")
            
            # 2. 关闭Redis连接
            logger.info("[2/4] 关闭Redis连接...")
            redis_client.close()
            logger.info("✅ Redis连接已关闭")
            
            # 3. 关闭数据库连接
            logger.info("[3/4] 关闭数据库连接...")
            db_manager.close_all_sessions()
            logger.info("✅ 数据库连接已关闭")
            
            # 4. 清理资源
            logger.info("[4/4] 清理资源...")
            # 这里可以添加其他资源清理逻辑
            
            logger.info("✅ 应用关闭完成")
            
        except Exception as e:
            logger.error(f"应用关闭异常: {e}")
        
        finally:
            logger.info("=" * 50)
            logger.info("CoachAI 应用已停止")
            logger.info("=" * 50)
    
    def run_sync(self) -> None:
        """同步运行应用"""
        try:
            # 创建事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 运行应用
            loop.run_until_complete(self._run_async())
            
        except KeyboardInterrupt:
            logger.info("收到键盘中断，正在关闭...")
        
        except Exception as e:
            logger.error(f"应用运行失败: {e}")
            sys.exit(1)
    
    async def _run_async(self) -> None:
        """异步运行应用"""
        try:
            await self.setup()
            await self.run()
        
        except Exception as e:
            logger.error(f"应用运行失败: {e}")
            await self.shutdown()
            raise


async def main_async() -> None:
    """异步主函数"""
    app = Application()
    await app.setup()
    await app.run()


def main() -> None:
    """同步主函数"""
    app = Application()
    app.run_sync()


if __name__ == "__main__":
    # 设置日志
    logger.remove()  # 移除默认处理器
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if config.APP_DEBUG else "INFO",
        colorize=True
    )
    
    # 运行应用
    main()
"""
全局配置模块
整合所有环境配置和设置
"""

import os
import sys
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """全局配置类"""
    
    # ====================== 应用基础配置 ======================
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_DEBUG: bool = os.getenv("APP_DEBUG", "True").lower() == "true"
    APP_PORT: int = int(os.getenv("APP_PORT", "8888"))
    APP_SECRET_KEY: str = os.getenv("APP_SECRET_KEY", "dev-secret-key-change-in-production")
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    
    # ====================== 数据库配置 ======================
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_NAME: str = os.getenv("DB_NAME", "coach_ai")
    DB_USER: str = os.getenv("DB_USER", "coach_ai_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_CHARSET: str = os.getenv("DB_CHARSET", "utf8mb4")
    
    # SQLAlchemy配置
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    DB_POOL_PRE_PING: bool = os.getenv("DB_POOL_PRE_PING", "True").lower() == "true"
    
    # 数据库URL（自动生成）
    @property
    def DATABASE_URL(self) -> str:
        """生成数据库连接URL"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset={self.DB_CHARSET}"
    
    # ====================== Redis配置 ======================
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_MAX_CONNECTIONS: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "20"))
    
    @property
    def REDIS_URL(self) -> str:
        """生成Redis连接URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # ====================== JWT配置 ======================
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # ====================== 租户配置 ======================
    TENANT_ID_HEADER: str = os.getenv("TENANT_ID_HEADER", "X-Tenant-ID")
    DEFAULT_TENANT_ID: str = os.getenv("DEFAULT_TENANT_ID", "default")
    
    # ====================== 文件上传配置 ======================
    UPLOAD_MAX_SIZE: int = int(os.getenv("UPLOAD_MAX_SIZE", "10485760"))  # 10MB
    UPLOAD_ALLOWED_EXTENSIONS: list = os.getenv("UPLOAD_ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif,pdf,doc,docx").split(",")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    
    # ====================== 日志配置 ======================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # ====================== 缓存配置 ======================
    CACHE_DEFAULT_TIMEOUT: int = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))
    CACHE_KEY_PREFIX: str = os.getenv("CACHE_KEY_PREFIX", "coach_ai")
    
    # ====================== 安全配置 ======================
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_DEFAULT: str = os.getenv("RATE_LIMIT_DEFAULT", "100/hour")
    
    # ====================== 事件总线配置 ======================
    EVENT_BUS_TYPE: str = os.getenv("EVENT_BUS_TYPE", "memory")  # memory, redis, rabbitmq
    EVENT_RETRY_ATTEMPTS: int = int(os.getenv("EVENT_RETRY_ATTEMPTS", "3"))
    EVENT_RETRY_DELAY: int = int(os.getenv("EVENT_RETRY_DELAY", "1"))
    
    # ====================== 业务配置 ======================
    # 成就系统
    ACHIEVEMENT_UNLOCK_NOTIFICATION: bool = os.getenv("ACHIEVEMENT_UNLOCK_NOTIFICATION", "True").lower() == "true"
    
    # 任务系统
    TASK_AUTO_ASSIGN: bool = os.getenv("TASK_AUTO_ASSIGN", "True").lower() == "true"
    TASK_DEFAULT_PRIORITY: str = os.getenv("TASK_DEFAULT_PRIORITY", "medium")
    
    # 运动系统
    EXERCISE_SESSION_TIMEOUT: int = int(os.getenv("EXERCISE_SESSION_TIMEOUT", "3600"))  # 1小时
    
    # ====================== 开发配置 ======================
    @property
    def is_development(self) -> bool:
        """是否开发环境"""
        return self.APP_ENV == "development"
    
    @property
    def is_production(self) -> bool:
        """是否生产环境"""
        return self.APP_ENV == "production"
    
    @property
    def is_testing(self) -> bool:
        """是否测试环境"""
        return self.APP_ENV == "testing"
    
    def __str__(self) -> str:
        """配置信息字符串表示"""
        return f"Config(env={self.APP_ENV}, debug={self.APP_DEBUG}, port={self.APP_PORT})"


# 全局配置实例
config = Config()


def init_config() -> Config:
    """
    初始化配置
    
    Returns:
        配置实例
    """
    # 这里可以添加配置验证逻辑
    return config


def get_config() -> Config:
    """
    获取配置实例
    
    Returns:
        配置实例
    """
    return config


# 导出
__all__ = ['config', 'Config', 'init_config', 'get_config']


if __name__ == "__main__":
    # 测试配置
    cfg = get_config()
    print(f"环境: {cfg.APP_ENV}")
    print(f"调试模式: {cfg.APP_DEBUG}")
    print(f"端口: {cfg.APP_PORT}")
    print(f"数据库URL: {cfg.DATABASE_URL}")
    print(f"Redis URL: {cfg.REDIS_URL}")
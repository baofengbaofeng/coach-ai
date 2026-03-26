"""
基础配置类和多环境配置
"""

import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class BaseConfig:
    """基础配置类"""
    
    # 应用配置
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_PORT: int = 8888
    APP_SECRET_KEY: str = "dev-secret-key-change-in-production"
    
    # 服务器配置
    APP_HOST: str = "0.0.0.0"
    APP_WORKERS: int = 1
    APP_MAX_BUFFER_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "coach_ai"
    DB_USER: str = "coach_ai_user"
    DB_PASSWORD: str = ""
    DB_CHARSET: str = "utf8mb4"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_MAX_CONNECTIONS: int = 20
    
    # RabbitMQ配置
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"
    
    # JWT配置
    JWT_SECRET_KEY: str = "jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_TOKEN_ISSUER: str = "coach-ai"
    
    # 多租户配置
    TENANT_ID_HEADER: str = "X-Tenant-ID"
    DEFAULT_TENANT_ID: str = "default"
    
    # 安全配置
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    SECURITY_HEADERS: dict = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    }
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    LOG_ROTATION: str = "00:00"
    LOG_RETENTION: str = "30 days"
    LOG_COMPRESSION: str = "zip"
    
    # 文件上传配置
    UPLOAD_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_ALLOWED_EXTENSIONS: list = [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx"]
    UPLOAD_DIR: str = "uploads"
    
    # 速率限制配置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/hour"
    RATE_LIMIT_AUTHENTICATED: str = "1000/hour"
    
    # 数据库连接URL
    @property
    def DATABASE_URL(self) -> str:
        """获取数据库连接URL"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset={self.DB_CHARSET}"
    
    @property
    def REDIS_URL(self) -> str:
        """获取Redis连接URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def RABBITMQ_URL(self) -> str:
        """获取RabbitMQ连接URL"""
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}{self.RABBITMQ_VHOST}"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """SQLAlchemy数据库URI（兼容性）"""
        return self.DATABASE_URL


class DevelopmentConfig(BaseConfig):
    """开发环境配置"""
    
    def __init__(self):
        super().__init__()
        self.APP_ENV = "development"
        self.APP_DEBUG = True
        self.APP_PORT = int(os.getenv("APP_PORT", "8888"))
        self.LOG_LEVEL = "DEBUG"
        
        # 开发环境特定配置
        self.DB_HOST = os.getenv("DB_HOST", "localhost")
        self.DB_NAME = os.getenv("DB_NAME", "coach_ai_dev")
        
        # 允许更详细的日志
        self.SQLALCHEMY_ECHO = True
        
        # 宽松的安全设置
        self.CORS_ORIGINS = ["*"]


class TestingConfig(BaseConfig):
    """测试环境配置"""
    
    def __init__(self):
        super().__init__()
        self.APP_ENV = "testing"
        self.APP_DEBUG = True
        self.APP_PORT = int(os.getenv("APP_PORT", "8889"))
        
        # 测试数据库
        self.DB_NAME = os.getenv("DB_NAME", "coach_ai_test")
        
        # 测试环境特定配置
        self.JWT_SECRET_KEY = "test-jwt-secret-key-for-testing-only"
        
        # 禁用速率限制以便测试
        self.RATE_LIMIT_ENABLED = False
        
        # 使用内存数据库或测试数据库
        test_db_url = os.getenv("TEST_DATABASE_URL")
        if test_db_url:
            # 覆盖DATABASE_URL属性
            self._test_db_url = test_db_url
    
    @property
    def DATABASE_URL(self) -> str:
        """测试环境数据库URL"""
        if hasattr(self, "_test_db_url"):
            return self._test_db_url
        return super().DATABASE_URL


class ProductionConfig(BaseConfig):
    """生产环境配置"""
    
    def __init__(self):
        super().__init__()
        self.APP_ENV = "production"
        self.APP_DEBUG = False
        self.APP_PORT = int(os.getenv("APP_PORT", "8000"))
        self.APP_WORKERS = int(os.getenv("APP_WORKERS", "4"))
        
        # 生产环境必需配置
        self.APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        
        # 生产数据库
        self.DB_HOST = os.getenv("DB_HOST", "db")
        self.DB_NAME = os.getenv("DB_NAME", "coach_ai_prod")
        self.DB_USER = os.getenv("DB_USER", "coach_ai_prod_user")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "")
        
        # Redis生产配置
        self.REDIS_HOST = os.getenv("REDIS_HOST", "redis")
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
        
        # RabbitMQ生产配置
        self.RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
        self.RABBITMQ_USER = os.getenv("RABBITMQ_USER", "coach_ai")
        self.RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "")
        
        # 生产环境安全配置
        self.CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",") or ["https://yourdomain.com"]
        self.SECURITY_HEADERS["Content-Security-Policy"] = "default-src 'self'"
        
        # 生产日志配置
        self.LOG_LEVEL = "INFO"
        self.LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
        
        # 生产环境优化
        self.DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
        self.DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "40"))
        self.REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
        
        # 文件上传限制
        self.UPLOAD_MAX_SIZE = int(os.getenv("UPLOAD_MAX_SIZE", "50")) * 1024 * 1024  # 50MB


# 配置类映射
Config = BaseConfig  # 默认配置类


# 环境特定的配置实例
def get_config_for_env(env: str = None) -> BaseConfig:
    """
    根据环境获取配置实例
    
    Args:
        env: 环境名称
        
    Returns:
        BaseConfig: 配置实例
    """
    if env is None:
        env = os.getenv("APP_ENV", "development")
    
    env = env.lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()
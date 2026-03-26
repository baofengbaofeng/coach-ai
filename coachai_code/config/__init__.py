"""
配置管理模块
支持多环境配置和配置验证
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger

from .config import Config, DevelopmentConfig, TestingConfig, ProductionConfig


class ConfigManager:
    """配置管理器"""
    
    _instance = None
    _config: Optional[Config] = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化配置管理器"""
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._config_map = {
                "development": DevelopmentConfig,
                "testing": TestingConfig,
                "production": ProductionConfig
            }
    
    def load_config(self, env: Optional[str] = None) -> Config:
        """
        加载配置
        
        Args:
            env: 环境名称，如果为None则从环境变量读取
            
        Returns:
            Config: 配置实例
        """
        if env is None:
            env = os.getenv("APP_ENV", "development")
        
        # 根据环境选择配置类
        config_class = self._config_map.get(env.lower())
        if not config_class:
            logger.warning(f"Unknown environment: {env}, using development config")
            config_class = DevelopmentConfig
        
        # 创建配置实例
        self._config = config_class()
        
        # 验证配置
        self._validate_config()
        
        # 记录配置信息
        self._log_config_info()
        
        return self._config
    
    def _validate_config(self):
        """验证配置"""
        if not self._config:
            raise ValueError("Config not loaded")
        
        # 验证必需配置
        required_settings = [
            ("APP_SECRET_KEY", "Application secret key is required"),
            ("JWT_SECRET_KEY", "JWT secret key is required"),
            ("DATABASE_URL", "Database URL is required"),
        ]
        
        for setting, error_msg in required_settings:
            value = getattr(self._config, setting, None)
            if not value or value == "":
                raise ValueError(f"{error_msg} (setting: {setting})")
        
        # 验证生产环境配置
        if self._config.APP_ENV == "production":
            production_checks = [
                ("APP_DEBUG", False, "Debug mode should be disabled in production"),
                ("APP_SECRET_KEY", lambda x: x != "dev-secret-key", 
                 "Default secret key should not be used in production"),
                ("JWT_SECRET_KEY", lambda x: x != "jwt-secret-key",
                 "Default JWT secret key should not be used in production"),
            ]
            
            for setting, expected, error_msg in production_checks:
                value = getattr(self._config, setting, None)
                
                if callable(expected):
                    if not expected(value):
                        logger.warning(f"Production warning: {error_msg}")
                elif value != expected:
                    logger.warning(f"Production warning: {error_msg}")
    
    def _log_config_info(self):
        """记录配置信息"""
        if not self._config:
            return
        
        # 记录基本信息
        logger.info(f"Application environment: {self._config.APP_ENV}")
        logger.info(f"Debug mode: {self._config.APP_DEBUG}")
        logger.info(f"Server port: {self._config.APP_PORT}")
        
        # 记录数据库信息（隐藏密码）
        db_url = self._config.DATABASE_URL
        if "@" in db_url:
            # 隐藏密码
            parts = db_url.split("@")
            if ":" in parts[0]:
                user_part = parts[0].split(":")[0] + ":*****"
                safe_db_url = user_part + "@" + parts[1]
                logger.info(f"Database: {safe_db_url}")
        else:
            logger.info(f"Database: {db_url}")
        
        # 记录Redis信息
        redis_url = self._config.REDIS_URL
        if ":" in redis_url and "@" in redis_url:
            # 隐藏密码
            parts = redis_url.split("@")
            safe_redis_url = "redis://*****@" + parts[1]
            logger.info(f"Redis: {safe_redis_url}")
        else:
            logger.info(f"Redis: {redis_url}")
    
    def get_config(self) -> Config:
        """
        获取当前配置
        
        Returns:
            Config: 配置实例
            
        Raises:
            ValueError: 如果配置未加载
        """
        if not self._config:
            raise ValueError("Config not loaded. Call load_config() first.")
        return self._config
    
    def reload_config(self):
        """重新加载配置"""
        current_env = self._config.APP_ENV if self._config else None
        self._config = None
        return self.load_config(current_env)
    
    def export_config(self, hide_secrets: bool = True) -> Dict[str, Any]:
        """
        导出配置为字典
        
        Args:
            hide_secrets: 是否隐藏敏感信息
            
        Returns:
            Dict[str, Any]: 配置字典
        """
        if not self._config:
            raise ValueError("Config not loaded")
        
        config_dict = {}
        for key in dir(self._config):
            if not key.startswith("_") and not callable(getattr(self._config, key)):
                value = getattr(self._config, key)
                
                # 隐藏敏感信息
                if hide_secrets and any(secret in key.lower() for secret in ["secret", "password", "key"]):
                    if isinstance(value, str) and value:
                        config_dict[key] = "*****"
                    else:
                        config_dict[key] = value
                else:
                    config_dict[key] = value
        
        return config_dict
    
    def save_config_to_file(self, filepath: str, hide_secrets: bool = True):
        """
        保存配置到文件
        
        Args:
            filepath: 文件路径
            hide_secrets: 是否隐藏敏感信息
        """
        config_dict = self.export_config(hide_secrets)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Configuration saved to {filepath}")


# 全局配置管理器实例
config_manager = ConfigManager()


def get_config() -> Config:
    """
    获取配置的便捷函数
    
    Returns:
        Config: 配置实例
    """
    return config_manager.get_config()


def init_config(env: Optional[str] = None) -> Config:
    """
    初始化配置的便捷函数
    
    Args:
        env: 环境名称
        
    Returns:
        Config: 配置实例
    """
    return config_manager.load_config(env)


# 默认导出
__all__ = [
    "Config",
    "DevelopmentConfig", 
    "TestingConfig", 
    "ProductionConfig",
    "ConfigManager",
    "config_manager",
    "get_config",
    "init_config"
]
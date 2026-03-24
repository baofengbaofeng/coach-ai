"""
AI服务基类模块，定义所有AI服务的通用接口和基础功能。
按照豆包AI助手最佳实践：提供类型安全的AI服务基类。
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from django.contrib.auth import get_user_model

from apps.common.utils import Timer


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 用户模型引用 ====================
User = get_user_model()


# ==================== AI服务基类 ====================
class BaseAIService(ABC):
    """
    AI服务基类，定义所有AI服务的通用接口。
    """
    
    def __init__(self, service_name: str) -> None:
        """
        初始化AI服务。
        
        Args:
            service_name: 服务名称
        """
        self.service_name: str = service_name
        self._initialized: bool = False
        self._logger: logging.Logger = logging.getLogger(f"services.{service_name}")
    
    def initialize(self) -> bool:
        """
        初始化服务。
        
        Returns:
            是否初始化成功
        """
        if self._initialized:
            return True
        
        try:
            with Timer(f"初始化 {self.service_name}"):
                success = self._initialize_internal()
                
                if success:
                    self._initialized = True
                    self._logger.info("服务初始化成功")
                else:
                    self._logger.error("服务初始化失败")
                
                return success
        except Exception as e:
            self._logger.error("服务初始化异常: %s", str(e), exc_info=True)
            return False
    
    @abstractmethod
    def _initialize_internal(self) -> bool:
        """
        内部初始化逻辑，由子类实现。
        
        Returns:
            是否初始化成功
        """
        pass
    
    def is_initialized(self) -> bool:
        """
        检查服务是否已初始化。
        
        Returns:
            是否已初始化
        """
        return self._initialized
    
    def process(self, input_data: Any, **kwargs: Any) -> Any:
        """
        处理输入数据。
        
        Args:
            input_data: 输入数据
            **kwargs: 其他参数
            
        Returns:
            处理结果
        """
        if not self._initialized:
            self._logger.warning("服务未初始化，尝试自动初始化")
            if not self.initialize():
                raise RuntimeError(f"{self.service_name} 服务初始化失败")
        
        try:
            with Timer(f"{self.service_name} 处理"):
                return self._process_internal(input_data, **kwargs)
        except Exception as e:
            self._logger.error("服务处理异常: %s", str(e), exc_info=True)
            raise
    
    @abstractmethod
    def _process_internal(self, input_data: Any, **kwargs: Any) -> Any:
        """
        内部处理逻辑，由子类实现。
        
        Args:
            input_data: 输入数据
            **kwargs: 其他参数
            
        Returns:
            处理结果
        """
        pass
    
    def batch_process(self, input_list: List[Any], **kwargs: Any) -> List[Any]:
        """
        批量处理输入数据。
        
        Args:
            input_list: 输入数据列表
            **kwargs: 其他参数
            
        Returns:
            处理结果列表
        """
        if not self._initialized:
            self._logger.warning("服务未初始化，尝试自动初始化")
            if not self.initialize():
                raise RuntimeError(f"{self.service_name} 服务初始化失败")
        
        try:
            with Timer(f"{self.service_name} 批量处理 ({len(input_list)} 项)"):
                results: List[Any] = []
                
                for i, input_data in enumerate(input_list):
                    try:
                        result = self._process_internal(input_data, **kwargs)
                        results.append(result)
                    except Exception as e:
                        self._logger.error("批量处理第 %s 项时异常: %s", i + 1, str(e))
                        results.append(None)
                
                return results
        except Exception as e:
            self._logger.error("批量处理异常: %s", str(e), exc_info=True)
            raise
    
    def validate_input(self, input_data: Any) -> bool:
        """
        验证输入数据。
        
        Args:
            input_data: 输入数据
            
        Returns:
            是否有效
        """
        try:
            return self._validate_input_internal(input_data)
        except Exception as e:
            self._logger.error("输入验证异常: %s", str(e))
            return False
    
    def _validate_input_internal(self, input_data: Any) -> bool:
        """
        内部输入验证逻辑，由子类实现。
        
        Args:
            input_data: 输入数据
            
        Returns:
            是否有效
        """
        return input_data is not None
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        获取服务信息。
        
        Returns:
            服务信息字典
        """
        return {
            "service_name": self.service_name,
            "initialized": self._initialized,
            "service_type": self.__class__.__name__,
        }
    
    def cleanup(self) -> None:
        """
        清理服务资源。
        """
        try:
            self._cleanup_internal()
            self._initialized = False
            self._logger.info("服务清理完成")
        except Exception as e:
            self._logger.error("服务清理异常: %s", str(e))
    
    def _cleanup_internal(self) -> None:
        """
        内部清理逻辑，由子类实现。
        """
        pass
    
    def __enter__(self) -> BaseAIService:
        """进入上下文管理器。"""
        self.initialize()
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """退出上下文管理器。"""
        self.cleanup()


# ==================== 用户相关的AI服务基类 ====================
class UserAwareAIService(BaseAIService):
    """
    用户相关的AI服务基类，提供用户上下文支持。
    """
    
    def __init__(self, service_name: str) -> None:
        """
        初始化用户相关的AI服务。
        
        Args:
            service_name: 服务名称
        """
        super().__init__(service_name)
        self._user_context: Optional[Dict[str, Any]] = None
    
    def set_user_context(self, user: User, context: Optional[Dict[str, Any]] = None) -> None:
        """
        设置用户上下文。
        
        Args:
            user: 用户对象
            context: 额外上下文信息
        """
        self._user_context = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "last_login": user.last_login,
        }
        
        if context:
            self._user_context.update(context)
        
        self._logger.debug("用户上下文已设置: %s", user.username)
    
    def clear_user_context(self) -> None:
        """
        清除用户上下文。
        """
        self._user_context = None
        self._logger.debug("用户上下文已清除")
    
    def get_user_context(self) -> Optional[Dict[str, Any]]:
        """
        获取用户上下文。
        
        Returns:
            用户上下文字典
        """
        return self._user_context
    
    def process_with_user(self, user: User, input_data: Any, **kwargs: Any) -> Any:
        """
        使用用户上下文处理输入数据。
        
        Args:
            user: 用户对象
            input_data: 输入数据
            **kwargs: 其他参数
            
        Returns:
            处理结果
        """
        self.set_user_context(user, kwargs.get("user_context"))
        
        try:
            result = self.process(input_data, **kwargs)
            return result
        finally:
            self.clear_user_context()
    
    def _validate_input_internal(self, input_data: Any) -> bool:
        """
        验证输入数据（包含用户上下文检查）。
        
        Args:
            input_data: 输入数据
            
        Returns:
            是否有效
        """
        if not super()._validate_input_internal(input_data):
            return False
        
        # 检查用户上下文（如果服务需要）
        if self.requires_user_context() and not self._user_context:
            self._logger.warning("服务需要用户上下文，但未设置")
            return False
        
        return True
    
    def requires_user_context(self) -> bool:
        """
        检查服务是否需要用户上下文。
        
        Returns:
            是否需要用户上下文
        """
        return False


# ==================== 配置相关的AI服务基类 ====================
class ConfigurableAIService(BaseAIService):
    """
    可配置的AI服务基类，支持运行时配置。
    """
    
    def __init__(self, service_name: str, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化可配置的AI服务。
        
        Args:
            service_name: 服务名称
            config: 服务配置
        """
        super().__init__(service_name)
        self._config: Dict[str, Any] = config or {}
        self._default_config: Dict[str, Any] = self.get_default_config()
    
    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置，由子类实现。
        
        Returns:
            默认配置字典
        """
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取当前配置。
        
        Returns:
            当前配置字典
        """
        # 合并默认配置和用户配置
        config = self._default_config.copy()
        config.update(self._config)
        return config
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        更新配置。
        
        Args:
            new_config: 新配置
        """
        old_config = self._config.copy()
        self._config.update(new_config)
        
        # 记录配置变更
        changed_keys = []
        for key, new_value in new_config.items():
            old_value = old_config.get(key)
            if old_value != new_value:
                changed_keys.append(key)
        
        if changed_keys:
            self._logger.info("配置已更新: %s", ", ".join(changed_keys))
            
            # 如果服务已初始化，可能需要重新初始化
            if self._initialized and self.requires_reinitialization_on_config_change():
                self._logger.info("配置变更需要重新初始化服务")
                self._initialized = False
    
    def requires_reinitialization_on_config_change(self) -> bool:
        """
        检查配置变更是否需要重新初始化服务。
        
        Returns:
            是否需要重新初始化
        """
        return False
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        获取服务信息（包含配置信息）。
        
        Returns:
            服务信息字典
        """
        info = super().get_service_info()
        info["config"] = self.get_config()
        info["config_keys"] = list(self.get_config().keys())
        return info


# ==================== 导出列表 ====================
__all__: List[str] = [
    "BaseAIService",
    "UserAwareAIService",
    "ConfigurableAIService",
]
"""
AI服务管理器模块，统一管理所有AI服务。
按照豆包AI助手最佳实践：提供类型安全的服务管理。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from services.base import BaseAIService
from services.recommendation import RecommendationService, RecommendationManager
from services.analytics_simple import SimpleAnalyticsService as AnalyticsService
from services.prediction import PredictionService


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== AI服务管理器 ====================
class AIServiceManager:
    """
    AI服务管理器类，统一管理所有AI服务。
    """
    
    def __init__(self) -> None:
        """初始化AI服务管理器。"""
        self._services: Dict[str, BaseAIService] = {}
        self._managers: Dict[str, Any] = {}
        self._initialized: bool = False
        
        # 初始化服务管理器
        self._init_managers()
    
    def _init_managers(self) -> None:
        """初始化服务管理器。"""
        # 推荐服务管理器
        self._managers["recommendation"] = RecommendationManager()
        
        # 其他服务管理器可以在这里添加
    
    def initialize(self) -> bool:
        """
        初始化所有AI服务。
        
        Returns:
            是否全部初始化成功
        """
        if self._initialized:
            return True
        
        try:
            _LOGGER.info("开始初始化AI服务...")
            
            # 初始化推荐服务
            rec_manager = self._managers.get("recommendation")
            if rec_manager:
                if not rec_manager.initialize_all():
                    _LOGGER.error("推荐服务初始化失败")
                    return False
                _LOGGER.info("推荐服务初始化成功")
            
            # 初始化其他服务...
            
            self._initialized = True
            _LOGGER.info("所有AI服务初始化完成")
            return True
            
        except Exception as e:
            _LOGGER.error("AI服务初始化失败: %s", str(e), exc_info=True)
            return False
    
    def get_service(self, service_type: str, service_name: str = "default") -> Optional[BaseAIService]:
        """
        获取AI服务实例。
        
        Args:
            service_type: 服务类型（recommendation, analytics, prediction）
            service_name: 服务名称
            
        Returns:
            AI服务实例
        """
        if service_type == "recommendation":
            manager = self._managers.get("recommendation")
            if manager:
                return manager.get_service(service_name)
        
        # 其他服务类型的处理...
        
        return None
    
    def get_recommendation_service(self, service_name: str = "default") -> Optional[RecommendationService]:
        """
        获取推荐服务实例。
        
        Args:
            service_name: 服务名称
            
        Returns:
            推荐服务实例
        """
        manager = self._managers.get("recommendation")
        if manager:
            return manager.get_service(service_name)
        return None
    
    def get_analytics_service(self, config: Optional[Dict[str, Any]] = None) -> AnalyticsService:
        """
        获取分析服务实例。
        
        Args:
            config: 服务配置
            
        Returns:
            分析服务实例
        """
        service_key = f"analytics_{hash(str(config)) if config else 'default'}"
        
        if service_key not in self._services:
            self._services[service_key] = AnalyticsService(config)
        
        return self._services[service_key]
    
    def get_prediction_service(self, config: Optional[Dict[str, Any]] = None) -> PredictionService:
        """
        获取预测服务实例。
        
        Args:
            config: 服务配置
            
        Returns:
            预测服务实例
        """
        service_key = f"prediction_{hash(str(config)) if config else 'default'}"
        
        if service_key not in self._services:
            self._services[service_key] = PredictionService(config)
        
        return self._services[service_key]
    
    def process_recommendation(self, user: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        处理推荐请求。
        
        Args:
            user: 用户对象或ID
            **kwargs: 其他参数
            
        Returns:
            推荐结果
        """
        try:
            service = self.get_recommendation_service()
            if not service:
                return self._create_error_response("推荐服务不可用")
            
            if not service.is_initialized():
                if not service.initialize():
                    return self._create_error_response("推荐服务初始化失败")
            
            return service.process(user, **kwargs)
            
        except Exception as e:
            _LOGGER.error("处理推荐请求失败: %s", str(e), exc_info=True)
            return self._create_error_response(f"处理推荐请求失败: {str(e)}")
    
    def process_analysis(self, user: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        处理分析请求。
        
        Args:
            user: 用户对象或ID
            **kwargs: 其他参数
            
        Returns:
            分析结果
        """
        try:
            service = self.get_analytics_service(kwargs.get("config"))
            if not service.is_initialized():
                if not service.initialize():
                    return self._create_error_response("分析服务初始化失败")
            
            return service.process(user, **kwargs)
            
        except Exception as e:
            _LOGGER.error("处理分析请求失败: %s", str(e), exc_info=True)
            return self._create_error_response(f"处理分析请求失败: {str(e)}")
    
    def process_prediction(self, user: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        处理预测请求。
        
        Args:
            user: 用户对象或ID
            **kwargs: 其他参数
            
        Returns:
            预测结果
        """
        try:
            service = self.get_prediction_service(kwargs.get("config"))
            if not service.is_initialized():
                if not service.initialize():
                    return self._create_error_response("预测服务初始化失败")
            
            return service.process(user, **kwargs)
            
        except Exception as e:
            _LOGGER.error("处理预测请求失败: %s", str(e), exc_info=True)
            return self._create_error_response(f"处理预测请求失败: {str(e)}")
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        获取服务状态。
        
        Returns:
            服务状态信息
        """
        status = {
            "initialized": self._initialized,
            "total_services": len(self._services),
            "services": {},
            "managers": {},
        }
        
        # 收集服务状态
        for name, service in self._services.items():
            status["services"][name] = {
                "type": service.__class__.__name__,
                "initialized": service.is_initialized(),
                "service_name": service.service_name,
            }
        
        # 收集管理器状态
        for name, manager in self._managers.items():
            if hasattr(manager, "get_service_info"):
                status["managers"][name] = manager.get_service_info()
            else:
                status["managers"][name] = {
                    "type": manager.__class__.__name__,
                    "status": "active",
                }
        
        return status
    
    def get_available_services(self) -> List[str]:
        """
        获取可用的服务列表。
        
        Returns:
            服务名称列表
        """
        services = []
        
        # 从管理器获取服务
        for manager_name, manager in self._managers.items():
            if hasattr(manager, "get_available_services"):
                services.extend(manager.get_available_services())
            else:
                services.append(manager_name)
        
        # 从直接管理的服务获取
        for service_key, service in self._services.items():
            if service.service_name not in services:
                services.append(service.service_name)
        
        return list(set(services))  # 去重
    
    def cleanup(self) -> None:
        """
        清理所有AI服务。
        """
        _LOGGER.info("开始清理AI服务...")
        
        # 清理服务
        for name, service in self._services.items():
            try:
                service.cleanup()
                _LOGGER.info("服务 %s 清理完成", name)
            except Exception as e:
                _LOGGER.error("服务 %s 清理失败: %s", name, str(e))
        
        # 清理管理器
        for name, manager in self._managers.items():
            if hasattr(manager, "cleanup_all"):
                try:
                    manager.cleanup_all()
                    _LOGGER.info("管理器 %s 清理完成", name)
                except Exception as e:
                    _LOGGER.error("管理器 %s 清理失败: %s", name, str(e))
        
        self._services.clear()
        self._managers.clear()
        self._initialized = False
        
        _LOGGER.info("所有AI服务清理完成")
    
    def _create_error_response(self, message: str, code: str = "service_error") -> Dict[str, Any]:
        """
        创建错误响应。
        
        Args:
            message: 错误消息
            code: 错误代码
            
        Returns:
            错误响应字典
        """
        return {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "timestamp": self._get_timestamp(),
            }
        }
    
    def _get_timestamp(self) -> str:
        """
        获取当前时间戳。
        
        Returns:
            ISO格式时间戳
        """
        from django.utils import timezone
        return timezone.now().isoformat()
    
    def __enter__(self) -> AIServiceManager:
        """进入上下文管理器。"""
        self.initialize()
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """退出上下文管理器。"""
        self.cleanup()


# ==================== 全局AI服务管理器实例 ====================
_global_manager: Optional[AIServiceManager] = None


def get_ai_service_manager() -> AIServiceManager:
    """
    获取全局AI服务管理器实例。
    
    Returns:
        AI服务管理器实例
    """
    global _global_manager
    
    if _global_manager is None:
        _global_manager = AIServiceManager()
    
    return _global_manager


def initialize_ai_services() -> bool:
    """
    初始化全局AI服务。
    
    Returns:
        是否初始化成功
    """
    manager = get_ai_service_manager()
    return manager.initialize()


def cleanup_ai_services() -> None:
    """
    清理全局AI服务。
    """
    global _global_manager
    
    if _global_manager:
        _global_manager.cleanup()
        _global_manager = None


def get_service_status() -> Dict[str, Any]:
    """
    获取全局服务状态。
    
    Returns:
        服务状态信息
    """
    manager = get_ai_service_manager()
    return manager.get_service_status()


# ==================== 导出列表 ====================
__all__: List[str] = [
    "AIServiceManager",
    "get_ai_service_manager",
    "initialize_ai_services",
    "cleanup_ai_services",
    "get_service_status",
]
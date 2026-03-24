"""
通用API视图。
按照豆包AI助手最佳实践：提供类型安全的通用API视图。
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from django.http import HttpRequest, HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers.common_serializers import (
    SuccessResponseSerializer,
    ErrorResponseSerializer,
)


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 健康检查视图 ====================
class HealthCheckView(APIView):
    """
    健康检查API视图。
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request: HttpRequest) -> Response:
        """
        健康检查端点。
        
        Args:
            request: HTTP请求
            
        Returns:
            HTTP响应
        """
        try:
            from django.db import connection
            from django.core.cache import cache
            
            # 检查数据库连接
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_healthy = cursor.fetchone()[0] == 1
            
            # 检查缓存
            cache.set("health_check", "ok", 5)
            cache_healthy = cache.get("health_check") == "ok"
            
            # 检查服务状态
            services_status = {
                "database": "healthy" if db_healthy else "unhealthy",
                "cache": "healthy" if cache_healthy else "unhealthy",
                "api": "healthy",
            }
            
            # 构建响应
            response_data = {
                "success": True,
                "status": "healthy",
                "timestamp": self._get_timestamp(),
                "services": services_status,
                "version": self._get_version(),
            }
            
            serializer = SuccessResponseSerializer(data=response_data)
            if serializer.is_valid():
                return Response(serializer.validated_data)
            else:
                return Response(
                    self._create_error_response("响应数据验证失败"),
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            
        except Exception as e:
            _LOGGER.error("健康检查失败: %s", str(e), exc_info=True)
            return Response(
                self._create_error_response(f"健康检查失败: {str(e)}"),
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
    
    def _get_timestamp(self) -> str:
        """
        获取当前时间戳。
        
        Returns:
            ISO格式时间戳
        """
        from django.utils import timezone
        return timezone.now().isoformat()
    
    def _get_version(self) -> str:
        """
        获取API版本。
        
        Returns:
            版本字符串
        """
        return "1.0.0"


# ==================== 系统状态视图 ====================
class SystemStatusView(APIView):
    """
    系统状态API视图。
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request: HttpRequest) -> Response:
        """
        系统状态端点。
        
        Args:
            request: HTTP请求
            
        Returns:
            HTTP响应
        """
        try:
            import platform
            from django.conf import settings
            
            # 获取系统信息（不依赖psutil）
            system_info = {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "django_version": self._get_django_version(),
                "cpu_count": "N/A",  # 简化，不依赖psutil
                "memory_total": "N/A",
                "memory_available": "N/A",
                "disk_usage": "N/A",
            }
            
            # 获取应用信息
            app_info = {
                "debug": settings.DEBUG,
                "allowed_hosts": settings.ALLOWED_HOSTS,
                "installed_apps_count": len(settings.INSTALLED_APPS),
                "database_backend": settings.DATABASES["default"]["ENGINE"],
            }
            
            # 构建响应
            response_data = {
                "success": True,
                "timestamp": self._get_timestamp(),
                "system": system_info,
                "application": app_info,
            }
            
            serializer = SuccessResponseSerializer(data=response_data)
            if serializer.is_valid():
                return Response(serializer.validated_data)
            else:
                return Response(
                    self._create_error_response("响应数据验证失败"),
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            
        except Exception as e:
            _LOGGER.error("获取系统状态失败: %s", str(e), exc_info=True)
            return Response(
                self._create_error_response(f"获取系统状态失败: {str(e)}"),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    def _get_django_version(self) -> str:
        """
        获取Django版本。
        
        Returns:
            Django版本字符串
        """
        import django
        return django.get_version()
    
    def _get_timestamp(self) -> str:
        """
        获取当前时间戳。
        
        Returns:
            ISO格式时间戳
        """
        from django.utils import timezone
        return timezone.now().isoformat()


# ==================== API信息视图 ====================
class APIInfoView(APIView):
    """
    API信息视图。
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request: HttpRequest) -> Response:
        """
        API信息端点。
        
        Args:
            request: HTTP请求
            
        Returns:
            HTTP响应
        """
        try:
            # API端点信息
            endpoints = {
                "ai": {
                    "recommendation": {
                        "method": "POST",
                        "url": "/api/v1/ai/recommendation/",
                        "description": "获取AI推荐",
                        "authentication": True,
                    },
                    "analysis": {
                        "method": "POST",
                        "url": "/api/v1/ai/analysis/",
                        "description": "获取AI分析",
                        "authentication": True,
                    },
                    "prediction": {
                        "method": "POST",
                        "url": "/api/v1/ai/prediction/",
                        "description": "获取AI预测",
                        "authentication": True,
                    },
                    "advice": {
                        "method": "POST",
                        "url": "/api/v1/ai/advice/",
                        "description": "获取AI建议",
                        "authentication": True,
                    },
                    "status": {
                        "method": "GET",
                        "url": "/api/v1/ai/status/",
                        "description": "获取AI服务状态",
                        "authentication": True,
                    },
                },
                "system": {
                    "health": {
                        "method": "GET",
                        "url": "/api/v1/health/",
                        "description": "健康检查",
                        "authentication": False,
                    },
                    "status": {
                        "method": "GET",
                        "url": "/api/v1/status/",
                        "description": "系统状态",
                        "authentication": False,
                    },
                    "info": {
                        "method": "GET",
                        "url": "/api/v1/info/",
                        "description": "API信息",
                        "authentication": False,
                    },
                },
            }
            
            # 构建响应
            response_data = {
                "success": True,
                "timestamp": self._get_timestamp(),
                "api": {
                    "version": "1.0.0",
                    "name": "CoachAI API",
                    "description": "CoachAI智能教练系统RESTful API",
                    "base_url": "/api/v1/",
                    "endpoints": endpoints,
                },
                "authentication": {
                    "methods": ["JWT", "Session", "Basic"],
                    "default": "JWT",
                },
                "rate_limiting": {
                    "enabled": False,
                    "limits": "待实现",
                },
            }
            
            serializer = SuccessResponseSerializer(data=response_data)
            if serializer.is_valid():
                return Response(serializer.validated_data)
            else:
                return Response(
                    self._create_error_response("响应数据验证失败"),
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            
        except Exception as e:
            _LOGGER.error("获取API信息失败: %s", str(e), exc_info=True)
            return Response(
                self._create_error_response(f"获取API信息失败: {str(e)}"),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    def _get_timestamp(self) -> str:
        """
        获取当前时间戳。
        
        Returns:
            ISO格式时间戳
        """
        from django.utils import timezone
        return timezone.now().isoformat()


# ==================== 错误处理视图 ====================
def bad_request(request: HttpRequest, exception: Exception) -> HttpResponse:
    """
    400错误处理。
    
    Args:
        request: HTTP请求
        exception: 异常
        
    Returns:
        HTTP响应
    """
    error_data = {
        "success": False,
        "error": {
            "code": "bad_request",
            "message": "请求格式错误",
            "details": str(exception) if exception else "未知错误",
        },
        "timestamp": _get_timestamp(),
    }
    
    serializer = ErrorResponseSerializer(data=error_data)
    if serializer.is_valid():
        return JsonResponse(serializer.validated_data, status=400)
    else:
        return JsonResponse(
            {"error": "响应序列化失败"},
            status=500,
        )


def permission_denied(request: HttpRequest, exception: Exception) -> HttpResponse:
    """
    403错误处理。
    
    Args:
        request: HTTP请求
        exception: 异常
        
    Returns:
        HTTP响应
    """
    error_data = {
        "success": False,
        "error": {
            "code": "permission_denied",
            "message": "权限不足",
            "details": str(exception) if exception else "未知错误",
        },
        "timestamp": _get_timestamp(),
    }
    
    serializer = ErrorResponseSerializer(data=error_data)
    if serializer.is_valid():
        return JsonResponse(serializer.validated_data, status=403)
    else:
        return JsonResponse(
            {"error": "响应序列化失败"},
            status=500,
        )


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """
    404错误处理。
    
    Args:
        request: HTTP请求
        exception: 异常
        
    Returns:
        HTTP响应
    """
    error_data = {
        "success": False,
        "error": {
            "code": "not_found",
            "message": "资源未找到",
            "details": f"请求路径: {request.path}",
        },
        "timestamp": _get_timestamp(),
    }
    
    serializer = ErrorResponseSerializer(data=error_data)
    if serializer.is_valid():
        return JsonResponse(serializer.validated_data, status=404)
    else:
        return JsonResponse(
            {"error": "响应序列化失败"},
            status=500,
        )


def server_error(request: HttpRequest) -> HttpResponse:
    """
    500错误处理。
    
    Args:
        request: HTTP请求
        
    Returns:
        HTTP响应
    """
    error_data = {
        "success": False,
        "error": {
            "code": "internal_server_error",
            "message": "服务器内部错误",
            "details": "请稍后重试或联系管理员",
        },
        "timestamp": _get_timestamp(),
    }
    
    serializer = ErrorResponseSerializer(data=error_data)
    if serializer.is_valid():
        return JsonResponse(serializer.validated_data, status=500)
    else:
        return JsonResponse(
            {"error": "响应序列化失败"},
            status=500,
        )


def _get_timestamp() -> str:
    """
    获取当前时间戳。
    
    Returns:
        ISO格式时间戳
    """
    from django.utils import timezone
    return timezone.now().isoformat()


# ==================== 工具方法 ====================
def _create_error_response(message: str, code: str = "internal_error") -> Dict[str, Any]:
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
            "timestamp": _get_timestamp(),
        }
    }
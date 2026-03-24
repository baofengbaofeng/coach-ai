"""
AI服务API视图。
按照豆包AI助手最佳实践：提供类型安全的AI API视图。
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers.ai_serializers import (
    AIRecommendationRequestSerializer,
    AIRecommendationResponseSerializer,
    AIAnalysisRequestSerializer,
    AIAnalysisResponseSerializer,
    AIPredictionRequestSerializer,
    AIPredictionResponseSerializer,
    AIAdviceRequestSerializer,
    AIAdviceResponseSerializer,
)
from services.manager import get_ai_service_manager


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== AI推荐视图 ====================
class AIRecommendationView(APIView):
    """
    AI推荐API视图。
    """
    
    permission_classes = [IsAuthenticated]
    
    @method_decorator(cache_page(60 * 5))  # 缓存5分钟
    @method_decorator(vary_on_cookie)
    def post(self, request) -> Response:
        """
        获取AI推荐。
        
        Args:
            request: HTTP请求
            
        Returns:
            HTTP响应
        """
        try:
            # 验证请求数据
            serializer = AIRecommendationRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {
                        "success": False,
                        "error": {
                            "code": "validation_error",
                            "message": "请求数据验证失败",
                            "details": serializer.errors,
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            validated_data = serializer.validated_data
            
            # 获取AI服务管理器
            manager = get_ai_service_manager()
            
            # 处理推荐请求
            result = manager.process_recommendation(
                user=request.user,
                type=validated_data.get("recommendation_type", "all"),
                max_recommendations=validated_data.get("max_recommendations", 10),
                similarity_threshold=validated_data.get("similarity_threshold", 0.6),
                diversity_factor=validated_data.get("diversity_factor", 0.3),
                enable_content_based=validated_data.get("enable_content_based", True),
                enable_collaborative=validated_data.get("enable_collaborative", True),
                enable_hybrid=validated_data.get("enable_hybrid", True),
                user_context=validated_data.get("user_context"),
            )
            
            # 验证响应数据
            response_serializer = AIRecommendationResponseSerializer(data=result)
            if not response_serializer.is_valid():
                _LOGGER.error("AI推荐响应数据验证失败: %s", response_serializer.errors)
                return Response(
                    {
                        "success": False,
                        "error": {
                            "code": "response_validation_error",
                            "message": "响应数据验证失败",
                        }
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            
            return Response(response_serializer.validated_data)
            
        except Exception as e:
            _LOGGER.error("AI推荐处理失败: %s", str(e), exc_info=True)
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "internal_server_error",
                        "message": "AI推荐处理失败",
                        "details": str(e),
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ==================== AI分析视图 ====================
class AIAnalysisView(APIView):
    """
    AI分析API视图。
    """
    
    permission_classes = [IsAuthenticated]
    
    @method_decorator(cache_page(60 * 10))  # 缓存10分钟
    @method_decorator(vary_on_cookie)
    def post(self, request) -> Response:
        """
        获取AI分析。
        
        Args:
            request: HTTP请求
            
        Returns:
            HTTP响应
        """
        try:
            # 验证请求数据
            serializer = AIAnalysisRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {
                        "success": False,
                        "error": {
                            "code": "validation_error",
                            "message": "请求数据验证失败",
                            "details": serializer.errors,
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            validated_data = serializer.validated_data
            
            # 获取AI服务管理器
            manager = get_ai_service_manager()
            
            # 处理分析请求
            result = manager.process_analysis(
                user=request.user,
                type=validated_data.get("analysis_type", "comprehensive"),
                period_days=validated_data.get("period_days", 30),
                enable_basic_analysis=validated_data.get("enable_basic_analysis", True),
                enable_trend_analysis=validated_data.get("enable_trend_analysis", True),
                enable_pattern_recognition=validated_data.get("enable_pattern_recognition", True),
                enable_insight_extraction=validated_data.get("enable_insight_extraction", True),
                user_context=validated_data.get("user_context"),
            )
            
            # 验证响应数据
            response_serializer = AIAnalysisResponseSerializer(data=result)
            if not response_serializer.is_valid():
                _LOGGER.error("AI分析响应数据验证失败: %s", response_serializer.errors)
                return Response(
                    {
                        "success": False,
                        "error": {
                            "code": "response_validation_error",
                            "message": "响应数据验证失败",
                        }
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            
            return Response(response_serializer.validated_data)
            
        except Exception as e:
            _LOGGER.error("AI分析处理失败: %s", str(e), exc_info=True)
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "internal_server_error",
                        "message": "AI分析处理失败",
                        "details": str(e),
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ==================== AI预测视图 ====================
class AIPredictionView(APIView):
    """
    AI预测API视图。
    """
    
    permission_classes = [IsAuthenticated]
    
    @method_decorator(cache_page(60 * 15))  # 缓存15分钟
    @method_decorator(vary_on_cookie)
    def post(self, request) -> Response:
        """
        获取AI预测。
        
        Args:
            request: HTTP请求
            
        Returns:
            HTTP响应
        """
        try:
            # 验证请求数据
            serializer = AIPredictionRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {
                        "success": False,
                        "error": {
                            "code": "validation_error",
                            "message": "请求数据验证失败",
                            "details": serializer.errors,
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            validated_data = serializer.validated_data
            
            # 获取AI服务管理器
            manager = get_ai_service_manager()
            
            # 处理预测请求
            result = manager.process_prediction(
                user=request.user,
                type=validated_data.get("prediction_type", "all"),
                horizon_days=validated_data.get("horizon_days", 7),
                confidence_threshold=validated_data.get("confidence_threshold", 0.7),
                enable_task_completion_prediction=validated_data.get("enable_task_completion_prediction", True),
                enable_exercise_habit_prediction=validated_data.get("enable_exercise_habit_prediction", True),
                enable_achievement_unlock_prediction=validated_data.get("enable_achievement_unlock_prediction", True),
                enable_trend_prediction=validated_data.get("enable_trend_prediction", True),
                user_context=validated_data.get("user_context"),
            )
            
            # 验证响应数据
            response_serializer = AIPredictionResponseSerializer(data=result)
            if not response_serializer.is_valid():
                _LOGGER.error("AI预测响应数据验证失败: %s", response_serializer.errors)
                return Response(
                    {
                        "success": False,
                        "error": {
                            "code": "response_validation_error",
                            "message": "响应数据验证失败",
                        }
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            
            return Response(response_serializer.validated_data)
            
        except Exception as e:
            _LOGGER.error("AI预测处理失败: %s", str(e), exc_info=True)
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "internal_server_error",
                        "message": "AI预测处理失败",
                        "details": str(e),
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ==================== AI建议视图 ====================
class AIAdviceView(APIView):
    """
    AI建议API视图。
    """
    
    permission_classes = [IsAuthenticated]
    
    @method_decorator(cache_page(60 * 30))  # 缓存30分钟
    @method_decorator(vary_on_cookie)
    def post(self, request) -> Response:
        """
        获取AI建议。
        
        Args:
            request: HTTP请求
            
        Returns:
            HTTP响应
        """
        try:
            # 验证请求数据
            serializer = AIAdviceRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {
                        "success": False,
                        "error": {
                            "code": "validation_error",
                            "message": "请求数据验证失败",
                            "details": serializer.errors,
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            validated_data = serializer.validated_data
            
            # 获取AI服务管理器
            manager = get_ai_service_manager()
            
            # 处理建议请求
            result = manager.generate_ai_advice(
                user=request.user,
                advice_type=validated_data.get("advice_type", "personalized"),
                analysis_data=validated_data.get("analysis_data"),
                recommendations=validated_data.get("recommendations"),
                predictions=validated_data.get("predictions"),
                user_context=validated_data.get("user_context"),
            )
            
            # 验证响应数据
            response_serializer = AIAdviceResponseSerializer(data=result)
            if not response_serializer.is_valid():
                _LOGGER.error("AI建议响应数据验证失败: %s", response_serializer.errors)
                return Response(
                    {
                        "success": False,
                        "error": {
                            "code": "response_validation_error",
                            "message": "响应数据验证失败",
                        }
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            
            return Response(response_serializer.validated_data)
            
        except Exception as e:
            _LOGGER.error("AI建议处理失败: %s", str(e), exc_info=True)
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "internal_server_error",
                        "message": "AI建议处理失败",
                        "details": str(e),
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ==================== AI服务状态视图 ====================
class AIServiceStatusView(APIView):
    """
    AI服务状态API视图。
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request) -> Response:
        """
        获取AI服务状态。
        
        Args:
            request: HTTP请求
            
        Returns:
            HTTP响应
        """
        try:
            # 获取AI服务管理器
            manager = get_ai_service_manager()
            
            # 获取服务状态
            status_info = manager.get_service_status()
            
            return Response(
                {
                    "success": True,
                    "timestamp": self._get_timestamp(),
                    "status": status_info,
                }
            )
            
        except Exception as e:
            _LOGGER.error("获取AI服务状态失败: %s", str(e), exc_info=True)
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "internal_server_error",
                        "message": "获取AI服务状态失败",
                        "details": str(e),
                    }
                },
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
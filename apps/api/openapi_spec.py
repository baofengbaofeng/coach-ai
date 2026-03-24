"""
OpenAPI规范生成器。
按照豆包AI助手最佳实践：提供类型安全的OpenAPI规范。
"""
from __future__ import annotations

import json
from typing import Any, Dict, List


# ==================== OpenAPI规范生成器 ====================
class OpenAPISpecGenerator:
    """
    OpenAPI规范生成器类。
    """
    
    def __init__(self) -> None:
        """初始化OpenAPI规范生成器。"""
        self._spec: Dict[str, Any] = {
            "openapi": "3.0.0",
            "info": self._get_info(),
            "servers": self._get_servers(),
            "paths": self._get_paths(),
            "components": self._get_components(),
            "tags": self._get_tags(),
            "externalDocs": self._get_external_docs(),
        }
    
    def _get_info(self) -> Dict[str, Any]:
        """
        获取API信息。
        
        Returns:
            API信息字典
        """
        return {
            "title": "CoachAI API",
            "description": (
                "# CoachAI 智能教练系统 API\n\n"
                "## 概述\n"
                "CoachAI是一个智能教练系统，提供运动管理、任务管理、成就系统和AI智能服务。\n\n"
                "## 主要功能\n"
                "1. **AI智能服务**：推荐、分析、预测、建议\n"
                "2. **运动管理**：运动计划、运动记录、运动分析\n"
                "3. **任务管理**：任务创建、任务跟踪、任务统计\n"
                "4. **成就系统**：成就定义、成就进度、成就解锁\n"
                "5. **用户管理**：用户资料、用户统计、用户偏好\n\n"
                "## 认证方式\n"
                "- JWT Token认证\n"
                "- Session认证\n"
                "- Basic认证\n\n"
                "## 响应格式\n"
                "所有API响应都遵循统一的JSON格式。"
            ),
            "version": "1.0.0",
            "contact": {
                "name": "CoachAI Team",
                "email": "support@coachai.example.com",
                "url": "https://coachai.example.com",
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT",
            },
            "termsOfService": "https://coachai.example.com/terms",
        }
    
    def _get_servers(self) -> List[Dict[str, str]]:
        """
        获取服务器信息。
        
        Returns:
            服务器列表
        """
        return [
            {
                "url": "http://localhost:8000/api/v1",
                "description": "本地开发服务器",
                "variables": {
                    "protocol": {
                        "default": "http",
                        "enum": ["http", "https"],
                    },
                },
            },
            {
                "url": "https://api.coachai.example.com/api/v1",
                "description": "生产服务器",
            },
            {
                "url": "https://staging.api.coachai.example.com/api/v1",
                "description": "测试服务器",
            },
        ]
    
    def _get_tags(self) -> List[Dict[str, str]]:
        """
        获取标签定义。
        
        Returns:
            标签列表
        """
        return [
            {
                "name": "AI",
                "description": "人工智能服务",
                "externalDocs": {
                    "description": "了解更多",
                    "url": "https://coachai.example.com/docs/ai",
                },
            },
            {
                "name": "Users",
                "description": "用户管理",
            },
            {
                "name": "Exercises",
                "description": "运动管理",
            },
            {
                "name": "Tasks",
                "description": "任务管理",
            },
            {
                "name": "Achievements",
                "description": "成就管理",
            },
            {
                "name": "System",
                "description": "系统管理",
            },
            {
                "name": "Health",
                "description": "健康检查",
            },
        ]
    
    def _get_external_docs(self) -> Dict[str, str]:
        """
        获取外部文档。
        
        Returns:
            外部文档字典
        """
        return {
            "description": "完整文档",
            "url": "https://coachai.example.com/docs",
        }
    
    def _get_paths(self) -> Dict[str, Any]:
        """
        获取API路径定义。
        
        Returns:
            路径字典
        """
        return {
            # ==================== AI服务路径 ====================
            "/ai/recommendation/": self._get_ai_recommendation_path(),
            "/ai/analysis/": self._get_ai_analysis_path(),
            "/ai/prediction/": self._get_ai_prediction_path(),
            "/ai/advice/": self._get_ai_advice_path(),
            "/ai/status/": self._get_ai_status_path(),
            
            # ==================== 系统服务路径 ====================
            "/health/": self._get_health_path(),
            "/status/": self._get_system_status_path(),
            "/info/": self._get_api_info_path(),
            
            # ==================== 用户服务路径 ====================
            "/users/profile/": self._get_user_profile_path(),
            "/users/stats/": self._get_user_stats_path(),
            "/users/preferences/": self._get_user_preferences_path(),
            
            # ==================== 运动服务路径 ====================
            "/exercises/records/": self._get_exercise_records_path(),
            "/exercises/plans/": self._get_exercise_plans_path(),
            "/exercises/stats/": self._get_exercise_stats_path(),
            
            # ==================== 任务服务路径 ====================
            "/tasks/": self._get_tasks_path(),
            "/tasks/categories/": self._get_task_categories_path(),
            "/tasks/stats/": self._get_task_stats_path(),
            
            # ==================== 成就服务路径 ====================
            "/achievements/": self._get_achievements_path(),
            "/achievements/user/": self._get_user_achievements_path(),
            "/achievements/stats/": self._get_achievement_stats_path(),
        }
    
    def _get_ai_recommendation_path(self) -> Dict[str, Any]:
        """
        获取AI推荐路径定义。
        
        Returns:
            路径定义字典
        """
        return {
            "post": {
                "tags": ["AI"],
                "summary": "获取AI推荐",
                "description": "根据用户数据和偏好生成个性化推荐",
                "operationId": "getAIRecommendation",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/AIRecommendationRequest",
                            },
                            "examples": {
                                "basic": {
                                    "summary": "基础推荐",
                                    "value": {
                                        "recommendation_type": "all",
                                        "max_recommendations": 5,
                                    },
                                },
                                "exercise": {
                                    "summary": "运动推荐",
                                    "value": {
                                        "recommendation_type": "exercise",
                                        "max_recommendations": 3,
                                        "similarity_threshold": 0.7,
                                    },
                                },
                                "task": {
                                    "summary": "任务推荐",
                                    "value": {
                                        "recommendation_type": "task",
                                        "max_recommendations": 5,
                                        "diversity_factor": 0.4,
                                    },
                                },
                            },
                        },
                    },
                },
                "responses": {
                    "200": {
                        "description": "推荐生成成功",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AIRecommendationResponse",
                                },
                                "examples": {
                                    "success": {
                                        "summary": "成功响应",
                                        "value": {
                                            "success": True,
                                            "user_id": 1,
                                            "username": "test_user",
                                            "recommendation_type": "all",
                                            "total_count": 5,
                                            "generated_at": "2026-03-24T10:30:00Z",
                                            "recommendations": [
                                                {
                                                    "id": "rec_001",
                                                    "title": "晨跑30分钟",
                                                    "description": "基于您的运动习惯推荐",
                                                    "type": "exercise",
                                                    "score": 0.85,
                                                    "confidence": 0.8,
                                                    "metadata": {
                                                        "duration": 30,
                                                        "calories": 300,
                                                        "difficulty": "medium",
                                                    },
                                                },
                                            ],
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError",
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized",
                    },
                    "500": {
                        "$ref": "#/components/responses/InternalServerError",
                    },
                },
                "x-code-samples": [
                    {
                        "lang": "Python",
                        "source": "import requests\n\nresponse = requests.post(\n    'http://localhost:8000/api/v1/ai/recommendation/',\n    json={'recommendation_type': 'all', 'max_recommendations': 5},\n    headers={'Authorization': 'Bearer YOUR_TOKEN'}\n)\nprint(response.json())",
                    },
                    {
                        "lang": "JavaScript",
                        "source": "fetch('http://localhost:8000/api/v1/ai/recommendation/', {\n  method: 'POST',\n  headers: {\n    'Content-Type': 'application/json',\n    'Authorization': 'Bearer YOUR_TOKEN'\n  },\n  body: JSON.stringify({\n    recommendation_type: 'all',\n    max_recommendations: 5\n  })\n})\n.then(response => response.json())\n.then(data => console.log(data));",
                    },
                    {
                        "lang": "cURL",
                        "source": "curl -X POST \\\n  http://localhost:8000/api/v1/ai/recommendation/ \\\n  -H 'Authorization: Bearer YOUR_TOKEN' \\\n  -H 'Content-Type: application/json' \\\n  -d '{\"recommendation_type\": \"all\", \"max_recommendations\": 5}'",
                    },
                ],
            },
        }
    
    def _get_ai_analysis_path(self) -> Dict[str, Any]:
        """
        获取AI分析路径定义。
        
        Returns:
            路径定义字典
        """
        return {
            "post": {
                "tags": ["AI"],
                "summary": "获取AI分析",
                "description": "分析用户数据，生成洞察和建议",
                "operationId": "getAIAnalysis",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/AIAnalysisRequest",
                            },
                        },
                    },
                },
                "responses": {
                    "200": {
                        "description": "分析生成成功",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AIAnalysisResponse",
                                },
                            },
                        },
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError",
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized",
                    },
                    "500": {
                        "$ref": "#/components/responses/InternalServerError",
                    },
                },
            },
        }
    
    def _get_ai_prediction_path(self) -> Dict[str, Any]:
        """
        获取AI预测路径定义。
        
        Returns:
            路径定义字典
        """
        return {
            "post": {
                "tags": ["AI"],
                "summary": "获取AI预测",
                "description": "基于用户数据和历史趋势生成预测",
                "operationId": "getAIPrediction",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/AIPredictionRequest",
                            },
                        },
                    },
                },
                "responses": {
                    "200": {
                        "description": "预测生成成功",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AIPredictionResponse",
                                },
                            },
                        },
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError",
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized",
                    },
                    "500": {
                        "$ref": "#/components/responses/InternalServerError",
                    },
                },
            },
        }
    
    def _get_ai_advice_path(self) -> Dict[str, Any]:
        """
        获取AI建议路径定义。
        
        Returns:
            路径定义字典
        """
        return {
            "post": {
                "tags": ["AI"],
                "summary": "获取AI建议",
                "description": "基于分析结果生成个性化建议",
                "operationId": "getAIAdvice",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/AIAdviceRequest",
                            },
                        },
                    },
                },
                "responses": {
                    "200": {
                        "description": "建议生成成功",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AIAdviceResponse",
                                },
                            },
                        },
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError",
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized",
                    },
                    "500": {
                        "$ref": "#/components/responses/InternalServerError",
                    },
                },
            },
        }
    
    def _get_ai_status_path(self) -> Dict[str, Any]:
        """
        获取AI服务状态路径定义。
        
        Returns:
            路径定义字典
        """
        return {
            "get": {
                "tags": ["AI"],
                "summary": "获取AI服务状态",
                "description": "获取AI服务的状态和配置信息",
                "operationId": "getAIServiceStatus",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "状态获取成功",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AIServiceStatusResponse",
                                },
                            },
                        },
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized",
                    },
                    "500": {
                        "$ref": "#/components/responses/InternalServerError",
                    },
                },
            },
        }
    
    def _get_health_path(self) -> Dict[str, Any]:
        """
        获取健康检查路径定义。
        
        Returns:
            路径定义字典
        """
        return {
            "get": {
                "tags": ["Health", "System"],
                "summary": "健康检查",
                "description": "检查系统健康状态",
                "operationId": "getHealth",
                "responses": {
                    "200": {
                        "description": "系统健康",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HealthResponse",
                                },
                            },
                        },
                    },
                    "503": {
                        "description": "服务不可用",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse",
                                },
                            },
                        },
                    },
                },
            },
        }
    
    def _get_system_status_path(self) -> Dict[str, Any]:
        """
        获取系统状态路径定义。
        
        Returns:
            路径定义字典
        """
        return {
            "get": {
                "tags": ["System"],
                "summary": "系统状态",
                "description": "获取系统状态信息",
                "operationId": "getSystemStatus",
                "responses": {
                    "200": {
                        "description": "状态获取成功",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/SystemStatusResponse",
                                },
                            },
                        },
                    },
                    "500": {
                        "$ref": "#/components/responses/InternalServerError",
                    },
                },
            },
        }
    
    def _get_api_info_path(self) -> Dict[str, Any]:
        """
        获取API信息路径定义
"""
API文档生成器。
按照豆包AI助手最佳实践：提供类型安全的API文档。
"""
from __future__ import annotations

import json
from typing import Any, Dict, List


# ==================== API文档生成器 ====================
class APIDocumentationGenerator:
    """
    API文档生成器类。
    """
    
    def __init__(self) -> None:
        """初始化API文档生成器。"""
        self._docs: Dict[str, Any] = {
            "openapi": "3.0.0",
            "info": self._get_api_info(),
            "servers": self._get_servers(),
            "paths": {},
            "components": self._get_components(),
            "tags": self._get_tags(),
        }
    
    def _get_api_info(self) -> Dict[str, Any]:
        """
        获取API信息。
        
        Returns:
            API信息字典
        """
        return {
            "title": "CoachAI API",
            "description": "CoachAI智能教练系统RESTful API",
            "version": "1.0.0",
            "contact": {
                "name": "CoachAI Team",
                "email": "support@coachai.example.com",
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT",
            },
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
                "description": "开发服务器",
            },
            {
                "url": "https://api.coachai.example.com/api/v1",
                "description": "生产服务器",
            },
        ]
    
    def _get_components(self) -> Dict[str, Any]:
        """
        获取组件定义。
        
        Returns:
            组件字典
        """
        return {
            "schemas": self._get_schemas(),
            "securitySchemes": self._get_security_schemes(),
            "parameters": self._get_parameters(),
            "responses": self._get_responses(),
        }
    
    def _get_schemas(self) -> Dict[str, Any]:
        """
        获取模式定义。
        
        Returns:
            模式字典
        """
        return {
            "Error": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "example": "validation_error",
                    },
                    "message": {
                        "type": "string",
                        "example": "请求数据验证失败",
                    },
                    "details": {
                        "type": "object",
                        "additionalProperties": True,
                    },
                },
                "required": ["code", "message"],
            },
            "SuccessResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": True,
                    },
                    "message": {
                        "type": "string",
                        "example": "操作成功",
                    },
                    "data": {
                        "type": "object",
                        "additionalProperties": True,
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                    },
                },
                "required": ["success", "timestamp"],
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": False,
                    },
                    "error": {
                        "$ref": "#/components/schemas/Error",
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                    },
                },
                "required": ["success", "error", "timestamp"],
            },
        }
    
    def _get_security_schemes(self) -> Dict[str, Any]:
        """
        获取安全方案。
        
        Returns:
            安全方案字典
        """
        return {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT认证令牌",
            },
            "BasicAuth": {
                "type": "http",
                "scheme": "basic",
                "description": "基本认证",
            },
        }
    
    def _get_parameters(self) -> Dict[str, Any]:
        """
        获取参数定义。
        
        Returns:
            参数字典
        """
        return {
            "PageParameter": {
                "name": "page",
                "in": "query",
                "description": "页码",
                "required": False,
                "schema": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 1,
                },
            },
            "PageSizeParameter": {
                "name": "page_size",
                "in": "query",
                "description": "每页大小",
                "required": False,
                "schema": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20,
                },
            },
            "SortByParameter": {
                "name": "sort_by",
                "in": "query",
                "description": "排序字段",
                "required": False,
                "schema": {
                    "type": "string",
                },
            },
            "SortOrderParameter": {
                "name": "sort_order",
                "in": "query",
                "description": "排序顺序",
                "required": False,
                "schema": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "default": "desc",
                },
            },
        }
    
    def _get_responses(self) -> Dict[str, Any]:
        """
        获取响应定义。
        
        Returns:
            响应字典
        """
        return {
            "Success": {
                "description": "成功响应",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/SuccessResponse",
                        },
                    },
                },
            },
            "Error": {
                "description": "错误响应",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse",
                        },
                    },
                },
            },
            "ValidationError": {
                "description": "验证错误",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse",
                        },
                    },
                },
            },
            "NotFound": {
                "description": "资源未找到",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse",
                        },
                    },
                },
            },
            "Unauthorized": {
                "description": "未授权",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse",
                        },
                    },
                },
            },
            "Forbidden": {
                "description": "禁止访问",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse",
                        },
                    },
                },
            },
        }
    
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
        ]
    
    def add_ai_endpoints(self) -> None:
        """添加AI端点文档。"""
        self._docs["paths"]["/ai/recommendation/"] = {
            "post": {
                "tags": ["AI"],
                "summary": "获取AI推荐",
                "description": "根据用户数据和偏好生成个性化推荐",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "recommendation_type": {
                                        "type": "string",
                                        "enum": ["all", "exercise", "task", "achievement", "category"],
                                        "default": "all",
                                        "description": "推荐类型",
                                    },
                                    "max_recommendations": {
                                        "type": "integer",
                                        "minimum": 1,
                                        "maximum": 50,
                                        "default": 10,
                                        "description": "最大推荐数量",
                                    },
                                    "similarity_threshold": {
                                        "type": "number",
                                        "minimum": 0.0,
                                        "maximum": 1.0,
                                        "default": 0.6,
                                        "description": "相似度阈值",
                                    },
                                    "diversity_factor": {
                                        "type": "number",
                                        "minimum": 0.0,
                                        "maximum": 1.0,
                                        "default": 0.3,
                                        "description": "多样性因子",
                                    },
                                },
                                "required": [],
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
                                    "type": "object",
                                    "properties": {
                                        "success": {
                                            "type": "boolean",
                                            "example": True,
                                        },
                                        "user_id": {
                                            "type": "integer",
                                            "example": 1,
                                        },
                                        "username": {
                                            "type": "string",
                                            "example": "test_user",
                                        },
                                        "recommendation_type": {
                                            "type": "string",
                                            "example": "all",
                                        },
                                        "total_count": {
                                            "type": "integer",
                                            "example": 5,
                                        },
                                        "generated_at": {
                                            "type": "string",
                                            "format": "date-time",
                                        },
                                        "recommendations": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "string"},
                                                    "title": {"type": "string"},
                                                    "description": {"type": "string"},
                                                    "type": {"type": "string"},
                                                    "score": {"type": "number"},
                                                    "confidence": {"type": "number"},
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "400": {"$ref": "#/components/responses/ValidationError"},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                    "500": {"$ref": "#/components/responses/Error"},
                },
            },
        }
        
        self._docs["paths"]["/ai/analysis/"] = {
            "post": {
                "tags": ["AI"],
                "summary": "获取AI分析",
                "description": "分析用户数据，生成洞察和建议",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "analysis_type": {
                                        "type": "string",
                                        "enum": ["comprehensive", "exercise", "task", "achievement", "trend"],
                                        "default": "comprehensive",
                                        "description": "分析类型",
                                    },
                                    "period_days": {
                                        "type": "integer",
                                        "minimum": 1,
                                        "maximum": 365,
                                        "default": 30,
                                        "description": "分析周期（天）",
                                    },
                                },
                                "required": [],
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
                                    "type": "object",
                                    "properties": {
                                        "success": {
                                            "type": "boolean",
                                            "example": True,
                                        },
                                        "user_id": {
                                            "type": "integer",
                                            "example": 1,
                                        },
                                        "username": {
                                            "type": "string",
                                            "example": "test_user",
                                        },
                                        "analysis_type": {
                                            "type": "string",
                                            "example": "comprehensive",
                                        },
                                        "analysis_period_days": {
                                            "type": "integer",
                                            "example": 30,
                                        },
                                        "generated_at": {
                                            "type": "string",
                                            "format": "date-time",
                                        },
                                        "summary": {
                                            "type": "object",
                                            "properties": {
                                                "overall_score": {"type": "number"},
                                                "strengths": {"type": "array", "items": {"type": "string"}},
                                                "weaknesses": {"type": "array", "items": {"type": "string"}},
                                            },
                                        },
                                        "insights": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "type": {"type": "string"},
                                                    "title": {"type": "string"},
                                                    "description": {"type": "string"},
                                                    "priority": {"type": "string"},
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "400": {"$ref": "#/components/responses/ValidationError"},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                    "500": {"$ref": "#/components/responses/Error"},
                },
            },
        }
        
        self._docs["paths"]["/ai/prediction/"] = {
            "post": {
                "tags": ["AI"],
                "summary": "获取AI预测",
                "description": "基于用户数据和历史趋势生成预测",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "prediction_type": {
                                        "type": "string",
                                        "enum": ["all", "task", "exercise", "achievement", "trend"],
                                        "default": "all",
                                        "description": "预测类型",
                                    },
                                    "horizon_days": {
                                        "type": "integer",
                                        "minimum": 1,
                                        "maximum": 90,
                                        "default": 7,
                                        "description": "预测周期（天）",
                                    },
                                    "confidence_threshold": {
                                        "type": "number",
                                        "minimum": 0.0,
                                        "maximum": 1.0,
                                        "default": 0.7,
                                        "description": "置信度阈值",
                                    },
                                },
                                "required": [],
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
                                    "type": "object",
                                    "properties": {
                                        "success": {
                                            "type": "boolean",
                                            "example": True,
                                        },
                                        "user_id": {
                                            "type": "integer",
                                            "example": 1,
                                        },
                                        "username": {
                                            "type": "string",
                                            "example": "test_user",
                                        },
                                        "prediction_type": {
                                            "type": "string",
                                            "example": "all",
                                        },
                                        "prediction_horizon": {
                                            "type": "integer",
                                            "example": 7,
                                        },
                                        "generated_at": {
                                            "type": "string",
                                            "format": "date-time",
                                        },
                                        "predictions": {
                                            "type": "object",
                                            "additionalProperties": True,
                                        },
                                        "summary": {
                                            "type": "object",
                                            "properties": {
                                                "overall_confidence": {"type": "number"},
                                                "key_takeaways": {"type": "array", "items": {"type": "string"}},
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "400": {"$ref": "#/components/responses/ValidationError"},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                    "500": {"$ref": "#/components/responses/Error"},
                },
            },
        }
        
        self._docs["paths"]["/ai/status/"] = {
            "get": {
                "tags": ["AI"],
                "summary": "获取AI服务状态",
                "description": "获取AI服务的状态和配置信息",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "状态获取成功",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {
                                            "type": "boolean",
                                            "example": True,
                                        },
                                        "timestamp": {
                                            "type": "string",
                                            "format": "date-time",
                                        },
                                        "status": {
                                            "type": "object",
                                            "properties": {
                                                "initialized": {"type": "boolean"},
                                                "total_services": {"type": "integer"},
                                                "services": {"type": "object"},
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                    "500": {"$ref": "#/components/responses/Error"},
                },
            },
        }
    
    def add_system_endpoints(self) -> None:
        """添加系统端点文档。"""
        self._docs["paths"]["/health/"] = {
            "get": {
                "tags": ["System"],
                "summary": "健康检查",
                "description": "检查系统健康状态",
                "responses": {
                    "200": {
                        "description": "系统健康",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success
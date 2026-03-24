"""
API文档视图。
按照豆包AI助手最佳实践：提供类型安全的API文档视图。
"""
from __future__ import annotations

import json
from typing import Any, Dict

from django.http import HttpRequest, JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


# ==================== API文档视图 ====================
class APIDocumentationView(APIView):
    """
    API文档视图。
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request: HttpRequest) -> Response:
        """
        获取OpenAPI规范文档。
        
        Args:
            request: HTTP请求
            
        Returns:
            HTTP响应
        """
        try:
            # 生成OpenAPI规范
            openapi_spec = self._generate_openapi_spec()
            
            return Response(openapi_spec)
            
        except Exception as e:
            return Response(
                {
                    "error": "生成API文档失败",
                    "details": str(e),
                },
                status=500,
            )
    
    def _generate_openapi_spec(self) -> Dict[str, Any]:
        """
        生成OpenAPI规范。
        
        Returns:
            OpenAPI规范字典
        """
        return {
            "openapi": "3.0.0",
            "info": {
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
            },
            "servers": [
                {
                    "url": "http://localhost:8000/api/v1",
                    "description": "开发服务器",
                },
                {
                    "url": "https://api.coachai.example.com/api/v1",
                    "description": "生产服务器",
                },
            ],
            "tags": [
                {
                    "name": "AI",
                    "description": "人工智能服务",
                },
                {
                    "name": "System",
                    "description": "系统管理",
                },
            ],
            "paths": self._get_paths(),
            "components": self._get_components(),
        }
    
    def _get_paths(self) -> Dict[str, Any]:
        """
        获取API路径定义。
        
        Returns:
            路径字典
        """
        return {
            "/ai/recommendation/": {
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
                                        },
                                        "max_recommendations": {
                                            "type": "integer",
                                            "minimum": 1,
                                            "maximum": 50,
                                            "default": 10,
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
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "user_id": {"type": "integer"},
                                            "recommendation_type": {"type": "string"},
                                            "total_count": {"type": "integer"},
                                            "recommendations": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "string"},
                                                        "title": {"type": "string"},
                                                        "type": {"type": "string"},
                                                        "score": {"type": "number"},
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
            },
            "/ai/analysis/": {
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
                                        },
                                        "period_days": {
                                            "type": "integer",
                                            "minimum": 1,
                                            "maximum": 365,
                                            "default": 30,
                                        },
                                    },
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
                                            "success": {"type": "boolean"},
                                            "user_id": {"type": "integer"},
                                            "analysis_type": {"type": "string"},
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
            },
            "/ai/prediction/": {
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
                                        },
                                        "horizon_days": {
                                            "type": "integer",
                                            "minimum": 1,
                                            "maximum": 90,
                                            "default": 7,
                                        },
                                    },
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
                                            "success": {"type": "boolean"},
                                            "user_id": {"type": "integer"},
                                            "prediction_type": {"type": "string"},
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
            },
            "/ai/status/": {
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
                                            "success": {"type": "boolean"},
                                            "timestamp": {"type": "string", "format": "date-time"},
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
            },
            "/health/": {
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
                                            "success": {"type": "boolean"},
                                            "status": {"type": "string"},
                                            "timestamp": {"type": "string", "format": "date-time"},
                                            "services": {
                                                "type": "object",
                                                "additionalProperties": {
                                                    "type": "string",
                                                },
                                            },
                                        },
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
            },
            "/status/": {
                "get": {
                    "tags": ["System"],
                    "summary": "系统状态",
                    "description": "获取系统状态信息",
                    "responses": {
                        "200": {
                            "description": "状态获取成功",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "timestamp": {"type": "string", "format": "date-time"},
                                            "system": {
                                                "type": "object",
                                                "properties": {
                                                    "platform": {"type": "string"},
                                                    "python_version": {"type": "string"},
                                                    "django_version": {"type": "string"},
                                                },
                                            },
                                            "application": {
                                                "type": "object",
                                                "properties": {
                                                    "debug": {"type": "boolean"},
                                                    "installed_apps_count": {"type": "integer"},
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                        "500": {"$ref": "#/components/responses/Error"},
                    },
                },
            },
            "/info/": {
                "get": {
                    "tags": ["System"],
                    "summary": "API信息",
                    "description": "获取API信息和端点列表",
                    "responses": {
                        "200": {
                            "description": "信息获取成功",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "timestamp": {"type": "string", "format": "date-time"},
                                            "api": {
                                                "type": "object",
                                                "properties": {
                                                    "version": {"type": "string"},
                                                    "name": {"type": "string"},
                                                    "description": {"type": "string"},
                                                    "base_url": {"type": "string"},
                                                },
                                            },
                                            "endpoints": {
                                                "type": "object",
                                                "additionalProperties": True,
                                            },
                                        },
                                    },
                                },
                            },
                        },
                        "500": {"$ref": "#/components/responses/Error"},
                    },
                },
            },
        }
    
    def _get_components(self) -> Dict[str, Any]:
        """
        获取组件定义。
        
        Returns:
            组件字典
        """
        return {
            "schemas": {
                "Error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "message": {"type": "string"},
                        "details": {"type": "object", "additionalProperties": True},
                    },
                    "required": ["code", "message"],
                },
                "SuccessResponse": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "message": {"type": "string"},
                        "data": {"type": "object", "additionalProperties": True},
                        "timestamp": {"type": "string", "format": "date-time"},
                    },
                    "required": ["success", "timestamp"],
                },
                "ErrorResponse": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "error": {"$ref": "#/components/schemas/Error"},
                        "timestamp": {"type": "string", "format": "date-time"},
                    },
                    "required": ["success", "error", "timestamp"],
                },
            },
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                },
            },
            "responses": {
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
            },
        }


# ==================== API文档HTML视图 ====================
class APIDocumentationHTMLView(APIView):
    """
    API文档HTML视图。
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request: HttpRequest) -> Response:
        """
        获取API文档HTML页面。
        
        Args:
            request: HTTP请求
            
        Returns:
            HTTP响应
        """
        html_content = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CoachAI API 文档</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                
                header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 2rem;
                    border-radius: 10px;
                    margin-bottom: 2rem;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                
                h1 {
                    margin: 0;
                    font-size: 2.5rem;
                }
                
                .subtitle {
                    font-size: 1.2rem;
                    opacity: 0.9;
                    margin-top: 0.5rem;
                }
                
                .container {
                    display: grid;
                    grid-template-columns: 300px 1fr;
                    gap: 2rem;
                }
                
                .sidebar {
                    background: white;
                    padding: 1.5rem;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    height: fit-content;
                }
                
                .nav-list {
                    list-style: none;
                    padding: 0;
                    margin: 0;
                }
                
                .nav-item {
                    margin-bottom: 0.5rem;
                }
                
                .nav-link {
                    display: block;
                    padding: 0.75rem 1rem;
                    color: #333;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: all 0.3s ease;
                }
                
                .nav-link:hover {
                    background-color: #f0f0f0;
                    color: #667eea;
                }
                
                .nav-link.active {
                    background-color: #667eea;
                    color: white;
                }
                
                .content {
                    background: white;
                    padding: 2rem;
                    border-radius
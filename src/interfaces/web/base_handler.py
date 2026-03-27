"""
基础Handler模块（DDD迁移版）
定义所有Handler的基类
"""

import json
from typing import Any, Dict, Optional, Union
from tornado.web import RequestHandler
from loguru import logger

from src.interfaces.api.middleware.exceptions import (
    BadRequestError, UnauthorizedError, ForbiddenError,
    NotFoundError, ValidationError, InternalServerError
)


class BaseHandler(RequestHandler):
    """基础Handler类，所有自定义Handler应继承此类"""
    
    def initialize(self) -> None:
        """初始化Handler"""
        super().initialize()
    
    def set_default_headers(self) -> None:
        """设置默认响应头"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.set_header("Access-Control-Allow-Credentials", "true")
    
    def options(self, *args, **kwargs) -> None:
        """处理OPTIONS请求（CORS预检）"""
        self.set_status(204)
        self.finish()
    
    def get_json_body(self) -> Dict[str, Any]:
        """
        获取JSON请求体
        
        Returns:
            JSON解析后的字典
            
        Raises:
            BadRequestError: JSON解析失败
        """
        try:
            if not self.request.body:
                return {}
            
            body = self.request.body.decode('utf-8')
            if not body.strip():
                return {}
            
            return json.loads(body)
        except json.JSONDecodeError as e:
            raise BadRequestError(f"Invalid JSON: {str(e)}")
        except UnicodeDecodeError as e:
            raise BadRequestError(f"Invalid encoding: {str(e)}")
    
    def get_query_params(self) -> Dict[str, Any]:
        """
        获取查询参数
        
        Returns:
            查询参数字典
        """
        params = {}
        for key in self.request.arguments:
            values = self.get_arguments(key)
            if len(values) == 1:
                params[key] = values[0]
            else:
                params[key] = values
        return params
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        获取当前用户
        
        Returns:
            当前用户信息字典，如果未认证则返回None
        """
        # 从请求头获取认证信息
        auth_header = self.request.headers.get("Authorization")
        if not auth_header:
            return None
        
        # 这里应该验证JWT令牌并返回用户信息
        # 暂时返回模拟数据
        return {
            'id': 'user_123',
            'username': 'test_user',
            'email': 'test@example.com',
            'tenant_id': 'tenant_123',
            'roles': ['user']
        }
    
    def write_json(self, data: Dict[str, Any], status_code: int = 200) -> None:
        """
        写入JSON响应
        
        Args:
            data: 响应数据
            status_code: HTTP状态码
        """
        self.set_status(status_code)
        response = {
            'success': status_code < 400,
            'data': data,
            'timestamp': self.request.request_time()
        }
        self.write(response)
    
    def write_error(self, status_code: int, **kwargs: Any) -> None:
        """
        统一错误处理
        
        Args:
            status_code: HTTP状态码
            **kwargs: 额外参数
        """
        exc_info = kwargs.get('exc_info')
        
        if exc_info:
            exc_type, exc_value, exc_traceback = exc_info
            
            # 处理自定义异常
            if isinstance(exc_value, (BadRequestError, UnauthorizedError, ForbiddenError,
                                     NotFoundError, ValidationError, InternalServerError)):
                error_data = {
                    'code': exc_value.code,
                    'message': str(exc_value),
                    'details': getattr(exc_value, 'details', None)
                }
            else:
                # 处理其他异常
                error_data = {
                    'code': f'HTTP_{status_code}',
                    'message': str(exc_value) if str(exc_value) else self._reason,
                    'details': None
                }
        else:
            # 没有异常信息
            error_data = {
                'code': f'HTTP_{status_code}',
                'message': self._reason or 'Unknown error',
                'details': None
            }
        
        self.set_status(status_code)
        self.write({
            'success': False,
            'error': error_data,
            'timestamp': self.request.request_time()
        })
    
    def validate_request(self, schema: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        验证请求数据
        
        Args:
            schema: 验证模式（暂时简化）
            data: 要验证的数据，如果为None则使用请求体
            
        Returns:
            验证后的数据
            
        Raises:
            ValidationError: 验证失败
        """
        request_data = data or self.get_json_body()
        
        # 这里应该实现完整的验证逻辑
        # 暂时只做基本检查
        if schema:
            # 简化验证：检查必填字段
            for field, field_schema in schema.items():
                if field_schema.get('required', False) and field not in request_data:
                    raise ValidationError(f"Field '{field}' is required")
        
        return request_data
    
    def paginate(self, items: list, page: int, limit: int, total: int) -> Dict[str, Any]:
        """
        生成分页响应
        
        Args:
            items: 当前页的项目列表
            page: 当前页码
            limit: 每页数量
            total: 总项目数
            
        Returns:
            分页响应数据
        """
        return {
            'items': items,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit if limit > 0 else 0,
                'has_next': page * limit < total,
                'has_prev': page > 1
            }
        }
    
    def log_request(self) -> None:
        """记录请求日志"""
        try:
            method = self.request.method
            uri = self.request.uri
            remote_ip = self.request.remote_ip
            user_agent = self.request.headers.get('User-Agent', 'Unknown')
            user_id = self.current_user.get('id') if self.current_user else 'anonymous'
            
            logger.info(f"[{method}] {uri} - IP: {remote_ip} - User: {user_id} - UA: {user_agent[:50]}")
            
            # 记录慢请求
            request_time = self.request.request_time()
            if request_time > 1.0:  # 超过1秒的请求
                logger.warning(f"Slow request: {method} {uri} took {request_time:.2f}s")
                
        except Exception as e:
            logger.error(f"Failed to log request: {e}")
    
    def on_finish(self) -> None:
        """请求完成时调用"""
        super().on_finish()
        
        # 记录请求完成
        try:
            method = self.request.method
            uri = self.request.uri
            status = self.get_status()
            request_time = self.request.request_time()
            
            if status >= 400:
                logger.warning(f"[{method}] {uri} - Status: {status} - Time: {request_time:.3f}s")
            else:
                logger.debug(f"[{method}] {uri} - Status: {status} - Time: {request_time:.3f}s")
                
        except Exception as e:
            logger.error(f"Failed to log request finish: {e}")
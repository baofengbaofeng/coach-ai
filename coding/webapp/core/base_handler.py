"""
基础Handler模块
定义所有Handler的基类
"""

import json
from typing import Any, Dict, Optional
from tornado.web import RequestHandler

from .error_handler import ErrorHandler
from .middleware import MiddlewareManager


class BaseHandler(MiddlewareManager.wrap_handler(RequestHandler)):
    """基础Handler类，所有自定义Handler应继承此类"""
    
    def initialize(self) -> None:
        """初始化Handler"""
        super().initialize()
    
    def write_error(self, status_code: int, **kwargs: Any) -> None:
        """
        统一错误处理
        
        Args:
            status_code: HTTP状态码
            **kwargs: 额外参数
        """
        ErrorHandler.write_error(self, status_code, **kwargs)
    
    def log_exception(self, exc_info: tuple) -> None:
        """
        记录异常日志
        
        Args:
            exc_info: 异常信息
        """
        ErrorHandler.log_exception(self, exc_info)
    
    def success(self, data: Any = None, message: str = "Success") -> None:
        """
        成功响应
        
        Args:
            data: 响应数据
            message: 成功消息
        """
        response = {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": self.request.request_time()
        }
        self.write(response)
    
    def error(self, error_code: str, message: str, status_code: int = 400, details: Dict[str, Any] = None) -> None:
        """
        错误响应
        
        Args:
            error_code: 错误代码
            message: 错误消息（英文）
            status_code: HTTP状态码
            details: 错误详情
        """
        self.set_status(status_code)
        response = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "details": details or {}
            },
            "timestamp": self.request.request_time()
        }
        self.write(response)
    
    def get_json_body(self) -> Dict[str, Any]:
        """
        获取JSON请求体
        
        Returns:
            JSON请求体字典
        """
        return getattr(self.request, "json", {})
    
    def get_tenant_id(self) -> str:
        """
        获取租户ID
        
        Returns:
            租户ID字符串
        """
        return getattr(self.request, "tenant_id", "default")
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        获取当前用户（需在子类中实现）
        
        Returns:
            用户信息字典或None
        """
        # 默认实现，子类应重写此方法
        return None
    
    def get_pagination_params(self) -> Dict[str, int]:
        """
        获取分页参数
        
        Returns:
            包含page和limit的字典
        """
        try:
            page = int(self.get_argument("page", "1"))
            limit = int(self.get_argument("limit", "20"))
            
            # 限制分页参数范围
            page = max(1, page)
            limit = max(1, min(limit, 100))  # 限制每页最多100条
            
            return {"page": page, "limit": limit}
        except ValueError:
            return {"page": 1, "limit": 20}
    
    def get_sort_params(self) -> Dict[str, str]:
        """
        获取排序参数
        
        Returns:
            包含sort_field和sort_order的字典
        """
        sort_field = self.get_argument("sort", "id")
        sort_order = self.get_argument("order", "asc").lower()
        
        # 验证排序方向
        if sort_order not in ["asc", "desc"]:
            sort_order = "asc"
        
        return {"sort_field": sort_field, "sort_order": sort_order}
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: list) -> bool:
        """
        验证必需字段
        
        Args:
            data: 数据字典
            required_fields: 必需字段列表
            
        Returns:
            验证是否通过
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(field)
        
        if missing_fields:
            self.error(
                error_code="VALIDATION_ERROR",
                message=f"Missing required fields: {', '.join(missing_fields)}",
                status_code=400
            )
            return False
        
        return True
    
    def validate_field_types(self, data: Dict[str, Any], field_types: Dict[str, type]) -> bool:
        """
        验证字段类型
        
        Args:
            data: 数据字典
            field_types: 字段类型映射
            
        Returns:
            验证是否通过
        """
        type_errors = []
        
        for field, expected_type in field_types.items():
            if field in data and data[field] is not None:
                if not isinstance(data[field], expected_type):
                    type_errors.append(f"{field} should be {expected_type.__name__}")
        
        if type_errors:
            self.error(
                error_code="VALIDATION_ERROR",
                message=f"Type errors: {', '.join(type_errors)}",
                status_code=400
            )
            return False
        
        return True
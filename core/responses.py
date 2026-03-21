"""
统一API响应格式模块，提供标准化的成功和错误响应构建器，确保所有API接口返回一致的响应格式。
按照豆包AI助手最佳实践和coding-style.md规范实现。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union

from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from core.constants import HttpStatus


# ==================== 日志记录器 ====================
# 模块级别的日志记录器，用于记录响应构建信息和调试信息，遵循coding-style.md规范
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 基础响应构建器 ====================
class APIResponseBuilder:
    """
    API响应构建器基类，提供统一的响应格式构建方法和工具函数，确保所有API接口返回一致的响应结构。
    """
    
    def __init__(
        self,
        success: bool = True,
        data: Optional[Union[Dict[str, Any], List[Any]]] = None,
        error: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        初始化API响应构建器实例。
        """
        self.success: bool = success
        self.data: Optional[Union[Dict[str, Any], List[Any]]] = data
        self.error: Optional[Dict[str, Any]] = error
        self.message: Optional[str] = message
        self.meta: Optional[Dict[str, Any]] = meta
        
        self._validate_response_data()
    
    def _validate_response_data(self) -> None:
        """
        验证响应数据的有效性。
        """
        if self.success and self.error:
            raise ValueError("成功响应不能包含错误信息")
        if not self.success and not self.error:
            raise ValueError("错误响应必须包含错误信息")
    
    def build(self) -> Dict[str, Any]:
        """
        构建标准化的API响应字典。
        """
        response_dict: Dict[str, Any] = {
            "success": self.success,
            "timestamp": self._get_timestamp(),
        }
        
        if self.success:
            if self.data is not None:
                response_dict["data"] = self.data
            if self.message:
                response_dict["message"] = self.message
        else:
            if self.error:
                response_dict["error"] = self.error
            if self.message:
                response_dict["message"] = self.message
        
        if self.meta:
            response_dict["meta"] = self.meta
        
        return response_dict
    
    def _get_timestamp(self) -> str:
        """
        获取当前时间戳。
        """
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


# ==================== 成功响应构建器 ====================
class SuccessResponseBuilder(APIResponseBuilder):
    """
    成功响应构建器。
    """
    
    def __init__(
        self,
        data: Optional[Union[Dict[str, Any], List[Any]]] = None,
        message: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        status_code: int = HTTP_200_OK,
    ) -> None:
        """
        初始化成功响应构建器实例。
        """
        super().__init__(success=True, data=data, message=message, meta=meta)
        self.status_code: int = status_code
    
    def to_json_response(self) -> JsonResponse:
        """
        将成功响应构建为Django JsonResponse对象。
        """
        response_data: Dict[str, Any] = self.build()
        return JsonResponse(response_data, status=self.status_code)
    
    def to_drf_response(self) -> Response:
        """
        将成功响应构建为DRF Response对象。
        """
        response_data: Dict[str, Any] = self.build()
        return Response(response_data, status=self.status_code)


# ==================== 错误响应构建器 ====================
class ErrorResponseBuilder(APIResponseBuilder):
    """
    错误响应构建器。
    """
    
    def __init__(
        self,
        error_code: str,
        error_message: str,
        error_details: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        status_code: int = HttpStatus.BAD_REQUEST,
    ) -> None:
        """
        初始化错误响应构建器实例。
        """
        error_dict: Dict[str, Any] = {
            "code": error_code,
            "message": error_message,
        }
        
        if error_details:
            error_dict["details"] = error_details
        
        super().__init__(success=False, error=error_dict, message=message)
        self.status_code: int = status_code
    
    def to_json_response(self) -> JsonResponse:
        """
        将错误响应构建为Django JsonResponse对象。
        """
        response_data: Dict[str, Any] = self.build()
        return JsonResponse(response_data, status=self.status_code)
    
    def to_drf_response(self) -> Response:
        """
        将错误响应构建为DRF Response对象。
        """
        response_data: Dict[str, Any] = self.build()
        return Response(response_data, status=self.status_code)


# ==================== 便捷响应函数 ====================
def success_response(
    data: Optional[Union[Dict[str, Any], List[Any]]] = None,
    message: Optional[str] = None,
    status_code: int = HTTP_200_OK,
) -> JsonResponse:
    """
    构建成功响应的便捷函数。
    """
    builder: SuccessResponseBuilder = SuccessResponseBuilder(
        data=data,
        message=message,
        status_code=status_code,
    )
    return builder.to_json_response()


def created_response(
    data: Optional[Union[Dict[str, Any], List[Any]]] = None,
    message: Optional[str] = None,
) -> JsonResponse:
    """
    构建创建成功的响应函数。
    """
    return success_response(data=data, message=message, status_code=HTTP_201_CREATED)


def no_content_response(message: Optional[str] = None) -> JsonResponse:
    """
    构建无内容响应函数。
    """
    return success_response(data=None, message=message, status_code=HTTP_204_NO_CONTENT)


def error_response(
    error_code: str,
    error_message: str,
    error_details: Optional[Dict[str, Any]] = None,
    message: Optional[str] = None,
    status_code: int = HttpStatus.BAD_REQUEST,
) -> JsonResponse:
    """
    构建错误响应的便捷函数。
    """
    builder: ErrorResponseBuilder = ErrorResponseBuilder(
        error_code=error_code,
        error_message=error_message,
        error_details=error_details,
        message=message,
        status_code=status_code,
    )
    return builder.to_json_response()


def validation_error_response(
    errors: Dict[str, List[str]],
    message: Optional[str] = None,
) -> JsonResponse:
    """
    构建验证错误响应函数。
    """
    return error_response(
        error_code="VALIDATION_ERROR",
        error_message="请求参数验证失败",
        error_details={"errors": errors},
        message=message,
        status_code=HttpStatus.UNPROCESSABLE_ENTITY,
    )


def not_found_response(
    resource_type: str,
    resource_id: Optional[Union[int, str]] = None,
    message: Optional[str] = None,
) -> JsonResponse:
    """
    构建资源未找到响应函数。
    """
    error_details: Dict[str, Any] = {"resource_type": resource_type}
    if resource_id is not None:
        error_details["resource_id"] = resource_id
    
    return error_response(
        error_code="RESOURCE_NOT_FOUND",
        error_message=f"{resource_type}资源不存在",
        error_details=error_details,
        message=message,
        status_code=HttpStatus.NOT_FOUND,
    )


def unauthorized_response(
    reason: Optional[str] = None,
    message: Optional[str] = None,
) -> JsonResponse:
    """
    构建未授权响应函数。
    """
    error_details: Dict[str, Any] = {}
    if reason:
        error_details["reason"] = reason
    
    return error_response(
        error_code="UNAUTHORIZED",
        error_message="未授权访问，请先登录",
        error_details=error_details,
        message=message,
        status_code=HttpStatus.UNAUTHORIZED,
    )


def forbidden_response(
    reason: Optional[str] = None,
    message: Optional[str] = None,
) -> JsonResponse:
    """
    构建禁止访问响应函数。
    """
    error_details: Dict[str, Any] = {}
    if reason:
        error_details["reason"] = reason
    
    return error_response(
        error_code="FORBIDDEN",
        error_message="权限不足，无法访问该资源",
        error_details=error_details,
        message=message,
        status_code=HttpStatus.FORBIDDEN,
    )


# ==================== 分页响应构建器 ====================
class PaginatedResponseBuilder(SuccessResponseBuilder):
    """
    分页响应构建器。
    """
    
    def __init__(
        self,
        data: List[Any],
        total_count: int,
        page: int,
        page_size: int,
        message: Optional[str] = None,
    ) -> None:
        """
        初始化分页响应构建器实例。
        """
        total_pages: int = (total_count + page_size - 1) // page_size if page_size > 0 else 0
        
        meta: Dict[str, Any] = {
            "pagination": {
                "total": total_count,
                "count": len(data),
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            }
        }
        
        super().__init__(data=data, message=message, meta=meta)


def paginated_response(
    data: List[Any],
    total_count: int,
    page: int,
    page_size: int,
    message: Optional[str] = None,
) -> JsonResponse:
    """
    构建分页响应的便捷函数。
    """
    builder: PaginatedResponseBuilder = PaginatedResponseBuilder(
        data=data,
        total_count=total_count,
        page=page,
        page_size=page_size,
        message=message,
    )
    return builder.to_json_response()


# ==================== 导出定义 ====================
__all__: list[str] = [
    "APIResponseBuilder",
    "SuccessResponseBuilder",
    "ErrorResponseBuilder",
    "PaginatedResponseBuilder",
    "success_response",
    "created_response",
    "no_content_response",
    "error_response",
    "validation_error_response",
    "not_found_response",
    "unauthorized_response",
    "forbidden_response",
    "paginated_response",
]
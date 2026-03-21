"""
全局异常处理模块，定义项目级别的自定义异常类和异常处理逻辑，确保统一的错误响应格式。
按照豆包AI助手最佳实践和coding-style.md规范实现。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpRequest
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

from core.constants import ErrorMessages, HttpStatus


# ==================== 日志记录器 ====================
# 模块级别的日志记录器，用于记录异常信息和调试信息，遵循coding-style.md规范
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 基础异常类 ====================
class CoachAIBaseException(APIException):
    """
    CoachAI 项目基础异常类，所有自定义异常的基类，提供统一的异常处理接口和错误信息格式。
    
    Attributes:
        status_code (int): HTTP 状态码，默认为 500 内部服务器错误
        default_detail (str): 默认错误描述信息，用于客户端显示
        default_code (str): 默认错误代码，用于程序内部识别异常类型
        extra_data (Optional[Dict[str, Any]]): 额外的错误数据，用于提供更详细的错误上下文
    """
    
    def __init__(
        self,
        detail: Optional[str] = None,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        初始化基础异常类实例，设置异常的各种属性和上下文信息。
        
        Args:
            detail (Optional[str]): 错误描述信息，如果为 None 则使用默认描述
            code (Optional[str]): 错误代码，如果为 None 则使用默认代码
            status_code (Optional[int]): HTTP 状态码，如果为 None 则使用默认状态码
            extra_data (Optional[Dict[str, Any]]): 额外的错误数据字典，用于提供错误上下文
            
        Returns:
            None: 此方法不返回值，但会初始化异常实例的各种属性
        """
        self.status_code: int = status_code or self.status_code
        self.default_detail: str = detail or self.default_detail
        self.default_code: str = code or self.default_code
        self.extra_data: Dict[str, Any] = extra_data or {}
        
        super().__init__(detail=self.default_detail, code=self.default_code)
        
        # 记录异常信息到日志，便于问题追踪和调试
        _LOGGER.error(
            "异常发生: %s (代码: %s, 状态码: %d, 额外数据: %s)",
            self.default_detail,
            self.default_code,
            self.status_code,
            self.extra_data,
        )


# ==================== 业务异常类 ====================
class BusinessValidationError(CoachAIBaseException):
    """
    业务验证异常类，用于处理业务逻辑验证失败的情况，如参数校验、数据一致性检查等。
    
    Examples:
        >>> raise BusinessValidationError("用户年龄必须大于0", code="INVALID_AGE")
    """
    
    status_code: int = HttpStatus.BAD_REQUEST
    default_detail: str = ErrorMessages.VALIDATION_ERROR
    default_code: str = "VALIDATION_ERROR"


class ResourceNotFoundException(CoachAIBaseException):
    """
    资源未找到异常类，用于处理请求的资源不存在的情况，如用户、作业、任务等资源查找失败。
    
    Examples:
        >>> raise ResourceNotFoundException("用户不存在", code="USER_NOT_FOUND")
    """
    
    status_code: int = HttpStatus.NOT_FOUND
    default_detail: str = ErrorMessages.NOT_FOUND
    default_code: str = "RESOURCE_NOT_FOUND"


class AuthenticationFailedException(CoachAIBaseException):
    """
    认证失败异常类，用于处理用户认证失败的情况，如无效的令牌、过期的会话等。
    
    Examples:
        >>> raise AuthenticationFailedException("无效的访问令牌", code="INVALID_TOKEN")
    """
    
    status_code: int = HttpStatus.UNAUTHORIZED
    default_detail: str = ErrorMessages.UNAUTHORIZED
    default_code: str = "AUTHENTICATION_FAILED"


class PermissionDeniedException(CoachAIBaseException):
    """
    权限拒绝异常类，用于处理用户权限不足的情况，如访问未授权的资源、执行未授权的操作等。
    
    Examples:
        >>> raise PermissionDeniedException("权限不足，无法访问该资源", code="INSUFFICIENT_PERMISSIONS")
    """
    
    status_code: int = HttpStatus.FORBIDDEN
    default_detail: str = ErrorMessages.FORBIDDEN
    default_code: str = "PERMISSION_DENIED"


class ServiceUnavailableException(CoachAIBaseException):
    """
    服务不可用异常类，用于处理依赖服务不可用的情况，如数据库连接失败、第三方API服务异常等。
    
    Examples:
        >>> raise ServiceUnavailableException("数据库服务暂时不可用", code="DATABASE_UNAVAILABLE")
    """
    
    status_code: int = HttpStatus.SERVICE_UNAVAILABLE
    default_detail: str = ErrorMessages.INTERNAL_SERVER_ERROR
    default_code: str = "SERVICE_UNAVAILABLE"


class RateLimitExceededException(CoachAIBaseException):
    """
    速率限制异常类，用于处理用户请求频率超过限制的情况，防止恶意请求和资源滥用。
    
    Examples:
        >>> raise RateLimitExceededException("请求过于频繁，请稍后重试", code="RATE_LIMIT_EXCEEDED")
    """
    
    status_code: int = HttpStatus.TOO_MANY_REQUESTS
    default_detail: str = "请求过于频繁，请稍后重试"
    default_code: str = "RATE_LIMIT_EXCEEDED"


# ==================== AI 服务异常类 ====================
class OCRProcessingException(CoachAIBaseException):
    """
    OCR 处理异常类，用于处理作业图片OCR识别失败的情况，如图片质量差、文字识别错误等。
    
    Examples:
        >>> raise OCRProcessingException("OCR识别失败，请检查图片质量", code="OCR_PROCESSING_FAILED")
    """
    
    status_code: int = HttpStatus.INTERNAL_SERVER_ERROR
    default_detail: str = ErrorMessages.OCR_PROCESSING_FAILED
    default_code: str = "OCR_PROCESSING_FAILED"


class ActionRecognitionException(CoachAIBaseException):
    """
    动作识别异常类，用于处理运动动作识别失败的情况，如视频质量差、动作识别错误等。
    
    Examples:
        >>> raise ActionRecognitionException("动作识别失败，请检查视频质量", code="ACTION_RECOGNITION_FAILED")
    """
    
    status_code: int = HttpStatus.INTERNAL_SERVER_ERROR
    default_detail: str = ErrorMessages.ACTION_RECOGNITION_FAILED
    default_code: str = "ACTION_RECOGNITION_FAILED"


class SpeechRecognitionException(CoachAIBaseException):
    """
    语音识别异常类，用于处理语音识别失败的情况，如音频质量差、语音识别错误等。
    
    Examples:
        >>> raise SpeechRecognitionException("语音识别失败，请检查音频质量", code="SPEECH_RECOGNITION_FAILED")
    """
    
    status_code: int = HttpStatus.INTERNAL_SERVER_ERROR
    default_detail: str = ErrorMessages.SPEECH_RECOGNITION_FAILED
    default_code: str = "SPEECH_RECOGNITION_FAILED"


# ==================== 文件处理异常类 ====================
class FileUploadException(CoachAIBaseException):
    """
    文件上传异常类，用于处理文件上传失败的情况，如文件大小超限、文件类型不支持等。
    
    Examples:
        >>> raise FileUploadException("文件大小超过限制", code="FILE_TOO_LARGE")
    """
    
    status_code: int = HttpStatus.BAD_REQUEST
    default_detail: str = ErrorMessages.FILE_UPLOAD_FAILED
    default_code: str = "FILE_UPLOAD_FAILED"


class InvalidFileTypeException(CoachAIBaseException):
    """
    无效文件类型异常类，用于处理不支持的文件类型上传情况。
    
    Examples:
        >>> raise InvalidFileTypeException("不支持的文件类型", code="INVALID_FILE_TYPE")
    """
    
    status_code: int = HttpStatus.BAD_REQUEST
    default_detail: str = ErrorMessages.INVALID_FILE_TYPE
    default_code: str = "INVALID_FILE_TYPE"


class FileTooLargeException(CoachAIBaseException):
    """
    文件过大异常类，用于处理文件大小超过限制的情况。
    
    Examples:
        >>> raise FileTooLargeException("文件大小超过10MB限制", code="FILE_TOO_LARGE")
    """
    
    status_code: int = HttpStatus.BAD_REQUEST
    default_detail: str = ErrorMessages.FILE_TOO_LARGE
    default_code: str = "FILE_TOO_LARGE"


# ==================== 异常处理器 ====================
def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Optional[Response]:
    """
    自定义异常处理器，统一处理所有异常并返回标准化的错误响应格式。
    
    Args:
        exc (Exception): 捕获到的异常对象，可能是系统异常或自定义业务异常
        context (Dict[str, Any]): 异常发生的上下文信息，包含请求对象、视图函数等
        
    Returns:
        Optional[Response]: 标准化的错误响应对象，包含错误代码、描述和详细信息
        
    Raises:
        此函数本身不抛出异常，但会处理传入的异常并返回适当的响应
    """
    # 调用 DRF 默认异常处理器获取基础响应
    response: Optional[Response] = exception_handler(exc, context)
    
    # 如果 DRF 无法处理该异常，则使用自定义处理逻辑
    if response is None:
        return handle_unhandled_exception(exc, context)
    
    # 自定义响应数据格式
    response.data = {
        "success": False,
        "error": {
            "code": getattr(exc, "default_code", "UNKNOWN_ERROR"),
            "message": str(exc.detail) if hasattr(exc, "detail") else str(exc),
            "details": getattr(exc, "extra_data", {}),
        },
        "timestamp": context.get("timestamp", ""),
        "path": str(context.get("request").path) if context.get("request") else "",
    }
    
    return response


def handle_unhandled_exception(exc: Exception, context: Dict[str, Any]) -> Response:
    """
    处理未捕获的异常，确保所有异常都有统一的响应格式。
    
    Args:
        exc (Exception): 未捕获的异常对象
        context (Dict[str, Any]): 异常发生的上下文信息
        
    Returns:
        Response: 标准化的错误响应对象，包含通用的错误信息
        
    Raises:
        此函数本身不抛出异常，但会处理传入的异常并返回适当的响应
    """
    request: Optional[HttpRequest] = context.get("request")
    
    # 记录未捕获异常的详细信息，便于问题排查
    _LOGGER.exception(
        "未捕获的异常: %s, 路径: %s, 方法: %s",
        str(exc),
        request.path if request else "unknown",
        request.method if request else "unknown",
    )
    
    # 根据异常类型确定状态码和错误信息
    if isinstance(exc, PermissionDenied):
        status_code: int = HttpStatus.FORBIDDEN
        error_message: str = ErrorMessages.FORBIDDEN
        error_code: str = "PERMISSION_DENIED"
    elif isinstance(exc, ValidationError):
        status_code = HttpStatus.BAD_REQUEST
        error_message = ErrorMessages.VALIDATION_ERROR
        error_code = "VALIDATION_ERROR"
    else:
        status_code = HttpStatus.INTERNAL_SERVER_ERROR
        error_message = ErrorMessages.INTERNAL_SERVER_ERROR
        error_code = "INTERNAL_SERVER_ERROR"
    
    # 构建标准化错误响应
    response_data: Dict[str, Any] = {
        "success": False,
        "error": {
            "code": error_code,
            "message": error_message,
            "details": {"original_error": str(exc)} if str(exc) else {},
        },
        "timestamp": context.get("timestamp", ""),
        "path": str(request.path) if request else "",
    }
    
    return Response(response_data, status=status_code)


# ==================== 导出定义 ====================
__all__: list[str] = [
    "CoachAIBaseException",
    "BusinessValidationError",
    "ResourceNotFoundException",
    "AuthenticationFailedException",
    "PermissionDeniedException",
    "ServiceUnavailableException",
    "RateLimitExceededException",
    "OCRProcessingException",
    "ActionRecognitionException",
    "SpeechRecognitionException",
    "FileUploadException",
    "InvalidFileTypeException",
    "FileTooLargeException",
    "custom_exception_handler",
    "handle_unhandled_exception",
]

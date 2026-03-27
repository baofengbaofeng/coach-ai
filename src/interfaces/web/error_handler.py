"""
错误处理器模块（DDD迁移版）
统一错误处理和异常管理
"""

import traceback
from typing import Any, Dict
from tornado.web import RequestHandler
from loguru import logger

from src.interfaces.api.middleware.exceptions import (
    BadRequestError, UnauthorizedError, ForbiddenError,
    NotFoundError, ValidationError, InternalServerError
)


class ErrorHandler:
    """错误处理器"""
    
    @staticmethod
    def write_error(handler: RequestHandler, status_code: int, **kwargs: Any) -> None:
        """
        统一错误处理
        
        Args:
            handler: 请求处理器
            status_code: HTTP状态码
            **kwargs: 额外参数
        """
        exc_info = kwargs.get('exc_info')
        
        # 设置响应头
        handler.set_header("Content-Type", "application/json; charset=UTF-8")
        
        if exc_info:
            exc_type, exc_value, exc_traceback = exc_info
            
            # 记录错误日志
            ErrorHandler._log_error(exc_type, exc_value, exc_traceback, handler)
            
            # 处理自定义异常
            if isinstance(exc_value, BadRequestError):
                ErrorHandler._handle_bad_request(handler, exc_value)
            elif isinstance(exc_value, UnauthorizedError):
                ErrorHandler._handle_unauthorized(handler, exc_value)
            elif isinstance(exc_value, ForbiddenError):
                ErrorHandler._handle_forbidden(handler, exc_value)
            elif isinstance(exc_value, NotFoundError):
                ErrorHandler._handle_not_found(handler, exc_value)
            elif isinstance(exc_value, ValidationError):
                ErrorHandler._handle_validation_error(handler, exc_value)
            elif isinstance(exc_value, InternalServerError):
                ErrorHandler._handle_internal_error(handler, exc_value)
            else:
                # 处理其他异常
                ErrorHandler._handle_generic_error(handler, status_code, exc_value)
        else:
            # 没有异常信息
            ErrorHandler._handle_status_code_error(handler, status_code)
    
    @staticmethod
    def _log_error(exc_type: Any, exc_value: Any, exc_traceback: Any, handler: RequestHandler) -> None:
        """记录错误日志"""
        try:
            # 获取请求信息
            method = handler.request.method
            uri = handler.request.uri
            remote_ip = handler.request.remote_ip
            user_agent = handler.request.headers.get('User-Agent', 'Unknown')
            
            # 获取异常信息
            error_message = str(exc_value)
            error_type = exc_type.__name__
            
            # 记录错误
            logger.error(
                f"Error in [{method}] {uri} - "
                f"Type: {error_type} - "
                f"Message: {error_message} - "
                f"IP: {remote_ip} - "
                f"UA: {user_agent[:50]}"
            )
            
            # 在调试模式下记录堆栈跟踪
            if handler.settings.get('debug', False):
                tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                tb_text = ''.join(tb_lines)
                logger.debug(f"Stack trace:\n{tb_text}")
                
        except Exception as e:
            logger.error(f"Failed to log error: {e}")
    
    @staticmethod
    def _handle_bad_request(handler: RequestHandler, error: BadRequestError) -> None:
        """处理400错误"""
        handler.set_status(400)
        handler.write({
            'success': False,
            'error': {
                'code': error.code,
                'message': str(error),
                'details': getattr(error, 'details', None)
            },
            'timestamp': handler.request.request_time()
        })
    
    @staticmethod
    def _handle_unauthorized(handler: RequestHandler, error: UnauthorizedError) -> None:
        """处理401错误"""
        handler.set_status(401)
        handler.write({
            'success': False,
            'error': {
                'code': error.code,
                'message': str(error),
                'details': getattr(error, 'details', None)
            },
            'timestamp': handler.request.request_time()
        })
    
    @staticmethod
    def _handle_forbidden(handler: RequestHandler, error: ForbiddenError) -> None:
        """处理403错误"""
        handler.set_status(403)
        handler.write({
            'success': False,
            'error': {
                'code': error.code,
                'message': str(error),
                'details': getattr(error, 'details', None)
            },
            'timestamp': handler.request.request_time()
        })
    
    @staticmethod
    def _handle_not_found(handler: RequestHandler, error: NotFoundError) -> None:
        """处理404错误"""
        handler.set_status(404)
        handler.write({
            'success': False,
            'error': {
                'code': error.code,
                'message': str(error),
                'details': getattr(error, 'details', None)
            },
            'timestamp': handler.request.request_time()
        })
    
    @staticmethod
    def _handle_validation_error(handler: RequestHandler, error: ValidationError) -> None:
        """处理验证错误"""
        handler.set_status(422)  # Unprocessable Entity
        handler.write({
            'success': False,
            'error': {
                'code': error.code,
                'message': str(error),
                'details': getattr(error, 'details', None),
                'validation_errors': getattr(error, 'validation_errors', None)
            },
            'timestamp': handler.request.request_time()
        })
    
    @staticmethod
    def _handle_internal_error(handler: RequestHandler, error: InternalServerError) -> None:
        """处理500错误"""
        handler.set_status(500)
        
        # 在生产环境中隐藏内部错误详情
        if handler.settings.get('debug', False):
            error_message = str(error)
            error_details = getattr(error, 'details', None)
        else:
            error_message = "Internal server error"
            error_details = None
        
        handler.write({
            'success': False,
            'error': {
                'code': error.code,
                'message': error_message,
                'details': error_details
            },
            'timestamp': handler.request.request_time()
        })
    
    @staticmethod
    def _handle_generic_error(handler: RequestHandler, status_code: int, error: Exception) -> None:
        """处理通用错误"""
        handler.set_status(status_code)
        
        # 在生产环境中隐藏内部错误详情
        if handler.settings.get('debug', False):
            error_message = str(error)
        else:
            if status_code >= 500:
                error_message = "Internal server error"
            else:
                error_message = str(error) or handler._reason or 'Unknown error'
        
        handler.write({
            'success': False,
            'error': {
                'code': f'HTTP_{status_code}',
                'message': error_message
            },
            'timestamp': handler.request.request_time()
        })
    
    @staticmethod
    def _handle_status_code_error(handler: RequestHandler, status_code: int) -> None:
        """处理状态码错误（无异常）"""
        handler.set_status(status_code)
        
        # 定义常见状态码的错误消息
        error_messages = {
            400: "Bad request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not found",
            405: "Method not allowed",
            408: "Request timeout",
            429: "Too many requests",
            500: "Internal server error",
            502: "Bad gateway",
            503: "Service unavailable",
            504: "Gateway timeout"
        }
        
        error_message = error_messages.get(status_code, handler._reason or 'Unknown error')
        
        handler.write({
            'success': False,
            'error': {
                'code': f'HTTP_{status_code}',
                'message': error_message
            },
            'timestamp': handler.request.request_time()
        })
    
    @staticmethod
    def create_error_response(code: str, message: str, details: Any = None) -> Dict[str, Any]:
        """
        创建错误响应
        
        Args:
            code: 错误代码
            message: 错误消息
            details: 错误详情
            
        Returns:
            错误响应字典
        """
        return {
            'success': False,
            'error': {
                'code': code,
                'message': message,
                'details': details
            }
        }
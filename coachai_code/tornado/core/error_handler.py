"""
错误处理器模块
统一处理应用中的异常
"""

import json
import traceback
from typing import Any, Dict
from loguru import logger
from tornado.web import RequestHandler, HTTPError

from .exceptions import BaseAPIError


class ErrorHandler:
    """错误处理器"""
    
    @staticmethod
    def write_error(handler: RequestHandler, status_code: int, **kwargs: Any) -> None:
        """
        统一错误响应方法
        
        Args:
            handler: RequestHandler实例
            status_code: HTTP状态码
            **kwargs: 额外参数
        """
        exc_info = kwargs.get("exc_info")
        
        if exc_info:
            exc_type, exc_value, exc_traceback = exc_info
            
            # 处理自定义API异常
            if isinstance(exc_value, BaseAPIError):
                error_response = {
                    "success": False,
                    "error": {
                        "code": exc_value.error_code,
                        "message": exc_value.message,
                        "details": exc_value.details
                    },
                    "timestamp": handler.request.request_time()
                }
                handler.set_status(exc_value.status_code)
                handler.write(error_response)
                return
            
            # 处理HTTPError
            elif isinstance(exc_value, HTTPError):
                error_response = {
                    "success": False,
                    "error": {
                        "code": f"HTTP_{exc_value.status_code}",
                        "message": exc_value.reason or "HTTP error",
                        "details": {}
                    },
                    "timestamp": handler.request.request_time()
                }
                handler.set_status(exc_value.status_code)
                handler.write(error_response)
                return
            
            # 处理其他异常
            else:
                # 记录错误日志（英文）
                logger.error(f"Unhandled exception: {exc_value}")
                logger.error(traceback.format_exc())
                
                # 生产环境隐藏详细错误信息
                if handler.settings.get("debug", False):
                    error_details = {
                        "type": exc_type.__name__,
                        "message": str(exc_value),
                        "traceback": traceback.format_exception(exc_type, exc_value, exc_traceback)
                    }
                else:
                    error_details = {}
                
                error_response = {
                    "success": False,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "Internal server error",
                        "details": error_details
                    },
                    "timestamp": handler.request.request_time()
                }
                handler.set_status(500)
                handler.write(error_response)
                return
        
        # 默认错误响应
        error_response = {
            "success": False,
            "error": {
                "code": f"HTTP_{status_code}",
                "message": "Unknown error",
                "details": {}
            },
            "timestamp": handler.request.request_time()
        }
        handler.set_status(status_code)
        handler.write(error_response)
    
    @staticmethod
    def log_exception(handler: RequestHandler, exc_info: tuple) -> None:
        """
        记录异常日志
        
        Args:
            handler: RequestHandler实例
            exc_info: 异常信息
        """
        exc_type, exc_value, exc_traceback = exc_info
        
        # 记录请求信息
        request_info = {
            "method": handler.request.method,
            "uri": handler.request.uri,
            "remote_ip": handler.request.remote_ip,
            "headers": dict(handler.request.headers),
            "body": handler.request.body.decode("utf-8", errors="ignore") if handler.request.body else None
        }
        
        # 记录异常信息（英文日志）
        logger.error(f"Request failed: {request_info}")
        logger.error(f"Exception: {exc_type.__name__}: {exc_value}")
        logger.error(f"Traceback: {traceback.format_exception(exc_type, exc_value, exc_traceback)}")
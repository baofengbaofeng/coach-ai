"""
项目全局公共层初始化文件，包含全局常量、异常处理、中间件、分页、响应格式和工具函数等。
按照豆包AI助手最佳实践：全局公共代码放在 core/ 目录下。
"""
from __future__ import annotations


__version__: str = "0.1.0"
__description__: str = "CoachAI 全局公共层，提供项目级别的通用功能和工具"


# ==================== 导出核心模块 ====================
# 导入并重新导出所有公共模块，方便外部使用
from .constants import *  # noqa: F403
from .exceptions import *  # noqa: F403
from .middlewares import *  # noqa: F403
from .paginations import *  # noqa: F403
from .responses import *  # noqa: F403
from .utils import *  # noqa: F403


# ==================== 导出列表 ====================
__all__: list[str] = [
    # 从 constants 模块导出
    "SystemConfig",
    "UserRole",
    "HomeworkStatus",
    "ExerciseType",
    "TaskStatus",
    "TaskPriority",
    "HttpStatus",
    "ErrorMessages",
    "BusinessRules",
    "RegexPatterns",
    "CacheKeys",
    
    # 从 exceptions 模块导出
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
    
    # 从 middlewares 模块导出
    "RequestLoggingMiddleware",
    "ExceptionHandlingMiddleware",
    "CorsMiddleware",
    "PerformanceMonitoringMiddleware",
    "RequestIdMiddleware",
    
    # 从 paginations 模块导出
    "StandardPagination",
    "CursorPagination",
    "InfiniteScrollPagination",
    "get_pagination_params",
    
    # 从 responses 模块导出
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
    
    # 从 utils 模块导出
    "generate_random_string",
    "generate_uuid",
    "camel_to_snake",
    "snake_to_camel",
    "truncate_string",
    "get_current_timestamp",
    "get_current_datetime",
    "format_datetime",
    "parse_datetime",
    "get_time_range",
    "validate_file_extension",
    "validate_file_size",
    "generate_filename",
    "save_file_to_storage",
    "validate_email",
    "validate_phone",
    "validate_password_strength",
    "cache_result",
    "clear_cache_by_prefix",
    "paginate_queryset",
    "hash_string",
    "generate_token",
    "safe_json_loads",
    "safe_json_dumps",
    "timeit",
]

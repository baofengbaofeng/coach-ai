"""
项目全局常量定义文件，包含系统配置、业务规则、状态码和错误消息等常量。
按照豆包AI助手最佳实践：全局常量放在 core/constants.py 中。
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, List, Tuple


# ==================== 系统配置常量 ====================
class SystemConfig:
    """系统配置常量类，包含系统级别的配置参数"""
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # 文件上传配置
    MAX_FILE_SIZE_MB: int = 10  # 最大文件大小：10MB
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
    ALLOWED_VIDEO_EXTENSIONS: List[str] = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    ALLOWED_DOCUMENT_EXTENSIONS: List[str] = [".pdf", ".doc", ".docx", ".txt"]
    
    # 缓存配置
    DEFAULT_CACHE_TIMEOUT: int = 300  # 默认缓存超时时间：5分钟
    USER_SESSION_TIMEOUT: int = 1209600  # 用户会话超时时间：2周（秒）
    
    # 安全配置
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_MAX_LENGTH: int = 128
    TOKEN_EXPIRY_HOURS: int = 24  # JWT令牌过期时间：24小时
    REFRESH_TOKEN_EXPIRY_DAYS: int = 7  # 刷新令牌过期时间：7天


# ==================== 业务状态常量 ====================
class UserRole(str, Enum):
    """用户角色枚举"""
    
    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"
    ADMIN = "admin"


class HomeworkStatus(str, Enum):
    """作业状态枚举"""
    
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    GRADED = "graded"
    ERROR = "error"


class ExerciseType(str, Enum):
    """运动类型枚举"""
    
    JUMP_ROPE = "jump_rope"
    PUSH_UP = "push_up"
    SIT_UP = "sit_up"
    SQUAT = "squat"
    OTHER = "other"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """任务优先级枚举"""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# ==================== HTTP 状态码和消息 ====================
class HttpStatus:
    """HTTP 状态码常量"""
    
    # 成功状态码
    OK: int = 200
    CREATED: int = 201
    ACCEPTED: int = 202
    NO_CONTENT: int = 204
    
    # 客户端错误状态码
    BAD_REQUEST: int = 400
    UNAUTHORIZED: int = 401
    FORBIDDEN: int = 403
    NOT_FOUND: int = 404
    METHOD_NOT_ALLOWED: int = 405
    CONFLICT: int = 409
    UNPROCESSABLE_ENTITY: int = 422
    TOO_MANY_REQUESTS: int = 429
    
    # 服务器错误状态码
    INTERNAL_SERVER_ERROR: int = 500
    NOT_IMPLEMENTED: int = 501
    BAD_GATEWAY: int = 502
    SERVICE_UNAVAILABLE: int = 503
    GATEWAY_TIMEOUT: int = 504


class ErrorMessages:
    """错误消息常量"""
    
    # 通用错误消息
    INTERNAL_SERVER_ERROR: str = "服务器内部错误，请稍后重试"
    NOT_FOUND: str = "请求的资源不存在"
    UNAUTHORIZED: str = "未授权访问，请先登录"
    FORBIDDEN: str = "权限不足，无法访问该资源"
    BAD_REQUEST: str = "请求参数错误"
    VALIDATION_ERROR: str = "数据验证失败"
    
    # 业务错误消息
    USER_NOT_FOUND: str = "用户不存在"
    USER_ALREADY_EXISTS: str = "用户已存在"
    INVALID_CREDENTIALS: str = "用户名或密码错误"
    INVALID_TOKEN: str = "无效的令牌"
    EXPIRED_TOKEN: str = "令牌已过期"
    INSUFFICIENT_PERMISSIONS: str = "权限不足"
    
    # 文件相关错误
    FILE_TOO_LARGE: str = "文件大小超过限制"
    INVALID_FILE_TYPE: str = "不支持的文件类型"
    FILE_UPLOAD_FAILED: str = "文件上传失败"
    
    # AI 服务错误
    OCR_PROCESSING_FAILED: str = "OCR 处理失败"
    ACTION_RECOGNITION_FAILED: str = "动作识别失败"
    SPEECH_RECOGNITION_FAILED: str = "语音识别失败"


# ==================== 业务规则常量 ====================
class BusinessRules:
    """业务规则常量"""
    
    # 用户相关规则
    MIN_USER_AGE: int = 0
    MAX_USER_AGE: int = 120
    USERNAME_MIN_LENGTH: int = 3
    USERNAME_MAX_LENGTH: int = 150
    EMAIL_MAX_LENGTH: int = 254
    
    # 作业相关规则
    HOMEWORK_TITLE_MAX_LENGTH: int = 200
    HOMEWORK_SUBJECT_MAX_LENGTH: int = 50
    MAX_HOMEWORK_IMAGES: int = 10  # 每次最多上传10张图片
    
    # 运动相关规则
    EXERCISE_TITLE_MAX_LENGTH: int = 200
    MIN_EXERCISE_DURATION: int = 1  # 最小运动时长：1秒
    MAX_EXERCISE_DURATION: int = 3600  # 最大运动时长：1小时
    
    # 任务相关规则
    TASK_TITLE_MAX_LENGTH: int = 200
    MAX_TASK_REMINDERS: int = 5  # 每个任务最多设置5个提醒


# ==================== 正则表达式常量 ====================
class RegexPatterns:
    """正则表达式常量"""
    
    # 用户名：字母、数字、下划线，3-150个字符
    USERNAME: str = r"^[a-zA-Z0-9_]{3,150}$"
    
    # 邮箱地址
    EMAIL: str = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    # 手机号：中国手机号格式
    PHONE: str = r"^1[3-9]\d{9}$"
    
    # 密码：至少8个字符，包含字母和数字
    PASSWORD: str = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$"
    
    # 日期格式：YYYY-MM-DD
    DATE: str = r"^\d{4}-\d{2}-\d{2}$"
    
    # 时间格式：HH:MM:SS
    TIME: str = r"^\d{2}:\d{2}:\d{2}$"


# ==================== 缓存键常量 ====================
class CacheKeys:
    """缓存键常量"""
    
    # 用户相关缓存键
    USER_PROFILE_PREFIX: str = "user:profile:"
    USER_SESSION_PREFIX: str = "user:session:"
    
    # 作业相关缓存键
    HOMEWORK_RESULT_PREFIX: str = "homework:result:"
    HOMEWORK_LIST_PREFIX: str = "homework:list:"
    
    # 运动相关缓存键
    EXERCISE_SESSION_PREFIX: str = "exercise:session:"
    EXERCISE_STATS_PREFIX: str = "exercise:stats:"
    
    # 系统缓存键
    SYSTEM_CONFIG: str = "system:config"
    API_RATE_LIMIT_PREFIX: str = "api:rate_limit:"


# ==================== 导出常量 ====================
__all__: List[str] = [
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
]

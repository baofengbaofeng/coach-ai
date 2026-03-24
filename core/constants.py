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
    
    DRAFT = "draft"  # 草稿
    SUBMITTED = "submitted"  # 已提交
    PROCESSING = "processing"  # 处理中（OCR识别）
    CORRECTING = "correcting"  # 批改中
    COMPLETED = "completed"  # 已完成
    ERROR = "error"  # 错误
    
    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        """返回Django模型可用的choices列表。"""
        return [(member.value, member.name) for member in cls]


class ExerciseType(str, Enum):
    """运动类型枚举"""
    
    JUMP_ROPE = "jump_rope"
    PUSH_UP = "push_up"
    SIT_UP = "sit_up"
    SQUAT = "squat"
    RUNNING = "running"
    YOGA = "yoga"
    OTHER = "other"
    
    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        """返回Django模型可用的choices列表。"""
        return [(member.value, member.name) for member in cls]


class TaskStatus(str, Enum):
    """任务状态枚举"""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    
    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        """返回Django模型可用的choices列表。"""
        return [(member.value, member.name) for member in cls]


class TaskPriority(str, Enum):
    """任务优先级枚举"""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    
    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        """返回Django模型可用的choices列表。"""
        return [(member.value, member.name) for member in cls]


# ==================== 成就系统常量 ====================
class AchievementType(str, Enum):
    """成就类型枚举"""
    
    COUNT = "count"  # 计数型
    STREAK = "streak"  # 连续型
    COMPOSITE = "composite"  # 复合型
    TIME_BASED = "time_based"  # 时间型
    MILESTONE = "milestone"  # 里程碑型
    
    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        """返回Django模型可用的choices列表。"""
        return [(member.value, member.name) for member in cls]


class AchievementDifficulty(str, Enum):
    """成就难度枚举"""
    
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"
    MASTER = "master"
    
    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        """返回Django模型可用的choices列表。"""
        return [(member.value, member.name) for member in cls]


class AchievementConditionOperator(str, Enum):
    """成就条件运算符枚举"""
    
    GTE = "gte"  # 大于等于
    LTE = "lte"  # 小于等于
    EQ = "eq"  # 等于
    GT = "gt"  # 大于
    LT = "lt"  # 小于
    
    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        """返回Django模型可用的choices列表。"""
        return [(member.value, member.name) for member in cls]


class AchievementRewardType(str, Enum):
    """成就奖励类型枚举"""
    
    POINTS = "points"  # 积分
    BADGE = "badge"  # 徽章
    COUPON = "coupon"  # 优惠券
    PRIVILEGE = "privilege"  # 特权
    TITLE = "title"  # 称号
    ITEM = "item"  # 物品
    
    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        """返回Django模型可用的choices列表。"""
        return [(member.value, member.name) for member in cls]


class AchievementStatisticType(str, Enum):
    """成就统计类型枚举"""
    
    DAILY_UNLOCKS = "daily_unlocks"  # 每日解锁数
    CATEGORY_DISTRIBUTION = "category_distribution"  # 分类分布
    DIFFICULTY_DISTRIBUTION = "difficulty_distribution"  # 难度分布
    USER_PROGRESS = "user_progress"  # 用户进度
    REWARD_DISTRIBUTION = "reward_distribution"  # 奖励分布
    
    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        """返回Django模型可用的choices列表。"""
        return [(member.value, member.name) for member in cls]


# ==================== 文件类型常量 ====================
class FileTypes:
    """文件类型常量类"""
    
    IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
    PDF_EXTENSIONS: List[str] = [".pdf"]
    VIDEO_EXTENSIONS: List[str] = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    DOCUMENT_EXTENSIONS: List[str] = [".doc", ".docx", ".txt"]
    
    # 所有允许的文件扩展名
    ALL_EXTENSIONS: List[str] = (
        IMAGE_EXTENSIONS + 
        PDF_EXTENSIONS + 
        VIDEO_EXTENSIONS + 
        DOCUMENT_EXTENSIONS
    )


# ==================== 题目类型常量 ====================
class QuestionType(str, Enum):
    """题目类型枚举"""
    
    SINGLE_CHOICE = "single_choice"  # 单选题
    MULTIPLE_CHOICE = "multiple_choice"  # 多选题
    TRUE_FALSE = "true_false"  # 判断题
    FILL_BLANK = "fill_blank"  # 填空题
    SHORT_ANSWER = "short_answer"  # 简答题
    ESSAY = "essay"  # 论述题
    CALCULATION = "calculation"  # 计算题
    
    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        """返回Django模型可用的choices列表。"""
        return [(member.value, member.name) for member in cls]


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
    """业务规则常量类，包含各种业务限制和规则"""
    
    # 用户相关
    MIN_USER_AGE: int = 0
    MAX_USER_AGE: int = 120
    USERNAME_MIN_LENGTH: int = 3
    USERNAME_MAX_LENGTH: int = 150
    EMAIL_MAX_LENGTH: int = 254
    DISPLAY_NAME_MAX_LENGTH: int = 50
    PHONE_NUMBER_MAX_LENGTH: int = 20
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_MAX_LENGTH: int = 128
    
    # 作业相关
    HOMEWORK_TITLE_MAX_LENGTH: int = 200
    HOMEWORK_DESCRIPTION_MAX_LENGTH: int = 2000
    SUBJECT_NAME_MAX_LENGTH: int = 50
    STATUS_MAX_LENGTH: int = 20
    MAX_HOMEWORK_IMAGES: int = 10  # 每次最多上传10张图片
    
    # 题目相关
    QUESTION_CONTENT_MAX_LENGTH: int = 5000
    QUESTION_TYPE_MAX_LENGTH: int = 50
    ANSWER_MAX_LENGTH: int = 2000
    CORRECTION_NOTES_MAX_LENGTH: int = 1000
    
    # 知识点相关
    KNOWLEDGE_POINT_NAME_MAX_LENGTH: int = 100
    KNOWLEDGE_POINT_DESC_MAX_LENGTH: int = 1000
    
    # 分数相关
    SCORE_MAX_DIGITS: int = 5
    SCORE_DECIMAL_PLACES: int = 2
    MAX_SCORE: int = 100
    MAX_SCORE_PER_QUESTION: int = 20
    PERCENTAGE_MAX_DIGITS: int = 5
    PERCENTAGE_DECIMAL_PLACES: int = 2
    
    # 难度等级
    DIFFICULTY_EASY: int = 1
    DIFFICULTY_MEDIUM: int = 3
    DIFFICULTY_HARD: int = 5
    DIFFICULTY_LEVEL_CHOICES: List[Tuple[int, str]] = [
        (1, "非常简单"),
        (2, "简单"),
        (3, "中等"),
        (4, "困难"),
        (5, "非常困难"),
    ]
    
    # 运动相关规则
    EXERCISE_TITLE_MAX_LENGTH: int = 200
    EXERCISE_DESCRIPTION_MAX_LENGTH: int = 2000
    EXERCISE_TYPE_MAX_LENGTH: int = 50
    EXERCISE_PLAN_NAME_MAX_LENGTH: int = 100
    EXERCISE_PLAN_DESC_MAX_LENGTH: int = 1000
    MIN_EXERCISE_DURATION: int = 1  # 最小运动时长：1秒
    MAX_EXERCISE_DURATION: int = 3600  # 最大运动时长：1小时
    CALORIES_MAX_DIGITS: int = 7
    CALORIES_DECIMAL_PLACES: int = 2
    COORDINATE_MAX_DIGITS: int = 10
    COORDINATE_DECIMAL_PLACES: int = 8
    LOCATION_NAME_MAX_LENGTH: int = 100
    ANALYSIS_PERIOD_MAX_LENGTH: int = 20
    DURATION_MAX_DIGITS: int = 7
    DURATION_DECIMAL_PLACES: int = 2
    ANALYSIS_TEXT_MAX_LENGTH: int = 5000
    
    # 任务相关规则
    TASK_TITLE_MAX_LENGTH: int = 200
    MAX_TASK_REMINDERS: int = 5  # 每个任务最多设置5个提醒
    
    # 成就相关规则
    ACHIEVEMENT_NAME_MAX_LENGTH: int = 200
    ACHIEVEMENT_DESCRIPTION_MAX_LENGTH: int = 2000
    ACHIEVEMENT_CATEGORY_NAME_MAX_LENGTH: int = 100
    ACHIEVEMENT_CATEGORY_DESC_MAX_LENGTH: int = 1000
    ACHIEVEMENT_CONDITION_TYPE_MAX_LENGTH: int = 50
    ACHIEVEMENT_CONDITION_OPERATOR_MAX_LENGTH: int = 10
    ACHIEVEMENT_REWARD_TYPE_MAX_LENGTH: int = 50
    ACHIEVEMENT_REWARD_VALUE_MAX_LENGTH: int = 255
    ACHIEVEMENT_ICON_MAX_LENGTH: int = 50
    ACHIEVEMENT_BADGE_IMAGE_MAX_LENGTH: int = 255
    ACHIEVEMENT_REWARD_BADGE_MAX_LENGTH: int = 100
    ACHIEVEMENT_RECURRENCE_RULE_MAX_LENGTH: int = 100
    ACHIEVEMENT_TEMPLATE_NAME_MAX_LENGTH: int = 100
    ACHIEVEMENT_STATISTIC_TYPE_MAX_LENGTH: int = 50
    
    # 成就条件值范围
    ACHIEVEMENT_CONDITION_MIN_VALUE: float = 0.01
    ACHIEVEMENT_CONDITION_MAX_VALUE: float = 1000000.00
    ACHIEVEMENT_TIME_LIMIT_MIN_DAYS: int = 0
    ACHIEVEMENT_TIME_LIMIT_MAX_DAYS: int = 365  # 最多一年
    
    # 成就奖励范围
    ACHIEVEMENT_REWARD_MIN_POINTS: int = 0
    ACHIEVEMENT_REWARD_MAX_POINTS: int = 10000
    ACHIEVEMENT_DISPLAY_ORDER_MIN: int = 0
    ACHIEVEMENT_DISPLAY_ORDER_MAX: int = 1000
    
    # 用户成就进度范围
    USER_ACHIEVEMENT_MIN_VALUE: float = 0.00
    USER_ACHIEVEMENT_MAX_VALUE: float = 1000000.00
    USER_ACHIEVEMENT_MIN_PROGRESS: int = 0
    USER_ACHIEVEMENT_MAX_PROGRESS: int = 100
    
    # 成就统计限制
    MAX_ACHIEVEMENTS_PER_CATEGORY: int = 100
    MAX_USER_ACHIEVEMENTS: int = 1000  # 每个用户最多1000个成就记录
    MAX_DAILY_STATISTICS_DAYS: int = 365  # 最多统计365天的数据


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
    "AchievementType",
    "AchievementDifficulty",
    "AchievementConditionOperator",
    "AchievementRewardType",
    "AchievementStatisticType",
    "FileTypes",
    "QuestionType",
    "HttpStatus",
    "ErrorMessages",
    "BusinessRules",
    "RegexPatterns",
    "CacheKeys",
]

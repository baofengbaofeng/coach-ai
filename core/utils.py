"""
全局工具函数模块，提供项目级别的通用工具函数和辅助类。
按照豆包AI助手最佳实践和coding-style.md规范实现。
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import re
import string
import time
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

from django.core.cache import cache
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import QuerySet

from core.constants import RegexPatterns, SystemConfig


# ==================== 类型定义 ====================
T = TypeVar("T")
R = TypeVar("R")


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 字符串处理工具 ====================
def generate_random_string(length: int = 32, include_digits: bool = True) -> str:
    """
    生成指定长度的随机字符串。
    """
    characters: str = string.ascii_letters
    if include_digits:
        characters += string.digits
    
    return "".join(random.choice(characters) for _ in range(length))


def generate_uuid(include_hyphens: bool = True) -> str:
    """
    生成UUID字符串。
    """
    uuid_str: str = str(uuid.uuid4())
    if not include_hyphens:
        uuid_str = uuid_str.replace("-", "")
    
    return uuid_str


def camel_to_snake(camel_str: str) -> str:
    """
    将驼峰命名转换为蛇形命名。
    """
    snake_str: str = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", camel_str)
    snake_str = re.sub(r"([a-z])([A-Z])", r"\1_\2", snake_str)
    snake_str = snake_str.lower().replace("__", "_")
    
    return snake_str


def snake_to_camel(snake_str: str, upper_first: bool = False) -> str:
    """
    将蛇形命名转换为驼峰命名。
    """
    components: List[str] = snake_str.split("_")
    
    if upper_first:
        camel_str: str = "".join(x.title() for x in components)
    else:
        camel_str = components[0] + "".join(x.title() for x in components[1:])
    
    return camel_str


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断字符串到指定长度。
    """
    if len(text) <= max_length:
        return text
    
    actual_length: int = max_length - len(suffix)
    if actual_length <= 0:
        return suffix
    
    return text[:actual_length] + suffix


# ==================== 日期时间处理工具 ====================
def get_current_timestamp() -> int:
    """
    获取当前时间戳（秒级）。
    """
    return int(time.time())


def get_current_datetime() -> datetime:
    """
    获取当前日期时间对象（UTC时区）。
    """
    return datetime.now(timezone.utc)


def format_datetime(
    dt: datetime,
    format_str: str = "%Y-%m-%d %H:%M:%S",
    timezone_str: Optional[str] = None,
) -> str:
    """
    格式化日期时间对象为字符串。
    """
    if timezone_str:
        import pytz
        
        target_tz = pytz.timezone(timezone_str)
        dt = dt.astimezone(target_tz)
    
    return dt.strftime(format_str)


def parse_datetime(
    datetime_str: str,
    format_str: str = "%Y-%m-%d %H:%M:%S",
    timezone_str: Optional[str] = None,
) -> datetime:
    """
    解析字符串为日期时间对象。
    """
    dt: datetime = datetime.strptime(datetime_str, format_str)
    
    if timezone_str:
        import pytz
        
        target_tz = pytz.timezone(timezone_str)
        dt = target_tz.localize(dt)
    
    return dt


def get_time_range(
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
) -> Tuple[datetime, datetime]:
    """
    获取时间范围。
    """
    end_time: datetime = get_current_datetime()
    start_time: datetime = end_time - timedelta(
        days=days, hours=hours, minutes=minutes, seconds=seconds
    )
    
    return start_time, end_time


# ==================== 文件处理工具 ====================
def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    验证文件扩展名是否在允许的列表中。
    """
    _, ext = os.path.splitext(filename)
    return ext.lower() in [ext.lower() for ext in allowed_extensions]


def validate_file_size(file_size: int, max_size_mb: int = SystemConfig.MAX_FILE_SIZE_MB) -> bool:
    """
    验证文件大小是否超过限制。
    """
    max_size_bytes: int = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes


def generate_filename(original_filename: str, prefix: str = "") -> str:
    """
    生成唯一的文件名。
    """
    name, ext = os.path.splitext(original_filename)
    
    timestamp: int = get_current_timestamp()
    random_num: int = random.randint(100000, 999999)
    
    if prefix:
        new_filename: str = f"{prefix}_{timestamp}_{random_num}{ext}"
    else:
        new_filename = f"{timestamp}_{random_num}{ext}"
    
    return new_filename


def save_file_to_storage(file_content: bytes, file_path: str) -> str:
    """
    保存文件到存储系统。
    """
    try:
        saved_path: str = default_storage.save(file_path, file_content)
        return saved_path
    except Exception as e:
        _LOGGER.error("文件保存失败: %s, 路径: %s", str(e), file_path)
        raise IOError(f"文件保存失败: {str(e)}")


# ==================== 数据验证工具 ====================
def validate_email(email: str) -> bool:
    """
    验证邮箱地址格式是否正确。
    """
    return bool(re.match(RegexPatterns.EMAIL, email))


def validate_phone(phone: str) -> bool:
    """
    验证手机号格式是否正确。
    """
    return bool(re.match(RegexPatterns.PHONE, phone))


def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """
    验证密码强度。
    """
    errors: List[str] = []
    
    if len(password) < SystemConfig.PASSWORD_MIN_LENGTH:
        errors.append(f"密码长度至少{SystemConfig.PASSWORD_MIN_LENGTH}位")
    
    if len(password) > SystemConfig.PASSWORD_MAX_LENGTH:
        errors.append(f"密码长度不能超过{SystemConfig.PASSWORD_MAX_LENGTH}位")
    
    if not re.search(r"[A-Z]", password):
        errors.append("密码必须包含大写字母")
    
    if not re.search(r"[a-z]", password):
        errors.append("密码必须包含小写字母")
    
    if not re.search(r"\d", password):
        errors.append("密码必须包含数字")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("密码必须包含特殊字符")
    
    return len(errors) == 0, errors


# ==================== 缓存工具 ====================
def cache_result(
    key_prefix: str,
    timeout: int = SystemConfig.DEFAULT_CACHE_TIMEOUT,
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    缓存装饰器。
    """
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            # 生成缓存键
            cache_key: str = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取结果
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                _LOGGER.debug("缓存命中: %s", cache_key)
                return cached_result
            
            # 执行函数并缓存结果
            result: R = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            _LOGGER.debug("缓存设置: %s, 超时: %d秒", cache_key, timeout)
            
            return result
        
        return wrapper
    
    return decorator


def clear_cache_by_prefix(key_prefix: str) -> int:
    """
    清除指定前缀的缓存。
    """
    # 注意：这个实现依赖于具体的缓存后端
    # 对于Redis，可以使用keys命令，但生产环境慎用
    _LOGGER.info("清除缓存前缀: %s", key_prefix)
    
    # 这里只是示例，实际实现需要根据缓存后端调整
    return 0


# ==================== 分页工具 ====================
def paginate_queryset(
    queryset: QuerySet[T],
    page: int = 1,
    page_size: int = SystemConfig.DEFAULT_PAGE_SIZE,
) -> Tuple[List[T], Dict[str, Any]]:
    """
    分页查询集。
    """
    paginator = Paginator(queryset, page_size)
    
    try:
        page_obj = paginator.page(page)
        data: List[T] = list(page_obj.object_list)
        
        meta: Dict[str, Any] = {
            "pagination": {
                "total": paginator.count,
                "count": len(data),
                "page": page,
                "page_size": page_size,
                "total_pages": paginator.num_pages,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            }
        }
        
        return data, meta
        
    except Exception as e:
        _LOGGER.error("分页查询失败: %s", str(e))
        raise


# ==================== 加密工具 ====================
def hash_string(text: str, algorithm: str = "sha256") -> str:
    """
    哈希字符串。
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode("utf-8"))
    return hash_obj.hexdigest()


def generate_token(length: int = 64) -> str:
    """
    生成安全令牌。
    """
    random_bytes = os.urandom(length)
    return random_bytes.hex()


# ==================== JSON工具 ====================
def safe_json_loads(json_str: str) -> Optional[Any]:
    """
    安全解析JSON字符串。
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None


def safe_json_dumps(obj: Any, indent: Optional[int] = None) -> Optional[str]:
    """
    安全序列化对象为JSON字符串。
    """
    try:
        return json.dumps(obj, indent=indent, ensure_ascii=False)
    except (TypeError, ValueError):
        return None


# ==================== 性能监控工具 ====================
def timeit(func: Callable[..., R]) -> Callable[..., R]:
    """
    函数执行时间监控装饰器。
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> R:
        start_time: float = time.time()
        
        try:
            result: R = func(*args, **kwargs)
            return result
        finally:
            end_time: float = time.time()
            execution_time: float = end_time - start_time
            
            _LOGGER.debug(
                "函数 %s 执行时间: %.3f秒",
                func.__name__,
                execution_time,
            )
    
    return wrapper


# ==================== 导出定义 ====================
__all__: list[str] = [
    # 字符串处理
    "generate_random_string",
    "generate_uuid",
    "camel_to_snake",
    "snake_to_camel",
    "truncate_string",
    
    # 日期时间处理
    "get_current_timestamp",
    "get_current_datetime",
    "format_datetime",
    "parse_datetime",
    "get_time_range",
    
    # 文件处理
    "validate_file_extension",
    "validate_file_size",
    "generate_filename",
    "save_file_to_storage",
    
    # 数据验证
    "validate_email",
    "validate_phone",
    "validate_password_strength",
    
    # 缓存工具
    "cache_result",
    "clear_cache_by_prefix",
    
    # 分页工具
    "paginate_queryset",
    
    # 加密工具
    "hash_string",
    "generate_token",
    
    # JSON工具
    "safe_json_loads",
    "safe_json_dumps",
    
    # 性能监控
    "timeit",
]
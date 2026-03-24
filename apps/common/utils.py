"""
公共工具函数模块，提供跨模块使用的通用工具函数。
按照豆包AI助手最佳实践：提供类型安全的工具函数。
"""
from __future__ import annotations

import hashlib
import json
import logging
import random
import re
import string
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlencode, urlparse

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import QuerySet
from django.utils import timezone

from core.constants import BusinessRules, ErrorMessages, RegexPatterns


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 字符串处理工具 ====================
def generate_random_string(length: int = 8) -> str:
    """
    生成指定长度的随机字符串。
    
    Args:
        length: 字符串长度，默认为8
        
    Returns:
        随机字符串
        
    Raises:
        ValueError: 如果长度小于1
    """
    if length < 1:
        raise ValueError("长度必须大于0")
    
    characters: str = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def generate_slug(text: str, max_length: int = 50) -> str:
    """
    从文本生成slug（URL友好的字符串）。
    
    Args:
        text: 原始文本
        max_length: 最大长度限制
        
    Returns:
        slug字符串
    """
    if not text:
        return ""
    
    # 转换为小写，替换非字母数字字符为连字符
    slug: str = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[-\s]+", "-", slug).strip("-")
    
    # 限制长度
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")
    
    return slug


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断文本到指定长度。
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
        
    Returns:
        截断后的文本
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[: max_length - len(suffix)] + suffix


def is_valid_email(email: str) -> bool:
    """
    验证邮箱地址是否有效。
    
    Args:
        email: 邮箱地址
        
    Returns:
        是否有效
    """
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def is_valid_phone(phone: str) -> bool:
    """
    验证手机号是否有效。
    
    Args:
        phone: 手机号
        
    Returns:
        是否有效
    """
    if not phone:
        return False
    
    # 简单的手机号验证（中国手机号格式）
    pattern: str = r"^1[3-9]\d{9}$"
    return bool(re.match(pattern, phone))


def is_valid_url(url: str) -> bool:
    """
    验证URL是否有效。
    
    Args:
        url: URL字符串
        
    Returns:
        是否有效
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


# ==================== 数字处理工具 ====================
def format_number(value: Union[int, float, Decimal], precision: int = 2) -> str:
    """
    格式化数字。
    
    Args:
        value: 数字值
        precision: 小数位数
        
    Returns:
        格式化后的字符串
    """
    if isinstance(value, Decimal):
        value = float(value)
    
    return f"{value:.{precision}f}"


def calculate_percentage(part: Union[int, float, Decimal], total: Union[int, float, Decimal]) -> float:
    """
    计算百分比。
    
    Args:
        part: 部分值
        total: 总值
        
    Returns:
        百分比值（0-100）
        
    Raises:
        ValueError: 如果总值为0
    """
    if total == 0:
        raise ValueError("总值不能为0")
    
    if isinstance(part, Decimal):
        part = float(part)
    if isinstance(total, Decimal):
        total = float(total)
    
    return (part / total) * 100


def calculate_average(values: List[Union[int, float, Decimal]]) -> float:
    """
    计算平均值。
    
    Args:
        values: 数值列表
        
    Returns:
        平均值
        
    Raises:
        ValueError: 如果列表为空
    """
    if not values:
        raise ValueError("数值列表不能为空")
    
    # 转换为float
    float_values: List[float] = [float(v) if isinstance(v, Decimal) else v for v in values]
    
    return sum(float_values) / len(float_values)


def calculate_median(values: List[Union[int, float, Decimal]]) -> float:
    """
    计算中位数。
    
    Args:
        values: 数值列表
        
    Returns:
        中位数
        
    Raises:
        ValueError: 如果列表为空
    """
    if not values:
        raise ValueError("数值列表不能为空")
    
    # 转换为float并排序
    float_values: List[float] = [float(v) if isinstance(v, Decimal) else v for v in values]
    sorted_values: List[float] = sorted(float_values)
    n: int = len(sorted_values)
    
    if n % 2 == 1:
        # 奇数个元素
        return sorted_values[n // 2]
    else:
        # 偶数个元素
        return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2


# ==================== 日期时间工具 ====================
def get_current_timestamp() -> int:
    """
    获取当前时间戳（秒）。
    
    Returns:
        当前时间戳
    """
    return int(time.time())


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间。
    
    Args:
        dt: 日期时间对象
        format_str: 格式字符串
        
    Returns:
        格式化后的字符串
    """
    if not dt:
        return ""
    
    return dt.strftime(format_str)


def parse_datetime(datetime_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    解析日期时间字符串。
    
    Args:
        datetime_str: 日期时间字符串
        format_str: 格式字符串
        
    Returns:
        日期时间对象，解析失败返回None
    """
    try:
        return datetime.strptime(datetime_str, format_str)
    except (ValueError, TypeError):
        return None


def get_time_range(start_date: datetime, end_date: datetime) -> List[datetime]:
    """
    获取两个日期之间的所有日期。
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        日期列表
    """
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    date_list: List[datetime] = []
    current_date: datetime = start_date
    
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    
    return date_list


def is_weekend(date: datetime) -> bool:
    """
    判断日期是否为周末。
    
    Args:
        date: 日期
        
    Returns:
        是否为周末
    """
    return date.weekday() >= 5  # 5=周六, 6=周日


def get_week_start_end(date: datetime) -> Tuple[datetime, datetime]:
    """
    获取指定日期所在周的起始和结束日期。
    
    Args:
        date: 日期
        
    Returns:
        (周开始日期, 周结束日期)
    """
    week_start: datetime = date - timedelta(days=date.weekday())
    week_end: datetime = week_start + timedelta(days=6)
    
    return week_start, week_end


def get_month_start_end(date: datetime) -> Tuple[datetime, datetime]:
    """
    获取指定日期所在月的起始和结束日期。
    
    Args:
        date: 日期
        
    Returns:
        (月开始日期, 月结束日期)
    """
    month_start: datetime = date.replace(day=1)
    
    # 计算下个月的第一天，然后减一天得到本月最后一天
    if month_start.month == 12:
        next_month: datetime = month_start.replace(year=month_start.year + 1, month=1, day=1)
    else:
        next_month = month_start.replace(month=month_start.month + 1, day=1)
    
    month_end: datetime = next_month - timedelta(days=1)
    
    return month_start, month_end


# ==================== 数据验证工具 ====================
def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """
    验证必填字段。
    
    Args:
        data: 数据字典
        required_fields: 必填字段列表
        
    Returns:
        缺失的字段列表，如果全部存在则返回空列表
    """
    missing_fields: List[str] = []
    
    for field in required_fields:
        if field not in data or data[field] in (None, "", [], {}):
            missing_fields.append(field)
    
    return missing_fields


def validate_field_length(value: str, min_length: int = 0, max_length: int = 255) -> bool:
    """
    验证字段长度。
    
    Args:
        value: 字段值
        min_length: 最小长度
        max_length: 最大长度
        
    Returns:
        是否有效
    """
    if value is None:
        return min_length == 0
    
    length: int = len(str(value))
    return min_length <= length <= max_length


def validate_numeric_range(value: Union[int, float, Decimal], min_value: float, max_value: float) -> bool:
    """
    验证数值范围。
    
    Args:
        value: 数值
        min_value: 最小值
        max_value: 最大值
        
    Returns:
        是否有效
    """
    if isinstance(value, Decimal):
        value = float(value)
    
    return min_value <= value <= max_value


def validate_list_length(value_list: List[Any], min_length: int = 0, max_length: int = 100) -> bool:
    """
    验证列表长度。
    
    Args:
        value_list: 列表
        min_length: 最小长度
        max_length: 最大长度
        
    Returns:
        是否有效
    """
    if value_list is None:
        return min_length == 0
    
    length: int = len(value_list)
    return min_length <= length <= max_length


# ==================== 缓存工具 ====================
def get_cache_key(prefix: str, *args: Any) -> str:
    """
    生成缓存键。
    
    Args:
        prefix: 缓存键前缀
        *args: 缓存键参数
        
    Returns:
        缓存键
    """
    if not args:
        return prefix
    
    # 将参数转换为字符串并连接
    param_str: str = ":".join(str(arg) for arg in args)
    return f"{prefix}:{param_str}"


def cache_get_or_set(key: str, default_func: callable, timeout: int = 300) -> Any:
    """
    获取缓存，如果不存在则设置缓存。
    
    Args:
        key: 缓存键
        default_func: 默认值函数
        timeout: 缓存超时时间（秒）
        
    Returns:
        缓存值
    """
    value = cache.get(key)
    
    if value is None:
        value = default_func()
        cache.set(key, value, timeout)
    
    return value


def cache_multi_get(keys: List[str]) -> Dict[str, Any]:
    """
    批量获取缓存。
    
    Args:
        keys: 缓存键列表
        
    Returns:
        缓存值字典
    """
    result: Dict[str, Any] = {}
    
    for key in keys:
        value = cache.get(key)
        if value is not None:
            result[key] = value
    
    return result


def cache_multi_set(data: Dict[str, Any], timeout: int = 300) -> None:
    """
    批量设置缓存。
    
    Args:
        data: 缓存数据字典
        timeout: 缓存超时时间（秒）
    """
    for key, value in data.items():
        cache.set(key, value, timeout)


# ==================== 安全工具 ====================
def hash_string(text: str, algorithm: str = "sha256") -> str:
    """
    哈希字符串。
    
    Args:
        text: 原始文本
        algorithm: 哈希算法
        
    Returns:
        哈希值
    """
    if not text:
        return ""
    
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode("utf-8"))
    return hash_obj.hexdigest()


def generate_secure_token(length: int = 32) -> str:
    """
    生成安全令牌。
    
    Args:
        length: 令牌长度
        
    Returns:
        安全令牌
    """
    if length < 16:
        raise ValueError("令牌长度必须至少为16")
    
    # 使用安全的随机数生成器
    characters: str = string.ascii_letters + string.digits + "_-"
    return "".join(random.SystemRandom().choice(characters) for _ in range(length))


def sanitize_input(input_str: str) -> str:
    """
    清理用户输入，防止XSS攻击。
    
    Args:
        input_str: 用户输入
        
    Returns:
        清理后的字符串
    """
    if not input_str:
        return ""
    
    # 移除HTML标签
    sanitized: str = re.sub(r"<[^>]*>", "", input_str)
    
    # 转义特殊字符
    sanitized = (
        sanitized.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )
    
    return sanitized


# ==================== 文件处理工具 ====================
def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名。
    
    Args:
        filename: 文件名
        
    Returns:
        文件扩展名（小写）
    """
    if not filename:
        return ""
    
    return filename.split(".")[-1].lower() if "." in filename else ""


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    验证文件扩展名。
    
    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名列表
        
    Returns:
        是否有效
    """
    extension: str = get_file_extension(filename)
    return extension in allowed_extensions


def get_file_size_mb(size_bytes: int) -> float:
    """
    将字节数转换为MB。
    
    Args:
        size_bytes: 字节数
        
    Returns:
        MB数
    """
    return size_bytes / (1024 * 1024)


def validate_file_size(size_bytes: int, max_size_mb: float) -> bool:
    """
    验证文件大小。
    
    Args:
        size_bytes: 文件大小（字节）
        max_size_mb: 最大文件大小（MB）
        
    Returns:
        是否有效
    """
    file_size_mb: float = get_file_size_mb(size_bytes)
    return file_size_mb <= max_size_mb


# ==================== JSON处理工具 ====================
def safe_json_loads(json_str: str) -> Optional[Dict[str, Any]]:
    """
    安全地解析JSON字符串。
    
    Args:
        json_str: JSON字符串
        
    Returns:
        JSON字典，解析失败返回None
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None


def safe_json_dumps(data: Any, indent: Optional[int] = None) -> str:
    """
    安全地将数据转换为JSON字符串。
    
    Args:
        data: 要转换的数据
        indent: 缩进
        
    Returns:
        JSON字符串
    """
    try:
        return json.dumps(data, indent=indent, ensure_ascii=False)
    except (TypeError, ValueError):
        return "{}"


# ==================== 分页工具 ====================
def paginate_queryset(
    queryset: QuerySet,
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100,
) -> Dict[str, Any]:
    """
    分页查询集。
    
    Args:
        queryset: Django查询集
        page: 页码（从1开始）
        page_size: 每页大小
        max_page_size: 最大每页大小
        
    Returns:
        分页结果字典
    """
    # 验证参数
    page = max(1, page)
    page_size = min(max(1, page_size), max_page_size)
    
    # 计算偏移量
    offset: int = (page - 1) * page_size
    
    # 获取总数
    total_count: int = queryset.count()
    
    # 计算总页数
    total_pages: int = (total_count + page_size - 1) // page_size if page_size > 0 else 0
    
    # 获取当前页数据
    items = list(queryset[offset : offset + page_size])
    
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_previous": page > 1,
        "has_next": page < total_pages,
    }


# ==================== 错误处理工具 ====================
def create_error_response(
    message: str,
    code: str = "error",
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    创建错误响应。
    
    Args:
        message: 错误消息
        code: 错误代码
        status_code: HTTP状态码
        details: 错误详情
        
    Returns:
        错误响应字典
    """
    response: Dict[str, Any] = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "status_code": status_code,
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    return response


def create_success_response(
    data: Any,
    message: str = "操作成功",
    status_code: int = 200,
) -> Dict[str, Any]:
    """
    创建成功响应。
    
    Args:
        data: 响应数据
        message: 成功消息
        status_code: HTTP状态码
        
    Returns:
        成功响应字典
    """
    return {
        "success": True,
        "data": data,
        "message": message,
        "status_code": status_code,
    }


# ==================== 业务逻辑工具 ====================
def calculate_progress(current: Union[int, float, Decimal], total: Union[int, float, Decimal]) -> int:
    """
    计算进度百分比。
    
    Args:
        current: 当前值
        total: 总值
        
    Returns:
        进度百分比（0-100）
    """
    if total == 0:
        return 0
    
    if isinstance(current, Decimal):
        current = float(current)
    if isinstance(total, Decimal):
        total = float(total)
    
    progress: float = (current / total) * 100
    return min(100, max(0, int(progress)))


def format_duration(seconds: int) -> str:
    """
    格式化持续时间。
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化后的持续时间字符串
    """
    if seconds < 60:
        return f"{seconds}秒"
    
    minutes: int = seconds // 60
    remaining_seconds: int = seconds % 60
    
    if minutes < 60:
        if remaining_seconds > 0:
            return f"{minutes}分{remaining_seconds}秒"
        return f"{minutes}分钟"
    
    hours: int = minutes // 60
    remaining_minutes: int = minutes % 60
    
    if hours < 24:
        if remaining_minutes > 0:
            return f"{hours}小时{remaining_minutes}分钟"
        return f"{hours}小时"
    
    days: int = hours // 24
    remaining_hours: int = hours % 24
    
    if remaining_hours > 0:
        return f"{days}天{remaining_hours}小时"
    return f"{days}天"


def calculate_age(birth_date: datetime) -> int:
    """
    计算年龄。
    
    Args:
        birth_date: 出生日期
        
    Returns:
        年龄
    """
    today: datetime = timezone.now().date()
    
    age: int = today.year - birth_date.year
    
    # 如果生日还没过，年龄减1
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    return age


# ==================== 性能监控工具 ====================
class Timer:
    """
    计时器类，用于测量代码执行时间。
    """
    
    def __init__(self, name: str = "Timer") -> None:
        """
        初始化计时器。
        
        Args:
            name: 计时器名称
        """
        self.name: str = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def __enter__(self) -> Timer:
        """进入上下文管理器时开始计时。"""
        self.start()
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """退出上下文管理器时停止计时。"""
        self.stop()
        
        if exc_type is None:
            _LOGGER.debug("%s 执行时间: %.4f秒", self.name, self.elapsed_time)
    
    def start(self) -> None:
        """开始计时。"""
        self.start_time = time.time()
        self.end_time = None
    
    def stop(self) -> None:
        """停止计时。"""
        if self.start_time is not None:
            self.end_time = time.time()
    
    @property
    def elapsed_time(self) -> float:
        """获取经过的时间（秒）。"""
        if self.start_time is None:
            return 0.0
        
        end_time: float = self.end_time if self.end_time is not None else time.time()
        return end_time - self.start_time


def measure_execution_time(func: callable) -> callable:
    """
    测量函数执行时间的装饰器。
    
    Args:
        func: 要测量的函数
        
    Returns:
        装饰后的函数
    """
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        timer: Timer = Timer(func.__name__)
        timer.start()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            timer.stop()
            _LOGGER.debug("%s 执行时间: %.4f秒", func.__name__, timer.elapsed_time)
    
    return wrapper


# ==================== 导出列表 ====================
__all__: List[str] = [
    # 字符串处理工具
    "generate_random_string",
    "generate_slug",
    "truncate_text",
    "is_valid_email",
    "is_valid_phone",
    "is_valid_url",
    
    # 数字处理工具
    "format_number",
    "calculate_percentage",
    "calculate_average",
    "calculate_median",
    
    # 日期时间工具
    "get_current_timestamp",
    "format_datetime",
    "parse_datetime",
    "get_time_range",
    "is_weekend",
    "get_week_start_end",
    "get_month_start_end",
    
    # 数据验证工具
    "validate_required_fields",
    "validate_field_length",
    "validate_numeric_range",
    "validate_list_length",
    
    # 缓存工具
    "get_cache_key",
    "cache_get_or_set",
    "cache_multi_get",
    "cache_multi_set",
    
    # 安全工具
    "hash_string",
    "generate_secure_token",
    "sanitize_input",
    
    # 文件处理工具
    "get_file_extension",
    "validate_file_extension",
    "get_file_size_mb",
    "validate_file_size",
    
    # JSON处理工具
    "safe_json_loads",
    "safe_json_dumps",
    
    # 分页工具
    "paginate_queryset",
    
    # 错误处理工具
    "create_error_response",
    "create_success_response",
    
    # 业务逻辑工具
    "calculate_progress",
    "format_duration",
    "calculate_age",
    
    # 性能监控工具
    "Timer",
    "measure_execution_time",
]
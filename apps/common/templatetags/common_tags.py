"""
公共模板标签模块，提供跨模块使用的模板标签。
按照豆包AI助手最佳实践：提供类型安全的模板标签。
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List

from django import template
from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from apps.common.utils import (
    calculate_age,
    calculate_percentage,
    format_datetime,
    get_current_timestamp,
    get_month_start_end,
    get_week_start_end,
    is_weekend,
)


# ==================== 注册标签 ====================
register = template.Library()


# ==================== 简单标签 ====================
@register.simple_tag
def current_time(format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    获取当前时间。
    
    Args:
        format_string: 时间格式字符串
        
    Returns:
        格式化后的当前时间
    """
    return timezone.now().strftime(format_string)


@register.simple_tag
def current_timestamp() -> int:
    """
    获取当前时间戳。
    
    Returns:
        当前时间戳（秒）
    """
    return get_current_timestamp()


@register.simple_tag
def settings_value(name: str) -> Any:
    """
    获取设置值。
    
    Args:
        name: 设置名称
        
    Returns:
        设置值
    """
    return getattr(settings, name, "")


@register.simple_tag
def debug_mode() -> bool:
    """
    检查是否处于调试模式。
    
    Returns:
        是否处于调试模式
    """
    return getattr(settings, "DEBUG", False)


@register.simple_tag
def app_version() -> str:
    """
    获取应用版本。
    
    Returns:
        应用版本字符串
    """
    return getattr(settings, "APP_VERSION", "1.0.0")


# ==================== 包含标签 ====================
@register.inclusion_tag("common/includes/pagination.html")
def render_pagination(
    page_obj: Any,
    page_param: str = "page",
    extra_params: Dict[str, str] = None,
) -> Dict[str, Any]:
    """
    渲染分页组件。
    
    Args:
        page_obj: 分页对象
        page_param: 页码参数名
        extra_params: 额外参数
        
    Returns:
        模板上下文
    """
    if not page_obj:
        return {}
    
    extra_params = extra_params or {}
    
    # 构建查询参数
    query_params = extra_params.copy()
    if page_param in query_params:
        del query_params[page_param]
    
    return {
        "page_obj": page_obj,
        "page_param": page_param,
        "query_params": query_params,
    }


@register.inclusion_tag("common/includes/breadcrumb.html")
def render_breadcrumb(items: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    渲染面包屑导航。
    
    Args:
        items: 面包屑项列表
        
    Returns:
        模板上下文
    """
    return {"items": items}


@register.inclusion_tag("common/includes/alert.html")
def render_alert(
    message: str,
    alert_type: str = "info",
    dismissible: bool = True,
) -> Dict[str, Any]:
    """
    渲染警告框。
    
    Args:
        message: 消息内容
        alert_type: 警告类型（success, info, warning, danger）
        dismissible: 是否可关闭
        
    Returns:
        模板上下文
    """
    return {
        "message": message,
        "alert_type": alert_type,
        "dismissible": dismissible,
    }


@register.inclusion_tag("common/includes/progress_bar.html")
def render_progress(
    value: Any,
    max_value: int = 100,
    show_label: bool = True,
    height: str = "20px",
) -> Dict[str, Any]:
    """
    渲染进度条。
    
    Args:
        value: 当前值
        max_value: 最大值
        show_label: 是否显示标签
        height: 进度条高度
        
    Returns:
        模板上下文
    """
    try:
        progress = min(max(int(value), 0), max_value)
        percentage = (progress / max_value) * 100
        
        # 根据百分比设置颜色
        if percentage >= 80:
            color_class = "bg-success"
        elif percentage >= 50:
            color_class = "bg-warning"
        else:
            color_class = "bg-danger"
        
        return {
            "progress": progress,
            "max_value": max_value,
            "percentage": percentage,
            "color_class": color_class,
            "show_label": show_label,
            "height": height,
        }
    except (ValueError, TypeError):
        return {
            "progress": 0,
            "max_value": max_value,
            "percentage": 0,
            "color_class": "bg-secondary",
            "show_label": show_label,
            "height": height,
        }


# ==================== 赋值标签 ====================
@register.simple_tag(takes_context=True)
def set_context_value(context: Dict[str, Any], name: str, value: Any) -> str:
    """
    设置上下文变量。
    
    Args:
        context: 模板上下文
        name: 变量名
        value: 变量值
        
    Returns:
        空字符串
    """
    context[name] = value
    return ""


@register.simple_tag(takes_context=True)
def get_context_value(context: Dict[str, Any], name: str, default: Any = "") -> Any:
    """
    获取上下文变量。
    
    Args:
        context: 模板上下文
        name: 变量名
        default: 默认值
        
    Returns:
        变量值
    """
    return context.get(name, default)


# ==================== 计算标签 ====================
@register.simple_tag
def calculate(
    operation: str,
    value1: Any,
    value2: Any = None,
) -> Any:
    """
    执行计算。
    
    Args:
        operation: 操作类型（add, subtract, multiply, divide, percentage）
        value1: 第一个值
        value2: 第二个值
        
    Returns:
        计算结果
    """
    try:
        # 转换值为数值
        if isinstance(value1, Decimal):
            num1 = float(value1)
        else:
            num1 = float(value1)
        
        if value2 is not None:
            if isinstance(value2, Decimal):
                num2 = float(value2)
            else:
                num2 = float(value2)
        
        # 执行计算
        if operation == "add":
            return num1 + num2
        elif operation == "subtract":
            return num1 - num2
        elif operation == "multiply":
            return num1 * num2
        elif operation == "divide":
            if num2 == 0:
                return 0
            return num1 / num2
        elif operation == "percentage":
            if num2 == 0:
                return 0
            return calculate_percentage(num1, num2)
        else:
            return value1
    except (ValueError, TypeError):
        return value1


@register.simple_tag
def format_calculation(
    operation: str,
    value1: Any,
    value2: Any = None,
    precision: int = 2,
) -> str:
    """
    格式化计算结果。
    
    Args:
        operation: 操作类型
        value1: 第一个值
        value2: 第二个值
        precision: 小数位数
        
    Returns:
        格式化后的计算结果
    """
    result = calculate(operation, value1, value2)
    
    try:
        return f"{float(result):.{precision}f}"
    except (ValueError, TypeError):
        return str(result)


# ==================== 日期时间标签 ====================
@register.simple_tag
def date_range(start_date: datetime, end_date: datetime) -> List[datetime]:
    """
    获取日期范围。
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        日期列表
    """
    from apps.common.utils import get_time_range
    return get_time_range(start_date, end_date)


@register.simple_tag
def week_range(date: datetime = None) -> Dict[str, datetime]:
    """
    获取周范围。
    
    Args:
        date: 日期，默认为当前日期
        
    Returns:
        周开始和结束日期
    """
    if date is None:
        date = timezone.now()
    
    week_start, week_end = get_week_start_end(date)
    
    return {
        "start": week_start,
        "end": week_end,
    }


@register.simple_tag
def month_range(date: datetime = None) -> Dict[str, datetime]:
    """
    获取月范围。
    
    Args:
        date: 日期，默认为当前日期
        
    Returns:
        月开始和结束日期
    """
    if date is None:
        date = timezone.now()
    
    month_start, month_end = get_month_start_end(date)
    
    return {
        "start": month_start,
        "end": month_end,
    }


@register.simple_tag
def is_date_weekend(date: datetime) -> bool:
    """
    检查日期是否为周末。
    
    Args:
        date: 日期
        
    Returns:
        是否为周末
    """
    return is_weekend(date)


@register.simple_tag
def calculate_age_from_birthdate(birth_date: datetime) -> int:
    """
    根据出生日期计算年龄。
    
    Args:
        birth_date: 出生日期
        
    Returns:
        年龄
    """
    return calculate_age(birth_date)


# ==================== JSON标签 ====================
@register.simple_tag
def to_json(data: Any) -> str:
    """
    将数据转换为JSON字符串。
    
    Args:
        data: 要转换的数据
        
    Returns:
        JSON字符串
    """
    try:
        return json.dumps(data, ensure_ascii=False)
    except (TypeError, ValueError):
        return "{}"


@register.simple_tag
def from_json(json_str: str) -> Any:
    """
    从JSON字符串解析数据。
    
    Args:
        json_str: JSON字符串
        
    Returns:
        解析后的数据
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return {}


# ==================== 条件标签 ====================
@register.simple_tag(takes_context=True)
def if_authenticated(context: Dict[str, Any], true_text: str, false_text: str = "") -> str:
    """
    根据用户认证状态返回不同文本。
    
    Args:
        context: 模板上下文
        true_text: 认证时显示的文本
        false_text: 未认证时显示的文本
        
    Returns:
        文本
    """
    user = context.get("user")
    
    if user and user.is_authenticated:
        return true_text
    return false_text


@register.simple_tag(takes_context=True)
def if_has_perm(
    context: Dict[str, Any],
    perm: str,
    true_text: str,
    false_text: str = "",
) -> str:
    """
    根据用户权限返回不同文本。
    
    Args:
        context: 模板上下文
        perm: 权限字符串
        true_text: 有权限时显示的文本
        false_text: 无权限时显示的文本
        
    Returns:
        文本
    """
    user = context.get("user")
    
    if user and user.has_perm(perm):
        return true_text
    return false_text


@register.simple_tag(takes_context=True)
def if_in_group(
    context: Dict[str, Any],
    group_name: str,
    true_text: str,
    false_text: str = "",
) -> str:
    """
    根据用户组返回不同文本。
    
    Args:
        context: 模板上下文
        group_name: 组名
        true_text: 在组内时显示的文本
        false_text: 不在组内时显示的文本
        
    Returns:
        文本
    """
    user = context.get("user")
    
    if user and user.groups.filter(name=group_name).exists():
        return true_text
    return false_text


# ==================== URL标签 ====================
@register.simple_tag
def build_query_string(params: Dict[str, str]) -> str:
    """
    构建查询字符串。
    
    Args:
        params: 参数字典
        
    Returns:
        查询字符串
    """
    from urllib.parse import urlencode
    return urlencode(params)


@register.simple_tag
def add_query_param(url: str, param_name: str, param_value: str) -> str:
    """
    为URL添加查询参数。
    
    Args:
        url: 原始URL
        param_name: 参数名
        param_value: 参数值
        
    Returns:
        添加参数后的URL
    """
    from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
    
    parsed = urlparse(url)
    query_dict = parse_qs(parsed.query)
    query_dict[param_name] = [param_value]
    
    new_query = urlencode(query_dict, doseq=True)
    new_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment,
    ))
    
    return new_url


# ==================== 导出列表 ====================
__all__: list = [
    # 简单标签
    "current_time",
    "current_timestamp",
    "settings_value",
    "debug_mode",
    "app_version",
    
    # 包含标签
    "render_pagination",
    "render_breadcrumb",
    "render_alert",
    "render_progress",
    
    # 赋值标签
    "set_context_value",
    "get_context_value",
    
    # 计算标签
    "calculate",
    "format_calculation",
    
    # 日期时间标签
    "date_range",
    "week_range",
    "month_range",
    "is_date_weekend",
    "calculate_age_from_birthdate",
    
    # JSON标签
    "to_json",
    "from_json",
    
    # 条件标签
    "if_authenticated",
    "if_has_perm",
    "if_in_group",
    
    # URL标签
    "build_query_string",
    "add_query_param",
]
"""
公共模板过滤器模块，提供跨模块使用的模板过滤器。
按照豆包AI助手最佳实践：提供类型安全的模板过滤器。
"""
from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal
from typing import Any

from django import template
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from apps.common.utils import format_datetime, format_duration, truncate_text


# ==================== 注册过滤器 ====================
register = template.Library()


# ==================== 字符串处理过滤器 ====================
@register.filter
def truncate(value: str, length: int = 50) -> str:
    """
    截断字符串到指定长度。
    
    Args:
        value: 原始字符串
        length: 最大长度
        
    Returns:
        截断后的字符串
    """
    if not value:
        return ""
    
    return truncate_text(str(value), length)


@register.filter
def slugify(value: str) -> str:
    """
    将字符串转换为slug格式。
    
    Args:
        value: 原始字符串
        
    Returns:
        slug字符串
    """
    if not value:
        return ""
    
    # 转换为小写，替换非字母数字字符为连字符
    slug: str = re.sub(r"[^\w\s-]", "", value.lower())
    slug = re.sub(r"[-\s]+", "-", slug).strip("-")
    
    return slug


@register.filter
def capitalize_first(value: str) -> str:
    """
    将字符串首字母大写。
    
    Args:
        value: 原始字符串
        
    Returns:
        首字母大写的字符串
    """
    if not value:
        return ""
    
    return value[0].upper() + value[1:] if value else ""


@register.filter
def replace(value: str, old: str, new: str) -> str:
    """
    替换字符串中的子串。
    
    Args:
        value: 原始字符串
        old: 要替换的子串
        new: 替换后的子串
        
    Returns:
        替换后的字符串
    """
    if not value:
        return ""
    
    return str(value).replace(old, new)


@register.filter
def strip_tags(value: str) -> str:
    """
    移除HTML标签。
    
    Args:
        value: 原始字符串
        
    Returns:
        移除HTML标签后的字符串
    """
    if not value:
        return ""
    
    # 简单的HTML标签移除
    return re.sub(r"<[^>]*>", "", str(value))


# ==================== 数字处理过滤器 ====================
@register.filter
def format_number(value: Any, precision: int = 2) -> str:
    """
    格式化数字。
    
    Args:
        value: 数字值
        precision: 小数位数
        
    Returns:
        格式化后的字符串
    """
    if value is None:
        return ""
    
    try:
        if isinstance(value, Decimal):
            num_value = float(value)
        else:
            num_value = float(value)
        
        return f"{num_value:.{precision}f}"
    except (ValueError, TypeError):
        return str(value)


@register.filter
def format_percentage(value: Any, precision: int = 1) -> str:
    """
    格式化百分比。
    
    Args:
        value: 百分比值（0-100）
        precision: 小数位数
        
    Returns:
        格式化后的百分比字符串
    """
    if value is None:
        return ""
    
    try:
        if isinstance(value, Decimal):
            num_value = float(value)
        else:
            num_value = float(value)
        
        return f"{num_value:.{precision}f}%"
    except (ValueError, TypeError):
        return str(value)


@register.filter
def add_commas(value: Any) -> str:
    """
    为数字添加千位分隔符。
    
    Args:
        value: 数字值
        
    Returns:
        添加千位分隔符后的字符串
    """
    if value is None:
        return ""
    
    try:
        if isinstance(value, Decimal):
            str_value = str(value)
        else:
            str_value = str(value)
        
        # 分离整数和小数部分
        if "." in str_value:
            integer_part, decimal_part = str_value.split(".")
        else:
            integer_part, decimal_part = str_value, ""
        
        # 为整数部分添加千位分隔符
        integer_with_commas = ""
        for i, char in enumerate(reversed(integer_part)):
            if i > 0 and i % 3 == 0:
                integer_with_commas = "," + integer_with_commas
            integer_with_commas = char + integer_with_commas
        
        # 组合结果
        if decimal_part:
            return f"{integer_with_commas}.{decimal_part}"
        return integer_with_commas
    except (ValueError, TypeError):
        return str(value)


# ==================== 日期时间过滤器 ====================
@register.filter
def format_date(value: Any, format_str: str = "%Y-%m-%d") -> str:
    """
    格式化日期。
    
    Args:
        value: 日期时间值
        format_str: 格式字符串
        
    Returns:
        格式化后的日期字符串
    """
    if not value:
        return ""
    
    try:
        if isinstance(value, datetime):
            dt = value
        elif isinstance(value, str):
            # 尝试解析字符串
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return str(value)
        else:
            return str(value)
        
        return format_datetime(dt, format_str)
    except (ValueError, TypeError):
        return str(value)


@register.filter
def format_time(value: Any, format_str: str = "%H:%M:%S") -> str:
    """
    格式化时间。
    
    Args:
        value: 日期时间值
        format_str: 格式字符串
        
    Returns:
        格式化后的时间字符串
    """
    if not value:
        return ""
    
    try:
        if isinstance(value, datetime):
            dt = value
        elif isinstance(value, str):
            # 尝试解析字符串
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return str(value)
        else:
            return str(value)
        
        return dt.strftime(format_str)
    except (ValueError, TypeError):
        return str(value)


@register.filter
def time_ago(value: Any) -> str:
    """
    显示相对时间（如"3天前"）。
    
    Args:
        value: 日期时间值
        
    Returns:
        相对时间字符串
    """
    if not value:
        return ""
    
    try:
        if isinstance(value, datetime):
            dt = value
        elif isinstance(value, str):
            # 尝试解析字符串
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return str(value)
        else:
            return str(value)
        
        now = timezone.now()
        diff = now - dt
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years}年前"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months}个月前"
        elif diff.days > 0:
            return f"{diff.days}天前"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}小时前"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}分钟前"
        else:
            return "刚刚"
    except (ValueError, TypeError):
        return str(value)


@register.filter
def format_duration_seconds(value: Any) -> str:
    """
    格式化持续时间（秒）。
    
    Args:
        value: 秒数
        
    Returns:
        格式化后的持续时间字符串
    """
    if value is None:
        return ""
    
    try:
        seconds = int(value)
        return format_duration(seconds)
    except (ValueError, TypeError):
        return str(value)


# ==================== 布尔值过滤器 ====================
@register.filter
def yesno(value: Any, yes_str: str = "是", no_str: str = "否") -> str:
    """
    将布尔值转换为"是/否"。
    
    Args:
        value: 布尔值
        yes_str: "是"的文本
        no_str: "否"的文本
        
    Returns:
        "是"或"否"
    """
    if value in (True, "true", "True", "1", 1):
        return yes_str
    return no_str


@register.filter
def boolean_icon(value: Any) -> str:
    """
    将布尔值转换为图标。
    
    Args:
        value: 布尔值
        
    Returns:
        HTML图标
    """
    if value in (True, "true", "True", "1", 1):
        return format_html('<span class="text-success">✓</span>')
    return format_html('<span class="text-danger">✗</span>')


# ==================== 列表处理过滤器 ====================
@register.filter
def join_list(value: list, separator: str = ", ") -> str:
    """
    将列表连接为字符串。
    
    Args:
        value: 列表
        separator: 分隔符
        
    Returns:
        连接后的字符串
    """
    if not value:
        return ""
    
    return separator.join(str(item) for item in value)


@register.filter
def list_length(value: list) -> int:
    """
    获取列表长度。
    
    Args:
        value: 列表
        
    Returns:
        列表长度
    """
    if not value:
        return 0
    
    return len(value)


@register.filter
def get_item(value: dict, key: str) -> Any:
    """
    从字典中获取项。
    
    Args:
        value: 字典
        key: 键
        
    Returns:
        字典项的值
    """
    if not value or not isinstance(value, dict):
        return ""
    
    return value.get(key, "")


# ==================== 安全过滤器 ====================
@register.filter
def safe_html(value: str) -> str:
    """
    将字符串标记为安全的HTML。
    
    Args:
        value: HTML字符串
        
    Returns:
        安全的HTML字符串
    """
    if not value:
        return ""
    
    return mark_safe(str(value))


@register.filter
def escape_html(value: str) -> str:
    """
    转义HTML特殊字符。
    
    Args:
        value: 原始字符串
        
    Returns:
        转义后的字符串
    """
    if not value:
        return ""
    
    from django.utils.html import escape
    return escape(str(value))


# ==================== 业务逻辑过滤器 ====================
@register.filter
def progress_bar(value: Any, max_value: int = 100) -> str:
    """
    生成进度条HTML。
    
    Args:
        value: 当前值
        max_value: 最大值
        
    Returns:
        进度条HTML
    """
    if value is None:
        value = 0
    
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
        
        return format_html(
            '''
            <div class="progress" style="height: 20px;">
                <div class="progress-bar {}" role="progressbar" 
                     style="width: {}%;" 
                     aria-valuenow="{}" 
                     aria-valuemin="0" 
                     aria-valuemax="{}">
                    {}%
                </div>
            </div>
            ''',
            color_class,
            percentage,
            progress,
            max_value,
            int(percentage),
        )
    except (ValueError, TypeError):
        return str(value)


@register.filter
def status_badge(value: Any, status_map: dict = None) -> str:
    """
    生成状态徽章HTML。
    
    Args:
        value: 状态值
        status_map: 状态映射字典
        
    Returns:
        状态徽章HTML
    """
    if not value:
        return ""
    
    # 默认状态映射
    default_status_map = {
        "active": ("活跃", "success"),
        "inactive": ("未激活", "secondary"),
        "pending": ("待处理", "warning"),
        "completed": ("已完成", "success"),
        "failed": ("失败", "danger"),
        "success": ("成功", "success"),
        "error": ("错误", "danger"),
        "warning": ("警告", "warning"),
        "info": ("信息", "info"),
    }
    
    status_map = status_map or default_status_map
    
    status_str = str(value).lower()
    
    if status_str in status_map:
        text, badge_class = status_map[status_str]
    else:
        text, badge_class = status_str, "secondary"
    
    return format_html(
        '<span class="badge bg-{}">{}</span>',
        badge_class,
        text,
    )
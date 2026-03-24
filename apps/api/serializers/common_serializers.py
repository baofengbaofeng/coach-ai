"""
通用API序列化器。
按照豆包AI助手最佳实践：提供类型安全的通用API序列化器。
"""
from __future__ import annotations

from typing import Any, Dict, List

from rest_framework import serializers


# ==================== 成功响应序列化器 ====================
class SuccessResponseSerializer(serializers.Serializer):
    """
    成功响应序列化器。
    """
    
    success = serializers.BooleanField(
        default=True,
        help_text="是否成功",
    )
    
    message = serializers.CharField(
        required=False,
        help_text="成功消息",
    )
    
    data = serializers.DictField(
        required=False,
        help_text="响应数据",
    )
    
    timestamp = serializers.DateTimeField(
        help_text="响应时间戳",
    )
    
    request_id = serializers.CharField(
        required=False,
        help_text="请求ID",
    )


# ==================== 错误响应序列化器 ====================
class ErrorDetailSerializer(serializers.Serializer):
    """
    错误详情序列化器。
    """
    
    field = serializers.CharField(
        required=False,
        help_text="错误字段",
    )
    
    message = serializers.CharField(
        help_text="错误消息",
    )
    
    code = serializers.CharField(
        required=False,
        help_text="错误代码",
    )


class ErrorResponseSerializer(serializers.Serializer):
    """
    错误响应序列化器。
    """
    
    success = serializers.BooleanField(
        default=False,
        help_text="是否成功",
    )
    
    error = serializers.DictField(
        help_text="错误信息",
        child=serializers.CharField(),
    )
    
    timestamp = serializers.DateTimeField(
        help_text="错误时间戳",
    )
    
    request_id = serializers.CharField(
        required=False,
        help_text="请求ID",
    )
    
    details = ErrorDetailSerializer(
        many=True,
        required=False,
        help_text="错误详情",
    )


# ==================== 分页请求序列化器 ====================
class PaginationRequestSerializer(serializers.Serializer):
    """
    分页请求序列化器。
    """
    
    page = serializers.IntegerField(
        min_value=1,
        default=1,
        help_text="页码",
    )
    
    page_size = serializers.IntegerField(
        min_value=1,
        max_value=100,
        default=20,
        help_text="每页大小",
    )


# ==================== 分页响应序列化器 ====================
class PaginationResponseSerializer(serializers.Serializer):
    """
    分页响应序列化器。
    """
    
    page = serializers.IntegerField(
        help_text="当前页码",
    )
    
    page_size = serializers.IntegerField(
        help_text="每页大小",
    )
    
    total_pages = serializers.IntegerField(
        help_text="总页数",
    )
    
    total_items = serializers.IntegerField(
        help_text="总项目数",
    )
    
    has_next = serializers.BooleanField(
        help_text="是否有下一页",
    )
    
    has_previous = serializers.BooleanField(
        help_text="是否有上一页",
    )


# ==================== 过滤请求序列化器 ====================
class FilterRequestSerializer(serializers.Serializer):
    """
    过滤请求序列化器。
    """
    
    filters = serializers.DictField(
        required=False,
        help_text="过滤条件",
    )
    
    search = serializers.CharField(
        required=False,
        help_text="搜索关键词",
    )
    
    date_from = serializers.DateField(
        required=False,
        help_text="开始日期",
    )
    
    date_to = serializers.DateField(
        required=False,
        help_text="结束日期",
    )


# ==================== 排序请求序列化器 ====================
class SortRequestSerializer(serializers.Serializer):
    """
    排序请求序列化器。
    """
    
    sort_by = serializers.CharField(
        required=False,
        help_text="排序字段",
    )
    
    sort_order = serializers.ChoiceField(
        choices=["asc", "desc"],
        default="desc",
        help_text="排序顺序",
    )


# ==================== 批量操作序列化器 ====================
class BatchOperationSerializer(serializers.Serializer):
    """
    批量操作序列化器。
    """
    
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="ID列表",
    )
    
    action = serializers.CharField(
        help_text="操作类型",
    )


# ==================== 文件上传序列化器 ====================
class FileUploadSerializer(serializers.Serializer):
    """
    文件上传序列化器。
    """
    
    file = serializers.FileField(
        help_text="上传的文件",
    )
    
    description = serializers.CharField(
        required=False,
        help_text="文件描述",
    )
    
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="文件标签",
    )


# ==================== 时间范围序列化器 ====================
class TimeRangeSerializer(serializers.Serializer):
    """
    时间范围序列化器。
    """
    
    start_time = serializers.DateTimeField(
        help_text="开始时间",
    )
    
    end_time = serializers.DateTimeField(
        help_text="结束时间",
    )


# ==================== 统计请求序列化器 ====================
class StatisticsRequestSerializer(serializers.Serializer):
    """
    统计请求序列化器。
    """
    
    period = serializers.ChoiceField(
        choices=["day", "week", "month", "year", "custom"],
        default="month",
        help_text="统计周期",
    )
    
    group_by = serializers.CharField(
        required=False,
        help_text="分组字段",
    )
    
    metrics = serializers.ListField(
        child=serializers.CharField(),
        help_text="统计指标",
    )


# ==================== 导出请求序列化器 ====================
class ExportRequestSerializer(serializers.Serializer):
    """
    导出请求序列化器。
    """
    
    format = serializers.ChoiceField(
        choices=["csv", "json", "excel", "pdf"],
        default="json",
        help_text="导出格式",
    )
    
    include_headers = serializers.BooleanField(
        default=True,
        help_text="是否包含表头",
    )
    
    filters = serializers.DictField(
        required=False,
        help_text="过滤条件",
    )


# ==================== 导入请求序列化器 ====================
class ImportRequestSerializer(serializers.Serializer):
    """
    导入请求序列化器。
    """
    
    file = serializers.FileField(
        help_text="导入文件",
    )
    
    format = serializers.ChoiceField(
        choices=["csv", "json", "excel"],
        default="json",
        help_text="文件格式",
    )
    
    overwrite = serializers.BooleanField(
        default=False,
        help_text="是否覆盖现有数据",
    )
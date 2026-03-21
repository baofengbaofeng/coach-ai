"""
通用分页模块，提供Django REST Framework的分页器类，支持标准的分页参数和响应格式。
按照豆包AI助手最佳实践和coding-style.md规范实现。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from core.constants import SystemConfig


# ==================== 日志记录器 ====================
# 模块级别的日志记录器，用于记录分页操作信息和调试信息，遵循coding-style.md规范
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 标准分页器 ====================
class StandardPagination(PageNumberPagination):
    """
    标准分页器类，提供统一的分页参数和响应格式，支持自定义页面大小和最大页面大小限制。
    
    Attributes:
        page_size (int): 默认页面大小，从系统配置中获取
        page_size_query_param (str): 页面大小查询参数名称
        max_page_size (int): 最大页面大小限制，从系统配置中获取
        page_query_param (str): 页码查询参数名称
    """
    
    page_size: int = SystemConfig.DEFAULT_PAGE_SIZE
    page_size_query_param: str = "page_size"
    max_page_size: int = SystemConfig.MAX_PAGE_SIZE
    page_query_param: str = "page"
    
    def get_paginated_response(self, data: List[Any]) -> Response:
        """
        获取分页响应，返回标准化的分页数据格式。
        
        Args:
            data (List[Any]): 当前页的数据列表
            
        Returns:
            Response: 标准化的分页响应对象，包含数据、分页元数据和成功状态
            
        Examples:
            >>> paginator = StandardPagination()
            >>> queryset = User.objects.all()
            >>> page = paginator.paginate_queryset(queryset, request)
            >>> serializer = UserSerializer(page, many=True)
            >>> return paginator.get_paginated_response(serializer.data)
        """
        return Response({
            "success": True,
            "data": data,
            "meta": {
                "pagination": {
                    "total": self.page.paginator.count,
                    "count": len(data),
                    "page": self.page.number,
                    "page_size": self.get_page_size(self.request),
                    "total_pages": self.page.paginator.num_pages,
                    "has_next": self.page.has_next(),
                    "has_previous": self.page.has_previous(),
                    "next_page_number": self.page.next_page_number() if self.page.has_next() else None,
                    "previous_page_number": self.page.previous_page_number() if self.page.has_previous() else None,
                }
            },
            "timestamp": self._get_timestamp(),
        })
    
    def _get_timestamp(self) -> str:
        """
        获取当前时间戳，格式化为ISO 8601标准格式。
        
        Returns:
            str: ISO 8601格式的时间戳字符串
        """
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    def get_page_size(self, request: Any) -> int:
        """
        获取页面大小，支持通过查询参数动态调整，但不超过最大限制。
        
        Args:
            request (Any): Django请求对象
            
        Returns:
            int: 页面大小，介于1和最大页面大小之间
            
        Raises:
            此方法不直接抛出异常，但会记录无效的页面大小参数
        """
        page_size: Optional[str] = request.query_params.get(self.page_size_query_param)
        
        if page_size:
            try:
                page_size_int: int = int(page_size)
                if page_size_int < 1:
                    _LOGGER.warning("无效的页面大小: %s, 使用默认值", page_size)
                    return self.page_size
                if page_size_int > self.max_page_size:
                    _LOGGER.warning("页面大小超过限制: %s > %s, 使用最大值", page_size_int, self.max_page_size)
                    return self.max_page_size
                return page_size_int
            except (ValueError, TypeError):
                _LOGGER.warning("无效的页面大小参数: %s, 使用默认值", page_size)
        
        return self.page_size


# ==================== 游标分页器 ====================
class CursorPagination(PageNumberPagination):
    """
    游标分页器类，基于游标的分页方式，适用于需要保持顺序和避免重复数据的大型数据集。
    
    Attributes:
        page_size (int): 默认页面大小
        cursor_query_param (str): 游标查询参数名称
        ordering (str): 排序字段，默认为"-created_at"（按创建时间倒序）
    """
    
    page_size: int = SystemConfig.DEFAULT_PAGE_SIZE
    cursor_query_param: str = "cursor"
    ordering: str = "-created_at"
    
    def get_paginated_response(self, data: List[Any]) -> Response:
        """
        获取游标分页响应，返回包含游标的分页数据格式。
        
        Args:
            data (List[Any]): 当前页的数据列表
            
        Returns:
            Response: 标准化的游标分页响应对象
        """
        return Response({
            "success": True,
            "data": data,
            "meta": {
                "pagination": {
                    "next_cursor": self.get_next_cursor(),
                    "previous_cursor": self.get_previous_cursor(),
                    "has_next": self.has_next,
                    "has_previous": self.has_previous,
                    "count": len(data),
                }
            },
            "timestamp": self._get_timestamp(),
        })
    
    def _get_timestamp(self) -> str:
        """
        获取当前时间戳。
        """
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    def get_next_cursor(self) -> Optional[str]:
        """
        获取下一个游标。
        
        Returns:
            Optional[str]: 下一个游标值，如果没有下一页则返回None
        """
        if self.has_next:
            return self.get_next_link()
        return None
    
    def get_previous_cursor(self) -> Optional[str]:
        """
        获取上一个游标。
        
        Returns:
            Optional[str]: 上一个游标值，如果没有上一页则返回None
        """
        if self.has_previous:
            return self.get_previous_link()
        return None


# ==================== 无限滚动分页器 ====================
class InfiniteScrollPagination(PageNumberPagination):
    """
    无限滚动分页器类，适用于前端无限滚动加载的场景，简化分页参数。
    
    Attributes:
        page_size (int): 默认页面大小
        page_query_param (str): 页码查询参数名称
        has_more_field (str): 是否有更多数据的字段名称
    """
    
    page_size: int = SystemConfig.DEFAULT_PAGE_SIZE
    page_query_param: str = "page"
    has_more_field: str = "has_more"
    
    def get_paginated_response(self, data: List[Any]) -> Response:
        """
        获取无限滚动分页响应，返回简化的分页数据格式。
        
        Args:
            data (List[Any]): 当前页的数据列表
            
        Returns:
            Response: 标准化的无限滚动分页响应对象
        """
        has_more: bool = self.page.has_next()
        
        return Response({
            "success": True,
            "data": data,
            "meta": {
                "pagination": {
                    self.has_more_field: has_more,
                    "next_page": self.page.next_page_number() if has_more else None,
                    "count": len(data),
                }
            },
            "timestamp": self._get_timestamp(),
        })
    
    def _get_timestamp(self) -> str:
        """
        获取当前时间戳。
        """
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


# ==================== 便捷分页函数 ====================
def get_pagination_params(request: Any) -> Dict[str, Any]:
    """
    从请求中获取分页参数，提供统一的参数解析接口。
    
    Args:
        request (Any): Django请求对象
        
    Returns:
        Dict[str, Any]: 分页参数字典，包含page和page_size字段
    """
    page: int = 1
    page_size: int = SystemConfig.DEFAULT_PAGE_SIZE
    
    try:
        page_param: Optional[str] = request.query_params.get("page")
        if page_param:
            page = int(page_param)
            if page < 1:
                page = 1
    except (ValueError, TypeError):
        _LOGGER.warning("无效的页码参数: %s, 使用默认值1", request.query_params.get("page"))
    
    try:
        page_size_param: Optional[str] = request.query_params.get("page_size")
        if page_size_param:
            page_size = int(page_size_param)
            if page_size < 1:
                page_size = SystemConfig.DEFAULT_PAGE_SIZE
            if page_size > SystemConfig.MAX_PAGE_SIZE:
                page_size = SystemConfig.MAX_PAGE_SIZE
    except (ValueError, TypeError):
        _LOGGER.warning("无效的页面大小参数: %s, 使用默认值", request.query_params.get("page_size"))
    
    return {
        "page": page,
        "page_size": page_size,
    }


# ==================== 导出定义 ====================
__all__: list[str] = [
    "StandardPagination",
    "CursorPagination",
    "InfiniteScrollPagination",
    "get_pagination_params",
]
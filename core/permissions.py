"""
项目全局权限类定义文件，包含自定义的权限检查逻辑。
按照豆包AI助手最佳实践：自定义权限放在 core/permissions.py 中。
"""
from __future__ import annotations

import logging
from typing import Any

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.accounts.models import User
from core.constants import UserRole


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 基础权限类 ====================
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    对象所有者或只读权限类。
    允许对象所有者进行修改，其他用户只能读取。
    """
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """检查对特定对象的权限。"""
        # 安全方法（GET、HEAD、OPTIONS）允许所有用户
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 检查对象是否有 owner 属性
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        
        # 检查对象是否有 user 属性
        if hasattr(obj, "user"):
            return obj.user == request.user
        
        # 检查对象是否有 student 属性（作业等）
        if hasattr(obj, "student"):
            return obj.student == request.user
        
        # 检查对象是否有 created_by 属性
        if hasattr(obj, "created_by"):
            return obj.created_by == request.user
        
        # 默认情况下，只允许超级用户修改
        return request.user.is_superuser


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    教师或管理员权限类。
    只允许教师角色或管理员进行访问。
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """检查视图级别的权限。"""
        # 未认证用户不允许访问
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 检查用户角色
        user: User = request.user
        return user.role in [UserRole.TEACHER, UserRole.ADMIN] or user.is_superuser
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """检查对特定对象的权限。"""
        return self.has_permission(request, view)


class IsStudentOrParent(permissions.BasePermission):
    """
    学生或家长权限类。
    只允许学生或家长角色进行访问。
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """检查视图级别的权限。"""
        # 未认证用户不允许访问
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 检查用户角色
        user: User = request.user
        return user.role in [UserRole.STUDENT, UserRole.PARENT]
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """检查对特定对象的权限。"""
        return self.has_permission(request, view)


class IsStudentOnly(permissions.BasePermission):
    """
    仅学生权限类。
    只允许学生角色进行访问。
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """检查视图级别的权限。"""
        # 未认证用户不允许访问
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 检查用户角色
        user: User = request.user
        return user.role == UserRole.STUDENT
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """检查对特定对象的权限。"""
        return self.has_permission(request, view)


class IsParentOnly(permissions.BasePermission):
    """
    仅家长权限类。
    只允许家长角色进行访问。
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """检查视图级别的权限。"""
        # 未认证用户不允许访问
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 检查用户角色
        user: User = request.user
        return user.role == UserRole.PARENT
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """检查对特定对象的权限。"""
        return self.has_permission(request, view)


class IsAdminOnly(permissions.BasePermission):
    """
    仅管理员权限类。
    只允许管理员角色进行访问。
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """检查视图级别的权限。"""
        # 未认证用户不允许访问
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 检查用户角色
        user: User = request.user
        return user.role == UserRole.ADMIN or user.is_superuser
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """检查对特定对象的权限。"""
        return self.has_permission(request, view)


# ==================== 组合权限类 ====================
class IsOwnerOrTeacherOrAdmin(permissions.BasePermission):
    """
    所有者或教师或管理员权限类。
    允许对象所有者、教师或管理员进行访问。
    """
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """检查对特定对象的权限。"""
        # 安全方法（GET、HEAD、OPTIONS）允许所有认证用户
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # 检查用户角色
        user: User = request.user
        if not user or not user.is_authenticated:
            return False
        
        # 教师或管理员有完全权限
        if user.role in [UserRole.TEACHER, UserRole.ADMIN] or user.is_superuser:
            return True
        
        # 检查对象所有权
        if hasattr(obj, "student"):
            return obj.student == user
        if hasattr(obj, "owner"):
            return obj.owner == user
        if hasattr(obj, "user"):
            return obj.user == user
        if hasattr(obj, "created_by"):
            return obj.created_by == user
        
        return False


class IsStudentOrTeacherOrAdmin(permissions.BasePermission):
    """
    学生或教师或管理员权限类。
    允许学生、教师或管理员进行访问。
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """检查视图级别的权限。"""
        # 未认证用户不允许访问
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 检查用户角色
        user: User = request.user
        return user.role in [
            UserRole.STUDENT,
            UserRole.TEACHER,
            UserRole.ADMIN,
        ] or user.is_superuser
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """检查对特定对象的权限。"""
        return self.has_permission(request, view)


# ==================== 功能特定权限类 ====================
class CanViewHomework(permissions.BasePermission):
    """
    查看作业权限类。
    控制谁可以查看作业。
    """
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """检查对作业对象的权限。"""
        from apps.homework.models import Homework
        
        if not isinstance(obj, Homework):
            return False
        
        user: User = request.user
        if not user or not user.is_authenticated:
            return False
        
        # 作业所有者可以查看
        if obj.student == user:
            return True
        
        # 教师、家长、管理员可以查看
        if user.role in [UserRole.TEACHER, UserRole.PARENT, UserRole.ADMIN]:
            return True
        
        # 超级用户可以查看
        if user.is_superuser:
            return True
        
        return False


class CanCorrectHomework(permissions.BasePermission):
    """
    批改作业权限类。
    控制谁可以批改作业。
    """
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """检查对作业对象的批改权限。"""
        from apps.homework.models import Homework
        
        if not isinstance(obj, Homework):
            return False
        
        user: User = request.user
        if not user or not user.is_authenticated:
            return False
        
        # 只有教师和管理员可以批改作业
        return user.role in [UserRole.TEACHER, UserRole.ADMIN] or user.is_superuser


class CanProcessHomework(permissions.BasePermission):
    """
    处理作业权限类。
    控制谁可以触发作业处理（OCR识别等）。
    """
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """检查对作业对象的处理权限。"""
        from apps.homework.models import Homework
        
        if not isinstance(obj, Homework):
            return False
        
        user: User = request.user
        if not user or not user.is_authenticated:
            return False
        
        # 作业所有者可以触发处理
        if obj.student == user:
            return True
        
        # 教师和管理员可以触发处理
        if user.role in [UserRole.TEACHER, UserRole.ADMIN]:
            return True
        
        # 超级用户可以触发处理
        if user.is_superuser:
            return True
        
        return False


# ==================== 工具函数 ====================
def check_user_role(user: User, allowed_roles: list[str]) -> bool:
    """
    检查用户角色是否在允许的角色列表中。
    
    Args:
        user: 要检查的用户对象
        allowed_roles: 允许的角色列表
    
    Returns:
        如果用户角色在允许列表中返回True，否则返回False
    """
    if not user or not user.is_authenticated:
        return False
    
    return user.role in allowed_roles or user.is_superuser


def is_object_owner(user: User, obj: Any) -> bool:
    """
    检查用户是否是对象的所有者。
    
    Args:
        user: 要检查的用户对象
        obj: 要检查的对象
    
    Returns:
        如果用户是对象所有者返回True，否则返回False
    """
    if not user or not user.is_authenticated:
        return False
    
    # 检查各种可能的所有者属性
    owner_attributes = ["student", "owner", "user", "created_by", "author"]
    
    for attr in owner_attributes:
        if hasattr(obj, attr):
            owner = getattr(obj, attr)
            if owner == user:
                return True
    
    return False
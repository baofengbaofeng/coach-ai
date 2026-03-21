"""
用户管理序列化器模块，定义API请求和响应的数据格式验证和转换规则。
按照豆包AI助手最佳实践：序列化器负责参数校验，业务逻辑写在services.py。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from core.constants import BusinessRules, RegexPatterns, UserRole
from core.utils import validate_email, validate_phone, validate_password_strength

from .models import FamilyRelationship, LoginHistory, User, UserProfile


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 基础序列化器 ====================
class BaseUserSerializer(serializers.ModelSerializer):
    """
    基础用户序列化器，提供用户数据的通用验证和转换功能。
    """
    
    class Meta:
        """
        基础用户序列化器的元数据配置。
        """
        model = User
        fields: List[str] = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "bio",
            "role",
            "points",
            "level",
            "date_joined",
        ]
        read_only_fields: List[str] = [
            "id",
            "points",
            "level",
            "date_joined",
        ]
    
    def validate_username(self, value: str) -> str:
        """
        验证用户名格式和唯一性。
        
        Args:
            value (str): 用户名
            
        Returns:
            str: 验证后的用户名
            
        Raises:
            serializers.ValidationError: 当用户名格式不正确或已存在时抛出此异常
        """
        # 检查用户名长度
        if len(value) < BusinessRules.USERNAME_MIN_LENGTH:
            raise serializers.ValidationError(
                f"用户名长度至少为{BusinessRules.USERNAME_MIN_LENGTH}个字符"
            )
        
        if len(value) > BusinessRules.USERNAME_MAX_LENGTH:
            raise serializers.ValidationError(
                f"用户名长度不能超过{BusinessRules.USERNAME_MAX_LENGTH}个字符"
            )
        
        # 检查用户名格式（字母、数字、下划线）
        import re
        if not re.match(RegexPatterns.USERNAME, value):
            raise serializers.ValidationError(
                "用户名只能包含字母、数字和下划线"
            )
        
        return value
    
    def validate_email(self, value: str) -> str:
        """
        验证邮箱地址格式和唯一性。
        
        Args:
            value (str): 邮箱地址
            
        Returns:
            str: 验证后的邮箱地址
            
        Raises:
            serializers.ValidationError: 当邮箱格式不正确或已存在时抛出此异常
        """
        # 检查邮箱格式
        if not validate_email(value):
            raise serializers.ValidationError("请输入有效的邮箱地址")
        
        # 检查邮箱长度
        if len(value) > BusinessRules.EMAIL_MAX_LENGTH:
            raise serializers.ValidationError(
                f"邮箱地址长度不能超过{BusinessRules.EMAIL_MAX_LENGTH}个字符"
            )
        
        return value.lower()  # 统一转换为小写
    
    def validate_phone(self, value: Optional[str]) -> Optional[str]:
        """
        验证手机号格式和唯一性。
        
        Args:
            value (Optional[str]): 手机号
            
        Returns:
            Optional[str]: 验证后的手机号，如果为None则返回None
            
        Raises:
            serializers.ValidationError: 当手机号格式不正确或已存在时抛出此异常
        """
        if not value:
            return None
        
        # 检查手机号格式
        if not validate_phone(value):
            raise serializers.ValidationError("请输入有效的中国手机号")
        
        return value


# ==================== 用户注册序列化器 ====================
class UserRegisterSerializer(BaseUserSerializer):
    """
    用户注册序列化器，处理用户注册时的数据验证和用户创建。
    """
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        min_length=BusinessRules.PASSWORD_MIN_LENGTH,
        max_length=BusinessRules.PASSWORD_MAX_LENGTH,
        help_text="用户密码，长度8-128个字符，必须包含大小写字母、数字和特殊字符",
    )
    
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        help_text="确认密码，必须与密码字段一致",
    )
    
    class Meta(BaseUserSerializer.Meta):
        """
        用户注册序列化器的元数据配置。
        """
        fields = BaseUserSerializer.Meta.fields + [
            "password",
            "password_confirm",
            "phone",
            "date_of_birth",
        ]
        read_only_fields = BaseUserSerializer.Meta.read_only_fields
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证注册数据的完整性和一致性。
        
        Args:
            attrs (Dict[str, Any]): 注册数据字典
            
        Returns:
            Dict[str, Any]: 验证后的注册数据字典
            
        Raises:
            serializers.ValidationError: 当数据验证失败时抛出此异常
        """
        # 验证密码和确认密码是否一致
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")
        
        if password != password_confirm:
            raise serializers.ValidationError({
                "password_confirm": "两次输入的密码不一致"
            })
        
        # 验证密码强度
        is_valid, errors = validate_password_strength(password)
        if not is_valid:
            raise serializers.ValidationError({
                "password": errors
            })
        
        # 验证Django密码策略
        try:
            validate_password(password)
        except DjangoValidationError as e:
            raise serializers.ValidationError({
                "password": list(e.messages)
            })
        
        # 移除确认密码字段，不在数据库中保存
        attrs.pop("password_confirm", None)
        
        return attrs
    
    def create(self, validated_data: Dict[str, Any]) -> User:
        """
        创建用户实例并保存到数据库。
        
        Args:
            validated_data (Dict[str, Any]): 验证后的用户数据
            
        Returns:
            User: 创建的用户对象
            
        Raises:
            serializers.ValidationError: 当用户创建失败时抛出此异常
        """
        try:
            # 创建用户
            user = User.objects.create_user(
                username=validated_data["username"],
                email=validated_data["email"],
                password=validated_data["password"],
                phone=validated_data.get("phone"),
                first_name=validated_data.get("first_name", ""),
                last_name=validated_data.get("last_name", ""),
                role=validated_data.get("role", UserRole.STUDENT),
                date_of_birth=validated_data.get("date_of_birth"),
            )
            
            # 创建用户资料
            UserProfile.objects.create(user=user)
            
            _LOGGER.info("用户注册成功: %s (%s)", user.username, user.email)
            return user
            
        except Exception as e:
            _LOGGER.error("用户注册失败: %s", str(e))
            raise serializers.ValidationError({
                "non_field_errors": [f"用户注册失败: {str(e)}"]
            })


# ==================== 用户登录序列化器 ====================
class UserLoginSerializer(serializers.Serializer):
    """
    用户登录序列化器，处理用户登录认证和令牌生成。
    """
    
    username = serializers.CharField(
        required=True,
        help_text="用户名或邮箱地址",
    )
    
    password = serializers.CharField(
        required=True,
        style={"input_type": "password"},
        write_only=True,
        help_text="用户密码",
    )
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证用户登录凭证并生成访问令牌。
        
        Args:
            attrs (Dict[str, Any]): 登录数据字典
            
        Returns:
            Dict[str, Any]: 包含用户和令牌的验证数据字典
            
        Raises:
            serializers.ValidationError: 当登录认证失败时抛出此异常
        """
        username = attrs.get("username")
        password = attrs.get("password")
        
        # 尝试认证用户
        user = authenticate(
            request=self.context.get("request"),
            username=username,
            password=password,
        )
        
        if not user:
            _LOGGER.warning("登录失败: 用户名或密码错误 - %s", username)
            raise serializers.ValidationError({
                "non_field_errors": ["用户名或密码错误"]
            })
        
        if not user.is_active:
            _LOGGER.warning("登录失败: 用户账户已禁用 - %s", username)
            raise serializers.ValidationError({
                "non_field_errors": ["用户账户已禁用"]
            })
        
        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)
        
        # 更新登录信息
        request = self.context.get("request")
        if request:
            user.update_login_info(
                ip_address=self._get_client_ip(request),
                device_info=request.META.get("HTTP_USER_AGENT", ""),
            )
        
        _LOGGER.info("用户登录成功: %s", user.username)
        
        return {
            "user": user,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    
    def _get_client_ip(self, request: Any) -> str:
        """
        获取客户端IP地址。
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "unknown")
        return ip


# ==================== 用户详情序列化器 ====================
class UserDetailSerializer(BaseUserSerializer):
    """
    用户详情序列化器，提供完整的用户信息展示。
    """
    
    age = serializers.IntegerField(
        read_only=True,
        help_text="用户年龄（基于出生日期计算）",
    )
    
    full_name = serializers.CharField(
        read_only=True,
        help_text="用户全名",
    )
    
    profile = serializers.SerializerMethodField(
        help_text="用户扩展资料",
    )
    
    class Meta(BaseUserSerializer.Meta):
        """
        用户详情序列化器的元数据配置。
        """
        fields = BaseUserSerializer.Meta.fields + [
            "phone",
            "date_of_birth",
            "age",
            "full_name",
            "profile",
            "email_verified",
            "phone_verified",
            "last_login",
            "last_login_ip",
        ]
        read_only_fields = BaseUserSerializer.Meta.read_only_fields + [
            "age",
            "full_name",
            "profile",
            "email_verified",
            "phone_verified",
            "last_login",
            "last_login_ip",
        ]
    
    def get_profile(self, obj: User) -> Dict[str, Any]:
        """
        获取用户扩展资料。
        
        Args:
            obj (User): 用户对象
            
        Returns:
            Dict[str, Any]: 用户资料字典
        """
        try:
            profile = obj.profile
            return {
                "total_study_time": profile.total_study_time,
                "total_homework_count": profile.total_homework_count,
                "total_exercise_count": profile.total_exercise_count,
                "achievements_unlocked": profile.achievements_unlocked,
                "followers_count": profile.followers_count,
                "following_count": profile.following_count,
            }
        except UserProfile.DoesNotExist:
            return {}


# ==================== 用户更新序列化器 ====================
class UserUpdateSerializer(BaseUserSerializer):
    """
    用户更新序列化器，处理用户个人资料的更新。
    """
    
    current_password = serializers.CharField(
        write_only=True,
        required=False,
        style={"input_type": "password"},
        help_text="当前密码（修改敏感信息时需要）",
    )
    
    new_password = serializers.CharField(
        write_only=True,
        required=False,
        style={"input_type": "password"},
        min_length=BusinessRules.PASSWORD_MIN_LENGTH,
        max_length=BusinessRules.PASSWORD_MAX_LENGTH,
        help_text="新密码（修改密码时需要）",
    )
    
    class Meta(BaseUserSerializer.Meta):
        """
        用户更新序列化器的元数据配置。
        """
        fields = BaseUserSerializer.Meta.fields + [
            "phone",
            "date_of_birth",
            "current_password",
            "new_password",
            "notification_preferences",
            "privacy_settings",
        ]
        read_only_fields = BaseUserSerializer.Meta.read_only_fields + [
            "role",  # 角色不能通过普通更新修改
        ]
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证更新数据的完整性和安全性。
        
        Args:
            attrs (Dict[str, Any]): 更新数据字典
            
        Returns:
            Dict[str, Any]: 验证后的更新数据字典
            
        Raises:
            serializers.ValidationError: 当数据验证失败时抛出此异常
        """
        user = self.instance
        current_password = attrs.get("current_password")
        new_password = attrs.get("new_password")
        
        # 如果尝试修改密码，需要验证当前密码
        if new_password:
            if not current_password:
                raise serializers.ValidationError({
                    "current_password": "修改密码需要提供当前密码"
                })
            
            if not user.check_password(current_password):
                raise serializers.ValidationError({
                    "current_password": "当前密码不正确"
                })
            
            # 验证新密码强度
            is_valid, errors = validate_password_strength(new_password)
            if not is_valid:
                raise serializers.ValidationError({
                    "new_password": errors
                })
            
            # 验证Django密码策略
            try:
                validate_password(new_password, user=user)
            except DjangoValidationError as e:
                raise serializers.ValidationError({
                    "new_password": list(e.messages)
                })
            
            # 设置新密码
            user.set_password(new_password)
            attrs.pop("current_password")
            attrs.pop("new_password")
            attrs["password"] = user.password
        
        # 移除当前密码字段（如果存在且没有新密码）
        elif current_password:
            attrs.pop("current_password")
        
        return attrs
    
    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        """
        更新用户实例。
        
        Args:
            instance (User): 要更新的用户对象
            validated_data (Dict[str, Any]): 验证后的更新数据
            
        Returns:
            User: 更新后的用户对象
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        _LOGGER.info("用户资料更新成功: %s", instance.username)
        return instance


# ==================== 家庭关系序列化器 ====================
class FamilyRelationshipSerializer(serializers.ModelSerializer):
    """
    家庭关系序列化器，处理家长和学生关系的创建和展示。
    """
    
    parent_username = serializers.CharField(
        source="parent.username",
        read_only=True,
        help_text="家长用户名",
    )
    
    parent_email = serializers.EmailField(
        source="parent.email",
        read_only=True,
        help_text="家长邮箱",
    )
    
    student_username = serializers.CharField(
        source="student.username",
        read_only=True,
        help_text="学生用户名",
    )
    
    student_email = serializers.EmailField(
        source="student.email",
        read_only=True,
        help_text="学生邮箱",
    )
    
    class Meta:
        """
        家庭关系序列化器的元数据配置。
        """
        model = FamilyRelationship
        fields: List[str] = [
            "id",
            "parent",
            "parent_username",
            "parent_email",
            "student",
            "student_username",
            "student_email",
            "relationship",
            "is_primary",
            "can_view_progress",
            "can_set_tasks",
            "created_at",
            "updated_at",
        ]
        read_only_fields: List[str] = [
            "id",
            "parent_username",
            "parent_email",
            "student_username",
            "student_email",
            "created_at",
            "updated_at",
        ]
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证家庭关系数据的有效性。
        
        Args:
            attrs (Dict[str, Any]): 家庭关系数据字典
            
        Returns:
            Dict[str, Any]: 验证后的家庭关系数据字典
            
        Raises:
            serializers.ValidationError: 当数据验证失败时抛出此异常
        """
        parent = attrs.get("parent")
        student = attrs.get("student")
        
        # 验证家长角色
        if parent.role != UserRole.PARENT:
            raise serializers.ValidationError({
                "parent": "家长用户角色必须为'家长'"
            })
        
        # 验证学生角色
        if student.role != UserRole.STUDENT:
            raise serializers.ValidationError({
                "student": "学生用户角色必须为'学生'"
            })
        
        # 验证不能建立自我关系
        if parent == student:
            raise serializers.ValidationError({
                "non_field_errors": "不能建立自己与自己的家庭关系"
            })
        
        return attrs


# ==================== 登录历史序列化器 ====================
class LoginHistorySerializer(serializers.ModelSerializer):
    """
    登录历史序列
"""
用户管理数据模型模块，定义用户、角色、权限等核心数据结构和关系。
按照豆包AI助手最佳实践：使用Django的AbstractUser扩展自定义用户模型。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import EmailValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.constants import BusinessRules, RegexPatterns, UserRole


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 自定义用户管理器 ====================
class UserManager(BaseUserManager):
    """
    自定义用户管理器类。
    """
    
    def create_user(
        self,
        username: str,
        email: str,
        password: Optional[str] = None,
        **extra_fields: Any,
    ) -> "User":
        """
        创建普通用户。
        """
        if not username:
            raise ValueError("用户名不能为空")
        if not email:
            raise ValueError("邮箱不能为空")
        
        email = self.normalize_email(email)
        user: User = self.model(username=username, email=email, **extra_fields)
        
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        
        user.save(using=self._db)
        _LOGGER.info("用户创建成功: %s (%s)", username, email)
        return user
    
    def create_superuser(
        self,
        username: str,
        email: str,
        password: Optional[str] = None,
        **extra_fields: Any,
    ) -> "User":
        """
        创建超级管理员。
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", UserRole.ADMIN)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError("超级管理员必须设置 is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("超级管理员必须设置 is_superuser=True")
        
        return self.create_user(username, email, password, **extra_fields)


# ==================== 用户模型 ====================
class User(AbstractUser):
    """
    自定义用户模型类。
    """
    
    # 用户名字段
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("用户名"),
        max_length=BusinessRules.USERNAME_MAX_LENGTH,
        unique=True,
        help_text=_("必填。{min_length}到{max_length}个字符。".format(
            min_length=BusinessRules.USERNAME_MIN_LENGTH,
            max_length=BusinessRules.USERNAME_MAX_LENGTH,
        )),
        validators=[username_validator],
        error_messages={"unique": _("该用户名已被使用。")},
    )
    
    # 邮箱字段
    email = models.EmailField(
        _("邮箱地址"),
        max_length=BusinessRules.EMAIL_MAX_LENGTH,
        unique=True,
        help_text=_("必填。请输入有效的邮箱地址。"),
        validators=[EmailValidator()],
        error_messages={"unique": _("该邮箱已被注册。")},
    )
    
    # 手机号字段
    phone = models.CharField(
        _("手机号"),
        max_length=11,
        blank=True,
        null=True,
        unique=True,
        help_text=_("请输入11位中国手机号。"),
        validators=[RegexValidator(regex=RegexPatterns.PHONE)],
        error_messages={"unique": _("该手机号已被注册。")},
    )
    
    # 用户角色字段
    ROLE_CHOICES = [
        (UserRole.STUDENT, "学生"),
        (UserRole.PARENT, "家长"),
        (UserRole.TEACHER, "老师"),
        (UserRole.ADMIN, "管理员"),
    ]
    
    role = models.CharField(
        _("用户角色"),
        max_length=20,
        choices=ROLE_CHOICES,
        default=UserRole.STUDENT,
        help_text=_("用户的角色，决定可访问的功能和权限。"),
    )
    
    # 个人资料字段
    avatar = models.ImageField(
        _("头像"),
        upload_to="avatars/%Y/%m/%d/",
        blank=True,
        null=True,
        help_text=_("用户头像图片，建议尺寸200x200像素。"),
    )
    
    bio = models.TextField(
        _("个人简介"),
        max_length=500,
        blank=True,
        help_text=_("简短的个人介绍，最多500个字符。"),
    )
    
    date_of_birth = models.DateField(
        _("出生日期"),
        blank=True,
        null=True,
        help_text=_("用户的出生日期，格式：YYYY-MM-DD。"),
    )
    
    # 积分和等级字段
    points = models.PositiveIntegerField(
        _("积分"),
        default=0,
        help_text=_("用户通过完成任务和活动获得的积分。"),
    )
    
    level = models.PositiveIntegerField(
        _("等级"),
        default=1,
        help_text=_("用户等级，基于积分自动计算。"),
    )
    
    # 登录和安全字段
    last_login_ip = models.GenericIPAddressField(
        _("最后登录IP"),
        blank=True,
        null=True,
        help_text=_("用户最后一次登录的IP地址。"),
    )
    
    last_login_device = models.CharField(
        _("最后登录设备"),
        max_length=200,
        blank=True,
        null=True,
        help_text=_("用户最后一次登录的设备信息。"),
    )
    
    # 验证状态字段
    email_verified = models.BooleanField(
        _("邮箱已验证"),
        default=False,
        help_text=_("标识用户的邮箱地址是否已经过验证。"),
    )
    
    phone_verified = models.BooleanField(
        _("手机号已验证"),
        default=False,
        help_text=_("标识用户的手机号是否已经过验证。"),
    )
    
    # 偏好设置字段
    notification_preferences = models.JSONField(
        _("通知偏好"),
        default=dict,
        help_text=_("用户的通知偏好设置，JSON格式。"),
    )
    
    privacy_settings = models.JSONField(
        _("隐私设置"),
        default=dict,
        help_text=_("用户的隐私设置，JSON格式。"),
    )
    
    # 时间戳字段
    date_joined = models.DateTimeField(_("注册时间"), default=timezone.now)
    last_login = models.DateTimeField(_("最后登录时间"), blank=True, null=True)
    
    # ==================== 元数据配置 ====================
    class Meta:
        """
        用户模型的元数据配置。
        """
        verbose_name = _("用户")
        verbose_name_plural = _("用户")
        db_table = "accounts_user"
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["role"]),
            models.Index(fields=["points"]),
            models.Index(fields=["date_joined"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(points__gte=0),
                name="points_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(level__gte=1),
                name="level_at_least_one",
            ),
        ]
    
    # ==================== 管理器配置 ====================
    objects = UserManager()
    
    # ==================== 属性方法 ====================
    @property
    def full_name(self) -> str:
        """
        获取用户全名。
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def is_student(self) -> bool:
        """
        检查用户是否为学生角色。
        """
        return self.role == UserRole.STUDENT
    
    @property
    def is_parent(self) -> bool:
        """
        检查用户是否为家长角色。
        """
        return self.role == UserRole.PARENT
    
    @property
    def is_teacher(self) -> bool:
        """
        检查用户是否为老师角色。
        """
        return self.role == UserRole.TEACHER
    
    @property
    def is_admin(self) -> bool:
        """
        检查用户是否为管理员角色。
        """
        return self.role == UserRole.ADMIN
    
    @property
    def age(self) -> Optional[int]:
        """
        计算用户年龄。
        """
        if not self.date_of_birth:
            return None
        
        today = timezone.now().date()
        age = today.year - self.date_of_birth.year
        
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        
        return age
    
    # ==================== 业务方法 ====================
    def add_points(self, points: int, reason: str = "") -> None:
        """
        为用户添加积分。
        """
        if points < 0:
            raise ValueError("积分必须为正数")
        
        old_points = self.points
        self.points += points
        old_level = self.level
        self.level = (self.points // 1000) + 1
        
        self.save(update_fields=["points", "level"])
        
        _LOGGER.info(
            "用户积分更新: %s, 旧积分: %d, 新积分: %d, 旧等级: %d, 新等级: %d, 原因: %s",
            self.username,
            old_points,
            self.points,
            old_level,
            self.level,
            reason,
        )
    
    def verify_email(self) -> None:
        """
        验证用户邮箱地址。
        """
        if not self.email_verified:
            self.email_verified = True
            self.save(update_fields=["email_verified"])
            _LOGGER.info("邮箱验证成功: %s (%s)", self.username, self.email)
    
    def verify_phone(self) -> None:
        """
        验证用户手机号。
        """
        if not self.phone_verified:
            self.phone_verified = True
            self.save(update_fields=["phone_verified"])
            _LOGGER.info("手机号验证成功: %s (%s)", self.username, self.phone)
    
    def update_login_info(self, ip_address: str, device_info: str) -> None:
        """
        更新用户登录信息。
        """
        self.last_login_ip = ip_address
        self.last_login_device = device_info
        self.last_login = timezone.now()
        
        self.save(update_fields=["last_login_ip", "last_login_device", "last_login"])
        
        _LOGGER.info(
            "用户登录信息更新: %s, IP: %s, 设备: %s",
            self.username,
            ip_address,
            device_info,
        )
    
    # ==================== 字符串表示 ====================
    def __str__(self) -> str:
        """
        返回用户的字符串表示。
        """
        return f"{self.username} ({self.email})"


# ==================== 用户资料模型 ====================
class UserProfile(models.Model):
    """
    用户扩展资料模型。
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("用户"),
    )
    
    # 学习统计
    total_study_time = models.PositiveIntegerField(
        _("总学习时间"),
        default=0,
        help_text=_("用户总学习时间（分钟）。"),
    )
    
    total_homework_count = models.PositiveIntegerField(
        _("总作业数"),
        default=0,
        help_text=_("用户完成的作业总数。"),
    )
    
    total_exercise_count = models.PositiveIntegerField(
        _("总运动次数"),
        default=0,
        help_text=_("用户完成的运动次数。"),
    )
    
    # 成就统计
    achievements_unlocked = models.PositiveIntegerField(
        _("已解锁成就数"),
        default=0,
        help_text=_("用户已解锁的成就数量。"),
    )
    
    # 社交统计
    followers_count = models.PositiveIntegerField(
        _("粉丝数"),
        default=0,
        help_text=_("关注该用户的用户数量。"),
    )
    
    following_count = models.PositiveIntegerField(
        _("关注数"),
        default=0,
        help_text=_("该用户关注的用户数量。"),
    )
    
    # 元数据
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)
    
    class Meta:
        """
        用户资料模型的元数据配置。
        """
        verbose_name = _("用户资料")
        verbose_name_plural = _("用户资料")
        db_table = "accounts_user_profile"
    
    def __str__(self) -> str:
        """
        返回用户资料的字符串表示。
        """
        return f"{self.user.username} 的资料"


# ==================== 家庭关系模型 ====================
class FamilyRelationship(models.Model):
    """
    家庭关系模型，用于管理家长和学生之间的关系。
    """
    
    parent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="children_relationships",
        verbose_name=_("家长"),
        limit_choices_to={"role": UserRole.PARENT},
    )
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="parent_relationships",
        verbose_name=_("学生"),
        limit_choices_to={"role": UserRole.STUDENT},
    )
    
    RELATIONSHIP_CHOICES = [
        ("father", "父亲"),
        ("mother", "母亲"),
        ("guardian", "监护人"),
        ("other", "其他"),
    ]
    
    relationship = models.CharField(
        _("关系类型"),
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        default="parent",
        help_text=_("家长与学生的关系类型。"),
    )
    
    is_primary = models.BooleanField(
        _("主要监护人"),
        default=False,
        help_text=_("标识是否为学生的主要监护人。"),
    )
    
    can_view_progress = models.BooleanField(
        _("可查看学习进度"),
        default=True,
        help_text=_("家长是否可以查看学生的学习进度。"),
    )
    
    can_set_tasks = models.BooleanField(
        _("可设置任务"),
        default=True,
        help_text=_("家长是否可以给学生设置任务。"),
    )
    
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)
    
    class Meta:
        """
        家庭关系模型的元数据配置。
        """
        verbose_name = _("家庭关系")
        verbose_name_plural = _("家庭关系")
        db_table = "accounts_family_relationship"
        unique_together = [["parent", "student"]]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(parent=models.F("student")),
                name="parent_not_equal_student",
            ),
        ]
    
    def __str__(self) -> str:
        """
        返回家庭关系的字符串表示。
        """
        return f"{self.parent.username} -> {self.student.username} ({self.get_relationship_display()})"


# ==================== 登录历史模型 ====================
class LoginHistory(models.Model):
    """
    用户登录历史模型，记录用户的登录活动。
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="login_history",
        verbose_name=_("用户"),
    )
    
    ip_address = models.GenericIPAddressField(
        _("IP地址"),
        help_text=_("登录时使用的IP地址。"),
    )
    
    user_agent = models.TextField(
        _("用户代理"),
        help_text=_("登录时使用的浏览器或设备信息。"),
    )
    
    location = models.CharField(
        _("地理位置"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("根据IP地址推断的地理位置。"),
    )
    
    login_method = models.CharField(
        _("登录方式"),
        max_length=20,
        choices=[
            ("password", "密码登录"),
            ("sms", "短信验证码"),
            ("wechat", "微信登录"),
            ("other", "其他"),
        ],
        default="password",
        help_text=_("用户使用的登录方式。"),
    )
    
    success = models.BooleanField(
        _("登录成功"),
        default=True,
        help_text=_("标识登录是否成功。"),
    )
    
    failure_reason = models.CharField(
        _("失败原因"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("如果登录失败，记录失败原因。"),
    )
    
    created_at = models.DateTimeField(_("登录时间"), auto_now_add=True)
    
    class Meta:
        """
        登录历史模型的元数据配置。
        """
        verbose_name = _("登录历史")
        verbose_name_plural = _("登录历史")
        db_table = "accounts_login_history"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["ip_address"]),
        ]
    
    def __str__(self) -> str:
        """
        返回登录历史的字符串表示。
        """
        status = "成功" if self.success else "失败"
        return f"{self.user.username} 登录 {status} ({self.created_at})"
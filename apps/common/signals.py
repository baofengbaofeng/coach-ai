"""
公共信号处理器模块，提供跨模块使用的信号处理器。
按照豆包AI助手最佳实践：提供类型安全的信号处理器。
"""
from __future__ import annotations

import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.core.signals import request_finished, request_started
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver

from apps.common.utils import Timer


# ==================== 日志记录器 ====================
_LOGGER: logging.Logger = logging.getLogger(__name__)


# ==================== 用户模型引用 ====================
User = get_user_model()


# ==================== 请求信号处理器 ====================
@receiver(request_started)
def handle_request_started(sender: Any, **kwargs: Any) -> None:
    """
    处理请求开始信号。
    
    Args:
        sender: 信号发送者
        **kwargs: 其他参数
    """
    environ = kwargs.get("environ", {})
    path = environ.get("PATH_INFO", "未知路径")
    method = environ.get("REQUEST_METHOD", "未知方法")
    
    _LOGGER.debug("请求开始: %s %s", method, path)


@receiver(request_finished)
def handle_request_finished(sender: Any, **kwargs: Any) -> None:
    """
    处理请求完成信号。
    
    Args:
        sender: 信号发送者
        **kwargs: 其他参数
    """
    _LOGGER.debug("请求完成")


# ==================== 用户认证信号处理器 ====================
@receiver(user_logged_in)
def handle_user_logged_in(sender: Any, request: Any, user: User, **kwargs: Any) -> None:
    """
    处理用户登录成功信号。
    
    Args:
        sender: 信号发送者
        request: HTTP请求对象
        user: 用户对象
        **kwargs: 其他参数
    """
    ip_address = request.META.get("REMOTE_ADDR", "未知")
    user_agent = request.META.get("HTTP_USER_AGENT", "未知")
    
    _LOGGER.info(
        "用户登录成功: %s (%s) - IP: %s, UA: %s",
        user.username,
        user.email or "无邮箱",
        ip_address,
        user_agent[:50],  # 截断用户代理字符串
    )
    
    # 更新用户最后登录时间
    try:
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
    except Exception as e:
        _LOGGER.warning("更新用户最后登录时间失败: %s", str(e))


@receiver(user_logged_out)
def handle_user_logged_out(sender: Any, request: Any, user: User, **kwargs: Any) -> None:
    """
    处理用户登出信号。
    
    Args:
        sender: 信号发送者
        request: HTTP请求对象
        user: 用户对象
        **kwargs: 其他参数
    """
    ip_address = request.META.get("REMOTE_ADDR", "未知")
    
    _LOGGER.info(
        "用户登出: %s (%s) - IP: %s",
        user.username if user else "未知用户",
        user.email if user else "无邮箱",
        ip_address,
    )


@receiver(user_login_failed)
def handle_user_login_failed(sender: Any, credentials: dict, request: Any, **kwargs: Any) -> None:
    """
    处理用户登录失败信号。
    
    Args:
        sender: 信号发送者
        credentials: 凭据字典
        request: HTTP请求对象
        **kwargs: 其他参数
    """
    username = credentials.get("username", "未知用户")
    ip_address = request.META.get("REMOTE_ADDR", "未知")
    
    _LOGGER.warning(
        "用户登录失败: %s - IP: %s",
        username,
        ip_address,
    )


# ==================== 模型信号处理器 ====================
@receiver(pre_save)
def handle_pre_save(sender: Any, instance: Any, **kwargs: Any) -> None:
    """
    处理模型保存前信号。
    
    Args:
        sender: 模型类
        instance: 模型实例
        **kwargs: 其他参数
    """
    # 跳过不需要处理的模型
    model_name = sender.__name__
    if model_name in ["Session", "Migration"]:
        return
    
    # 记录操作
    if instance.pk:
        _LOGGER.debug("准备更新 %s: ID=%s", model_name, instance.pk)
    else:
        _LOGGER.debug("准备创建 %s", model_name)


@receiver(post_save)
def handle_post_save(sender: Any, instance: Any, created: bool, **kwargs: Any) -> None:
    """
    处理模型保存后信号。
    
    Args:
        sender: 模型类
        instance: 模型实例
        created: 是否新创建
        **kwargs: 其他参数
    """
    # 跳过不需要处理的模型
    model_name = sender.__name__
    if model_name in ["Session", "Migration"]:
        return
    
    # 记录操作
    if created:
        _LOGGER.info("创建 %s 成功: ID=%s", model_name, instance.pk)
    else:
        _LOGGER.debug("更新 %s 成功: ID=%s", model_name, instance.pk)


@receiver(pre_delete)
def handle_pre_delete(sender: Any, instance: Any, **kwargs: Any) -> None:
    """
    处理模型删除前信号。
    
    Args:
        sender: 模型类
        instance: 模型实例
        **kwargs: 其他参数
    """
    # 跳过不需要处理的模型
    model_name = sender.__name__
    if model_name in ["Session", "Migration"]:
        return
    
    # 记录操作
    _LOGGER.debug("准备删除 %s: ID=%s", model_name, instance.pk)


@receiver(post_delete)
def handle_post_delete(sender: Any, instance: Any, **kwargs: Any) -> None:
    """
    处理模型删除后信号。
    
    Args:
        sender: 模型类
        instance: 模型实例
        **kwargs: 其他参数
    """
    # 跳过不需要处理的模型
    model_name = sender.__name__
    if model_name in ["Session", "Migration"]:
        return
    
    # 记录操作
    _LOGGER.info("删除 %s 成功: ID=%s", model_name, instance.pk)


# ==================== 自定义信号处理器 ====================
def register_model_signals(model_class: Any) -> None:
    """
    为指定模型注册信号处理器。
    
    Args:
        model_class: 模型类
    """
    model_name = model_class.__name__
    
    @receiver(pre_save, sender=model_class)
    def handle_model_pre_save(sender: Any, instance: Any, **kwargs: Any) -> None:
        """处理指定模型保存前信号。"""
        _LOGGER.debug("准备保存 %s: ID=%s", model_name, instance.pk or "新记录")
    
    @receiver(post_save, sender=model_class)
    def handle_model_post_save(sender: Any, instance: Any, created: bool, **kwargs: Any) -> None:
        """处理指定模型保存后信号。"""
        if created:
            _LOGGER.info("创建 %s 成功: ID=%s", model_name, instance.pk)
        else:
            _LOGGER.debug("更新 %s 成功: ID=%s", model_name, instance.pk)
    
    @receiver(pre_delete, sender=model_class)
    def handle_model_pre_delete(sender: Any, instance: Any, **kwargs: Any) -> None:
        """处理指定模型删除前信号。"""
        _LOGGER.debug("准备删除 %s: ID=%s", model_name, instance.pk)
    
    @receiver(post_delete, sender=model_class)
    def handle_model_post_delete(sender: Any, instance: Any, **kwargs: Any) -> None:
        """处理指定模型删除后信号。"""
        _LOGGER.info("删除 %s 成功: ID=%s", model_name, instance.pk)
    
    _LOGGER.debug("已为 %s 模型注册信号处理器", model_name)


# ==================== 性能监控信号处理器 ====================
class PerformanceSignalHandler:
    """
    性能监控信号处理器类。
    """
    
    def __init__(self) -> None:
        """初始化性能监控信号处理器。"""
        self.timers: dict = {}
    
    def start_timer(self, name: str) -> None:
        """
        开始计时器。
        
        Args:
            name: 计时器名称
        """
        self.timers[name] = Timer(name)
        self.timers[name].start()
    
    def stop_timer(self, name: str) -> float:
        """
        停止计时器并返回经过的时间。
        
        Args:
            name: 计时器名称
            
        Returns:
            经过的时间（秒）
        """
        if name in self.timers:
            self.timers[name].stop()
            return self.timers[name].elapsed_time
        return 0.0
    
    def get_timer(self, name: str) -> Optional[Timer]:
        """
        获取计时器。
        
        Args:
            name: 计时器名称
            
        Returns:
            计时器对象
        """
        return self.timers.get(name)


# ==================== 导出列表 ====================
__all__: list = [
    # 请求信号处理器
    "handle_request_started",
    "handle_request_finished",
    
    # 用户认证信号处理器
    "handle_user_logged_in",
    "handle_user_logged_out",
    "handle_user_login_failed",
    
    # 模型信号处理器
    "handle_pre_save",
    "handle_post_save",
    "handle_pre_delete",
    "handle_post_delete",
    
    # 自定义信号处理器
    "register_model_signals",
    
    # 性能监控信号处理器
    "PerformanceSignalHandler",
]
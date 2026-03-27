"""
认证领域模块
包含会话、令牌、认证策略等核心业务概念
"""

from .entities import Session, Token, AuthAttempt
from .value_objects import TokenType, AuthMethod, SessionStatus
from .services import AuthService, TokenService, SessionService
from .events import (
    UserAuthenticatedEvent,
    UserLoginFailedEvent,
    SessionCreatedEvent,
    SessionTerminatedEvent,
    TokenIssuedEvent,
    TokenRevokedEvent
)

__all__ = [
    # 实体
    'Session',
    'Token',
    'AuthAttempt',
    
    # 值对象
    'TokenType',
    'AuthMethod',
    'SessionStatus',
    
    # 领域服务
    'AuthService',
    'TokenService',
    'SessionService',
    
    # 领域事件
    'UserAuthenticatedEvent',
    'UserLoginFailedEvent',
    'SessionCreatedEvent',
    'SessionTerminatedEvent',
    'TokenIssuedEvent',
    'TokenRevokedEvent',
]
"""
JWT工具模块（迁移版）
处理JWT令牌的生成和验证
"""

import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import jwt
from loguru import logger

from src.settings import settings


# 创建工具类实例
_jwt_utils = None

def get_jwt_utils():
    """获取JWT工具实例"""
    global _jwt_utils
    if _jwt_utils is None:
        _jwt_utils = JWTUtils()
    return _jwt_utils


def create_jwt_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT令牌（兼容性函数）
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        
    Returns:
        JWT令牌字符串
    """
    return get_jwt_utils().create_access_token(data, expires_delta)


def verify_jwt_token(token: str, secret_key: Optional[str] = None) -> Dict[str, Any]:
    """
    验证JWT令牌（兼容性函数）
    
    Args:
        token: JWT令牌
        secret_key: 密钥，如果为None则使用配置中的密钥
        
    Returns:
        解码后的数据
    """
    return get_jwt_utils().verify_token(token, secret_key)


class JWTUtils:
    """JWT工具类"""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        创建访问令牌
        
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
            
        Returns:
            JWT令牌字符串
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        创建刷新令牌
        
        Args:
            data: 要编码的数据
            
        Returns:
            JWT刷新令牌字符串
        """
        to_encode = data.copy()
        
        expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        验证JWT令牌
        
        Args:
            token: JWT令牌字符串
            token_type: 令牌类型（access/refresh）
            
        Returns:
            解码后的数据或None（验证失败）
        """
        try:
            # 解码令牌
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # 验证令牌类型
            if payload.get("type") != token_type:
                logger.warning(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
                return None
            
            # 检查过期时间
            exp_timestamp = payload.get("exp")
            if exp_timestamp and exp_timestamp < time.time():
                logger.warning("Token has expired")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token signature has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[str]:
        """
        使用刷新令牌获取新的访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的访问令牌或None（刷新失败）
        """
        # 验证刷新令牌
        payload = JWTUtils.verify_token(refresh_token, "refresh")
        if not payload:
            return None
        
        # 移除令牌特定的字段
        data = {k: v for k, v in payload.items() if k not in ["exp", "iat", "type"]}
        
        # 创建新的访问令牌
        return JWTUtils.create_access_token(data)
    
    @staticmethod
    def extract_user_id_from_token(token: str) -> Optional[str]:
        """
        从令牌中提取用户ID
        
        Args:
            token: JWT令牌
            
        Returns:
            用户ID或None
        """
        payload = JWTUtils.verify_token(token)
        if payload:
            return payload.get("user_id")
        return None
    
    @staticmethod
    def extract_tenant_id_from_token(token: str) -> Optional[str]:
        """
        从令牌中提取租户ID
        
        Args:
            token: JWT令牌
            
        Returns:
            租户ID或None
        """
        payload = JWTUtils.verify_token(token)
        if payload:
            return payload.get("tenant_id")
        return None
    
    @staticmethod
    def create_tokens_pair(user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        创建访问令牌和刷新令牌对
        
        Args:
            user_data: 用户数据
            
        Returns:
            包含access_token和refresh_token的字典
        """
        access_token = JWTUtils.create_access_token(user_data)
        refresh_token = JWTUtils.create_refresh_token(user_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }


class TokenBlacklist:
    """令牌黑名单管理"""
    
    def __init__(self, redis_client):
        """
        初始化令牌黑名单
        
        Args:
            redis_client: Redis客户端
        """
        self.redis = redis_client
        self.prefix = "token_blacklist:"
    
    def add_token(self, token: str, expire_seconds: int = 86400) -> bool:
        """
        添加令牌到黑名单
        
        Args:
            token: 要加入黑名单的令牌
            expire_seconds: 过期时间（秒）
            
        Returns:
            操作是否成功
        """
        try:
            # 使用令牌的哈希作为键
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            key = f"{self.prefix}{token_hash}"
            
            # 设置到Redis，并设置过期时间
            result = self.redis.setex(key, expire_seconds, "1")
            return bool(result)
        except Exception as e:
            logger.error(f"Add token to blacklist error: {e}")
            return False
    
    def is_token_blacklisted(self, token: str) -> bool:
        """
        检查令牌是否在黑名单中
        
        Args:
            token: 要检查的令牌
            
        Returns:
            是否在黑名单中
        """
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            key = f"{self.prefix}{token_hash}"
            
            result = self.redis.get(key)
            return result is not None
        except Exception as e:
            logger.error(f"Check token blacklist error: {e}")
            return False
    
    def revoke_token(self, token: str) -> bool:
        """
        撤销令牌（加入黑名单）
        
        Args:
            token: 要撤销的令牌
            
        Returns:
            操作是否成功
        """
        return self.add_token(token)
    
    def cleanup_expired(self) -> int:
        """
        清理过期的黑名单条目
        
        Returns:
            清理的条目数量
        """
        # Redis会自动清理过期的键
        # 这里可以添加额外的清理逻辑
        return 0
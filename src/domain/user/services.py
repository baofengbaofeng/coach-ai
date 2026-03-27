"""
用户领域服务
包含用户和租户的业务逻辑
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import re
from loguru import logger

from ..base_simple import DomainException
from .entities_simple import User, Tenant, Permission
from .value_objects_simple import Email, Password, PhoneNumber, UserStatus
from .events_simple import (
    UserRegisteredEvent, UserActivatedEvent, UserUpdatedEvent,
    TenantCreatedEvent, TenantMemberAddedEvent
)


class UserService:
    """用户领域服务"""
    
    def __init__(self):
        self.logger = logger.bind(service="UserService")
    
    def validate_username(self, username: str) -> bool:
        """
        验证用户名
        
        Args:
            username: 用户名
            
        Returns:
            是否有效
        """
        if not username or len(username) < 3:
            return False
        
        # 只允许字母、数字、下划线
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False
        
        # 检查保留用户名
        reserved_names = {'admin', 'root', 'system', 'guest', 'test'}
        if username.lower() in reserved_names:
            return False
        
        return True
    
    def validate_email(self, email: str) -> bool:
        """
        验证邮箱
        
        Args:
            email: 邮箱地址
            
        Returns:
            是否有效
        """
        try:
            email_obj = Email(email)
            return email_obj.is_valid()
        except ValueError:
            return False
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """
        验证密码强度
        
        Args:
            password: 密码
            
        Returns:
            验证结果字典
        """
        result = {
            'valid': True,
            'strength': 'weak',
            'issues': []
        }
        
        # 长度检查
        if len(password) < 8:
            result['valid'] = False
            result['issues'].append('密码长度必须至少8个字符')
        
        # 复杂度检查
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        complexity_score = sum([has_upper, has_lower, has_digit, has_special])
        
        if complexity_score >= 3:
            result['strength'] = 'strong'
        elif complexity_score >= 2:
            result['strength'] = 'medium'
        else:
            result['strength'] = 'weak'
            if not result['issues']:  # 如果没有其他问题，添加复杂度建议
                result['issues'].append('建议使用大小写字母、数字和特殊字符的组合')
        
        return result
    
    def calculate_password_score(self, password: str) -> int:
        """
        计算密码分数
        
        Args:
            password: 密码
            
        Returns:
            密码分数（0-100）
        """
        score = 0
        
        # 长度分数
        length = len(password)
        if length >= 12:
            score += 40
        elif length >= 8:
            score += 20
        else:
            score += 0
        
        # 复杂度分数
        checks = [
            any(c.isupper() for c in password),  # 大写字母
            any(c.islower() for c in password),  # 小写字母
            any(c.isdigit() for c in password),  # 数字
            any(not c.isalnum() for c in password),  # 特殊字符
        ]
        
        complexity = sum(checks)
        score += complexity * 15
        
        # 唯一性分数（简单检查）
        if len(set(password)) >= len(password) * 0.7:
            score += 10
        
        return min(score, 100)
    
    def generate_username_suggestions(self, email: str, display_name: Optional[str] = None) -> List[str]:
        """
        生成用户名建议
        
        Args:
            email: 邮箱
            display_name: 显示名称
            
        Returns:
            用户名建议列表
        """
        suggestions = []
        
        # 从邮箱生成
        try:
            email_obj = Email(email)
            local_part = email_obj.get_local_part()
            
            # 移除特殊字符
            clean_local = re.sub(r'[^a-zA-Z0-9]', '', local_part)
            if clean_local and len(clean_local) >= 3:
                suggestions.append(clean_local.lower())
            
            # 添加数字变体
            for i in range(1, 4):
                suggestions.append(f"{clean_local}{i}".lower())
        
        except ValueError:
            pass
        
        # 从显示名称生成
        if display_name:
            # 移除空格和特殊字符
            clean_name = re.sub(r'[^a-zA-Z0-9]', '', display_name)
            if clean_name and len(clean_name) >= 3:
                suggestions.append(clean_name.lower())
            
            # 添加数字变体
            for i in range(1, 4):
                suggestions.append(f"{clean_name}{i}".lower())
        
        # 确保唯一性（在实际应用中需要检查数据库）
        return list(dict.fromkeys(suggestions))[:5]  # 去重并限制数量
    
    def check_login_security(self, user: User, ip_address: Optional[str] = None) -> Dict[str, Any]:
        """
        检查登录安全性
        
        Args:
            user: 用户实体
            ip_address: IP地址
            
        Returns:
            安全检查结果
        """
        result = {
            'can_login': True,
            'warnings': [],
            'requirements': []
        }
        
        # 检查用户状态
        if not user.status.can_login():
            result['can_login'] = False
            result['warnings'].append('用户账户不可用')
        
        # 检查账户锁定
        if user.locked_until and user.locked_until > datetime.now():
            result['can_login'] = False
            result['warnings'].append(f'账户已锁定，直到 {user.locked_until}')
        
        # 检查失败次数
        if user.failed_login_attempts >= 3:
            result['warnings'].append(f'最近有 {user.failed_login_attempts} 次登录失败')
        
        # 检查MFA要求
        if user.mfa_enabled:
            result['requirements'].append('mfa')
        
        # 检查IP地址（简单示例）
        if ip_address:
            # 这里可以添加IP黑名单检查、地理位置检查等
            pass
        
        return result
    
    def generate_password_reset_token(self) -> str:
        """
        生成密码重置令牌
        
        Returns:
            重置令牌
        """
        import secrets
        import hashlib
        
        # 生成安全的随机令牌
        token = secrets.token_urlsafe(32)
        
        # 添加时间戳和哈希
        timestamp = datetime.now().isoformat()
        combined = f"{token}:{timestamp}"
        
        # 计算哈希
        hash_obj = hashlib.sha256(combined.encode())
        return f"{token}.{hash_obj.hexdigest()[:16]}"
    
    def validate_password_reset_token(self, token: str, max_age_hours: int = 24) -> bool:
        """
        验证密码重置令牌
        
        Args:
            token: 重置令牌
            max_age_hours: 最大有效时间（小时）
            
        Returns:
            是否有效
        """
        try:
            # 解析令牌
            parts = token.split('.')
            if len(parts) != 2:
                return False
            
            token_part, hash_part = parts
            
            # 这里应该验证令牌的有效期和签名
            # 简化实现：检查格式
            return len(token_part) >= 32 and len(hash_part) == 16
        
        except Exception:
            return False
    
    def validate_registration_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证注册数据 - 所有业务规则集中在这里
        
        Args:
            data: 注册数据
            
        Returns:
            验证结果
        """
        result = {
            'is_valid': True,
            'errors': []
        }
        
        # 检查必填字段
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                result['is_valid'] = False
                result['errors'].append(f"{field} is required")
        
        # 验证邮箱格式 - 使用领域服务的方法
        if 'email' in data and data['email']:
            if not self.validate_email(data['email']):
                result['is_valid'] = False
                result['errors'].append("Invalid email format")
        
        # 验证用户名格式 - 使用领域服务的方法
        if 'username' in data and data['username']:
            if not self.validate_username(data['username']):
                result['is_valid'] = False
                result['errors'].append("Invalid username format")
        
        # 验证密码强度 - 使用领域服务的方法
        if 'password' in data and data['password']:
            password_validation = self.validate_password(data['password'])
            if not password_validation['valid']:  # 注意：这里是'valid'不是'is_valid'
                result['is_valid'] = False
                result['errors'].extend(password_validation['issues'])
        
        return result
    
    def check_username_exists(self, username: str) -> bool:
        """
        检查用户名是否存在
        
        Args:
            username: 用户名
            
        Returns:
            是否存在
        """
        # 这里应该调用仓储层查询数据库
        # 暂时返回False，实际实现需要仓储层
        return False
    
    def check_email_exists(self, email: str) -> bool:
        """
        检查邮箱是否存在
        
        Args:
            email: 邮箱地址
            
        Returns:
            是否存在
        """
        # 这里应该调用仓储层查询数据库
        # 暂时返回False，实际实现需要仓储层
        return False
    
    def find_user_by_identifier(self, identifier: str) -> Optional[User]:
        """
        通过标识符查找用户（用户名或邮箱）
        
        Args:
            identifier: 用户名或邮箱
            
        Returns:
            用户实体或None
        """
        # 这里应该调用仓储层查询数据库
        # 暂时返回None，实际实现需要仓储层
        return None
    
    def find_user_by_email(self, email: str) -> Optional[User]:
        """
        通过邮箱查找用户
        
        Args:
            email: 邮箱地址
            
        Returns:
            用户实体或None
        """
        # 这里应该调用仓储层查询数据库
        # 暂时返回None，实际实现需要仓储层
        return None
    
    def create_user(self, username: str, email: str, password_hash: str, 
                   display_name: Optional[str] = None, phone: Optional[str] = None) -> User:
        """
        创建用户实体
        
        Args:
            username: 用户名
            email: 邮箱
            password_hash: 密码哈希
            display_name: 显示名称
            phone: 手机号
            
        Returns:
            用户实体
        """
        # 创建值对象
        email_obj = Email(email)
        password_obj = Password(password_hash)  # Password类只接受哈希值
        phone_obj = PhoneNumber(phone) if phone else None
        
        # 创建用户实体
        user = User(
            username=username,
            email=email_obj,
            password=password_obj,
            phone=phone_obj,
            display_name=display_name or username
        )
        
        return user
    
    def validate_password_for_reset(self, password: str) -> Dict[str, Any]:
        """
        验证重置密码的强度
        
        Args:
            password: 密码
            
        Returns:
            验证结果
        """
        # 调用现有的密码验证方法
        return self.validate_password(password)


class TenantService:
    """租户领域服务"""
    
    def __init__(self):
        self.logger = logger.bind(service="TenantService")
    
    def validate_tenant_name(self, name: str) -> bool:
        """
        验证租户名称
        
        Args:
            name: 租户名称
            
        Returns:
            是否有效
        """
        if not name or len(name) < 2:
            return False
        
        # 检查保留名称
        reserved_names = {'system', 'admin', 'root', 'default'}
        if name.lower() in reserved_names:
            return False
        
        # 允许中文、字母、数字、空格和常用标点
        pattern = r'^[\u4e00-\u9fa5a-zA-Z0-9\s\-_\.\(\)]+$'
        return bool(re.match(pattern, name))
    
    def generate_tenant_code(self, name: str) -> str:
        """
        生成租户代码
        
        Args:
            name: 租户名称
            
        Returns:
            租户代码
        """
        # 移除空格和特殊字符
        clean_name = re.sub(r'[^\w]', '', name)
        
        # 转换为小写
        code = clean_name.lower()
        
        # 如果太短，添加随机字符
        if len(code) < 4:
            import secrets
            code += secrets.token_hex(2)
        
        return code[:20]  # 限制长度
    
    def validate_tenant_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证租户设置
        
        Args:
            settings: 租户设置
            
        Returns:
            验证后的设置
        """
        validated = {}
        
        # 验证通用设置
        if 'language' in settings:
            valid_languages = {'zh-CN', 'en-US', 'ja-JP', 'ko-KR'}
            if settings['language'] in valid_languages:
                validated['language'] = settings['language']
        
        if 'timezone' in settings:
            # 简单的时区验证
            try:
                import pytz
                if settings['timezone'] in pytz.all_timezones:
                    validated['timezone'] = settings['timezone']
            except ImportError:
                # 如果没有pytz，进行简单验证
                if settings['timezone'] in {'Asia/Shanghai', 'UTC', 'America/New_York'}:
                    validated['timezone'] = settings['timezone']
        
        if 'theme' in settings:
            valid_themes = {'light', 'dark', 'auto'}
            if settings['theme'] in valid_themes:
                validated['theme'] = settings['theme']
        
        # 验证业务设置
        if 'max_members' in settings:
            try:
                max_members = int(settings['max_members'])
                if 1 <= max_members <= 1000:
                    validated['max_members'] = max_members
            except (ValueError, TypeError):
                pass
        
        if 'allow_guest_access' in settings:
            validated['allow_guest_access'] = bool(settings['allow_guest_access'])
        
        return validated
    
    def check_tenant_limits(self, tenant: Tenant, action: str, **kwargs) -> Dict[str, Any]:
        """
        检查租户限制
        
        Args:
            tenant: 租户实体
            action: 操作类型（add_member, create_resource等）
            **kwargs: 额外参数
            
        Returns:
            检查结果
        """
        result = {
            'allowed': True,
            'reason': None,
            'limits': {}
        }
        
        # 检查成员数量限制
        if action == 'add_member':
            max_members = tenant.settings.get('max_members', 10)
            current_members = len(tenant.member_ids)
            
            if current_members >= max_members:
                result['allowed'] = False
                result['reason'] = f'已达到最大成员数限制 ({max_members})'
                result['limits'] = {
                    'current': current_members,
                    'max': max_members
                }
        
        # 检查资源创建限制
        elif action == 'create_resource':
            # 这里可以添加资源创建限制检查
            pass
        
        return result
    
    def calculate_tenant_stats(self, tenant: Tenant) -> Dict[str, Any]:
        """
        计算租户统计信息
        
        Args:
            tenant: 租户实体
            
        Returns:
            统计信息
        """
        return {
            'member_count': len(tenant.member_ids),
            'active_member_count': len(tenant.member_ids),  # 简化：假设所有成员都活跃
            'tenant_age_days': (datetime.now() - tenant.created_at).days,
            'settings_count': len(tenant.settings),
            'is_active': tenant.status == 'active',
            'has_custom_settings': bool(tenant.settings)
        }


class PermissionService:
    """权限领域服务"""
    
    def __init__(self):
        self.logger = logger.bind(service="PermissionService")
    
    def validate_permission_string(self, permission_string: str) -> bool:
        """
        验证权限字符串格式
        
        Args:
            permission_string: 权限字符串（resource:action格式）
            
        Returns:
            是否有效
        """
        if not permission_string or ':' not in permission_string:
            return False
        
        resource, action = permission_string.split(':', 1)
        
        if not resource or not action:
            return False
        
        # 检查资源名称
        if not re.match(r'^[a-z_]+$', resource):
            return False
        
        # 检查操作名称
        valid_actions = {'create', 'read', 'update', 'delete', 'list', 'execute'}
        if action not in valid_actions:
            return False
        
        return True
    
    def parse_permission_string(self, permission_string: str) -> Dict[str, str]:
        """
        解析权限字符串
        
        Args:
            permission_string: 权限字符串
            
        Returns:
            解析后的字典
        """
        if not self.validate_permission_string(permission_string):
            raise ValueError(f"无效的权限字符串: {permission_string}")
        
        resource, action = permission_string.split(':', 1)
        
        return {
            'resource': resource,
            'action': action,
            'permission_string': permission_string
        }
    
    def generate_permission_name(self, resource: str, action: str) -> str:
        """
        生成权限名称
        
        Args:
            resource: 资源
            action: 操作
            
        Returns:
            权限名称
        """
        # 将下划线转换为空格并首字母大写
        resource_name = resource.replace('_', ' ').title()
        action_name = action.title()
        
        return f"{action_name} {resource_name}"
    
    def check_permission_hierarchy(self, user_permissions: List[str], required_permission: str) -> bool:
        """
        检查权限层次结构
        
        Args:
            user_permissions: 用户拥有的权限列表
            required_permission: 需要的权限
            
        Returns:
            是否拥有足够权限
        """
        # 解析需要的权限
        required_parts = self.parse_permission_string(required_permission)
        required_resource = required_parts['resource']
        required_action = required_parts['action']
        
        # 定义权限层次结构
        action_hierarchy = {
            'delete': ['create', 'read', 'update', 'delete'],
            'update': ['create', 'read', 'update'],
            'create': ['create', 'read'],
            'read': ['read'],
            'list': ['list'],
            'execute': ['execute']
        }
        
        # 检查用户权限
        for user_perm in user_permissions:
            try:
                user_parts = self.parse_permission_string(user_perm)
                
                # 检查资源是否匹配
                if user_parts['resource'] != required_resource:
                    continue
                
                # 检查操作是否在层次结构中
                allowed_actions = action_hierarchy.get(user_parts['action'], [])
                if required_action in allowed_actions:
                    return True
            
            except ValueError:
                continue
        
        return False
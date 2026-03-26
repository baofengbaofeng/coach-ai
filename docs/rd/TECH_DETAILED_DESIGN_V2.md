# CoachAI 技术详细设计 v2.0
## 基于SaaS多租户、移动端H5、硬件外设集成的详细技术方案

## 📋 文档信息

| 项目 | 内容 |
|------|------|
| **文档名称** | CoachAI 技术详细设计 v2.0 |
| **文档版本** | 2.0.0 |
| **创建日期** | 2026-03-26 |
| **最后更新** | 2026-03-26 |
| **文档状态** | 正式版 |
| **作者** | CoachAI-RD (后端研发专家) |
| **审核人** | 待定 |
| **关联文档** | [技术架构概要设计](./TECH_ARCHITECTURE_OVERVIEW_V2.md) |
| **目标读者** | 开发团队、架构师、技术负责人 |

## 📝 修订历史

| 版本 | 日期 | 作者 | 变更描述 |
|------|------|------|----------|
| 1.0.0 | 2026-03-24 | baofengbaofeng | 初始详细设计版本 |
| 2.0.0 | 2026-03-26 | CoachAI-RD | 基于新需求重构：SaaS多租户、移动端H5、硬件外设集成 |

## 🎯 设计目标

### 1. 核心设计目标
- **SaaS多租户实现**: 完整的多租户架构设计和实现方案
- **移动端H5优化**: 深度优化的移动端H5技术方案
- **硬件外设集成**: 完整的硬件设备集成和兼容性方案
- **高性能实时处理**: 支持实时音视频处理和AI分析
- **可扩展架构**: 支持未来业务扩展和技术演进

### 2. 非功能性需求
- **性能**: API响应时间 < 200ms，实时处理延迟 < 1s
- **可用性**: 系统可用性 99.9%，支持10万并发用户
- **安全性**: 数据完全隔离，硬件访问权限控制
- **兼容性**: 支持主流移动浏览器和硬件设备
- **可维护性**: 代码结构清晰，文档完善，易于维护

## 📊 目录

1. [SaaS多租户详细设计](#1-saas多租户详细设计)
2. [移动端H5详细设计](#2-移动端h5详细设计)
3. [硬件外设集成详细设计](#3-硬件外设集成详细设计)
4. [AI服务详细设计](#4-ai服务详细设计)
5. [数据库详细设计](#5-数据库详细设计)
6. [API接口详细设计](#6-api接口详细设计)
7. [安全设计](#7-安全设计)
8. [部署详细设计](#8-部署详细设计)
9. [测试策略](#9-测试策略)
10. [监控和运维](#10-监控和运维)

---

## 1. SaaS多租户详细设计

### 1.1 多租户数据库设计

#### 1.1.1 数据库Schema设计
```sql
-- 共享Schema（所有租户共享）
CREATE SCHEMA shared;

-- 租户Schema模板
CREATE SCHEMA tenant_template;

-- 在共享Schema中创建租户管理表
CREATE TABLE shared.tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schema_name VARCHAR(63) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    family_type VARCHAR(20) NOT NULL CHECK (family_type IN ('core', 'couple', 'extended', 'single')),
    subscription_plan VARCHAR(20) NOT NULL CHECK (subscription_plan IN ('basic', 'premium', 'professional')),
    max_members INTEGER NOT NULL DEFAULT 5,
    storage_quota BIGINT NOT NULL DEFAULT 10737418240, -- 10GB
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE shared.domains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES shared.tenants(id) ON DELETE CASCADE,
    domain VARCHAR(255) UNIQUE NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 在租户Schema中创建业务表模板
CREATE TABLE tenant_template.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'adult', 'teenager', 'child', 'elder')),
    date_of_birth DATE,
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    fitness_level VARCHAR(20) CHECK (fitness_level IN ('beginner', 'intermediate', 'advanced')),
    preferences JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE tenant_template.family_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES tenant_template.users(id) ON DELETE CASCADE,
    tenant_user_id UUID NOT NULL, -- 在租户内的用户ID
    relationship VARCHAR(50), -- 父子、夫妻等关系
    permissions JSONB DEFAULT '{"view": true, "edit": false}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE tenant_template.exercise_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES tenant_template.users(id) ON DELETE CASCADE,
    exercise_type VARCHAR(50) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    video_url VARCHAR(500),
    audio_url VARCHAR(500),
    posture_data JSONB, -- 姿势数据
    ai_feedback JSONB, -- AI反馈
    calories_burned DECIMAL(6,2),
    heart_rate_data JSONB, -- 心率数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_tenants_status ON shared.tenants(status);
CREATE INDEX idx_tenants_created_at ON shared.tenants(created_at);
CREATE INDEX idx_domains_tenant ON shared.domains(tenant_id);
CREATE INDEX idx_users_email ON tenant_template.users(email);
CREATE INDEX idx_users_role ON tenant_template.users(role);
CREATE INDEX idx_exercise_sessions_user_time ON tenant_template.exercise_sessions(user_id, start_time);
```

#### 1.1.2 租户Schema创建和迁移
```python
# services/tenant_schema_service.py
import psycopg2
from psycopg2 import sql
from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model
import logging

logger = logging.getLogger(__name__)

class TenantSchemaService:
    """租户Schema管理服务"""
    
    @staticmethod
    def create_tenant_schema(tenant):
        """创建租户Schema"""
        schema_name = tenant.schema_name
        
        try:
            with connection.cursor() as cursor:
                # 1. 创建Schema
                cursor.execute(
                    sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                        sql.Identifier(schema_name)
                    )
                )
                
                # 2. 从模板复制表结构
                TenantSchemaService.copy_schema_from_template(cursor, schema_name)
                
                # 3. 设置搜索路径
                cursor.execute(
                    sql.SQL("ALTER ROLE {} SET search_path TO {}, public").format(
                        sql.Identifier(connection.settings_dict['USER']),
                        sql.Identifier(schema_name)
                    )
                )
                
                logger.info(f"Created schema for tenant: {schema_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create schema for tenant {schema_name}: {e}")
            raise
    
    @staticmethod
    def copy_schema_from_template(cursor, schema_name):
        """从模板Schema复制表结构"""
        # 获取模板Schema中的所有表
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'tenant_template'
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        # 复制每个表
        for table in tables:
            cursor.execute(
                sql.SQL("""
                    CREATE TABLE {}.{} (LIKE tenant_template.{} INCLUDING ALL)
                """).format(
                    sql.Identifier(schema_name),
                    sql.Identifier(table),
                    sql.Identifier(table)
                )
            )
            
            # 复制索引
            cursor.execute(
                sql.SQL("""
                    SELECT indexdef 
                    FROM pg_indexes 
                    WHERE schemaname = 'tenant_template' AND tablename = %s
                """), [table]
            )
            
            for row in cursor.fetchall():
                index_sql = row[0]
                # 替换Schema名称
                index_sql = index_sql.replace('tenant_template', schema_name)
                cursor.execute(index_sql)
    
    @staticmethod
    def delete_tenant_schema(tenant):
        """删除租户Schema"""
        schema_name = tenant.schema_name
        
        try:
            with connection.cursor() as cursor:
                # 删除Schema（级联删除所有对象）
                cursor.execute(
                    sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                        sql.Identifier(schema_name)
                    )
                )
                
                logger.info(f"Deleted schema for tenant: {schema_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete schema for tenant {schema_name}: {e}")
            raise
    
    @staticmethod
    def backup_tenant_schema(tenant):
        """备份租户Schema"""
        schema_name = tenant.schema_name
        backup_schema = f"{schema_name}_backup_{int(time.time())}"
        
        try:
            with connection.cursor() as cursor:
                # 创建备份Schema
                cursor.execute(
                    sql.SQL("CREATE SCHEMA {}").format(
                        sql.Identifier(backup_schema)
                    )
                )
                
                # 复制Schema
                cursor.execute(
                    sql.SQL("""
                        SELECT 'CREATE TABLE ' || quote_ident(%s) || '.' || quote_ident(tablename) || 
                               ' AS SELECT * FROM ' || quote_ident(%s) || '.' || quote_ident(tablename)
                        FROM pg_tables 
                        WHERE schemaname = %s
                    """), [backup_schema, schema_name, schema_name]
                )
                
                for row in cursor.fetchall():
                    cursor.execute(row[0])
                
                logger.info(f"Backed up schema {schema_name} to {backup_schema}")
                return backup_schema
                
        except Exception as e:
            logger.error(f"Failed to backup schema {schema_name}: {e}")
            raise
    
    @staticmethod
    def migrate_tenant_schema(tenant, migration_script):
        """迁移租户Schema"""
        schema_name = tenant.schema_name
        
        try:
            # 备份当前Schema
            backup_schema = TenantSchemaService.backup_tenant_schema(tenant)
            
            with connection.cursor() as cursor:
                # 设置搜索路径到租户Schema
                cursor.execute(f"SET search_path TO {schema_name}, public")
                
                # 执行迁移脚本
                cursor.execute(migration_script)
                
                logger.info(f"Migrated schema {schema_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to migrate schema {schema_name}: {e}")
            # 尝试恢复备份
            TenantSchemaService.restore_from_backup(tenant, backup_schema)
            raise
    
    @staticmethod
    def restore_from_backup(tenant, backup_schema):
        """从备份恢复Schema"""
        schema_name = tenant.schema_name
        
        try:
            with connection.cursor() as cursor:
                # 删除当前Schema
                cursor.execute(
                    sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                        sql.Identifier(schema_name)
                    )
                )
                
                # 重命名备份Schema
                cursor.execute(
                    sql.SQL("ALTER SCHEMA {} RENAME TO {}").format(
                        sql.Identifier(backup_schema),
                        sql.Identifier(schema_name)
                    )
                )
                
                logger.info(f"Restored schema {schema_name} from backup {backup_schema}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to restore schema {schema_name}: {e}")
            raise
```

### 1.2 租户路由和中间件

#### 1.2.1 租户识别中间件
```python
# middleware/tenant_middleware.py
from django.http import Http404
from django_tenants.middleware import TenantMainMiddleware
from django_tenants.utils import get_tenant_model, get_tenant_domain_model
import logging

logger = logging.getLogger(__name__)

class CustomTenantMiddleware(TenantMainMiddleware):
    """自定义租户中间件，支持多种识别方式"""
    
    def get_tenant(self, model, hostname, request):
        tenant = None
        
        # 1. 尝试通过子域名识别
        tenant = self.get_tenant_by_subdomain(model, hostname)
        
        # 2. 如果子域名识别失败，尝试通过路径识别
        if not tenant:
            tenant = self.get_tenant_by_path(model, request)
        
        # 3. 如果路径识别失败，尝试通过JWT令牌识别
        if not tenant:
            tenant = self.get_tenant_by_jwt(model, request)
        
        # 4. 如果所有方式都失败，使用默认租户（用于未登录用户）
        if not tenant:
            tenant = self.get_default_tenant(model)
        
        if not tenant:
            raise Http404("Tenant not found")
        
        return tenant
    
    def get_tenant_by_subdomain(self, model, hostname):
        """通过子域名识别租户"""
        try:
            # 解析子域名
            parts = hostname.split('.')
            if len(parts) >= 3:
                subdomain = parts[0]
                if subdomain and subdomain != 'www':
                    domain_model = get_tenant_domain_model()
                    domain = domain_model.objects.select_related('tenant').get(
                        domain=subdomain,
                        is_primary=True
                    )
                    return domain.tenant
        except Exception as e:
            logger.debug(f"Failed to get tenant by subdomain: {e}")
        
        return None
    
    def get_tenant_by_path(self, model, request):
        """通过URL路径识别租户"""
        try:
            path = request.path
            if path.startswith('/tenant/'):
                # 路径格式: /tenant/{tenant_id}/...
                parts = path.split('/')
                if len(parts) >= 3:
                    tenant_id = parts[2]
                    return model.objects.get(id=tenant_id)
        except Exception as e:
            logger.debug(f"Failed to get tenant by path: {e}")
        
        return None
    
    def get_tenant_by_jwt(self, model, request):
        """通过JWT令牌识别租户"""
        try:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                # 解码JWT令牌获取租户ID
                import jwt
                from django.conf import settings
                
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=['HS256']
                )
                
                tenant_id = payload.get('tenant_id')
                if tenant_id:
                    return model.objects.get(id=tenant_id)
        except Exception as e:
            logger.debug(f"Failed to get tenant by JWT: {e}")
        
        return None
    
    def get_default_tenant(self, model):
        """获取默认租户（用于未登录用户）"""
        try:
            return model.objects.get(schema_name='public')
        except model.DoesNotExist:
            return None
    
    def process_request(self, request):
        """处理请求，设置当前租户"""
        try:
            # 调用父类方法设置租户
            super().process_request(request)
            
            # 将租户信息添加到request对象
            if hasattr(request, 'tenant'):
                request.tenant_info = {
                    'id': str(request.tenant.id),
                    'name': request.tenant.name,
                    'schema_name': request.tenant.schema_name,
                    'plan': request.tenant.subscription_plan
                }
                
                logger.debug(f"Tenant set: {request.tenant_info}")
                
        except Exception as e:
            logger.error(f"Failed to process tenant request: {e}")
            raise
```

#### 1.2.2 租户上下文管理器
```python
# utils/tenant_context.py
from contextlib import contextmanager
from django.db import connection
from django_tenants.utils import schema_context
import logging

logger = logging.getLogger(__name__)

@contextmanager
def tenant_context(tenant=None, readonly=False):
    """
    租户上下文管理器
    
    Args:
        tenant: 租户对象，如果为None则使用当前请求的租户
        readonly: 是否只读模式
    """
    from django_tenants.utils import get_tenant_model
    
    if tenant is None:
        # 尝试从当前请求获取租户
        from django.core.handlers.wsgi import WSGIRequest
        import threading
        
        request = getattr(threading.local(), 'request', None)
        if request and hasattr(request, 'tenant'):
            tenant = request.tenant
    
    if not tenant:
        raise ValueError("No tenant specified and no tenant in current request")
    
    # 设置数据库连接到租户Schema
    original_schema = connection.schema_name
    
    try:
        # 切换到租户Schema
        connection.set_schema(tenant.schema_name)
        
        if readonly:
            # 只读模式：设置事务为只读
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION READ ONLY")
        
        logger.debug(f"Entered tenant context: {tenant.schema_name} (readonly: {readonly})")
        yield tenant
        
    except Exception as e:
        logger.error(f"Error in tenant context {tenant.schema_name}: {e}")
        raise
        
    finally:
        # 恢复原始Schema
        connection.set_schema(original_schema)
        logger.debug(f"Exited tenant context: {tenant.schema_name}")

class TenantRouter:
    """租户数据库路由器"""
    
    def db_for_read(self, model, **hints):
        """读操作路由"""
        from django_tenants.utils import get_tenant_model
        
        # 检查是否在租户上下文中
        if hasattr(model, '_tenant_managed') and model._tenant_managed:
            tenant = getattr(model, '_tenant', None)
            if tenant:
                return tenant.schema_name
        
        # 默认使用共享数据库
        return 'default'
    
    def db_for_write(self, model, **hints):
        """写操作路由"""
        from django_tenants.utils import get_tenant_model
        
        # 检查是否在租户上下文中
        if hasattr(model, '_tenant_managed') and model._tenant_managed:
            tenant = getattr(model, '_tenant', None)
            if tenant:
                return tenant.schema_name
        
        # 默认使用共享数据库
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """允许关系"""
        # 允许同一租户内的关系
        if hasattr(obj1, '_tenant') and hasattr(obj2, '_tenant'):
            return obj1._tenant == obj2._tenant
        
        # 允许共享表之间的关系
        if not hasattr(obj1, '_tenant') and not hasattr(obj2, '_tenant'):
            return True
        
        # 不允许租户表和共享表之间的关系
        return False
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """允许迁移"""
        # 共享应用迁移到共享数据库
        from django.conf import settings
        
        if app_label in settings.SHARED_APPS:
            return db == 'default'
        
        # 租户应用迁移到租户数据库
        if app_label in settings.TENANT_APPS:
            return db != 'default'
        
        return None
```

### 1.3 租户配额和限制管理

#### 1.3.1 配额管理服务
```python
# services/quota_service.py
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class QuotaService:
    """租户配额管理服务"""
    
    QUOTA_PLANS = {
        'basic': {
            'max_members': 5,
            'storage_gb': 10,
            'video_minutes_per_month': 300,
            'ai_processing_per_month': 1000,
            'api_requests_per_day': 10000,
            'concurrent_sessions': 3,
        },
        'premium': {
            'max_members': 10,
            'storage_gb': 50,
            'video_minutes_per_month': 1000,
            'ai_processing_per_month': 5000,
            'api_requests_per_day': 50000,
            'concurrent_sessions': 10,
        },
        'professional': {
            'max_members': 20,
            'storage_gb': 200,
            'video_minutes_per_month': 5000,
            'ai_processing_per_month': 25000,
            'api_requests_per_day': 200000,
            'concurrent_sessions': 30,
        }
    }
    
    @classmethod
    def get_tenant_quota(cls, tenant):
        """获取租户配额"""
        plan = tenant.subscription_plan
        return cls.QUOTA_PLANS.get(plan, cls.QUOTA_PLANS['basic'])
    
    @classmethod
    def check_member_quota(cls, tenant, current_count):
        """检查成员数量配额"""
        quota = cls.get_tenant_quota(tenant)
        max_members = quota['max_members']
        
        if current_count >= max_members:
            raise QuotaExceededError(
                f"成员数量超过配额限制: {current_count}/{max_members}",
                quota_type='members',
                current=current_count,
                limit=max_members
            )
        
        return True
    
    @classmethod
    def check_storage_quota(cls, tenant, additional_bytes=0):
        """检查存储配额"""
        from .storage_service import StorageService
        
        quota = cls.get_tenant_quota(tenant)
        max_bytes = quota['storage_gb'] * 1024 * 1024 * 1024
        
        current_bytes = StorageService.get_tenant_storage_usage(tenant)
        total_bytes = current_bytes + additional_bytes
        
        if total_bytes > max_bytes:
            raise QuotaExceededError(
                f"存储空间超过配额限制: {total_bytes}/{max_bytes} bytes",
                quota_type='storage',
                current=current_bytes,
                limit=max_bytes,
                additional=additional_bytes
            )
        
        return True
    
    @classmethod
    def check_video_quota(cls, tenant, duration_seconds):
        """检查视频时长配额"""
        cache_key = f"tenant:{tenant.id}:video_usage:{timezone.now().strftime('%Y-%m')}"
        
        # 获取本月已使用时长
        current_seconds = cache.get(cache_key, 0)
        quota = cls.get_tenant_quota(tenant)
        max_seconds = quota['video_minutes_per_month'] * 60
        
        total_seconds = current_seconds + duration_seconds
        
        if total_seconds > max_seconds:
            raise QuotaExceededError(
                f"视频时长超过月度配额: {total_seconds}/{max_seconds} seconds",
                quota_type='video',
                current=current_seconds,
                limit=max_seconds,
                additional=duration_seconds
            )
        
        # 更新缓存
        cache.set(cache_key, total_seconds, timeout=31 * 24 * 60 * 60)  # 31天
        
        return True
    
    @classmethod
    def check_ai_processing_quota(cls, tenant, processing_units=1):
        """检查AI处理配额"""
        cache_key = f"tenant:{tenant.id}:ai_usage:{timezone.now().strftime('%Y-%m')}"
        
        # 获取本月已使用量
        current_units = cache.get(cache_key, 0)
        quota = cls.get_tenant_quota(tenant)
        max_units = quota['ai_processing_per_month']
        
        total_units = current_units + processing_units
        
        if total_units > max_units:
            raise QuotaExceededError(
                f"AI处理超过月度配额: {total_units}/{max_units} units",
                quota_type='ai_processing',
                current=current_units,
                limit=max_units,
                additional=processing_units
            )
        
        # 更新缓存
        cache.set(cache_key, total_units, timeout=31 * 24 * 60 * 60)
        
        return True
    
    @classmethod
    def check_api_rate_limit(cls, tenant):
        """检查API速率限制"""
        cache_key = f"tenant:{tenant.id}:api_requests:{timezone.now().strftime('%Y-%m-%d')}"
        
        # 获取今日已请求次数
        current_requests = cache.get(cache_key, 0)
        quota = cls.get_tenant_quota(tenant)
        max_requests = quota['api_requests_per_day']
        
        if current_requests >= max_requests:
            raise RateLimitExceededError(
                f"API请求超过每日限制: {current_requests}/{max_requests}",
                quota_type='api_requests',
                current=current_requests,
                limit=max_requests
            )
        
        # 增加计数
        cache.incr(cache_key)
        # 设置过期时间到明天
        tomorrow = timezone.now() + timedelta(days=1)
        cache.expireat(cache_key, tomorrow)
        
        return True
    
    @classmethod
    def check_concurrent_sessions(cls, tenant, session_id):
        """检查并发会话限制"""
        cache_key = f"tenant:{tenant.id}:concurrent_sessions"
        
        # 获取当前活跃会话
        active_sessions = cache.get(cache_key, set())
        quota = cls.get_tenant_quota(tenant)
        max_sessions = quota['concurrent_sessions']
        
        # 清理过期会话
        active_sessions = {s for s in active_sessions if cache.get(f"session:{s}", False)}
        
        if len(active_sessions) >= max_sessions and session_id not in active_sessions:
            raise QuotaExceededError(
                f"并发会话超过限制: {len(active_sessions)}/{max_sessions}",
                quota_type='concurrent_sessions',
                current=len(active_sessions),
                limit=max_sessions
            )
        
        # 添加新会话
        active_sessions.add(session_id)
        cache.set(cache_key, active_sessions, timeout=3600)  # 1小时
        cache.set(f"session:{session_id}", True, timeout=3600)  # 会话有效期1小时
        
        return True
    
    @classmethod
    def get_quota_usage(cls, tenant):
        """获取租户配额使用情况"""
        from .storage_service import StorageService
        
        quota = cls.get_tenant_quota(tenant)
        current_month = timezone.now().strftime('%Y-%m')
        
        usage = {
            'members': {
                'current': cls.get_member_count(tenant),
                'limit': quota['max_members'],
                'percentage': 0,
            },
            'storage': {
                'current': StorageService.get_tenant_storage_usage(tenant),
                'limit': quota['storage_gb'] * 1024 * 1024 * 1024,
                'percentage': 0,
            },
            'video': {
                'current': cache.get(f"tenant:{tenant.id}:video_usage:{current_month}", 0),
                'limit': quota['video_minutes_per_month'] * 60,
                'percentage': 0,
            },
            'ai_processing': {
                'current': cache.get(f"tenant:{tenant.id}:ai_usage:{current_month}", 0),
                'limit': quota['ai_processing_per_month'],
                'percentage': 0,
            },
            'api_requests': {
                'current': cache.get(f"tenant:{tenant.id}:api_requests:{timezone.now().strftime('%Y-%m-%d')}", 0),
                'limit': quota['api_requests_per_day'],
                'percentage': 0,
            },
            'concurrent_sessions': {
                'current': len(cache.get(f"tenant:{tenant.id}:concurrent_sessions", set())),
                'limit': quota['concurrent_sessions'],
                'percentage': 0,
            }
        }
        
        # 计算百分比
        for key, data in usage.items():
            if data['limit'] > 0:
                data['percentage'] = min(100, (data['current'] / data['limit']) * 100)
        
        return usage

class QuotaExceededError(Exception):
    """配额超出异常"""
    
    def __init__(self, message, quota_type, current, limit, additional=0):
        super().__init__(message)
        self.quota_type = quota_type
        self.current = current
        self.limit = limit
        self.additional = additional

class RateLimitExceededError(Exception):
    """速率限制超出异常"""
    
    def __init__(self, message, quota_type, current, limit):
        super().__init__(message)
        self.quota_type = quota_type
        self.current = current
        self.limit = limit
```

#### 1.3.2 配额中间件
```python
# middleware/quota_middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from .quota_service import QuotaService, QuotaExceededError, RateLimitExceededError
import logging

logger = logging.getLogger(__name__)

class QuotaMiddleware(MiddlewareMixin):
    """配额检查中间件"""
    
    def process_request(self, request):
        """处理请求前检查配额"""
        if not hasattr(request, 'tenant'):
            return None
        
        tenant = request.tenant
        
        try:
            # 检查API速率限制
            QuotaService.check_api_rate_limit(tenant)
            
            # 检查并发会话限制
            if request.user.is_authenticated:
                session_id = f"{tenant.id}:{request.user.id}"
                QuotaService.check_concurrent_sessions(tenant, session_id)
            
            return None
            
        except RateLimitExceededError as e:
            logger.warning(f"Rate limit exceeded for tenant {tenant.id}: {e}")
            return JsonResponse({
                'error': 'rate_limit_exceeded',
                'message': str(e),
                'quota_type': e.quota_type,
                'current': e.current,
                'limit': e.limit,
                'retry_after': 3600  # 1小时后重试
            }, status=429)
            
        except QuotaExceededError as e:
            logger.warning(f"Quota exceeded for tenant {tenant.id}: {e}")
            return JsonResponse({
                'error': 'quota_exceeded',
                'message': str(e),
                'quota_type': e.quota_type,
                'current': e.current,
                'limit': e.limit,
                'additional': e.additional
            }, status=403)
    
    def process_response(self, request, response):
        """处理响应后清理资源"""
        if hasattr(request, 'tenant') and request.user.is_authenticated:
            # 这里可以添加响应后的配额处理逻辑
            pass
        
        return response
```

## 2. 移动端H5详细设计

### 2.1 前端架构设计

#### 2.1.1 项目结构
```
frontend/
├── public/                    # 静态资源
│   ├── index.html            # 入口HTML
│   ├── manifest.json         # PWA清单
│   ├── robots.txt
│   └── favicon.ico
├── src/
│   ├── main.tsx              # 应用入口
│   ├── App.tsx               # 根组件
│   ├── index.css             # 全局样式
│   ├── vite-env.d.ts         # Vite类型声明
│   ├── assets/               # 静态资源
│   │   ├── images/           # 图片资源
│   │   ├── fonts/            # 字体文件
│   │   └── styles/           # 样式文件
│   ├── components/           # 通用组件
│   │   ├── ui/               # UI基础组件
│   │   │   ├── Button/
│   │   │   ├── Input/
│   │   │   ├── Modal/
│   │   │   └── ...
│   │   ├── layout/           # 布局组件
│   │   │   ├── Header/
│   │   │   ├── Footer/
│   │   │   ├── Sidebar/
│   │   │   └── ...
│   │   └── shared/           # 共享组件
│   │       ├── LoadingSpinner/
│   │       ├── ErrorBoundary/
│   │       └── ...
│   ├── pages/                # 页面组件
│   │   ├── Home/             # 首页
│   │   ├── Auth/             # 认证页面
│   │   ├── Training/         # 训练页面
│   │   ├── Family/           # 家庭管理
│   │   ├── Profile/          # 个人资料
│   │   └── ...
│   ├── hooks/                # 自定义Hooks
│   │   ├── useMediaDevices.ts
│   │   ├── useNetworkStatus.ts
│   │   ├── useWebRTC.ts
│   │   └── ...
│   ├── services/             # 服务层
│   │   ├── api/              # API服务
│   │   │   ├── auth.ts
│   │   │   ├── exercises.ts
│   │   │   ├── family.ts
│   │   │   └── ...
│   │   ├── websocket/        # WebSocket服务
│   │   ├── webrtc/           # WebRTC服务
│   │   └── storage/          # 存储服务
│   ├── stores/               # 状态管理
│   │   ├── auth.store.ts     # 认证状态
│   │   ├── user.store.ts     # 用户状态
│   │   ├── training.store.ts # 训练状态
│   │   └── ...
│   ├── utils/                # 工具函数
│   │   ├── device.ts         # 设备工具
│   │   ├── validation.ts     # 验证工具
│   │   ├── formatters.ts     # 格式化工具

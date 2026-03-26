# CoachAI 技术架构概要设计 v2.0
## 基于SaaS多租户、移动端H5、硬件外设集成的技术方案

## 📋 文档信息

| 项目 | 内容 |
|------|------|
| **文档名称** | CoachAI 技术架构概要设计 v2.0 |
| **文档版本** | 2.0.0 |
| **创建日期** | 2026-03-26 |
| **最后更新** | 2026-03-26 |
| **文档状态** | 正式版 |
| **作者** | CoachAI-RD (后端研发专家) |
| **审核人** | 待定 |
| **关联文档** | [BRD.md](../pm/BRD.md), [PRD.md](../pm/PRD.md) |
| **目标读者** | 技术团队、产品团队、测试团队 |

## 📝 修订历史

| 版本 | 日期 | 作者 | 变更描述 |
|------|------|------|----------|
| 1.0.0 | 2026-03-21 | baofengbaofeng | 初始版本创建 (简化架构) |
| 2.0.0 | 2026-03-26 | CoachAI-RD | 基于新需求重构：SaaS多租户、移动端H5、硬件外设集成 |

## 🎯 核心需求变更摘要

### 1. SaaS多租户模式
- **租户单位**: 家庭为租户，一个家庭对应一个租户
- **数据隔离**: 家庭间数据完全隔离
- **成员管理**: 支持家庭成员角色定义（家长、成人、青少年、儿童、老人）
- **订阅模式**: 按家庭订阅，支持不同家庭成员数量

### 2. 移动端H5访问
- **仅支持移动端**: 不开发桌面端和原生App
- **H5优先**: 移动端H5页面为主要访问方式
- **移动优化**: 针对移动端进行深度性能优化
- **PWA支持**: 支持渐进式Web应用特性

### 3. 硬件外设集成
- **核心外设**: 麦克风和摄像头为必需硬件外设
- **可选外设**: 心率监测、运动传感器、环境传感器
- **硬件规格**: 详细的技术规格和兼容性要求
- **集成要求**: WebRTC支持、设备检测、权限管理

## 📊 目录

1. [架构设计原则](#1-架构设计原则)
2. [整体架构概述](#2-整体架构概述)
3. [技术栈选型对比](#3-技术栈选型对比)
4. [SaaS多租户架构设计](#4-saas多租户架构设计)
5. [移动端H5技术方案](#5-移动端h5技术方案)
6. [硬件外设集成方案](#6-硬件外设集成方案)
7. [系统模块划分](#7-系统模块划分)
8. [数据架构设计](#8-数据架构设计)
9. [部署架构设计](#9-部署架构设计)
10. [性能优化策略](#10-性能优化策略)
11. [扩展性设计](#11-扩展性设计)
12. [落地路径规划](#12-落地路径规划)

---

## 1. 架构设计原则

### 1.1 核心设计原则

#### 1.1.1 SaaS多租户原则
- **数据隔离**: 确保家庭租户间数据完全隔离
- **资源隔离**: 租户间资源使用隔离，避免相互影响
- **配置独立**: 支持租户级配置自定义
- **计费灵活**: 支持按家庭规模和功能计费

#### 1.1.2 移动端H5优先原则
- **移动优先**: 所有设计以移动端体验为核心
- **性能优化**: 针对移动网络和设备进行深度优化
- **离线可用**: 支持PWA，基础功能离线可用
- **硬件访问**: 优化移动端硬件设备访问体验

#### 1.1.3 硬件集成原则
- **标准化接口**: 使用Web标准API访问硬件
- **兼容性优先**: 支持主流硬件设备
- **隐私安全**: 硬件访问权限和隐私保护
- **故障容错**: 硬件故障时的降级处理

### 1.2 技术选型原则

#### 1.2.1 成熟稳定
- **生产验证**: 选择经过大规模生产验证的技术
- **社区活跃**: 选择有活跃社区支持的技术
- **文档完善**: 选择有完善文档的技术
- **生态丰富**: 选择生态丰富的技术栈

#### 1.2.2 开发效率
- **开发体验**: 提供良好的开发体验
- **调试便利**: 支持方便的调试和测试
- **部署简单**: 部署流程简单明了
- **维护成本**: 长期维护成本可控

#### 1.2.3 扩展性
- **水平扩展**: 支持水平扩展应对用户增长
- **垂直扩展**: 支持垂直扩展提升单机性能
- **功能扩展**: 支持新功能快速迭代
- **技术演进**: 支持技术栈平滑演进

## 2. 整体架构概述

### 2.1 架构视图

#### 2.1.1 逻辑架构
```
┌─────────────────────────────────────────────────────────┐
│                   移动端H5客户端层                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   React PWA │  │ 微信浏览器  │  │ 其他浏览器  │    │
│  │  (TypeScript)│  │  (H5页面)  │  │  (H5页面)   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────┘
                    │ HTTP/WebSocket/WebRTC
┌─────────────────────────────────────────────────────────┐
│                SaaS多租户后端服务层                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Django多租户应用                    │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │   │
│  │  │ 租户管理    │ │ 硬件集成    │ │ AI服务    │  │   │
│  │  │ (Django     │ │ (WebRTC/    │ │ (MediaPipe│  │   │
│  │  │  Tenants)   │ │  Web Audio) │ │ /Whisper) │  │   │
│  │  └─────────────┘ └─────────────┘ └───────────┘  │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │   │
│  │  │ 家庭管理    │ │ 运动管理    │ │ 任务系统  │  │   │
│  │  │ (家庭成员)  │ │ (实时训练)  │ │ (成就)    │  │   │
│  │  └─────────────┘ └─────────────┘ └───────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────────────────┐
│                   数据存储层                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ PostgreSQL  │  │   Redis     │  │   MinIO     │    │
│  │ (多租户隔离)│  │  (缓存/队列) │  │ (文件存储)  │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────┘
```

#### 2.1.2 数据流架构
```
移动端H5 → WebRTC音视频流 → 后端AI处理 → 实时反馈
        ↓
家庭租户请求 → 租户路由 → 业务处理 → 数据库操作
        ↓
硬件设备 → 设备检测 → 权限管理 → 功能调用
```

### 2.2 核心组件说明

#### 2.2.1 移动端H5客户端
- **React PWA**: 提供类原生App体验
- **WebRTC集成**: 摄像头和麦克风访问
- **离线功能**: 基础功能离线可用
- **移动优化**: 针对移动端的性能优化

#### 2.2.2 SaaS多租户后端
- **Django Tenants**: 多租户数据隔离
- **租户路由**: 基于子域名或路径的租户路由
- **资源隔离**: 租户间资源使用隔离
- **计费管理**: 租户订阅和计费管理

#### 2.2.3 硬件集成服务
- **WebRTC服务**: 音视频通信服务
- **设备管理**: 硬件设备检测和管理
- **权限控制**: 硬件访问权限控制
- **质量监控**: 音视频质量监控

#### 2.2.4 AI服务层
- **MediaPipe**: 动作识别和分析
- **Whisper**: 语音识别和处理
- **实时分析**: 实时运动数据分析
- **个性化推荐**: 基于用户数据的智能推荐

## 3. 技术栈选型对比

### 3.1 多租户方案选型对比

| 方案 | 技术 | 优点 | 缺点 | 选择理由 |
|------|------|------|------|----------|
| **方案A** | 数据库Schema隔离 | 1. 数据完全隔离<br>2. 备份恢复简单<br>3. 性能影响小 | 1. 迁移复杂<br>2. 连接数多 | ✅ **选择**：数据安全最重要 |
| **方案B** | 表级租户ID | 1. 迁移简单<br>2. 连接数少 | 1. 数据隔离弱<br>2. 查询复杂 | ❌ 不选：数据隔离不足 |
| **方案C** | 数据库实例隔离 | 1. 完全隔离<br>2. 性能最好 | 1. 成本高<br>2. 管理复杂 | ❌ 不选：成本过高 |

**最终选择**: **Django Tenants + PostgreSQL Schema隔离**
- 使用`django-tenants`库实现Schema级多租户
- 每个家庭租户一个独立的数据库Schema
- 数据完全隔离，安全性高
- 支持租户级备份和恢复

### 3.2 移动端H5框架选型对比

| 方案 | 技术栈 | 优点 | 缺点 | 选择理由 |
|------|--------|------|------|----------|
| **方案A** | React + TypeScript + Vite | 1. 生态丰富<br>2. 性能优秀<br>3. 开发体验好 | 1. 学习曲线陡<br>2. 包体积较大 | ✅ **选择**：生态和性能最佳 |
| **方案B** | Vue 3 + TypeScript + Vite | 1. 学习曲线平缓<br>2. 文档完善 | 1. 生态相对较小<br>2. 企业应用案例少 | ❌ 不选：企业级应用支持不足 |
| **方案C** | Svelte + Vite | 1. 包体积小<br>2. 编译时优化 | 1. 生态不成熟<br>2. 企业案例少 | ❌ 不选：生态不成熟 |

**最终选择**: **React 18 + TypeScript + Vite + PWA**
- React生态丰富，社区活跃
- TypeScript提供类型安全
- Vite提供优秀的开发体验
- PWA支持离线功能和类原生体验

### 3.3 硬件集成方案选型对比

| 方案 | 技术 | 优点 | 缺点 | 选择理由 |
|------|------|------|------|----------|
| **方案A** | WebRTC原生API | 1. 浏览器原生支持<br>2. 延迟低<br>3. 无需插件 | 1. 兼容性需处理<br>2. 代码复杂度高 | ✅ **选择**：标准方案，未来兼容性好 |
| **方案B** | 第三方SDK | 1. 功能完整<br>2. 兼容性好 | 1. 成本高<br>2. 依赖第三方 | ❌ 不选：成本和控制权问题 |
| **方案C** | 自定义协议 | 1. 完全可控<br>2. 定制灵活 | 1. 开发成本高<br>2. 兼容性差 | ❌ 不选：开发成本过高 |

**最终选择**: **WebRTC + Web Audio API**
- 浏览器原生支持，无需插件
- 延迟低，适合实时交互
- 标准协议，未来兼容性好
- 结合Web Audio API提供音频处理

### 3.4 AI技术栈选型对比

| 方案 | 技术 | 优点 | 缺点 | 选择理由 |
|------|------|------|------|----------|
| **方案A** | MediaPipe + Whisper | 1. Google/OpenAI出品<br>2. 准确率高<br>3. Python原生 | 1. 资源消耗大<br>2. 部署复杂 | ✅ **选择**：准确率最重要 |
| **方案B** | OpenPose + CMU Sphinx | 1. 开源免费<br>2. 可定制性强 | 1. 准确率一般<br>2. 维护成本高 | ❌ 不选：准确率不足 |
| **方案C** | 第三方API | 1. 部署简单<br>2. 维护成本低 | 1. 成本高<br>2. 数据隐私问题 | ❌ 不选：成本和数据隐私问题 |

**最终选择**: **MediaPipe + Whisper + 自定义模型**
- MediaPipe提供准确的动作识别
- Whisper提供高质量的语音识别
- 自定义模型针对健身场景优化
- 本地部署保证数据隐私

## 4. SaaS多租户架构设计

### 4.1 多租户实现方案

#### 4.1.1 数据库Schema隔离设计
```python
# settings.py
INSTALLED_APPS = [
    'django_tenants',  # 多租户支持
    'django.contrib.contenttypes',
    'django.contrib.auth',
    # ... 其他应用
]

# 多租户配置
TENANT_MODEL = "accounts.Tenant"
TENANT_DOMAIN_MODEL = "accounts.Domain"

# 共享应用（所有租户共享）
SHARED_APPS = [
    'django_tenants',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# 租户应用（每个租户独立）
TENANT_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'accounts',
    'exercises',
    'tasks',
    'achievements',
    'services',
]

# 数据库路由
DATABASE_ROUTERS = ('django_tenants.routers.TenantSyncRouter',)
```

#### 4.1.2 租户模型设计
```python
# models.py
from django_tenants.models import TenantMixin, DomainMixin

class Tenant(TenantMixin):
    """家庭租户模型"""
    name = models.CharField(max_length=100)
    family_type = models.CharField(max_length=50, choices=[
        ('core', '核心家庭'),
        ('couple', '年轻夫妻'),
        ('extended', '三代同堂'),
        ('single', '单身家庭'),
    ])
    max_members = models.IntegerField(default=5)
    subscription_plan = models.CharField(max_length=50, choices=[
        ('basic', '基础版'),
        ('premium', '高级版'),
        ('professional', '专业版'),
    ])
    subscription_status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    auto_create_schema = True

class Domain(DomainMixin):
    """租户域名模型"""
    pass

class FamilyMember(models.Model):
    """家庭成员模型"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[
        ('admin', '家庭管理员'),
        ('adult', '成人成员'),
        ('teenager', '青少年成员'),
        ('child', '儿童成员'),
        ('elder', '老年成员'),
    ])
    relationship = models.CharField(max_length=50, blank=True)
    permissions = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 4.1.3 租户路由中间件
```python
# middleware.py
from django_tenants.middleware import TenantMainMiddleware

class CustomTenantMiddleware(TenantMainMiddleware):
    """自定义租户中间件"""
    
    def get_tenant(self, model, hostname, request):
        # 基于子域名获取租户
        subdomain = hostname.split('.')[0]
        try:
            return model.objects.get(domain__domain=subdomain)
        except model.DoesNotExist:
            # 默认租户或错误处理
            return None
```

### 4.2 租户数据隔离策略

#### 4.2.1 数据访问控制
```python
# views.py
from django_tenants.utils import tenant_context

class FamilyExerciseView(APIView):
    """家庭运动视图，自动限制在当前租户"""
    
    def get_queryset(self):
        # 自动限制在当前租户的范围内
        return ExerciseRecord.objects.all()
    
    def list(self, request):
        # 只能看到当前租户的数据
        queryset = self.get_queryset()
        serializer = ExerciseRecordSerializer(queryset, many=True)
        return Response(serializer.data)

# 跨租户数据访问（管理员权限）
class AdminExerciseView(APIView):
    """管理员视图，可以访问所有租户数据"""
    
    @tenant_context(tenant=None)  # 禁用租户过滤
    def list(self, request):
        queryset = ExerciseRecord.objects.all()
        serializer = ExerciseRecordSerializer(queryset, many=True)
        return Response(serializer.data)
```

#### 4.2.2 租户资源配额管理
```python
# quota_manager.py
class TenantQuotaManager:
    """租户资源配额管理"""
    
    def __init__(self, tenant):
        self.tenant = tenant
    
    def check_storage_quota(self, file_size):
        """检查存储配额"""
        plan_limits = {
            'basic': 10 * 1024 * 1024 * 1024,  # 10GB
            'premium': 50 * 1024 * 1024 * 1024,  # 50GB
            'professional': 200 * 1024 * 1024 * 1024,  # 200GB
        }
        
        used_storage = self.get_used_storage()
        limit = plan_limits.get(self.tenant.subscription_plan, 0)
        
        return used_storage + file_size <= limit
    
    def check_member_quota(self):
        """检查成员数量配额"""
        plan_limits = {
            'basic': 5,
            'premium': 10,
            'professional': 20,
        }
        
        current_members = FamilyMember.objects.filter(tenant=self.tenant).count()
        limit = plan_limits.get(self.tenant.subscription_plan, 0)
        
        return current_members < limit
    
    def get_used_storage(self):
        """获取已使用存储"""
        # 计算租户所有文件大小
        total_size = 0
        # ... 实现存储计算逻辑
        return total_size
```

### 4.3 租户生命周期管理

#### 4.3.1 租户创建流程
```python
# tenant_service.py
class TenantService:
    """租户服务"""
    
    @staticmethod
    def create_tenant(family_data, admin_user):
        """创建新租户"""
        # 1. 创建租户记录
        tenant = Tenant.objects.create(
            name=family_data['name'],
            family_type=family_data['family_type'],
            max_members=family_data.get('max_members', 5),
            subscription_plan=family_data.get('subscription_plan', 'basic'),
            subscription_status='active',
        )
        
        # 2. 创建租户Schema
        tenant.create_schema()
        
        # 3. 创建域名记录
        domain = Domain.objects.create(
            domain=f"{tenant.schema_name}.coachai.com",
            tenant=tenant,
            is_primary=True,
        )
        
        # 4. 添加管理员为家庭成员
        FamilyMember.objects.create(
            tenant=tenant,
            user=admin_user,
            role='admin',
            relationship='admin',
            permissions={'all': True},
        )
        
        # 5. 初始化租户数据
        with tenant_context(tenant):
            TenantService.initialize_tenant_data(tenant)
        
        return tenant
    
    @staticmethod
    def initialize_tenant_data(tenant):
        """初始化租户数据"""
        # 创建默认运动计划
        default_plans = [
            {'name': '家庭基础训练', 'difficulty': 'beginner'},
            {'name': '亲子互动训练', 'difficulty': 'easy'},
            {'name': '全家健康计划', 'difficulty': 'medium'},
        ]
        
        for plan_data in default_plans:
            TrainingPlan.objects.create(
                name=plan_data['name'],
                difficulty=plan_data['difficulty'],
                is_default=True,
            )
        
        # 创建默认成就
        default_achievements = [
            {'name': '家庭健身起步', 'points': 100},
            {'name': '亲子运动达人', 'points': 200},
            {'name': '全家健康卫士', 'points': 300},
        ]
        
        for achievement_data in default_achievements:
            Achievement.objects.create(
                name=achievement_data['name'],
                points=achievement_data['points'],
                is_default=True,
            )
```

#### 4.3.2 租户迁移和备份
```python
# tenant_migration.py
class TenantMigrationService:
    """租户迁移服务"""
    
    @staticmethod
    def backup_tenant(tenant_id):
        """备份租户数据"""
        tenant = Tenant.objects.get(id=tenant_id)
        
        # 1. 锁定租户（禁止写入）
        tenant.is_locked = True
        tenant.save()
        
        # 2. 导出数据库Schema
        with tenant_context(tenant):
            backup_data = {
                'schema_name': tenant.schema_name,
                'backup_time': timezone.now(),
                'tables': {},
            }
            
            # 导出所有表数据
            for model in apps.get_models():
                if model._meta.app_label in TENANT_APPS:
                    table_name = model._meta.db_table
                    backup_data['tables'][table_name] = list(
                        model.objects.all().values()
                    )
        
        # 3. 导出文件存储
        file_backup = TenantMigrationService.backup_tenant_files(tenant)
        
        # 4. 解锁租户
        tenant.is_locked = False
        tenant.save()
        
        return {
            'database': backup_data,
            'files': file_backup,
        }
    
    @staticmethod
    def restore_tenant(tenant_id, backup_data):
        """恢复租户数据"""
        tenant = Tenant.objects.get(id=tenant_id)
        
        # 1. 清空现有数据
        with tenant_context(tenant):
            for model in reversed(apps.get_models()):
                if model._meta.app_label in TENANT_APPS:
                    model.objects.all().delete()
        
        # 2. 恢复数据库数据
        with tenant_context(tenant):
            for table_name, records in backup_data['database']['tables'].items():
                # 找到对应的模型
                for model in apps.get_models():
                    if model._meta.db_table == table_name:
                        for record in records:
                            model.objects.create(**record)
                        break
        
        # 3. 恢复文件存储
        TenantMigrationService.restore_tenant_files(tenant, backup_data['files'])
        
        return True
```

## 5. 移动端H5技术方案

### 5.1 前端架构设计

#### 5.1.1 技术栈配置
```json
// package.json 核心依赖
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "react-router-dom": "^6.0.0",
    "axios": "^1.6.0",
    "zustand": "^4.4.0",
    "react-query": "^3.0.0",
    "tailwindcss": "^3.3.0",
    "framer-motion": "^10.0.0",
    "react-hook-form": "^7.0.0",
    "zod": "^3.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0",
    "vite-plugin-pwa": "^0.17.0"
  }
}
```

#### 5.1.2 PWA配置
```javascript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'CoachAI - 家庭智能健身教练',
        short_name: 'CoachAI',
        description: '基于AI的家庭智能健身教练系统',
        theme_color: '#4F46E5',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 365 // 一年
              }
            }
          },
          {
            urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'gstatic-fonts-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 365
              }
            }
          },
          {
            urlPattern: /\/api\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              networkTimeoutSeconds: 10,
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 5 // 5分钟
              }
            }
          }
        ]
      }
    })
  ],
  build: {
    target: 'es2020',
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['@headlessui/react', '@heroicons/react'],
          state: ['zustand', 'react-query'],
          forms: ['react-hook-form', 'zod']
        }
      }
    }
  }
})
```

### 5.2 移动端性能优化

#### 5.2.1 代码分割和懒加载
```typescript
// App.tsx
import React, { Suspense, lazy } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LoadingSpinner from './components/LoadingSpinner'

// 懒加载页面组件
const HomePage = lazy(() => import('./pages/HomePage'))
const TrainingPage = lazy(() => import('./pages/TrainingPage'))
const FamilyPage = lazy(() => import('./pages/FamilyPage'))
const ProfilePage = lazy(() => import('./pages/ProfilePage'))
const ExerciseDetailPage = lazy(() => import('./pages/ExerciseDetailPage'))

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/training" element={<TrainingPage />} />
          <Route path="/family" element={<FamilyPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/exercise/:id" element={<ExerciseDetailPage />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}

export default App
```

#### 5.2.2 图片和资源优化
```typescript
// components/ImageOptimizer.tsx
import React from 'react'

interface ImageOptimizerProps {
  src: string
  alt: string
  width?: number
  height?: number
  className?: string
  lazy?: boolean
}

const ImageOptimizer: React.FC<ImageOptimizerProps> = ({
  src,
  alt,
  width,
  height,
  className,
  lazy = true
}) => {
  // 根据设备像素比和屏幕尺寸生成优化后的图片URL
  const getOptimizedSrc = () => {
    const dpr = window.devicePixelRatio || 1
    const screenWidth = window.innerWidth
    
    // 生成不同尺寸的图片URL
    if (src.includes('cloudinary')) {
      // Cloudinary图片优化
      const transformations = []
      
      if (width) transformations.push(`w_${width}`)
      if (height) transformations.push(`h_${height}`)
      
      // 根据DPR调整质量
      if (dpr > 1) {
        transformations.push(`q_auto:good`)
        transformations.push(`dpr_${Math.min(dpr, 2)}`)
      } else {
        transformations.push(`q_auto:eco`)
      }
      
      // WebP格式支持
      if (window.Modernizr && window.Modernizr.webp) {
        transformations.push('f_webp')
      }
      
      const transformStr = transformations.join(',')
      return src.replace('/upload/', `/upload/${transformStr}/`)
    }
    
    return src
  }

  return (
    <img
      src={getOptimizedSrc()}
      alt={alt}
      width={width}
      height={height}
      className={className}
      loading={lazy ? 'lazy' : 'eager'}
      decoding="async"
    />
  )
}

export default ImageOptimizer
```

#### 5.2.3 网络状态感知
```typescript
// hooks/useNetworkStatus.ts
import { useState, useEffect } from 'react'

interface NetworkStatus {
  isOnline: boolean
  effectiveType: string
  downlink: number
  rtt: number
  saveData: boolean
}

export function useNetworkStatus(): NetworkStatus {
  const [status, setStatus] = useState<NetworkStatus>({
    isOnline: navigator.onLine,
    effectiveType: '4g',
    downlink: 10,
    rtt: 50,
    saveData: false
  })

  useEffect(() => {
    const handleOnline = () => {
      setStatus(prev => ({ ...prev, isOnline: true }))
    }

    const handleOffline = () => {
      setStatus(prev => ({ ...prev, isOnline: false }))
    }

    const handleChange = () => {
      if ('connection' in navigator) {
        const connection = (navigator as any).connection
        setStatus({
          isOnline: navigator.onLine,
          effectiveType: connection.effectiveType,
          downlink: connection.downlink,
          rtt: connection.rtt,
          saveData: connection.saveData
        })
      } else {
        setStatus(prev => ({ ...prev, isOnline: navigator.onLine }))
      }
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    
    if ('connection' in navigator) {
      const connection = (navigator as any).connection
      connection.addEventListener('change', handleChange)
    }

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
      
      if ('connection' in navigator) {
        const connection = (navigator as any).connection
        connection.removeEventListener('change', handleChange)
      }
    }
  }, [])

  return status
}

// 使用示例
export function useAdaptiveLoading() {
  const network = useNetworkStatus()
  
  // 根据网络状况调整加载策略
  const getLoadingStrategy = () => {
    if (!network.isOnline) {
      return 'offline' // 使用离线缓存
    }
    
    if (network.effectiveType === 'slow-2g' || network.effectiveType === '2g') {
      return 'minimal' // 最小化加载
    }
    
    if (network.effectiveType === '3g') {
      return 'balanced' // 平衡加载
    }
    
    return 'full' // 完整加载
  }
  
  return {
    strategy: getLoadingStrategy(),
    network
  }
}
```

### 5.3 移动端硬件访问

#### 5.3.1 摄像头和麦克风访问
```typescript
// hooks/useMediaDevices.ts
import { useState, useEffect, useCallback } from 'react'

interface MediaDevice {
  deviceId: string
  kind: 'videoinput' | 'audioinput' | 'audiooutput'
  label: string
  groupId: string
}

interface MediaStreamConstraints {
  video: boolean | MediaTrackConstraints
  audio: boolean | MediaTrackConstraints
}

export function useMediaDevices() {
  const [devices, setDevices] = useState<MediaDevice[]>([])
  const [permission, setPermission] = useState<'granted' | 'denied' | 'prompt'>('prompt')
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [error, setError] = useState<Error | null>(null)

  // 获取设备列表
  const getDevices = useCallback(async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      const deviceList = await navigator.mediaDevices.enumerateDevices()
      setDevices(deviceList.map(device => ({
        deviceId: device.deviceId,
        kind: device.kind as 'videoinput' | 'audioinput' | 'audiooutput',
        label: device.label,
        groupId: device.groupId
      })))
      setPermission('granted')
    } catch (err) {
      setPermission('denied')
      setError(err as Error)
    }
  }, [])

  // 请求媒体访问权限
  const requestMedia = useCallback(async (constraints: MediaStreamConstraints) => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints)
      setStream(mediaStream)
      setPermission('granted')
      setError(null)
      return mediaStream
    } catch (err) {
      setPermission('denied')
      setError(err as Error)
      return null
    }
  }, [])

  // 停止媒体流
  const stopMedia = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
  }, [stream])

  // 切换摄像头
  const switchCamera = useCallback(async (deviceId: string) => {
    if (!stream) return null
    
    const videoTrack = stream.getVideoTracks()[0]
    if (videoTrack) {
      videoTrack.stop()
      
      const newStream = await navigator.mediaDevices.getUserMedia({
        video: { deviceId: { exact: deviceId } },
        audio: stream.getAudioTracks().length > 0
      })
      
      setStream(newStream)
      return newStream
    }
    
    return null
  }, [stream])

  useEffect(() => {
    getDevices()
    
    // 监听设备变化
    navigator.mediaDevices.addEventListener('devicechange', getDevices)
    
    return () => {
      navigator.mediaDevices.removeEventListener('devicechange', getDevices)
      stopMedia()
    }
  }, [getDevices, stopMedia])

  return {
    devices,
    permission,
    stream,
    error,
    requestMedia,
    stopMedia,
    switchCamera,
    getDevices
  }
}

// 使用示例：摄像头组件
import React, { useEffect, useRef } from 'react'
import { useMediaDevices } from '../hooks/useMediaDevices'

const CameraComponent: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null)
  const { devices, stream, requestMedia, stopMedia } = useMediaDevices()
  const videoDevices = devices.filter(d => d.kind === 'videoinput')

  useEffect(() => {
    if (stream && videoRef.current) {
      videoRef.current.srcObject = stream
    }
  }, [stream])

  const startCamera = async () => {
    await requestMedia({
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        frameRate: { ideal: 30 },
        facingMode: 'user'
      },
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    })
  }

  return (
    <div className="camera-container">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="camera-preview"
      />
      
      <div className="camera-controls">
        <button onClick={startCamera}>开启摄像头</button>
        <button onClick={stopMedia}>关闭摄像头</button>
        
        {videoDevices.length > 1 && (
          <select onChange={(e) => {
            // 切换摄像头逻辑
          }}>
            {videoDevices.map(device => (
              <option key={device.deviceId} value={device.deviceId}>
                {device.label || `摄像头 ${device.deviceId.slice(0, 8)}`}
              </option>
            ))}
          </select>
        )}
      </div>
    </div>
  )
}
```

#### 5.3.2 WebRTC音视频通信
```typescript
// services/WebRTCService.ts
class WebRTCService {
  private peerConnection: RTCPeerConnection | null = null
  private dataChannel: RTCDataChannel | null = null
  private iceCandidates: RTCIceCandidate[] = []
  private onTrackCallback: ((stream: MediaStream) => void) | null = null
  private onDataCallback: ((data: any) => void) | null = null

  constructor() {
    this.initializePeerConnection()
  }

  private initializePeerConnection() {
    const config: RTCConfiguration = {
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },
        // 生产环境使用TURN服务器
        // {
        //   urls: 'turn:your-turn-server.com',
        //   username: 'username',
        //   credential: 'password'
        // }
      ],
      iceCandidatePoolSize: 10
    }

    this.peerConnection = new RTCPeerConnection(config)

    // ICE候选收集
    this.peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        this.iceCandidates.push(event.candidate)
        // 发送ICE候选到信令服务器
        this.sendIceCandidate(event.candidate)
      }
    }

    // 远程流到达
    this.peerConnection.ontrack = (event) => {
      if (this.onTrackCallback) {
        this.onTrackCallback(event.streams[0])
      }
    }

    // 连接状态变化
    this.peerConnection.onconnectionstatechange = () => {
      console.log('Connection state:', this.peerConnection?.connectionState)
    }

    // ICE连接状态变化
    this.peerConnection.oniceconnectionstatechange = () => {
      console.log('ICE connection state:', this.peerConnection?.iceConnectionState)
    }
  }

  // 创建Offer
  async createOffer(stream: MediaStream): Promise<RTCSessionDescriptionInit> {
    if (!this.peerConnection) {
      throw new Error('Peer connection not initialized')
    }

    // 添加本地流
    stream.getTracks().forEach(track => {
      this.peerConnection!.addTrack(track, stream)
    })

    // 创建数据通道
    this.dataChannel = this.peerConnection.createDataChannel('coachai-data')
    this.setupDataChannel()

    // 创建Offer
    const offer = await this.peerConnection.createOffer({
      offerToReceiveAudio: true,
      offerToReceiveVideo: true
    })

    await this.peerConnection.setLocalDescription(offer)
    
    return offer
  }

  // 处理Answer
  async handleAnswer(answer: RTCSessionDescriptionInit) {
    if (!this.peerConnection) {
      throw new Error('Peer connection not initialized')
    }

    await this.peerConnection.setRemoteDescription(new RTCSessionDescription(answer))
  }

  // 处理ICE候选
  async addIceCandidate(candidate: RTCIceCandidateInit) {
    if (!this.peerConnection) {
      throw new Error('Peer connection not initialized')
    }

    await this.peerConnection.addIceCandidate(new RTCIceCandidate(candidate))
  }

  // 设置数据通道
  private setupDataChannel() {
    if (!this.dataChannel) return

    this.dataChannel.onopen = () => {
      console.log('Data channel opened')
    }

    this.dataChannel.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (this.onDataCallback) {
          this.onDataCallback(data)
        }
      } catch (error) {
        console.error('Failed to parse data channel message:', error)
      }
    }

    this.dataChannel.onclose = () => {
      console.log('Data channel closed')
    }
  }

  // 发送数据
  sendData(data: any) {
    if (this.dataChannel && this.dataChannel.readyState === 'open') {
      this.dataChannel.send(JSON.stringify(data))
    }
  }

  // 关闭连接
  close() {
    if (this.dataChannel) {
      this.dataChannel.close()
    }
    
    if (this.peerConnection) {
      this.peerConnection.close()
    }
    
    this.peerConnection = null
    this.dataChannel = null
    this.iceCandidates = []
  }

  // 设置回调
  setOnTrackCallback(callback: (stream: MediaStream) => void) {
    this.onTrackCallback = callback
  }

  setOnDataCallback(callback: (data: any) => void) {
    this.onDataCallback = callback
  }

  // 发送ICE候选（需要实现信令服务器通信）
  private sendIceCandidate(candidate: RTCIceCandidate) {
    // 实现信令服务器通信逻辑
    console.log('Sending ICE candidate:', candidate)
  }
}

export default WebRTCService
```

## 6. 硬件外设集成方案

### 6.1 硬件兼容性处理

#### 6.1.1 设备检测和兼容性检查
```typescript
// utils/deviceCompatibility.ts
export interface DeviceCapabilities {
  hasCamera: boolean
  hasMicrophone: boolean
  hasWebRTC: boolean
  hasWebAudio: boolean
  hasSensors: boolean
  browser: string
  browserVersion: string
  os: string
  isMobile: boolean
}

export class DeviceCompatibilityChecker {
  static async checkCapabilities(): Promise<DeviceCapabilities> {
    const capabilities: DeviceCapabilities = {
      hasCamera: false,
      hasMicrophone: false,
      hasWebRTC: false,
      hasWebAudio: false,
      hasSensors: false,
      browser: this.getBrowser(),
      browserVersion: this.getBrowserVersion(),
      os: this.getOS(),
      isMobile: this.isMobile()
    }

    // 检查WebRTC支持
    capabilities.hasWebRTC = !!(
      navigator.mediaDevices &&
      navigator.mediaDevices.getUserMedia &&
      window.RTCPeerConnection
    )

    // 检查Web Audio API支持
    capabilities.hasWebAudio = !!(window.AudioContext || (window as any).webkitAudioContext)

    // 检查传感器支持
    capabilities.hasSensors = !!(window.DeviceOrientationEvent || window.DeviceMotionEvent)

    // 检查摄像头和麦克风
    if (capabilities.hasWebRTC) {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices()
        capabilities.hasCamera = devices.some(d => d.kind === 'videoinput')
        capabilities.hasMicrophone = devices.some(d => d.kind === 'audioinput')
      } catch (error) {
        console.warn('Failed to enumerate devices:', error)
      }
    }

    return capabilities
  }

  static getBrowser(): string {
    const userAgent = navigator.userAgent
    if (userAgent.includes('Chrome') && !userAgent.includes('Edg')) return 'Chrome'
    if (userAgent.includes('Firefox')) return 'Firefox'
    if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) return 'Safari'
    if (userAgent.includes('Edg')) return 'Edge'
    return 'Unknown'
  }

  static getBrowserVersion(): string {
    const userAgent = navigator.userAgent
    const browser = this.getBrowser()
    
    switch (browser) {
      case 'Chrome':
        const chromeMatch = userAgent.match(/Chrome\/(\d+)/)
        return chromeMatch ? chromeMatch[1] : 'Unknown'
      case 'Firefox':
        const firefoxMatch = userAgent.match(/Firefox\/(\d+)/)
        return firefoxMatch ? firefoxMatch[1] : 'Unknown'
      case 'Safari':
        const safariMatch = userAgent.match(/Version\/(\d+)/)
        return safariMatch ? safariMatch[1] : 'Unknown'
      default:
        return 'Unknown'
    }
  }

  static getOS(): string {
    const userAgent = navigator.userAgent
    if (userAgent.includes('Android')) return 'Android'
    if (userAgent.includes('iPhone') || userAgent.includes('iPad')) return 'iOS'
    if (userAgent.includes('Windows')) return 'Windows'
    if (userAgent.includes('Mac')) return 'macOS'
    if (userAgent.includes('Linux')) return 'Linux'
    return 'Unknown'
  }

  static isMobile(): boolean {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
  }

  static async getRecommendedSettings(): Promise<MediaStreamConstraints> {
    const capabilities = await this.checkCapabilities()
    
    const constraints: MediaStreamConstraints = {
      video: false,
      audio: false
    }

    if (capabilities.hasCamera) {
      constraints.video = {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        frameRate: { ideal: 30 },
        facingMode: 'user'
      }

      // 移动端优化
      if (capabilities.isMobile) {
        if (capabilities.browser === 'Safari') {
          // Safari移动端限制
          constraints.video = {
            width: { ideal: 640 },
            height: { ideal: 480 },
            frameRate: { ideal: 24 }
          }
        }
      }
    }

    if (capabilities.hasMicrophone) {
      constraints.audio = {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        sampleRate: 48000,
        channelCount: 1
      }
    }

    return constraints
  }
}
```

#### 6.1.2 硬件故障处理和降级
```typescript
// services/HardwareFallbackService.ts
export class HardwareFallbackService {
  private fallbackStrategies: Map<string, FallbackStrategy> = new Map()
  private currentStrategy: string = 'optimal'
  private metrics: HardwareMetrics = {
    cameraFps: 0,
    audioLatency: 0,
    networkLatency: 0,
    cpuUsage: 0,
    memoryUsage: 0
  }

  constructor() {
    this.initializeStrategies()
    this.startMonitoring()
  }

  private initializeStrategies() {
    // 最优策略（全功能）
    this.fallbackStrategies.set('optimal', {
      name: 'optimal',
      video: {
        enabled: true,
        width: 1280,
        height: 720,
        fps: 30,
        bitrate: 2000000
      },
      audio: {
        enabled: true,
        sampleRate: 48000,
        channels: 1,
        bitrate: 128000
      },
      ai: {
        enabled: true,
        model: 'high_accuracy',
        frequency: 30
      }
    })

    // 平衡策略
    this.fallbackStrategies.set('balanced', {
      name: 'balanced',
      video: {
        enabled: true,
        width: 640,
        height: 480,
        fps: 24,
        bitrate: 1000000
      },
      audio: {
        enabled: true,
        sampleRate: 44100,
        channels: 1,
        bitrate: 96000
      },
      ai: {
        enabled: true,
        model: 'balanced',
        frequency: 15
      }
    })

    // 最小策略
    this.fallbackStrategies.set('minimal', {
      name: 'minimal',
      video: {
        enabled: false,
        width: 320,
        height: 240,
        fps: 15,
        bitrate: 500000
      },
      audio: {
        enabled: true,
        sampleRate: 22050,
        channels: 1,
        bitrate: 64000
      },
      ai: {
        enabled: false,
        model: 'basic',
        frequency: 5
      }
    })

    // 离线策略
    this.fallbackStrategies.set('offline', {
      name: 'offline',
      video: {
        enabled: false,
        width: 0,
        height: 0,
        fps: 0,
        bitrate: 0
      },
      audio: {
        enabled: false,
        sampleRate: 0,
        channels: 0,
        bitrate: 0
      },
      ai: {
        enabled: false,
        model: 'none',
        frequency: 0
      }
    })
  }

  private startMonitoring() {
    // 监控硬件性能
    setInterval(() => {
      this.updateMetrics()
      this.evaluateAndAdjustStrategy()
    }, 5000) // 每5秒检查一次
  }

  private updateMetrics() {
    // 实现硬件性能监控逻辑
    // 这里需要实际实现性能数据收集
    this.metrics = {
      cameraFps: this.getCameraFps(),
      audioLatency: this.getAudioLatency(),
      networkLatency: this.getNetworkLatency(),
      cpuUsage: this.getCpuUsage(),
      memoryUsage: this.getMemoryUsage()
    }
  }

  private evaluateAndAdjustStrategy() {
    const { cameraFps, audioLatency, networkLatency, cpuUsage } = this.metrics
    
    let newStrategy = this.currentStrategy

    // 评估条件并调整策略
    if (cpuUsage > 80 || networkLatency > 500) {
      newStrategy =
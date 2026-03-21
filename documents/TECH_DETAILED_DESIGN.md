# CoachAI 技术详细设计 (简化架构版本)

## 文档信息

| 项目 | 内容 |
|------|------|
| **文档名称** | CoachAI 技术详细设计 |
| **文档版本** | 3.0.0 |
| **创建日期** | 2026-03-21 |
| **最后更新** | 2026-03-21 |
| **文档状态** | 草案 |
| **作者** | baofengbaofeng |
| **审核人** | 待定 |
| **许可证** | GNU General Public License v3.0 |
| **关联文档** | [BRD.md](./BRD.md), [PRD.md](./PRD.md), [TECH_ARCHITECTURE_OVERVIEW.md](./TECH_ARCHITECTURE_OVERVIEW.md) |

## 修订历史

| 版本 | 日期 | 作者 | 变更描述 |
|------|------|------|----------|
| 3.0.0 | 2026-03-21 | baofengbaofeng | 简化架构版本，无中间件，GPL v3 许可证 |

## 重要说明

**架构简化原则**：
1. 无中间件架构：不引入 Redis、RabbitMQ 等中间件
2. 数据库中心化：使用数据库表实现缓存和队列功能
3. 简化部署：只需 Django + MySQL，部署维护简单
4. 开源要求：采用 GPL v3 许可证，代码必须持续开源

## 目录

1. [Django 项目详细设计](#1-django-项目详细设计)
2. [MySQL 数据库详细设计](#2-mysql-数据库详细设计)
3. [Django REST API 详细设计](#3-django-rest-api-详细设计)
4. [异步任务系统设计](#4-异步任务系统设计)
5. [文件存储系统设计](#5-文件存储系统设计)
6. [AI 服务集成设计](#6-ai-服务集成设计)
7. [安全设计](#7-安全设计)
8. [性能优化设计](#8-性能优化设计)
9. [部署配置设计](#9-部署配置设计)
10. [测试设计](#10-测试设计)

---

## 1. Django 项目详细设计

### 1.1 项目结构设计

#### 1.1.1 项目目录结构
```
coachai/
├── coachai/                    # 项目配置目录
│   ├── __init__.py
│   ├── settings/              # 多环境配置
│   │   ├── __init__.py
│   │   ├── base.py           # 基础配置
│   │   ├── development.py    # 开发环境
│   │   ├── production.py     # 生产环境
│   │   └── testing.py        # 测试环境
│   ├── urls.py               # 主 URL 配置
│   ├── asgi.py               # ASGI 配置
│   └── wsgi.py               # WSGI 配置
├── apps/                      # 业务应用目录
│   ├── accounts/             # 用户管理
│   ├── homework/             # 作业管理
│   ├── exercise/             # 运动管理
│   ├── tasks/                # 任务管理
│   ├── achievements/         # 成就系统
│   └── common/               # 公共组件
├── services/                  # 服务层
│   ├── ocr_service.py        # OCR 服务
│   ├── cv_service.py         # 计算机视觉服务
│   └── speech_service.py     # 语音服务
├── utils/                     # 工具函数
│   ├── cache.py              # 数据库缓存
│   ├── tasks.py              # 异步任务处理
│   └── validators.py         # 数据验证
├── templates/                 # 模板文件
├── static/                    # 静态文件
├── media/                     # 媒体文件
├── requirements/              # 依赖管理
│   ├── base.txt              # 基础依赖
│   ├── development.txt       # 开发依赖
│   └── production.txt        # 生产依赖
├── docker/                    # Docker 配置
├── scripts/                   # 部署脚本
├── tests/                     # 测试文件
├── manage.py                  # Django 管理命令
├── pyproject.toml            # Poetry 配置
├── .env.example              # 环境变量示例
└── .gitignore                # Git 忽略文件
```

#### 1.1.2 依赖管理 (requirements/base.txt)
```
# Django 核心
Django==5.0.2
djangorestframework==3.15.1
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
drf-yasg==1.21.7
django-filter==23.5

# 数据库
mysqlclient==2.2.4
django-environ==0.11.2

# 异步和实时
channels==4.0.0
channels-redis==4.1.0  # 可选，未来扩展
daphne==4.0.0

# AI 相关
paddleocr==2.7.0.3
easyocr==1.7.1
opencv-python==4.9.0.80
mediapipe==0.10.8
openai-whisper==20231117
SpeechRecognition==3.10.1

# 工具类
Pillow==10.2.0
python-magic==0.4.27
celery==5.3.6
redis==5.0.1  # 可选，未来扩展

# 开发工具
black==23.12.1
flake8==7.0.0
pytest==7.4.4
pytest-django==4.7.0
```

### 1.2 Django 应用设计

#### 1.2.1 用户管理应用 (accounts)
**功能范围**：
- 用户注册、登录、认证
- 个人资料管理
- 权限和角色管理
- 家庭关系管理（家长-学生）

**模型设计**：
```python
# apps/accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """扩展的用户模型"""
    
    class Role(models.TextChoices):
        STUDENT = 'student', _('学生')
        PARENT = 'parent', _('家长')
        TEACHER = 'teacher', _('老师')
        ADMIN = 'admin', _('管理员')
    
    # 基础信息
    email = models.EmailField(_('邮箱'), unique=True, db_index=True)
    phone = models.CharField(_('手机号'), max_length=20, blank=True, null=True)
    
    # 角色信息
    role = models.CharField(
        _('角色'),
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        db_index=True
    )
    
    # 学生信息
    age = models.IntegerField(_('年龄'), blank=True, null=True)
    grade = models.CharField(_('年级'), max_length=20, blank=True, null=True)
    school = models.CharField(_('学校'), max_length=100, blank=True, null=True)
    
    # 家长信息
    children = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='parents',
        blank=True
    )
    
    # 用户设置
    avatar = models.ImageField(
        _('头像'),
        upload_to='avatars/',
        blank=True,
        null=True
    )
    settings = models.JSONField(_('设置'), default=dict, blank=True)
    
    # 时间戳
    last_login_at = models.DateTimeField(_('最后登录时间'), blank=True, null=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    # 状态
    is_verified = models.BooleanField(_('已验证'), default=False)
    
    class Meta:
        db_table = 'users'
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['role']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'
    
    @property
    def is_student(self):
        return self.role == self.Role.STUDENT
    
    @property
    def is_parent(self):
        return self.role == self.Role.PARENT
    
    def get_display_name(self):
        """获取显示名称"""
        if self.first_name and self.last_name:
            return f'{self.last_name}{self.first_name}'
        return self.username
```

#### 1.2.2 作业管理应用 (homework)
**功能范围**：
- 作业上传和管理
- 作业批改状态跟踪
- 学习报告生成
- 错题本管理

**模型设计**：
```python
# apps/homework/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _


class Homework(models.Model):
    """作业模型"""
    
    class Status(models.TextChoices):
        UPLOADED = 'uploaded', _('已上传')
        PROCESSING = 'processing', _('处理中')
        GRADED = 'graded', _('已批改')
        ERROR = 'error', _('错误')
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='homeworks',
        verbose_name=_('用户')
    )
    
    # 作业信息
    subject = models.CharField(_('科目'), max_length=50)
    title = models.CharField(_('标题'), max_length=200)
    description = models.TextField(_('描述'), blank=True)
    
    # 文件信息
    image_files = models.JSONField(_('图片文件'), default=list)
    original_filenames = models.JSONField(_('原始文件名'), default=list)
    
    # 状态信息
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=Status.choices,
        default=Status.UPLOADED,
        db_index=True
    )
    
    # 批改结果
    grade_result = models.JSONField(_('批改结果'), blank=True, null=True)
    total_questions = models.IntegerField(_('总题数'), blank=True, null=True)
    correct_questions = models.IntegerField(_('正确题数'), blank=True, null=True)
    score = models.DecimalField(
        _('分数'),
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )
    feedback = models.TextField(_('反馈'), blank=True)
    
    # 时间戳
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    processed_at = models.DateTimeField(_('处理时间'), blank=True, null=True)
    
    class Meta:
        db_table = 'homeworks'
        verbose_name = _('作业')
        verbose_name_plural = _('作业')
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['subject']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.subject} - {self.title}'


class Question(models.Model):
    """题目模型"""
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name=_('作业')
    )
    
    # 题目信息
    question_number = models.IntegerField(_('题号'))
    question_text = models.TextField(_('题目内容'))
    student_answer = models.TextField(_('学生答案'), blank=True)
    correct_answer = models.TextField(_('正确答案'), blank=True, null=True)
    
    # 批改信息
    is_correct = models.BooleanField(_('是否正确'), blank=True, null=True)
    points = models.DecimalField(
        _('得分'),
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )
    feedback = models.TextField(_('反馈'), blank=True)
    
    # 知识点
    knowledge_points = models.JSONField(_('知识点'), default=list)
    
    class Meta:
        db_table = 'questions'
        verbose_name = _('题目')
        verbose_name_plural = _('题目')
        unique_together = ['homework', 'question_number']
        ordering = ['question_number']
```

#### 1.2.3 运动管理应用 (exercise)
**功能范围**：
- 运动记录管理
- 实时运动计数
- 运动数据统计
- 姿势评估和反馈

**模型设计**：
```python
# apps/exercise/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _


class ExerciseRecord(models.Model):
    """运动记录模型"""
    
    class ExerciseType(models.TextChoices):
        JUMP_ROPE = 'jump_rope', _('跳绳')
        PUSH_UP = 'push_up', _('俯卧撑')
        SIT_UP = 'sit_up', _('仰卧起坐')
        SQUAT = 'squat', _('深蹲')
        OTHER = 'other', _('其他')
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='exercise_records',
        verbose_name=_('用户')
    )
    
    # 运动信息
    exercise_type = models.CharField(
        _('运动类型'),
        max_length=20,
        choices=ExerciseType.choices,
        db_index=True
    )
    title = models.CharField(_('标题'), max_length=200, blank=True)
    
    # 时间信息
    start_time = models.DateTimeField(_('开始时间'), db_index=True)
    end_time = models.DateTimeField(_('结束时间'), blank=True, null=True)
    duration_seconds = models.IntegerField(_('持续时间(秒)'), blank=True, null=True)
    
    # 计数信息
    total_count = models.IntegerField(_('总计数'), default=0)
    valid_count = models.IntegerField(_('有效计数'), default=0)
    average_frequency = models.DecimalField(
        _('平均频率(次/分钟)'),
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    # 评估信息
    posture_score = models.DecimalField(
        _('姿势评分'),
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )
    feedback = models.TextField(_('反馈'), blank=True)
    
    # 文件信息
    video_file = models.FileField(
        _('视频文件'),
        upload_to='exercises/',
        blank=True,
        null=True
    )
    thumbnail = models.ImageField(
        _('缩略图'),
        upload_to='exercise_thumbnails/',
        blank=True,
        null=True
    )
    
    # 数据点
    data_points = models.JSONField(_('数据点'), default=list)
    
    # 时间戳
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        db_table = 'exercise_records'
        verbose_name = _('运动记录')
        verbose_name_plural = _('运动记录')
        indexes = [
            models.Index(fields=['user', 'start_time']),
            models.Index(fields=['exercise_type']),
        ]
        ordering = ['-start_time']
    
    def __str__(self):
        return f'{self.user.username} - {self.get_exercise_type_display()} - {self.start_time}'
    
    def save(self, *args, **kwargs):
        # 计算持续时间
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            self.duration_seconds = int(duration.total_seconds())
        super().save(*args, **kwargs)


class ExerciseDataPoint(models.Model):
    """运动数据点模型"""
    record = models.ForeignKey(
        ExerciseRecord,
        on_delete=models.CASCADE,
        related_name='detailed_data_points',
        verbose_name=_('运动记录')
    )
    
    # 时间信息
    timestamp = models.DateTimeField(_('时间戳'), db_index=True)
    relative_time_ms = models.IntegerField(_('相对时间(毫秒)'))
    
    # 计数信息
    count = models.IntegerField(_('计数'), default=0)
    is_valid = models.BooleanField(_('是否有效'), default=True)
    
    # 姿势数据
    posture_data = models.JSONField(_('姿势数据'), default=dict)
    posture_score = models.DecimalField(
        _('姿势评分'),
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    # 关键点数据
    keypoints = models.JSONField(_('关键点'), default=list)
    
    class Meta:
        db_table = 'exercise_data_points'
        verbose_name = _('运动数据点')
        verbose_name_plural = _('运动数据点')
        indexes = [
            models.Index(fields=['record', 'timestamp']),
        ]
        ordering = ['timestamp']
```

#### 1.2.4 任务管理应用 (tasks)
**功能范围**：
- 任务创建和管理
- 任务提醒和通知
- 进度跟踪
- 成就计算

**模型设计**：
```python
# apps/tasks/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _


class Task(models.Model):
    """任务模型"""
    
    class Priority(models.TextChoices):
        LOW = 'low',        LOW = 'low', _('低')
        MEDIUM = 'medium', _('中')
        HIGH = 'high', _('高')
        URGENT = 'urgent', _('紧急')
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('待处理')
        IN_PROGRESS = 'in_progress', _('进行中')
        COMPLETED = 'completed', _('已完成')
        CANCELLED = 'cancelled', _('已取消')
    
    class TaskType(models.TextChoices):
        HOMEWORK = 'homework', _('作业')
        EXERCISE = 'exercise', _('运动')
        READING = 'reading', _('阅读')
        PRACTICE = 'practice', _('练习')
        OTHER = 'other', _('其他')
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name=_('用户')
    )
    
    # 任务信息
    title = models.CharField(_('标题'), max_length=200)
    description = models.TextField(_('描述'), blank=True)
    task_type = models.CharField(
        _('任务类型'),
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.HOMEWORK,
        db_index=True
    )
    
    # 优先级和状态
    priority = models.CharField(
        _('优先级'),
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        db_index=True
    )
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    
    # 时间信息
    due_date = models.DateTimeField(_('截止时间'), blank=True, null=True, db_index=True)
    completed_at = models.DateTimeField(_('完成时间'), blank=True, null=True)
    
    # 提醒设置
    reminder_settings = models.JSONField(_('提醒设置'), default=dict, blank=True)
    
    # 关联信息
    related_homework = models.ForeignKey(
        'homework.Homework',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('关联作业')
    )
    related_exercise = models.ForeignKey(
        'exercise.ExerciseRecord',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('关联运动')
    )
    
    # 时间戳
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        db_table = 'tasks'
        verbose_name = _('任务')
        verbose_name_plural = _('任务')
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['priority']),
        ]
        ordering = ['-priority', 'due_date']
    
    def __str__(self):
        return f'{self.user.username} - {self.title}'
    
    @property
    def is_overdue(self):
        """是否过期"""
        if self.due_date and self.status != Task.Status.COMPLETED:
            from django.utils import timezone
            return timezone.now() > self.due_date
        return False
    
    def mark_completed(self):
        """标记为完成"""
        from django.utils import timezone
        self.status = Task.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save()


class TaskReminder(models.Model):
    """任务提醒模型"""
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='reminders',
        verbose_name=_('任务')
    )
    
    # 提醒信息
    reminder_time = models.DateTimeField(_('提醒时间'), db_index=True)
    reminder_type = models.CharField(
        _('提醒类型'),
        max_length=20,
        choices=[
            ('notification', '通知'),
            ('email', '邮件'),
            ('sms', '短信'),
        ],
        default='notification'
    )
    
    # 状态
    sent = models.BooleanField(_('已发送'), default=False)
    sent_at = models.DateTimeField(_('发送时间'), blank=True, null=True)
    
    # 时间戳
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        db_table = 'task_reminders'
        verbose_name = _('任务提醒')
        verbose_name_plural = _('任务提醒')
        indexes = [
            models.Index(fields=['task', 'reminder_time']),
            models.Index(fields=['sent']),
        ]
        ordering = ['reminder_time']
```

## 2. MySQL 数据库详细设计

### 2.1 数据库表设计

#### 2.1.1 核心表结构
```sql
-- 用户表
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(30),
    last_name VARCHAR(150),
    role ENUM('student', 'parent', 'teacher', 'admin') DEFAULT 'student',
    age INT,
    grade VARCHAR(20),
    school VARCHAR(100),
    avatar_url VARCHAR(500),
    settings JSON,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 家庭关系表
CREATE TABLE user_relationships (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    parent_id BIGINT NOT NULL,
    child_id BIGINT NOT NULL,
    relationship_type ENUM('parent_child', 'guardian') DEFAULT 'parent_child',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (child_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_relationship (parent_id, child_id),
    INDEX idx_parent_id (parent_id),
    INDEX idx_child_id (child_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 作业表
CREATE TABLE homeworks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    subject VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    image_files JSON,
    original_filenames JSON,
    status ENUM('uploaded', 'processing', 'graded', 'error') DEFAULT 'uploaded',
    grade_result JSON,
    total_questions INT,
    correct_questions INT,
    score DECIMAL(5,2),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    processed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_subject (subject),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 题目表
CREATE TABLE questions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    homework_id BIGINT NOT NULL,
    question_number INT NOT NULL,
    question_text TEXT NOT NULL,
    student_answer TEXT,
    correct_answer TEXT,
    is_correct BOOLEAN,
    points DECIMAL(5,2),
    feedback TEXT,
    knowledge_points JSON,
    FOREIGN KEY (homework_id) REFERENCES homeworks(id) ON DELETE CASCADE,
    UNIQUE KEY unique_question (homework_id, question_number),
    INDEX idx_homework_id (homework_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 运动记录表
CREATE TABLE exercise_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    exercise_type ENUM('jump_rope', 'push_up', 'sit_up', 'squat', 'other') NOT NULL,
    title VARCHAR(200),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NULL,
    duration_seconds INT,
    total_count INT DEFAULT 0,
    valid_count INT DEFAULT 0,
    average_frequency DECIMAL(6,2),
    posture_score DECIMAL(5,2),
    feedback TEXT,
    video_file VARCHAR(500),
    thumbnail VARCHAR(500),
    data_points JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_exercise_type (exercise_type),
    INDEX idx_start_time (start_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 运动数据点表
CREATE TABLE exercise_data_points (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    record_id BIGINT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    relative_time_ms INT NOT NULL,
    count INT DEFAULT 0,
    is_valid BOOLEAN DEFAULT TRUE,
    posture_data JSON,
    posture_score DECIMAL(5,2),
    keypoints JSON,
    FOREIGN KEY (record_id) REFERENCES exercise_records(id) ON DELETE CASCADE,
    INDEX idx_record_id (record_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 任务表
CREATE TABLE tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    task_type ENUM('homework', 'exercise', 'reading', 'practice', 'other') DEFAULT 'homework',
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    status ENUM('pending', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
    due_date TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    reminder_settings JSON,
    related_homework_id BIGINT NULL,
    related_exercise_id BIGINT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (related_homework_id) REFERENCES homeworks(id) ON DELETE SET NULL,
    FOREIGN KEY (related_exercise_id) REFERENCES exercise_records(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_due_date (due_date),
    INDEX idx_priority (priority)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 任务提醒表
CREATE TABLE task_reminders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_id BIGINT NOT NULL,
    reminder_time TIMESTAMP NOT NULL,
    reminder_type ENUM('notification', 'email', 'sms') DEFAULT 'notification',
    sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    INDEX idx_task_id (task_id),
    INDEX idx_reminder_time (reminder_time),
    INDEX idx_sent (sent)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 2.2 数据库替代中间件表设计

#### 2.2.1 数据库缓存表
```sql
-- 数据库缓存表（替代Redis缓存）
CREATE TABLE database_cache (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_value JSON NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cache_key (cache_key),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 缓存清理存储过程
DELIMITER //
CREATE PROCEDURE cleanup_expired_cache()
BEGIN
    DELETE FROM database_cache WHERE expires_at < NOW();
END //
DELIMITER ;
```

#### 2.2.2 异步任务表（替代消息队列）
```sql
-- 异步任务表（替代Celery/RabbitMQ）
CREATE TABLE async_tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_type VARCHAR(50) NOT NULL,
    payload JSON NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    result JSON,
    error_message TEXT,
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    scheduled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_task_type (task_type),
    INDEX idx_scheduled_at (scheduled_at),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 任务处理存储过程
DELIMITER //
CREATE PROCEDURE process_pending_tasks(IN batch_size INT)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE task_id BIGINT;
    DECLARE task_type VARCHAR(50);
    DECLARE task_payload JSON;
    DECLARE cur CURSOR FOR 
        SELECT id, task_type, payload 
        FROM async_tasks 
        WHERE status = 'pending' 
        ORDER BY created_at 
        LIMIT batch_size
        FOR UPDATE;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN cur;
    
    read_loop: LOOP
        FETCH cur INTO task_id, task_type, task_payload;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- 更新状态为处理中
        UPDATE async_tasks 
        SET status = 'processing', started_at = NOW() 
        WHERE id = task_id;
        
        -- 这里可以调用相应的处理逻辑
        -- 实际处理逻辑需要在应用层实现
        
    END LOOP;
    
    CLOSE cur;
END //
DELIMITER ;
```

#### 2.2.3 系统事件表（替代消息总线）
```sql
-- 系统事件表（替代事件总线）
CREATE TABLE system_events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    payload JSON NOT NULL,
    source VARCHAR(100),
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_event_type (event_type),
    INDEX idx_processed (processed),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 事件处理存储过程
DELIMITER //
CREATE PROCEDURE process_system_events(IN batch_size INT)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE event_id BIGINT;
    DECLARE event_type VARCHAR(50);
    DECLARE event_payload JSON;
    DECLARE cur CURSOR FOR 
        SELECT id, event_type, payload 
        FROM system_events 
        WHERE processed = FALSE 
        ORDER BY created_at 
        LIMIT batch_size
        FOR UPDATE;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN cur;
    
    read_loop: LOOP
        FETCH cur INTO event_id, event_type, event_payload;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- 更新状态为已处理
        UPDATE system_events 
        SET processed = TRUE, processed_at = NOW() 
        WHERE id = event_id;
        
        -- 这里可以根据事件类型触发相应的处理逻辑
        -- 实际处理逻辑需要在应用层实现
        
    END LOOP;
    
    CLOSE cur;
END //
DELIMITER ;
```

### 2.3 数据库优化策略

#### 2.3.1 索引优化
```sql
-- 复合索引优化
CREATE INDEX idx_homework_user_status ON homeworks(user_id, status);
CREATE INDEX idx_exercise_user_type_time ON exercise_records(user_id, exercise_type, start_time);
CREATE INDEX idx_task_user_status_due ON tasks(user_id, status, due_date);

-- 覆盖索引优化
CREATE INDEX idx_user_basic_info ON users(id, username, email, role);
CREATE INDEX idx_homework_basic_info ON homeworks(id, user_id, subject, status, created_at);
```

#### 2.3.2 分区策略（未来扩展）
```sql
-- 按时间分区（适用于大数据量表）
ALTER TABLE exercise_data_points 
PARTITION BY RANGE (UNIX_TIMESTAMP(timestamp)) (
    PARTITION p2024q1 VALUES LESS THAN (UNIX_TIMESTAMP('2024-04-01')),
    PARTITION p2024q2 VALUES LESS THAN (UNIX_TIMESTAMP('2024-07-01')),
    PARTITION p2024q3 VALUES LESS THAN (UNIX_TIMESTAMP('2024-10-01')),
    PARTITION p2024q4 VALUES LESS THAN (UNIX_TIMESTAMP('2025-01-01')),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);

-- 按用户ID哈希分区
ALTER TABLE homeworks 
PARTITION BY HASH(user_id) 
PARTITIONS 8;
```

#### 2.3.3 连接池配置
```python
# Django数据库连接池配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'coachai',
        'USER': 'coachai',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'connect_timeout': 10,
        },
        'CONN_MAX_AGE': 300,  # 连接保持5分钟
        'CONN_HEALTH_CHECKS': True,
    }
}
```

## 3. Django REST API 详细设计

### 3.1 API 设计原则

#### 3.1.1 RESTful 设计
- **资源导向**：API 围绕资源设计
- **HTTP 方法**：正确使用 GET、POST、PUT、DELETE
- **状态码**：使用合适的 HTTP 状态码
- **版本控制**：API 版本管理

#### 3.1.2 认证和授权
- **JWT 认证**：使用 JSON Web Token 进行认证
- **权限控制**：基于角色的权限控制
- **速率限制**：防止 API 滥用
- **请求验证**：输入数据验证

### 3.2 API 端点设计

#### 3.2.1 认证 API
```python
# apps/accounts/views.py
from rest_framework import views, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, RegisterSerializer


class RegisterView(views.APIView):
    """用户注册"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # 生成 JWT token
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """用户登录"""
    pass


class LogoutView(views.APIView):
    """用户登出"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(views.APIView):
    """用户资料"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

#### 3.2.2 作业管理 API
```python
# apps/homework/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Homework, Question
from .serializers import HomeworkSerializer, QuestionSerializer
from .permissions import IsOwnerOrReadOnly


class HomeworkViewSet(viewsets.ModelViewSet):
    """作业管理"""
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        # 只返回当前用户的作业
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # 设置作业所有者
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def upload_images(self, request, pk=None):
        """上传作业图片"""
        homework = self.get_object()
        images = request.FILES.getlist('images')
        
        if not images:
            return Response(
                {'error': '没有上传图片'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 保存图片文件
        image_urls = []
        original_filenames = []
        
        for image in images:
            # 生成唯一文件名
            import uuid
            filename = f"{uuid.uuid4()}_{image.name}"
            
            # 保存文件
            from django.core.files.storage import default_storage
            file_path = default_storage.save(f'homeworks/{filename}', image)
            
            image_urls.append(file_path)
            original_filenames.append(image.name)
        
        # 更新作业信息
        homework.image_files = image_urls
        homework.original_filenames = original_filenames
        homework.save()
        
        # 创建异步处理任务
        from utils.tasks import create_async_task
        create_async_task(
            task_type='process_homework',
            payload={'homework_id': homework.id}
        )
        
        return Response({
            'message': '图片上传成功，开始处理作业',
            'homework_id': homework.id
        })
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """获取作业题目"""
        homework = self.get_object()
        questions = homework.questions.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)


class QuestionViewSet(viewsets.ModelViewSet):
    """题目管理"""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # 只返回用户有权限访问的题目
        user = self.request.user
        return self.queryset.filter(homework__user=user)
```

#### 3.2.3 运动管理 API
```python
# apps/exercise/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import ExerciseRecord, ExerciseDataPoint
from .serializers import ExerciseRecordSerializer, ExerciseDataPointSerializer
from .permissions import IsOwnerOrReadOnly


class ExerciseRecordViewSet(viewsets.ModelViewSet):
    """运动记录管理"""
    queryset = ExerciseRecord.objects.all()
    serializer_class = ExerciseRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        # 只返回当前用户的运动记录
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # 设置运动记录所有者
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def start(self, request):
        """开始运动"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            exercise_record = serializer.save(
                user=request.user,
                start_time=timezone.now()
            )
            
            return Response({
                'message': '运动开始',
                'record_id': exercise_record.id,
                'start_time': exercise_record.start_time
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """结束运动"""
        exercise_record = self.get_object()
        
        if exercise_record.end_time:
            return Response(
                {'error': '运动已经结束'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exercise_record.end_time = timezone.now()
        exercise_record.save()
        
        # 计算运动数据
        self.calculate_exercise_stats(exercise_record)
        
        return Response({
            'message': '运动结束',
            'record_id': exercise_record.id,
            'duration': exercise_record.duration_seconds,
            'total_count': exercise_record.total_count
        })
    
    @action(detail=True, methods=['post'])
    def add_data_point(self, request, pk=None):
        """添加运动数据点"""
        exercise_record = self.get_object()
        
        serializer = ExerciseDataPointSerializer(data=request.data)
        if serializer.is_valid():
            data_point = serializer.save(record=exercise_record)
            
            # 实时更新计数
            if data_point.is_valid:
                exercise_record.total_count += 1
                exercise_record.valid_count += 1
                exercise_record.save()
            
            return Response({
                'message': '数据点添加成功',
                'data_point_id': data_point.id,
                'current_count': exercise_record.total_count
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def calculate_exercise_stats(self, exercise_record):
        """计算运动统计数据"""
        data_points = exercise_record.detailed_data_points.all()
        
        if not data_points:
            return
        
        # 计算平均频率
        if exercise_record.duration_seconds and exercise_record.duration_seconds > 0:
            frequency = (exercise_record.valid_count / exercise_record.duration_seconds) * 60
            exercise_record.average_frequency = round(frequency, 2)
        
        # 计算平均姿势评分
        valid_scores = [
            dp.posture_score for dp in data_points 
            if dp.posture_score is not None
        ]
        if valid_scores:
            exercise_record.posture_score = round(sum(valid_scores) / len(valid_scores), 2)
        
        exercise_record.save()
```

#### 3.2.4 任务管理 API
```python
# apps/tasks/views.py
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task, TaskReminder
from .serializers import TaskSerializer, TaskReminderSerializer
from .permissions import IsOwnerOrReadOnly
from .filters import TaskFilter


class TaskViewSet(viewsets.ModelViewSet):
    """任务管理"""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'priority', 'created_at']
    ordering = ['-priority', 'due_date']
    
    def get_queryset(self):
        # 只返回当前用户的任务
        queryset = self.queryset.filter(user=self.request.user)
        
        # 过滤参数
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        return queryset
    
    def perform_create(self, serializer):
        # 设置任务所有者
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """完成任务"""
        task = self.get_object()
        
        if task.status == Task.Status.COMPLETED:
            return Response(
                {'error': '任务已经完成'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.mark_completed()
        
        return Response({
            'message': '任务完成',
            'task_id': task.id,
            'completed_at': task.completed_at
        })
    
    @action(detail=True, methods=['post'])
    def add_reminder(self, request, pk=None):
        """添加任务提醒"""
        task = self.get_object()
        
        serializer = TaskReminderSerializer(data=request.data)
        if serializer.is_valid():
            reminder = serializer.save(task=task)
            
            return Response({
                'message': '提醒添加成功',
                'reminder_id': reminder.id,
                'reminder_time': reminder.reminder_time
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """获取过期任务"""
        queryset = self.get_queryset().filter(
            status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS],
            due_date__lt=timezone.now()
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """获取今日任务"""
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timezone.timedelta(days=1)
        
        queryset = self.get_queryset().filter(
            status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS],
            due_date__range=[today_start, today_end]
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
```

### 3.3 API 文档和测试

#### 3.3.1 OpenAPI 文档配置
```python
# coachai/urls.py
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="CoachAI API",
        default_version='v1',
        description="CoachAI 智能伴读AI系统 API 文档",
        terms_of_service="https://www.coachai.com/terms/",
        contact=openapi.Contact(email="contact@coachai.com"),
        license=openapi.License(name="GPL v3 License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # API 文档
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API 路由
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/homework/', include('apps.homework.urls')),
    path('api/v1/exercise/', include('apps.exercise.urls')),
    path('api/v1/tasks/', include('apps.tasks.urls')),
]
```

#### 3.3.2 API 测试配置
```python
# tests/test_api.py
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.accounts.models import User


class AuthenticationTests(APITestCase):
    """认证API测试"""
    
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'role': 'student'
        }
    
    def test_user_registration(self):
        """测试用户注册"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_user_login(self):
        """测试用户登录"""
        # 先注册用户
        self.client.post(self.register_url, self.user_data)
        
        # 测试登录
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class HomeworkAPITests(APITestCase):
    """作业API测试"""
    
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        # 获取token
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        self.homework_url = reverse('homework-list')
    
    def test_create_homework(self):
        """测试创建作业"""
        data = {
            'subject': '数学',
            'title': '第一章练习题',
            'description': '基础练习题'
        }
        response        response = self.client.post(self.homework_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['subject'], '数学')
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_get_homework_list(self):
        """测试获取作业列表"""
        # 先创建一些作业
        for i in range(5):
            self.client.post(self.homework_url, {
                'subject': f'科目{i}',
                'title': f'作业{i}',
                'description': f'描述{i}'
            })
        
        response = self.client.get(self.homework_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # 分页返回

## 4. 异步任务系统设计

### 4.1 数据库驱动的异步任务

#### 4.1.1 任务管理器
```python
# utils/tasks.py
from django.db import models, transaction
from django.utils import timezone
from datetime import timedelta
import json


class TaskManager:
    """任务管理器"""
    
    @staticmethod
    def create_task(task_type, payload, scheduled_at=None, max_retries=3):
        """创建异步任务"""
        from .models import AsyncTask
        
        task = AsyncTask.objects.create(
            task_type=task_type,
            payload=json.dumps(payload),
            max_retries=max_retries,
            scheduled_at=scheduled_at or timezone.now()
        )
        return task
    
    @staticmethod
    def process_tasks(batch_size=10):
        """处理待处理任务"""
        from .models import AsyncTask
        
        with transaction.atomic():
            # 获取待处理任务
            tasks = AsyncTask.objects.filter(
                status='pending',
                scheduled_at__lte=timezone.now()
            ).select_for_update(skip_locked=True)[:batch_size]
            
            for task in tasks:
                task.status = 'processing'
                task.started_at = timezone.now()
                task.save()
                
                try:
                    # 执行任务
                    result = TaskExecutor.execute(task)
                    
                    task.status = 'completed'
                    task.result = json.dumps(result)
                    task.completed_at = timezone.now()
                    task.save()
                    
                except Exception as e:
                    task.retry_count += 1
                    
                    if task.retry_count >= task.max_retries:
                        task.status = 'failed'
                        task.error_message = str(e)
                    else:
                        # 重试，延迟时间指数递增
                        delay_minutes = 2 ** task.retry_count
                        task.scheduled_at = timezone.now() + timedelta(minutes=delay_minutes)
                        task.status = 'pending'
                    
                    task.save()


class TaskExecutor:
    """任务执行器"""
    
    @staticmethod
    def execute(task):
        """执行任务"""
        task_type = task.task_type
        payload = json.loads(task.payload)
        
        if task_type == 'process_homework':
            return TaskExecutor.process_homework(payload)
        elif task_type == 'process_exercise':
            return TaskExecutor.process_exercise(payload)
        elif task_type == 'send_notification':
            return TaskExecutor.send_notification(payload)
        else:
            raise ValueError(f'未知任务类型: {task_type}')
    
    @staticmethod
    def process_homework(payload):
        """处理作业"""
        from apps.homework.models import Homework
        from services.ocr_service import OCRService
        
        homework_id = payload.get('homework_id')
        if not homework_id:
            raise ValueError('缺少 homework_id')
        
        homework = Homework.objects.get(id=homework_id)
        
        # 更新状态为处理中
        homework.status = 'processing'
        homework.save()
        
        try:
            # 使用 OCR 服务处理作业图片
            ocr_service = OCRService()
            result = ocr_service.process_homework(homework)
            
            # 更新作业结果
            homework.status = 'graded'
            homework.grade_result = result
            homework.processed_at = timezone.now()
            homework.save()
            
            return {'success': True, 'homework_id': homework_id}
            
        except Exception as e:
            homework.status = 'error'
            homework.save()
            raise e
    
    @staticmethod
    def process_exercise(payload):
        """处理运动数据"""
        from apps.exercise.models import ExerciseRecord
        
        record_id = payload.get('record_id')
        if not record_id:
            raise ValueError('缺少 record_id')
        
        record = ExerciseRecord.objects.get(id=record_id)
        
        # 处理运动数据
        # 这里可以添加运动数据分析逻辑
        
        return {'success': True, 'record_id': record_id}
    
    @staticmethod
    def send_notification(payload):
        """发送通知"""
        user_id = payload.get('user_id')
        message = payload.get('message')
        notification_type = payload.get('type', 'info')
        
        # 这里可以实现通知发送逻辑
        # 可以集成邮件、短信、推送通知等
        
        return {'success': True, 'user_id': user_id}
```

#### 4.1.2 定时任务调度
```python
# management/commands/process_tasks.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from utils.tasks import TaskManager


class Command(BaseCommand):
    """处理异步任务的 Django 管理命令"""
    help = '处理数据库中的异步任务'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='每次处理的任务数量'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='处理间隔（秒）'
        )
    
    def handle(self, *args, **options):
        batch_size = options['batch_size']
        interval = options['interval']
        
        self.stdout.write(
            self.style.SUCCESS(f'开始处理异步任务，批量大小: {batch_size}, 间隔: {interval}秒')
        )
        
        import time
        while True:
            try:
                # 处理任务
                processed = TaskManager.process_tasks(batch_size)
                
                if processed > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'处理了 {processed} 个任务')
                    )
                
                # 等待指定间隔
                time.sleep(interval)
                
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('任务处理已停止'))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'处理任务时出错: {str(e)}'))
                time.sleep(interval)
```

### 4.2 数据库缓存系统

#### 4.2.1 缓存管理器
```python
# utils/cache.py
from django.db import models, transaction
from django.utils import timezone
from datetime import timedelta
import json


class DatabaseCache:
    """数据库缓存"""
    
    @staticmethod
    def get(key, default=None):
        """获取缓存值"""
        from .models import DatabaseCache as CacheModel
        
        try:
            cache = CacheModel.objects.get(
                cache_key=key,
                expires_at__gt=timezone.now()
            )
            return json.loads(cache.cache_value)
        except CacheModel.DoesNotExist:
            return default
    
    @staticmethod
    def set(key, value, timeout=300):
        """设置缓存值"""
        from .models import DatabaseCache as CacheModel
        
        expires_at = timezone.now() + timedelta(seconds=timeout)
        
        with transaction.atomic():
            CacheModel.objects.update_or_create(
                cache_key=key,
                defaults={
                    'cache_value': json.dumps(value),
                    'expires_at': expires_at
                }
            )
    
    @staticmethod
    def delete(key):
        """删除缓存"""
        from .models import DatabaseCache as CacheModel
        
        CacheModel.objects.filter(cache_key=key).delete()
    
    @staticmethod
    def clear():
        """清空缓存"""
        from .models import DatabaseCache as CacheModel
        
        CacheModel.objects.all().delete()
    
    @staticmethod
    def cleanup():
        """清理过期缓存"""
        from .models import DatabaseCache as CacheModel
        
        deleted_count, _ = CacheModel.objects.filter(
            expires_at__lte=timezone.now()
        ).delete()
        
        return deleted_count
```

#### 4.2.2 缓存装饰器
```python
# utils/decorators.py
from functools import wraps
from django.utils import timezone
from datetime import timedelta
from .cache import DatabaseCache


def cached(timeout=300, key_prefix=''):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 尝试从缓存获取
            cached_value = DatabaseCache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 缓存结果
            DatabaseCache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


class CacheMixin:
    """缓存混合类"""
    
    def get_cache_key(self, prefix, *args, **kwargs):
        """生成缓存键"""
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}:{v}" for k, v in kwargs.items())
        return ":".join(key_parts)
    
    def cached_method(self, timeout=300):
        """方法缓存装饰器"""
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                cache_key = self.get_cache_key(
                    f"{self.__class__.__name__}:{func.__name__}",
                    *args,
                    **kwargs
                )
                
                cached_value = DatabaseCache.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                result = func(self, *args, **kwargs)
                DatabaseCache.set(cache_key, result, timeout)
                
                return result
            return wrapper
        return decorator
```

## 5. 文件存储系统设计

### 5.1 本地文件存储

#### 5.1.1 文件存储配置
```python
# settings/base.py
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 文件上传配置
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# 文件类型白名单
ALLOWED_FILE_EXTENSIONS = {
    'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'],
    'video': ['mp4', 'avi', 'mov', 'mkv', 'webm'],
    'document': ['pdf', 'doc', 'docx', 'txt']
}

MAX_FILE_SIZES = {
    'image': 5 * 1024 * 1024,  # 5MB
    'video': 50 * 1024 * 1024,  # 50MB
    'document': 10 * 1024 * 1024  # 10MB
}
```

#### 5.1.2 文件上传服务
```python
# utils/storage.py
import os
import uuid
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from pathlib import Path
from PIL import Image
import magic


class FileUploadService:
    """文件上传服务"""
    
    @staticmethod
    def validate_file(file, file_type='image'):
        """验证文件"""
        # 检查文件大小
        max_size = MAX_FILE_SIZES.get(file_type, 5 * 1024 * 1024)
        if file.size > max_size:
            raise ValidationError(f'文件大小不能超过 {max_size // 1024 // 1024}MB')
        
        # 检查文件类型
        mime = magic.Magic(mime=True)
        file_mime = mime.from_buffer(file.read(1024))
        file.seek(0)  # 重置文件指针
        
        allowed_extensions = ALLOWED_FILE_EXTENSIONS.get(file_type, [])
        
        # 简单的MIME类型检查
        if file_type == 'image' and not file_mime.startswith('image/'):
            raise ValidationError('请上传图片文件')
        elif file_type == 'video' and not file_mime.startswith('video/'):
            raise ValidationError('请上传视频文件')
        
        return True
    
    @staticmethod
    def generate_filename(original_filename, file_type='image'):
        """生成唯一文件名"""
        ext = original_filename.split('.')[-1].lower()
        
        # 确保扩展名在允许列表中
        allowed_extensions = ALLOWED_FILE_EXTENSIONS.get(file_type, [])
        if ext not in allowed_extensions:
            ext = allowed_extensions[0] if allowed_extensions else 'jpg'
        
        # 生成UUID文件名
        filename = f"{uuid.uuid4()}.{ext}"
        
        return filename
    
    @staticmethod
    def save_file(file, file_type='image', subdirectory=''):
        """保存文件"""
        # 验证文件
        FileUploadService.validate_file(file, file_type)
        
        # 生成文件名
        filename = FileUploadService.generate_filename(file.name, file_type)
        
        # 构建保存路径
        if subdirectory:
            save_path = Path(subdirectory) / filename
        else:
            save_path = Path(file_type) / filename
        
        # 确保目录存在
        full_path = MEDIA_ROOT / save_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        file_path = default_storage.save(str(save_path), file)
        
        # 如果是图片，生成缩略图
        if file_type == 'image':
            FileUploadService.generate_thumbnail(file_path)
        
        return file_path
    
    @staticmethod
    def generate_thumbnail(image_path, size=(200, 200)):
        """生成缩略图"""
        try:
            full_path = MEDIA_ROOT / image_path
            
            # 打开图片
            with Image.open(full_path) as img:
                # 转换为RGB（处理PNG透明背景）
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                
                # 调整大小
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # 保存缩略图
                thumbnail_path = f"{image_path}.thumbnail.jpg"
                thumbnail_full_path = MEDIA_ROOT / thumbnail_path
                img.save(thumbnail_full_path, 'JPEG', quality=85)
                
                return thumbnail_path
        except Exception as e:
            print(f"生成缩略图失败: {e}")
            return None
    
    @staticmethod
    def delete_file(file_path):
        """删除文件"""
        try:
            # 删除主文件
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
            
            # 删除缩略图（如果存在）
            thumbnail_path = f"{file_path}.thumbnail.jpg"
            if default_storage.exists(thumbnail_path):
                default_storage.delete(thumbnail_path)
            
            return True
        except Exception as e:
            print(f"删除文件失败: {e}")
            return False
```

### 5.2 文件管理API

#### 5.2.1 文件上传API
```python
# apps/common/views.py
from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.utils import timezone
from utils.storage import FileUploadService


class FileUploadView(views.APIView):
    """文件上传API"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        file = request.FILES.get('file')
        file_type = request.data.get('type', 'image')
        subdirectory = request.data.get('subdirectory', '')
        
        if not file:
            return Response(
                {'error': '没有上传文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 保存文件
            file_path = FileUploadService.save_file(file, file_type, subdirectory)
            
            # 构建文件URL
            from django.conf import settings
            file_url = f"{settings.MEDIA_URL}{file_path}"
            
            return Response({
                'success': True,
                'file_path': file_path,
                'file_url': file_url,
                'filename': file.name,
                'size': file.size,
                'uploaded_at': timezone.now().isoformat()
            })
            
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'文件上传失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
```

## 6. AI 服务集成设计

### 6.1 OCR 服务设计

#### 6.1.1 OCR 服务实现
```python
# services/ocr_service.py
import cv2
import numpy as np
from PIL import Image
import io
from django.core.files.storage import default_storage
from utils.cache import cached


class OCRService:
    """OCR 服务"""
    
    def __init__(self### 6.1 OCR 服务设计

#### 6.1.1 OCR 服务完整实现
```python
# services/ocr_service.py
import cv2
import numpy as np
from PIL import Image
import io
import json
from django.core.files.storage import default_storage
from django.conf import settings
from utils.cache import cached
import paddleocr
from paddleocr import PaddleOCR
import easyocr


class OCRService:
    """OCR 服务"""
    
    def __init__(self):
        # 初始化 PaddleOCR
        self.paddle_ocr = PaddleOCR(
            use_angle_cls=True,
            lang='ch',
            rec_algorithm='CRNN',
            use_gpu=False,  # 开发环境不使用GPU
            show_log=False
        )
        
        # 初始化 EasyOCR
        self.easy_ocr = easyocr.Reader(['ch_sim', 'en'])
    
    @cached(timeout=3600, key_prefix='ocr')
    def recognize_text(self, image_path, use_paddle=True):
        """识别图片中的文字"""
        try:
            # 读取图片
            image_data = default_storage.open(image_path).read()
            image = Image.open(io.BytesIO(image_data))
            
            # 转换为OpenCV格式
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            if use_paddle:
                # 使用PaddleOCR
                result = self.paddle_ocr.ocr(cv_image, cls=True)
                return self._parse_paddle_result(result)
            else:
                # 使用EasyOCR
                result = self.easy_ocr.readtext(cv_image)
                return self._parse_easy_result(result)
                
        except Exception as e:
            raise Exception(f"OCR识别失败: {str(e)}")
    
    def _parse_paddle_result(self, result):
        """解析PaddleOCR结果"""
        if not result or not result[0]:
            return []
        
        parsed_result = []
        for line in result[0]:
            # 提取文本和置信度
            text = line[1][0]
            confidence = float(line[1][1])
            
            # 提取边界框
            box = line[0]
            
            parsed_result.append({
                'text': text,
                'confidence': confidence,
                'box': box,
                'type': 'text'
            })
        
        return parsed_result
    
    def _parse_easy_result(self, result):
        """解析EasyOCR结果"""
        parsed_result = []
        for detection in result:
            # 提取文本和置信度
            text = detection[1]
            confidence = float(detection[2])
            
            # 提取边界框
            box = detection[0]
            
            parsed_result.append({
                'text': text,
                'confidence': confidence,
                'box': box,
                'type': 'text'
            })
        
        return parsed_result
    
    def process_homework(self, homework):
        """处理作业图片"""
        image_paths = homework.image_files
        
        if not image_paths:
            raise ValueError("作业没有图片")
        
        all_results = []
        for image_path in image_paths:
            # 识别单张图片
            result = self.recognize_text(image_path)
            all_results.extend(result)
        
        # 提取题目和答案
        questions = self._extract_questions(all_results)
        
        return {
            'success': True,
            'total_pages': len(image_paths),
            'total_text_blocks': len(all_results),
            'questions': questions,
            'raw_results': all_results
        }
    
    def _extract_questions(self, ocr_results):
        """从OCR结果中提取题目"""
        questions = []
        current_question = None
        
        for result in ocr_results:
            text = result['text'].strip()
            
            # 检查是否是题号（如 "1."、"一、"等）
            if self._is_question_number(text):
                if current_question:
                    questions.append(current_question)
                
                current_question = {
                    'number': self._extract_question_number(text),
                    'text': text,
                    'answer': '',
                    'type': 'single_choice'  # 默认单选
                }
            elif current_question:
                # 添加到当前题目
                if '答案' in text or '答:' in text:
                    current_question['answer'] = text
                else:
                    current_question['text'] += ' ' + text
        
        # 添加最后一个题目
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def _is_question_number(self, text):
        """判断是否是题号"""
        import re
        patterns = [
            r'^\d+[\.、]',  # 1. 或 1、
            r'^[一二三四五六七八九十]+[\.、]',  # 一、 或 二.
            r'^\([一二三四五六七八九十]+\)',  # (一) 或 (二)
            r'^[A-Z][\.、]',  # A. 或 B、
        ]
        
        for pattern in patterns:
            if re.match(pattern, text):
                return True
        
        return False
    
    def _extract_question_number(self, text):
        """提取题号"""
        import re
        match = re.match(r'^(\d+|[一二三四五六七八九十]+|[A-Z])', text)
        if match:
            return match.group(1)
        return text


class HomeworkGrader:
    """作业批改器"""
    
    def __init__(self):
        self.ocr_service = OCRService()
    
    def grade_homework(self, homework_id):
        """批改作业"""
        from apps.homework.models import Homework, Question
        
        homework = Homework.objects.get(id=homework_id)
        
        # 使用OCR识别作业
        ocr_result = self.ocr_service.process_homework(homework)
        
        # 创建题目记录
        questions_data = []
        for q_data in ocr_result['questions']:
            question = Question(
                homework=homework,
                question_number=q_data['number'],
                question_text=q_data['text'],
                student_answer=q_data.get('answer', '')
            )
            questions_data.append(question)
        
        # 批量创建题目
        Question.objects.bulk_create(questions_data)
        
        # 计算分数（这里可以集成更复杂的评分逻辑）
        total_questions = len(questions_data)
        correct_questions = self._estimate_correct_count(questions_data)
        score = (correct_questions / total_questions * 100) if total_questions > 0 else 0
        
        # 更新作业状态
        homework.status = 'graded'
        homework.total_questions = total_questions
        homework.correct_questions = correct_questions
        homework.score = round(score, 2)
        homework.grade_result = {
            'ocr_result': ocr_result,
            'grading_method': 'auto_ocr',
            'confidence': 0.8  # 置信度评分
        }
        homework.save()
        
        return {
            'homework_id': homework_id,
            'total_questions': total_questions,
            'correct_questions': correct_questions,
            'score': homework.score,
            'status': 'graded'
        }
    
    def _estimate_correct_count(self, questions):
        """估计正确题目数量（简化版本）"""
        # 这里可以实现更复杂的评分逻辑
        # 例如：与标准答案对比、使用AI模型评分等
        return len(questions) // 2  # 简单估计一半正确
```

### 6.2 计算机视觉服务设计

#### 6.2.1 动作识别服务
```python
# services/cv_service.py
import cv2
import numpy as np
import mediapipe as mp
from django.core.files.storage import default_storage
from django.conf import settings
import json
from datetime import datetime


class ActionRecognitionService:
    """动作识别服务"""
    
    def __init__(self):
        # 初始化MediaPipe
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            smooth_landmarks=True,
            enable_segmentation=False,
            smooth_segmentation=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 动作识别模型
        self.action_models = self._load_action_models()
    
    def _load_action_models(self):
        """加载动作识别模型"""
        # 这里可以加载预训练的模型
        # 简化版本使用规则判断
        return {
            'jump_rope': self._detect_jump_rope,
            'push_up': self._detect_push_up,
            'sit_up': self._detect_sit_up,
            'squat': self._detect_squat
        }
    
    def process_video_frame(self, frame_data, exercise_type='jump_rope'):
        """处理视频帧"""
        # 解码帧数据
        frame = self._decode_frame(frame_data)
        
        # 姿态估计
        pose_result = self._estimate_pose(frame)
        
        if not pose_result:
            return None
        
        # 动作识别
        action_result = self.action_models[exercise_type](pose_result)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'pose_landmarks': pose_result,
            'action_detected': action_result['detected'],
            'count': action_result.get('count', 0),
            'confidence': action_result.get('confidence', 0),
            'posture_score': action_result.get('posture_score', 0),
            'feedback': action_result.get('feedback', '')
        }
    
    def _decode_frame(self, frame_data):
        """解码帧数据"""
        if isinstance(frame_data, bytes):
            # 从字节数据解码
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif isinstance(frame_data, np.ndarray):
            frame = frame_data
        else:
            raise ValueError("不支持的帧数据格式")
        
        return frame
    
    def _estimate_pose(self, frame):
        """姿态估计"""
        # 转换为RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 处理图像
        results = self.pose.process(frame_rgb)
        
        if not results.pose_landmarks:
            return None
        
        # 提取关键点
        landmarks = []
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            landmarks.append({
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            })
        
        return landmarks
    
    def _detect_jump_rope(self, landmarks):
        """检测跳绳动作"""
        # 提取关键关节
        left_ankle = landmarks[27]  # 左脚踝
        right_ankle = landmarks[28]  # 右脚踝
        left_knee = landmarks[25]  # 左膝盖
        right_knee = landmarks[26]  # 右膝盖
        
        # 计算膝盖弯曲角度
        knee_angles = self._calculate_knee_angles(landmarks)
        
        # 判断是否跳跃
        is_jumping = (
            knee_angles['left'] > 150 and  # 膝盖接近伸直
            knee_angles['right'] > 150 and
            left_ankle['y'] < 0.5 and  # 脚踝位置较高
            right_ankle['y'] < 0.5
        )
        
        # 姿势评分
        posture_score = self._calculate_posture_score(landmarks, 'jump_rope')
        
        return {
            'detected': is_jumping,
            'count': 1 if is_jumping else 0,
            'confidence': 0.8 if is_jumping else 0.2,
            'posture_score': posture_score,
            'feedback': self._generate_feedback(landmarks, 'jump_rope')
        }
    
    def _detect_push_up(self, landmarks):
        """检测俯卧撑动作"""
        # 俯卧撑检测逻辑
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_elbow = landmarks[13]
        right_elbow = landmarks[14]
        
        # 计算肘部角度
        elbow_angles = self._calculate_elbow_angles(landmarks)
        
        # 判断是否完成俯卧撑
        is_push_up = (
            elbow_angles['left'] < 90 and  # 肘部弯曲
            elbow_angles['right'] < 90 and
            left_shoulder['y'] > 0.6 and  # 肩膀位置较低
            right_shoulder['y'] > 0.6
        )
        
        posture_score = self._calculate_posture_score(landmarks, 'push_up')
        
        return {
            'detected': is_push_up,
            'count': 1 if is_push_up else 0,
            'confidence': 0.7 if is_push_up else 0.3,
            'posture_score': posture_score,
            'feedback': self._generate_feedback(landmarks, 'push_up')
        }
    
    def _calculate_knee_angles(self, landmarks):
        """计算膝盖角度"""
        # 简化版本，实际需要更精确的计算
        left_hip = landmarks[23]
        left_knee = landmarks[25]
        left_ankle = landmarks[27]
        
        right_hip = landmarks[24]
        right_knee = landmarks[26]
        right_ankle = landmarks[28]
        
        # 计算角度（简化）
        left_angle = self._calculate_angle(left_hip, left_knee, left_ankle)
        right_angle = self._calculate_angle(right_hip, right_knee, right_ankle)
        
        return {'left': left_angle, 'right': right_angle}
    
    def _calculate_elbow_angles(self, landmarks):
        """计算肘部角度"""
        left_shoulder = landmarks[11]
        left_elbow = landmarks[13]
        left_wrist = landmarks[15]
        
        right_shoulder = landmarks[12]
        right_elbow = landmarks[14]
        right_wrist = landmarks[16]
        
        left_angle = self._calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_angle = self._calculate_angle(right_shoulder, right_elbow, right_wrist)
        
        return {'left': left_angle, 'right': right_angle}
    
    def _calculate_angle(self, a, b, c):
        """计算三点之间的角度"""
        import math
        
        # 计算向量
        ba = [a['x'] - b['x'], a['y'] - b['y']]
        bc = [c['x'] - b['x'], c['y'] - b['y']]
        
        # 计算点积
        dot_product = ba[0] * bc[0] + ba[1] * bc[1]
        
        # 计算模长
        norm_ba = math.sqrt(ba[0]**2 + ba[1]**2)
        norm_bc = math.sqrt(bc[0]**2 + bc[1]**2)
        
        # 计算角度
        if norm_ba == 0 or norm_bc == 0:
            return 0
        
        cos_angle = dot_product / (norm_ba * norm_bc)
        cos_angle = max(-1, min(1, cos_angle))  # 防止数值误差
        
        angle = math.degrees(math.acos(cos_angle))
        
        return angle
    
    def _calculate_posture_score(self, landmarks, exercise_type):
        """计算姿势评分"""
        # 根据运动类型计算姿势评分
        if exercise_type == 'jump_rope':
            # 检查身体是否直立
            nose = landmarks[0]
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            
            # 计算身体倾斜角度
            body_tilt = abs(nose['x'] - (left_hip['x'] + right_hip['x']) / 2)
            
            # 评分：0-100，倾斜越小分数越高
            score = max(0, 100 - body_tilt * 1000)
            return round(score, 2)
        
        elif exercise_type == 'push_up':
            # 检查身体是否平直
            left_shoulder = landmarks[11]
            left_hip = landmarks[23]
            left_ankle = landmarks[27]
            
            # 计算身体            # 计算身体直线度
            shoulder_hip_diff = abs(left_shoulder['y'] - left_hip['y'])
            hip_ankle_diff = abs(left_hip['y'] - left_ankle['y'])
            
            # 评分：身体越平直分数越高
            score = 100 - (shoulder_hip_diff + hip_ankle_diff) * 50
            return round(max(0, min(100, score)), 2)
        
        return 80.0  # 默认分数
    
    def _generate_feedback(self, landmarks, exercise_type):
        """生成反馈建议"""
        if exercise_type == 'jump_rope':
            # 检查膝盖是否弯曲过多
            knee_angles = self._calculate_knee_angles(landmarks)
            
            if knee_angles['left'] < 160 or knee_angles['right'] < 160:
                return "膝盖可以再伸直一些，保持身体直立"
            else:
                return "姿势很好，继续保持"
        
        elif exercise_type == 'push_up':
            # 检查身体是否平直
            left_shoulder = landmarks[11]
            left_hip = landmarks[23]
            
            body_tilt = abs(left_shoulder['y'] - left_hip['y'])
            if body_tilt > 0.1:
                return "注意保持身体平直，不要塌腰"
            else:
                return "姿势标准，很好"
        
        return "继续努力"


class ExerciseProcessor:
    """运动处理器"""
    
    def __init__(self):
        self.cv_service = ActionRecognitionService()
    
    def process_exercise_session(self, exercise_record):
        """处理运动会话"""
        from apps.exercise.models import ExerciseDataPoint
        
        # 这里可以实现视频文件处理逻辑
        # 简化版本：模拟处理
        
        data_points = []
        total_count = 0
        
        # 模拟处理10个数据点
        for i in range(10):
            # 模拟帧数据
            frame_data = self._generate_mock_frame(i)
            
            # 处理帧
            result = self.cv_service.process_video_frame(
                frame_data,
                exercise_record.exercise_type
            )
            
            if result and result['action_detected']:
                total_count += result['count']
            
            # 创建数据点
            data_point = ExerciseDataPoint(
                record=exercise_record,
                timestamp=result['timestamp'],
                relative_time_ms=i * 1000,  # 每秒一个点
                count=total_count,
                is_valid=result['action_detected'],
                posture_data=result['pose_landmarks'],
                posture_score=result['posture_score'],
                keypoints=result['pose_landmarks']
            )
            data_points.append(data_point)
        
        # 批量保存数据点
        ExerciseDataPoint.objects.bulk_create(data_points)
        
        # 更新运动记录
        exercise_record.total_count = total_count
        exercise_record.valid_count = total_count
        exercise_record.posture_score = sum(
            dp.posture_score for dp in data_points if dp.posture_score
        ) / len(data_points) if data_points else 0
        exercise_record.save()
        
        return {
            'record_id': exercise_record.id,
            'total_count': total_count,
            'data_points_count': len(data_points),
            'average_posture_score': exercise_record.posture_score
        }
    
    def _generate_mock_frame(self, index):
        """生成模拟帧数据（用于测试）"""
        # 创建一个简单的测试图像
        import numpy as np
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:, :] = [255, 255, 255]  # 白色背景
        
        # 添加一些测试内容
        cv2.putText(
            frame,
            f'Test Frame {index}',
            (50, 240),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )
        
        return frame

### 6.3 语音服务设计

#### 6.3.1 语音识别服务
```python
# services/speech_service.py
import speech_recognition as sr
import whisper
from django.conf import settings
import io
import wave
import numpy as np


class SpeechRecognitionService:
    """语音识别服务"""
    
    def __init__(self):
        # 初始化语音识别器
        self.recognizer = sr.Recognizer()
        
        # 初始化Whisper模型（按需加载）
        self.whisper_model = None
    
    def recognize_speech(self, audio_data, use_whisper=False):
        """识别语音"""
        try:
            if use_whisper and self._load_whisper_model():
                # 使用Whisper
                return self._recognize_with_whisper(audio_data)
            else:
                # 使用SpeechRecognition
                return self._recognize_with_sr(audio_data)
                
        except Exception as e:
            raise Exception(f"语音识别失败: {str(e)}")
    
    def _load_whisper_model(self):
        """加载Whisper模型"""
        if self.whisper_model is None:
            try:
                self.whisper_model = whisper.load_model("base")
                return True
            except Exception as e:
                print(f"加载Whisper模型失败: {e}")
                return False
        return True
    
    def _recognize_with_whisper(self, audio_data):
        """使用Whisper识别语音"""
        # 转换音频格式
        audio_array = self._convert_to_numpy(audio_data)
        
        # 识别
        result = self.whisper_model.transcribe(audio_array)
        
        return {
            'text': result['text'],
            'language': result.get('language', 'zh'),
            'confidence': 0.9,  # Whisper不提供置信度
            'method': 'whisper'
        }
    
    def _recognize_with_sr(self, audio_data):
        """使用SpeechRecognition识别语音"""
        # 创建AudioData对象
        audio = sr.AudioData(
            audio_data,
            sample_rate=16000,
            sample_width=2
        )
        
        # 识别
        try:
            text = self.recognizer.recognize_google(audio, language='zh-CN')
            return {
                'text': text,
                'language': 'zh-CN',
                'confidence': 0.8,
                'method': 'google'
            }
        except sr.UnknownValueError:
            return {
                'text': '',
                'language': 'zh-CN',
                'confidence': 0.0,
                'method': 'google',
                'error': '无法识别语音'
            }
        except sr.RequestError as e:
            return {
                'text': '',
                'language': 'zh-CN',
                'confidence': 0.0,
                'method': 'google',
                'error': f'语音识别服务错误: {e}'
            }
    
    def _convert_to_numpy(self, audio_data):
        """转换音频数据为numpy数组"""
        # 这里需要根据音频格式进行转换
        # 简化版本
        import numpy as np
        return np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0


class VoiceCommandProcessor:
    """语音命令处理器"""
    
    def __init__(self):
        self.speech_service = SpeechRecognitionService()
    
    def process_voice_command(self, audio_data):
        """处理语音命令"""
        # 识别语音
        recognition_result = self.speech_service.recognize_speech(audio_data)
        
        if not recognition_result['text']:
            return {
                'success': False,
                'error': '无法识别语音',
                'recognized_text': ''
            }
        
        # 解析命令
        command = self._parse_command(recognition_result['text'])
        
        return {
            'success': True,
            'recognized_text': recognition_result['text'],
            'command': command,
            'confidence': recognition_result['confidence']
        }
    
    def _parse_command(self, text):
        """解析语音命令"""
        text_lower = text.lower()
        
        # 定义命令关键词
        commands = {
            '开始学习': ['开始学习', '学习时间', '做作业'],
            '开始运动': ['开始运动', '锻炼', '运动时间'],
            '查看任务': ['查看任务', '我的任务', '任务列表'],
            '查看进度': ['查看进度', '学习进度', '运动进度'],
            '帮助': ['帮助', '怎么用', '功能介绍']
        }
        
        # 匹配命令
        for command, keywords in commands.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return {
                        'type': command,
                        'action': command,
                        'parameters': self._extract_parameters(text)
                    }
        
        # 默认返回
        return {
            'type': 'unknown',
            'action': 'unknown',
            'parameters': {},
            'original_text': text
        }
    
    def _extract_parameters(self, text):
        """提取命令参数"""
        parameters = {}
        
        # 提取时间参数
        import re
        time_pattern = r'(\d+)(分钟|小时|秒)'
        time_matches = re.findall(time_pattern, text)
        
        if time_matches:
            parameters['duration'] = {
                'value': int(time_matches[0][0]),
                'unit': time_matches[0][1]
            }
        
        # 提取运动类型
        exercise_types = ['跳绳', '俯卧撑', '仰卧起坐', '深蹲']
        for exercise in exercise_types:
            if exercise in text:
                parameters['exercise_type'] = exercise
                break
        
        return parameters
```

## 7. 测试设计

### 7.1 测试策略

#### 7.1.1 测试金字塔
```
        E2E 测试 (10%)
           ↓
     集成测试 (20%)
           ↓
    单元测试 (70%)
```

#### 7.1.2 测试类型
- **单元测试**：测试单个函数或类
- **集成测试**：测试模块间集成
- **API测试**：测试REST API接口
- **E2E测试**：测试完整用户流程

### 7.2 单元测试设计

#### 7.2.1 模型测试
```python
# tests/test_models.py
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import User
from apps.homework.models import Homework
from apps.exercise.models import ExerciseRecord
from apps.tasks.models import Task


class UserModelTest(TestCase):
    """用户模型测试"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'role': 'student'
        }
    
    def test_create_user(self):
        """测试创建用户"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'student')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_verified)
    
    def test_user_str_representation(self):
        """测试用户字符串表示"""
        user = User.objects.create_user(**self.user_data)
        expected_str = f'testuser (学生)'
        self.assertEqual(str(user), expected_str)
    
    def test_student_property(self):
        """测试学生属性"""
        user = User.objects.create_user(**self.user_data)
        self.assertTrue(user.is_student)
        self.assertFalse(user.is_parent)


class HomeworkModelTest(TestCase):
    """作业模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='testpass123',
            role='student'
        )
    
    def test_create_homework(self):
        """测试创建作业"""
        homework = Homework.objects.create(
            user=self.user,
            subject='数学',
            title='第一章练习题'
        )
        
        self.assertEqual(homework.subject, '数学')
        self.assertEqual(homework.title, '第一章练习题')
        self.assertEqual(homework.status, 'uploaded')
        self.assertEqual(homework.user.username, 'student1')
    
    def test_homework_str_representation(self):
        """测试作业字符串表示"""
        homework = Homework.objects.create(
            user=self.user,
            subject='数学',
            title='第一章练习题'
        )
        
        expected_str = f'student1 - 数学 - 第一章练习题'
        self.assertEqual(str(homework), expected_str)
```

#### 7.2.2 服务测试
```python
# tests/test_services.py
import pytest
from django.test import TestCase
from unittest.mock import Mock, patch
from services.ocr_service import OCRService
from services.cv_service import ActionRecognitionService
from services.speech_service import SpeechRecognitionService


class OCRServiceTest(TestCase):
    """OCR服务测试"""
    
    def setUp(self):
        self.ocr_service = OCRService()
    
    @patch('services.ocr_service.PaddleOCR')
    def test_recognize_text_with_paddle(self, mock_paddle):
        """测试使用PaddleOCR识别文字"""
        # 模拟PaddleOCR返回结果
        mock_result = [[
            [[[0, 0], [100, 0], [100, 50], [0, 50]], ('测试文字', 0.9)]
        ]]
        mock_paddle.return_value.ocr.return_value = mock_result
        
        # 测试识别
        result = self.ocr_service.recognize_text('test.jpg', use_paddle=True)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['text'], '测试文字')
        self.assertEqual(result[0]['confidence'], 0.9)
    
    def test_is_question_number(self):
        """测试题号判断"""
        test_cases = [
            ('1.', True),
            ('一、', True),
            ('(一)', True),
            ('A.', True),
            ('题目', False),
            ('答案', False),
        ]
        
        for text, expected in test_cases:
            result = self.ocr_service._is_question_number(text)
            self.assertEqual(result, expected, f"Failed for: {text}")


class ActionRecognitionServiceTest(TestCase):
    """动作识别服务测试"""
    
    def setUp(self):
        self.cv_service = ActionRecognitionService()
    
    def test_calculate_angle(self):
        """测试角度计算"""
        # 测试直角
        a = {'x': 0, 'y': 0}
        b = {'x': 0, 'y': 1}
        c = {'x': 1, 'y': 1}
        
        angle = self.cv_service._calculate_angle(a, b, c)
        self.assertAlmostEqual(angle, 90.0, delta=0.1)
    
    @patch('services.cv_service.mp.solutions.pose.Pose')
    def test_estimate_pose(self, mock_pose):
        """测试姿态估计"""
        # 模拟MediaPipe返回结果
        mock_landmark = Mock()
        mock_landmark.x = 0.5
        mock_landmark.y = 0.5
        mock_landmark.z = 0.0
        mock_landmark.visibility = 0.9
        
        mock_results = Mock()
        mock_results.pose_landmarks.landmark = [mock_landmark] * 33
        
        mock_pose_instance = Mock()
        mock_pose_instance.process.return_value = mock_results
        mock_pose.return_value = mock_pose_instance
        
        # 创建测试图像
        import numpy as np
        test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # 测试姿态估计
        self.cv_service.pose = mock_pose_instance
        landmarks = self.cv_service._estimate_pose(test_frame)
        
        self.assertEqual(len(landmarks), 33)
        self.assertEqual(landmarks[0]['x'], 0.5)
        self.assertEqual(landmarks[0]['y'], 0.5)
```

### 7.3 API 测试设计

#### 7.3.1 认证API测试
```python
# tests/test_api_auth.py
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.accounts.models import User


class AuthenticationAPITest(APITestCase):
    """认证API测试"""
    
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.profile_url = reverse('profile')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'role': 'student'
        }
    
    def test_user_registration(self):
        """测试用户注册API"""
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # 验证用户已创建
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'student')
    
    def test_user_login(self):
        """测试用户登录API"""
        # 先注册用户
        self.client.post(self.register_url, self.user_data)
        
        # 测试登录
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_get_user_profile(self):
        """测试获取用户资料API"""
        # 先注册并登录
        self.client.post(self.register_url, self.user_data)
        
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        login_response = self.client.post(self.login_url, login_data)
        access_token = login_response.data['access']
        
        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # 获取用户资料
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')


class HomeworkAPITest(APITestCase):
    """作业API测试"""
    
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        # 获取token
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        self.homework_url = reverse('homework-list')
    
    def test_create_homework(self):
        """测试创建作业API"""
        data = {
            'subject': '数学',
            'title': '第一章练习题',
            'description': '基础练习题'
        }
        response = self.client.post(self.homework_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['subject'], '数学')
        self.assertEqual(response.data['title'], '第一章练习题')
        self.assertEqual(response.data['status'], 'uploaded')
    
    def test_get_homework_list(self):
        """测试获取作业列表API"""
        # 先创建一些作业
        for i in range(3):
            self.client.post(self.homework_url, {
                'subject': f'科目{i}',
                'title': f'作业{i}',
                'description': f'描述{i}'
            })
        
        response = self.client.get(self.homework_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_upload_homework_images(self):
        """测试上传作业图片API"""
        # 先创建作业
        homework_response = self.client.post(self.homework_url, {
            'subject': '数学',
            'title': '测试作业'
        })
        homework_id = homework_response.data['id']
        
        # 测试上传图片
        from io import BytesIO
        from PIL import Image
        
        # 创建测试图片
        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'JPEG')
        image_file.seek(0)
        
        upload_url = reverse('homework-upload-images', kwargs={'pk': homework_id})
        response = self.client.post(
            upload_url,
            {'images': image_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('homework_id', response.data)

### 7.4 性能测试设计

#### 7.4.1 负载测试
```python
# tests/performance/test_load.py
import pytest
from locust import HttpUser, task, between


class CoachAIUser(HttpUser):
    """CoachAI负载测试用户"""
    wait_time = between(1, 3)
    
    def on_start(self):
        """用户启动时执行"""
        # 登录获取token
        response = self.client.post("/api/v1/auth/login/", {
            "username": "testuser",
            "password": "testpassword123"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def get_homework_list(self):
        """获取作业列表"""
        self.client.get("/api/v1/homework/", headers=self.headers)
    
    @task(2)
    def create_homework(self):
        """创建作业"""
        self.client.post("/api/v1/homework/", {
            "subject": "数学",
            "title": "性能测试作业"
        }, headers=self.headers)
    
    @task(1)
    def get_exercise_records(self):
        """获取运动记录"""
        self.client.get("/api/v1/exercise/", headers=self.headers)
    
    @task(1)
    def get_tasks(self):
        """获取任务列表"""
        self.client.get("/api/v1/tasks/", headers=self.headers)
```

#### 7.4.2 数据库性能测试
```python
# tests/performance/test_database.py
import pytest
from django.test import TestCase
from django.db import connection
from apps.accounts.models import User
from apps.homework.models import Homework
import time


class DatabasePerformanceTest(TestCase):
    """数据库性能测试"""
    
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='perftest',
            email='perftest@example.com',
            password='testpass123'
        )
    
    def test_bulk_create_performance(self):
        """测试批量创建性能"""
        import time
        
        # 测试单个创建
        start_time = time.time()
        for i in range(100):
            Homework.objects.create(
                user=self.user,
                subject='数学',
                title=f'作业{i}'
            )
        single_create_time = time.time() - start_time
        
        # 清理数据
        Homework.objects.all().delete()
        
        # 测试批量创建
        start_time = time.time()
        homework_list = []
        for i in range(100):
            homework_list.append(Homework(
                user=self.user,
                subject='数学',
                title=f'作业{i}'
            ))
        Homework.objects.bulk_create(homework_list)
        bulk_create_time = time.time() - start_time
        
        # 验证性能提升
        print(f"单个创建时间: {single_create_time:.2f}秒")
        print(f"批量创建时间: {bulk_create_time:.2f}秒")
        print(f"性能提升: {single_create_time/bulk_create_time:.1f}倍")
        
        self.assertLess(bulk_create_time, single_create_time)
    
    def test_query_performance(self):
        """测试查询性能"""
        # 创建测试数据
        for i in range(1000):
            Homework.objects.create(
                user=self.user,
                subject='数学' if i % 2 == 0 else '语文',
                title=f'作业{i}',
                status='graded' if i % 3 == 0 else 'uploaded'
            )
        
        # 测试无索引查询
        start_time = time.time()
        for _ in range(100):
            list(Homework.objects.filter(subject='数学', status='graded'))
        no_index_time = time.time() - start_time
        
        print(f"无索引查询时间: {no_index_time:.2f}秒")
        
        # 这里可以测试添加索引后的性能
        # 实际项目中应该对比索引前后的性能差异

## 8. 部署配置设计

### 8.1 Docker 配置

#### 8.1.1 Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim as builder

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements/production.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r production.txt

# 复制项目文件
COPY . .

# 运行阶段
FROM python:3.11-slim

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN useradd -m -u 1000 appuser

# 设置工作目录
WORKDIR /app

# 从builder阶段复制已安装的包
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

# 设置权限
RUN chown -R appuser:appuser /app
USER appuser

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=coachai.settings.production

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "coachai.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

#### 8.1.2 Docker Compose 配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: coachai-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-rootpassword}
      MYSQL_DATABASE: coachai
      MYSQL_USER: coachai
      MYSQL_PASSWORD: ${MYSQL_PASSWORD:-coachaipassword}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./config/mysql/my.cnf:/etc/mysql/conf.d/my.cnf
    command: --default-authentication-plugin=mysql_native_password
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 10

  web:
    build: .
    container_name: coachai-web
    command: >
      sh -c "python manage.py wait_for_db &&
             python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn coachai.wsgi:application --bind 0.0.0.0:8000 --workers 4"
    environment:
      DATABASE_URL: mysql://coachai:${MYSQL_PASSWORD:-coachaipassword}@mysql:3306/coachai
      DJANGO_SETTINGS_MODULE: coachai.settings.production
      SECRET_KEY: ${DJANGO_SECRET_KEY}
      DEBUG: "False"
    ports:
      - "8000:8000"
    volumes:
      - media_volume:/app/media
      - static_volume:/app/staticfiles
    depends_on:
      mysql:
        condition: service_healthy
    restart: unless-stopped

  websocket:
    build: .
    container_name: coachai-websocket
    command: daphne -b 0.0.0.0 -p 8001 coachai.asgi:application
    environment:
      DATABASE_URL: mysql://coachai:${MYSQL_PASSWORD:-coachaipassword}@mysql:3306/coachai
      DJANGO_SETTINGS_MODULE: coachai.settings.production
      SECRET_KEY: ${DJANGO_SECRET_KEY}
    ports:
      - "8001:8001"
    volumes:
      - media_volume:/app/media
    depends_on:
      - mysql
    restart: unless-stopped

  worker:
    build: .
    container_name: coachai-worker
    command: python manage.py process_tasks --batch-size 20 --interval 30
    environment:
      DATABASE_URL: mysql://coachai:${MYSQL_PASSWORD:-coachaipassword}@mysql:3306/coachai
      DJANGO_SETTINGS_MODULE: coachai.settings.production
      SECRET_KEY: ${DJANGO_SECRET_KEY}
    volumes:
      - media_volume:/app/media
    depends_on:
      - mysql
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: coachai-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./config/nginx/ssl:/etc/nginx/ssl
      - static_volume:/static
      - media_volume:/media
    depends_on:
      - web
      - websocket
    restart: unless-stopped

volumes:
  mysql_data:
  media_volume:
  static_volume:
```

#### 8.1.3 Nginx 配置
```nginx
# config/nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
    
    # 优化设置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/xml application/xhtml+xml image/svg+xml;
    
    # 上游服务器
    upstream django {
        server web:8000;
    }
    
    upstream websocket {
        server websocket:8001;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # 重定向到HTTPS
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name localhost;
        
        # SSL证书配置
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        
        # 静态文件
        location /static/ {
            alias /static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # 媒体文件
        location /media/ {
            alias /media/;
            expires 30d;
            add_header Cache-Control "public";
        }
        
        # WebSocket
        location /ws/ {
            proxy_pass http://websocket;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 86400;
        }
        
        # API请求
        location /api/ {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # CORS头
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Authorization, Content-Type";
            
            # 处理预检请求
            if ($request_method = OPTIONS) {
                add_header Access-Control-Allow-Origin *;
                add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
                add_header Access-Control-Allow-Headers "Authorization, Content-Type";
                add_header Content-Length 0;
                add_header Content-Type text/plain;
                return 204;
            }
        }
        
        # 默认请求转发到Django
        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 8.2 环境变量配置

#### 8.2.1 环境变量文件
```bash
# .env.example
# Django设置
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库设置
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_PASSWORD=coachaipassword
MYSQL_DATABASE=coachai
MYSQL_USER=coachai
MYSQL_HOST=mysql
MYSQL_PORT=3306

# 缓存设置（未来扩展）
REDIS# 缓存设置（未来扩展）
REDIS_URL=redis://redis:6379/0

# 文件存储设置
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_ENDPOINT_URL=

# AI服务设置
OCR_ENGINE=paddle  # paddle 或 easy
USE_GPU=False
WHISPER_MODEL_SIZE=base

# 邮件设置（未来扩展）
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# 监控设置
SENTRY_DSN=
```

#### 8.2.2 环境变量管理脚本
```bash
#!/bin/bash
# scripts/generate_env.sh

# 生成环境变量文件
echo "生成环境变量文件..."

# 检查是否已存在.env文件
if [ -f .env ]; then
    echo "警告: .env文件已存在，将备份为.env.backup"
    cp .env .env.backup
fi

# 生成新的.env文件
cat > .env << EOF
# Django设置
DJANGO_SECRET_KEY=$(openssl rand -base64 32)
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库设置
MYSQL_ROOT_PASSWORD=$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9')
MYSQL_PASSWORD=$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9')
MYSQL_DATABASE=coachai
MYSQL_USER=coachai
MYSQL_HOST=mysql
MYSQL_PORT=3306

# 文件存储设置
MEDIA_ROOT=/app/media
STATIC_ROOT=/app/staticfiles

# AI服务设置
OCR_ENGINE=paddle
USE_GPU=False

# 时区设置
TZ=Asia/Shanghai
EOF

echo "环境变量文件已生成: .env"
echo "请根据需要修改配置"
```

### 8.3 数据库迁移策略

#### 8.3.1 迁移脚本
```python
# management/commands/wait_for_db.py
import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """等待数据库可用的Django命令"""
    
    def handle(self, *args, **options):
        self.stdout.write('等待数据库连接...')
        
        db_conn = None
        retries = 30
        
        while retries > 0:
            try:
                db_conn = connections['default']
                db_conn.cursor()
                self.stdout.write(self.style.SUCCESS('数据库连接成功'))
                break
            except OperationalError:
                self.stdout.write('数据库不可用，等待2秒...')
                time.sleep(2)
                retries -= 1
        
        if retries == 0:
            self.stdout.write(self.style.ERROR('数据库连接失败'))
            raise OperationalError("无法连接到数据库")
```

#### 8.3.2 数据库备份脚本
```bash
#!/bin/bash
# scripts/backup_database.sh

# 数据库备份脚本
BACKUP_DIR="/backup/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="coachai"

# 创建备份目录
mkdir -p $BACKUP_DIR

echo "开始备份数据库: $DB_NAME"

# 备份数据库
mysqldump -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASSWORD $DB_NAME \
  --single-transaction \
  --routines \
  --triggers \
  --events \
  > $BACKUP_DIR/${DB_NAME}_${DATE}.sql

# 检查备份是否成功
if [ $? -eq 0 ]; then
    echo "数据库备份成功: $BACKUP_DIR/${DB_NAME}_${DATE}.sql"
    
    # 压缩备份文件
    gzip $BACKUP_DIR/${DB_NAME}_${DATE}.sql
    echo "备份文件已压缩"
    
    # 保留最近7天备份
    find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
    echo "已清理7天前的备份文件"
else
    echo "数据库备份失败"
    exit 1
fi
```

## 9. GitHub 配置和推送

### 9.1 GitHub 仓库配置

#### 9.1.1 .gitignore 配置
```
# .gitignore

# Django
*.log
*.pot
*.pyc
__pycache__/
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Python
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Tests
.coverage
htmlcov/
.pytest_cache/
.tox/

# Jupyter Notebook
.ipynb_checkpoints

# Docker
docker-compose.override.yml

# Logs
logs/
*.log

# Temporary files
*.tmp
*.temp
```

#### 9.1.2 README.md 更新
```markdown
# CoachAI - 智能伴读AI系统

![CoachAI Logo](docs/images/logo.png)

## 项目简介

CoachAI 是一个集智能作业批改、动作识别计数、语音交互和任务管理于一体的智能伴读AI系统。通过摄像头和麦克风等外设，为学生提供个性化、互动式的学习陪伴体验。

## 核心功能

### 1. 智能作业批改
- 通过摄像头拍摄作业，自动识别题目和答案
- 智能批改与知识点分析
- 生成学习报告和薄弱点分析

### 2. 动作识别计数
- 实时识别跳绳、俯卧撑等运动动作
- 自动计数和姿势纠正
- 运动数据统计和分析

### 3. 语音交互系统
- 语音唤醒和自然语言指令
- 语音反馈和交互
- 支持多轮对话

### 4. 任务管理系统
- 每日TODO列表管理
- 任务进度跟踪
- 成就系统和激励机制

## 技术架构 (简化版本)

### 前端
- React 18 + TypeScript
- Ant Design / Chakra UI
- Vite 构建工具

### 后端
- Python + Django 5.0
- MySQL 8.0 (主数据库)
- 无中间件架构 (简化部署)
- Docker 容器化

### AI服务
- PaddleOCR / EasyOCR (OCR识别)
- OpenCV + MediaPipe (计算机视觉)
- Whisper / SpeechRecognition (语音识别)
- 基于数据库的异步任务处理

## 项目结构

```
coach-ai/
├── coachai/                    # Django项目配置
├── apps/                       # Django应用
│   ├── accounts/              # 用户管理
│   ├── homework/              # 作业管理
│   ├── exercise/              # 运动管理
│   ├── tasks/                 # 任务管理
│   └── common/                # 公共组件
├── services/                   # AI服务
├── documents/                  # 项目文档
├── docker/                     # Docker配置
├── scripts/                    # 部署脚本
├── tests/                      # 测试文件
├── requirements/               # 依赖管理
├── .env.example               # 环境变量示例
├── docker-compose.yml         # Docker编排
├── Dockerfile                 # Docker构建
├── pyproject.toml            # Poetry配置
├── README.md                  # 项目说明
└── LICENSE                    # GPL v3许可证
```

## 快速开始

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- Git

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/your-username/coach-ai.git
cd coach-ai

# 复制环境变量文件
cp .env.example .env

# 启动服务
docker-compose up -d

# 创建超级用户
docker-compose exec web python manage.py createsuperuser
```

### 访问应用
- Web界面: http://localhost
- API文档: http://localhost/swagger/
- Admin后台: http://localhost/admin/

## 开发指南

### 代码规范
- 使用Black进行代码格式化
- 使用Flake8进行代码检查
- 遵循Django最佳实践

### 测试
```bash
# 运行测试
docker-compose exec web pytest

# 运行特定测试
docker-compose exec web pytest tests/test_models.py

# 生成测试覆盖率报告
docker-compose exec web pytest --cov=.
```

### 代码提交
```bash
# 格式化代码
black .

# 检查代码质量
flake8

# 运行测试
pytest

# 提交代码
git add .
git commit -m "feat: 添加新功能"
git push
```

## 部署指南

### 生产环境部署
1. 配置生产环境变量
2. 设置SSL证书
3. 配置域名和DNS
4. 启动服务: `docker-compose -f docker-compose.prod.yml up -d`

### 监控和维护
- 日志查看: `docker-compose logs -f`
- 数据库备份: `./scripts/backup_database.sh`
- 服务重启: `docker-compose restart`

## 贡献指南

我们欢迎各种形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与项目开发。

### 开发流程
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

### 代码规范
- 遵循PEP 8 Python代码规范
- 使用类型提示(Type Hints)
- 编写清晰的文档字符串
- 添加适当的测试用例

## 许可证

本项目采用 [GNU General Public License v3.0](LICENSE)。

### 开源要求
- 本项目代码必须持续开源
- 任何基于本项目的衍生作品也必须开源
- 禁止将本项目用于闭源商业用途

## 联系方式

- 项目发起人: baofengbaofeng
- 项目仓库: https://github.com/your-username/coach-ai
- 问题反馈: 请使用 [GitHub Issues](https://github.com/your-username/coach-ai/issues)

## 相关链接

- [项目文档](documents/)
- [API文档](http://localhost/swagger/)
- [部署指南](docs/deployment.md)
- [开发指南](docs/development.md)

---

**CoachAI - Your Personal AI Learning Coach**
```

### 9.2 GitHub Actions 配置

#### 9.2.1 CI/CD 流水线
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: coachai_test
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
        ports:
          - 3306:3306
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements/base.txt
        pip install -r requirements/development.txt
    
    - name: Run migrations
      env:
        DATABASE_URL: mysql://root:root@localhost:3306/coachai_test
        DJANGO_SECRET_KEY: test-secret-key
      run: |
        python manage.py migrate
    
    - name: Run tests
      env:
        DATABASE_URL: mysql://root:root@localhost:3306/coachai_test
        DJANGO_SECRET_KEY: test-secret-key
      run: |
        pytest --cov=.
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
  
  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install black flake8
    
    - name: Check code formatting
      run: |
        black --check .
    
    - name: Lint with flake8
      run: |
        flake8 .
  
  build:
    needs: [test, lint]
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/coachai:latest
          ${{ secrets.DOCKER_USERNAME }}/coachai:${{ github.sha }}
```

#### 9.2.2 发布工作流
```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0
    
    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        name: Release ${{ github.ref_name }}
        draft: false
        prerelease: false
        generate_release_notes: true
```

### 9.3 项目初始化脚本

#### 9.3.1 初始化脚本
```bash
#!/bin/bash
# scripts/init_project.sh

echo "初始化 CoachAI 项目..."

# 检查Python版本
python_version=$(python3 --version | cut -d' ' -f2)
required_version="3.11.0"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "错误: 需要 Python 3.11 或更高版本"
    exit 1
fi

# 创建虚拟环境
echo "创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install --upgrade pip
pip install -r requirements/development.txt

# 设置环境变量
echo "设置环境变量..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "请编辑 .env 文件配置环境变量"
fi

# 创建数据库
echo "创建数据库..."
python manage.py migrate

# 创建超级用户
echo "创建超级用户..."
python manage.py createsuperuser

# 收集静态文件
echo "收集静态文件..."
python manage.py collectstatic --noinput

echo "项目初始化完成！"
echo "启动开发服务器: python manage.py runserver"
echo "访问: http://localhost:8000"
```

## 10. 总结

### 10.1 项目完成状态

#### ✅ 已完成的工作：
1. **需求分析文档**：BRD、PRD 完整
2. **技术架构设计**：简化架构，无中间件
3. **详细技术设计**：完整的设计文档
4. **AI服务设计**：OCR、CV、语音服务
5. **测试设计**：单元测试、集成测试、性能测试
6. **部署设计**：Docker、环境变量、数据库迁移
7. **GitHub配置**：CI/CD、文档、工作流

#### 🔄 待完成的工作（实际开发）：
1. **代码实现**：根据设计文档编写代码
2. **前端开发**：React前端界面
3. **AI模型训练**：优化识别准确率
4. **用户测试**：实际用户测试和反馈
5. **性能优化**：根据实际使用优化性能

### 10.2 下一步行动计划

#### 阶段1：基础开发（1-2周）
1. 创建Django项目结构
2. 实现核心模型和API
3. 开发基础前端界面
4. 集成基础AI服务

#### 阶段2：功能完善（2-3周）
1. 完善各模块功能
2. 优化用户体验
3. 加强AI识别准确率
4. 添加更多运动类型

#### 阶段3：测试优化（1-2
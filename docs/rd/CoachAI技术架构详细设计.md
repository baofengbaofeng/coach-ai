# CoachAI 技术架构详细设计

## 📋 文档信息

| 项目 | 内容 |
|------|------|
| **文档名称** | CoachAI 技术架构详细设计 |
| **文档版本** | 4.0.0 |
| **创建日期** | 2026-03-26 |
| **最后更新** | 2026-03-26 |
| **文档状态** | 正式版 |
| **作者** | CoachAI-RD (后端研发专家) |
| **审核人** | 待定 |
| **开源许可证** | GPL V3 (所有衍生代码需保持开源) |
| **关联文档** | [技术架构概要设计.md](./CoachAI技术架构概要设计.md) |
| **目标读者** | 开发团队、测试团队、运维团队 |

## 📝 修订历史

| 版本 | 日期 | 作者 | 变更描述 |
|------|------|------|----------|
| 3.0.0 | 2026-03-26 | CoachAI-RD | 基于Tornado框架的详细技术设计 |
| 4.0.0 | 2026-03-26 | CoachAI-RD | 重命名为技术架构详细设计，合并数据库设计内容 |

## 🎯 设计目标

### 1.1 核心设计目标
1. **高性能**：利用Tornado异步特性，支持高并发实时处理
2. **可维护**：代码结构清晰，符合编码规范，便于团队协作
3. **可扩展**：模块化设计，支持功能快速迭代和水平扩展
4. **安全可靠**：数据安全、权限控制、错误处理完善

### 1.2 代码规范要求
1. **编码规范**：所有前后端代码必须严格遵循`.rules/coding-style.md`文件定义的规则
2. **注释规范**：所有代码注释必须使用中文编写，确保团队理解一致
3. **命名规范**：遵循统一的命名约定，提高代码可读性
4. **质量检查**：建立代码审查机制，确保代码规范执行
5. **开源协议**：项目使用GPL V3开源协议，所有衍生代码需保持开源

### 1.3 技术约束
1. **Python 3.12**：使用venv虚拟环境
2. **Tornado框架**：异步Web框架
3. **MySQL 5.8**：关系型数据库（当前环境支持版本）
4. **编码规范**：严格遵循项目编码规范，中文注释
5. **数据库前缀**：所有表名使用统一前缀：`coach_ai_`

## 📊 数据库设计

### 2.1 数据库设计原则

#### 2.1.1 设计原则
1. **多租户隔离**：通过tenant_id字段实现数据隔离
2. **性能优先**：合理的索引设计，避免全表扫描
3. **扩展性**：支持水平扩展和垂直扩展
4. **数据一致性**：使用事务保证数据完整性
5. **安全性**：敏感数据加密存储，SQL注入防护

#### 2.1.2 命名规范
- **表名前缀**：所有表使用`coach_ai_`前缀
- **字段命名**：小写蛇形命名（snake_case）
- **索引命名**：`idx_表名_字段名`
- **外键命名**：`fk_表名_字段名`
- **约束命名**：`uk_表名_字段名`（唯一约束）

### 2.2 核心表结构设计

#### 2.2.1 用户表（coach_ai_users）
```sql
-- 用户表：存储系统用户信息，支持邮箱、手机号等多种登录方式
CREATE TABLE coach_ai_users (
    -- 主键和标识
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID，自增整数',
    uuid VARCHAR(36) NOT NULL UNIQUE COMMENT '用户唯一标识（UUID）',
    
    -- 登录信息
    email VARCHAR(255) UNIQUE COMMENT '邮箱（登录账号）',
    phone VARCHAR(20) UNIQUE COMMENT '手机号（登录账号）',
    username VARCHAR(50) UNIQUE COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    salt VARCHAR(32) NOT NULL COMMENT '密码盐值',
    
    -- 基本信息
    nickname VARCHAR(50) COMMENT '昵称',
    real_name VARCHAR(50) COMMENT '真实姓名',
    avatar_url VARCHAR(500) COMMENT '头像URL',
    gender ENUM('male', 'female', 'other') COMMENT '性别',
    birth_date DATE COMMENT '出生日期',
    
    -- 账户状态
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否激活',
    is_verified BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否已验证',
    is_locked BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否锁定',
    failed_login_attempts INT NOT NULL DEFAULT 0 COMMENT '失败登录次数',
    locked_until TIMESTAMP NULL COMMENT '锁定截止时间',
    
    -- 安全信息
    last_login_at TIMESTAMP NULL COMMENT '最后登录时间',
    last_login_ip VARCHAR(45) COMMENT '最后登录IP',
    mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否启用多因素认证',
    mfa_secret VARCHAR(32) COMMENT '多因素认证密钥',
    
    -- 时间信息
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    verified_at TIMESTAMP NULL COMMENT '验证时间',
    
    -- 扩展信息
    preferences JSON COMMENT '用户偏好设置',
    metadata JSON COMMENT '元数据',
    
    -- 索引
    INDEX idx_uuid (uuid),
    INDEX idx_email (email),
    INDEX idx_phone (phone),
    INDEX idx_username (username),
    INDEX idx_is_active (is_active),
    INDEX idx_created_at (created_at),
    
    -- 约束
    CHECK (failed_login_attempts >= 0),
    CONSTRAINT chk_login_method CHECK (
        email IS NOT NULL OR 
        phone IS NOT NULL OR 
        username IS NOT NULL
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统用户表';
```

#### 2.2.2 租户表（coach_ai_tenants）
```sql
-- 租户表：存储家庭租户信息，每个家庭对应一个租户
CREATE TABLE coach_ai_tenants (
    -- 主键和标识
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID，自增整数',
    uuid VARCHAR(36) NOT NULL UNIQUE COMMENT '租户唯一标识（UUID）',
    
    -- 基本信息
    name VARCHAR(100) NOT NULL COMMENT '租户名称（家庭名称）',
    family_type ENUM('core', 'couple', 'extended', 'single') NOT NULL COMMENT '家庭类型',
    description TEXT COMMENT '家庭描述',
    
    -- 订阅信息
    subscription_plan ENUM('basic', 'premium', 'professional') NOT NULL DEFAULT 'basic' COMMENT '订阅计划',
    subscription_status ENUM('active', 'suspended', 'cancelled') NOT NULL DEFAULT 'active' COMMENT '订阅状态',
    max_members INT NOT NULL DEFAULT 5 COMMENT '最大成员数量',
    storage_quota BIGINT UNSIGNED NOT NULL DEFAULT 10737418240 COMMENT '存储配额（字节，默认10GB）',
    
    -- 联系信息
    contact_email VARCHAR(255) COMMENT '联系邮箱',
    contact_phone VARCHAR(20) COMMENT '联系电话',
    
    -- 时间信息
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    subscription_start_at TIMESTAMP COMMENT '订阅开始时间',
    subscription_end_at TIMESTAMP COMMENT '订阅结束时间',
    
    -- 扩展信息
    settings JSON COMMENT '租户设置',
    metadata JSON COMMENT '元数据',
    
    -- 索引
    INDEX idx_uuid (uuid),
    INDEX idx_subscription_status (subscription_status),
    INDEX idx_created_at (created_at),
    INDEX idx_family_type (family_type),
    
    -- 约束
    CHECK (max_members > 0),
    CHECK (storage_quota > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='租户（家庭）信息表';
```

#### 2.2.3 家庭成员表（coach_ai_family_members）
```sql
-- 家庭成员表：关联用户和租户，定义用户在家庭中的角色和权限
CREATE TABLE coach_ai_family_members (
    -- 主键和标识
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID，自增整数',
    uuid VARCHAR(36) NOT NULL UNIQUE COMMENT '成员唯一标识（UUID）',
    
    -- 关联信息
    tenant_id BIGINT UNSIGNED NOT NULL COMMENT '租户ID，关联tenants表',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID，关联users表',
    
    -- 成员信息
    role ENUM('admin', 'parent', 'student', 'guest') NOT NULL COMMENT '成员角色',
    relationship VARCHAR(50) COMMENT '家庭关系（如父亲、母亲、儿子、女儿）',
    nickname_in_family VARCHAR(50) COMMENT '家庭内昵称',
    
    -- 权限信息
    permissions JSON NOT NULL COMMENT '权限配置',
    is_default BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否默认成员',
    
    -- 状态信息
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否活跃',
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
    left_at TIMESTAMP NULL COMMENT '离开时间',
    
    -- 时间信息
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 扩展信息
    settings JSON COMMENT '成员设置',
    metadata JSON COMMENT '元数据',
    
    -- 索引
    INDEX idx_uuid (uuid),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_user_id (user_id),
    UNIQUE INDEX uk_tenant_user (tenant_id, user_id),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active),
    
    -- 外键约束
    CONSTRAINT fk_family_members_tenant_id 
        FOREIGN KEY (tenant_id) 
        REFERENCES coach_ai_tenants (id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_family_members_user_id 
        FOREIGN KEY (user_id) 
        REFERENCES coach_ai_users (id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='家庭成员关联表';
```

### 2.3 业务表结构设计

#### 2.3.1 作业表（coach_ai_homeworks）
```sql
-- 作业表：存储学生作业信息，包括作业内容、状态和批改结果
CREATE TABLE coach_ai_homeworks (
    -- 主键和标识
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID，自增整数',
    uuid VARCHAR(36) NOT NULL UNIQUE COMMENT '作业唯一标识（UUID）',
    
    -- 租户和成员关联
    tenant_id BIGINT UNSIGNED NOT NULL COMMENT '租户ID，关联tenants表',
    student_id BIGINT UNSIGNED NOT NULL COMMENT '学生ID，关联family_members表',
    
    -- 作业基本信息
    title VARCHAR(200) NOT NULL COMMENT '作业标题',
    subject ENUM('math', 'chinese', 'english', 'physics', 'chemistry', 'biology', 'history', 'geography', 'other') NOT NULL COMMENT '作业科目',
    description TEXT COMMENT '作业描述',
    grade_level VARCHAR(20) COMMENT '年级',
    
    -- 作业状态
    status ENUM('pending', 'processing', 'reviewing', 'completed', 'failed') NOT NULL DEFAULT 'pending' COMMENT '作业状态',
    
    -- 图片信息
    image_url VARCHAR(500) NOT NULL COMMENT '作业图片URL',
    image_size INT NOT NULL DEFAULT 0 COMMENT '图片大小（字节）',
    image_width INT COMMENT '图片宽度（像素）',
    image_height INT COMMENT '图片高度（像素）',
    thumbnail_url VARCHAR(500) COMMENT '缩略图URL',
    
    -- OCR识别结果
    ocr_text TEXT COMMENT 'OCR识别文本',
    ocr_confidence FLOAT COMMENT 'OCR识别置信度',
    ocr_raw_result JSON COMMENT 'OCR原始识别结果',
    
    -- 批改结果
    total_score FLOAT COMMENT '总分',
    obtained_score FLOAT COMMENT '得分',
    accuracy_rate FLOAT COMMENT '正确率',
    correction_result JSON COMMENT '批改结果详情',
    
    -- 知识点分析
    knowledge_points JSON COMMENT '涉及的知识点',
    weak_points JSON COMMENT '薄弱知识点',
    suggestions TEXT COMMENT '学习建议',
    
    -- 时间信息
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
    processed_at TIMESTAMP NULL COMMENT '处理完成时间',
    reviewed_at TIMESTAMP NULL COMMENT '审核时间',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 扩展信息
    tags JSON COMMENT '标签',
    metadata JSON COMMENT '元数据',
    
    -- 索引
    INDEX idx_uuid (uuid),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_student_id (student_id),
    INDEX idx_subject (subject),
    INDEX idx_status (status),
    INDEX idx_submitted_at (submitted_at),
    INDEX idx_tenant_student (tenant_id, student_id),
    INDEX idx_tenant_status (tenant_id, status),
    
    -- 外键约束
    CONSTRAINT fk_homeworks_tenant_id 
        FOREIGN KEY (tenant_id) 
        REFERENCES coach_ai_tenants (id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_homeworks_student_id 
        FOREIGN KEY (student_id) 
        REFERENCES coach_ai_family_members (id) 
        ON DELETE CASCADE,
    
    -- 检查约束
    CHECK (image_size >= 0),
    CHECK (total_score IS NULL OR total_score >= 0),
    CHECK (obtained_score IS NULL OR obtained_score >= 0),
    CHECK (accuracy_rate IS NULL OR (accuracy_rate >= 0 AND accuracy_rate <= 1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生作业表';
```

#### 2.3.2 运动记录表（coach_ai_exercise_records）
```sql
-- 运动记录表：存储学生运动数据，包括运动类型、计数和姿势分析
CREATE TABLE coach_ai_exercise_records (
    -- 主键和标识
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID，自增整数',
    uuid VARCHAR(36) NOT NULL UNIQUE COMMENT '记录唯一标识（UUID）',
    
    -- 租户和成员关联
    tenant_id BIGINT UNSIGNED NOT NULL COMMENT '租户ID，关联tenants表',
    student_id BIGINT UNSIGNED NOT NULL COMMENT '学生ID，关联family_members表',
    
    -- 运动基本信息
    exercise_type ENUM('jump_rope', 'push_up', 'sit_up', 'squat', 'plank', 'other') NOT NULL COMMENT '运动类型',
    exercise_name VARCHAR(100) NOT NULL COMMENT '运动名称',
    description TEXT COMMENT '运动描述',
    
    -- 运动数据
    duration_seconds INT NOT NULL COMMENT '持续时间（秒）',
    count INT NOT NULL COMMENT '计数',
    calories_burned FLOAT COMMENT '消耗卡路里',
    average_heart_rate INT COMMENT '平均心率',
    
    -- 姿势分析
    posture_score FLOAT COMMENT '姿势评分',
    posture_feedback TEXT COMMENT '姿势反馈',
    incorrect_count INT COMMENT '错误次数',
    posture_details JSON COMMENT '姿势详情',
    
    -- 视频信息
    video_url VARCHAR(500) COMMENT '运动视频URL',
    video_duration INT COMMENT '视频时长（秒）',
    thumbnail_url VARCHAR(500) COMMENT '视频缩略图URL',
    
    -- AI分析结果
    ai_analysis JSON COMMENT 'AI分析结果',
    confidence_score FLOAT COMMENT '置信度评分',
    
    -- 时间信息
    started_at TIMESTAMP NOT NULL COMMENT '开始时间',
    ended_at TIMESTAMP NOT NULL COMMENT '结束时间',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 扩展信息
    tags JSON COMMENT '标签',
    metadata JSON COMMENT '元数据',
    
    -- 索引
    INDEX idx_uuid (uuid),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_student_id (student_id),
    INDEX idx_exercise_type (exercise_type),
    INDEX idx_started_at (started_at),
    INDEX idx_tenant_student (tenant_id, student_id),
    INDEX idx_tenant_exercise (tenant_id, exercise_type),
    
    -- 外键约束
    CONSTRAINT fk_exercise_records_tenant_id 
        FOREIGN KEY (tenant_id) 
        REFERENCES coach_ai_tenants (id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_exercise_records_student_id 
        FOREIGN KEY (student_id) 
        REFERENCES coach_ai_family_members (id) 
        ON DELETE CASCADE,
    
    -- 检查约束
    CHECK (duration_seconds > 0),
    CHECK (count >= 0),
    CHECK (calories_burned IS NULL OR calories_burned >= 0),
    CHECK (average_heart_rate
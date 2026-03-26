# CoachAI 技术方案实施指南

## 📋 文档信息

| 项目 | 内容 |
|------|------|
| **文档名称** | CoachAI 技术方案实施指南 |
| **文档版本** | 1.0.0 |
| **创建日期** | 2026-03-26 |
| **最后更新** | 2026-03-26 |
| **文档状态** | 正式版 |
| **作者** | CoachAI-RD (后端研发专家) |
| **审核人** | 待定 |
| **关联文档** | [技术架构概要设计（Tornado版）.md](./CoachAI技术架构概要设计（Tornado版）.md) |
| **目标读者** | 开发团队、测试团队、运维团队 |

## 🎯 实施目标

### 1.1 核心实施目标
1. **快速启动**：在1周内完成开发环境搭建和基础框架搭建
2. **MVP优先**：优先实现核心功能（作业批改、运动计数）
3. **质量保证**：确保代码质量，符合编码规范，有完善的测试
4. **可部署**：支持开发、测试、生产环境的部署

### 1.2 技术约束
1. **Python 3.12**：使用venv虚拟环境
2. **Tornado框架**：异步Web框架
3. **MySQL数据库**：关系型数据库
4. **编码规范**：严格遵循项目编码规范，中文注释

## 🚀 快速开始指南

### 2.1 环境准备

#### 2.1.1 系统要求
- **操作系统**：Linux/macOS/Windows WSL2
- **Python版本**：3.12.0 或更高
- **MySQL版本**：8.0 或更高
- **Node.js版本**：18.0 或更高（前端开发）

#### 2.1.2 开发工具
- **代码编辑器**：VS Code 或 PyCharm
- **数据库工具**：MySQL Workbench 或 DBeaver
- **API测试工具**：Postman 或 Insomnia
- **版本控制**：Git

### 2.2 项目初始化

#### 2.2.1 克隆项目
```bash
# 克隆项目代码
git clone https://github.com/baofengbaofeng/coach-ai.git
cd coach-ai

# 切换到后端目录
cd coach-ai-backend
```

#### 2.2.2 设置Python虚拟环境
```bash
# 创建虚拟环境（使用Python 3.12）
python3.12 -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

# 升级pip
pip install --upgrade pip
```

#### 2.2.3 安装依赖
```bash
# 安装生产依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

#### 2.2.4 配置环境变量
```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑.env文件，配置数据库等参数
# 使用文本编辑器打开.env文件，根据实际情况修改配置
```

#### 2.2.5 数据库初始化
```bash
# 创建数据库（需要MySQL已安装并运行）
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS coachai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 运行数据库迁移
alembic upgrade head

# 初始化基础数据（可选）
python scripts/init_data.py
```

#### 2.2.6 启动开发服务器
```bash
# 启动Tornado开发服务器
python src/main.py --port=8000 --debug

# 或者使用开发脚本
./scripts/start_dev.sh
```

### 2.3 前端开发环境

#### 2.3.1 前端项目初始化
```bash
# 切换到前端目录
cd ../coach-ai-frontend

# 安装Node.js依赖
npm install

# 启动开发服务器
npm run dev
```

#### 2.3.2 访问应用
- **后端API**：http://localhost:8000
- **前端应用**：http://localhost:3000
- **API文档**：http://localhost:8000/docs

## 📁 代码结构说明

### 3.1 后端代码结构

#### 3.1.1 核心目录说明
```
src/
├── config/           # 配置模块
│   ├── settings.py   # 应用配置
│   ├── database.py   # 数据库配置
│   └── logging_config.py # 日志配置
│
├── core/             # 核心模块
│   ├── exceptions.py # 自定义异常
│   ├── middleware.py # 中间件
│   ├── authentication.py # 认证授权
│   ├── tenant.py     # 租户管理
│   └── cache.py      # 缓存管理
│
├── api/              # API接口层
│   ├── v1/           # API版本1
│   │   ├── handlers/ # 请求处理器
│   │   ├── schemas/  # 请求响应模型
│   │   └── routers.py # 路由配置
│   └── docs.py       # API文档生成
│
├── services/         # 业务服务层
│   ├── tenant_service.py    # 租户服务
│   ├── family_service.py    # 家庭服务
│   ├── exercise_service.py  # 运动服务
│   ├── homework_service.py  # 作业服务
│   ├── ai_service.py        # AI服务
│   └── webrtc_service.py    # WebRTC服务
│
├── models/           # 数据模型层
│   ├── base.py       # 基础模型类
│   ├── user.py       # 用户模型
│   ├── tenant.py     # 租户模型
│   ├── family.py     # 家庭模型
│   ├── exercise.py   # 运动模型
│   ├── homework.py   # 作业模型
│   └── achievement.py # 成就模型
│
├── database/         # 数据库层
│   ├── session.py    # 数据库会话管理
│   ├── migrations/   # 数据库迁移
│   └── repositories/ # 数据仓库
│
├── utils/            # 工具模块
│   ├── validators.py # 数据验证器
│   ├── security.py   # 安全工具
│   ├── file_utils.py # 文件处理工具
│   ├── date_utils.py # 日期时间工具
│   └── logging_utils.py # 日志工具
│
└── tasks/            # 异步任务模块
    ├── base.py       # 基础任务类
    ├── exercise_tasks.py # 运动相关任务
    └── homework_tasks.py # 作业相关任务
```

#### 3.1.2 配置文件说明
- **.env**：环境变量配置文件（不提交到Git）
- **.env.example**：环境变量示例文件
- **pyproject.toml**：项目配置和构建工具配置
- **requirements.txt**：生产环境依赖包
- **requirements-dev.txt**：开发环境依赖包

### 3.2 前端代码结构

#### 3.2.1 核心目录说明
```
coach-ai-frontend/
├── public/           # 静态资源
├── src/
│   ├── assets/       # 资源文件（图片、字体等）
│   ├── components/   # 可复用组件
│   ├── composables/  # 组合式函数
│   ├── layouts/      # 布局组件
│   ├── pages/        # 页面组件
│   ├── router/       # 路由配置
│   ├── stores/       # 状态管理
│   ├── styles/       # 样式文件
│   ├── types/        # TypeScript类型定义
│   ├── utils/        # 工具函数
│   └── main.ts       # 应用入口
│
├── index.html        # HTML模板
├── package.json      # 项目配置和依赖
├── tsconfig.json     # TypeScript配置
├── vite.config.ts    # Vite构建配置
└── README.md         # 项目说明
```

## 🔧 开发工作流

### 4.1 代码开发流程

#### 4.1.1 功能开发步骤
1. **需求分析**：阅读产品文档，理解功能需求
2. **数据库设计**：设计数据模型，创建迁移脚本
3. **API设计**：设计API接口，定义请求响应模型
4. **服务实现**：实现业务逻辑，编写单元测试
5. **前端实现**：实现用户界面，调用后端API
6. **集成测试**：进行端到端测试，确保功能完整
7. **代码审查**：提交代码审查，确保代码质量
8. **部署上线**：部署到测试环境，验证功能

#### 4.1.2 代码提交规范
```bash
# 创建功能分支
git checkout -b feature/作业批改功能

# 开发代码
# ... 编写代码 ...

# 添加更改
git add .

# 提交更改（使用中文提交信息）
git commit -m "feat: 实现作业批改核心功能

- 添加作业模型和数据库迁移
- 实现作业图片上传接口
- 集成OCR识别服务
- 添加作业批改结果存储"

# 推送到远程仓库
git push origin feature/作业批改功能

# 创建Pull Request
# 在GitHub上创建PR，请求代码审查
```

#### 4.1.3 提交信息规范
- **feat**：新功能
- **fix**：修复bug
- **docs**：文档更新
- **style**：代码格式调整
- **refactor**：代码重构
- **test**：测试相关
- **chore**：构建过程或辅助工具变动

### 4.2 数据库开发流程

#### 4.2.1 创建数据模型
```python
# src/models/homework.py
"""
作业数据模型模块，定义作业相关的数据模型，包括作业记录、批改结果、知识点分析等。
支持多租户数据隔离，记录作业的完整生命周期，从创建到批改完成。
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Text, Integer, Float, JSON, Enum, ForeignKey
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship, Mapped, mapped_column
from enum import Enum as PyEnum

from src.models.base import TenantBaseModel


# 日志配置
_LOGGER = logging.getLogger(__name__)


class HomeworkStatus(PyEnum):
    """作业状态枚举，定义作业在整个处理流程中的各个状态。"""
    
    PENDING = "pending"          # 待处理，作业已创建但未开始批改
    PROCESSING = "processing"    # 处理中，正在执行OCR识别和批改
    REVIEWING = "reviewing"      # 审核中，需要人工审核或确认
    COMPLETED = "completed"      # 已完成，批改完成并生成报告
    FAILED = "failed"            # 失败，处理过程中出现错误


class HomeworkSubject(PyEnum):
    """作业科目枚举，定义支持的作业科目类型。"""
    
    MATH = "math"                # 数学
    CHINESE = "chinese"          # 语文
    ENGLISH = "english"          # 英语
    PHYSICS = "physics"          # 物理
    CHEMISTRY = "chemistry"      # 化学
    BIOLOGY = "biology"          # 生物
    HISTORY = "history"          # 历史
    GEOGRAPHY = "geography"      # 地理
    OTHER = "other"              # 其他科目


class HomeworkModel(TenantBaseModel):
    """
    作业模型类，记录学生作业的基本信息、状态和批改结果。
    包含作业图片、识别结果、批改详情和知识点分析等完整信息。
    """
    
    __tablename__ = "homeworks"
    
    # 作业基本信息
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="作业标题"
    )
    
    subject: Mapped[HomeworkSubject] = mapped_column(
        Enum(HomeworkSubject),
        nullable=False,
        comment="作业科目"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="作业描述"
    )
    
    # 学生信息
    student_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        nullable=False,
        index=True,
        comment="学生ID，关联family_members表"
    )
    
    # 作业状态
    status: Mapped[HomeworkStatus] = mapped_column(
        Enum(HomeworkStatus),
        nullable=False,
        default=HomeworkStatus.PENDING,
        comment="作业状态"
    )
    
    # 图片信息
    image_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="作业图片URL"
    )
    
    image_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="图片大小（字节）"
    )
    
    image_width: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="图片宽度（像素）"
    )
    
    image_height: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="图片高度（像素）"
    )
    
    # OCR识别结果
    ocr_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="OCR识别文本"
    )
    
    ocr_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="OCR识别置信度"
    )
    
    ocr_raw_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="OCR原始识别结果"
    )
    
    # 批改结果
    total_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="总分"
    )
    
    obtained_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="得分"
    )
    
    correction_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="批改结果详情"
    )
    
    # 知识点分析
    knowledge_points: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="涉及的知识点"
    )
    
    weak_points: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="薄弱知识点"
    )
    
    # 时间信息
    submitted_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.now,
        comment="提交时间"
    )
    
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="处理完成时间"
    )
    
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="审核时间"
    )
    
    # 关系定义
    corrections: Mapped[List["HomeworkCorrectionModel"]] = relationship(
        "HomeworkCorrectionModel",
        back_populates="homework",
        cascade="all, delete-orphan"
    )
    
    # 表级约束
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id"],
            ["family_members.id"],
            name="fk_homeworks_student_id",
            ondelete="CASCADE"
        ),
        Index("idx_homeworks_tenant_student", "tenant_id", "student_id"),
        Index("idx_homeworks_tenant_status", "tenant_id", "status"),
        Index("idx_homeworks_submitted_at", "submitted_at"),
    )
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """
        生成作业摘要信息，用于列表展示，包含基本信息但不包含详细批改结果。
        
        Returns:
            包含作业摘要信息的字典，适合列表展示场景
        """
        return {
            "id": self.id,
            "uuid": str(self.uuid),
            "title": self.title,
            "subject": self.subject.value,
            "status": self.status.value,
            "student_id": self.student_id,
            "total_score": self.total_score,
            "obtained_score": self.obtained_score,
            "submitted_at": self.submitted_at.isoformat(),
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }
    
    def to_detail_dict(self) -> Dict[str, Any]:
        """
        生成作业详细信息，用于详情展示，包含完整的批改结果和知识点分析。
        
        Returns:
            包含作业完整信息的字典，适合详情展示场景
        """
        result = self.to_summary_dict()
        result.update({
            "description": self.description,
            "image_url": self.image_url,
            "image_size": self.image_size,
            "ocr_text": self.ocr_text,
            "ocr_confidence": self.ocr_confidence,
            "correction_result": self.correction_result,
            "knowledge_points": self.knowledge_points,
            "weak_points": self.weak_points,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "corrections": [correction.to_dict() for correction in self.corrections],
        })
        return result
```

#### 4.
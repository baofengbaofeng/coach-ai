# CoachAI 前端技术架构文档

## 技术栈选型

### 核心框架
- **React 18** - 现代、高性能的UI库
- **TypeScript** - 类型安全，提高代码质量和开发体验
- **Vite** - 快速构建工具，优秀的开发体验

### 状态管理
- **React Query (TanStack Query)** - 服务器状态管理
- **React Context + useReducer** - 客户端状态管理

### 路由
- **React Router DOM v6** - 客户端路由

### UI组件库
- **Ant Design** - 企业级UI组件库（根据项目README选择）
- **Styled Components** - CSS-in-JS解决方案

### HTTP客户端
- **Axios** - HTTP请求库

### 表单处理
- **React Hook Form** - 高性能表单处理
- **Zod** - 表单验证

### 工具库
- **date-fns** - 日期处理
- **lodash-es** - 实用工具函数

## 项目结构

```
frontend/
├── public/                    # 静态资源
├── src/
│   ├── assets/               # 静态资源（图片、字体等）
│   ├── components/           # 可复用组件
│   │   ├── common/           # 通用组件（Button, Input, Modal等）
│   │   ├── layout/           # 布局组件
│   │   ├── homework/         # 作业相关组件
│   │   ├── exercise/         # 运动相关组件
│   │   ├── tasks/            # 任务相关组件
│   │   └── achievements/     # 成就相关组件
│   ├── hooks/                # 自定义Hooks
│   ├── layouts/              # 页面布局
│   ├── pages/                # 页面组件
│   │   ├── Home/             # 首页
│   │   ├── Login/            # 登录页
│   │   ├── Dashboard/        # 仪表板
│   │   ├── Homework/         # 作业管理
│   │   ├── Exercise/         # 运动管理
│   │   ├── Tasks/            # 任务管理
│   │   └── Achievements/     # 成就系统
│   ├── services/             # API服务
│   │   ├── api/              # API客户端配置
│   │   ├── auth/             # 认证服务
│   │   ├── homework/         # 作业服务
│   │   ├── exercise/         # 运动服务
│   │   ├── tasks/            # 任务服务
│   │   └── achievements/     # 成就服务
│   ├── stores/               # 状态管理
│   ├── types/                # TypeScript类型定义
│   ├── utils/                # 工具函数
│   ├── styles/               # 全局样式
│   ├── App.tsx               # 应用根组件
│   ├── main.tsx              # 应用入口
│   └── vite-env.d.ts         # Vite类型声明
├── .env                      # 环境变量
├── .env.example              # 环境变量示例
├── package.json              # 依赖管理
├── tsconfig.json             # TypeScript配置
├── vite.config.ts            # Vite配置
└── README.md                 # 项目说明
```

## API接口设计

### 基础配置
```typescript
// src/services/api/config.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
```

### 接口模块
1. **认证模块** (`/api/v1/auth/`)
   - 登录/注册
   - 令牌刷新
   - 用户信息

2. **作业模块** (`/api/v1/homework/`)
   - 作业上传
   - 作业批改
   - 知识点分析
   - 学习报告

3. **运动模块** (`/api/v1/exercise/`)
   - 运动记录
   - 实时计数
   - 姿势评估
   - 数据统计

4. **任务模块** (`/api/v1/tasks/`)
   - 任务创建
   - 进度跟踪
   - 提醒设置

5. **成就模块** (`/api/v1/achievements/`)
   - 成就解锁
   - 进度跟踪
   - 奖励发放

## 状态管理策略

### 服务器状态 (React Query)
- 用户数据
- 作业列表
- 运动记录
- 任务列表
- 成就进度

### 客户端状态 (Context + useReducer)
- UI状态（侧边栏展开/收起）
- 主题设置
- 表单状态
- 临时数据

## 路由设计

```typescript
const routes = [
  {
    path: '/',
    element: <Home />,
  },
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/dashboard',
    element: <ProtectedRoute><Dashboard /></ProtectedRoute>,
    children: [
      { path: 'homework', element: <HomeworkPage /> },
      { path: 'exercise', element: <ExercisePage /> },
      { path: 'tasks', element: <TasksPage /> },
      { path: 'achievements', element: <AchievementsPage /> },
    ],
  },
];
```

## 组件设计原则

### 1. 原子设计
- **Atoms**: 基础组件（Button, Input, Icon）
- **Molecules**: 组合组件（SearchBar, Card）
- **Organisms**: 复杂组件（Header, Sidebar）
- **Templates**: 页面模板
- **Pages**: 完整页面

### 2. 单一职责
每个组件只负责一个功能

### 3. 可复用性
组件设计要考虑复用场景

### 4. 可测试性
组件要易于单元测试

## 样式方案

### 1. 全局样式
- 重置样式
- 主题变量
- 字体定义

### 2. 组件样式
- Styled Components
- CSS Modules（可选）

### 3. 响应式设计
- 移动优先
- 断点设计

## 开发规范

### 代码规范
- ESLint + Prettier
- TypeScript严格模式
- 组件命名规范

### Git工作流
- 功能分支
- 代码审查
- 自动化测试

### 测试策略
- 单元测试（Jest + React Testing Library）
- 集成测试
- E2E测试（Cypress）

## 性能优化

### 1. 代码分割
- 路由级代码分割
- 组件懒加载

### 2. 图片优化
- 图片压缩
- 懒加载
- WebP格式

### 3. 缓存策略
- 浏览器缓存
- API响应缓存

### 4. 包体积优化
- Tree Shaking
- 按需引入

## 部署策略

### 开发环境
- 本地开发服务器
- 热重载

### 生产环境
- 静态文件托管
- CDN加速
- 环境变量管理

## 监控与日志

### 错误监控
- Sentry集成
- 错误边界

### 性能监控
- Web Vitals
- 自定义指标

### 用户行为分析
- 页面访问
- 功能使用

## 安全考虑

### 1. 认证安全
- JWT令牌管理
- 刷新令牌机制

### 2. 数据安全
- XSS防护
- CSRF防护

### 3. 代码安全
- 依赖安全检查
- 敏感信息管理

## 未来扩展

### 1. 移动端
- React Native
- PWA支持

### 2. 实时功能
- WebSocket
- 实时通知

### 3. 国际化
- i18n支持
- 多语言切换

---

**版本历史**
- v1.0.0 (2026-03-25): 初始版本创建
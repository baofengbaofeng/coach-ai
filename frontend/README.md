# CoachAI 前端项目

CoachAI智能伴读AI系统的前端项目，基于React 18 + TypeScript + Vite构建。

## 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **路由**: React Router DOM v6
- **状态管理**: React Query (TanStack Query)
- **HTTP客户端**: Axios
- **UI组件**: Heroicons + 自定义组件
- **样式**: Tailwind CSS
- **代码规范**: ESLint + Prettier

## 项目结构

```
frontend/
├── public/                    # 静态资源
├── src/
│   ├── assets/               # 静态资源（图片、字体等）
│   ├── components/           # 可复用组件
│   │   ├── auth/             # 认证相关组件
│   │   ├── common/           # 通用组件
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
├── tailwind.config.js        # Tailwind配置
├── postcss.config.js         # PostCSS配置
└── README.md                 # 项目说明
```

## 快速开始

### 环境要求
- Node.js 18+ 
- npm 9+

### 安装依赖
```bash
npm install
```

### 环境配置
复制环境变量文件并配置：
```bash
cp .env.example .env
```

编辑 `.env` 文件，配置API地址：
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 开发服务器
```bash
npm run dev
```
访问 http://localhost:3000

### 构建生产版本
```bash
npm run build
```

### 预览生产版本
```bash
npm run preview
```

## 开发指南

### 代码规范
- 使用TypeScript严格模式
- 组件使用函数式组件 + Hooks
- 遵循React最佳实践
- 使用ESLint + Prettier进行代码格式化

### 组件开发
1. 组件放在 `src/components/` 对应目录下
2. 使用TypeScript定义Props类型
3. 组件命名使用PascalCase
4. 文件命名使用PascalCase.tsx

### API集成
1. 在 `src/services/` 目录下创建对应服务
2. 使用React Query管理服务器状态
3. 错误处理统一在API拦截器中处理
4. 类型定义放在 `src/types/` 目录下

### 样式开发
1. 使用Tailwind CSS进行样式开发
2. 优先使用原子类，避免自定义CSS
3. 响应式设计使用Tailwind断点
4. 主题颜色使用配置的primary色系

## API接口

### 认证接口
- `POST /api/v1/auth/login/` - 用户登录
- `POST /api/v1/auth/token/refresh/` - 刷新令牌

### 作业接口
- `GET /api/v1/homework/homeworks/` - 获取作业列表
- `POST /api/v1/homework/homeworks/` - 创建作业
- `GET /api/v1/homework/homeworks/{id}/` - 获取作业详情
- `PUT /api/v1/homework/homeworks/{id}/` - 更新作业
- `DELETE /api/v1/homework/homeworks/{id}/` - 删除作业
- `POST /api/v1/homework/upload/` - 上传作业图片

### 运动接口
- `GET /api/v1/exercise/exercises/` - 获取运动记录
- `POST /api/v1/exercise/exercises/` - 创建运动记录

### 任务接口
- `GET /api/v1/tasks/tasks/` - 获取任务列表
- `POST /api/v1/tasks/tasks/` - 创建任务

### 成就接口
- `GET /api/v1/achievements/achievements/` - 获取成就列表
- `GET /api/v1/achievements/user-achievements/` - 获取用户成就

## 状态管理

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
      { index: true, element: <DashboardHome /> },
      { path: 'homework', element: <HomeworkPage /> },
      { path: 'exercise', element: <ExercisePage /> },
      { path: 'tasks', element: <TasksPage /> },
      { path: 'achievements', element: <AchievementsPage /> },
    ],
  },
];
```

## 部署

### 构建
```bash
npm run build
```

### 静态文件部署
构建后的文件在 `dist/` 目录，可以部署到：
- Nginx
- Apache
- Vercel
- Netlify
- GitHub Pages

### 环境变量
生产环境需要配置以下环境变量：
```env
VITE_API_BASE_URL=https://api.yourdomain.com/api/v1
VITE_APP_NAME=CoachAI
VITE_APP_VERSION=1.0.0
VITE_DEBUG=false
```

## 开发计划

### 第一阶段 (MVP)
- [x] 项目初始化
- [x] 基础架构搭建
- [x] 认证系统
- [x] 仪表板首页
- [ ] 作业管理页面
- [ ] 运动管理页面
- [ ] 任务管理页面
- [ ] 成就系统页面

### 第二阶段 (功能完善)
- [ ] 实时运动识别
- [ ] 作业拍照上传
- [ ] 语音交互
- [ ] 移动端适配
- [ ] 离线功能

### 第三阶段 (优化扩展)
- [ ] PWA支持
- [ ] 多语言支持
- [ ] 主题切换
- [ ] 性能优化
- [ ] 监控告警

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

## 许可证

本项目采用 [GNU General Public License v3.0](../LICENSE)。

## 联系方式

- 项目仓库: https://github.com/your-username/coach-ai
- 问题反馈: 请使用 GitHub Issues
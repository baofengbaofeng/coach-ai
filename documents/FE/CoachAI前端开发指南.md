# CoachAI前端开发指南

## 📋 概述

本文档是CoachAI项目的前端开发指南，由FE (前端工程师) subagent创建和维护。文档按照项目文档规范要求，使用中文文件名，存储在`docs/开发指南/`目录下。

## 🏗️ 前端技术架构

### 1. 技术栈选型
#### 核心框架：
- **React 18**: 现代React框架，支持并发特性
- **TypeScript 5.0**: 强类型JavaScript超集
- **Vite 5.0**: 下一代前端构建工具

#### 状态管理：
- **React Query (TanStack Query)**: 服务器状态管理
- **React Context + useReducer**: 客户端状态管理
- **Zustand**: 轻量级状态管理（可选）

#### UI和样式：
- **Tailwind CSS 3.0**: 原子化CSS框架
- **Heroicons**: SVG图标库
- **Headless UI**: 无样式UI组件库
- **自定义组件库**: 项目专用组件库

#### 开发工具：
- **ESLint**: 代码质量检查
- **Prettier**: 代码格式化
- **Husky**: Git钩子管理
- **Commitlint**: 提交信息规范

### 2. 项目结构
```
coach-ai/frontend/
├── 📁 public/                    # 静态资源
├── 📁 src/                       # 源代码
│   ├── 📁 components/           # 可复用组件
│   │   ├── 📁 common/          # 通用组件
│   │   ├── 📁 layout/          # 布局组件
│   │   ├── 📁 forms/           # 表单组件
│   │   └── 📁 ui/              # UI基础组件
│   ├── 📁 pages/                # 页面组件
│   │   ├── 📁 auth/            # 认证相关页面
│   │   ├── 📁 dashboard/       # 仪表板页面
│   │   ├── 📁 exercise/        # 运动管理页面
│   │   ├── 📁 tasks/           # 任务管理页面
│   │   └── 📁 achievements/    # 成就系统页面
│   ├── 📁 services/             # API服务
│   │   ├── api/                # API客户端
│   │   ├── auth/               # 认证服务
│   │   ├── exercise/           # 运动服务
│   │   ├── tasks/              # 任务服务
│   │   └── achievements/       # 成就服务
│   ├── 📁 hooks/                # 自定义Hooks
│   ├── 📁 utils/                # 工具函数
│   ├── 📁 types/                # TypeScript类型定义
│   ├── 📁 styles/               # 全局样式
│   └── 📁 constants/            # 常量定义
├── 📄 vite.config.ts            # Vite配置
├── 📄 tsconfig.json             # TypeScript配置
├── 📄 tailwind.config.js        # Tailwind配置
├── 📄 package.json              # 依赖管理
└── 📄 README.md                 # 项目说明
```

## 🛠️ 开发环境配置

### 1. 环境要求
#### 系统要求：
- **Node.js**: >= 18.0.0
- **npm**: >= 9.0.0 或 **yarn**: >= 1.22.0
- **Git**: >= 2.30.0

#### 开发工具：
- **VS Code**: 推荐编辑器
- **React Developer Tools**: 浏览器扩展
- **Redux DevTools**: 状态管理调试工具

### 2. 项目初始化
#### 克隆项目：
```bash
git clone https://github.com/baofengbaofeng/coach-ai.git
cd coach-ai/frontend
```

#### 安装依赖：
```bash
npm install
# 或
yarn install
```

#### 启动开发服务器：
```bash
npm run dev
# 或
yarn dev
```

#### 访问应用：
打开浏览器访问：http://localhost:5173

### 3. 环境变量配置
#### 开发环境 (.env.development):
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=CoachAI Development
VITE_DEBUG=true
```

#### 生产环境 (.env.production):
```env
VITE_API_BASE_URL=https://api.coachai.example.com/api
VITE_APP_NAME=CoachAI
VITE_DEBUG=false
```

## 📝 编码规范

### 1. 文件命名规范
#### 组件文件：
- **PascalCase**: 组件使用大驼峰命名
  - `UserProfile.tsx`
  - `ExerciseRecordList.tsx`
  - `TaskAssignmentForm.tsx`

#### 工具文件：
- **camelCase**: 工具函数使用小驼峰命名
  - `formatDate.ts`
  - `apiClient.ts`
  - `validationUtils.ts`

#### 样式文件：
- **kebab-case**: 样式文件使用短横线命名
  - `global-styles.css`
  - `component-styles.module.css`

### 2. 组件开发规范
#### 函数组件：
```typescript
// ✅ 正确的组件写法
import React from 'react';
import { User } from '@/types';

interface UserProfileProps {
  user: User;
  onUpdate?: (user: User) => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ 
  user, 
  onUpdate 
}) => {
  // 组件逻辑
  return (
    <div className="user-profile">
      {/* 组件内容 */}
    </div>
  );
};
```

#### Props定义：
- 使用TypeScript接口定义Props
- 提供默认值和可选标记
- 添加详细的JSDoc注释

### 3. 状态管理规范
#### 服务器状态 (React Query):
```typescript
import { useQuery, useMutation } from '@tanstack/react-query';
import { exerciseApi } from '@/services/api/exercise';

// 查询示例
export const useExerciseRecords = (userId: string) => {
  return useQuery({
    queryKey: ['exercise-records', userId],
    queryFn: () => exerciseApi.getRecords(userId),
    staleTime: 5 * 60 * 1000, // 5分钟
  });
};

// 突变示例
export const useCreateExerciseRecord = () => {
  return useMutation({
    mutationFn: exerciseApi.createRecord,
    onSuccess: () => {
      // 成功处理
    },
    onError: (error) => {
      // 错误处理
    },
  });
};
```

#### 客户端状态 (Context + useReducer):
```typescript
import React, { createContext, useContext, useReducer } from 'react';

interface AppState {
  theme: 'light' | 'dark';
  notifications: Notification[];
  sidebarOpen: boolean;
}

type AppAction = 
  | { type: 'SET_THEME'; payload: 'light' | 'dark' }
  | { type: 'ADD_NOTIFICATION'; payload: Notification }
  | { type: 'TOGGLE_SIDEBAR' };

const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
} | null>(null);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);
  
  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};
```

## 🔌 API集成指南

### 1. API客户端配置
#### Axios配置：
```typescript
import axios from 'axios';
import { getToken, clearToken } from './auth';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearToken();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 2. API服务层
#### 服务模块示例：
```typescript
// services/api/exercise.ts
import apiClient from '../apiClient';
import { 
  ExerciseRecord, 
  CreateExerciseRecordDto, 
  UpdateExerciseRecordDto 
} from '@/types';

export const exerciseApi = {
  // 获取运动记录列表
  getRecords: async (userId: string): Promise<ExerciseRecord[]> => {
    const response = await apiClient.get(`/exercise/records?user_id=${userId}`);
    return response.data;
  },

  // 创建运动记录
  createRecord: async (data: CreateExerciseRecordDto): Promise<ExerciseRecord> => {
    const response = await apiClient.post('/exercise/records', data);
    return response.data;
  },

  // 更新运动记录
  updateRecord: async (id: string, data: UpdateExerciseRecordDto): Promise<ExerciseRecord> => {
    const response = await apiClient.put(`/exercise/records/${id}`, data);
    return response.data;
  },

  // 删除运动记录
  deleteRecord: async (id: string): Promise<void> => {
    await apiClient.delete(`/exercise/records/${id}`);
  },
};
```

### 3. 类型定义
#### API响应类型：
```typescript
// types/api.ts
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
  timestamp: string;
}
```

## 🎨 UI组件开发

### 1. 基础组件库
#### 按钮组件示例：
```typescript
// components/ui/Button.tsx
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/utils/cn';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10 py-2 px-4',
        sm: 'h-9 px-3',
        lg: 'h-11 px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, children, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={loading || props.disabled}
        {...props}
      >
        {loading && (
          <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button, buttonVariants };
```

### 2. 表单组件
#### 表单处理示例：
```typescript
// components/forms/ExerciseRecordForm.tsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';

const exerciseRecordSchema = z.object({
  exerciseTypeId: z.string().min(1, '请选择运动类型'),
  startTime: z.string().min(1, '请选择开始时间'),
  durationMinutes: z.number().min(1, '持续时间至少1分钟'),
  caloriesBurned: z.number().optional(),
  notes: z.string().optional(),
});

type ExerciseRecordFormData = z.infer<typeof exerciseRecordSchema>;

interface ExerciseRecordFormProps {
  onSubmit: (data: ExerciseRecordFormData) => Promise<void>;
  exerciseTypes: Array<{ id: string; name: string }>;
}

export const ExerciseRecordForm: React.FC<ExerciseRecordFormProps> = ({
  onSubmit,
  exerciseTypes,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ExerciseRecordFormData>({
    resolver: zodResolver(exerciseRecordSchema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <Select
        label="运动类型"
        options={exerciseTypes.map(type => ({
          value: type.id,
          label: type.name,
        }))}
        error={errors.exerciseTypeId?.message}
        {...register('exerciseTypeId')}
      />

      <Input
        type="datetime-local"
        label="开始时间"
        error={errors.startTime?.message}
        {...register('startTime')}
      />

      <Input
        type="number"
        label="持续时间（分钟）"
        error={errors.durationMinutes?.message}
        {...register('durationMinutes', { valueAsNumber: true })}
      />

      <Input
        type="number"
        label="消耗卡路里"
        optional
        error={errors.caloriesBurned?.message}
        {...register('caloriesBurned', { valueAsNumber: true })}
      />

      <Input
        type="text"
        label="备注"
        optional
        error={errors.notes?.message}
        {...register('notes')}
      />

      <Button type="submit" loading={isSubmitting}>
        保存记录
      </Button>
    </form>
  );
};
```

## 🚀 性能优化

### 1. 代码分割
#### 路由级代码分割：
```typescript
// 使用React.lazy进行懒加载
import React, { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

const Dashboard = lazy(() => import('@/pages/dashboard/Dashboard'));
const ExercisePage = lazy(() => import('@/pages/exercise/ExercisePage'));
const TasksPage = lazy(() => import('@/pages/tasks/TasksPage'));

const AppRoutes = () => {
  return (
    <Router>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/exercise" element={<ExercisePage />} />
          <Route path="/tasks" element={<TasksPage />} />
        </Routes>
      </Suspense>
    </Router>
  );
};
```

### 2. 图片优化
#### 使用WebP格式：
```typescript
// 组件中使用优化的图片
import React from 'react';

const OptimizedImage = ({ src, alt, ...props }) => {
  const webpSrc = src.replace(/\.(jpg|png)$/, '.webp');
  
  return (
    <picture>
      <source srcSet={webpSrc} type="image/webp" />
      <source srcSet={src} type={`image/${src.split('.').pop()}`} />
      <img src={src} alt={alt} {...props} />
    </picture>
  );
};
```

### 3. 缓存策略
#### 服务工作者缓存：
```javascript
// public/sw.js
const CACHE_NAME = 'coachai-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.ico',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => response || fetch(event.request))
  );
});
```

## 🧪 测试指南

### 1. 单元测试
#### 使用Vitest + Testing Library：
```typescript
// __tests__/components/Button.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/ui/Button';

describe('Button', () => {
  it('渲染按钮文本', () => {

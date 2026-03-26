// 通用类型
export interface ApiResponse<T = any> {
  data: T
  message?: string
  success: boolean
  code: number
}

export interface PaginationParams {
  page?: number
  page_size?: number
  search?: string
  ordering?: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// 用户相关类型
export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  is_staff: boolean
  date_joined: string
  last_login: string | null
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

export interface RefreshTokenRequest {
  refresh: string
}

export interface RefreshTokenResponse {
  access: string
}

// 作业相关类型
export interface KnowledgePoint {
  id: number
  name: string
  description: string
  subject: string
  subject_display: string
  difficulty_level: number
  difficulty_display: string
  created_at: string
  updated_at: string
}

export interface Question {
  id: number
  content: string
  question_type: string
  question_type_display: string
  correct_answer: string
  user_answer: string | null
  score: number | null
  max_score: number
  score_percentage: number | null
  knowledge_points: KnowledgePoint[]
  created_at: string
  updated_at: string
}

export interface Homework {
  id: number
  title: string
  description: string | null
  student: number
  student_name: string
  subject: string
  subject_display: string
  status: string
  status_display: string
  total_score: number | null
  max_total_score: number
  score_percentage: number | null
  questions: Question[]
  created_at: string
  updated_at: string
}

export interface HomeworkCreateRequest {
  title: string
  description?: string
  subject: string
  questions: QuestionCreateRequest[]
}

export interface QuestionCreateRequest {
  content: string
  question_type: string
  correct_answer: string
  max_score: number
  knowledge_point_ids?: number[]
}

// 运动相关类型
export interface Exercise {
  id: number
  user: number
  user_name: string
  exercise_type: string
  exercise_type_display: string
  duration: number
  count: number
  calories_burned: number | null
  posture_score: number | null
  notes: string | null
  created_at: string
  updated_at: string
}

// 任务相关类型
export interface Task {
  id: number
  title: string
  description: string | null
  user: number
  user_name: string
  task_type: string
  task_type_display: string
  priority: string
  priority_display: string
  status: string
  status_display: string
  due_date: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

// 成就相关类型
export interface Achievement {
  id: number
  name: string
  description: string
  achievement_type: string
  achievement_type_display: string
  requirement: number
  reward_points: number
  icon_url: string | null
  created_at: string
  updated_at: string
}

export interface UserAchievement {
  id: number
  user: number
  user_name: string
  achievement: Achievement
  progress: number
  is_unlocked: boolean
  unlocked_at: string | null
  created_at: string
  updated_at: string
}
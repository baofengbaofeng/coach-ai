import { apiRequest } from '../api/config'
import { Homework, HomeworkCreateRequest, KnowledgePoint, PaginatedResponse, PaginationParams, Question } from '@/types'

export const homeworkService = {
  // 获取作业列表
  getHomeworks: async (params?: PaginationParams): Promise<PaginatedResponse<Homework>> => {
    return await apiRequest.get<PaginatedResponse<Homework>>('/homework/homeworks/', { params })
  },

  // 获取单个作业
  getHomework: async (id: number): Promise<Homework> => {
    return await apiRequest.get<Homework>(`/homework/homeworks/${id}/`)
  },

  // 创建作业
  createHomework: async (data: HomeworkCreateRequest): Promise<Homework> => {
    return await apiRequest.post<Homework>('/homework/homeworks/', data)
  },

  // 更新作业
  updateHomework: async (id: number, data: Partial<HomeworkCreateRequest>): Promise<Homework> => {
    return await apiRequest.put<Homework>(`/homework/homeworks/${id}/`, data)
  },

  // 删除作业
  deleteHomework: async (id: number): Promise<void> => {
    await apiRequest.delete(`/homework/homeworks/${id}/`)
  },

  // 获取作业统计
  getHomeworkStatistics: async (): Promise<any> => {
    return await apiRequest.get('/homework/api/homeworks/statistics/')
  },

  // 获取知识点列表
  getKnowledgePoints: async (params?: PaginationParams): Promise<PaginatedResponse<KnowledgePoint>> => {
    return await apiRequest.get<PaginatedResponse<KnowledgePoint>>('/homework/knowledge-points/', { params })
  },

  // 获取单个知识点
  getKnowledgePoint: async (id: number): Promise<KnowledgePoint> => {
    return await apiRequest.get<KnowledgePoint>(`/homework/knowledge-points/${id}/`)
  },

  // 创建知识点
  createKnowledgePoint: async (data: Omit<KnowledgePoint, 'id' | 'created_at' | 'updated_at' | 'subject_display' | 'difficulty_display'>): Promise<KnowledgePoint> => {
    return await apiRequest.post<KnowledgePoint>('/homework/knowledge-points/', data)
  },

  // 获取题目列表
  getQuestions: async (params?: PaginationParams): Promise<PaginatedResponse<Question>> => {
    return await apiRequest.get<PaginatedResponse<Question>>('/homework/questions/', { params })
  },

  // 获取单个题目
  getQuestion: async (id: number): Promise<Question> => {
    return await apiRequest.get<Question>(`/homework/questions/${id}/`)
  },

  // 创建题目
  createQuestion: async (data: Omit<Question, 'id' | 'created_at' | 'updated_at' | 'question_type_display' | 'score_percentage' | 'knowledge_points'>): Promise<Question> => {
    return await apiRequest.post<Question>('/homework/questions/', data)
  },

  // 获取题目统计
  getQuestionStatistics: async (): Promise<any> => {
    return await apiRequest.get('/homework/api/questions/statistics/')
  },

  // 上传作业图片（OCR处理）
  uploadHomeworkImage: async (file: File): Promise<any> => {
    const formData = new FormData()
    formData.append('image', file)
    
    return await apiRequest.post('/homework/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // 批改作业
  gradeHomework: async (homeworkId: number, answers: Record<number, string>): Promise<Homework> => {
    return await apiRequest.post<Homework>(`/homework/homeworks/${homeworkId}/grade/`, { answers })
  },
}

export default homeworkService
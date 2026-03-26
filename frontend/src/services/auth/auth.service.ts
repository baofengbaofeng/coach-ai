import { apiRequest } from '../api/config'
import { LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse, User } from '@/types'

export const authService = {
  // 登录
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await apiRequest.post<LoginResponse>('/auth/login/', credentials)
    
    // 保存token和用户信息
    if (response.access && response.refresh) {
      localStorage.setItem('access_token', response.access)
      localStorage.setItem('refresh_token', response.refresh)
      localStorage.setItem('user', JSON.stringify(response.user))
    }
    
    return response
  },

  // 登出
  logout: (): void => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  },

  // 刷新token
  refreshToken: async (refreshToken: string): Promise<RefreshTokenResponse> => {
    const request: RefreshTokenRequest = { refresh: refreshToken }
    return await apiRequest.post<RefreshTokenResponse>('/auth/token/refresh/', request)
  },

  // 获取当前用户
  getCurrentUser: (): User | null => {
    const userStr = localStorage.getItem('user')
    if (!userStr) return null
    
    try {
      return JSON.parse(userStr) as User
    } catch {
      return null
    }
  },

  // 检查是否已登录
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('access_token')
  },

  // 获取access token
  getAccessToken: (): string | null => {
    return localStorage.getItem('access_token')
  },

  // 获取refresh token
  getRefreshToken: (): string | null => {
    return localStorage.getItem('refresh_token')
  },

  // 更新用户信息
  updateUser: (user: User): void => {
    localStorage.setItem('user', JSON.stringify(user))
  },
}

export default authService
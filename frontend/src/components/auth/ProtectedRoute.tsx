import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { authService } from '@/services/auth/auth.service'

interface ProtectedRouteProps {
  children: React.ReactNode
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const location = useLocation()
  const isAuthenticated = authService.isAuthenticated()

  if (!isAuthenticated) {
    // 重定向到登录页，并保存当前路径以便登录后跳转回来
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <>{children}</>
}

export default ProtectedRoute
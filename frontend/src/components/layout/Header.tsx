import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authService } from '@/services/auth/auth.service'

const Header: React.FC = () => {
  const navigate = useNavigate()
  const user = authService.getCurrentUser()

  const handleLogout = () => {
    authService.logout()
    navigate('/login')
  }

  return (
    <header className="bg-white shadow-md">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <Link to="/" className="text-2xl font-bold text-blue-600">
              CoachAI
            </Link>
            
            {user && (
              <nav className="hidden md:flex space-x-6">
                <Link to="/dashboard" className="text-gray-700 hover:text-blue-600 transition-colors">
                  仪表板
                </Link>
                <Link to="/dashboard/homework" className="text-gray-700 hover:text-blue-600 transition-colors">
                  作业管理
                </Link>
                <Link to="/dashboard/exercise" className="text-gray-700 hover:text-blue-600 transition-colors">
                  运动管理
                </Link>
                <Link to="/dashboard/tasks" className="text-gray-700 hover:text-blue-600 transition-colors">
                  任务管理
                </Link>
                <Link to="/dashboard/achievements" className="text-gray-700 hover:text-blue-600 transition-colors">
                  成就系统
                </Link>
              </nav>
            )}
          </div>

          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-semibold">
                      {user.first_name?.[0] || user.username[0]}
                    </span>
                  </div>
                  <span className="text-gray-700 hidden md:inline">
                    {user.first_name || user.username}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-sm bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
                >
                  退出登录
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="px-4 py-2 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
                >
                  登录
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  注册
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  HomeIcon,
  BookOpenIcon,
  FireIcon,
  CheckCircleIcon,
  TrophyIcon,
  CogIcon,
} from '@heroicons/react/24/outline'

const navigation = [
  { name: '仪表板', href: '/dashboard', icon: HomeIcon },
  { name: '作业管理', href: '/dashboard/homework', icon: BookOpenIcon },
  { name: '运动管理', href: '/dashboard/exercise', icon: FireIcon },
  { name: '任务管理', href: '/dashboard/tasks', icon: CheckCircleIcon },
  { name: '成就系统', href: '/dashboard/achievements', icon: TrophyIcon },
  { name: '设置', href: '/dashboard/settings', icon: CogIcon },
]

const Sidebar: React.FC = () => {
  return (
    <div className="w-64 bg-white border-r border-gray-200 min-h-screen">
      <div className="p-6">
        <h2 className="text-lg font-semibold text-gray-900">导航</h2>
      </div>
      
      <nav className="px-4 space-y-1">
        {navigation.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                `flex items-center px-4 py-3 text-sm rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-600 border-l-4 border-blue-600'
                    : 'text-gray-700 hover:bg-gray-50'
                }`
              }
            >
              <Icon className="h-5 w-5 mr-3" />
              {item.name}
            </NavLink>
          )
        })}
      </nav>

      <div className="absolute bottom-0 w-64 p-6 border-t border-gray-200">
        <div className="flex items-center">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
            <span className="text-blue-600 font-semibold">AI</span>
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium text-gray-900">CoachAI助手</p>
            <p className="text-xs text-gray-500">随时为您服务</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
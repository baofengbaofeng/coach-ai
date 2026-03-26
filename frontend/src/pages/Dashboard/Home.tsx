import React from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { authService } from '@/services/auth/auth.service'
import { homeworkService } from '@/services/homework/homework.service'
import {
  AcademicCapIcon,
  FireIcon,
  CheckCircleIcon,
  TrophyIcon,
  ArrowUpIcon,
  ArrowDownIcon,
} from '@heroicons/react/24/outline'

const DashboardHome: React.FC = () => {
  const user = authService.getCurrentUser()

  // 获取作业统计
  const { data: homeworkStats, isLoading: homeworkLoading } = useQuery({
    queryKey: ['homework-stats'],
    queryFn: () => homeworkService.getHomeworkStatistics(),
  })

  // 获取最近作业
  const { data: recentHomeworks, isLoading: homeworksLoading } = useQuery({
    queryKey: ['recent-homeworks'],
    queryFn: () => homeworkService.getHomeworks({ page_size: 5 }),
  })

  const stats = [
    {
      name: '总作业数',
      value: homeworkStats?.total_homeworks || 0,
      change: '+12%',
      changeType: 'increase',
      icon: AcademicCapIcon,
      color: 'bg-blue-500',
      href: '/dashboard/homework',
    },
    {
      name: '平均分数',
      value: homeworkStats?.average_score ? `${homeworkStats.average_score.toFixed(1)}%` : '0%',
      change: '+5.2%',
      changeType: 'increase',
      icon: TrophyIcon,
      color: 'bg-green-500',
      href: '/dashboard/homework',
    },
    {
      name: '完成运动',
      value: '24',
      change: '+8',
      changeType: 'increase',
      icon: FireIcon,
      color: 'bg-red-500',
      href: '/dashboard/exercise',
    },
    {
      name: '完成任务',
      value: '18',
      change: '+3',
      changeType: 'increase',
      icon: CheckCircleIcon,
      color: 'bg-yellow-500',
      href: '/dashboard/tasks',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              欢迎回来，{user?.first_name || user?.username}！
            </h1>
            <p className="mt-1 text-gray-600">
              今天是 {new Date().toLocaleDateString('zh-CN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
          </div>
          <div className="flex space-x-3">
            <button className="px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors">
              开始学习
            </button>
            <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
              查看报告
            </button>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Link
              key={stat.name}
              to={stat.href}
              className="bg-white overflow-hidden rounded-xl shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="p-6">
                <div className="flex items-center">
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                    <div className="flex items-baseline">
                      <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                      <div className={`ml-2 flex items-center text-sm font-semibold ${
                        stat.changeType === 'increase' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {stat.changeType === 'increase' ? (
                          <ArrowUpIcon className="h-4 w-4" />
                        ) : (
                          <ArrowDownIcon className="h-4 w-4" />
                        )}
                        <span>{stat.change}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          )
        })}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Homeworks */}
        <div className="bg-white rounded-xl shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">最近作业</h3>
          </div>
          <div className="p-6">
            {homeworksLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-500">加载中...</p>
              </div>
            ) : recentHomeworks?.results?.length ? (
              <div className="space-y-4">
                {recentHomeworks.results.map((homework) => (
                  <div key={homework.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <h4 className="font-medium text-gray-900">{homework.title}</h4>
                      <p className="text-sm text-gray-500 mt-1">
                        {homework.subject_display} • {new Date(homework.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className={`text-lg font-semibold ${
                        homework.score_percentage && homework.score_percentage >= 80
                          ? 'text-green-600'
                          : homework.score_percentage && homework.score_percentage >= 60
                          ? 'text-yellow-600'
                          : 'text-red-600'
                      }`}>
                        {homework.score_percentage ? `${homework.score_percentage}%` : '未批改'}
                      </div>
                      <div className="text-sm text-gray-500">
                        {homework.status_display}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <AcademicCapIcon className="h-12 w-12 text-gray-400 mx-auto" />
                <p className="mt-2 text-gray-500">暂无作业记录</p>
                <Link
                  to="/dashboard/homework"
                  className="mt-4 inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  上传作业
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-xl shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">快速操作</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 gap-4">
              <Link
                to="/dashboard/homework/upload"
                className="flex flex-col items-center justify-center p-6 bg-blue-50 rounded-xl hover:bg-blue-100 transition-colors"
              >
                <AcademicCapIcon className="h-8 w-8 text-blue-600" />
                <span className="mt-2 font-medium text-gray-900">上传作业</span>
                <span className="text-sm text-gray-500">拍照批改</span>
              </Link>
              
              <Link
                to="/dashboard/exercise/start"
                className="flex flex-col items-center justify-center p-6 bg-red-50 rounded-xl hover:bg-red-100 transition-colors"
              >
                <FireIcon className="h-8 w-8 text-red-600" />
                <span className="mt-2 font-medium text-gray-900">开始运动</span>
                <span className="text-sm text-gray-500">动作识别</span>
              </Link>
              
              <Link
                to="/dashboard/tasks/create"
                className="flex flex-col items-center justify-center p-6 bg-green-50 rounded-xl hover:bg-green-100 transition-colors"
              >
                <CheckCircleIcon className="h-8 w-8 text-green-600" />
                <span className="mt-2 font-medium text-gray-900">创建任务</span>
                <span className="text-sm text-gray-500">TODO列表</span>
              </Link>
              
              <Link
                to="/dashboard/achievements"
                className="flex flex-col items-center justify-center p-6 bg-yellow-50 rounded-xl hover:bg-yellow-100 transition-colors"
              >
                <TrophyIcon className="h-8 w-8 text-yellow-600" />
                <span className="mt-2 font-medium text-gray-900">查看成就</span>
                <span className="text-sm text-gray-500">解锁奖励</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Daily Goals */}
      <div className="bg-white rounded-xl shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">今日目标</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">完成1份作业</span>
                <span className="text-sm font-medium text-gray-700">0/1</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: '0%' }}></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">运动30分钟</span>
                <span className="text-sm font-medium text-gray-700">0/30分钟</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-red-600 h-2 rounded-full" style={{ width: '0%' }}></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">完成3个任务</span>
                <span className="text-sm font-medium text-gray-700">0/3</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: '0%' }}></div>
              </div>
            </div>
          </div>
          
          <div className="mt-6 flex justify-center">
            <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              开始今日学习
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardHome
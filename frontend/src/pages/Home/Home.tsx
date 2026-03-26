import React from 'react'
import { Link } from 'react-router-dom'
import { authService } from '@/services/auth/auth.service'
import {
  AcademicCapIcon,
  FireIcon,
  CheckCircleIcon,
  TrophyIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline'

const Home: React.FC = () => {
  const isAuthenticated = authService.isAuthenticated()

  const features = [
    {
      name: '智能作业批改',
      description: '通过摄像头拍摄作业，自动识别题目和答案，智能批改与知识点分析',
      icon: AcademicCapIcon,
      color: 'bg-blue-100 text-blue-600',
    },
    {
      name: '动作识别计数',
      description: '实时识别跳绳、俯卧撑等运动动作，自动计数和姿势纠正',
      icon: FireIcon,
      color: 'bg-red-100 text-red-600',
    },
    {
      name: '任务管理系统',
      description: '每日TODO列表管理，任务进度跟踪，成就系统和激励机制',
      icon: CheckCircleIcon,
      color: 'bg-green-100 text-green-600',
    },
    {
      name: '成就系统',
      description: '解锁成就，获得奖励，激励学习进步',
      icon: TrophyIcon,
      color: 'bg-yellow-100 text-yellow-600',
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div className="relative z-10 pb-8 sm:pb-16 md:pb-20 lg:max-w-2xl lg:w-full lg:pb-28 xl:pb-32">
            <main className="mt-10 mx-auto max-w-7xl px-4 sm:mt-12 sm:px-6 md:mt-16 lg:mt-20 lg:px-8 xl:mt-28">
              <div className="sm:text-center lg:text-left">
                <h1 className="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
                  <span className="block">智能伴读</span>
                  <span className="block text-blue-600">AI学习教练</span>
                </h1>
                <p className="mt-3 text-base text-gray-500 sm:mt-5 sm:text-lg sm:max-w-xl sm:mx-auto md:mt-5 md:text-xl lg:mx-0">
                  CoachAI是一个集智能作业批改、动作识别计数、语音交互和任务管理于一体的智能伴读AI系统。
                  通过摄像头和麦克风等外设，为学生提供个性化、互动式的学习陪伴体验。
                </p>
                <div className="mt-5 sm:mt-8 sm:flex sm:justify-center lg:justify-start">
                  <div className="rounded-md shadow">
                    {isAuthenticated ? (
                      <Link
                        to="/dashboard"
                        className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10"
                      >
                        进入仪表板
                        <ArrowRightIcon className="ml-2 h-5 w-5" />
                      </Link>
                    ) : (
                      <Link
                        to="/login"
                        className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10"
                      >
                        开始使用
                        <ArrowRightIcon className="ml-2 h-5 w-5" />
                      </Link>
                    )}
                  </div>
                  <div className="mt-3 sm:mt-0 sm:ml-3">
                    <Link
                      to="/features"
                      className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 md:py-4 md:text-lg md:px-10"
                    >
                      了解更多
                    </Link>
                  </div>
                </div>
              </div>
            </main>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:text-center">
            <h2 className="text-base text-blue-600 font-semibold tracking-wide uppercase">
              核心功能
            </h2>
            <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
              全方位的学习陪伴
            </p>
            <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
              从作业辅导到运动指导，从任务管理到成就激励，CoachAI为您提供完整的学习解决方案。
            </p>
          </div>

          <div className="mt-10">
            <div className="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10">
              {features.map((feature) => {
                const Icon = feature.icon
                return (
                  <div key={feature.name} className="relative">
                    <div className="absolute flex items-center justify-center h-12 w-12 rounded-md">
                      <div className={`h-12 w-12 rounded-lg flex items-center justify-center ${feature.color}`}>
                        <Icon className="h-6 w-6" aria-hidden="true" />
                      </div>
                    </div>
                    <div className="ml-16">
                      <h3 className="text-lg leading-6 font-medium text-gray-900">
                        {feature.name}
                      </h3>
                      <p className="mt-2 text-base text-gray-500">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-blue-600">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8 lg:flex lg:items-center lg:justify-between">
          <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
            <span className="block">准备好开始智能学习了吗？</span>
            <span className="block text-blue-200">立即加入CoachAI社区。</span>
          </h2>
          <div className="mt-8 flex lg:mt-0 lg:flex-shrink-0">
            <div className="inline-flex rounded-md shadow">
              <Link
                to={isAuthenticated ? '/dashboard' : '/register'}
                className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white hover:bg-blue-50"
              >
                {isAuthenticated ? '进入仪表板' : '免费注册'}
              </Link>
            </div>
            <div className="ml-3 inline-flex rounded-md shadow">
              <Link
                to="/demo"
                className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-700 hover:bg-blue-800"
              >
                观看演示
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-base text-gray-400">
              &copy; {new Date().getFullYear()} CoachAI. 保留所有权利。
            </p>
            <p className="mt-2 text-sm text-gray-500">
              智能伴读AI系统 - 让学习更高效，让成长更快乐
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Home
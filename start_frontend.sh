#!/bin/bash

# CoachAI 前端启动脚本

echo "🚀 启动 CoachAI 前端项目..."

# 进入前端目录
cd frontend

# 检查依赖是否安装
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
fi

# 启动开发服务器
echo "🌐 启动开发服务器..."
npm run dev
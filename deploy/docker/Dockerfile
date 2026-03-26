# CoachAI Dockerfile
# 多阶段构建：构建阶段 + 运行阶段

# 第一阶段：构建阶段
FROM python:3.9-slim as builder

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --user --no-warn-script-location -r requirements.txt

# 第二阶段：运行阶段
FROM python:3.9-slim as runner

# 设置工作目录
WORKDIR /app

# 创建非root用户
RUN groupadd -r coachai && useradd -r -g coachai coachai

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制已安装的Python包
COPY --from=builder /root/.local /home/coachai/.local

# 复制应用代码
COPY . .

# 设置权限
RUN chown -R coachai:coachai /app
USER coachai

# 设置环境变量
ENV PATH="/home/coachai/.local/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH" \
    APP_ENV="production" \
    APP_PORT="8000" \
    APP_HOST="0.0.0.0"

# 创建必要的目录
RUN mkdir -p logs uploads

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${APP_PORT}/api/health || exit 1

# 暴露端口
EXPOSE ${APP_PORT}

# 启动命令
CMD ["python", "code/main.py"]
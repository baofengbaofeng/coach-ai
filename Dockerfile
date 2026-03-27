# CoachAI Dockerfile
# 基于Python 3.9的轻量级镜像

# 构建阶段
FROM python:3.9-slim as builder

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmariadb-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 运行阶段
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 创建非root用户
RUN groupadd -r coachai && useradd -r -g coachai coachai

# 创建必要的目录
RUN mkdir -p /app/uploads /var/log/coach-ai && \
    chown -R coachai:coachai /app /var/log/coach-ai

# 从构建阶段复制已安装的包
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY . .

# 设置文件权限
RUN chown -R coachai:coachai /app && \
    chmod +x /app/scripts/*.sh

# 切换到非root用户
USER coachai

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8888/api/health || exit 1

# 暴露端口
EXPOSE 8888

# 启动命令
CMD ["python", "src/main.py"]

# 标签
LABEL maintainer="CoachAI Team <team@coach-ai.com>" \
      version="1.0.0" \
      description="CoachAI - AI Coach Platform" \
      org.label-schema.name="CoachAI" \
      org.label-schema.description="AI Coach Platform" \
      org.label-schema.url="https://coach-ai.com" \
      org.label-schema.vcs-url="https://github.com/baofengbaofeng/coach-ai" \
      org.label-schema.version="1.0.0" \
      org.label-schema.schema-version="1.0"
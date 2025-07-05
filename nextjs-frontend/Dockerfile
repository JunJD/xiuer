# Dockerfile for nextjs-frontend

# 阶段 1: 构建器 (Builder)
# 使用包含完整 Node.js 和 pnpm 的镜像来构建应用
FROM node:20-slim AS builder

# 设置工作目录
WORKDIR /app

# 安装 pnpm
RUN npm install -g pnpm

# 复制依赖定义文件
COPY package.json pnpm-lock.yaml ./

# 安装所有依赖 (包括 devDependencies 用于构建)
RUN pnpm install

# 复制所有源代码
COPY . .

# 执行构建
# Next.js 会根据 next.config.mjs 中的 'standalone' 配置
# 自动将必要的依赖和文件输出到 .next/standalone/
RUN pnpm build


# 阶段 2: 运行器 (Runner)
# 使用一个非常轻量的 Node.js 镜像来运行应用
FROM node:20-slim AS runner

# 设置工作目录
WORKDIR /app

# 设置生产环境变量
ENV NODE_ENV=production

# 从构建器阶段复制 'standalone' 输出
# 这是运行应用所需的一切
COPY --from=builder /app/.next/standalone ./

# 从构建器阶段复制 'public' 和 '.next/static' 文件夹
# 'standalone' 模式下需要手动复制这些静态资源
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/static ./.next/static

# 暴露端口
EXPOSE 3000

# 运行应用的命令
# 'standalone' 模式会生成一个 server.js 入口文件
CMD ["node", "server.js"]
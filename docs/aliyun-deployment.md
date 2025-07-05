# 阿里云部署指南

本指南将帮助你在阿里云上部署小红书数据分析平台。

## 📋 阿里云准备工作

### 1. 创建ECS实例

**推荐配置：**
- 实例规格：2核2GB（最低配置）
- 操作系统：Alibaba Cloud Linux 3、Ubuntu 20.04 LTS、CentOS 7+ 或 RHEL 8+
- 网络：专有网络VPC
- 安全组：开放端口 22, 80, 443, 3000, 8000

### 2. 创建容器镜像服务（ACR）

1. 登录阿里云控制台
2. 进入容器镜像服务
3. 创建个人版实例（免费）
4. 创建命名空间：`xiuer`
5. 记录镜像仓库地址，格式类似：`registry.cn-shanghai.aliyuncs.com`

### 3. 配置数据库（可选）

**选项1：使用Docker PostgreSQL（推荐）**
- 无需额外配置，工作流会自动创建

**选项2：使用RDS PostgreSQL**
- 创建RDS PostgreSQL实例
- 配置安全组允许ECS访问
- 记录连接字符串

### 4. 配置Redis（可选）

**选项1：使用Docker Redis（推荐）**
- 无需额外配置，工作流会自动创建

**选项2：使用Redis云数据库**
- 创建Redis实例
- 配置安全组允许ECS访问
- 记录连接字符串

## 🔧 ECS服务器初始化

### 1. 连接到ECS服务器

```bash
# 使用SSH连接到你的ECS实例
ssh root@your-ecs-ip
```

### 2. 安装Docker

```bash
# 方法1：使用自动化脚本（推荐）
curl -fsSL https://raw.githubusercontent.com/JunJD/xiuer/main/scripts/setup-aliyun-server.sh | bash

# 方法2：手动安装
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Alibaba Cloud Linux/CentOS/RHEL
sudo yum install -y yum-utils device-mapper-persistent-data lvm2
sudo yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到docker组
sudo usermod -aG docker $USER
```

### 3. 安装Docker Compose

```bash
# 下载Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### 4. 配置防火墙

```bash
# Ubuntu
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# CentOS
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

### 5. 优化系统（针对2GB内存）

```bash
# 创建swap文件
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久启用swap
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 调整swap使用策略
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
```

## 🔐 GitHub Secrets 配置

在你的GitHub仓库中，进入 `Settings` → `Secrets and variables` → `Actions`，添加以下secrets：

### 必需的Secrets

| Secret名称 | 描述 | 示例值 |
|-----------|------|--------|
| `ALIYUN_REGISTRY_URL` | 阿里云镜像仓库地址 | `registry.cn-shanghai.aliyuncs.com` |
| `ALIYUN_REGISTRY_USERNAME` | 阿里云镜像仓库用户名 | `your-aliyun-username` |
| `ALIYUN_REGISTRY_PASSWORD` | 阿里云镜像仓库密码 | `your-aliyun-password` |
| `ECS_HOST` | ECS服务器IP地址 | `123.456.789.10` |
| `ECS_USERNAME` | ECS登录用户名 | `root` |
| `ECS_SSH_KEY` | ECS SSH私钥 | `-----BEGIN RSA PRIVATE KEY-----...` |
| `DATABASE_URL` | 数据库连接字符串 | `postgresql+asyncpg://user:pass@host:5432/db` |
| `ACCESS_SECRET_KEY` | JWT访问令牌密钥 | `your-secret-key-32-chars` |
| `RESET_PASSWORD_SECRET_KEY` | 重置密码密钥 | `your-reset-secret-key` |
| `VERIFICATION_SECRET_KEY` | 验证密钥 | `your-verification-secret-key` |

### 可选的Secrets

| Secret名称 | 描述 | 默认值 |
|-----------|------|--------|
| `ECS_PORT` | SSH端口 | `22` |
| `API_BASE_URL` | API基础URL | `http://backend:8000` |
| `NEXT_PUBLIC_API_URL` | 前端API URL | `http://your-domain/api` |
| `POSTGRES_USER` | PostgreSQL用户名 | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL密码 | `password` |
| `POSTGRES_DB` | PostgreSQL数据库名 | `xiuer` |
| `REDIS_URL` | Redis连接字符串 | `redis://redis:6379` |
| `GITHUB_TOKEN` | GitHub令牌 | `ghp_xxx` |
| `GITHUB_REPO_OWNER` | GitHub仓库所有者 | `JunJD` |
| `GITHUB_REPO_NAME` | GitHub仓库名 | `xiuer-spider` |

## 🔑 生成SSH密钥

### 1. 在本地生成SSH密钥对

```bash
# 生成SSH密钥对
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# 查看公钥
cat ~/.ssh/id_rsa.pub

# 查看私钥（用于GitHub Secret）
cat ~/.ssh/id_rsa
```

### 2. 将公钥添加到ECS服务器

```bash
# 在ECS服务器上执行
mkdir -p ~/.ssh
echo "your-public-key-content" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### 3. 将私钥添加到GitHub Secrets

将私钥内容（包括`-----BEGIN RSA PRIVATE KEY-----`和`-----END RSA PRIVATE KEY-----`）复制到GitHub Secrets中的`ECS_SSH_KEY`。

## 🚀 部署流程

### 1. 推送代码触发部署

```bash
# 推送到main分支会自动触发部署
git add .
git commit -m "feat: 添加阿里云部署配置"
git push origin main
```

### 2. 手动触发部署

在GitHub仓库页面：
1. 点击 `Actions` 标签
2. 选择 `Deploy Xiuer to Aliyun` 工作流
3. 点击 `Run workflow`
4. 选择分支并点击 `Run workflow`

### 3. 监控部署过程

在GitHub Actions页面可以实时查看部署日志，了解部署进度。

## 🔍 部署后验证

### 1. 检查服务状态

```bash
# 连接到ECS服务器
ssh root@your-ecs-ip

# 检查容器状态
cd /app/xiuer
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 2. 访问应用

- **前端页面**: `http://your-ecs-ip`
- **后端API文档**: `http://your-ecs-ip/docs`
- **后端健康检查**: `http://your-ecs-ip/api/health`

### 3. 测试功能

1. 访问前端页面，确认界面正常显示
2. 测试用户注册和登录功能
3. 测试爬虫任务创建和执行
4. 检查数据库连接和数据存储

## 🛠️ 故障排除

### 常见问题

**1. 内存不足**
```bash
# 检查内存使用
free -h

# 检查swap
swapon --show

# 如果没有swap，创建swap文件
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**2. 端口被占用**
```bash
# 检查端口占用
netstat -tlnp | grep :80
netstat -tlnp | grep :3000
netstat -tlnp | grep :8000

# 停止占用端口的进程
sudo kill -9 <pid>
```

**3. Docker镜像拉取失败**
```bash
# 检查Docker登录状态
docker login registry.cn-shanghai.aliyuncs.com

# 手动拉取镜像
docker pull registry.cn-shanghai.aliyuncs.com/xiuer/backend:latest
```

**4. 数据库连接失败**
```bash
# 检查数据库容器状态
docker-compose -f docker-compose.prod.yml logs db

# 检查数据库连接
docker exec -it xiuer_db_1 psql -U postgres -d xiuer
```

### 日志查看

```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml logs db

# 实时查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

## 📊 监控和维护

### 1. 系统监控

```bash
# 查看系统资源使用
htop

# 查看Docker容器资源使用
docker stats

# 查看磁盘使用
df -h

# 查看内存使用
free -h
```

### 2. 定期维护

```bash
# 清理未使用的Docker镜像
docker image prune -f

# 清理未使用的容器
docker container prune -f

# 清理未使用的卷
docker volume prune -f

# 清理未使用的网络
docker network prune -f
```

### 3. 备份数据

```bash
# 备份PostgreSQL数据
docker exec xiuer_db_1 pg_dump -U postgres xiuer > backup_$(date +%Y%m%d).sql

# 备份Redis数据
docker exec xiuer_redis_1 redis-cli SAVE
docker cp xiuer_redis_1:/data/dump.rdb redis_backup_$(date +%Y%m%d).rdb
```

## 🔒 安全建议

### 1. 更新系统

```bash
# Ubuntu
sudo apt update && sudo apt upgrade -y

# CentOS
sudo yum update -y
```

### 2. 配置SSL证书（可选）

```bash
# 安装Certbot
sudo apt install certbot

# 获取SSL证书
sudo certbot certonly --standalone -d your-domain.com

# 配置自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. 配置防火墙

```bash
# 只允许必要的端口
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

## 📈 性能优化

### 1. 针对2GB内存的优化

```bash
# 调整Docker默认配置
echo '{"default-ulimits":{"nofile":{"Name":"nofile","Hard":65536,"Soft":65536}}}' | sudo tee /etc/docker/daemon.json
sudo systemctl restart docker
```

### 2. 数据库优化

在生产环境中，建议使用外部的RDS数据库服务，而不是Docker容器中的数据库。

### 3. 缓存优化

配置Redis缓存来减少数据库查询压力。

**规则引用：性能优化 - 异步优先，合理缓存，避免N+1查询**

## 🎯 总结

通过以上配置，你的小红书数据分析平台将能够：

1. **自动化部署**：每次推送到main分支自动部署
2. **容器化运行**：所有服务运行在Docker容器中
3. **资源优化**：针对2GB内存进行了优化配置
4. **监控完善**：包含健康检查和日志监控
5. **安全可靠**：包含基本的安全配置

部署完成后，你可以通过浏览器访问你的应用，开始使用小红书数据分析平台！ 
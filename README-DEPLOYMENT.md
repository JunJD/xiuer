# 🚀 阿里云一键部署指南

本指南将帮助你快速在阿里云上部署小红书数据分析平台。

## 📋 快速开始

### 1. 准备阿里云资源

1. **创建ECS实例**
   - 规格：2核2GB（最低配置）
   - 系统：Alibaba Cloud Linux 3（推荐）、Ubuntu 20.04 LTS 或 CentOS 7+
   - 安全组：开放端口 22, 80, 443, 3000, 8000

2. **创建容器镜像服务**
   - 进入阿里云控制台 → 容器镜像服务
   - 创建个人版实例（免费）
   - 创建命名空间：`xiuer`
   - 记录仓库地址：`registry.cn-shanghai.aliyuncs.com`

### 2. 初始化服务器

连接到你的ECS服务器，运行一键初始化脚本：

```bash
# 方法1：先测试兼容性（推荐）
curl -fsSL https://raw.githubusercontent.com/JunJD/xiuer/main/scripts/test-aliyun-compatibility.sh | bash

# 方法2：直接运行完整初始化
curl -fsSL https://raw.githubusercontent.com/JunJD/xiuer/main/scripts/setup-aliyun-server.sh | bash

# 方法3：下载后运行
wget https://raw.githubusercontent.com/JunJD/xiuer/main/scripts/setup-aliyun-server.sh
chmod +x setup-aliyun-server.sh
./setup-aliyun-server.sh
```

脚本会自动完成：
- ✅ 系统兼容性检测（支持Alibaba Cloud Linux 3）
- ✅ 系统更新和基础软件安装
- ✅ Docker 和 Docker Compose 安装（针对阿里云系统优化）
- ✅ 防火墙配置（支持firewalld/iptables）
- ✅ Swap 文件创建（针对2GB内存优化）
- ✅ 系统性能优化
- ✅ 应用目录创建
- ✅ 错误处理和继续执行机制

### 3. 配置GitHub Secrets

在你的GitHub仓库中，进入 `Settings` → `Secrets and variables` → `Actions`，添加以下secrets：

#### 必需配置（9个）

| Secret名称 | 描述 | 示例 |
|-----------|------|------|
| `ALIYUN_REGISTRY_URL` | 阿里云镜像仓库地址 | `registry.cn-shanghai.aliyuncs.com` |
| `ALIYUN_REGISTRY_USERNAME` | 阿里云用户名 | `your-username` |
| `ALIYUN_REGISTRY_PASSWORD` | 阿里云密码 | `your-password` |
| `ECS_HOST` | ECS服务器IP | `123.456.789.10` |
| `ECS_USERNAME` | SSH用户名 | `root` |
| `ECS_SSH_KEY` | SSH私钥 | `-----BEGIN RSA PRIVATE KEY-----...` |
| `DATABASE_URL` | 数据库连接 | `postgresql+asyncpg://postgres:password@db:5432/xiuer` |
| `ACCESS_SECRET_KEY` | JWT密钥 | 生成32位随机字符串 |
| `POSTGRES_PASSWORD` | 数据库密码 | 设置一个强密码 |

#### 生成密钥的方法

```bash
# 生成JWT密钥
python3 -c "import secrets; print(secrets.token_hex(32))"

# 生成SSH密钥对
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
# 公钥添加到服务器：~/.ssh/authorized_keys
# 私钥内容添加到GitHub Secret：ECS_SSH_KEY
```

### 4. 部署应用

推送代码到main分支会自动触发部署：

```bash
git add .
git commit -m "feat: 添加阿里云部署配置"
git push origin main
```

或者手动触发：
1. 进入GitHub仓库 → Actions
2. 选择 `Deploy Xiuer to Aliyun`
3. 点击 `Run workflow`

### 5. 访问应用

部署完成后，访问以下地址：

- 🌐 **前端页面**: `http://your-ecs-ip`
- 📚 **API文档**: `http://your-ecs-ip/docs`
- 🔍 **健康检查**: `http://your-ecs-ip/api/health`

## 🛠️ 常见问题

### Q: 内存不足怎么办？
A: 脚本会自动创建2GB Swap文件。如果仍然不足，考虑升级到4GB内存。

### Q: 部署失败怎么排查？
A: 检查GitHub Actions日志，或SSH到服务器查看：
```bash
cd /app/xiuer
docker-compose -f docker-compose.prod.yml logs -f
```

### Q: 如何更新应用？
A: 推送新代码到main分支会自动重新部署。

### Q: 如何备份数据？
A: 运行以下命令：
```bash
# 备份数据库
docker exec xiuer_db_1 pg_dump -U postgres xiuer > backup.sql

# 备份Redis
docker exec xiuer_redis_1 redis-cli SAVE
docker cp xiuer_redis_1:/data/dump.rdb ./redis_backup.rdb
```

## 📊 监控和维护

### 查看系统状态
```bash
# 系统资源
htop

# Docker容器
docker ps
docker stats

# 应用日志
cd /app/xiuer
docker-compose -f docker-compose.prod.yml logs -f
```

### 清理系统
```bash
# 清理Docker
docker system prune -f

# 清理日志
journalctl --vacuum-time=7d
```

## 🔒 安全建议

1. **定期更新系统**
   ```bash
   apt update && apt upgrade -y
   ```

2. **配置SSL证书**（可选）
   ```bash
   # 安装Certbot
   apt install certbot
   
   # 获取证书
   certbot certonly --standalone -d your-domain.com
   ```

3. **监控系统日志**
   ```bash
   # 查看登录日志
   tail -f /var/log/auth.log
   
   # 查看系统日志
   journalctl -f
   ```

## 📈 性能优化

- ✅ 已针对2GB内存优化
- ✅ 已配置Swap文件
- ✅ 已优化Docker配置
- ✅ 已设置资源限制
- ✅ 已配置日志轮转

## 🎯 总结

通过以上步骤，你的小红书数据分析平台将具备：

1. **自动化部署**：推送代码自动部署
2. **容器化运行**：所有服务运行在Docker中
3. **资源优化**：针对2GB内存优化配置
4. **监控完善**：健康检查和日志监控
5. **安全可靠**：基础安全配置

**规则引用：DevOps - Docker + GitHub Actions，分层架构，性能优化**

---

🎉 **部署完成后，你就可以开始使用小红书数据分析平台了！**

如有问题，请参考详细文档：[docs/aliyun-deployment.md](docs/aliyun-deployment.md) 
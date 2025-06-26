## 🎯 新手必读 - 3 步启动

> 🤔 **完全没有开发经验？** 不用担心！按以下 3 步操作即可：

### 第一步：安装 Docker
- **Windows/Mac**: 访问 [Docker 官网](https://www.docker.com/products/docker-desktop/) 下载 Docker Desktop
- **安装完成后**：桌面会出现 Docker 图标，确保它正在运行（图标不是灰色）

### 第二步：下载项目
```bash
# 在终端/命令行中执行（复制粘贴即可）
git clone <你的项目地址>
cd <项目文件夹名称>
```

### 第三步：启动项目
```bash
# 执行这一条命令即可
docker-compose up -d
```

**🎉 完成！** 几分钟后访问 http://localhost:3000 即可看到你的应用！

---

## 🚀 快速开始指南

### 📋 准备工作
在开始之前，请确保你的电脑已安装：
- **Docker** 和 **Docker Compose** ([安装指南](https://docs.docker.com/get-docker/))
- **Make** (可选，用于便捷命令)

> 💡 **什么是 Docker？** Docker 可以让你无需手动配置复杂的开发环境，一键启动整个应用。

### 1️⃣ 克隆项目
```bash
# 克隆项目到本地
git clone https://github.com/JunJD/xiuer
cd xiuer
```

### 2️⃣ 一键启动应用
```bash
# 启动所有服务（推荐）
docker-compose up -d

# 或者分别启动服务
docker-compose up backend    # 后端服务
docker-compose up frontend   # 前端服务
docker-compose up db         # 数据库服务
```

> ⏰ **首次启动需要等待几分钟**，Docker 会自动下载和构建所需的环境。

**💡 网络问题解决方案：**
如果遇到网络超时（常见于 mailhog 服务），可以：
```bash
# 选项1：只启动核心服务（跳过邮件）
docker-compose up -d db backend frontend

# 选项2：使用无邮件服务的配置
docker-compose -f docker-compose.no-mail.yml up -d
```

### 3️⃣ 访问应用
启动成功后，打开浏览器访问：
- 🌐 **前端页面**: http://localhost:3000
- 🔗 **后端 API**: http://localhost:8000
- 📚 **API 文档**: http://localhost:8000/docs （自动生成的接口文档）
- 📧 **邮件测试**: http://localhost:8025 （查看测试邮件）

### 4️⃣ 常用开发命令
```bash
# 查看运行日志
docker-compose logs -f backend     # 查看后端日志
docker-compose logs -f frontend    # 查看前端日志

# 进入容器内部（高级用户）
make docker-backend-shell          # 进入后端容器
make docker-frontend-shell         # 进入前端容器

## 📋 进入容器后查看日志

### 🐍 后端容器内查看日志

**方法1：查看应用运行日志（推荐）**
```bash
# 进入后端容器
make docker-backend-shell

# 应用日志会直接输出到控制台（stdout）
# 由于日志配置使用 StreamHandler(sys.stdout)，所以容器内不会生成单独的日志文件

# 查看当前运行的日志，可以使用：
ps aux | grep python           # 查看Python进程
ps aux | grep uvicorn          # 查看FastAPI服务进程
```

**方法2：查看系统日志**
```bash
# 进入容器后
tail -f /var/log/syslog        # 系统日志（如果存在）
dmesg                          # 内核日志
journalctl                     # systemd日志（某些容器可能不支持）
```

**方法3：实时监控应用行为**
```bash
# 进入容器后
# 查看正在运行的进程
top
htop  # 如果安装了的话

# 查看网络连接
netstat -tlnp

# 查看文件操作
lsof | grep python
```

### ⚛️ 前端容器内查看日志

**前端开发日志**
```bash
# 进入前端容器
make docker-frontend-shell

# Next.js开发服务器日志通常输出到控制台
# 查看Node.js进程
ps aux | grep node
ps aux | grep next

# 如果有构建日志文件：
find . -name "*.log" -type f   # 查找所有log文件
cat .next/trace               # Next.js跟踪日志（如果存在）
```

### 🔍 在容器外查看实时日志（更常用）

**实际上，更推荐的方式是在容器外查看实时日志：**

```bash
# 查看所有服务的实时日志
docker-compose logs -f

# 查看特定服务的实时日志
docker-compose logs -f backend     # 后端服务日志
docker-compose logs -f frontend    # 前端服务日志
docker-compose logs -f db          # 数据库日志

# 查看最近的日志（不跟踪）
docker-compose logs --tail=100 backend    # 查看后端最近100行日志
docker-compose logs --since=1h frontend   # 查看前端最近1小时日志

# 查看特定时间段的日志
docker-compose logs --since="2024-01-01T00:00:00" --until="2024-01-01T23:59:59" backend
```

### 📊 日志级别和格式说明

**后端日志格式：**
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```
示例：
```
2024-01-15 10:30:45,123 - fastapi_app - INFO - 开始处理搜索结果: 护肤, 共10个笔记
2024-01-15 10:30:45,456 - fastapi_app - ERROR - 处理笔记 abc123 失败: 数据格式错误
```

**日志级别：**
- `DEBUG`: 详细的调试信息
- `INFO`: 一般信息，程序正常运行
- `WARNING`: 警告信息，程序继续运行但可能有问题
- `ERROR`: 错误信息，程序某部分失败
- `CRITICAL`: 严重错误，程序可能无法继续运行

### 🛠️ 日志调试技巧

**1. 过滤特定日志内容：**
```bash
# 只查看错误日志
docker-compose logs backend | grep ERROR

# 查看包含特定关键词的日志
docker-compose logs backend | grep "webhook"
docker-compose logs backend | grep "笔记"

# 查看最近的错误
docker-compose logs --tail=50 backend | grep -E "(ERROR|CRITICAL)"
```

**2. 保存日志到文件：**
```bash
# 保存当前所有日志到文件
docker-compose logs > app_logs.txt

# 保存特定服务日志
docker-compose logs backend > backend_logs.txt

# 实时保存日志
docker-compose logs -f backend | tee backend_realtime.log
```

**3. 监控特定业务操作：**
```bash
# 监控爬虫webhook相关日志
docker-compose logs -f backend | grep -i "webhook\|爬虫\|搜索结果"

# 监控数据库相关操作
docker-compose logs -f backend | grep -i "sql\|database\|migration"

# 监控用户操作
docker-compose logs -f backend | grep -i "用户\|登录\|注册"
```

### ⚡ 性能监控

**在容器内监控资源使用：**
```bash
# 进入容器后
docker stats                    # 查看所有容器资源使用
docker stats xiuer-backend-1    # 查看特定容器资源

# 在容器内部：
free -h                         # 内存使用情况
df -h                          # 磁盘使用情况
iostat                         # IO统计（如果安装了sysstat）
```

### 🚨 常见问题排查

**1. 日志输出为空或找不到日志：**
- 检查容器是否正在运行：`docker-compose ps`
- 检查日志配置：确认 `StreamHandler(sys.stdout)` 配置正确

**2. 日志输出乱码：**
```bash
# 设置正确的编码
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8
```

**3. 日志过多影响性能：**
- 修改日志级别为 `WARNING` 或 `ERROR`
- 使用日志轮转：在生产环境中配置logrotate

### 📝 自定义日志查看

**如果需要更详细的日志，可以临时修改日志级别：**
```bash
# 进入后端容器
make docker-backend-shell

# 在Python环境中临时调整日志级别
python -c "
import logging
logging.getLogger('fastapi_app').setLevel(logging.DEBUG)
print('日志级别已调整为DEBUG')
"
```

**规则引用：分层架构 - Routes → Services → Models，异步优先，类型安全**

### 🔄 其他常用开发命令
```bash
# 运行测试
make docker-test-backend           # 后端测试
make docker-test-frontend          # 前端测试

# 停止所有服务
docker-compose down
```

### 5️⃣ 应用启动流程详解

当你运行 `docker-compose up` 时，会发生以下步骤：

1. **🗄️ 数据库启动**: PostgreSQL 数据库容器启动
2. **🐍 后端初始化**:
   - 使用 `uv` 安装 Python 依赖包
   - 可选的数据库迁移（如果 `AUTO_MIGRATE=true`）
   - 启动 FastAPI 服务器（支持热重载）
   - 启动文件监控器（开发模式）
3. **⚛️ 前端初始化**:
   - 使用 `pnpm` 安装 Node.js 依赖包
   - 从后端 OpenAPI 自动生成类型化 API 客户端
   - 启动 Next.js 开发服务器

## 🗄️ 数据库管理

本模板使用 Alembic 进行数据库架构管理和迁移。以下是如何处理数据库变更：

### 🔧 初始设置
数据库迁移**默认关闭**，避免开发过程中不必要的开销。你可以：

**选项1：手动运行迁移（推荐）**
```bash
# 运行所有待执行的迁移
make docker-migrate-db
```

**选项2：启用自动迁移**
在 `docker-compose.yml` 中设置后端服务的环境变量：
```yaml
environment:
  - AUTO_MIGRATE=true
```

### 📝 添加新表/模型

1. **定义模型** 在 `fastapi_backend/app/models.py` 中：
```python
class UserLog(Base):
    __tablename__ = "user_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    action = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="logs")
```

2. **生成迁移文件**（Alembic 自动检测变更）：
```bash
make docker-db-schema migration_name="add_user_log_table"
```

3. **应用迁移**：
```bash
make docker-migrate-db
```

4. **验证变更**：
```bash
# 检查数据库表
docker exec xiuer-db-1 psql -U postgres -d mydatabase -c "\dt"

# 检查特定表结构
docker exec xiuer-db-1 psql -U postgres -d mydatabase -c "\d user_logs"
```

### 📋 迁移命令参考

| 命令 | 说明 |
|------|------|
| `make docker-migrate-db` | 运行所有待执行的迁移 |
| `make docker-db-schema migration_name="描述"` | 生成新的迁移文件 |
| `docker exec xiuer-backend-1 uv run alembic history` | 查看迁移历史 |
| `docker exec xiuer-backend-1 uv run alembic current` | 检查当前迁移状态 |
| `docker exec xiuer-backend-1 uv run alembic downgrade -1` | 回滚一个迁移 |

### 🚀 生产环境部署注意事项

- **务必备份** 在生产环境运行迁移前备份数据库
- **先测试** 在测试环境中先验证迁移
- 应用程序会在启动时自动运行迁移
- 对于关键生产系统，考虑在维护窗口期手动运行迁移
- 迁移文件存储在 `fastapi_backend/alembic_migrations/versions/`

### 🚨 故障排除

**"relation does not exist" 错误：**
如果看到数据库表不存在的错误，说明还没有运行迁移：
```bash
# 方法1：手动运行迁移（推荐）
make docker-migrate-db

# 方法2：在 docker-compose.yml 中启用自动迁移
# 设置 AUTO_MIGRATE=true 并重启容器
docker-compose down && docker-compose up -d
```

**迁移冲突：**
如果有迁移冲突，检查迁移历史并手动解决：
```bash
docker exec xiuer-backend-1 uv run alembic history
```

**重置数据库（仅开发环境）：**
```bash
# 停止容器
docker-compose down

# 删除数据库卷
docker volume rm xiuer_postgres_data

# 重启并运行迁移
docker-compose up -d
make docker-migrate-db
```

### ❓ 常见问题

**Q: 首次启动很慢怎么办？**
A: 这是正常的，Docker 需要下载镜像和安装依赖。后续启动会很快。

**Q: 端口被占用怎么办？**
A: 检查是否有其他服务占用了 3000、8000、5432 端口，或修改 `docker-compose.yml` 中的端口配置。

**Q: 如何查看详细的错误信息？**
A: 使用 `docker-compose logs -f backend` 或 `docker-compose logs -f frontend` 查看详细日志。

**Q: 如何停止所有服务？**
A: 运行 `docker-compose down` 即可停止所有容器。

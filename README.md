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

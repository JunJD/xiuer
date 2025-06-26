# Changelog

This changelog references changes made both to the FastAPI backend, `fastapi_backend`, and the
frontend TypeScript client, `nextjs-frontend`.

!!! note
    The backend and the frontend are versioned together, that is, they have the same version number.
    When you update the backend, you should also update the frontend to the same version.

## 0.0.4 <small>December 26, 2024</small> {id="0.0.4"}

### 🏗️ 项目结构重组和关注分离

- **重构路由结构**: 统一所有路由到 `app/routes/` 目录，删除冗余的 `app/api/endpoints/` 结构
- **服务层重组**: 将业务逻辑服务 (`users.py`, `email.py`) 迁移到 `app/services/` 目录，实现清晰的分层架构
- **关注分离重构**: 将原本混杂在 webhook 中的功能按职责分离：
  - `webhook.py`: 专注数据接收和处理
  - `notes.py`: 专注笔记查询功能 
  - `tasks.py`: 专注任务管理功能
- **删除冗余代码**: 移除未使用的同步版本服务文件
- **导入路径统一**: 更新所有模块的导入路径，确保结构一致性

### 📁 新增模块

- `app/routes/notes.py`: 笔记查询 API (`/api/notes/`)
- `app/routes/tasks.py`: 任务管理 API (`/api/tasks/`)
- `app/services/__init__.py`: 统一的服务模块导出

### 🔧 改进

- 更清晰的项目结构和模块职责划分
- 提高代码可维护性和可扩展性
- 符合单一职责原则的架构设计

## 0.0.3 <small>April 23, 2025</small> {id="0.0.3"}

- Created docs

## 0.0.2 <small>March 12, 2025</small> {id="0.0.2"}

- Generate release draft using github actions

## 0.0.1 <small>March 12, 2025</small> {id="0.0.1"}

- Initial release

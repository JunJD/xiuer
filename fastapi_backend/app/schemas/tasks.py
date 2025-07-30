"""
Tasks 相关的 Pydantic 模式定义
用于处理爬取任务的数据验证和序列化
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TaskStatusEnum(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SortTypeEnum(int, Enum):
    """排序方式枚举"""
    GENERAL = 0  # 综合
    LATEST = 1   # 最新
    POPULAR = 2  # 最热
    EXTENDED_1 = 3  # 扩展排序类型1
    EXTENDED_2 = 4  # 扩展排序类型2
    
    
# === 基础模式 ===
class TaskBase(BaseModel):
    """任务基础模式"""
    task_name: str = Field(..., description="任务名称", max_length=200)
    keyword: str = Field(..., description="搜索关键词", max_length=200)
    target_count: int = Field(default=200, ge=1, le=1000, description="目标爬取数量")
    sort_type: int = Field(default=1, ge=0, le=4, description="排序方式")
    cookies: Optional[str] = Field(None, description="自定义cookies")


# === 请求模式 ===
class TaskCreate(TaskBase):
    """创建任务请求"""
    webhook_url: Optional[str] = Field(None, description="webhook回调URL")


class TaskUpdate(BaseModel):
    """更新任务请求"""
    task_name: Optional[str] = Field(None, max_length=200)
    status: Optional[TaskStatusEnum] = None
    error_message: Optional[str] = None


# === 响应模式 ===
class TaskResponse(TaskBase):
    """任务响应"""
    id: str = Field(..., description="任务ID")
    status: TaskStatusEnum = Field(..., description="任务状态")
    owner_id: str = Field(..., description="任务创建者ID")
    
    # 执行结果
    total_crawled: int = Field(default=0, description="总爬取数量")
    new_notes: int = Field(default=0, description="新笔记数量")
    changed_notes: int = Field(default=0, description="变更笔记数量")
    important_notes: int = Field(default=0, description="重要笔记数量")
    error_message: Optional[str] = Field(None, description="错误信息")
    
    # 时间字段
    scheduled_time: Optional[datetime] = Field(None, description="计划执行时间")
    started_at: Optional[datetime] = Field(None, description="开始执行时间")
    finished_at: Optional[datetime] = Field(None, description="完成时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """任务列表响应"""
    tasks: List[TaskResponse]
    total: int
    page: int
    size: int
    
    
class TaskStatsResponse(BaseModel):
    """任务统计响应"""
    total_tasks: int
    pending_tasks: int
    running_tasks: int
    completed_tasks: int
    failed_tasks: int
    

# === 操作响应 ===
class TaskActionResponse(BaseModel):
    """任务操作响应"""
    success: bool
    message: str
    task_id: Optional[str] = None
    github_run_url: Optional[str] = None


# === 查询参数 ===
class TaskQueryParams(BaseModel):
    """任务查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=10, ge=1, le=100, description="每页数量")
    status: Optional[TaskStatusEnum] = Field(None, description="任务状态筛选")
    keyword: Optional[str] = Field(None, description="关键词筛选")
    owner_id: Optional[str] = Field(None, description="创建者ID筛选") 
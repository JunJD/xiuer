"""
Webhook 相关的 Pydantic 模式定义
用于处理来自GitHub Actions的webhook数据
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# 导入简化后的模式
from .notes import XhsNoteData, ProcessResult
from .comments import XhsCommentData


class WebhookStatus(str, Enum):
    """Webhook状态枚举"""
    STARTED = "started"
    PROGRESS = "progress"
    SUCCESS = "success"
    ERROR = "error"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(str, Enum):
    """任务类型枚举"""
    SEARCH = "search"
    NOTE = "note"
    USER = "user"


# === 基础Webhook模式 ===
class WebhookBase(BaseModel):
    """Webhook基础模式"""
    status: WebhookStatus
    message: str
    timestamp: datetime
    run_id: str
    task_id: Optional[str] = None  # 添加task_id字段，用于关联爬取任务
    elapsed_time: Optional[float] = None
    progress: Optional[int] = Field(None, ge=0, le=100)


# === Webhook数据载荷 ===
class WebhookDataPayload(BaseModel):
    """Webhook数据载荷 - 简化版"""
    data: Optional[Union[XhsNoteData, List[XhsNoteData], Dict[str, Any]]] = None


class WebhookRequest(WebhookBase, WebhookDataPayload):
    """完整的Webhook请求模式"""
    pass


# === 任务执行请求模式 ===
class CrawlTaskRequest(BaseModel):
    """爬取任务请求"""
    task_name: str = Field(..., description="任务名称")
    keyword: str = Field(..., description="搜索关键词")
    target_count: int = Field(default=50, ge=1, le=500, description="目标爬取数量")
    sort_type: int = Field(default=1, ge=0, le=4, description="排序方式")
    cookies: Optional[str] = Field(None, description="自定义cookies")
    webhook_url: str = Field(..., description="接收结果的webhook URL")


# === 响应模式 ===
class WebhookResponse(BaseModel):
    """Webhook响应"""
    status: str = "received"
    message: str = "数据已接收"
    processed_count: Optional[int] = None
    errors: Optional[List[str]] = None


class TaskTriggerResponse(BaseModel):
    """任务触发响应"""
    success: bool
    message: str
    task_id: Optional[str] = None
    github_run_url: Optional[str] = None 
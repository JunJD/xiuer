"""
Webhook 相关的 Pydantic 模式定义
用于处理来自GitHub Actions的webhook数据
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


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
    elapsed_time: Optional[float] = None
    progress: Optional[int] = Field(None, ge=0, le=100)


# === 笔记相关模式 ===
class XhsAuthorInfo(BaseModel):
    """小红书作者信息"""
    user_id: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class XhsInteractInfo(BaseModel):
    """小红书互动信息"""
    liked_count: int = 0
    collected_count: int = 0
    comment_count: int = 0
    share_count: int = 0


class XhsNoteData(BaseModel):
    """小红书笔记数据"""
    note_id: str
    note_url: Optional[str] = None
    note_type: Optional[str] = None  # "video" 或 "normal"
    
    # 作者信息
    author: Optional[XhsAuthorInfo] = None
    
    # 内容信息
    title: Optional[str] = None
    desc: Optional[str] = None
    tags: Optional[List[str]] = None
    upload_time: Optional[datetime] = None
    ip_location: Optional[str] = None
    
    # 互动数据
    interact_info: Optional[XhsInteractInfo] = None
    
    # 媒体内容
    video_cover: Optional[str] = None
    video_addr: Optional[str] = None
    image_list: Optional[List[str]] = None
    
    # 额外数据
    xsec_token: Optional[str] = None
    
    @validator('note_id')
    def validate_note_id(cls, v):
        if not v or len(v) < 10:
            raise ValueError('note_id 无效')
        return v


class XhsSearchResult(BaseModel):
    """搜索结果数据"""
    query: str
    total_found: int
    notes: List[XhsNoteData]


class XhsUserResult(BaseModel):
    """用户结果数据"""
    user_url: str
    notes_count: int
    notes: List[Dict[str, Any]]  # 简化的笔记信息


# === Webhook数据载荷 ===
class WebhookDataPayload(BaseModel):
    """Webhook数据载荷"""
    data: Optional[Union[XhsSearchResult, XhsNoteData, XhsUserResult, Dict[str, Any]]] = None


class WebhookRequest(WebhookBase, WebhookDataPayload):
    """完整的Webhook请求模式"""
    pass


# === 评论相关模式 ===
class XhsCommentData(BaseModel):
    """小红书评论数据"""
    comment_id: str
    note_id: str
    content: Optional[str] = None
    like_count: int = 0
    upload_time: Optional[datetime] = None
    ip_location: Optional[str] = None
    
    # 评论者信息
    commenter_user_id: Optional[str] = None
    commenter_nickname: Optional[str] = None
    
    # 层级关系
    parent_comment_id: Optional[str] = None
    root_comment_id: Optional[str] = None


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


# === 笔记处理结果 ===
class NoteProcessResult(BaseModel):
    """笔记处理结果"""
    note_id: str
    is_new: bool
    is_changed: bool
    is_important: bool
    change_reason: Optional[str] = None
    important_keywords: Optional[List[str]] = None


class BatchProcessResult(BaseModel):
    """批量处理结果"""
    total_processed: int
    new_notes: int
    changed_notes: int
    important_notes: int
    errors: List[str]
    details: List[NoteProcessResult]


# === 统计和查询模式 ===
class NoteStatsResponse(BaseModel):
    """笔记统计响应"""
    total_notes: int
    new_notes: int
    changed_notes: int
    important_notes: int
    today_crawled: int


class NoteQueryParams(BaseModel):
    """笔记查询参数"""
    keyword: Optional[str] = None
    is_new: Optional[bool] = None
    is_changed: Optional[bool] = None
    is_important: Optional[bool] = None
    author_user_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class XhsNoteResponse(BaseModel):
    """笔记响应模式"""
    id: str
    note_id: str
    note_url: Optional[str]
    note_type: Optional[str]
    title: Optional[str]
    desc: Optional[str]
    author_nickname: Optional[str]
    liked_count: int
    comment_count: int
    current_tags: Optional[List[str]]
    is_new: bool
    is_changed: bool
    is_important: bool
    first_crawl_time: datetime
    last_crawl_time: datetime
    
    class Config:
        from_attributes = True 
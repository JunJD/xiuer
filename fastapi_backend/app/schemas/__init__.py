"""
Schemas 模块初始化文件
统一导出所有模式定义
"""

# 用户相关模式
from .users import UserRead, UserCreate, UserUpdate


# Keywords 相关模式
from .keywords import (
    KeywordBase,
    KeywordCreate, 
    KeywordUpdate,
    KeywordResponse,
    KeywordListResponse
)

# Notes 相关模式
from .notes import (
    XhsNoteData,
    NoteQueryParams,
    XhsNoteResponse,
    NotesListResponse,
    NoteStatsResponse,
    ProcessResult
)

# Comments 相关模式
from .comments import (
    XhsCommentData,
    CommentResponse,
    CommentQueryParams
)

# Webhook 相关模式
from .webhook import (
    WebhookStatus,
    TaskType,
    WebhookBase,
    WebhookRequest,
    WebhookResponse,
    CrawlTaskRequest,
    TaskTriggerResponse
)

# Tasks 相关模式
from .tasks import (
    TaskStatusEnum,
    SortTypeEnum,
    TaskBase,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskStatsResponse,
    TaskActionResponse,
    TaskQueryParams
)

__all__ = [
    # 用户模式
    "UserRead",
    "UserCreate", 
    "UserUpdate",

    # Keywords 模式
    "KeywordBase",
    "KeywordCreate",
    "KeywordUpdate", 
    "KeywordResponse",
    "KeywordListResponse",
    
    # Notes 模式
    "XhsNoteData",
    "NoteQueryParams",
    "XhsNoteResponse",
    "NotesListResponse",
    "NoteStatsResponse",
    "ProcessResult",
    
    # Comments 模式
    "XhsCommentData",
    "CommentResponse",
    "CommentQueryParams",
    
    # Webhook 模式
    "WebhookStatus",
    "TaskType",
    "WebhookBase",
    "WebhookRequest",
    "WebhookResponse",
    "CrawlTaskRequest",
    "TaskTriggerResponse",
    
    # Tasks 模式
    "TaskStatusEnum",
    "SortTypeEnum",
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    "TaskStatsResponse",
    "TaskActionResponse",
    "TaskQueryParams",
] 
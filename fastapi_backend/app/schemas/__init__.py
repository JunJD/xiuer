"""
Schemas 模块初始化文件
统一导出所有模式定义
"""

# 用户相关模式
from .users import UserRead, UserCreate, UserUpdate

# Items 相关模式  
from .items import ItemBase, ItemCreate, ItemRead

# Keywords 相关模式
from .keywords import (
    KeywordBase,
    KeywordCreate, 
    KeywordUpdate,
    KeywordResponse,
    KeywordListResponse
)

# Webhook 相关模式
from .webhook import (
    WebhookStatus,
    TaskType,
    WebhookBase,
    XhsAuthorInfo,
    XhsInteractInfo,
    XhsNoteData,
    XhsSearchResult,
    XhsUserResult,
    XhsCommentData,
    WebhookRequest,
    WebhookResponse,
    CrawlTaskRequest,
    TaskTriggerResponse,
    NoteProcessResult,
    BatchProcessResult,
    NoteStatsResponse,
    NoteQueryParams,
    XhsNoteResponse
)

__all__ = [
    # 用户模式
    "UserRead",
    "UserCreate", 
    "UserUpdate",
    
    # Items 模式
    "ItemBase",
    "ItemCreate",
    "ItemRead",
    
    # Keywords 模式
    "KeywordBase",
    "KeywordCreate",
    "KeywordUpdate", 
    "KeywordResponse",
    "KeywordListResponse",
    
    # Webhook 模式
    "WebhookStatus",
    "TaskType",
    "WebhookBase",
    "XhsAuthorInfo",
    "XhsInteractInfo", 
    "XhsNoteData",
    "XhsSearchResult",
    "XhsUserResult",
    "XhsCommentData",
    "WebhookRequest",
    "WebhookResponse",
    "CrawlTaskRequest",
    "TaskTriggerResponse",
    "NoteProcessResult",
    "BatchProcessResult",
    "NoteStatsResponse",
    "NoteQueryParams",
    "XhsNoteResponse",
] 
"""
Comments 相关的 Pydantic 模式定义
用于处理小红书评论数据的结构化定义
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class XhsCommentData(BaseModel):
    """小红书评论数据 - 爬取原始数据"""
    comment_id: str
    note_id: str
    content: Optional[str] = None
    like_count: int = 0
    upload_time: Optional[datetime] = None
    ip_location: Optional[str] = None
    
    # 评论者信息 - 直接作为字段
    commenter_user_id: Optional[str] = None
    commenter_nickname: Optional[str] = None
    
    # 层级关系
    parent_comment_id: Optional[str] = None
    root_comment_id: Optional[str] = None

    @validator('comment_id')
    def validate_comment_id(cls, v):
        if not v or len(v) < 10:
            raise ValueError('comment_id 无效')
        return v

    @validator('note_id')
    def validate_note_id(cls, v):
        if not v or len(v) < 10:
            raise ValueError('note_id 无效')
        return v


class CommentResponse(BaseModel):
    """评论响应模式"""
    id: str
    comment_id: str
    note_id: str
    content: Optional[str]
    like_count: int
    commenter_nickname: Optional[str]
    upload_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CommentQueryParams(BaseModel):
    """评论查询参数"""
    note_id: Optional[str] = None
    commenter_user_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0) 
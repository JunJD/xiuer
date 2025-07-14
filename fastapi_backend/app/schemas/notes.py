"""
Notes 相关的 Pydantic 模式定义
用于处理小红书笔记数据的结构化定义
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class XhsNoteData(BaseModel):
    """小红书笔记数据 - 爬取原始数据"""
    note_id: str
    note_url: Optional[str] = None
    note_type: Optional[str] = None  # "video" 或 "normal"
    
    # 作者信息 - 直接作为字段
    author_user_id: Optional[str] = None
    author_nickname: Optional[str] = None
    author_avatar: Optional[str] = None
    
    # 内容信息
    title: Optional[str] = None
    desc: Optional[str] = None
    tags: Optional[List[str]] = None
    upload_time: Optional[datetime] = None
    ip_location: Optional[str] = None
    
    # 互动数据 - 直接作为字段
    liked_count: int = 0
    collected_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    
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
    image_list: Optional[List[str]] = None
    author_avatar: Optional[str] = None
    
    class Config:
        from_attributes = True


class NoteStatsResponse(BaseModel):
    """笔记统计响应"""
    total_notes: int
    new_notes: int
    changed_notes: int
    important_notes: int
    today_crawled: int


# 简化的批量处理结果
class ProcessResult(BaseModel):
    """数据处理结果 - 通用"""
    total_processed: int
    new_count: int
    changed_count: int
    important_count: int
    errors: List[str] = [] 
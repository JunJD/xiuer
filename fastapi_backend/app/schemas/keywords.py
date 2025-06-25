"""
关键词相关的 Pydantic 模式
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class KeywordBase(BaseModel):
    keyword: str
    category: Optional[str] = None
    weight: int = 1
    is_active: bool = True
    description: Optional[str] = None


class KeywordCreate(KeywordBase):
    pass


class KeywordUpdate(BaseModel):
    keyword: Optional[str] = None
    category: Optional[str] = None
    weight: Optional[int] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class KeywordResponse(KeywordBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KeywordListResponse(BaseModel):
    keywords: List[KeywordResponse]
    total: int
    categories: List[str] 
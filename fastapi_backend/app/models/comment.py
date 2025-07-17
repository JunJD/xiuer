from __future__ import annotations
from typing import TYPE_CHECKING, List, Any
from sqlalchemy import (
    String, Integer, ForeignKey, DateTime, Text, JSON, Boolean
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime

from .base import Base

if TYPE_CHECKING:
    from .note import XhsNote


class XhsComment(Base):
    __tablename__ = "xhs_comments"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    comment_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    note_id: Mapped[str] = mapped_column(String(100), ForeignKey("xhs_notes.note_id"), nullable=False, index=True)
    commenter_user_id: Mapped[str] = mapped_column(String(100), nullable=True)
    commenter_nickname: Mapped[str] = mapped_column(String(100), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    upload_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    ip_location: Mapped[str] = mapped_column(String(100), nullable=True)
    parent_comment_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    root_comment_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    contains_business_keywords: Mapped[bool] = mapped_column(Boolean, default=False)
    business_keywords_found: Mapped[List[Any]] = mapped_column(JSON, nullable=True)
    importance_score: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    note: Mapped["XhsNote"] = relationship("XhsNote", back_populates="comments") 
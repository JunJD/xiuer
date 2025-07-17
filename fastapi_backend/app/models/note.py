from __future__ import annotations
from typing import TYPE_CHECKING, List, Any
import enum
from sqlalchemy import (
    String, Integer, ForeignKey, DateTime, Text, JSON, Boolean, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime
from .base import Base

if TYPE_CHECKING:
    from .comment import XhsComment


class NoteTag(enum.Enum):
    NEW = "new"
    CHANGED = "changed"
    IMPORTANT = "important"


class XhsNote(Base):
    __tablename__ = "xhs_notes"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    note_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    note_url: Mapped[str] = mapped_column(String(500), nullable=True)
    note_type: Mapped[str] = mapped_column(String(20), nullable=True)
    author_user_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    author_nickname: Mapped[str] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=True)
    desc: Mapped[str] = mapped_column(Text, nullable=True)
    tags: Mapped[List[Any]] = mapped_column(JSON, nullable=True)
    upload_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    ip_location: Mapped[str] = mapped_column(String(100), nullable=True)
    liked_count: Mapped[int] = mapped_column(Integer, default=0)
    collected_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    share_count: Mapped[int] = mapped_column(Integer, default=0)
    video_cover: Mapped[str] = mapped_column(String(500), nullable=True)
    video_addr: Mapped[str] = mapped_column(String(500), nullable=True)
    image_list: Mapped[List[Any]] = mapped_column(JSON, nullable=True)
    author_avatar: Mapped[str] = mapped_column(String(500), nullable=True)
    current_tags: Mapped[List[Any]] = mapped_column(JSON, nullable=True)
    is_new: Mapped[bool] = mapped_column(Boolean, default=True)
    is_changed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_important: Mapped[bool] = mapped_column(Boolean, default=False)
    change_reason: Mapped[str] = mapped_column(String(200), nullable=True)
    important_comment_ids: Mapped[List[Any]] = mapped_column(JSON, nullable=True)
    first_crawl_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_crawl_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    crawl_count: Mapped[int] = mapped_column(Integer, default=1)
    previous_stats: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    comments: Mapped[List["XhsComment"]] = relationship("XhsComment", back_populates="note", cascade="all, delete-orphan")
    tag_logs: Mapped[List["NoteTagLog"]] = relationship("NoteTagLog", back_populates="note", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_note_crawl_time', 'last_crawl_time'),
        Index('idx_note_tags', 'is_new', 'is_changed', 'is_important'),
        Index('idx_author_id', 'author_user_id'),
    )


class NoteTagLog(Base):
    __tablename__ = "note_tag_logs"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    note_id: Mapped[str] = mapped_column(String(100), ForeignKey("xhs_notes.note_id"), nullable=False, index=True)
    old_tags: Mapped[List[Any]] = mapped_column(JSON, nullable=True)
    new_tags: Mapped[List[Any]] = mapped_column(JSON, nullable=True)
    change_type: Mapped[str] = mapped_column(String(50), nullable=False)
    change_reason: Mapped[str] = mapped_column(String(200), nullable=True)
    old_stats: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)
    new_stats: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)
    related_comment_ids: Mapped[List[Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    note: Mapped["XhsNote"] = relationship("XhsNote", back_populates="tag_logs") 
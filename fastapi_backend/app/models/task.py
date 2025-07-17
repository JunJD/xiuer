from __future__ import annotations
from typing import TYPE_CHECKING
import enum
from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum as SQLAlchemyEnum, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime

from .base import Base

if TYPE_CHECKING:
    from .user import User


class TaskStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CrawlTask(Base):
    __tablename__ = "crawl_tasks"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    task_name: Mapped[str] = mapped_column(String(200), nullable=False)
    keyword: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    status: Mapped[TaskStatus] = mapped_column(SQLAlchemyEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    owner_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    target_count: Mapped[int] = mapped_column(Integer, default=200)
    sort_type: Mapped[int] = mapped_column(Integer, default=1)
    cookies: Mapped[str] = mapped_column(Text, nullable=True)
    total_crawled: Mapped[int] = mapped_column(Integer, default=0)
    new_notes: Mapped[int] = mapped_column(Integer, default=0)
    changed_notes: Mapped[int] = mapped_column(Integer, default=0)
    important_notes: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    scheduled_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner: Mapped[User] = relationship("User", back_populates="crawl_tasks") 
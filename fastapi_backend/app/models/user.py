from __future__ import annotations
from typing import TYPE_CHECKING, List
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime

from .base import Base

if TYPE_CHECKING:
    from .task import CrawlTask


class User(SQLAlchemyBaseUserTableUUID, Base):
    logs: Mapped[List["UserLog"]] = relationship("UserLog", back_populates="user", cascade="all, delete-orphan")
    crawl_tasks: Mapped[List["CrawlTask"]] = relationship("CrawlTask", back_populates="owner", cascade="all, delete-orphan")


class UserLog(Base):
    __tablename__ = "user_logs"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="logs") 
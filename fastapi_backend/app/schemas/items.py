"""
Items 相关的 Pydantic 模式
"""

from pydantic import BaseModel
from uuid import UUID


class ItemBase(BaseModel):
    name: str
    description: str | None = None
    quantity: int | None = None


class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: UUID
    user_id: UUID

    model_config = {"from_attributes": True} 
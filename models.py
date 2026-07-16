"""数据模型：基于 SQLModel 定义任务表结构。"""
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=200)
    priority: str = Field(default="medium", index=True)   # high | medium | low
    category: str = Field(default="work", index=True)      # work | study | life
    status: str = Field(default="pending", index=True)    # pending | completed
    note: str = Field(default="", max_length=2000)
    sort_order: int = Field(default=0, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

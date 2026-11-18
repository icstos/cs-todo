"""任务表结构：纯数据定义，不含业务规则、不含 UI。

``Task`` 仍由 SQLModel 直接映射 SQLite；字段、索引、长度限制与迁移前保持一致。
时间字段带时区 —— SQLAlchemy 2 会拒绝 naive 的 ``datetime.utcnow()``。
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel

from cs_todo.models.enums import Category, Priority, TaskStatus

__all__ = ["Task"]


def _utc_now() -> datetime:
    """带 UTC 时区的当前时间（SQLAlchemy 2 的 datetime 列要求 aware 值）。"""
    return datetime.now(timezone.utc)


class Task(SQLModel, table=True):
    """一条任务记录。"""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=200)
    priority: str = Field(default=Priority.MEDIUM.value, index=True)
    category: str = Field(default=Category.WORK.value, index=True)
    status: str = Field(default=TaskStatus.PENDING.value, index=True)
    labels: str = Field(default="", max_length=1000, index=True)
    note: str = Field(default="", max_length=2000)
    sort_order: int = Field(default=0, index=True)
    created_at: datetime = Field(default_factory=_utc_now, index=True)
    updated_at: datetime = Field(default_factory=_utc_now)

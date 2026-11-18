"""日期展示：页头meta 的"今天"文案。"""
from __future__ import annotations

from datetime import datetime

_WEEKDAYS: tuple[str, ...] = ("一", "二", "三", "四", "五", "六", "日")

__all__ = ["format_today"]


def format_today() -> str:
    """返回形如 ``2026/07/17 周四`` 的日期字符串。"""
    now = datetime.now()
    return f"{now.year}/{now.month:02d}/{now.day:02d} 周{_WEEKDAYS[now.weekday()]}"

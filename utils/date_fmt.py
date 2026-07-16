"""日期格式化。"""
from datetime import datetime

_WEEKDAYS = ("一", "二", "三", "四", "五", "六", "日")


def format_today() -> str:
    """返回形如 2026/07/17 周四 的日期字符串。"""
    now = datetime.now()
    return f"{now.year}/{now.month:02d}/{now.day:02d} 周{_WEEKDAYS[now.weekday()]}"

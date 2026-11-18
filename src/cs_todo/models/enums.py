"""领域枚举：任务属性、筛选档位与反馈语气。

统一用 :class:`enum.StrEnum`（Python 3.11+）：既是强类型常量，又保持字符串语义，
写库、做字典键、拼文案时不需要 ``.value`` 来回转换。字符串取值与迁移前逐字一致，
旧库里的 ``"high"`` / ``"pending"`` 无需翻译。
"""
from __future__ import annotations

from enum import StrEnum

__all__ = ["Category", "FilterStatus", "Priority", "TaskStatus", "ToastTone"]


class Priority(StrEnum):
    """艾森豪威尔优先级。"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Category(StrEnum):
    """任务分类。"""

    WORK = "work"
    STUDY = "study"
    LIFE = "life"


class TaskStatus(StrEnum):
    """任务完成态。"""

    PENDING = "pending"
    COMPLETED = "completed"


class FilterStatus(StrEnum):
    """状态筛选档位；``ALL`` 表示不筛选。"""

    ALL = "all"
    PENDING = TaskStatus.PENDING.value
    COMPLETED = TaskStatus.COMPLETED.value


class ToastTone(StrEnum):
    """一次性提示的语气。视图负责把它投影成 ``ui.StyleType``。"""

    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

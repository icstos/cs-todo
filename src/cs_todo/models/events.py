"""领域事件：视图与视图模型之间传递的纯数据信号。

这些对象不含任何控件引用，因此视图模型可以脱离界面单测；视图只负责把原生事件
翻译成 :class:`Shortcut`，把 :class:`Notice` 播报成一条轻提示。
"""
from __future__ import annotations

from dataclasses import dataclass

from cs_todo.models.enums import ToastTone

__all__ = ["Notice", "Shortcut"]


@dataclass(frozen=True, slots=True)
class Notice:
    """一次性用户提示。``seq`` 单调递增，避免重渲染 / 重新挂载时重复播报。"""

    seq: int
    message: str
    tone: ToastTone = ToastTone.INFO


@dataclass(frozen=True, slots=True)
class Shortcut:
    """归一化键盘手势：视图把 ``ui.KeyboardEvent`` 翻译到这里。"""

    key: str
    ctrl: bool = False

"""操作反馈：把视图模型的一次性通知播报成 cs-ui 的轻提示。

``ui.Message`` 顶部居中、几秒自走、同类合并计数；与旧的 SnackBar（弹层栈、底部、
一次一条）语义不同，迁移后维持原选择。
"""
from __future__ import annotations

import ui

_TONES: dict[str, ui.StyleType] = {
    "success": ui.StyleType.SUCCESS,
    "info": ui.StyleType.INFO,
    "warning": ui.StyleType.WARNING,
    "error": ui.StyleType.ERROR,
}

__all__ = ["show_toast"]


def show_toast(page: ui.Page, message: str, *, tone: str = "info") -> None:
    """显示一条一次性回执。

    ``page`` 由视图在渲染期取 ``ui.context.page`` 后传入 —— 事件回调里再取上下文并
    不可靠。
    """
    ui.Message(message, style_type=_TONES.get(tone, ui.StyleType.INFO)).show(page)

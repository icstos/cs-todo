"""操作反馈：统一走 cs-ui 的 Message。

``Message`` 是顶部居中、几秒自走的轻提示，同类会合并计数；旧的 SnackBar 走弹层栈、
钉在底部、一次只能挂一条，和这里的"轻量回执"语义不符。
"""
from __future__ import annotations

import ui
from ui import StyleType

_TONES: dict[str, StyleType] = {
    "success": StyleType.SUCCESS,
    "info": StyleType.INFO,
    "warning": StyleType.WARNING,
    "error": StyleType.ERROR,
}


def show_toast(page: ui.Page, message: str, *, tone: str = "info") -> None:
    """显示一条一次性回执。

    Args:
        page: 当前页面。由调用方在渲染期取 ``ui.context.page`` 后传入 ——
            事件回调里再取上下文并不可靠。
        message: 提示文案。
        tone: success / info / warning / error。
    """
    ui.Message(message, style_type=_TONES.get(tone, StyleType.INFO)).show(page)

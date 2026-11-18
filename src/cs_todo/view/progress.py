"""完成度环：底层用 :class:`ui.ProgressRing`，中央叠加百分比与计数。

环形进度直接由 ui 公开控件组合，不再依赖 cs-ui 的自定义同名组件。
环回答比例，中央文字回答绝对量，两者同屏时不必再去看列表尾部的统计行。

设计约定（沿用既有观感）：

- 默认 80×80、线宽 6；轨道取前景色 15% 透明度，深色主题下不突兀。
- 中央主文案是百分比（600 字重），次文案是 ``done/total``（caption 字号）。
- 环本身带语义标签 / 值与 tooltip，悬停和读屏都能拿到完整信息。
"""
from __future__ import annotations

import ui

__all__ = ["CompletionRing"]

_SIZE: int = 80
_STROKE: int = 6


def _ratio(done: int, total: int) -> float:
    """把计数归一到 0–1；总数为 0 时按 0 处理，不抛异常。"""
    return min(max(done / total, 0.0), 1.0) if total > 0 else 0.0


def CompletionRing(
    done: int,
    *,
    total: int,
    tooltip: str | None = None,
) -> ui.Control:
    """圆环 + 居中两行文字；纯函数，不含状态与业务逻辑。

    Args:
        done: 已完成数。
        total: 总数；为 0 时显示 0% 与 ``0/0``。
        tooltip: 悬浮说明，同时作为读屏标签。

    Returns:
        固定边长的 :class:`ui.Container`，可直接放进 Row / Stack。
    """
    ratio = _ratio(done, total)
    percent = round(ratio * 100)
    accent: str = ui.Colors.PRIMARY

    ring = ui.ProgressRing(
        value=ratio,
        width=_SIZE,
        height=_SIZE,
        stroke_width=_STROKE,
        color=accent,
        bgcolor=ui.overlay(0.15, role=accent),
        semantics_label=tooltip,
        semantics_value=f"{percent}%",
    )
    center = ui.Container(
        width=_SIZE,
        height=_SIZE,
        alignment=ui.Alignment.CENTER,
        content=ui.Column(
            controls=[
                ui.Text(
                    f"{percent}%",
                    size=ui.FONT_SIZE["title"],
                    weight=ui.FONT_WEIGHT["semibold"],
                    color=ui.Colors.ON_SURFACE,
                    text_align=ui.TextAlign.CENTER,
                ),
                ui.Text(
                    f"{done}/{total}",
                    size=ui.FONT_SIZE["caption"],
                    color=ui.Colors.ON_SURFACE_VARIANT,
                    text_align=ui.TextAlign.CENTER,
                ),
            ],
            spacing=0,
            tight=True,
            alignment=ui.MainAxisAlignment.CENTER,
            horizontal_alignment=ui.CrossAxisAlignment.CENTER,
        ),
    )
    return ui.Container(
        width=_SIZE,
        height=_SIZE,
        tooltip=tooltip,
        content=ui.Stack(controls=[ring, center], width=_SIZE, height=_SIZE),
    )

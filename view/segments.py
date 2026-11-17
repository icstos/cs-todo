"""分段选择：把「显示文案 ≠ 逻辑值」的单选交给 :class:`ui.SegmentedButton`。

筛选栏与任务表单都需要在几个短选项里快速切换：用户看「高优先级」，业务拿
``high``。这里用 ui 的分段控件承载这类选择，选中值始终由外部状态传入（``UI = f(state)``），
组件自身只分发事件、不保存选择。

设计约定：

- 单选且不允许空选：点已选段不会把选择清掉，状态永远有一个确定值。
- 关掉选中对勾：分段自带图标时不会被对勾顶掉，纯文字组也不会在切换时左右跳动。
- 整组禁用：专注模式锁定筛选条件，但当前选中的那一段仍然可见。
"""
from __future__ import annotations

from collections.abc import Callable, Sequence

import ui

__all__ = ["ChoiceHandler", "SegmentedChoice"]

type ChoiceHandler = Callable[[str], None]


def _picked(event: ui.ControlEvent) -> list[str]:
    """取选中值：``data`` 优先，拿不到再读控件自己的 ``selected``。

    不同 flet 版本里 ``data`` 可能是列表、也可能为空；只认其中一个，
    升级后就会出现「点了没反应」。
    """
    data = getattr(event, "data", None)
    if isinstance(data, list):
        return [str(item) for item in data]
    selected = getattr(getattr(event, "control", None), "selected", None)
    return [str(item) for item in (selected or [])]


def SegmentedChoice(
    items: Sequence[tuple[str, str, ui.IconData | None]],
    selected: str,
    on_change: ChoiceHandler,
    *,
    disabled: bool = False,
) -> ui.Control:
    """一组互斥选项；点击后只把逻辑值交给回调，不回传事件对象。

    Args:
        items: ``(逻辑值, 显示文案, 图标)`` 三元组，顺序即渲染顺序。
        selected: 当前选中的逻辑值，由调用方状态提供。
        on_change: 选中值变化时收到新的逻辑值。
        disabled: 整组禁用（保留选中态，但不响应点击）。

    Returns:
        一个 :class:`ui.SegmentedButton`，可直接放进 Row / Column。
    """

    def handle(event: ui.ControlEvent) -> None:
        values = _picked(event)
        if values:
            on_change(values[0])

    return ui.SegmentedButton(
        segments=[
            ui.Segment(value=value, label=label, icon=icon)
            for value, label, icon in items
        ],
        selected=[selected],
        allow_empty_selection=False,
        show_selected_icon=False,
        disabled=disabled,
        on_change=handle,
    )

"""搜索栏：纯受控输入，值来自展示状态，变化只回调视图模型。"""
from __future__ import annotations

from collections.abc import Callable

import ui

__all__ = ["SearchBar"]


@ui.component
def SearchBar(
    value: str,
    on_change: Callable[[str], None],
    focus_key: int = 0,
) -> ui.Control:
    """任务搜索输入框。

    ``focus_key`` 变化时用 key 重建输入框，从而获得 autofocus —— 这是给 Ctrl+F
    用的：结构改动发生在组件重渲染里，不违反"已挂载子树不做结构补丁"。
    """
    trimmed = value.strip()

    def handle_change(event: ui.ControlEvent) -> None:
        # 事件自带的 data 就是新值；读 event.control.value 可能拿到尚未回写的旧值。
        raw = getattr(event, "data", None)
        on_change("" if raw is None else str(raw))

    return ui.TextField(
        key=f"search-bar-{focus_key}",
        value=value,
        hint_text="搜索任务标题、备注、标签…",
        prefix_icon=ui.Icons.SEARCH,
        suffix=(
            ui.IconButton(
                icon=ui.Icons.CLOSE,
                icon_size=16,
                icon_color=ui.Colors.ON_SURFACE_VARIANT,
                tooltip="清除搜索",
                on_click=lambda _: on_change(""),
                style=ui.ButtonStyle(padding=ui.Padding.all(4)),
            )
            if trimmed
            else None
        ),
        text_size=ui.FONT_SIZE["small"] + 1,
        height=ui.CONTROL_HEIGHT["md"],
        # 新语法：描边用 OutlineInputBorder + 状态字典；旧的 border_color /
        # focused_border_color / border_radius 在 flet 1.1 已标记废弃。
        border={
            ui.ControlState.DEFAULT: ui.OutlineInputBorder(
                border_radius=ui.RADIUS["md"],
                side=ui.BorderSide(1, ui.Colors.OUTLINE_VARIANT),
            ),
            ui.ControlState.FOCUSED: ui.OutlineInputBorder(
                border_radius=ui.RADIUS["md"],
                side=ui.BorderSide(1, ui.Colors.PRIMARY),
            ),
        },
        content_padding=ui.Padding.symmetric(
            horizontal=ui.SPACE["3"], vertical=ui.SPACE["2"]
        ),
        on_change=handle_change,
        autofocus=focus_key > 0,
    )

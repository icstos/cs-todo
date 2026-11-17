"""任务条目：拖拽手柄、完成勾选、优先级、标题、分类标签与行内操作。

悬停只改状态、不直接改控件属性：组件树是 frozen 的，任何 ``control.update()``
都会抛异常；状态变化触发整行重渲染才是这套范式的正确写法。
"""
from __future__ import annotations

import ui

from theme import (
    CATEGORY_COLOR,
    CATEGORY_ICON,
    CATEGORY_LABEL,
    PRIORITY_COLOR,
    PRIORITY_SHORT,
    SUCCESS_TEXT,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


@ui.component
def TaskItem(task, on_toggle, on_edit, on_delete) -> ui.Control:
    """单个任务行。"""
    hovered, set_hovered = ui.use_state(False)

    is_completed = task.status == "completed"
    priority_color = PRIORITY_COLOR[task.priority]
    category_color = CATEGORY_COLOR[task.category]

    def handle_hover(e) -> None:
        # e.data 是 "true"/"false" 字符串，比较前先归一。
        value = str(getattr(e, "data", "")).lower() == "true"
        if value != hovered:
            set_hovered(value)

    labels = [
        item.strip() for item in getattr(task, "labels", "").split(",") if item.strip()
    ]

    body = ui.Row(
        controls=[
            ui.ReorderableDragHandle(
                content=ui.Icon(ui.Icons.DRAG_INDICATOR, size=ui.ICON_SIZE["lg"], color=TEXT_MUTED),
                mouse_cursor=ui.MouseCursor.GRAB,
            ),
            ui.IconButton(
                icon=ui.Icons.CHECK_CIRCLE if is_completed else ui.Icons.RADIO_BUTTON_UNCHECKED,
                icon_color=SUCCESS_TEXT if is_completed else TEXT_MUTED,
                icon_size=ui.ICON_SIZE["xl"],
                tooltip="标记完成" if not is_completed else "标记未完成",
                on_click=lambda _: on_toggle(task.id),
                style=ui.ButtonStyle(padding=ui.Padding.all(6)),
            ),
            ui.Container(
                width=8,
                height=8,
                border_radius=ui.RADIUS["sm"],
                bgcolor=priority_color,
                tooltip=PRIORITY_SHORT[task.priority],
            ),
            ui.Column(
                controls=[
                    ui.Text(
                        spans=[
                            ui.TextSpan(
                                text=task.title,
                                style=ui.TextStyle(
                                    size=ui.FONT_SIZE["body"],
                                    weight=ui.FontWeight.W_500,
                                    color=TEXT_MUTED if is_completed else TEXT_PRIMARY,
                                    decoration=ui.TextDecoration.LINE_THROUGH
                                    if is_completed
                                    else None,
                                ),
                            ),
                        ],
                        max_lines=1,
                        overflow=ui.TextOverflow.ELLIPSIS,
                    ),
                    *(
                        [
                            ui.Text(
                                value=task.note,
                                size=ui.FONT_SIZE["caption"],
                                color=TEXT_MUTED,
                                max_lines=1,
                                overflow=ui.TextOverflow.ELLIPSIS,
                                italic=True,
                            )
                        ]
                        if task.note
                        else []
                    ),
                ],
                spacing=2,
                alignment=ui.MainAxisAlignment.CENTER,
                expand=True,
            ),
            _badge(PRIORITY_SHORT[task.priority], priority_color),
            _badge(
                CATEGORY_LABEL[task.category],
                category_color,
                icon=CATEGORY_ICON[task.category],
            ),
            *(
                [
                    ui.Row(
                        controls=[
                            _badge(label, TEXT_SECONDARY, pill=True) for label in labels
                        ],
                        wrap=True,
                        spacing=ui.SPACE["2"],
                        run_spacing=ui.SPACE["1"],
                    )
                ]
                if labels
                else []
            ),
            _action(ui.Icons.EDIT_OUTLINED, "编辑", lambda _: on_edit(task.id)),
            _action(ui.Icons.DELETE_OUTLINE, "删除", lambda _: on_delete(task.id)),
        ],
        alignment=ui.MainAxisAlignment.START,
        vertical_alignment=ui.CrossAxisAlignment.CENTER,
        spacing=ui.SPACE["2"] + 2,
    )

    return ui.GestureDetector(
        content=ui.Container(
            content=body,
            padding=ui.Padding.symmetric(vertical=ui.SPACE["2"] + 2, horizontal=ui.SPACE["3"]),
            border_radius=ui.RADIUS["lg"],
            bgcolor=ui.overlay(0.04) if hovered else ui.Colors.SURFACE,
            border=ui.Border.all(1, ui.Colors.OUTLINE_VARIANT),
            animate=ui.Animation(ui.DURATION["fast"], ui.AnimationCurve.EASE_OUT),
            on_hover=handle_hover,
        ),
        mouse_cursor=ui.MouseCursor.CLICK,
        on_double_tap=lambda _: on_edit(task.id),
    )


def _badge(
    text: str,
    color: str,
    *,
    icon: str | None = None,
    pill: bool = False,
) -> ui.Control:
    """行内角标：淡底 + 同色文字，pill 形态用于用户自定义标签。"""
    content: ui.Control
    if icon is not None:
        content = ui.Row(
            controls=[ui.Icon(icon, size=ui.ICON_SIZE["xs"], color=color), ui.Text(text, size=11, color=color, weight=ui.FontWeight.W_500)],
            spacing=4,
            tight=True,
        )
    else:
        content = ui.Text(text, size=11, color=color, weight=ui.FontWeight.W_600)

    return ui.Container(
        content=content,
        padding=ui.Padding.symmetric(vertical=2, horizontal=6),
        border_radius=ui.RADIUS["full"] if pill else ui.RADIUS["sm"],
        bgcolor=ui.Colors.with_opacity(0.08, color),
    )


def _action(icon: str, tooltip: str, on_click) -> ui.Control:
    """行末图标按钮：统一尺寸与留白，避免编辑/删除两枚大小不一。"""
    return ui.IconButton(
        icon=icon,
        icon_color=TEXT_SECONDARY,
        icon_size=ui.ICON_SIZE["md"],
        tooltip=tooltip,
        on_click=on_click,
        style=ui.ButtonStyle(padding=ui.Padding.all(6)),
    )

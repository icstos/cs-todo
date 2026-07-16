"""任务条目：复选框、优先级、标题、备注、分类、操作。"""
import flet as ft

from theme import (
    BG_CARD,
    BG_HOVER,
    BORDER_SUBTLE,
    CATEGORY_COLOR,
    CATEGORY_ICON,
    CATEGORY_LABEL,
    PRIORITY_COLOR,
    PRIORITY_SHORT,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


@ft.component
def TaskItem(task, on_toggle, on_edit, on_delete):
    """单个任务行。"""
    hovered, set_hovered = ft.use_state(False)

    is_completed = task.status == "completed"
    priority_color = PRIORITY_COLOR[task.priority]
    category_color = CATEGORY_COLOR[task.category]
    bg = BG_HOVER if hovered else BG_CARD

    body = ft.Row(
        controls=[
            ft.ReorderableDragHandle(
                content=ft.Icon(ft.Icons.DRAG_INDICATOR, size=18, color=TEXT_MUTED),
                mouse_cursor=ft.MouseCursor.GRAB,
            ),
            ft.IconButton(
                icon=ft.Icons.CHECK_CIRCLE if is_completed else ft.Icons.RADIO_BUTTON_UNCHECKED,
                icon_color="#10B981" if is_completed else TEXT_MUTED,
                icon_size=20,
                tooltip="标记完成" if not is_completed else "标记未完成",
                on_click=lambda _: on_toggle(task.id),
                style=ft.ButtonStyle(padding=ft.Padding.all(6)),
            ),
            ft.Container(
                width=8,
                height=8,
                border_radius=4,
                bgcolor=priority_color,
                tooltip=PRIORITY_SHORT[task.priority],
            ),
            ft.Column(
                controls=[
                    ft.Text(
                        spans=[
                            ft.TextSpan(
                                text=task.title,
                                style=ft.TextStyle(
                                    size=14,
                                    weight=ft.FontWeight.W_500,
                                    color=TEXT_MUTED if is_completed else TEXT_PRIMARY,
                                    decoration=ft.TextDecoration.LINE_THROUGH if is_completed else None,
                                ),
                            ),
                        ],
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    *(
                        [
                            ft.Text(
                                value=task.note,
                                size=11,
                                color=TEXT_MUTED,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                italic=True,
                            )
                        ]
                        if task.note
                        else []
                    ),
                ],
                spacing=2,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            ),
            ft.Container(
                content=ft.Text(
                    PRIORITY_SHORT[task.priority],
                    size=10,
                    color=priority_color,
                    weight=ft.FontWeight.W_600,
                ),
                padding=ft.Padding.symmetric(vertical=2, horizontal=6),
                border_radius=4,
                bgcolor=ft.Colors.with_opacity(0.08, priority_color),
            ),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(CATEGORY_ICON[task.category], size=11, color=category_color),
                        ft.Text(
                            CATEGORY_LABEL[task.category],
                            size=11,
                            color=category_color,
                            weight=ft.FontWeight.W_500,
                        ),
                    ],
                    spacing=4,
                    tight=True,
                ),
                padding=ft.Padding.symmetric(vertical=3, horizontal=7),
                border_radius=4,
                bgcolor=ft.Colors.with_opacity(0.08, category_color),
            ),
            ft.IconButton(
                icon=ft.Icons.EDIT_OUTLINED,
                icon_color=TEXT_SECONDARY,
                icon_size=16,
                tooltip="编辑",
                on_click=lambda _: on_edit(task.id),
                style=ft.ButtonStyle(padding=ft.Padding.all(6)),
            ),
            ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_color=TEXT_SECONDARY,
                icon_size=16,
                tooltip="删除",
                on_click=lambda _: on_delete(task.id),
                style=ft.ButtonStyle(padding=ft.Padding.all(6)),
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    return ft.GestureDetector(
        content=ft.Container(
            content=body,
            padding=ft.Padding.symmetric(vertical=10, horizontal=12),
            border_radius=8,
            bgcolor=bg,
            border=ft.Border.all(1, BORDER_SUBTLE),
            animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT),
            on_hover=lambda e: set_hovered(e.data == "true"),
        ),
        mouse_cursor=ft.MouseCursor.CLICK,
        on_double_tap=lambda _: on_edit(task.id),
    )

"""筛选栏：分类标签、状态筛选、专注模式切换。"""
import flet as ft

from components.chip import SelectChip
from theme import (
    ACCENT,
    CATEGORY_COLOR,
    CATEGORY_ICON,
    CATEGORY_LABEL,
    PRIORITY_COLOR,
    STATUS_LABEL,
    TEXT_SECONDARY,
)


@ft.component
def FilterBar(
    category: str,
    status: str,
    focus_mode: bool,
    on_category,
    on_status,
    on_focus,
    on_add,
):
    """筛选栏组件。"""
    categories = [
        ("all", "全部", None, "#71717A"),
        ("work", CATEGORY_LABEL["work"], CATEGORY_ICON["work"], CATEGORY_COLOR["work"]),
        ("study", CATEGORY_LABEL["study"], CATEGORY_ICON["study"], CATEGORY_COLOR["study"]),
        ("life", CATEGORY_LABEL["life"], CATEGORY_ICON["life"], CATEGORY_COLOR["life"]),
    ]
    statuses = ["all", "pending", "completed"]

    return ft.Row(
        controls=[
            ft.Row(
                controls=[
                    SelectChip(
                        label=label,
                        active=(category == value),
                        disabled=focus_mode,
                        on_click=lambda e, v=value: on_category(v),
                        color=color,
                        icon=icon,
                    )
                    for value, label, icon, color in categories
                ],
                spacing=6,
                tight=True,
            ),
            ft.VerticalDivider(width=1, opacity=0.6),
            ft.Row(
                controls=[
                    SelectChip(
                        label=STATUS_LABEL[s],
                        active=(status == s),
                        disabled=focus_mode,
                        on_click=lambda e, v=s: on_status(v),
                        color=ACCENT,
                    )
                    for s in statuses
                ],
                spacing=6,
                tight=True,
            ),
            ft.Container(expand=True),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.CENTER_FOCUS_STRONG,
                            size=14,
                            color=ft.Colors.WHITE if focus_mode else PRIORITY_COLOR["high"],
                        ),
                        ft.Text(
                            "专注模式",
                            size=12,
                            weight=ft.FontWeight.W_600 if focus_mode else ft.FontWeight.W_500,
                            color=ft.Colors.WHITE if focus_mode else PRIORITY_COLOR["high"],
                        ),
                    ],
                    spacing=6,
                    tight=True,
                ),
                padding=ft.Padding.symmetric(vertical=7, horizontal=12),
                border_radius=6,
                bgcolor=PRIORITY_COLOR["high"] if focus_mode else ft.Colors.TRANSPARENT,
                border=ft.Border.all(
                    1,
                    PRIORITY_COLOR["high"] if not focus_mode else ft.Colors.TRANSPARENT,
                ),
                tooltip="仅显示高优先级未完成任务",
                on_click=lambda _: on_focus(),
                ink=True,
            ),
            ft.Button(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ADD, size=16),
                        ft.Text("新建任务", size=12),
                    ],
                    spacing=6,
                    tight=True,
                ),
                tooltip="Ctrl+N",
                style=ft.ButtonStyle(
                    bgcolor=ACCENT,
                    color=ft.Colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=6),
                    padding=ft.Padding.symmetric(vertical=4, horizontal=14),
                ),
                on_click=on_add,
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
    )

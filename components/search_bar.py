"""搜索栏：按关键词筛选任务列表。"""
import flet as ft

from theme import ACCENT, BORDER_SUBTLE, TEXT_MUTED


@ft.component
def SearchBar(value: str, on_change, focus_key: int = 0):
    """任务搜索输入框。"""
    trimmed = value.strip()

    def handle_clear(_=None):
        on_change("")

    return ft.TextField(
        key=f"search-bar-{focus_key}",
        value=value,
        hint_text="搜索任务标题、备注…",
        prefix_icon=ft.Icons.SEARCH,
        suffix=ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_size=16,
            icon_color=TEXT_MUTED,
            tooltip="清除搜索",
            on_click=handle_clear,
            style=ft.ButtonStyle(padding=ft.Padding.all(4)),
        )
        if trimmed
        else None,
        text_size=13,
        height=36,
        border_radius=6,
        border_color=BORDER_SUBTLE,
        focused_border_color=ACCENT,
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
        on_change=lambda e: on_change(e.control.value),
        autofocus=focus_key > 0,
    )

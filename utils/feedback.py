"""操作反馈：轻量 Toast。"""
import flet as ft
from flet.controls.context import context


def show_toast(message: str, *, icon: str | None = None) -> None:
    """在页面底部显示短暂提示。"""
    content = (
        ft.Row(
            controls=[
                ft.Icon(icon, size=16, color=ft.Colors.WHITE),
                ft.Text(message, size=13, color=ft.Colors.WHITE),
            ],
            spacing=8,
            tight=True,
        )
        if icon
        else ft.Text(message, size=13, color=ft.Colors.WHITE)
    )
    context.page.show_dialog(
        ft.SnackBar(
            content=content,
            bgcolor="#27272A",
            duration=2200,
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.Margin.only(bottom=20, left=24, right=24),
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    )

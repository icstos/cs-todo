"""可复用选择 Chip：筛选栏与表单共用。"""
import flet as ft

from theme import ACCENT, BORDER_SUBTLE, TEXT_SECONDARY


def SelectChip(
    label: str,
    *,
    active: bool,
    on_click,
    color: str = ACCENT,
    icon: str | None = None,
    disabled: bool = False,
    width: int | None = None,
) -> ft.Control:
    """单选 chip：选中填充，未选中描边；支持禁用态。"""
    if disabled:
        fg = TEXT_SECONDARY
        bg = ft.Colors.TRANSPARENT
        border_color = BORDER_SUBTLE
    elif active:
        fg = ft.Colors.WHITE
        bg = color
        border_color = color
    else:
        fg = color if icon else TEXT_SECONDARY
        bg = ft.Colors.TRANSPARENT
        border_color = BORDER_SUBTLE

    inner = (
        ft.Row(
            controls=[
                ft.Icon(icon, size=14, color=fg),
                ft.Text(
                    label,
                    size=12,
                    weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_400,
                    color=fg,
                ),
            ],
            spacing=6,
            tight=True,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        if icon
        else ft.Text(
            label,
            size=12,
            weight=ft.FontWeight.W_500 if active else ft.FontWeight.W_400,
            color=fg,
        )
    )

    return ft.Container(
        content=inner,
        padding=ft.Padding.symmetric(vertical=7, horizontal=12),
        border_radius=6,
        bgcolor=bg,
        border=ft.Border.all(1, border_color),
        on_click=None if disabled else on_click,
        ink=not disabled,
        opacity=0.45 if disabled else 1.0,
        width=width,
        alignment=ft.Alignment.CENTER,
    )

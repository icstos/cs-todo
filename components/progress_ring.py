"""环形进度条：实时反馈完成率。"""
import flet as ft

from theme import ACCENT, BORDER_SUBTLE, TEXT_MUTED, TEXT_PRIMARY


@ft.component
def ProgressRingView(completed: int, total: int):
    """显示完成数量与百分比。"""
    ratio = completed / total if total else 0.0
    percent = int(round(ratio * 100))

    return ft.Container(
        width=80,
        height=80,
        tooltip=f"已完成 {completed} / {total} 项",
        content=ft.Stack(
            controls=[
                ft.ProgressRing(
                    value=ratio,
                    width=80,
                    height=80,
                    stroke_width=6,
                    color=ACCENT,
                    bgcolor=BORDER_SUBTLE,
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                f"{percent}%",
                                size=17,
                                weight=ft.FontWeight.W_600,
                                color=TEXT_PRIMARY,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                f"{completed}/{total}",
                                size=10,
                                color=TEXT_MUTED,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    alignment=ft.Alignment.CENTER,
                    width=80,
                    height=80,
                ),
            ],
            width=80,
            height=80,
        ),
    )

"""应用入口：窗口配置、主题、挂载根组件。"""
import flet as ft

from components.app import App
from database import init_db
from theme import ACCENT, BG_APP, BORDER_SUBTLE


async def main(page: ft.Page):
    init_db()

    page.title = "cs-todo · 高效任务管理"
    page.bgcolor = BG_APP
    page.padding = 0

    # 窗口配置（仅桌面端生效，web 端忽略）
    try:
        page.window.width = 1024
        page.window.height = 720
        page.window.min_width = 820
        page.window.min_height = 560
        await page.window.center()
    except Exception:
        pass

    # 主题：克制、理性、严谨
    page.theme = ft.Theme(
        color_scheme_seed=ACCENT,
        color_scheme=ft.ColorScheme(
            primary=ACCENT,
            on_primary=ft.Colors.WHITE,
            surface="#FFFFFF",
            on_surface="#18181B",
            on_surface_variant="#71717A",
            outline=BORDER_SUBTLE,
            outline_variant="#F4F4F5",
        ),
        font_family="Segoe UI",
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
    page.theme_mode = ft.ThemeMode.LIGHT

    page.render(App)


if __name__ == "__main__":
    ft.run(main)

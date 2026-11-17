"""应用入口：窗口与主题配置，然后挂载根组件。

页面级配置只在这里做，组件不碰 ``page`` 的样式属性。主题遵循 cs-ui 的唯一出口：
品牌色经色板引擎展开成 46 个 M3 角色，明暗两棵树一次下发 —— 应用侧不再出现
``color_scheme_seed``（tonalSpot 会把品牌蓝抽掉一半彩度）。
"""
from __future__ import annotations

import ui

from components.app import App
from database import init_db
from theme import BRAND_PRIMARY


def configure_page(page: ui.Page) -> None:
    """一次性配好标题、主题与窗口。"""
    page.title = "cs-todo · 高效任务管理"
    page.padding = 0

    theme = ui.theme_state()
    theme.set_mode("light")          # 本产品的设计稿按浅色定义
    theme.set_primary(BRAND_PRIMARY)
    ui.apply_theme(page, theme)      # 同时写 theme / dark_theme / bgcolor

    try:
        window = page.window
        window.width = 1024
        window.height = 720
        window.min_width = 820
        window.min_height = 560
    except Exception:
        pass  # web 端没有 window


async def main(page: ui.Page) -> None:
    init_db()
    configure_page(page)
    page.render(App)
    try:
        await page.window.center()
    except Exception:
        pass


if __name__ == "__main__":
    ui.run(main, name="cs-todo")

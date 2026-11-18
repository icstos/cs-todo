"""应用启动入口：组合根 + 页面配置的唯一出口。

依赖在这里显式装配、单向注入：

    SqliteTaskRepository → TaskServiceImpl → TodoViewModelImpl → App

业务代码只认识端口（``cs_todo.infra.ports`` / ``cs_todo.service.ports`` /
``cs_todo.viewmodel.ports``），换数据库、换业务实现或换界面都只改这一处。
页面级配置（标题、主题、窗口）集中在这里，组件不碰 ``page`` 的样式属性。
主题遵循 cs-ui 的唯一出口：品牌色经色板引擎展开成 M3 角色，明暗两棵树一次下发。
"""
from __future__ import annotations

from functools import partial

import ui

from cs_todo.infra.sqlite import SqliteTaskRepository
from cs_todo.service.task_service import TaskServiceImpl
from cs_todo.view.app import App
from cs_todo.view.design import (
    BRAND_PRIMARY,
    WINDOW_HEIGHT,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_WIDTH,
)
from cs_todo.viewmodel.todo_vm import TodoViewModelImpl

__all__ = ["build_view_model", "configure_page", "main", "run"]


def build_view_model() -> TodoViewModelImpl:
    """装配一会话份的视图模型：具体实现在此收口，状态在首帧前装载完毕。"""
    repository = SqliteTaskRepository()
    service = TaskServiceImpl(repository)
    service.initialize()
    view_model = TodoViewModelImpl(service)
    view_model.bootstrap()
    return view_model


def configure_page(page: ui.Page) -> None:
    """一次性配好标题、主题与窗口。"""
    page.title = "cs-todo · 高效任务管理"
    page.padding = 0

    theme = ui.theme_state()
    theme.set_mode("light")  # 本产品的设计稿按浅色定义
    theme.set_primary(BRAND_PRIMARY)
    ui.apply_theme(page, theme)  # 同时写 theme / dark_theme / bgcolor

    try:
        window = page.window
        window.width = WINDOW_WIDTH
        window.height = WINDOW_HEIGHT
        window.min_width = WINDOW_MIN_WIDTH
        window.min_height = WINDOW_MIN_HEIGHT
    except Exception:
        pass  # web 端没有 window


async def main(page: ui.Page) -> None:
    """每个窗口一份视图模型；界面状态不跨会话共享。"""
    view_model = build_view_model()
    configure_page(page)
    page.render(partial(App, vm=view_model))
    try:
        await page.window.center()
    except Exception:
        pass


def run() -> None:
    """启动桌面应用；根目录 ``main.py`` 与 console script 都调用它。"""
    ui.run(main, name="cs-todo")

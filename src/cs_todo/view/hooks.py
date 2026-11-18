"""视图钩子：把视图模型的信号接到 cs-ui 的渲染周期。

这里是"纯 Python 视图模型"与"UI 框架"之间唯一的一层胶水：

* :func:`use_vm` —— 订阅视图模型的单次变更信号，写进 ``use_state`` 触发重渲染；
* :func:`use_notices` —— 播报一次性提示（由视图模型判定是否已播过）；
* :func:`use_shortcuts` —— 把键盘事件归一化后交给视图模型，卸载时解绑。

三个钩子都在组件顶层无条件调用，保证 hook 数量与顺序稳定。
"""
from __future__ import annotations

from collections.abc import Callable

import ui

from cs_todo.models.events import Shortcut
from cs_todo.view.feedback import show_toast
from cs_todo.viewmodel.ports import TodoViewModel

__all__ = ["use_notices", "use_shortcuts", "use_vm"]


def use_vm(vm: TodoViewModel, set_revision: Callable[[int], None]) -> None:
    """把视图模型的状态变更映射成组件重渲染。"""
    def setup() -> Callable[[], None]:
        def listener() -> None:
            set_revision(vm.revision)

        vm.bind(listener)
        listener()  # 兜住挂载前发生的状态变化

        def cleanup() -> None:
            vm.bind(None)

        return cleanup

    ui.use_effect(setup, [])


def use_notices(page: ui.Page, vm: TodoViewModel) -> None:
    """播报尚未播报的一次性提示。"""
    notice = vm.notice

    def setup() -> None:
        claimed = vm.claim_notice()
        if claimed is not None:
            show_toast(page, claimed.message, tone=claimed.tone.value)

    ui.use_effect(setup, [notice])


def use_shortcuts(page: ui.Page, vm: TodoViewModel) -> None:
    """绑定页面级快捷键，视图只做事件翻译。"""

    def setup() -> Callable[[], None]:
        def handler(event: ui.KeyboardEvent) -> None:
            vm.on_shortcut(Shortcut(key=event.key, ctrl=bool(event.ctrl)))

        page.on_keyboard_event = handler

        def cleanup() -> None:
            page.on_keyboard_event = None

        return cleanup

    ui.use_effect(setup, [])

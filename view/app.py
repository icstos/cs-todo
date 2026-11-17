"""应用外壳：把展示状态翻译成布局，把事件分发给视图模型。

本模块不保存业务状态、不做业务判断：``state = vm.view`` 是唯一输入，所有点击 /
输入 / 快捷键都只调用视图模型的方法。对话框用 ``use_dialog`` 按状态挂载；空态区分
"被筛掉"与"真的没有"，只有后者给新建入口。
"""
from __future__ import annotations

from collections.abc import Callable

import ui

from models.enums import Category, Priority
from models.state import TaskDraft, ViewState
from view.design import PRIORITY_COLOR, TEXT_PRIMARY, TEXT_SECONDARY
from view.filter_bar import FilterBar
from view.formatting import format_today
from view.hooks import use_notices, use_shortcuts, use_vm
from view.search_bar import SearchBar
from view.task_form import FormRegistry, TaskForm
from view.task_item import TaskItem
from viewmodel.ports import TodoViewModel

__all__ = ["App"]


def _empty_state(state: ViewState, on_add: Callable[[], None]) -> ui.Control:
    """空态：区分"被筛掉"与"真的没有"，只有后者给新建入口。"""
    query = state.search_query.strip()
    if query:
        text = "未找到匹配任务"
        hint = f"没有包含「{query}」的任务，试试其他关键词"
        icon = ui.Icons.SEARCH_OFF
        icon_color = None
        action = None
    elif state.focus_mode:
        text = "暂无高优先级任务"
        hint = "保持专注，继续推进！"
        icon = ui.Icons.CENTER_FOCUS_STRONG
        icon_color = PRIORITY_COLOR[Priority.HIGH.value]
        action = None
    else:
        text = "暂无任务"
        hint = "新建第一条任务，或按 Ctrl+N 快速记录"
        icon = ui.Icons.INBOX_OUTLINED
        icon_color = None
        action = ui.Button(
            "新建任务",
            icon=ui.Icons.ADD,
            style_type=ui.StyleType.PRIMARY,
            on_click=lambda _: on_add(),
        )

    return ui.Container(
        expand=True,
        alignment=ui.Alignment.CENTER,
        content=ui.empty_block(
            text,
            hint=hint,
            icon=icon,
            icon_color=icon_color,
            action=action,
            height=None,
        ),
    )


@ui.component
def App(*, vm: TodoViewModel) -> ui.Control:
    """根组件：``UI = f(vm.view)``。"""
    page = ui.context.page
    _revision, set_revision = ui.use_state(vm.revision)
    use_vm(vm, set_revision)
    use_notices(page, vm)
    use_shortcuts(page, vm)

    state = vm.view
    form_registry: FormRegistry = ui.use_ref(lambda: {}).current

    def save_from_form() -> None:
        """保存按钮在对话框操作区，值从表单登记的数据对象读取。"""
        def read_text(key: str) -> str:
            field = form_registry.get(key)
            return str(getattr(field, "value", "") or "").strip()

        vm.save_form(
            TaskDraft(
                title=read_text("title"),
                priority=str(form_registry.get("priority", Priority.MEDIUM.value)),
                category=str(form_registry.get("category", Category.WORK.value)),
                note=read_text("note"),
                labels=read_text("labels"),
            )
        )

    def handle_reorder(event: ui.OnReorderEvent) -> None:
        if event.old_index is None or event.new_index is None:
            return
        vm.reorder(event.old_index, event.new_index)

    # ---------------------------------------------------------------- 对话框
    # use_dialog 必须在每次渲染都调用；用 None 表达"当前不展示"。
    ui.use_dialog(
        ui.AlertDialog(
            modal=True,
            title="新建任务" if state.editing_id is None else "编辑任务",
            content=TaskForm(
                task=state.editing_task,
                form=form_registry,
                key=f"task-form-{state.editing_id or 'new'}",
            ),
            actions=[
                ui.Button("取消", on_click=lambda _: vm.close_form()),
                ui.Button(
                    "保存",
                    icon=ui.Icons.CHECK,
                    style_type=ui.StyleType.PRIMARY,
                    on_click=lambda _: save_from_form(),
                ),
            ],
        )
        if state.form_open
        else None
    )

    ui.use_dialog(
        ui.AlertDialog(
            modal=True,
            title="删除任务",
            msg=(
                f"确定删除「{state.delete_target.title}」吗？此操作不可撤销。"
                if state.delete_target
                else "确定删除此任务吗？"
            ),
            style_type=ui.StyleType.ERROR,
            actions=[
                ui.Button("取消", on_click=lambda _: vm.cancel_delete()),
                ui.Button(
                    "删除",
                    icon=ui.Icons.DELETE_OUTLINE,
                    style_type=ui.StyleType.ERROR,
                    on_click=lambda _: vm.confirm_delete(),
                ),
            ],
        )
        if state.delete_id is not None
        else None
    )

    # ---------------------------------------------------------------- 列表
    list_content: ui.Control = (
        ui.ReorderableListView(
            controls=[
                TaskItem(
                    key=f"task-{task.id}",
                    task=task,
                    on_toggle=vm.toggle_task,
                    on_edit=vm.open_edit,
                    on_delete=vm.request_delete,
                )
                for task in state.visible_tasks
            ],
            expand=True,
            spacing=ui.SPACE["2"],
            padding=ui.Padding.symmetric(
                horizontal=ui.SPACE["6"], vertical=ui.SPACE["2"]
            ),
            show_default_drag_handles=False,
            on_reorder=handle_reorder,
        )
        if state.visible_tasks
        else _empty_state(state, vm.open_add)
    )

    meta: list[ui.Control] = [
        ui.Text(format_today(), size=ui.FONT_SIZE["small"], color=TEXT_SECONDARY),
        ui.Text("·", size=ui.FONT_SIZE["small"], color=ui.Colors.OUTLINE_VARIANT),
        ui.Text(
            f"{state.completed}/{state.total} 已完成",
            size=ui.FONT_SIZE["small"],
            color=TEXT_SECONDARY,
        ),
        ui.Text("·", size=ui.FONT_SIZE["small"], color=ui.Colors.OUTLINE_VARIANT),
        ui.Text(
            "专注模式" if state.focus_mode else "全部任务",
            size=ui.FONT_SIZE["small"],
            color=PRIORITY_COLOR[Priority.HIGH.value]
            if state.focus_mode
            else TEXT_SECONDARY,
            weight=ui.FontWeight.W_600 if state.focus_mode else ui.FontWeight.W_400,
        ),
    ]
    if state.search_query.strip():
        meta.extend(
            [
                ui.Text("·", size=ui.FONT_SIZE["small"], color=ui.Colors.OUTLINE_VARIANT),
                ui.Text(
                    f"搜索 {len(state.visible_tasks)} 条",
                    size=ui.FONT_SIZE["small"],
                    color=ui.Colors.PRIMARY,
                    weight=ui.FontWeight.W_500,
                ),
            ]
        )

    # ---------------------------------------------------------------- 页面
    return ui.Container(
        content=ui.Column(
            controls=[
                ui.Container(
                    content=ui.Row(
                        controls=[
                            ui.Column(
                                controls=[
                                    ui.Text(
                                        "今日任务",
                                        size=ui.FONT_SIZE["headline"],
                                        weight=ui.FontWeight.W_700,
                                        color=TEXT_PRIMARY,
                                    ),
                                    ui.Row(controls=meta, spacing=ui.SPACE["2"], tight=True),
                                ],
                                spacing=ui.SPACE["1"],
                                alignment=ui.MainAxisAlignment.CENTER,
                            ),
                            ui.Container(expand=True),
                            ui.RingProgress(
                                state.completed,
                                total=state.total,
                                tooltip=f"已完成 {state.completed} / {state.total} 项",
                            ),
                        ],
                        vertical_alignment=ui.CrossAxisAlignment.CENTER,
                        spacing=ui.SPACE["3"],
                    ),
                    padding=ui.Padding.symmetric(
                        horizontal=ui.SPACE["6"], vertical=ui.SPACE["5"] - 2
                    ),
                ),
                ui.Container(height=1, bgcolor=ui.Colors.OUTLINE_VARIANT),
                ui.Container(
                    content=SearchBar(
                        value=state.search_query,
                        on_change=vm.set_search_query,
                        focus_key=state.search_focus_key,
                    ),
                    padding=ui.Padding.symmetric(
                        horizontal=ui.SPACE["6"], vertical=ui.SPACE["2"] + 2
                    ),
                ),
                ui.Container(
                    content=FilterBar(
                        category=state.category,
                        status=state.status,
                        focus_mode=state.focus_mode,
                        on_category=vm.set_category,
                        on_status=vm.set_status,
                        on_focus=vm.toggle_focus,
                        on_add=vm.open_add,
                    ),
                    padding=ui.Padding.symmetric(
                        horizontal=ui.SPACE["6"], vertical=ui.SPACE["2"]
                    ),
                ),
                ui.Container(height=1, bgcolor=ui.Colors.OUTLINE_VARIANT),
                list_content,
            ],
            spacing=0,
            expand=True,
        ),
        bgcolor=ui.Colors.SURFACE,
        expand=True,
        padding=ui.Padding.only(top=ui.SPACE["2"]),
    )

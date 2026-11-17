"""主应用组件：状态编排、对话框与页面布局。

原则：**组件只描述 UI = f(state)**。所有业务写入都在事件回调里调用 repository，
成功后用 ``set_tasks`` 重取一次数据；列表、统计、筛选全部由 ``use_memo`` 从同一份
任务数组派生，不维护第二份真相。
"""
from __future__ import annotations

import ui

from components.filter_bar import FilterBar
from components.search_bar import SearchBar
from components.task_form import TaskForm
from components.task_item import TaskItem
from repository import (
    create_task,
    delete_task,
    get_task,
    list_tasks,
    reorder_tasks,
    toggle_status,
    update_task,
)
from services.task_query import filter_tasks, task_stats
from theme import PRIORITY_COLOR, TEXT_PRIMARY, TEXT_SECONDARY
from utils.date_fmt import format_today
from utils.feedback import show_toast


def _empty_state(focus_mode: bool, search_query: str, on_add) -> ui.Control:
    """空态：区分"被筛掉"与"真的没有"，只有后者给新建入口。"""
    if search_query.strip():
        text = "未找到匹配任务"
        hint = f"没有包含「{search_query.strip()}」的任务，试试其他关键词"
        icon = ui.Icons.SEARCH_OFF
        icon_color = None
        action = None
    elif focus_mode:
        text = "暂无高优先级任务"
        hint = "保持专注，继续推进！"
        icon = ui.Icons.CENTER_FOCUS_STRONG
        icon_color = PRIORITY_COLOR["high"]
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
            on_click=on_add,
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
def App() -> ui.Control:
    page = ui.context.page

    tasks, set_tasks = ui.use_state(lambda: list(list_tasks()))
    category, set_category = ui.use_state("all")
    status, set_status = ui.use_state("all")
    focus_mode, set_focus_mode = ui.use_state(False)
    search_query, set_search_query = ui.use_state("")
    search_focus_key, set_search_focus_key = ui.use_state(0)

    form_open, set_form_open = ui.use_state(False)
    editing_id, set_editing_id = ui.use_state(None)
    delete_id, set_delete_id = ui.use_state(None)
    form_data = ui.use_ref(lambda: {}).current

    visible_tasks = ui.use_memo(
        lambda: filter_tasks(
            tasks,
            category=category,
            status=status,
            focus_mode=focus_mode,
            search_query=search_query,
        ),
        [tasks, category, status, focus_mode, search_query],
    )
    completed_total, total = ui.use_memo(lambda: task_stats(tasks), [tasks])

    def refresh() -> None:
        set_tasks(list(list_tasks()))

    def patch_task(task_id: int, **fields) -> None:
        set_tasks(
            lambda prev: [
                t.model_copy(update=fields) if t.id == task_id else t for t in prev
            ]
        )

    def handle_toggle(task_id: int) -> None:
        target = next((t for t in tasks if t.id == task_id), None)
        if target is None:
            return
        patch_task(task_id, status="completed" if target.status == "pending" else "pending")
        try:
            toggle_status(task_id)
        except Exception:
            refresh()
            show_toast(page, "更新失败，请重试", tone="error")

    def handle_open_add() -> None:
        set_editing_id(None)
        set_form_open(True)

    def handle_open_edit(task_id: int) -> None:
        set_editing_id(task_id)
        set_form_open(True)

    def save(
        title: str,
        priority: str,
        category_value: str,
        note: str,
        labels: str,
    ) -> None:
        try:
            if editing_id is not None:
                update_task(
                    editing_id,
                    title=title,
                    priority=priority,
                    category=category_value,
                    note=note,
                    labels=labels,
                )
                show_toast(page, "任务已更新", tone="success")
            else:
                create_task(title, priority, category_value, note, labels)
                show_toast(page, "任务已创建", tone="success")
        except Exception:
            show_toast(page, "保存失败，请重试", tone="error")
            return
        set_form_open(False)
        set_editing_id(None)
        refresh()

    def handle_save_from_form() -> None:
        """保存按钮在对话框操作区，值从表单登记的数据对象读取。"""
        title_field = form_data.get("title")
        note_field = form_data.get("note")
        labels_field = form_data.get("labels")
        title = str(title_field.value or "").strip() if title_field else ""
        if not title:
            show_toast(page, "请填写任务标题", tone="info")
            return
        save(
            title,
            form_data.get("priority", "medium"),
            form_data.get("category", "work"),
            str(note_field.value or "").strip() if note_field else "",
            str(labels_field.value or "").strip() if labels_field else "",
        )

    def handle_form_cancel() -> None:
        set_form_open(False)
        set_editing_id(None)

    def handle_request_delete(task_id: int) -> None:
        set_delete_id(task_id)

    def handle_confirm_delete() -> None:
        if delete_id is None:
            return
        removed = next((t for t in tasks if t.id == delete_id), None)
        set_tasks(lambda prev: [t for t in prev if t.id != delete_id])
        set_delete_id(None)
        try:
            if not delete_task(delete_id):
                refresh()
                show_toast(page, "删除失败，请重试", tone="error")
                return
            show_toast(page, f"已删除「{removed.title if removed else '任务'}」", tone="success")
        except Exception:
            refresh()
            show_toast(page, "删除失败，请重试", tone="error")

    def handle_cancel_delete() -> None:
        set_delete_id(None)

    def handle_focus() -> None:
        set_focus_mode(lambda v: not v)

    def handle_reorder(e: ui.OnReorderEvent) -> None:
        if e.old_index is None or e.new_index is None or e.old_index == e.new_index:
            return

        visible = list(visible_tasks)
        moved = visible.pop(e.old_index)
        visible.insert(e.new_index, moved)

        full = sorted(tasks, key=lambda t: t.sort_order)
        visible_ids = {t.id for t in visible_tasks}
        visible_slots = [i for i, t in enumerate(full) if t.id in visible_ids]

        new_full = list(full)
        for slot, task in zip(visible_slots, visible):
            new_full[slot] = task

        set_tasks([t.model_copy(update={"sort_order": i}) for i, t in enumerate(new_full)])
        try:
            reorder_tasks([t.id for t in new_full])
        except Exception:
            refresh()
            show_toast(page, "排序保存失败，请重试", tone="error")

    def on_keyboard(e: ui.KeyboardEvent) -> None:
        if e.ctrl and e.key == "N":
            handle_open_add()
        elif e.ctrl and e.key == "F":
            set_search_focus_key(lambda k: k + 1)
        elif e.key == "Escape":
            if form_open:
                handle_form_cancel()
            elif delete_id is not None:
                handle_cancel_delete()
            elif search_query.strip():
                set_search_query("")

    def bind_keyboard():
        page.on_keyboard_event = on_keyboard

        def cleanup():
            page.on_keyboard_event = None

        return cleanup

    ui.use_effect(bind_keyboard, [])

    # ---------------------------------------------------------------- 对话框
    editing_task = get_task(editing_id) if editing_id is not None else None
    ui.use_dialog(
        ui.AlertDialog(
            modal=True,
            title="新建任务" if editing_id is None else "编辑任务",
            content=TaskForm(
                task=editing_task,
                form=form_data,
                key=f"task-form-{editing_id or 'new'}",
            ),
            actions=[
                ui.Button("取消", on_click=lambda _: handle_form_cancel()),
                ui.Button(
                    "保存",
                    icon=ui.Icons.CHECK,
                    style_type=ui.StyleType.PRIMARY,
                    on_click=lambda _: handle_save_from_form(),
                ),
            ],
        )
        if form_open
        else None
    )

    delete_target = next((t for t in tasks if t.id == delete_id), None)
    ui.use_dialog(
        ui.AlertDialog(
            modal=True,
            title="删除任务",
            msg=(
                f"确定删除「{delete_target.title}」吗？此操作不可撤销。"
                if delete_target
                else "确定删除此任务吗？"
            ),
            style_type=ui.StyleType.ERROR,
            actions=[
                ui.Button("取消", on_click=lambda _: handle_cancel_delete()),
                ui.Button(
                    "删除",
                    icon=ui.Icons.DELETE_OUTLINE,
                    style_type=ui.StyleType.ERROR,
                    on_click=lambda _: handle_confirm_delete(),
                ),
            ],
        )
        if delete_id is not None
        else None
    )

    # ---------------------------------------------------------------- 列表
    list_content = (
        ui.ReorderableListView(
            controls=[
                TaskItem(
                    key=f"task-{t.id}",
                    task=t,
                    on_toggle=handle_toggle,
                    on_edit=handle_open_edit,
                    on_delete=handle_request_delete,
                )
                for t in visible_tasks
            ],
            expand=True,
            spacing=ui.SPACE["2"],
            padding=ui.Padding.symmetric(horizontal=ui.SPACE["6"], vertical=ui.SPACE["2"]),
            show_default_drag_handles=False,
            on_reorder=handle_reorder,
        )
        if visible_tasks
        else _empty_state(focus_mode, search_query, lambda _: handle_open_add())
    )

    meta = [
        ui.Text(format_today(), size=ui.FONT_SIZE["small"], color=TEXT_SECONDARY),
        ui.Text("·", size=ui.FONT_SIZE["small"], color=ui.Colors.OUTLINE_VARIANT),
        ui.Text(
            f"{completed_total}/{total} 已完成",
            size=ui.FONT_SIZE["small"],
            color=TEXT_SECONDARY,
        ),
        ui.Text("·", size=ui.FONT_SIZE["small"], color=ui.Colors.OUTLINE_VARIANT),
        ui.Text(
            "专注模式" if focus_mode else "全部任务",
            size=ui.FONT_SIZE["small"],
            color=PRIORITY_COLOR["high"] if focus_mode else TEXT_SECONDARY,
            weight=ui.FontWeight.W_600 if focus_mode else ui.FontWeight.W_400,
        ),
    ]
    if search_query.strip():
        meta.extend(
            [
                ui.Text("·", size=ui.FONT_SIZE["small"], color=ui.Colors.OUTLINE_VARIANT),
                ui.Text(
                    f"搜索 {len(visible_tasks)} 条",
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
                                completed_total,
                                total=total,
                                tooltip=f"已完成 {completed_total} / {total} 项",
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
                        value=search_query,
                        on_change=set_search_query,
                        focus_key=search_focus_key,
                    ),
                    padding=ui.Padding.symmetric(
                        horizontal=ui.SPACE["6"], vertical=ui.SPACE["2"] + 2
                    ),
                ),
                ui.Container(
                    content=FilterBar(
                        category=category,
                        status=status,
                        focus_mode=focus_mode,
                        on_category=set_category,
                        on_status=set_status,
                        on_focus=handle_focus,
                        on_add=lambda _: handle_open_add(),
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

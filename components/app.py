"""主应用组件：状态管理与布局编排。"""
import flet as ft

from components.filter_bar import FilterBar
from components.progress_ring import ProgressRingView
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
from theme import (
    ACCENT,
    BG_APP,
    BORDER_SUBTLE,
    PRIORITY_COLOR,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from utils.date_fmt import format_today
from utils.feedback import show_toast


def _empty_state(focus_mode: bool, search_query: str = "") -> ft.Control:
    if search_query.strip():
        title, sub, icon, color = (
            "未找到匹配任务",
            f"没有包含「{search_query.strip()}」的任务，试试其他关键词",
            ft.Icons.SEARCH_OFF,
            TEXT_MUTED,
        )
    elif focus_mode:
        title, sub, icon, color = (
            "暂无高优先级任务",
            "保持专注，继续推进！",
            ft.Icons.CENTER_FOCUS_STRONG,
            PRIORITY_COLOR["high"],
        )
    else:
        title, sub, icon, color = (
            "暂无任务",
            "点击「新建任务」或按 Ctrl+N 开始记录",
            ft.Icons.INBOX_OUTLINED,
            TEXT_MUTED,
        )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(icon, size=48, color=color),
                ft.Text(title, size=14, weight=ft.FontWeight.W_500, color=TEXT_PRIMARY),
                ft.Text(sub, size=12, color=TEXT_MUTED),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        alignment=ft.Alignment.CENTER,
        expand=True,
    )


@ft.component
def App():
    tasks, set_tasks = ft.use_state(lambda: list(list_tasks()))
    category, set_category = ft.use_state("all")
    status, set_status = ft.use_state("all")
    focus_mode, set_focus_mode = ft.use_state(False)
    search_query, set_search_query = ft.use_state("")
    search_focus_key, set_search_focus_key = ft.use_state(0)

    form_open, set_form_open = ft.use_state(False)
    editing_id, set_editing_id = ft.use_state(None)
    delete_id, set_delete_id = ft.use_state(None)

    visible_tasks = ft.use_memo(
        lambda: filter_tasks(
            tasks,
            category=category,
            status=status,
            focus_mode=focus_mode,
            search_query=search_query,
        ),
        [tasks, category, status, focus_mode, search_query],
    )
    completed_total, total = ft.use_memo(lambda: task_stats(tasks), [tasks])

    def refresh():
        set_tasks(list(list_tasks()))

    def patch_task(task_id: int, **fields):
        set_tasks(
            lambda prev: [
                t.model_copy(update=fields) if t.id == task_id else t for t in prev
            ]
        )

    def handle_toggle(task_id):
        target = next((t for t in tasks if t.id == task_id), None)
        if target is None:
            return
        new_status = "completed" if target.status == "pending" else "pending"
        patch_task(task_id, status=new_status)
        try:
            toggle_status(task_id)
        except Exception:
            refresh()
            show_toast("更新失败，请重试", icon=ft.Icons.ERROR_OUTLINE)

    def handle_open_add():
        set_editing_id(None)
        set_form_open(True)

    def handle_open_edit(task_id):
        set_editing_id(task_id)
        set_form_open(True)

    def handle_save(t_title, t_priority, t_category, t_note):
        try:
            if editing_id is not None:
                update_task(
                    editing_id,
                    title=t_title,
                    priority=t_priority,
                    category=t_category,
                    note=t_note,
                )
                show_toast("任务已更新", icon=ft.Icons.CHECK_CIRCLE_OUTLINE)
            else:
                create_task(t_title, t_priority, t_category, t_note)
                show_toast("任务已创建", icon=ft.Icons.CHECK_CIRCLE_OUTLINE)
        except Exception:
            show_toast("保存失败，请重试", icon=ft.Icons.ERROR_OUTLINE)
            return
        set_form_open(False)
        set_editing_id(None)
        refresh()

    def handle_form_cancel():
        set_form_open(False)
        set_editing_id(None)

    def handle_request_delete(task_id):
        set_delete_id(task_id)

    def handle_confirm_delete():
        if delete_id is None:
            return
        removed = next((t for t in tasks if t.id == delete_id), None)
        set_tasks(lambda prev: [t for t in prev if t.id != delete_id])
        set_delete_id(None)
        try:
            if not delete_task(delete_id):
                refresh()
                show_toast("删除失败，请重试", icon=ft.Icons.ERROR_OUTLINE)
                return
            title = removed.title if removed else "任务"
            show_toast(f"已删除「{title}」", icon=ft.Icons.DELETE_OUTLINE)
        except Exception:
            refresh()
            show_toast("删除失败，请重试", icon=ft.Icons.ERROR_OUTLINE)

    def handle_cancel_delete():
        set_delete_id(None)

    def handle_focus():
        set_focus_mode(lambda v: not v)

    def handle_focus_search():
        set_search_focus_key(lambda k: k + 1)

    def handle_reorder(e: ft.OnReorderEvent):
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

        updated = [t.model_copy(update={"sort_order": i}) for i, t in enumerate(new_full)]
        set_tasks(updated)
        try:
            reorder_tasks([t.id for t in new_full])
        except Exception:
            refresh()
            show_toast("排序保存失败，请重试", icon=ft.Icons.ERROR_OUTLINE)

    def on_keyboard(e: ft.KeyboardEvent):
        if e.ctrl and e.key == "N":
            handle_open_add()
        elif e.ctrl and e.key == "F":
            handle_focus_search()
        elif e.key == "Escape":
            if form_open:
                handle_form_cancel()
            elif delete_id is not None:
                handle_cancel_delete()
            elif search_query.strip():
                set_search_query("")

    def bind_keyboard():
        page = ft.context.page
        page.on_keyboard_event = on_keyboard

        def cleanup():
            page.on_keyboard_event = None

        return cleanup

    ft.use_effect(bind_keyboard, [])

    editing_task = get_task(editing_id) if editing_id is not None else None

    ft.use_dialog(
        ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "新建任务" if editing_id is None else "编辑任务",
                size=18,
                weight=ft.FontWeight.W_600,
                color=TEXT_PRIMARY,
            ),
            content=TaskForm(
                key=f"task-form-{editing_id or 'new'}",
                task=editing_task,
                on_save=handle_save,
                on_cancel=handle_form_cancel,
            ),
            content_padding=ft.Padding.symmetric(horizontal=24, vertical=16),
            actions_padding=ft.Padding.symmetric(horizontal=16, vertical=8),
        )
        if form_open
        else None
    )

    delete_task_obj = next((t for t in tasks if t.id == delete_id), None)
    ft.use_dialog(
        ft.AlertDialog(
            modal=True,
            title=ft.Text("删除任务", size=16, weight=ft.FontWeight.W_600),
            content=ft.Text(
                f"确定删除「{delete_task_obj.title}」吗？此操作不可撤销。"
                if delete_task_obj
                else "确定删除此任务吗？",
                size=13,
                color=TEXT_SECONDARY,
            ),
            actions=[
                ft.TextButton("取消", on_click=lambda _: handle_cancel_delete()),
                ft.Button(
                    content=ft.Text("删除", size=13, weight=ft.FontWeight.W_500),
                    icon=ft.Icons.DELETE_OUTLINE,
                    on_click=lambda _: handle_confirm_delete(),
                    style=ft.ButtonStyle(
                        bgcolor=PRIORITY_COLOR["high"],
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=6),
                    ),
                ),
            ],
            actions_padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        )
        if delete_id is not None
        else None
    )

    list_content = (
        ft.ReorderableListView(
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
            spacing=8,
            padding=ft.Padding.symmetric(horizontal=24, vertical=8),
            show_default_drag_handles=False,
            on_reorder=handle_reorder,
        )
        if visible_tasks
        else _empty_state(focus_mode, search_query)
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "今日任务",
                                        size=22,
                                        weight=ft.FontWeight.W_700,
                                        color=TEXT_PRIMARY,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Text(format_today(), size=12, color=TEXT_SECONDARY),
                                            ft.Text("·", size=12, color=BORDER_SUBTLE),
                                            ft.Text(
                                                f"{completed_total}/{total} 已完成",
                                                size=12,
                                                color=TEXT_SECONDARY,
                                            ),
                                            ft.Text("·", size=12, color=BORDER_SUBTLE),
                                            ft.Text(
                                                "专注模式" if focus_mode else "全部任务",
                                                size=12,
                                                color=PRIORITY_COLOR["high"] if focus_mode else TEXT_SECONDARY,
                                                weight=ft.FontWeight.W_600 if focus_mode else ft.FontWeight.W_400,
                                            ),
                                            *(
                                                [
                                                    ft.Text("·", size=12, color=BORDER_SUBTLE),
                                                    ft.Text(
                                                        f"搜索 {len(visible_tasks)} 条",
                                                        size=12,
                                                        color=ACCENT,
                                                        weight=ft.FontWeight.W_500,
                                                    ),
                                                ]
                                                if search_query.strip()
                                                else []
                                            ),
                                        ],
                                        spacing=8,
                                        tight=True,
                                    ),
                                ],
                                spacing=4,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Container(expand=True),
                            ProgressRingView(completed_total, total),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    padding=ft.Padding.symmetric(horizontal=24, vertical=18),
                ),
                ft.Container(height=1, bgcolor=BORDER_SUBTLE),
                ft.Container(
                    content=SearchBar(
                        value=search_query,
                        on_change=set_search_query,
                        focus_key=search_focus_key,
                    ),
                    padding=ft.Padding.symmetric(horizontal=24, vertical=10),
                ),
                ft.Container(
                    content=FilterBar(
                        category=category,
                        status=status,
                        focus_mode=focus_mode,
                        on_category=set_category,
                        on_status=set_status,
                        on_focus=handle_focus,
                        on_add=lambda _: handle_open_add(),
                    ),
                    padding=ft.Padding.symmetric(horizontal=24, vertical=8),
                ),
                ft.Container(height=1, bgcolor=BORDER_SUBTLE),
                list_content,
            ],
            spacing=0,
            expand=True,
        ),
        bgcolor=BG_APP,
        expand=True,
        padding=ft.Padding.only(top=8),
    )

"""任务表单：新建/编辑对话框内容。"""
import flet as ft

from components.chip import SelectChip
from theme import (
    ACCENT,
    BORDER_SUBTLE,
    CATEGORY_COLOR,
    CATEGORY_ICON,
    CATEGORY_LABEL,
    PRIORITY_COLOR,
    PRIORITY_LABEL,
    TEXT_SECONDARY,
)
from utils.feedback import show_toast


@ft.component
def TaskForm(task, on_save, on_cancel):
    """任务表单（通过 key 在打开时重置状态）。"""
    title, set_title = ft.use_state(task.title if task else "")
    priority, set_priority = ft.use_state(task.priority if task else "medium")
    category, set_category = ft.use_state(task.category if task else "work")
    labels, set_labels = ft.use_state(task.labels if task else "")
    note, set_note = ft.use_state(task.note if task else "")

    def handle_save(_=None):
        trimmed = title.strip()
        if not trimmed:
            show_toast("请填写任务标题", icon=ft.Icons.INFO_OUTLINE)
            return
        on_save(trimmed, priority, category, note.strip(), labels.strip())

    can_save = bool(title.strip())

    return ft.Column(
        controls=[
            ft.TextField(
                label="任务标题",
                value=title,
                hint_text="例如：完成季度汇报草稿",
                autofocus=True,
                text_size=14,
                border_radius=6,
                border_color=BORDER_SUBTLE,
                focused_border_color=ACCENT,
                on_change=lambda e: set_title(e.control.value),
                on_submit=handle_save,
            ),
            ft.Column(
                controls=[
                    ft.Text("优先级", size=12, color=TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                    ft.Row(
                        controls=[
                            SelectChip(
                                label=PRIORITY_LABEL[p],
                                active=(priority == p),
                                on_click=lambda e, v=p: set_priority(v),
                                color=PRIORITY_COLOR[p],
                            )
                            for p in ("high", "medium", "low")
                        ],
                        spacing=8,
                        tight=True,
                    ),
                ],
                spacing=6,
            ),
            ft.Column(
                controls=[
                    ft.Text("分类", size=12, color=TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                    ft.Row(
                        controls=[
                            SelectChip(
                                label=CATEGORY_LABEL[c],
                                active=(category == c),
                                on_click=lambda e, v=c: set_category(v),
                                color=CATEGORY_COLOR[c],
                                icon=CATEGORY_ICON[c],
                            )
                            for c in ("work", "study", "life")
                        ],
                        spacing=8,
                        tight=True,
                    ),
                ],
                spacing=6,
            ),
            ft.TextField(
                label="标签（可选）",
                value=labels,
                hint_text="用逗号分隔，例如：紧急, 客户, 本周",
                text_size=13,
                border_radius=6,
                border_color=BORDER_SUBTLE,
                focused_border_color=ACCENT,
                on_change=lambda e: set_labels(e.control.value),
            ),
            ft.TextField(
                label="备注（可选）",
                value=note,
                hint_text="补充上下文、链接或验收标准…",
                multiline=True,
                min_lines=2,
                max_lines=4,
                text_size=13,
                border_radius=6,
                border_color=BORDER_SUBTLE,
                focused_border_color=ACCENT,
                on_change=lambda e: set_note(e.control.value),
            ),
            ft.Row(
                controls=[
                    ft.TextButton("取消", on_click=lambda _: on_cancel()),
                    ft.Button(
                        content=ft.Text("保存", size=13, weight=ft.FontWeight.W_500),
                        icon=ft.Icons.CHECK,
                        on_click=handle_save,
                        disabled=not can_save,
                        style=ft.ButtonStyle(
                            bgcolor=ACCENT,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=6),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
                spacing=8,
            ),
        ],
        spacing=14,
        tight=True,
    )

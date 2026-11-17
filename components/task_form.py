"""任务表单：新建 / 编辑对话框的内容区。

表单值不放在 ``use_state`` 里逐字回写（那会让每次敲键都重渲染整棵控件树）：
三个文本框用 cs-ui 的 ``Input`` 数据对象持有，选择项用两个 ``use_state`` 持有，
渲染时把这些数据对象交给外层的 ``form`` 字典。保存按钮在对话框操作区，
点击时读 ``form`` 即可拿到最新值 —— 值的唯一来源是数据对象，不是某个控件属性。
"""
from __future__ import annotations

import ui

from theme import (
    CATEGORY_COLOR,
    CATEGORY_ICON,
    CATEGORY_LABEL,
    PRIORITY_COLOR,
    PRIORITY_LABEL,
    TEXT_SECONDARY,
)


@ui.component
def TaskForm(task, form: dict) -> ui.Control:
    """任务表单。调用方用 ``key`` 区分新建 / 编辑，从而重置内部输入状态。"""
    title = ui.use_ref(
        lambda: ui.Input(
            label="任务标题",
            value=task.title if task else "",
            hint_text="例如：完成季度汇报草稿",
            width=420,
        )
    ).current
    labels = ui.use_ref(
        lambda: ui.Input(
            label="标签（可选）",
            value=task.labels if task else "",
            hint_text="用逗号分隔，例如：紧急, 客户, 本周",
            width=420,
        )
    ).current
    note = ui.use_ref(
        lambda: ui.Input(
            label="备注（可选）",
            value=task.note if task else "",
            hint_text="补充上下文、链接或验收标准…",
            multiline=True,
            width=420,
        )
    ).current

    priority, set_priority = ui.use_state(task.priority if task else "medium")
    category, set_category = ui.use_state(task.category if task else "work")

    # 每次渲染同步一次引用；事件回调里读 form 拿到的就是最新的数据对象。
    form.update(
        title=title,
        labels=labels,
        note=note,
        priority=priority,
        category=category,
    )

    return ui.Column(
        controls=[
            title.ui(),
            _choice_group(
                "优先级",
                [
                    ui.ChoiceChip(
                        PRIORITY_LABEL[p],
                        value=p,
                        selected=(priority == p),
                        on_click=set_priority,
                        color=PRIORITY_COLOR[p],
                    )
                    for p in ("high", "medium", "low")
                ],
            ),
            _choice_group(
                "分类",
                [
                    ui.ChoiceChip(
                        CATEGORY_LABEL[c],
                        value=c,
                        selected=(category == c),
                        on_click=set_category,
                        color=CATEGORY_COLOR[c],
                        icon=CATEGORY_ICON[c],
                    )
                    for c in ("work", "study", "life")
                ],
            ),
            labels.ui(),
            note.ui(),
        ],
        spacing=ui.SPACE["4"],
        tight=True,
    )


def _choice_group(label: str, chips: list[ui.Control]) -> ui.Control:
    """「标题 + 一排胶囊」的字段组，两组共用同一套间距与层级。"""
    return ui.Column(
        controls=[
            ui.Text(
                label,
                size=ui.FONT_SIZE["small"],
                color=TEXT_SECONDARY,
                weight=ui.FontWeight.W_500,
            ),
            ui.Row(controls=chips, spacing=ui.SPACE["2"], tight=True),
        ],
        spacing=ui.SPACE["2"],
        tight=True,
    )

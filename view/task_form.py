"""任务表单：新建 / 编辑对话框的内容区。

表单值不放在 ``use_state`` 里逐字回写（那会让每次敲键都重渲染整棵控件树）：
三个文本框用 cs-ui 的 ``Input`` 数据对象持有，选择项用两个 ``use_state`` 持有，
渲染时把这些数据对象登记到外层 ``form`` 字典。保存按钮在对话框操作区，点击时读
``form`` 拿到最新值 —— 唯一来源是数据对象，不是某个控件属性。

"编辑缓冲区"是视图的临时状态：只有提交时才整体交给视图模型，避免逐字触发业务层。
它不含判断规则，因此不违反"视图无业务逻辑"。
"""
from __future__ import annotations

import ui

from models.constants import CATEGORY_LABEL, PRIORITY_LABEL
from models.enums import Category, Priority
from models.task import Task
from view.design import (
    CATEGORY_COLOR,
    CATEGORY_ICON,
    PRIORITY_COLOR,
    TEXT_SECONDARY,
)

__all__ = ["FormRegistry", "TaskForm"]

type FormRegistry = dict[str, object]


@ui.component
def TaskForm(task: Task | None, form: FormRegistry) -> ui.Control:
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

    priority, set_priority = ui.use_state(
        task.priority if task else Priority.MEDIUM.value
    )
    category, set_category = ui.use_state(
        task.category if task else Category.WORK.value
    )

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
                        PRIORITY_LABEL[value],
                        value=value,
                        selected=(priority == value),
                        on_click=set_priority,
                        color=PRIORITY_COLOR[value],
                    )
                    for value in (Priority.HIGH.value, Priority.MEDIUM.value, Priority.LOW.value)
                ],
            ),
            _choice_group(
                "分类",
                [
                    ui.ChoiceChip(
                        CATEGORY_LABEL[value],
                        value=value,
                        selected=(category == value),
                        on_click=set_category,
                        color=CATEGORY_COLOR[value],
                        icon=CATEGORY_ICON[value],
                    )
                    for value in (
                        Category.WORK.value,
                        Category.STUDY.value,
                        Category.LIFE.value,
                    )
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

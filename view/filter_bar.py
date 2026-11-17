"""筛选栏：分类、状态、专注模式与新建入口。

分类 / 状态用 :class:`ui.SegmentedButton` 做分段选择：显示文案与逻辑值分开
（"工作" ↔ ``work``），选中态由外部状态决定，本组件不保存任何筛选条件。
"""
from __future__ import annotations

from collections.abc import Callable

import ui

from models.constants import CATEGORY_LABEL, STATUS_LABEL
from models.enums import Category, FilterStatus, Priority
from view.design import (
    CATEGORY_ICON,
    PRIORITY_COLOR,
    PRIORITY_FILL,
    PRIORITY_ON,
)
from view.segments import ChoiceHandler, SegmentedChoice

__all__ = ["FilterBar"]

# 分类选项：逻辑值 → 展示文案 → 图标；"全部" 不带图标，避免抢走分类的注意力。
_CATEGORIES: tuple[tuple[str, str, ui.IconData | None], ...] = (
    ("all", "全部", None),
    (
        Category.WORK.value,
        CATEGORY_LABEL[Category.WORK.value],
        CATEGORY_ICON[Category.WORK.value],
    ),
    (
        Category.STUDY.value,
        CATEGORY_LABEL[Category.STUDY.value],
        CATEGORY_ICON[Category.STUDY.value],
    ),
    (
        Category.LIFE.value,
        CATEGORY_LABEL[Category.LIFE.value],
        CATEGORY_ICON[Category.LIFE.value],
    ),
)
_STATUSES: tuple[str, ...] = (
    FilterStatus.ALL.value,
    FilterStatus.PENDING.value,
    FilterStatus.COMPLETED.value,
)


@ui.component
def FilterBar(
    category: str,
    status: str,
    focus_mode: bool,
    on_category: ChoiceHandler,
    on_status: ChoiceHandler,
    on_focus: Callable[[], None],
    on_add: Callable[[], None],
) -> ui.Control:
    """筛选栏组件：所有交互都只回调，不自己持有状态。"""
    return ui.Row(
        controls=[
            SegmentedChoice(
                _CATEGORIES,
                selected=category,
                on_change=on_category,
                disabled=focus_mode,
            ),
            ui.VerticalDivider(width=1, opacity=0.6),
            SegmentedChoice(
                tuple((value, STATUS_LABEL[value], None) for value in _STATUSES),
                selected=status,
                on_change=on_status,
                disabled=focus_mode,
            ),
            ui.Container(expand=True),
            _focus_toggle(focus_mode, on_focus),
            ui.Button(
                "新建任务",
                icon=ui.Icons.ADD,
                tooltip="Ctrl+N",
                style_type=ui.StyleType.PRIMARY,
                on_click=lambda _: on_add(),
            ),
        ],
        alignment=ui.MainAxisAlignment.START,
        vertical_alignment=ui.CrossAxisAlignment.CENTER,
        spacing=ui.SPACE["3"],
    )


def _focus_toggle(focus_mode: bool, on_focus: Callable[[], None]) -> ui.Control:
    """专注模式是开关而非单选，做成一枚可切换的胶囊。

    选中用语义 danger 实底 + 配套前景（对比度安全），未选中只留一圈描边；
    两种状态高度一致，切换时整行不跳动。
    """
    high = Priority.HIGH.value
    foreground = PRIORITY_ON[high] if focus_mode else PRIORITY_COLOR[high]
    return ui.Container(
        content=ui.Row(
            controls=[
                ui.Icon(
                    ui.Icons.CENTER_FOCUS_STRONG,
                    size=ui.ICON_SIZE["sm"],
                    color=foreground,
                ),
                ui.Text(
                    "专注模式",
                    size=ui.FONT_SIZE["small"],
                    weight=ui.FontWeight.W_600 if focus_mode else ui.FontWeight.W_500,
                    color=foreground,
                ),
            ],
            spacing=ui.SPACE["1"] + 2,
            tight=True,
        ),
        height=ui.CONTROL_HEIGHT["sm"],
        padding=ui.Padding.symmetric(horizontal=ui.SPACE["3"]),
        border_radius=ui.RADIUS["md"],
        bgcolor=PRIORITY_FILL[high] if focus_mode else None,
        border=None if focus_mode else ui.Border.all(1, PRIORITY_COLOR[high]),
        tooltip="仅显示高优先级未完成任务",
        on_click=lambda _: on_focus(),
        ink=True,
        ink_color=ui.overlay(0.12, role=PRIORITY_COLOR[high]),
        animate=ui.Animation(ui.DURATION["fast"], ui.AnimationCurve.EASE_OUT),
    )

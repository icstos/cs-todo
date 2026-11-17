"""筛选栏：分类、状态、专注模式与新建入口。

筛选胶囊直接用 cs-ui 的 ``ChoiceChip``：显示文案与逻辑值分开（"高优先级" ↔
``high``），选中态由外部状态决定，本组件不保存任何筛选条件。
"""
from __future__ import annotations

import ui

from theme import (
    CATEGORY_COLOR,
    CATEGORY_ICON,
    CATEGORY_LABEL,
    PRIORITY_COLOR,
    PRIORITY_FILL,
    PRIORITY_ON,
    STATUS_LABEL,
    TEXT_SECONDARY,
)

# 分类胶囊的强调色：全部用中性色，其余三类取主题角色。
_CATEGORIES: tuple[tuple[str, str, str | None, str], ...] = (
    ("all", "全部", None, TEXT_SECONDARY),
    ("work", CATEGORY_LABEL["work"], CATEGORY_ICON["work"], CATEGORY_COLOR["work"]),
    ("study", CATEGORY_LABEL["study"], CATEGORY_ICON["study"], CATEGORY_COLOR["study"]),
    ("life", CATEGORY_LABEL["life"], CATEGORY_ICON["life"], CATEGORY_COLOR["life"]),
)
_STATUSES = ("all", "pending", "completed")


@ui.component
def FilterBar(
    category: str,
    status: str,
    focus_mode: bool,
    on_category,
    on_status,
    on_focus,
    on_add,
) -> ui.Control:
    """筛选栏组件：所有交互都只回调，不自己持有状态。"""
    return ui.Row(
        controls=[
            ui.Row(
                controls=[
                    ui.ChoiceChip(
                        label=label,
                        value=value,
                        selected=(category == value),
                        disabled=focus_mode,
                        on_click=on_category,
                        icon=icon,
                        color=color,
                    )
                    for value, label, icon, color in _CATEGORIES
                ],
                spacing=ui.SPACE["2"],
                tight=True,
            ),
            ui.VerticalDivider(width=1, opacity=0.6),
            ui.Row(
                controls=[
                    ui.ChoiceChip(
                        label=STATUS_LABEL[s],
                        value=s,
                        selected=(status == s),
                        disabled=focus_mode,
                        on_click=on_status,
                        color=ui.Colors.PRIMARY,
                    )
                    for s in _STATUSES
                ],
                spacing=ui.SPACE["2"],
                tight=True,
            ),
            ui.Container(expand=True),
            _focus_toggle(focus_mode, on_focus),
            ui.Button(
                "新建任务",
                icon=ui.Icons.ADD,
                tooltip="Ctrl+N",
                style_type=ui.StyleType.PRIMARY,
                on_click=on_add,
            ),
        ],
        alignment=ui.MainAxisAlignment.START,
        vertical_alignment=ui.CrossAxisAlignment.CENTER,
        spacing=ui.SPACE["3"],
    )


def _focus_toggle(focus_mode: bool, on_focus) -> ui.Control:
    """专注模式是开关而非单选，做成一枚可切换的胶囊。

    选中用语义 danger 实底 + 配套前景（对比度安全），未选中只留一圈描边；
    两种状态高度一致，切换时整行不跳动。
    """
    fg = PRIORITY_ON["high"] if focus_mode else PRIORITY_COLOR["high"]
    return ui.Container(
        content=ui.Row(
            controls=[
                ui.Icon(ui.Icons.CENTER_FOCUS_STRONG, size=ui.ICON_SIZE["sm"], color=fg),
                ui.Text(
                    "专注模式",
                    size=ui.FONT_SIZE["small"],
                    weight=ui.FontWeight.W_600 if focus_mode else ui.FontWeight.W_500,
                    color=fg,
                ),
            ],
            spacing=ui.SPACE["1"] + 2,
            tight=True,
        ),
        height=ui.CONTROL_HEIGHT["sm"],
        padding=ui.Padding.symmetric(horizontal=ui.SPACE["3"]),
        border_radius=ui.RADIUS["md"],
        bgcolor=PRIORITY_FILL["high"] if focus_mode else None,
        border=None if focus_mode else ui.Border.all(1, PRIORITY_COLOR["high"]),
        tooltip="仅显示高优先级未完成任务",
        on_click=lambda _: on_focus(),
        ink=True,
        ink_color=ui.overlay(0.12, role=PRIORITY_COLOR["high"]),
        animate=ui.Animation(ui.DURATION["fast"], ui.AnimationCurve.EASE_OUT),
    )

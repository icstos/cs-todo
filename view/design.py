"""视图设计规范：品牌色、语义投影与窗口尺寸的唯一出口。

颜色只有两个来源：

1. **M3 角色名**（``ui.Colors.*``）—— 交给 Flutter 在绘制时解析，切主题零成本；
2. **cs-ui 语义三档**（``semantic_text`` / ``semantic`` / ``on_semantic``）——
   文字取 text 档、实底取 fill 档、实底上的字取 on 档，避免同一个绿出现五种色值。

间距 / 圆角 / 字号不在这里定义 —— 组件直接读 ``ui.SPACE`` / ``ui.RADIUS`` /
``ui.FONT_SIZE``，少一层转发就少一处漂移。中文文案来自 :mod:`models.constants`，
这里只负责把它们配上颜色与图标。
"""
from __future__ import annotations

import ui

from models.constants import CATEGORY_LABEL, PRIORITY_SHORT, STATUS_LABEL
from models.enums import Category, Priority

__all__ = [
    "BORDER_SUBTLE",
    "BRAND_PRIMARY",
    "CATEGORY_COLOR",
    "CATEGORY_ICON",
    "PRIORITY_COLOR",
    "PRIORITY_FILL",
    "PRIORITY_ON",
    "PRIORITY_SHORT",
    "STATUS_LABEL",
    "SUCCESS_TEXT",
    "TEXT_MUTED",
    "TEXT_PRIMARY",
    "TEXT_SECONDARY",
    "WINDOW_HEIGHT",
    "WINDOW_MIN_HEIGHT",
    "WINDOW_MIN_WIDTH",
    "WINDOW_WIDTH",
    "category_label",
]

#: 品牌蓝：唯一允许写在应用侧的色值，交给 cs-ui 色板引擎展开成 46 个角色。
BRAND_PRIMARY: str = "#2563EB"

WINDOW_WIDTH: int = 1024
WINDOW_HEIGHT: int = 720
WINDOW_MIN_WIDTH: int = 820
WINDOW_MIN_HEIGHT: int = 560

#: 文本层级：角色名随主题解析，不写死浅色专用色值。
TEXT_PRIMARY: str = ui.Colors.ON_SURFACE
TEXT_SECONDARY: str = ui.Colors.ON_SURFACE_VARIANT
TEXT_MUTED: str = ui.overlay(0.55)
BORDER_SUBTLE: str = ui.Colors.OUTLINE_VARIANT
#: M3 角色没有 success，完成态走 cs-ui 的语义文字档（对比度已解算）。
SUCCESS_TEXT: str = ui.semantic_text("success")

#: 优先级：text 档用于圆点与胶囊文字，fill / on 档用于实底（专注模式）。
PRIORITY_COLOR: dict[str, str] = {
    Priority.HIGH.value: ui.semantic_text("danger"),
    Priority.MEDIUM.value: ui.semantic_text("warning"),
    Priority.LOW.value: ui.semantic_text("success"),
}
PRIORITY_FILL: dict[str, str] = {
    Priority.HIGH.value: ui.semantic("danger"),
    Priority.MEDIUM.value: ui.semantic("warning"),
    Priority.LOW.value: ui.semantic("success"),
}
PRIORITY_ON: dict[str, str] = {
    Priority.HIGH.value: ui.on_semantic("danger"),
    Priority.MEDIUM.value: ui.on_semantic("warning"),
    Priority.LOW.value: ui.on_semantic("success"),
}

#: 分类：用主题角色而不是手抄色值，明暗主题下保持同一族性格。
CATEGORY_COLOR: dict[str, str] = {
    Category.WORK.value: ui.Colors.PRIMARY,
    Category.STUDY.value: ui.Colors.TERTIARY,
    Category.LIFE.value: ui.Colors.SECONDARY,
}
CATEGORY_ICON: dict[str, str] = {
    Category.WORK.value: ui.Icons.WORK_OUTLINED,
    Category.STUDY.value: (
        ui.Icons.SCHOOL_OUTLINED
        if hasattr(ui.Icons, "SCHOOL_OUTLINED")
        else ui.Icons.SCHOOL
    ),
    Category.LIFE.value: (
        ui.Icons.HOME_OUTLINED
        if hasattr(ui.Icons, "HOME_OUTLINED")
        else ui.Icons.HOME
    ),
}


def category_label(value: str) -> str:
    """取分类展示名；未知值退回原名，不让脏数据把界面打崩。"""
    return CATEGORY_LABEL.get(value, value)

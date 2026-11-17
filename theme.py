"""设计令牌：品牌色、语义色投影与业务文案常量。

颜色只有两个来源：

1. **M3 角色名**（``ui.Colors.*``）—— 交给 Flutter 在绘制时解析，切主题零成本；
2. **cs-ui 语义三档**（``semantic_text`` / ``semantic`` / ``on_semantic``）——
   文字取 text 档、实底取 fill 档、实底上的字取 on 档，避免同一个绿出现五种色值。

业务语义（优先级、分类）在这里投影一次，组件只认这些名字，不认十六进制。
间距 / 圆角 / 字号不在这里定义 —— 组件直接读 ``ui.SPACE`` / ``ui.RADIUS`` /
``ui.FONT_SIZE``，少一层转发就少一处漂移。
"""
from __future__ import annotations

import ui

# 品牌蓝：唯一一个允许写在应用侧的色值，交给 cs-ui 的色板引擎展开成 46 个角色。
BRAND_PRIMARY = "#2563EB"

# 文本层级：角色名随主题解析，不写死 #18181B 这类浅色专用值。
TEXT_PRIMARY = ui.Colors.ON_SURFACE
TEXT_SECONDARY = ui.Colors.ON_SURFACE_VARIANT
TEXT_MUTED = ui.overlay(0.55)
BORDER_SUBTLE = ui.Colors.OUTLINE_VARIANT
# M3 角色里没有 success，完成态走 cs-ui 的语义文字档（对比度已解算）。
SUCCESS_TEXT = ui.semantic_text("success")

# 艾森豪威尔优先级：text 档用于圆点与胶囊文字，fill/on 档用于实底（专注模式）。
PRIORITY_COLOR = {
    "high": ui.semantic_text("danger"),
    "medium": ui.semantic_text("warning"),
    "low": ui.semantic_text("success"),
}
PRIORITY_FILL = {
    "high": ui.semantic("danger"),
    "medium": ui.semantic("warning"),
    "low": ui.semantic("success"),
}
PRIORITY_ON = {
    "high": ui.on_semantic("danger"),
    "medium": ui.on_semantic("warning"),
    "low": ui.on_semantic("success"),
}

PRIORITY_LABEL = {
    "high": "高优先级",
    "medium": "中优先级",
    "low": "低优先级",
}
PRIORITY_SHORT = {"high": "高", "medium": "中", "low": "低"}

# 分类：用主题角色而不是三个手抄色值，浅色 / 深色下都保持同一族性格。
CATEGORY_COLOR = {
    "work": ui.Colors.PRIMARY,
    "study": ui.Colors.TERTIARY,
    "life": ui.Colors.SECONDARY,
}
CATEGORY_LABEL = {"work": "工作", "study": "学习", "life": "生活"}
CATEGORY_ICON = {
    "work": ui.Icons.WORK_OUTLINED,
    "study": ui.Icons.SCHOOL_OUTLINED
    if hasattr(ui.Icons, "SCHOOL_OUTLINED")
    else ui.Icons.SCHOOL,
    "life": ui.Icons.HOME_OUTLINED
    if hasattr(ui.Icons, "HOME_OUTLINED")
    else ui.Icons.HOME,
}

STATUS_LABEL = {"all": "全部", "pending": "进行中", "completed": "已完成"}

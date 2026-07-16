"""设计令牌：颜色、文案、图标常量。

Linear/Notion 风格：低饱和、克制、强调层级与可读性。
"""
import flet as ft

# 中性色（科学、有序、清爽）
BG_APP = "#FAFAFA"
BG_CARD = "#FFFFFF"
BG_HOVER = "#F4F4F5"
BG_FOCUS_ACTIVE = "#EFF6FF"

TEXT_PRIMARY = "#18181B"
TEXT_SECONDARY = "#71717A"
TEXT_MUTED = "#A1A1AA"

BORDER_SUBTLE = "#E4E4E7"
BORDER_FOCUS = "#C7C7CE"

ACCENT = "#2563EB"
ACCENT_SOFT = "#DBEAFE"

# 艾森豪威尔优先级（红/橙/绿）
PRIORITY_COLOR = {
    "high":   "#EF4444",
    "medium": "#F59E0B",
    "low":    "#10B981",
}
PRIORITY_LABEL = {
    "high":   "高优先级",
    "medium": "中优先级",
    "low":    "低优先级",
}
PRIORITY_SHORT = {
    "high":   "高",
    "medium": "中",
    "low":    "低",
}

# 任务分类标签
CATEGORY_COLOR = {
    "work":  "#6366F1",
    "study": "#8B5CF6",
    "life":  "#0EA5E9",
}
CATEGORY_LABEL = {
    "work":  "工作",
    "study": "学习",
    "life":  "生活",
}
CATEGORY_ICON = {
    "work":  ft.Icons.WORK_OUTLINE,
    "study": ft.Icons.SCHOOL_OUTLINED if hasattr(ft.Icons, "SCHOOL_OUTLINED") else ft.Icons.SCHOOL,
    "life":  ft.Icons.HOME_OUTLINED if hasattr(ft.Icons, "HOME_OUTLINED") else ft.Icons.HOME,
}

# 状态
STATUS_LABEL = {
    "all":       "全部",
    "pending":   "进行中",
    "completed": "已完成",
}

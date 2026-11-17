"""展示文案常量：业务语义到中文标签的唯一映射。

迁移前这些字典散落在 ``theme.py`` 与 ``services/task_query.py`` 里且各抄了一份；
现在收口到 models，服务层用它做搜索匹配，视图层用它做胶囊文案 —— 改一处两边同步，
也便于 Agent 静态核对"界面上出现的词"与"搜索能命中的词"是否一致。

颜色 / 图标属于视觉设计，不在这里，见 ``view.design``。
"""
from __future__ import annotations

from models.enums import Category, FilterStatus, Priority, TaskStatus

__all__ = [
    "CATEGORY_LABEL",
    "PRIORITY_LABEL",
    "PRIORITY_SHORT",
    "STATUS_LABEL",
    "TASK_STATUS_LABEL",
]

PRIORITY_LABEL: dict[str, str] = {
    Priority.HIGH.value: "高优先级",
    Priority.MEDIUM.value: "中优先级",
    Priority.LOW.value: "低优先级",
}
PRIORITY_SHORT: dict[str, str] = {
    Priority.HIGH.value: "高",
    Priority.MEDIUM.value: "中",
    Priority.LOW.value: "低",
}
CATEGORY_LABEL: dict[str, str] = {
    Category.WORK.value: "工作",
    Category.STUDY.value: "学习",
    Category.LIFE.value: "生活",
}
TASK_STATUS_LABEL: dict[str, str] = {
    TaskStatus.PENDING.value: "进行中",
    TaskStatus.COMPLETED.value: "已完成",
}
STATUS_LABEL: dict[str, str] = {
    FilterStatus.ALL.value: "全部",
    **TASK_STATUS_LABEL,
}

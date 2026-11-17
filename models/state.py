"""状态与展示模型：全部冻结数据类，任何变化都整体替换。

* :class:`AppState` —— 视图模型持有的唯一真相（原始任务 + 交互状态）。
* :class:`ViewState` —— 由服务查询能力派生出的只读投影，视图只认这一层。
* :class:`TaskDraft` / :class:`TaskChanges` —— 跨越层边界的数据载荷，避免用
  ``**kwargs`` 传业务字段导致调用点与契约漂移。

这里只有"数据长什么样"，没有筛选、排序、校验等规则，也没有任何 UI 类型。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from models.enums import Category, Priority
from models.task import Task

__all__ = ["AppState", "TaskChanges", "TaskDraft", "ViewState"]


@dataclass(frozen=True, slots=True)
class AppState:
    """视图模型的原始状态。"""

    tasks: tuple[Task, ...] = ()
    category: str = "all"
    status: str = "all"
    focus_mode: bool = False
    search_query: str = ""
    search_focus_key: int = 0
    form_open: bool = False
    editing_id: int | None = None
    delete_id: int | None = None


@dataclass(frozen=True, slots=True)
class ViewState:
    """视图可直接渲染的派生状态（由 ViewModel 计算并缓存）。"""

    all_tasks: tuple[Task, ...]
    visible_tasks: tuple[Task, ...]
    completed: int
    total: int
    category: str
    status: str
    focus_mode: bool
    search_query: str
    search_focus_key: int
    form_open: bool
    editing_id: int | None
    editing_task: Task | None
    delete_id: int | None
    delete_target: Task | None


@dataclass(frozen=True, slots=True)
class TaskDraft:
    """新建 / 编辑表单提交上来的字段集合。"""

    title: str
    priority: str = Priority.MEDIUM.value
    category: str = Category.WORK.value
    note: str = ""
    labels: str = ""


class TaskChanges(TypedDict, total=False):
    """局部更新任务时允许出现的字段（编译期可检查）。"""

    title: str
    priority: str
    category: str
    status: str
    labels: str
    note: str
    sort_order: int

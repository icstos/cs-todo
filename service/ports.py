"""服务层对外暴露的抽象接口。

视图模型只依赖这里的 ``Protocol``，因此业务编排可以脱离 SQLite 与 UI 单独测试。
方法名保持与迁移前一致，调用点只需换一层注入。
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from models.state import TaskChanges, TaskDraft
from models.task import Task

__all__ = ["TaskService"]


@runtime_checkable
class TaskService(Protocol):
    """任务业务服务：CRUD 编排 + 查询投影。"""

    def initialize(self) -> None:
        """初始化底层存储（幂等）。"""

    def list_tasks(self) -> list[Task]:
        """返回全部任务，顺序由仓储决定。"""

    def get_task(self, task_id: int) -> Task | None:
        """按 id 取任务。"""

    def create_task(self, draft: TaskDraft) -> Task:
        """校验并新建任务；标题为空抛 :class:`InvalidTaskError`。"""

    def update_task(self, task_id: int, changes: TaskChanges) -> Task | None:
        """校验并局部更新任务。"""

    def toggle_status(self, task_id: int) -> Task | None:
        """翻转完成态。"""

    def delete_task(self, task_id: int) -> bool:
        """删除任务。"""

    def reorder_tasks(self, ordered_ids: list[int]) -> None:
        """持久化任务顺序。"""

    def filter_tasks(
        self,
        tasks: Sequence[Task],
        *,
        category: str = "all",
        status: str = "all",
        focus_mode: bool = False,
        search_query: str = "",
    ) -> list[Task]:
        """按专注模式 / 分类 / 状态 / 关键词筛选，保留既有顺序。"""

    def task_stats(self, tasks: Sequence[Task]) -> tuple[int, int]:
        """返回 ``(已完成数, 总数)``。"""

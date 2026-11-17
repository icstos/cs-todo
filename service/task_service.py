"""任务业务服务：编排仓储调用，承载校验、筛选与统计规则。

不认识 SQLite，也不认识任何控件：构造时只拿到 :class:`~infra.ports.TaskRepository`
抽象。搜索命中的文案来自 :mod:`models.constants` —— 与界面文案同源，避免"看得见却
搜不到"的漂移。
"""
from __future__ import annotations

from collections.abc import Sequence

from infra.ports import TaskRepository
from models.constants import CATEGORY_LABEL, PRIORITY_LABEL, PRIORITY_SHORT
from models.enums import Category, FilterStatus, Priority, TaskStatus
from models.errors import InvalidTaskError
from models.state import TaskChanges, TaskDraft
from models.task import Task
from service.ports import TaskService

__all__ = ["TaskServiceImpl"]

_TEXT_FIELDS = ("title", "note", "labels")


def _matches_search(task: Task, query: str) -> bool:
    """在标题、备注、标签与分类 / 优先级文案中模糊匹配（不区分大小写）。"""
    needle = query.strip().lower()
    if not needle:
        return True
    haystack = " ".join(
        (
            task.title,
            task.note,
            task.labels,
            CATEGORY_LABEL.get(task.category, ""),
            PRIORITY_LABEL.get(task.priority, ""),
            PRIORITY_SHORT.get(task.priority, ""),
        )
    ).lower()
    return needle in haystack


class TaskServiceImpl(TaskService):
    """默认业务实现。无状态，可跨会话复用。"""

    def __init__(self, repository: TaskRepository) -> None:
        self._repo = repository

    def initialize(self) -> None:
        """初始化底层存储。"""
        self._repo.initialize()

    def list_tasks(self) -> list[Task]:
        """返回全部任务。"""
        return self._repo.list()

    def get_task(self, task_id: int) -> Task | None:
        """按 id 取任务。"""
        return self._repo.get(task_id)

    def create_task(self, draft: TaskDraft) -> Task:
        """校验并新建任务。"""
        cleaned = TaskDraft(
            title=draft.title.strip(),
            priority=draft.priority or Priority.MEDIUM.value,
            category=draft.category or Category.WORK.value,
            note=draft.note.strip(),
            labels=draft.labels.strip(),
        )
        if not cleaned.title:
            raise InvalidTaskError("任务标题不能为空")
        return self._repo.create(cleaned)

    def update_task(self, task_id: int, changes: TaskChanges) -> Task | None:
        """校验并局部更新任务。"""
        cleaned: TaskChanges = dict(changes)
        for key in _TEXT_FIELDS:
            value = cleaned.get(key)
            if isinstance(value, str):
                cleaned[key] = value.strip()  # type: ignore[literal-required]
        if "title" in cleaned and not cleaned["title"]:
            raise InvalidTaskError("任务标题不能为空")
        return self._repo.update(task_id, cleaned)

    def toggle_status(self, task_id: int) -> Task | None:
        """翻转完成态。"""
        return self._repo.toggle_status(task_id)

    def delete_task(self, task_id: int) -> bool:
        """删除任务。"""
        return self._repo.delete(task_id)

    def reorder_tasks(self, ordered_ids: list[int]) -> None:
        """持久化任务顺序。"""
        self._repo.reorder(ordered_ids)

    def filter_tasks(
        self,
        tasks: Sequence[Task],
        *,
        category: str = "all",
        status: str = "all",
        focus_mode: bool = False,
        search_query: str = "",
    ) -> list[Task]:
        """按专注模式 / 分类 / 状态 / 关键词筛选，保留用户自定义排序。"""
        if focus_mode:
            filtered = [
                task
                for task in tasks
                if task.priority == Priority.HIGH.value
                and task.status == TaskStatus.PENDING.value
            ]
        else:
            filtered = []
            for task in tasks:
                if category != FilterStatus.ALL.value and task.category != category:
                    continue
                if status != FilterStatus.ALL.value and task.status != status:
                    continue
                filtered.append(task)

        if search_query.strip():
            filtered = [task for task in filtered if _matches_search(task, search_query)]
        return filtered

    def task_stats(self, tasks: Sequence[Task]) -> tuple[int, int]:
        """返回 ``(已完成数, 总数)``。"""
        total = len(tasks)
        completed = sum(1 for task in tasks if task.status == TaskStatus.COMPLETED.value)
        return completed, total

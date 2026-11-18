"""基础设施层对外暴露的抽象接口。

服务层只依赖这里的 ``Protocol``，不认识 SQLite、会话工厂或迁移细节。组合根注入
具体实现，因此换数据库只需替换实现，业务代码一行不动。

接口只描述"能做什么"；返回的一律是 models 层的 :class:`~models.task.Task`。
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from cs_todo.models.state import TaskChanges, TaskDraft
from cs_todo.models.task import Task

__all__ = ["TaskRepository"]


@runtime_checkable
class TaskRepository(Protocol):
    """任务持久化端口：实现内部自行管理事务与连接。"""

    def initialize(self) -> None:
        """建表并补齐历史库缺失的列（幂等）。"""

    def list(self) -> list[Task]:
        """按 ``sort_order`` 升序返回全部任务。"""

    def get(self, task_id: int) -> Task | None:
        """按 id 取任务；不存在返回 ``None``。"""

    def create(self, draft: TaskDraft) -> Task:
        """新建任务并置于列表最前。"""

    def update(self, task_id: int, changes: TaskChanges) -> Task | None:
        """局部更新；任务不存在返回 ``None``。"""

    def toggle_status(self, task_id: int) -> Task | None:
        """翻转完成态（单次数据库往返）。"""

    def delete(self, task_id: int) -> bool:
        """删除任务；任务不存在返回 ``False``。"""

    def reorder(self, ordered_ids: list[int]) -> None:
        """按 id 顺序持久化排序。"""

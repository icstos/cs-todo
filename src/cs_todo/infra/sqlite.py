"""SQLite 实现：把数据库技术细节挡在 :class:`TaskRepository` 之后。

数据库位置与迁移前的 ``<项目根>/cs_todo.db`` 完全一致 —— 迁移不触碰用户数据。
``initialize()`` 同时负责历史库补列（``sort_order`` / ``labels``）与排序回填。
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine, func, select

from cs_todo._paths import database_path
from cs_todo.infra.ports import TaskRepository
from cs_todo.models.enums import TaskStatus
from cs_todo.models.state import TaskChanges, TaskDraft
from cs_todo.models.task import Task

__all__ = ["DB_PATH", "SqliteTaskRepository"]

#: 与迁移前相同：项目根目录下的 cs_todo.db；路径由 _paths 统一出口解析。
DB_PATH: Path = database_path()

_engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False},
)


@contextmanager
def _session_scope() -> Iterator[Session]:
    """事务作用域：自动提交 / 回滚 / 关闭。"""
    session = Session(_engine, expire_on_commit=False)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class SqliteTaskRepository(TaskRepository):
    """基于 SQLModel + SQLite 的仓储实现。"""

    def initialize(self) -> None:
        """建表并对历史库做幂等补列。"""
        SQLModel.metadata.create_all(_engine)
        self._migrate_legacy_columns()

    @staticmethod
    def _migrate_legacy_columns() -> None:
        """老库补 ``sort_order`` / ``labels``，并按创建时间回填排序。"""
        with _engine.connect() as conn:
            columns = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(tasks)")]
            altered = False
            if "sort_order" not in columns:
                conn.exec_driver_sql(
                    "ALTER TABLE tasks ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0"
                )
                altered = True
            if "labels" not in columns:
                conn.exec_driver_sql(
                    "ALTER TABLE tasks ADD COLUMN labels TEXT NOT NULL DEFAULT ''"
                )
                altered = True
            if altered:
                conn.commit()

        with _session_scope() as session:
            rows = session.exec(select(Task).order_by(Task.created_at.desc())).all()
            for index, task in enumerate(rows):
                task.sort_order = index
                session.add(task)

    def list(self) -> list[Task]:
        """按 ``sort_order`` 升序返回全部任务。"""
        with _session_scope() as session:
            rows = session.exec(select(Task).order_by(Task.sort_order.asc())).all()
            # 载入内存后立即关闭 session，避免延迟加载问题。
            return list(rows)

    def get(self, task_id: int) -> Task | None:
        """按 id 取任务。"""
        with _session_scope() as session:
            return session.get(Task, task_id)

    def create(self, draft: TaskDraft) -> Task:
        """新建任务，排到当前最前。"""
        with _session_scope() as session:
            min_order: int | None = session.exec(select(func.min(Task.sort_order))).one()
            sort_order = (min_order - 1) if min_order is not None else 0
            task = Task(
                title=draft.title,
                priority=draft.priority,
                category=draft.category,
                note=draft.note,
                labels=draft.labels,
                sort_order=sort_order,
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    def update(self, task_id: int, changes: TaskChanges) -> Task | None:
        """局部更新任务字段。"""
        with _session_scope() as session:
            task = session.get(Task, task_id)
            if task is None:
                return None
            for key, value in changes.items():
                if hasattr(task, key) and value is not None:
                    setattr(task, key, value)
            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    def toggle_status(self, task_id: int) -> Task | None:
        """翻转完成态。"""
        with _session_scope() as session:
            task = session.get(Task, task_id)
            if task is None:
                return None
            task.status = (
                TaskStatus.COMPLETED.value
                if task.status == TaskStatus.PENDING.value
                else TaskStatus.PENDING.value
            )
            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            # 不能在这里 refresh()：它会用库里的旧值覆盖刚改的 status，
            # 而提交发生在 session_scope 退出时 —— 结果就是勾选永远不落库。
            return task

    def delete(self, task_id: int) -> bool:
        """删除任务。"""
        with _session_scope() as session:
            task = session.get(Task, task_id)
            if task is None:
                return False
            session.delete(task)
            return True

    def reorder(self, ordered_ids: list[int]) -> None:
        """按 id 列表持久化排序。"""
        with _session_scope() as session:
            id_to_order = {task_id: index for index, task_id in enumerate(ordered_ids)}
            rows = session.exec(select(Task).where(Task.id.in_(ordered_ids))).all()
            for task in rows:
                task.sort_order = id_to_order[task.id]
                task.updated_at = datetime.now(timezone.utc)
                session.add(task)

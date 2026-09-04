"""数据访问层：封装任务 CRUD，保持业务逻辑与 UI 解耦。"""
from datetime import datetime
from typing import Optional

from sqlmodel import func, select

from database import session_scope
from models import Task


def list_tasks() -> list[Task]:
    """按 sort_order 升序返回全部任务。"""
    with session_scope() as s:
        rows = s.exec(select(Task).order_by(Task.sort_order.asc())).all()
        # 载入到内存后立即关闭 session，避免延迟加载问题
        return list(rows)


def get_task(task_id: int) -> Optional[Task]:
    with session_scope() as s:
        return s.get(Task, task_id)


def create_task(
    title: str,
    priority: str,
    category: str,
    note: str = "",
    labels: str = "",
) -> Task:
    with session_scope() as s:
        min_order = s.exec(select(func.min(Task.sort_order))).one()
        sort_order = (min_order - 1) if min_order is not None else 0
        task = Task(
            title=title.strip(),
            priority=priority,
            category=category,
            note=note.strip(),
            labels=labels.strip(),
            sort_order=sort_order,
        )
        s.add(task)
        s.commit()
        s.refresh(task)
        return task


def update_task(task_id: int, **fields) -> Optional[Task]:
    with session_scope() as s:
        task = s.get(Task, task_id)
        if task is None:
            return None
        for key, value in fields.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)
        task.updated_at = datetime.utcnow()
        s.add(task)
        s.commit()
        s.refresh(task)
        return task


def toggle_status(task_id: int) -> Optional[Task]:
    """切换任务完成状态（单次数据库往返）。"""
    with session_scope() as s:
        task = s.get(Task, task_id)
        if task is None:
            return None
        task.status = "completed" if task.status == "pending" else "pending"
        task.updated_at = datetime.utcnow()
        s.add(task)
        s.refresh(task)
        return task


def delete_task(task_id: int) -> bool:
    with session_scope() as s:
        task = s.get(Task, task_id)
        if task is None:
            return False
        s.delete(task)
        return True


def reorder_tasks(ordered_ids: list[int]) -> None:
    """按 id 列表持久化任务排序。"""
    with session_scope() as s:
        id_to_order = {task_id: idx for idx, task_id in enumerate(ordered_ids)}
        rows = s.exec(select(Task).where(Task.id.in_(ordered_ids))).all()
        for task in rows:
            task.sort_order = id_to_order[task.id]
            task.updated_at = datetime.utcnow()
            s.add(task)

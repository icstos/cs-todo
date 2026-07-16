"""数据库引擎与会话工厂：本地 SQLite。"""
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

DB_PATH = Path(__file__).parent / "cs_todo.db"
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """创建所有数据表（幂等）。"""
    # 确保 models 已被导入以注册表元数据
    import models  # noqa: F401

    SQLModel.metadata.create_all(engine)
    _migrate_sort_order()


def _migrate_sort_order() -> None:
    """为旧库补充 sort_order 列，并按创建时间初始化顺序。"""
    from sqlmodel import select

    from models import Task

    with engine.connect() as conn:
        cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(tasks)")]
        if "sort_order" in cols:
            return
        conn.exec_driver_sql(
            "ALTER TABLE tasks ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0"
        )
        conn.commit()

    with session_scope() as s:
        rows = s.exec(select(Task).order_by(Task.created_at.desc())).all()
        for i, task in enumerate(rows):
            task.sort_order = i
            s.add(task)


def get_session() -> Session:
    return Session(engine, expire_on_commit=False)


@contextmanager
def session_scope() -> Iterator[Session]:
    """事务作用域：自动提交/回滚/关闭。"""
    session = Session(engine, expire_on_commit=False)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

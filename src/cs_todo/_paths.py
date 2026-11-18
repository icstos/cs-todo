"""项目路径出口：数据文件与资源目录只在这里定位。

src 布局把包下移了两层，任何「向上数 N 层」的硬编码都会在迁移后静默指错位置。
这里改为向上查找项目根标记（``pyproject.toml`` / ``.git``），找不到时回退到
``src/<project>/_paths.py`` 的上三级 —— 即项目根。
"""
from __future__ import annotations

from pathlib import Path

__all__ = ["assets_dir", "database_path", "project_root"]

#: 数据库文件名保持与迁移前一致，用户数据原地不动。
_DB_NAME = "cs_todo.db"
_ASSETS_NAME = "assets"
_ROOT_MARKERS = ("pyproject.toml", ".git")


def project_root() -> Path:
    """返回项目根目录；优先找标记文件，找不到时按 src 布局回退。"""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if any((parent / marker).exists() for marker in _ROOT_MARKERS):
            return parent
    return here.parents[2]  # src/<project>/_paths.py → 项目根


def database_path() -> Path:
    """返回 SQLite 数据库路径（项目根下的 ``cs_todo.db``）。"""
    return project_root() / _DB_NAME


def assets_dir() -> Path:
    """返回资源目录；目录可能不存在，由调用方决定如何降级。"""
    return project_root() / _ASSETS_NAME

"""基础设施层统一出口：只暴露端口，具体实现留给组合根注入。"""
from __future__ import annotations

from cs_todo.infra.ports import TaskRepository

__all__ = ["TaskRepository"]

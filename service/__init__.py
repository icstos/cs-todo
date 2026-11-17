"""服务层统一出口：只暴露端口，不暴露具体实现。

:class:`~models.errors.InvalidTaskError` 属于领域契约，请从 ``models`` 导入。
"""
from __future__ import annotations

from service.ports import TaskService

__all__ = ["TaskService"]

"""视图模型层统一出口：只暴露抽象契约与纯 Python 基类。"""
from __future__ import annotations

from viewmodel.base import ViewModel
from viewmodel.ports import TodoViewModel

__all__ = ["TodoViewModel", "ViewModel"]

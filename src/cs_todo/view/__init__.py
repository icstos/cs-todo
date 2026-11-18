"""视图层统一出口：根组件与设计令牌。控件只在 view 包内部互相引用。"""
from __future__ import annotations

from cs_todo.view.app import App

__all__ = ["App"]

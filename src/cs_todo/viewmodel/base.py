"""视图模型基座：不可变状态、一次性通知、单向重渲染订阅。

刻意保持"纯 Python"：这里没有控件、没有 ``ui`` 依赖，只有一个回调槽位（**不是事件
总线**）。视图在挂载时 ``bind`` 一个回调，视图模型每次改状态后调用它；回调只把
``revision`` 写进视图的 ``use_state``，于是 ``UI = f(state)`` 自动成立。

三条约定：

1. ``state`` 是冻结数据类，变化整体替换；视图永远只读快照。
2. ``notice`` 带单调递增序号，且由视图模型自己判定是否已播报 —— 组件重新挂载不会
   把旧提示重放一遍。
3. 所有写操作以 ``_flush()`` 收尾，一次事件只发一次变更信号。
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import Any, cast

from cs_todo.models.enums import ToastTone
from cs_todo.models.events import Notice

__all__ = ["ViewModel"]


class ViewModel[S]:
    """持有不可变状态 ``S`` 的纯 Python 视图模型。"""

    def __init__(self, state: S) -> None:
        self._state = state
        self._notice: Notice | None = None
        self._notice_seq = 0
        self._announced_seq = 0
        self._revision = 0
        self._listener: Callable[[], None] | None = None

    @property
    def state(self) -> S:
        """当前状态快照（只读视图）。"""
        return self._state

    @property
    def revision(self) -> int:
        """单调递增的状态版本号，供视图做变更判定。"""
        return self._revision

    @property
    def notice(self) -> Notice | None:
        """最近一条提示；是否已播报由 :meth:`claim_notice` 决定。"""
        return self._notice

    def bind(self, listener: Callable[[], None] | None) -> None:
        """绑定唯一视图订阅者；传 ``None`` 解绑。"""
        self._listener = listener

    def claim_notice(self) -> Notice | None:
        """取走尚未播报的提示，已播过返回 ``None``。

        判定权放在视图模型：它的生命期跟业务状态一致，不随组件卸载归零。
        """
        notice = self._notice
        if notice is None or notice.seq <= self._announced_seq:
            return None
        self._announced_seq = notice.seq
        return notice

    def _set(self, **changes: object) -> None:
        """按字段替换状态（字段必须存在，属于开发期契约）。"""
        self._state = replace(cast(Any, self._state), **changes)

    def _notify(self, message: str, tone: ToastTone = ToastTone.INFO) -> None:
        """挂一条待播报的一次性提示。"""
        self._notice_seq += 1
        self._notice = Notice(self._notice_seq, message, tone)

    def _flush(self) -> None:
        """发布一次状态变更；视图据此重渲染。"""
        self._revision += 1
        if self._listener is not None:
            self._listener()

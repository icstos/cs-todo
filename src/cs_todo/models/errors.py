"""领域错误：业务上不成立的提交，不含 UI 语气与文案。

放在模型层是为了让服务与视图模型都能依赖同一份契约，而不必让上层认识服务的具体
实现模块。视图模型据此决定播报"请填写任务标题"，服务本身不产生界面文案。
"""
from __future__ import annotations

__all__ = ["InvalidTaskError"]


class InvalidTaskError(ValueError):
    """提交的任务数据不满足业务约束（如标题为空）。"""

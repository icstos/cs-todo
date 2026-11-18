"""待办视图模型：持有 UI 状态，编排服务调用，产出只读展示状态。

这里是"界面为什么会变成这样"的唯一答案：筛选结果、统计、对话框目标、空态判定、
提示文案全部由状态派生。视图不保存第二份真相，也不判断业务规则。

乐观更新与迁移前一致：勾选 / 删除 / 拖拽先改本地快照让界面立即响应，失败时再整表
重载并给出提示。用户可见文案逐字保留。
"""
from __future__ import annotations

from dataclasses import replace

from cs_todo.models.enums import TaskStatus, ToastTone
from cs_todo.models.errors import InvalidTaskError
from cs_todo.models.events import Shortcut
from cs_todo.models.state import AppState, TaskChanges, TaskDraft, ViewState
from cs_todo.models.task import Task
from cs_todo.service.ports import TaskService
from cs_todo.viewmodel.base import ViewModel

__all__ = ["TodoViewModelImpl"]


class TodoViewModelImpl(ViewModel[AppState]):
    """具体视图模型。只依赖服务端口，不依赖任何 UI 类型。"""

    def __init__(self, service: TaskService) -> None:
        super().__init__(AppState())
        self._service = service
        self._view_cache: ViewState | None = None

    # ------------------------------------------------------------------ 派生状态
    @property
    def view(self) -> ViewState:
        """当前展示状态；只在状态变化后重算并缓存。"""
        if self._view_cache is None:
            state = self._state
            all_tasks = list(state.tasks)
            visible = tuple(
                self._service.filter_tasks(
                    all_tasks,
                    category=state.category,
                    status=state.status,
                    focus_mode=state.focus_mode,
                    search_query=state.search_query,
                )
            )
            completed, total = self._service.task_stats(all_tasks)
            editing = (
                self._find(state.editing_id) if state.editing_id is not None else None
            )
            deleting = self._find(state.delete_id) if state.delete_id is not None else None
            self._view_cache = ViewState(
                all_tasks=state.tasks,
                visible_tasks=visible,
                completed=completed,
                total=total,
                category=state.category,
                status=state.status,
                focus_mode=state.focus_mode,
                search_query=state.search_query,
                search_focus_key=state.search_focus_key,
                form_open=state.form_open,
                editing_id=state.editing_id,
                editing_task=editing,
                delete_id=state.delete_id,
                delete_target=deleting,
            )
        return self._view_cache

    def _find(self, task_id: int) -> Task | None:
        """从内存快照找任务，避免渲染期再打一次数据库。"""
        return next((task for task in self._state.tasks if task.id == task_id), None)

    def _flush(self) -> None:
        """状态变更后作废派生缓存并通知视图。"""
        self._view_cache = None
        super()._flush()

    def _reload_tasks(self) -> None:
        """从服务重新读取任务（失败回滚路径）。"""
        self._state = replace(self._state, tasks=tuple(self._service.list_tasks()))

    # ------------------------------------------------------------------ 生命周期
    def bootstrap(self) -> None:
        """首次装载任务；在视图挂载前调用，首帧即为最终数据。"""
        self._set(tasks=tuple(self._service.list_tasks()))
        self._flush()

    # ------------------------------------------------------------------ 筛选条件
    def set_category(self, value: str) -> None:
        """切换分类筛选。"""
        if value != self._state.category:
            self._set(category=value)
            self._flush()

    def set_status(self, value: str) -> None:
        """切换状态筛选。"""
        if value != self._state.status:
            self._set(status=value)
            self._flush()

    def set_search_query(self, value: str) -> None:
        """更新搜索关键词。"""
        if value != self._state.search_query:
            self._set(search_query=value)
            self._flush()

    def focus_search(self) -> None:
        """请求搜索框获得焦点（Ctrl+F），用序号驱动视图重建输入框。"""
        self._set(search_focus_key=self._state.search_focus_key + 1)
        self._flush()

    def toggle_focus(self) -> None:
        """开关专注模式。"""
        self._set(focus_mode=not self._state.focus_mode)
        self._flush()

    # ------------------------------------------------------------------ 表单
    def open_add(self) -> None:
        """打开新建表单。"""
        self._set(form_open=True, editing_id=None)
        self._flush()

    def open_edit(self, task_id: int) -> None:
        """打开编辑表单。"""
        if self._find(task_id) is None:
            return
        self._set(form_open=True, editing_id=task_id)
        self._flush()

    def close_form(self) -> None:
        """关闭表单并清除编辑目标。"""
        if not self._state.form_open and self._state.editing_id is None:
            return
        self._set(form_open=False, editing_id=None)
        self._flush()

    def save_form(self, draft: TaskDraft) -> None:
        """提交表单：校验 → 写入 → 成功提示 → 关闭并刷新。"""
        editing_id = self._state.editing_id
        try:
            if editing_id is not None:
                changes: TaskChanges = {
                    "title": draft.title,
                    "priority": draft.priority,
                    "category": draft.category,
                    "note": draft.note,
                    "labels": draft.labels,
                }
                self._service.update_task(editing_id, changes)
                message = "任务已更新"
            else:
                self._service.create_task(draft)
                message = "任务已创建"
        except InvalidTaskError:
            self._notify("请填写任务标题", ToastTone.INFO)
            self._flush()
            return
        except Exception:
            self._notify("保存失败，请重试", ToastTone.ERROR)
            self._flush()
            return

        self._notify(message, ToastTone.SUCCESS)
        self._state = replace(self._state, form_open=False, editing_id=None)
        self._reload_tasks()
        self._flush()

    # ------------------------------------------------------------------ 删除
    def request_delete(self, task_id: int) -> None:
        """请求删除：只打开确认框，不写库。"""
        if self._find(task_id) is None:
            return
        self._set(delete_id=task_id)
        self._flush()

    def confirm_delete(self) -> None:
        """确认删除：先乐观移除，失败时回滚并提示。"""
        task_id = self._state.delete_id
        if task_id is None:
            return
        removed = self._find(task_id)
        self._state = replace(
            self._state,
            tasks=tuple(task for task in self._state.tasks if task.id != task_id),
            delete_id=None,
        )
        try:
            if not self._service.delete_task(task_id):
                self._reload_tasks()
                self._notify("删除失败，请重试", ToastTone.ERROR)
                self._flush()
                return
        except Exception:
            self._reload_tasks()
            self._notify("删除失败，请重试", ToastTone.ERROR)
            self._flush()
            return
        title = removed.title if removed else "任务"
        self._notify(f"已删除「{title}」", ToastTone.SUCCESS)
        self._flush()

    def cancel_delete(self) -> None:
        """取消删除。"""
        if self._state.delete_id is None:
            return
        self._set(delete_id=None)
        self._flush()

    # ------------------------------------------------------------------ 列表操作
    def toggle_task(self, task_id: int) -> None:
        """翻转完成态：乐观更新，失败回滚。"""
        target = self._find(task_id)
        if target is None:
            return
        next_status = (
            TaskStatus.COMPLETED.value
            if target.status == TaskStatus.PENDING.value
            else TaskStatus.PENDING.value
        )
        self._set(
            tasks=tuple(
                task.model_copy(update={"status": next_status})
                if task.id == task_id
                else task
                for task in self._state.tasks
            )
        )
        try:
            self._service.toggle_status(task_id)
        except Exception:
            self._reload_tasks()
            self._notify("更新失败，请重试", ToastTone.ERROR)
        self._flush()

    def reorder(self, old_index: int, new_index: int) -> None:
        """拖拽排序：把"可见区的新顺序"映射回完整列表后持久化。"""
        visible = list(self.view.visible_tasks)
        if (
            old_index == new_index
            or old_index < 0
            or new_index < 0
            or old_index >= len(visible)
            or new_index >= len(visible)
        ):
            return

        moved = visible.pop(old_index)
        visible.insert(new_index, moved)

        full = sorted(self._state.tasks, key=lambda task: task.sort_order)
        visible_ids = {task.id for task in visible}
        visible_slots = [
            index for index, task in enumerate(full) if task.id in visible_ids
        ]
        merged = list(full)
        for slot, task in zip(visible_slots, visible):
            merged[slot] = task

        self._set(
            tasks=tuple(
                task.model_copy(update={"sort_order": index})
                for index, task in enumerate(merged)
            )
        )
        try:
            self._service.reorder_tasks([task.id for task in merged])
        except Exception:
            self._reload_tasks()
            self._notify("排序保存失败，请重试", ToastTone.ERROR)
        self._flush()

    # ------------------------------------------------------------------ 快捷键
    def handle_escape(self) -> None:
        """Esc 逐层退出：表单 → 确认框 → 清空搜索。"""
        state = self._state
        if state.form_open:
            self.close_form()
        elif state.delete_id is not None:
            self.cancel_delete()
        elif state.search_query.strip():
            self.set_search_query("")

    def on_shortcut(self, shortcut: Shortcut) -> None:
        """处理视图翻译好的键盘手势。"""
        if shortcut.ctrl and shortcut.key == "N":
            self.open_add()
        elif shortcut.ctrl and shortcut.key == "F":
            self.focus_search()
        elif shortcut.key == "Escape":
            self.handle_escape()

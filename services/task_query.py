"""任务查询与排序：集中处理筛选逻辑。"""
from models import Task

_CATEGORY_LABEL = {"work": "工作", "study": "学习", "life": "生活"}
_PRIORITY_LABEL = {"high": "高优先级", "medium": "中优先级", "low": "低优先级"}
_PRIORITY_SHORT = {"high": "高", "medium": "中", "low": "低"}


def _matches_search(task: Task, query: str) -> bool:
    """在标题、备注、分类与优先级文案中模糊匹配（不区分大小写）。"""
    q = query.strip().lower()
    if not q:
        return True

    haystack = " ".join(
        [
            task.title,
            task.note,
            _CATEGORY_LABEL.get(task.category, ""),
            _PRIORITY_LABEL.get(task.priority, ""),
            _PRIORITY_SHORT.get(task.priority, ""),
        ]
    ).lower()
    return q in haystack


def filter_tasks(
    tasks: list[Task],
    *,
    category: str = "all",
    status: str = "all",
    focus_mode: bool = False,
    search_query: str = "",
) -> list[Task]:
    """按专注模式 / 分类 / 状态 / 关键词筛选，保留用户自定义排序。"""
    if focus_mode:
        filtered = [t for t in tasks if t.priority == "high" and t.status == "pending"]
    else:
        filtered = []
        for t in tasks:
            if category != "all" and t.category != category:
                continue
            if status != "all" and t.status != status:
                continue
            filtered.append(t)

    if search_query.strip():
        filtered = [t for t in filtered if _matches_search(t, search_query)]

    return filtered


def task_stats(tasks: list[Task]) -> tuple[int, int]:
    """返回 (已完成数, 总数)。"""
    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == "completed")
    return completed, total

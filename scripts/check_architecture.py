"""分层架构守卫：用 AST 静态校验单向依赖与全量类型注解。

约束（与 cs-todo 的 MVVM 设计一一对应）::

    view ──▶ viewmodel ──▶ service ──▶ infra
       ╲         │             │          │
        ╲        ▼             ▼          ▼
         ╲────────────── models ──────────┘

* 只允许箭头方向的依赖，禁止反向与跨层；
* 高层只依赖**抽象接口**：service 只碰 ``infra.ports``，viewmodel 只碰
  ``service.ports``，view 只碰 ``viewmodel.ports``；
* models / infra / service / viewmodel 不得出现 UI 依赖；view 的 UI 依赖收敛到
  ``ui``，不直接 import flet；
* 禁止用动态 import 绕过检查；所有函数都必须有完整类型注解。

源码位于 ``src/cs_todo/<layer>/``：层内模块以 ``cs_todo.`` 开头，包名 ``cs_todo``
本身不被当成第三方依赖；组合根 ``main.py`` 只做 sys.path 引导与启动。

用法::

    python scripts/check_architecture.py

退出码 0 表示全部通过，1 表示有问题（问题逐条打印，可复算）。
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "cs_todo"
PROJECT_ROOT = ROOT / "src" / PROJECT
LAYERS: tuple[str, ...] = ("models", "infra", "service", "viewmodel", "view")

#: 每层允许引用的包内前缀（含同层互引）。端口例外是"高层依赖抽象"的硬边界。
#: ``_paths`` 是无业务逻辑的项目级路径出口，所有层都可引用（与 models 同类）。
ALLOWED_PREFIXES: dict[str, tuple[str, ...]] = {
    "models": ("models", "_paths"),
    "infra": ("models", "infra", "_paths"),
    "service": ("models", "service", "infra.ports", "_paths"),
    "viewmodel": ("models", "viewmodel", "service.ports", "_paths"),
    "view": ("models", "view", "viewmodel.ports", "_paths"),
}

#: 每层允许的第三方顶层包；标准库不限。
ALLOWED_THIRD_PARTY: dict[str, tuple[str, ...]] = {
    "models": ("sqlmodel",),
    "infra": ("sqlmodel",),
    "service": (),
    "viewmodel": (),
    "view": ("ui",),
}

STDLIB = set(sys.stdlib_module_names)
DYNAMIC_IMPORT_NAMES = frozenset({"__import__", "import_module"})


def layer_of(path: Path) -> str | None:
    """相对 ``src/cs_todo`` 的路径 → 层名；不在任何层里返回 ``None``。"""
    try:
        parts = path.relative_to(PROJECT_ROOT).parts
    except ValueError:
        return None
    return parts[0] if parts and parts[0] in LAYERS else None


def module_name(path: Path) -> str:
    """文件路径 → 点分模块名；包外文件（如根 main.py）返回文件名。"""
    try:
        rel = path.relative_to(PROJECT_ROOT).with_suffix("").parts
    except ValueError:
        return path.stem
    return ".".join((PROJECT, *rel))


def resolve_from(node: ast.ImportFrom, package_parts: list[str]) -> str | None:
    """解析 ``ImportFrom`` 为绝对点分名（同时处理相对导入）。"""
    if node.level == 0:
        return node.module
    # 相对导入：level=1 保留当前包，level=2 再退一层，依此类推。
    base = package_parts[: len(package_parts) - (node.level - 1)]
    return ".".join([*base, node.module]) if node.module else ".".join(base)


def analyse(path: Path) -> tuple[set[str], set[str], list[str], list[str]]:
    """返回 ``(包内引用, 第三方包, 动态导入问题, 注解问题)``。"""
    source = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(path))
    package_parts = module_name(path).split(".")
    if package_parts[-1] != "__init__":
        package_parts.pop()

    internal: set[str] = set()
    third_party: set[str] = set()
    dynamic: list[str] = []
    annotations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root == PROJECT or root in LAYERS:
                    internal.add(alias.name)
                elif root not in STDLIB:
                    third_party.add(root)
        elif isinstance(node, ast.ImportFrom):
            resolved = resolve_from(node, package_parts)
            if resolved is None:
                continue
            root = resolved.split(".")[0]
            if root == PROJECT or root in LAYERS:
                internal.add(resolved)
            elif root not in STDLIB:
                third_party.add(root)
        elif isinstance(node, ast.Call):
            func = node.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
            if name in DYNAMIC_IMPORT_NAMES:
                dynamic.append(f"L{node.lineno}: 动态导入 {name}()")

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            missing = [
                arg.arg
                for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
                if arg.arg not in ("self", "cls") and arg.annotation is None
            ]
            if node.args.vararg and node.args.vararg.annotation is None:
                missing.append(f"*{node.args.vararg.arg}")
            if node.args.kwarg and node.args.kwarg.annotation is None:
                missing.append(f"**{node.args.kwarg.arg}")
            if node.returns is None:
                missing.append("返回类型")
            if missing:
                annotations.append(
                    f"L{node.lineno}: {node.name}() 缺少注解 {', '.join(missing)}"
                )
    return internal, third_party, dynamic, annotations


def uses_ui_name(path: Path) -> list[str]:
    """查找 ``ui.*`` / ``flet.*`` 形式的直接控件访问（不是 import）。"""
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id in ("ui", "ft", "flet"):
                hits.append(f"L{node.lineno}: {node.value.id}.{node.attr}")
    return hits


def check() -> list[str]:
    """执行全部检查，返回问题列表（空列表表示通过）。"""
    problems: list[str] = []
    layer_files: dict[str, list[Path]] = {layer: [] for layer in LAYERS}
    for path in sorted(ROOT.rglob("*.py")):
        if "__pycache__" in path.parts or ROOT / "scripts" in path.parents:
            continue
        layer = layer_of(path)
        if layer is not None:
            layer_files[layer].append(path)

    for layer, paths in layer_files.items():
        if not paths:
            problems.append(f"层 {layer} 没有任何源文件")

    for layer, paths in layer_files.items():
        allowed = ALLOWED_PREFIXES[layer]
        allowed_third = set(ALLOWED_THIRD_PARTY[layer])
        for path in paths:
            internal, third_party, dynamic, annotations = analyse(path)
            rel = path.relative_to(ROOT).as_posix()

            for target in sorted(internal):
                normalized = target.removeprefix(f"{PROJECT}.")
                if not any(
                    normalized == prefix or normalized.startswith(f"{prefix}.")
                    for prefix in allowed
                ):
                    problems.append(
                        f"{rel}: {layer} 层不得依赖 {target}（允许：{', '.join(allowed)}）"
                    )
            offenders = sorted(third_party - allowed_third)
            if offenders:
                problems.append(
                    f"{rel}: {layer} 层不得依赖第三方 {offenders}"
                    f"（允许：{list(allowed_third)}）"
                )
            problems.extend(f"{rel}: {item}" for item in dynamic)
            problems.extend(f"{rel}: {item}" for item in annotations)

            if layer != "view":
                hits = uses_ui_name(path)
                if hits:
                    problems.append(f"{rel}: {layer} 层不得访问 UI 名称 {hits}")

    # 组合根参与注解检查，但不参与依赖检查。
    main_py = ROOT / "main.py"
    if main_py.exists():
        _, _, dynamic, annotations = analyse(main_py)
        problems.extend(f"main.py: {item}" for item in (*dynamic, *annotations))
    return problems


def main() -> int:
    """打印检查结果并返回进程退出码。"""
    problems = check()
    if problems:
        print(f"架构检查失败：{len(problems)} 项")
        for item in problems:
            print(" -", item)
        return 1
    module_count = sum(
        1
        for path in ROOT.rglob("*.py")
        if "__pycache__" not in path.parts and ROOT / "scripts" not in path.parents
    )
    print(f"架构检查通过：5 层 / {module_count} 个模块；依赖方向、抽象边界、")
    print("无动态导入、无直接 flet 依赖、全量类型注解均符合要求。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

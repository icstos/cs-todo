"""项目入口：把 ``src`` 放进路径后启动应用。

src 布局必需：隔离打包环境（serious_python / PyInstaller 等）不会执行
``pip install -e .``，包被编译到 ``<app>/src/cs_todo/``，而运行时 ``sys.path``
只有 ``<app>/`` 根、不含 ``src``。这段同时覆盖开发态与打包态；删掉即打包后
``ModuleNotFoundError``。用 ``__file__`` 而不是 cwd，因为打包后 cwd 不确定。
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path and (_SRC / "cs_todo").exists():
    sys.path.insert(0, str(_SRC))

from cs_todo.bootstrap import run  # noqa: E402

if __name__ == "__main__":
    run()

from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4


def make_runtime_test_dir(label: str) -> Path:
    root = Path("data/test-runtime")
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{label}-{uuid4().hex[:8]}"
    path.mkdir()
    return path


def remove_runtime_test_dir(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)

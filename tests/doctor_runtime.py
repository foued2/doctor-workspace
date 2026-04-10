from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Callable, Mapping


DOCTOR_TEST_MODE_ENV = "LEETCODE_DOCTOR_FILE_MODE"
DOCTOR_TEST_MODE_VALUE = "run-tests"
DOCTOR_REQUIRED_MARKERS = ("TODO WORKFLOW", "TODO #2", "TODO #3", "TODO #4")


def _resolve_project_root(file_path: Path) -> Path:
    for candidate in (file_path.parent, *file_path.parents):
        if (
            (candidate / "leetcode-tools" / "leetcode_doctor.py").exists()
            and (candidate / "execution_controller.py").exists()
        ):
            return candidate
    raise FileNotFoundError(f"Could not locate project root for {file_path}")


def is_doctor_managed_file(file_path: str | Path) -> bool:
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return False
    content = path.read_text(encoding="utf-8")
    return all(marker in content for marker in DOCTOR_REQUIRED_MARKERS)


def run_doctor_or_embedded_tests(
    file_path: str | Path,
    run_embedded_tests: Callable[[], None],
    *,
    env: Mapping[str, str] | None = None,
) -> int:
    path = Path(file_path).resolve()
    environment = env if env is not None else os.environ

    if environment.get(DOCTOR_TEST_MODE_ENV) == DOCTOR_TEST_MODE_VALUE:
        run_embedded_tests()
        return 0

    if not is_doctor_managed_file(path):
        run_embedded_tests()
        return 0

    project_root = _resolve_project_root(path)
    doctor_script = project_root / "leetcode-tools" / "leetcode_doctor.py"
    result = subprocess.run(
        [sys.executable, str(doctor_script), str(path)],
        cwd=str(project_root),
        check=False,
    )
    return result.returncode

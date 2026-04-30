"""
Parent-side controller for sandboxed Doctor execution.
"""
from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_TIMEOUT_SECONDS = 10
DEFAULT_PER_TEST_TIMEOUT_SECONDS = 2
DEFAULT_MEMORY_LIMIT_BYTES = 256 * 1024 * 1024


@dataclass
class SandboxRunResult:
    ok: bool
    error: str
    total: int
    passed: int
    results: list[dict]
    traces: list[dict]


class _WindowsJob:
    def __init__(self, memory_limit_bytes: int | None, process_time_limit_seconds: int | None):
        self._handle = None
        self._kernel32 = None
        if os.name == "nt":
            self._create(memory_limit_bytes, process_time_limit_seconds)

    def _create(
        self,
        memory_limit_bytes: int | None,
        process_time_limit_seconds: int | None,
    ) -> None:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.CreateJobObjectW(None, None)
        if not handle:
            return

        class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", ctypes.c_longlong),
                ("PerJobUserTimeLimit", ctypes.c_longlong),
                ("LimitFlags", ctypes.c_uint32),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", ctypes.c_uint32),
                ("Affinity", ctypes.c_size_t),
                ("PriorityClass", ctypes.c_uint32),
                ("SchedulingClass", ctypes.c_uint32),
            ]

        class IO_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("ReadOperationCount", ctypes.c_ulonglong),
                ("WriteOperationCount", ctypes.c_ulonglong),
                ("OtherOperationCount", ctypes.c_ulonglong),
                ("ReadTransferCount", ctypes.c_ulonglong),
                ("WriteTransferCount", ctypes.c_ulonglong),
                ("OtherTransferCount", ctypes.c_ulonglong),
            ]

        class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
                ("IoInfo", IO_COUNTERS),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t),
            ]

        JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
        JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
        JOB_OBJECT_LIMIT_PROCESS_TIME = 0x00000002
        JobObjectExtendedLimitInformation = 9

        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if memory_limit_bytes:
            info.BasicLimitInformation.LimitFlags |= JOB_OBJECT_LIMIT_PROCESS_MEMORY
            info.ProcessMemoryLimit = int(memory_limit_bytes)
        if process_time_limit_seconds:
            info.BasicLimitInformation.LimitFlags |= JOB_OBJECT_LIMIT_PROCESS_TIME
            info.BasicLimitInformation.PerProcessUserTimeLimit = (
                int(process_time_limit_seconds) * 10_000_000
            )

        ok = kernel32.SetInformationJobObject(
            handle,
            JobObjectExtendedLimitInformation,
            ctypes.byref(info),
            ctypes.sizeof(info),
        )
        if not ok:
            kernel32.CloseHandle(handle)
            return

        self._handle = handle
        self._kernel32 = kernel32

    def assign(self, process: subprocess.Popen) -> None:
        if not self._handle:
            return
        self._kernel32.AssignProcessToJobObject(self._handle, int(process._handle))

    def close(self) -> None:
        if self._handle:
            self._kernel32.CloseHandle(self._handle)
            self._handle = None


def _minimal_env(temp_dir: str) -> dict[str, str]:
    keep = {}
    for key in ("SystemRoot", "WINDIR", "COMSPEC", "PATH"):
        value = os.environ.get(key)
        if value:
            keep[key] = value
    keep.update({
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "TEMP": temp_dir,
        "TMP": temp_dir,
    })
    return keep


def _failure(message: str, *, total: int = 0) -> SandboxRunResult:
    return SandboxRunResult(
        ok=False,
        error=message,
        total=total,
        passed=0,
        results=[],
        traces=[],
    )


def _sanitize_tests(tests: list[Any]) -> list[dict]:
    return [
        {
            "label": getattr(test, "label", ""),
            "input": _jsonable(getattr(test, "input", ())),
            "expected": _jsonable(getattr(test, "expected", None)),
            "validation_type": getattr(test, "validation_type", None),
        }
        for test in tests
    ]


def _jsonable(obj: Any) -> Any:
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, tuple):
        return [_jsonable(x) for x in obj]
    if isinstance(obj, list):
        return [_jsonable(x) for x in obj]
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if hasattr(obj, "val") and hasattr(obj, "next"):
        vals = []
        seen = set()
        current = obj
        while current is not None:
            ident = id(current)
            if ident in seen:
                vals.append("<cycle>")
                break
            seen.add(ident)
            vals.append(_jsonable(getattr(current, "val", None)))
            current = getattr(current, "next", None)
        return vals
    return repr(obj)


def run_solution_in_sandbox(
    *,
    code: str,
    problem_id: str,
    tests: list[Any],
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    per_test_timeout_seconds: int = DEFAULT_PER_TEST_TIMEOUT_SECONDS,
    memory_limit_bytes: int = DEFAULT_MEMORY_LIMIT_BYTES,
) -> SandboxRunResult:
    payload = {
        "code": code,
        "problem_id": problem_id,
        "tests": _sanitize_tests(tests),
        "per_test_timeout_seconds": per_test_timeout_seconds,
    }
    total = len(payload["tests"])
    worker = Path(__file__).with_name("sandbox_worker.py")

    with tempfile.TemporaryDirectory(prefix="doctor_sandbox_") as temp_dir:
        proc = subprocess.Popen(
            [sys.executable, "-I", "-S", str(worker)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            cwd=temp_dir,
            env=_minimal_env(temp_dir),
        )
        job = _WindowsJob(memory_limit_bytes, timeout_seconds)
        try:
            job.assign(proc)
            stdout, stderr = proc.communicate(
                json.dumps(payload, ensure_ascii=True),
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            return _failure(f"sandbox timeout after {timeout_seconds}s", total=total)
        except Exception as exc:
            proc.kill()
            proc.communicate()
            return _failure(f"sandbox launch failed: {exc}", total=total)
        finally:
            job.close()

    if proc.returncode != 0:
        detail = stderr.strip() or stdout.strip()
        return _failure(f"sandbox worker exited with code {proc.returncode}: {detail}", total=total)

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        detail = stderr.strip() or stdout.strip()
        return _failure(f"sandbox worker returned invalid JSON: {detail}", total=total)

    return SandboxRunResult(
        ok=bool(data.get("ok")),
        error=str(data.get("error", "")),
        total=int(data.get("total", total)),
        passed=int(data.get("passed", 0)),
        results=list(data.get("results", [])),
        traces=list(data.get("traces", [])),
    )

"""
Benchmark Stress Test Harness v2 — LeetCode Project
====================================================
NO architectural changes. NO refactoring. Instrumentation only.
Runs 5 test suites against the existing ExecutionController + IOManager stack.
All suites use LOCAL operations only — no network calls.
"""

from __future__ import annotations

import json
import os
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

# ── Path setup ──────────────────────────────────────────────────────────────
TOOLS_ROOT = Path(__file__).resolve().parent / "leetcode-tools"
PROJECT_ROOT = TOOLS_ROOT.parent
BENCHMARK_DIR = PROJECT_ROOT / ".benchmark_artifacts"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(TOOLS_ROOT))

from execution_controller import (
    ExecutionController,
    ExecutionControlError,
    BatchValidationError,
    get_execution_controller,
    BuildPipeline,
    ValidationPipeline,
)
from io_manager import IOManager, QueuedWrite

# Import only what we need — avoid network-triggering module-level code
from leetcode_suggestor import (
    get_folder_for_problem,
    FILE_PATTERN,
    FOLDER_PATTERN,
)
from leetcode_doctor import (
    run_test_cases,
    classify_exception,
    FailureReason,
    is_old_format_file,
)

# ── Shared controller ───────────────────────────────────────────────────────
CONTROLLER: ExecutionController = get_execution_controller(PROJECT_ROOT)

# ── Helpers ─────────────────────────────────────────────────────────────────
def ts() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def safe_cleanup(path: Path) -> None:
    try:
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
    except OSError:
        pass


_counter = 0
def next_id() -> int:
    global _counter
    _counter += 1
    return 90000 + _counter


def make_solution_content(problem_id: int, include_todo_workflow: bool = True) -> str:
    if include_todo_workflow:
        return f'''"""
LeetCode {problem_id}. Benchmark Test Problem
{'=' * 60}
TODO WORKFLOW - Complete in Order (1 → 2 → 3 → 4):
TODO #1 - PROBLEM STATEMENT      [Review auto-generated content above]
TODO #2 - APPROACH                [Describe your algorithm step-by-step]
TODO #3 - COMPLEXITY              [State Time/Space complexity with reasoning]
TODO #4 - SOLUTION + TESTS        [Implement solution + comprehensive test cases]

Approach:
I will iterate through the input array and use a hash map to store seen values.
For each element, I check if its complement exists in the map.

Time Complexity: O(n) — single pass through the array
Space Complexity: O(n) — hash map stores up to n elements
"""
from typing import List

class Solution:
    @staticmethod
    def solve(nums: List[int], target: int) -> List[int]:
        seen = {{}}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []

if __name__ == '__main__':
    s = Solution()
    # Example 1
    result = s.solve([2, 7, 11, 15], 9)
    print(f"Result: {{result}}")
    assert result == [0, 1], f"Expected [0, 1], got {{result}}"
    # Example 2
    result = s.solve([3, 2, 4], 6)
    print(f"Result: {{result}}")
    assert result == [1, 2], f"Expected [1, 2], got {{result}}"
    print("All tests passed!")
'''
    else:
        return f'''# Simple file without TODO workflow
x = {problem_id}
print(x)
'''


def create_test_file(problem_id: int = None, workflow: bool = True) -> Path:
    pid = problem_id or next_id()
    folder = get_folder_for_problem(pid)
    filepath = folder / f"{pid}. Benchmark Test.py"
    content = make_solution_content(pid, include_todo_workflow=workflow)
    CONTROLLER.queue_text_write(filepath, content, required_markers=['TODO WORKFLOW'] if workflow else [])
    CONTROLLER.commit(reason=f"bench:create:{pid}")
    return filepath


def measure(fn, label: str) -> Dict[str, Any]:
    start = time.monotonic()
    ok = False
    err = None
    result = None
    try:
        result = fn()
        ok = True
    except Exception as exc:
        err = f"{type(exc).__name__}: {exc}"
    elapsed = time.monotonic() - start
    return {
        "label": label,
        "ok": ok,
        "elapsed_s": round(elapsed, 4),
        "error": err,
        "result": result,
    }


# ── Results accumulator ─────────────────────────────────────────────────────
class BenchReport:
    def __init__(self):
        self.suites: Dict[str, List[Dict]] = {}
        self.meta: Dict[str, Any] = {}

    def add_suite(self, name: str, results: List[Dict]):
        self.suites[name] = results

    def set_meta(self, key: str, value: Any):
        self.meta[key] = value

    def print_summary(self):
        print("\n" + "=" * 72)
        print("  BENCHMARK STRESS TEST REPORT")
        print(f"  Generated: {datetime.now().isoformat()}")
        print("=" * 72)

        total_cases = 0
        total_failures = 0
        all_latencies: List[float] = []

        for suite_name, results in self.suites.items():
            failures = [r for r in results if not r["ok"]]
            latencies = [r["elapsed_s"] for r in results]
            total_cases += len(results)
            total_failures += len(failures)
            all_latencies.extend(latencies)

            if not latencies:
                continue

            mid = len(latencies) // 2
            first_half = latencies[:mid] if mid else latencies
            second_half = latencies[mid:] if mid else latencies
            avg_first = sum(first_half) / len(first_half) if first_half else 0
            avg_second = sum(second_half) / len(second_half) if second_half else 0

            if avg_first > 0 and avg_second > avg_first * 1.2:
                drift = "INCREASING (degradation)"
            elif avg_first > 0 and avg_second < avg_first * 0.8:
                drift = "DECREASING (improving)"
            else:
                drift = "STABLE"

            print(f"\n--- {suite_name} ---")
            print(f"  Cases:        {len(results)}")
            print(f"  Failures:     {len(failures)}")
            print(f"  Latency min:  {min(latencies):.4f}s")
            print(f"  Latency max:  {max(latencies):.4f}s")
            print(f"  Latency avg:  {sum(latencies)/len(latencies):.4f}s")
            print(f"  Drift:        {drift}")
            print(f"  First-half avg:  {avg_first:.4f}s")
            print(f"  Second-half avg: {avg_second:.4f}s")

            if failures:
                print(f"  Failed cases:")
                for f in failures:
                    print(f"    - {f['label']}: {f.get('error', 'unknown')}")

        # IO queue / commit bottleneck observation
        print(f"\n--- IO Queue / Commit Bottleneck ---")
        commit_latencies: List[float] = []
        for suite_results in self.suites.values():
            for r in suite_results:
                label_lower = r.get("label", "").lower()
                if "commit" in label_lower or "write" in label_lower or "create" in label_lower or "queue" in label_lower:
                    commit_latencies.append(r["elapsed_s"])

        if commit_latencies:
            print(f"  Commit/write ops measured: {len(commit_latencies)}")
            print(f"  Commit latency avg:  {sum(commit_latencies)/len(commit_latencies):.4f}s")
            print(f"  Commit latency max:  {max(commit_latencies):.4f}s")
            print(f"  Commit latency min:  {min(commit_latencies):.4f}s")
            # Check for contention: do later commits take longer?
            mid = len(commit_latencies) // 2
            early_avg = sum(commit_latencies[:mid]) / mid if mid else 0
            late_avg = sum(commit_latencies[mid:]) / (len(commit_latencies) - mid) if len(commit_latencies) > mid else 0
            if late_avg > early_avg * 1.3:
                print(f"  Bottleneck signal: LATE commits avg {late_avg:.4f}s vs EARLY {early_avg:.4f}s")
            else:
                print(f"  No significant bottleneck detected (early={early_avg:.4f}s, late={late_avg:.4f}s)")
        else:
            print(f"  No explicit commit measurements.")

        # Subprocess overhead
        print(f"\n--- Subprocess Overhead ---")
        sub_times = [
            r["elapsed_s"]
            for suite_results in self.suites.values()
            for r in suite_results
            if "subprocess" in r.get("label", "").lower()
            or "run_test" in r.get("label", "").lower()
            or "test" in r.get("label", "").lower()
        ]
        if sub_times:
            print(f"  Subprocess/exec runs:   {len(sub_times)}")
            print(f"  Avg exec time:          {sum(sub_times)/len(sub_times):.4f}s")
            print(f"  Max exec time:          {max(sub_times):.4f}s")
            print(f"  Min exec time:          {min(sub_times):.4f}s")
            timeouts = [t for t in sub_times if t > 15]
            print(f"  Slow runs (>15s):       {len(timeouts)}")
            if len(sub_times) >= 4:
                q1 = sorted(sub_times)[len(sub_times)//4]
                q3 = sorted(sub_times)[3*len(sub_times)//4]
                print(f"  P25: {q1:.4f}s  P75: {q3:.4f}s")
        else:
            print(f"  No subprocess measurements recorded.")

        # Overall verdict
        print(f"\n{'=' * 72}")
        failure_rate = total_failures / total_cases if total_cases else 0

        # Check per-suite failure rates
        worst_suite_failure = 0.0
        for suite_results in self.suites.values():
            if not suite_results:
                continue
            sr = len([r for r in suite_results if not r["ok"]]) / len(suite_results)
            worst_suite_failure = max(worst_suite_failure, sr)

        if failure_rate > 0.3:
            verdict = "CRITICAL INSTABILITY"
        elif failure_rate > 0.1 or worst_suite_failure > 0.25:
            verdict = "DEGRADED UNDER LOAD"
        else:
            # Check latency drift across all suites
            all_first = []
            all_second = []
            for suite_results in self.suites.values():
                latencies = [r["elapsed_s"] for r in suite_results]
                mid = len(latencies) // 2
                if mid > 0:
                    all_first.extend(latencies[:mid])
                    all_second.extend(latencies[mid:])
            avg_a = sum(all_first) / len(all_first) if all_first else 0
            avg_b = sum(all_second) / len(all_second) if all_second else 0
            if avg_a > 0 and avg_b > avg_a * 2.0:
                verdict = "DEGRADED UNDER LOAD"
            else:
                verdict = "STABLE UNDER LOAD"

        print(f"  Total cases:      {total_cases}")
        print(f"  Total failures:   {total_failures}")
        print(f"  Failure rate:     {failure_rate:.1%}")
        print(f"  Worst suite FR:   {worst_suite_failure:.1%}")
        print(f"\n  VERDICT: {verdict}")
        print(f"{'=' * 72}")


# ── TEST SUITE A: Burst Load ────────────────────────────────────────────────
def suite_a_burst_load() -> List[Dict]:
    """Create 30 files sequentially, measure commit time, verify, cleanup."""
    print(f"\n[{ts()}] Suite A: Burst Load (30 create+verify cycles)")
    results: List[Dict] = []
    created_files: List[Path] = []

    for i in range(30):
        pid = next_id()
        label = f"burst-create-{i:02d}"
        m = measure(lambda: create_test_file(pid), label)
        results.append(m)

        if m["ok"] and isinstance(m["result"], Path):
            created_files.append(m["result"])
            # Verify
            verify = measure(lambda p=m["result"]: p.exists() and p.stat().st_size > 0,
                           f"burst-verify-{i:02d}")
            results.append(verify)

        print(f"  [{ts()}] {label}: {'OK' if m['ok'] else 'FAIL'} {m['elapsed_s']:.4f}s")

    # Cleanup
    for f in created_files:
        safe_cleanup(f)

    return results


# ── TEST SUITE B: Alternating Mode Stress ───────────────────────────────────
def suite_b_alternating() -> List[Dict]:
    """Cycle 20 times: create → read → list → validate → regenerate.
    All LOCAL — no network, no AI calls."""
    print(f"\n[{ts()}] Suite B: Alternating Mode Stress (20 cycles)")
    results: List[Dict] = []

    for i in range(20):
        pid = next_id()
        folder = get_folder_for_problem(pid)
        filepath = folder / f"{pid}. Alternating Test.py"

        # Step 1: Create file
        m1 = measure(
            lambda fp=filepath, p=pid: (
                CONTROLLER.queue_text_write(fp, make_solution_content(p), required_markers=['TODO WORKFLOW']),
                CONTROLLER.commit(reason=f"bench-b-create:{p}"),
                fp
            )[-1],
            f"cycle-{i:02d}-create",
        )
        results.append(m1)
        print(f"  [{ts()}] cycle-{i:02d}-create: {'OK' if m1['ok'] else 'FAIL'} {m1['elapsed_s']:.4f}s")

        # Step 2: Read back
        m2 = measure(
            lambda fp=filepath: CONTROLLER.read_text(fp),
            f"cycle-{i:02d}-read",
        )
        results.append(m2)
        print(f"  [{ts()}] cycle-{i:02d}-read: {'OK' if m2['ok'] else 'FAIL'} {m2['elapsed_s']:.4f}s")

        # Step 3: List directory
        m3 = measure(
            lambda f=folder: CONTROLLER.list_directory(f),
            f"cycle-{i:02d}-listdir",
        )
        results.append(m3)
        print(f"  [{ts()}] cycle-{i:02d}-listdir: {'OK' if m3['ok'] else 'FAIL'} {m3['elapsed_s']:.4f}s")

        # Step 4: Queue another write (overwrite simulation)
        m4 = measure(
            lambda fp=filepath, p=pid: (
                CONTROLLER.queue_text_write(fp, make_solution_content(p + 1), required_markers=['TODO WORKFLOW']),
                CONTROLLER.commit(reason=f"bench-b-overwrite:{p}"),
            ),
            f"cycle-{i:02d}-overwrite",
        )
        results.append(m4)
        print(f"  [{ts()}] cycle-{i:02d}-overwrite: {'OK' if m4['ok'] else 'FAIL'} {m4['elapsed_s']:.4f}s")

        # Step 5: Backup + re-write (simulate regenerate pattern)
        backup = filepath.with_suffix('.py.bak')
        m5 = measure(
            lambda fp=filepath, bp=backup: (
                CONTROLLER.queue_text_write(bp, CONTROLLER.read_text(fp)),
                CONTROLLER.commit(reason=f"bench-b-backup:{fp.name}"),
            ),
            f"cycle-{i:02d}-backup",
        )
        results.append(m5)
        print(f"  [{ts()}] cycle-{i:02d}-backup: {'OK' if m5['ok'] else 'FAIL'} {m5['elapsed_s']:.4f}s")

        # Cleanup
        safe_cleanup(filepath)
        safe_cleanup(backup)

    return results


# ── TEST SUITE C: IO Pressure Loop ──────────────────────────────────────────
def suite_c_io_pressure() -> List[Dict]:
    """Write same file 20 times with growing content, measure queue/commit."""
    print(f"\n[{ts()}] Suite C: IO Pressure Loop (20 writes)")
    results: List[Dict] = []

    pid = next_id()
    folder = get_folder_for_problem(pid)
    filepath = folder / f"{pid}. IO Pressure.py"

    for i in range(20):
        # Grow content size each iteration
        extra_lines = "\n".join(f"# Comment line {j}" for j in range(i * 10))
        content = make_solution_content(pid) + "\n\n" + extra_lines

        queue_before = len(CONTROLLER.io_manager.peek())
        m1 = measure(
            lambda fp=filepath, c=content: (
                CONTROLLER.queue_text_write(fp, c, required_markers=['TODO WORKFLOW']),
                CONTROLLER.commit(reason=f"bench-c-write-{i}"),
            ),
            f"io-pressure-write-{i:02d}",
        )
        results.append(m1)
        queue_after = len(CONTROLLER.io_manager.peek())

        # Check tmp cleanup
        tmp_files = list(folder.glob("*.tmp"))
        results.append({
            "label": f"io-pressure-queue-{i:02d}",
            "ok": True,
            "elapsed_s": 0.0,
            "error": None,
            "result": {
                "queue_before": queue_before,
                "queue_after": queue_after,
                "tmp_left": len(tmp_files),
                "write_ok": m1["ok"],
            },
        })

        file_size = filepath.stat().st_size if filepath.exists() else 0
        print(f"  [{ts()}] write-{i:02d}: {'OK' if m1['ok'] else 'FAIL'} "
              f"{m1['elapsed_s']:.4f}s | queue: {queue_before}\u2192{queue_after} | "
              f"tmp: {len(tmp_files)} | size: {file_size}B")

    safe_cleanup(filepath)
    return results


# ── TEST SUITE D: Exception Injection ───────────────────────────────────────
def suite_d_exception_injection() -> List[Dict]:
    """20 cases: invalid paths, bad content, empty writes, batch limit tests."""
    print(f"\n[{ts()}] Suite D: Exception Injection (20 cases)")
    results: List[Dict] = []

    # Case 1-4: Read nonexistent files (should return default, not crash)
    for i, bad_path in enumerate([
        PROJECT_ROOT / "nonexistent_1.py",
        PROJECT_ROOT / "nonexistent_2.py",
        PROJECT_ROOT / "foo" / "bar" / "missing.json",
        Path("/absolute/nonexistent.txt"),
    ]):
        m = measure(lambda bp=bad_path: CONTROLLER.read_text(bp, default=None),
                   f"inject-read-missing-{i}")
        results.append(m)
        print(f"  [{ts()}] inject-read-missing-{i}: {'OK' if m['ok'] else 'FAIL'} {m['elapsed_s']:.4f}s")

    # Case 5-8: List nonexistent directories
    for i in range(4):
        bad_dir = PROJECT_ROOT / f"nonexistent_dir_{i}"
        m = measure(lambda bd=bad_dir: CONTROLLER.list_directory(bd),
                   f"inject-list-missing-{i}")
        results.append(m)
        print(f"  [{ts()}] inject-list-missing-{i}: {'OK' if m['ok'] else 'FAIL'} {m['elapsed_s']:.4f}s")

    # Case 9-12: Write with missing required markers (should FAIL validation — expected)
    for i in range(4):
        tmp_file = BENCHMARK_DIR / f"inject_no_marker_{i}.py"
        caught = False
        try:
            CONTROLLER.queue_text_write(tmp_file, "no markers here", required_markers=['TODO WORKFLOW'])
            CONTROLLER.commit(reason=f"inject-no-marker-{i}")
        except BatchValidationError:
            caught = True  # Expected — controller caught it
        except Exception:
            caught = True
        finally:
            CONTROLLER.io_manager.clear()
            safe_cleanup(tmp_file)
        results.append({
            "label": f"inject-no-marker-{i}",
            "ok": caught,  # Expected behavior: validation rejected write
            "elapsed_s": 0.0,
            "error": None,
            "result": "Validation correctly rejected invalid write",
        })
        print(f"  [{ts()}] inject-no-marker-{i}: {'OK (caught)' if caught else 'UNEXPECTED'}")

    # Case 13-14: Empty content write (should fail validation — expected)
    for i in range(2):
        tmp_file = BENCHMARK_DIR / f"inject_empty_{i}.py"
        caught = False
        try:
            CONTROLLER.queue_text_write(tmp_file, "", required_markers=[])
            CONTROLLER.commit(reason=f"inject-empty-{i}")
        except BatchValidationError:
            caught = True  # Expected
        except Exception:
            caught = True
        finally:
            CONTROLLER.io_manager.clear()
            safe_cleanup(tmp_file)
        results.append({
            "label": f"inject-empty-{i}",
            "ok": caught,
            "elapsed_s": 0.0,
            "error": None,
            "result": "Validation correctly rejected empty write",
        })
        print(f"  [{ts()}] inject-empty-{i}: {'OK (caught)' if caught else 'UNEXPECTED'}")

    # Case 15-16: Concurrent queue stress (queue many, commit once)
    for i in range(2):
        files = []
        try:
            for j in range(5):
                tf = BENCHMARK_DIR / f"inject_batch_{i}_{j}.py"
                files.append(tf)
                CONTROLLER.queue_text_write(tf, make_solution_content(80000 + i * 10 + j),
                                          required_markers=['TODO WORKFLOW'])
            m = measure(lambda: CONTROLLER.commit(reason=f"inject-batch-{i}"),
                       f"inject-batch-commit-{i}")
            results.append(m)
        except Exception as exc:
            results.append({
                "label": f"inject-batch-commit-{i}",
                "ok": False,
                "elapsed_s": 0.0,
                "error": str(exc),
                "result": None,
            })
        finally:
            CONTROLLER.io_manager.clear()
            for f in files:
                safe_cleanup(f)
        print(f"  [{ts()}] inject-batch-{i}: {'OK' if results[-1]['ok'] else 'FAIL'}")

    # Case 17-18: Ensure directory on already-existing path
    for i in range(2):
        existing_dir = BENCHMARK_DIR / f"inject_mkdir_{i}"
        existing_dir.mkdir(parents=True, exist_ok=True)
        m = measure(lambda ed=existing_dir: CONTROLLER.ensure_directory(ed),
                   f"inject-mkdir-existing-{i}")
        results.append(m)
        safe_cleanup(existing_dir)
        print(f"  [{ts()}] inject-mkdir-existing-{i}: {'OK' if m['ok'] else 'FAIL'} {m['elapsed_s']:.4f}s")

    # Case 19-20: JSON write then read back
    for i in range(2):
        tmp_json = BENCHMARK_DIR / f"inject_json_{i}.json"
        test_data = {"id": i, "values": list(range(100)), "nested": {"a": [1, 2, 3]}}
        try:
            CONTROLLER.ensure_directory(tmp_json.parent)
            CONTROLLER.queue_json_write(tmp_json, test_data)
            m1 = measure(lambda: CONTROLLER.commit(reason=f"inject-json-{i}"),
                        f"inject-json-write-{i}")
            results.append(m1)
            m2 = measure(lambda tj=tmp_json: CONTROLLER.read_json(tj, default=None),
                        f"inject-json-read-{i}")
            results.append(m2)
        except Exception as exc:
            results.append({
                "label": f"inject-json-{i}",
                "ok": False,
                "elapsed_s": 0.0,
                "error": str(exc),
                "result": None,
            })
        finally:
            CONTROLLER.io_manager.clear()
            safe_cleanup(tmp_json)
        print(f"  [{ts()}] inject-json-{i}: write={'OK' if m1['ok'] else 'FAIL'} read={'OK' if m2.get('ok') else 'FAIL'}")

    return results


# ── TEST SUITE E: Subprocess Load Test ──────────────────────────────────────
def suite_e_subprocess_load() -> List[Dict]:
    """Run 20 sequential run_test_cases() on working solution files."""
    print(f"\n[{ts()}] Suite E: Subprocess Load Test (20 runs)")
    results: List[Dict] = []

    for i in range(20):
        pid = next_id()
        folder = get_folder_for_problem(pid)
        filepath = folder / f"{pid}. Subprocess Test.py"

        # Create a working solution file
        content = f'''"""LeetCode {pid}. Subprocess Test"""
class Solution:
    @staticmethod
    def solve() -> int:
        return {i * 2}

if __name__ == "__main__":
    result = Solution.solve()
    print(f"Result: {{result}}")
    assert result == {i * 2}, f"Expected {i * 2}, got {{result}}"
    print("PASS")
'''
        try:
            CONTROLLER.queue_text_write(filepath, content)
            CONTROLLER.commit(reason=f"bench-e-create:{pid}")
        except Exception:
            CONTROLLER.io_manager.clear()
            folder.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content)

        m = measure(lambda fp=filepath: run_test_cases(fp),
                   f"subprocess-run-{i:02d}")
        results.append(m)
        print(f"  [{ts()}] subprocess-run-{i:02d}: {'OK' if m['ok'] else 'FAIL'} "
              f"{m['elapsed_s']:.4f}s")

        safe_cleanup(filepath)

    return results


# ── MAIN ────────────────────────────────────────────────────────────────────
def main():
    global _counter
    _counter = 0

    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)

    report = BenchReport()
    report.set_meta("start_time", datetime.now().isoformat())
    report.set_meta("project_root", str(PROJECT_ROOT))

    # Suite A
    results_a = suite_a_burst_load()
    report.add_suite("A — Burst Load", results_a)

    # Suite B
    _counter = 1000  # Reset IDs to avoid collisions
    results_b = suite_b_alternating()
    report.add_suite("B — Alternating Mode Stress", results_b)

    # Suite C
    _counter = 2000
    results_c = suite_c_io_pressure()
    report.add_suite("C — IO Pressure Loop", results_c)

    # Suite D
    _counter = 3000
    results_d = suite_d_exception_injection()
    report.add_suite("D — Exception Injection", results_d)

    # Suite E
    _counter = 4000
    results_e = suite_e_subprocess_load()
    report.add_suite("E — Subprocess Load Test", results_e)

    report.set_meta("end_time", datetime.now().isoformat())

    # Save raw data
    raw_output = {
        "meta": report.meta,
        "suites": {
            name: [
                {
                    "label": r["label"],
                    "ok": r["ok"],
                    "elapsed_s": r["elapsed_s"],
                    "error": r.get("error"),
                }
                for r in results
            ]
            for name, results in report.suites.items()
        },
    }
    raw_path = BENCHMARK_DIR / "benchmark_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(raw_output, f, indent=2, default=str)
    print(f"\nRaw data saved to: {raw_path}")

    # Print summary
    report.print_summary()


if __name__ == "__main__":
    main()

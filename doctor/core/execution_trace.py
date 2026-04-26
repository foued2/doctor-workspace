import concurrent.futures
import traceback
import time


def _tuples_to_lists(obj):
    """Recursively convert tuples to lists. Needed because normalize_solution
    converts list literals to tuples, and test harness may pass tuples as args."""
    if isinstance(obj, tuple):
        return [_tuples_to_lists(x) for x in obj]
    if isinstance(obj, list):
        return [_tuples_to_lists(x) for x in obj]
    return obj


def run_test_with_trace(func, input_data, expected_output, timeout_seconds=30):
    start = time.time()
    try:
        converted = _tuples_to_lists(input_data)
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            future = ex.submit(func, *converted)
            try:
                result = future.result(timeout=timeout_seconds)
            except concurrent.futures.TimeoutError:
                return {
                    "passed": False,
                    "output": None,
                    "error": f"timeout after {timeout_seconds}s",
                    "execution_time": round(time.time() - start, 6),
                }
        return {
            "passed": result == expected_output,
            "output": result,
            "error": None,
            "execution_time": round(time.time() - start, 6),
        }
    except Exception:
        return {
            "passed": False,
            "output": None,
            "error": traceback.format_exc(),
            "execution_time": round(time.time() - start, 6),
        }

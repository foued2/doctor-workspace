import traceback
import time

def run_test_with_trace(func, input_data, expected_output):
    start = time.time()
    try:
        result = func(*input_data)
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

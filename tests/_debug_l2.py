import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
print("Python:", sys.version, flush=True)
code = """
def twoSum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
"""
print("Code defined", flush=True)
namespace = {}
exec(code, namespace)
print("Exec done, keys:", list(namespace.keys()), flush=True)
func = namespace.get('twoSum')
print("Func:", func, flush=True)
result = func([2,7,11,15], 9)
print("Result:", result, flush=True)

from doctor.test_executor import TestExecutor
executor = TestExecutor()
report = executor.verify('Two Sum', code)
print("Error:", report.error, flush=True)
print("Verdict:", report.verdict, flush=True)
print("Pass rate:", report.pass_rate, flush=True)
for r in report.results:
    print(f"  {r.label}: passed={r.passed} got={r.got} exp={r.expected}", flush=True)

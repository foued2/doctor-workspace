"""Deep trace: full predict() for Two_Sum_partial."""
import sys
sys.path.insert(0, r'F:\pythonProject')

from tests.verify_code_only_baseline import SOLUTIONS
from doctor.llm_doctor import predict

sol = SOLUTIONS['Two Sum::partial']
prompt = f"PROBLEM: {sol['problem']}\n\nSOLUTION:\n{sol['code']}"

result = predict(prompt)

print(f"label: {result['label']}")
print(f"confidence: {result['confidence']}")
print(f"confidence_kind: {result['confidence_kind']}")
print(f"decision_path: {result['decision_path']}")

bias = result.get('system_bias_indicators', {})
print(f"layer1_verdict: {bias.get('layer1_verdict')}")
print(f"layer1_violations: {bias.get('layer1_violations')}")
print(f"layer1_fatal_flags: {bias.get('layer1_fatal_flags')}")
print(f"layer2_activated: {bias.get('layer2_activated')}")
print(f"layer2_verdict: {bias.get('layer2_verdict')}")
print(f"layer2_pass_rate: {bias.get('layer2_pass_rate')}")
print(f"layer2_failure_type: {bias.get('layer2_failure_type')}")
print(f"layer2_failures: {bias.get('layer2_failures')}")
print(f"insufficient_reason: {bias.get('insufficient_reason')}")
print(f"tests_total: {bias.get('tests_total')}")

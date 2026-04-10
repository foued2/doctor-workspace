import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from doctor.llm_doctor import predict

import tests.production_87 as p87
prob = p87.PROBLEMS[0]  # Two Sum
correct_code = prob["correct"]
prompt = f"PROBLEM: {prob['problem']}\n\nSOLUTION:\n{correct_code}"

result = predict(prompt)
print("=== FULL DUAL-LAYER RESULT ===")
print(f"Label: {result['label']}")
print(f"Confidence: {result['confidence']}")
print(f"Decision path: {result['decision_path']}")
bias = result.get('system_bias_indicators', {})
print(f"Layer 1 verdict: {bias.get('layer1_verdict')}")
print(f"Layer 1 violations: {bias.get('layer1_violations')}")
print(f"Layer 2 activated: {bias.get('layer2_activated')}")
print(f"Layer 2 verdict: {bias.get('layer2_verdict')}")
print(f"Layer 2 pass_rate: {bias.get('layer2_pass_rate')}")
print(f"Layer 2 failures: {bias.get('layer2_failures')}")

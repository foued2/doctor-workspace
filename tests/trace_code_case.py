"""Trace ONE code case to see where it fails."""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from doctor.llm_doctor import predict, _extract_problem_and_solution
from doctor.code_analyzer import CodeAnalyzer
from doctor.test_executor import TestExecutor, PROBLEM_KEY_MAP
from doctor.undefined_detection import classify_undefined
from doctor.llm_doctor import _LEETCODE_SOLUTIONS, _SOLUTION_TEXTS

# Two Sum correct
problem = "Two Sum"
sol_type = "correct"
solution_text = _SOLUTION_TEXTS[f"{problem}::{sol_type}"]
solution_info = _LEETCODE_SOLUTIONS[f"{problem}::{sol_type}"]

prompt = f"PROBLEM: {problem}. {solution_info['reasoning']}\n\nSOLUTION:\n{solution_text}"

print(f"PROMPT:\n{prompt}\n")
print(f"GT: {solution_info['verdict']}")
print()

# Step 1: Layer 0.5
undef_result = classify_undefined(prompt)
print(f"[L0.5] score={undef_result.score:.3f} signals={len(undef_result.signals)} is_undef={undef_result.is_undefined}")

# Step 2: Extraction
problem_text, code = _extract_problem_and_solution(prompt)
print(f"\n[EXTRACT] problem_text={problem_text[:80]!r}...")
print(f"[EXTRACT] code={code[:120]!r}...")

# Step 3: Layer 1
analyzer = CodeAnalyzer()
l1 = analyzer.analyze(problem_text, code)
print(f"\n[L1] verdict={l1.verdict} conf={l1.confidence}")
print(f"[L1] failures={l1.failures}")
print(f"[L1] details={l1.details}")

# Step 4: Layer 2
if "time_complexity_viable" not in l1.failures:
    executor = TestExecutor()
    # Map problem name
    problem_name = None
    for name in PROBLEM_KEY_MAP:
        if name.lower() in problem_text.lower():
            problem_name = name
            break
    print(f"\n[L2] problem_name resolved to: {problem_name}")
    if problem_name:
        l2 = executor.verify(problem_name, code)
        print(f"[L2] verdict={l2.verdict} pass_rate={l2.pass_rate}")
        for r in l2.results:
            print(f"  {'PASS' if r.passed else 'FAIL'} {r.label}: got={r.got}" + (f" expected={r.expected}" if not r.passed else ""))

# Final
pred = predict(prompt)
print(f"\n[FINAL] label={pred['label']} conf={pred['confidence']} kind={pred['confidence_kind']}")
print(f"[FINAL] path={pred['decision_path']}")
bias = pred.get('system_bias_indicators', {})
print(f"[FINAL] L1={bias.get('layer1_verdict')} L2={bias.get('layer2_verdict')}")

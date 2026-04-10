"""
Phase A — Step 1: Trace correct cases with verbose logging.
Reproduce the exact same batch as verify_production.py to see what happens to correct cases.
"""
import sys
import os
import traceback
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from doctor.llm_doctor import LLMDoctor, _extract_problem_and_solution
from doctor.undefined_detection import classify_undefined
from doctor.code_analyzer import CodeAnalyzer
from doctor.test_executor import TestExecutor
from external_stress_layer import StressCase, StressKind
from external_stress_layer.real_world_data_injector import RealWorldDataInjector
from external_stress_layer.cross_domain_stressor import CrossDomainStressor
from external_stress_layer.human_crafted_attacks import HumanCraftedAttacks
from dataset_generator.adaptive_generator import AdaptiveGenerator

# Rebuild the same batch as verify_production.py
gen = AdaptiveGenerator(seed=42)
internal_batch = gen.generate_batch(n=30, memory_fraction=0.5)
cases = []
for pub in internal_batch["public_cases"]:
    priv = internal_batch["private_key"].get(pub["case_id"])
    if priv:
        cases.append(StressCase(
            case_id=pub["case_id"], prompt=pub["prompt"],
            stress_kind=StressKind.MIXED, ground_truth=priv["ground_truth"],
            metadata={"contradiction": priv.get("contradiction", False)},
        ))

rw = RealWorldDataInjector(seed=42)
cd = CrossDomainStressor(seed=42)
hc = HumanCraftedAttacks(seed=42)
esl_cases = rw.generate_cases(15) + cd.generate_cases(15) + hc.generate_cases()
cases.extend(esl_cases)

# Find correct GT cases
correct_cases = [c for c in cases if c.ground_truth == "correct"]
print(f"Total correct GT cases: {len(correct_cases)}\n")

for case in correct_cases:
    print(f"{'='*80}")
    print(f"CASE: {case.case_id} | GT={case.ground_truth}")
    print(f"{'='*80}")

    # Show the full prompt
    print(f"PROMPT (first 300 chars):")
    print(f"  {case.prompt[:300]}")
    print(f"  ... ({len(case.prompt)} chars total)")

    # Step 1: Layer 0.5
    print(f"\n[L0.5] classify_undefined:")
    undef_result = classify_undefined(case.prompt)
    print(f"  score={undef_result.score:.3f} signals={len(undef_result.signals)} is_undef={undef_result.is_undefined}")

    # Step 2: Extraction
    print(f"\n[EXTRACT] _extract_problem_and_solution:")
    problem_text, code = _extract_problem_and_solution(case.prompt)
    if problem_text is None:
        print(f"  ✗ EXTRACTION FAILED — returned (None, None)")
        print(f"  This causes ANALYSIS_ERROR fallback in predict()")
        # Try the full predict to see the final verdict
        doctor = LLMDoctor()
        try:
            pred = doctor.predict(case.prompt)
            print(f"  Final predict: label={pred['label']} conf={pred['confidence']} kind={pred['confidence_kind']}")
            print(f"  decision_path={pred['decision_path']}")
        except Exception as e:
            print(f"  Exception in predict: {e}")
            traceback.print_exc()
    else:
        print(f"  problem_text: {problem_text[:100]}...")
        print(f"  code: {code[:120]}...")

        # Step 3: Layer 1
        print(f"\n[L1] CodeAnalyzer.analyze:")
        analyzer = CodeAnalyzer()
        try:
            l1_result = analyzer.analyze(problem_text, code)
            print(f"  verdict={l1_result.verdict} conf={l1_result.confidence}")
            print(f"  failures={l1_result.failures}")
            print(f"  reasoning={l1_result.reasoning}")
            if l1_result.details:
                for k, v in l1_result.details.items():
                    print(f"    {k}: {v}")
        except Exception as e:
            print(f"  ✗ EXCEPTION: {e}")
            traceback.print_exc()
            l1_result = None

        # Step 4: Layer 2
        if l1_result:
            FATAL_CHECKS = {"time_complexity_viable"}
            has_fatal = bool(set(l1_result.failures) & FATAL_CHECKS)
            if not has_fatal:
                print(f"\n[L2] TestExecutor.verify:")
                executor = TestExecutor()
                try:
                    from doctor.test_executor import PROBLEM_KEY_MAP
                    # Find problem name
                    problem_name = None
                    for name, key in PROBLEM_KEY_MAP.items():
                        if name.lower() in problem_text.lower():
                            problem_name = name
                            break
                    print(f"  problem_name resolved to: {problem_name}")
                    if problem_name:
                        l2_report = executor.verify(problem_name, code)
                        print(f"  verdict={l2_report.verdict} pass_rate={l2_report.pass_rate}")
                        for r in l2_report.results:
                            status = "PASS" if r.passed else "FAIL"
                            print(f"    {status} {r.label}: got={r.got}" + (f" expected={r.expected}" if not r.passed else ""))
                    else:
                        print(f"  No matching problem name in PROBLEM_KEY_MAP")
                except Exception as e:
                    print(f"  ✗ EXCEPTION: {e}")
                    traceback.print_exc()
            else:
                print(f"\n[L2] SKIPPED — FATAL checker in Layer 1")

        # Final predict
        doctor = LLMDoctor()
        try:
            pred = doctor.predict(case.prompt)
            verdict_ok = pred['label'] == case.ground_truth
            print(f"\n[FINAL] label={pred['label']} conf={pred['confidence']} kind={pred['confidence_kind']}")
            print(f"  decision_path={pred['decision_path']}")
            print(f"  {'✓ MATCH' if verdict_ok else '✗ MISMATCH'} (expected={case.ground_truth})")
        except Exception as e:
            print(f"\n[FINAL] EXCEPTION: {e}")
            traceback.print_exc()

    print()

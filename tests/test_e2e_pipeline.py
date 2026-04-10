"""
End-to-End Pipeline Test — Real LeetCode Problem
==================================================
Walks the entire Doctor pipeline for Three Sum solutions on Two Sum:
  1. Clean correct solution
  2. Subtle bug (stores after check — fails self-element-reuse)
  3. Clearly wrong solution (uses same element twice)

Shows all 6 stages: Layer 0.5 → extraction → Layer 1 checkers → Layer 2 tests → verdict → grader.
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from collections import defaultdict

from doctor.llm_doctor import LLMDoctor, predict, _extract_problem_and_solution
from doctor.code_analyzer import CodeAnalyzer
from doctor.test_executor import TestExecutor
from doctor.undefined_detection import classify_undefined
from external_stress_layer import StressCase, StressKind
from external_stress_layer.enhanced_evaluator import EnhancedEvaluator
from doctor.doctor_grader import DoctorGrader

# ===========================================================================
# TEST CASES — Two Sum, three solution types
# ===========================================================================

PROBLEM_TEXT = (
    "Given an array of integers nums and an integer target, "
    "return indices of the two numbers such that they add up to target.\n\n"
    "You may assume that each input would have exactly one solution, "
    "and you may not use the same element twice.\n\n"
    "You can return the answer in any order."
)

SOLUTIONS = {
    "correct": {
        "code": (
            "def twoSum(nums, target):\n"
            "    seen = {}\n"
            "    for i, n in enumerate(nums):\n"
            "        complement = target - n\n"
            "        if complement in seen:\n"
            "            return [seen[complement], i]\n"
            "        seen[n] = i\n"
            "    return []"
        ),
        "ground_truth": "correct",
        "description": "Hash map O(n) — stores AFTER checking complement",
    },
    "subtle_bug": {
        "code": (
            "def twoSum(nums, target):\n"
            "    seen = {}\n"
            "    for i, n in enumerate(nums):\n"
            "        seen[n] = i\n"
            "        complement = target - n\n"
            "        if complement in seen:\n"
            "            return [seen[complement], i]\n"
            "    return []"
        ),
        "ground_truth": "partial",
        "description": "Hash map O(n) — stores BEFORE checking (fails [3,3], 6)",
    },
    "wrong": {
        "code": (
            "def twoSum(nums, target):\n"
            "    for i in range(len(nums)):\n"
            "        if nums[i] + nums[i] == target:\n"
            "            return [i, i]\n"
            "    return []"
        ),
        "ground_truth": "incorrect",
        "description": "Uses same element twice — violates constraint",
    },
}


def run_pipeline(label, solution, ground_truth):
    """Run one solution through the full pipeline with verbose logging."""
    prompt = f"PROBLEM: {PROBLEM_TEXT}\n\nSOLUTION:\n{solution['code']}"

    print(f"\n{'='*80}")
    print(f"CASE: {label.upper()} — {solution['description']}")
    print(f"Ground Truth: {ground_truth}")
    print(f"{'='*80}")

    # ── STAGE 1: Layer 0.5 — Undefined Detection ─────────────────────────
    print(f"\n── STAGE 1: Layer 0.5 Undefined Detection ──")
    undef_result = classify_undefined(prompt)
    print(f"  Score:     {undef_result.score:.3f}")
    print(f"  Signals:   {len(undef_result.signals)}")
    print(f"  Is undef:  {undef_result.is_undefined}")
    print(f"  Path:      {undef_result.decision_path}")
    if undef_result.signals:
        for s in undef_result.signals:
            print(f"    [{s.category}] '{s.matched_text}' (str={s.strength})")
    else:
        print(f"    (no signals — passes through to Layer 1)")
    l05_fired = undef_result.is_undefined

    if l05_fired:
        print(f"\n  ⚠ FALSE POSITIVE — Layer 0.5 short-circuited, skipping Layers 1/2")
        pred = predict(prompt)
        print(f"\n  Verdict: {pred['label']} conf={pred['confidence']} kind={pred['confidence_kind']}")
        return pred

    # ── STAGE 2: Extraction ──────────────────────────────────────────────
    print(f"\n── STAGE 2: Problem + Solution Extraction ──")
    problem_text, code = _extract_problem_and_solution(prompt)
    if problem_text is None:
        print(f"  ✗ EXTRACTION FAILED — falling back to ANALYSIS_ERROR")
        pred = predict(prompt)
        print(f"  Verdict: {pred['label']} conf={pred['confidence']} kind={pred['confidence_kind']}")
        return pred
    print(f"  Problem:   {problem_text[:100]}...")
    print(f"  Code:      {code[:80]}...")
    print(f"  ✓ Extraction succeeded")

    # ── STAGE 3: Layer 1 — Static Analysis ───────────────────────────────
    print(f"\n── STAGE 3: Layer 1 Static Analysis (CodeAnalyzer) ──")
    analyzer = CodeAnalyzer()
    l1_result = analyzer.analyze(problem_text, code)
    print(f"  Verdict:     {l1_result.verdict}")
    print(f"  Confidence:  {l1_result.confidence}")
    print(f"  Failures:    {l1_result.failures if l1_result.failures else '(none)'}")
    print(f"  Reasoning:   {l1_result.reasoning}")
    if l1_result.details:
        print(f"  Checker details:")
        for key, val in l1_result.details.items():
            print(f"    {key}: {val}")

    # Check FATAL
    FATAL_CHECKS = {"time_complexity_viable"}
    has_fatal = bool(set(l1_result.failures) & FATAL_CHECKS)
    print(f"  FATAL:       {has_fatal}")
    print(f"  Layer 2:     {'SKIPPED' if has_fatal else 'will run'}")

    # ── STAGE 4: Layer 2 — Execution ─────────────────────────────────────
    if has_fatal:
        print(f"\n── STAGE 4: Layer 2 Execution — SKIPPED (FATAL in Layer 1) ──")
        l2_verdict = None
        l2_pass_rate = None
        l2_results = []
    else:
        print(f"\n── STAGE 4: Layer 2 Execution (TestExecutor) ──")
        executor = TestExecutor()
        l2_report = executor.verify("Two Sum", code)
        l2_verdict = l2_report.verdict
        l2_pass_rate = l2_report.pass_rate
        l2_results = l2_report.results
        print(f"  Verdict:     {l2_verdict}")
        print(f"  Pass rate:   {l2_pass_rate:.0%}")
        for r in l2_results:
            status = "✓ PASS" if r.passed else "✗ FAIL"
            if r.passed:
                print(f"    {status} {r.label}: got={r.got}")
            else:
                print(f"    {status} {r.label}: got={r.got} expected={r.expected}"
                      + (f" error={r.error}" if r.error else ""))

    # ── STAGE 5: Doctor Verdict ──────────────────────────────────────────
    print(f"\n── STAGE 5: Doctor Verdict (predict) ──")
    pred = predict(prompt)
    print(f"  Label:       {pred['label']}")
    print(f"  Confidence:  {pred['confidence']}")
    print(f"  Kind:        {pred['confidence_kind']}")
    print(f"  Decision:    {pred['decision_path']}")
    bias = pred.get('system_bias_indicators', {})
    if bias.get('layer1_verdict'):
        print(f"  Layer 1:     {bias['layer1_verdict']} violations={bias.get('layer1_violations', [])}")
    if bias.get('layer2_verdict') is not None:
        print(f"  Layer 2:     {bias['layer2_verdict']} pass_rate={bias.get('layer2_pass_rate')}")
    if bias.get('layer2_failures'):
        print(f"  Layer 2 FPs: {[f['label'] for f in bias['layer2_failures']]}")

    verdict_correct = pred['label'] == ground_truth
    print(f"\n  {'✓ VERDICT MATCHES GT' if verdict_correct else '✗ VERDICT MISMATCH'} "
          f"(predicted={pred['label']} expected={ground_truth})")

    return pred


def main():
    print("=" * 80)
    print("END-TO-END PIPELINE TEST — Two Sum (Real LeetCode Problem)")
    print("=" * 80)
    print(f"\nProblem: {PROBLEM_TEXT[:120]}...")

    doctor = LLMDoctor()
    print(f"Doctor provider: {doctor.get_provider()}")

    predictions = []
    cases = []

    for label, sol in SOLUTIONS.items():
        pred = run_pipeline(label, sol, sol["ground_truth"])
        predictions.append(pred)
        cases.append(StressCase(
            case_id=f"twosum-{label}",
            prompt=f"PROBLEM: {PROBLEM_TEXT}\n\nSOLUTION:\n{sol['code']}",
            stress_kind=StressKind.MIXED,
            ground_truth=sol["ground_truth"],
        ))

    # ── STAGE 6: Grader ──────────────────────────────────────────────────
    print(f"\n{'='*80}")
    print(f"STAGE 6: Grader — Batch Evaluation")
    print(f"{'='*80}")

    evaluator = EnhancedEvaluator()
    metrics = evaluator.evaluate_batch(cases, predictions)
    grader = DoctorGrader()
    result = grader.grade(cases, predictions, metrics.distribution_shift)

    print(f"\n  Accuracy:      {metrics.accuracy:.0%}")
    print(f"  Overconf:      {metrics.overconfidence_rate:.0%}")
    print(f"  Underconf:     {metrics.underconfidence_rate:.0%}")
    print(f"  Rule violations: {metrics.rule_violations}")
    print(f"  Correct by luck: {metrics.correct_by_luck_count}")
    print(f"  Wrong w/ violation: {metrics.wrong_with_violation_count}")
    print(f"\n  Grade:         {result['grade']:.4f} ({result['grade_letter']})")
    print(f"  Rule score:    {result['rule_score']:.4f}")
    print(f"  Wrong@HiConf:  {result['flags']['wrong_at_high_conf']*100:.1f}%")

    if 'breakdown' in result:
        bd = result['breakdown']
        print(f"\n  Per-class breakdown:")
        for cls in ['correct', 'partial', 'incorrect', 'undefined']:
            f1 = bd.get(f'{cls}_f1', 'N/A')
            rec = bd.get(f'{cls}_recall', 'N/A')
            if f1 != 'N/A':
                print(f"    {cls:12s}: F1={f1:.1%}  Recall={rec:.1%}")
            else:
                print(f"    {cls:12s}: F1=N/A  Recall=N/A")

    # ── Confusion Matrix ─────────────────────────────────────────────────
    print(f"\n  Confusion Matrix:")
    labels_order = ["correct", "partial", "incorrect", "undefined"]
    header = f"{'GT \\ Pred':<14}"
    for lbl in labels_order:
        header += f"{lbl:>12}"
    print(header)
    print("-" * len(header))
    cm = defaultdict(lambda: defaultdict(int))
    for case, pred in zip(cases, predictions):
        cm[case.ground_truth][pred['label']] += 1
    for gt in labels_order:
        row = f"{gt:<14}"
        for pred_lbl in labels_order:
            row += f"{cm[gt][pred_lbl]:>12}"
        print(row)

    # ── Side-by-Side Summary ─────────────────────────────────────────────
    print(f"\n{'='*80}")
    print(f"SIDEBY-SIDE SUMMARY")
    print(f"{'='*80}")
    print(f"\n{'Case':<16} {'GT':<12} {'Predicted':<12} {'Conf':>6} {'Match?':>8} {'Key Signals':<40}")
    print("-" * 94)
    for label, sol in SOLUTIONS.items():
        pred = None
        for c, p in zip(cases, predictions):
            if c.case_id == f"twosum-{label}":
                pred = p
                break
        match = "✓" if pred and pred['label'] == sol['ground_truth'] else "✗"
        key = ""
        if pred:
            bp = pred.get('system_bias_indicators', {})
            l1v = bp.get('layer1_verdict', '')
            l2v = bp.get('layer2_verdict', '') or ''
            l1viol = bp.get('layer1_violations', [])
            l2fps = [f['label'] for f in bp.get('layer2_failures', [])]
            parts = []
            if l1v:
                parts.append(f"L1={l1v}")
            if l1viol:
                parts.append(f"violations={l1viol}")
            if l2v:
                parts.append(f"L2={l2v}")
            if l2fps:
                parts.append(f"L2_fail={l2fps}")
            key = " | ".join(parts) if parts else pred.get('confidence_kind', '')
        print(f"{label:<16} {sol['ground_truth']:<12} {pred['label'] if pred else 'N/A':<12} "
              f"{pred['confidence'] if pred else 'N/A':>6} {match:>8} {key:<40}")

    print()


if __name__ == "__main__":
    main()

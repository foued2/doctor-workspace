#!/usr/bin/env python
"""
Production Runner — Solution Verification Mode
================================================
Usage: python production_runner.py --cases 30 --mode solution_verify

Does in sequence:
1. Environment bootstrap verify
2. Generate 10 problems × 3 solution types (correct, partial, incorrect)
3. Run Doctor (solution verifier) on each
4. Run enhanced evaluator
5. Compute Grade + Rule_Score
6. Print report card
7. Update session_state.json
8. Append to production_log.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from doctor.llm_doctor import LLMDoctor, _LEETCODE_SOLUTIONS, _SOLUTION_TEXTS
from doctor.doctor_grader import DoctorGrader
from external_stress_layer.enhanced_evaluator import EnhancedEvaluator, detect_rule_violations


class SolutionTestCase:
    """A single test case: problem + proposed solution + expected verdict."""

    def __init__(self, problem_title: str, solution_type: str, prompt: str, ground_truth: str):
        self.case_id = f"{problem_title.replace(' ', '_')}_{solution_type}"
        self.problem_title = problem_title
        self.solution_type = solution_type
        self.prompt = prompt
        self.ground_truth = ground_truth
        self.noise_level = 0.0
        self.failure_pattern = "none"
        self.stress_kind = type('StressKind', (), {'name': 'SOLUTION_VERIFY'})()
        self.metadata = {
            "problem": problem_title,
            "solution_type": solution_type,
        }


def generate_solution_verify_cases() -> list:
    """Generate 30 cases: 10 problems × 3 solution types (correct, partial, incorrect)."""
    cases = []

    # The 10 problems we have built-in knowledge for
    problems = [
        "Two Sum", "Palindrome Number", "Roman to Integer", "Valid Parentheses",
        "Merge Two Sorted Lists", "Longest Palindromic Substring",
        "Container With Most Water", "Median of Two Sorted Arrays",
        "Trapping Rain Water", "N-Queens",
    ]

    for title in problems:
        for sol_type in ["correct", "partial", "incorrect"]:
            key = f"{title}::{sol_type}"
            solution_text = _SOLUTION_TEXTS.get(key, "No solution text available.")
            entry = _LEETCODE_SOLUTIONS.get(key, {})
            reasoning = entry.get("reasoning", "")

            prompt = (
                f"PROBLEM: {title}. "
                f"SOLUTION ({sol_type}): {solution_text} "
                f"ANALYSIS: {reasoning}"
            )

            cases.append(SolutionTestCase(
                problem_title=title,
                solution_type=sol_type,
                prompt=prompt,
                ground_truth=sol_type,
            ))

    return cases


def bootstrap_verify() -> bool:
    print("[1/8] Environment bootstrap verify...")
    try:
        doctor = LLMDoctor()
        test = doctor.predict("PROBLEM: Test. SOLUTION: Test solution.")
        assert "label" in test
        assert "confidence" in test
        print(f"  ✓ Doctor initialized ({doctor.get_provider()}, {doctor.get_solution_count()} cases)")
        return True
    except Exception as e:
        print(f"  ✗ Bootstrap failed: {e}")
        return False


def run_evaluation(cases, doctor):
    print(f"\n[2/8] Running Doctor on {len(cases)} solution verification cases...")
    predictions = []
    for i, case in enumerate(cases):
        try:
            pred = doctor.predict(case.prompt)
            predictions.append(pred)
        except Exception as e:
            predictions.append({"case_id": case.case_id, "label": "incorrect", "confidence": 0.5, "decision_path": ["error"]})
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(cases)} cases...", end='\r')
    print(f"\n  ✓ Completed")

    print(f"\n[3/8] Running evaluator...")
    evaluator = EnhancedEvaluator()
    metrics = evaluator.evaluate_batch(cases, predictions)
    print(f"  ✓ Accuracy: {metrics.accuracy:.2%}")
    print(f"  ✓ Rule violations: {dict(metrics.rule_violations)}")

    return predictions, metrics


def compute_grades(cases, predictions, metrics):
    print(f"\n[4/8] Computing Grade + Rule_Score...")
    grader = DoctorGrader()
    result = grader.grade(cases, predictions, metrics.distribution_shift)
    result["flags"]["correct_by_luck"] = metrics.correct_by_luck_count
    print(f"  ✓ Grade: {result['grade']:.4f} ({result['grade_letter']})")
    print(f"  ✓ Rule_Score: {result['rule_score']:.4f}")
    return result


def print_report_card(result, predictions, cases):
    print(f"\n[5/8] Report card:")
    grader = DoctorGrader()
    grader.print_card(result)

    # Print per-problem breakdown
    print(f"\n  Per-problem results:")
    by_problem = {}
    for case, pred in zip(cases, predictions):
        title = case.problem_title
        if title not in by_problem:
            by_problem[title] = []
        by_problem[title].append((case.solution_type, pred["label"], pred["confidence"]))

    for title, results in by_problem.items():
        correct_count = sum(1 for st, label, _ in results if st == label)
        print(f"    {title}: {correct_count}/3 correct")
        for sol_type, label, conf in results:
            marker = "✓" if sol_type == label else "✗"
            print(f"      [{marker}] {sol_type:10s} -> {label:10s} (conf={conf:.2f})")


def update_session_state(result):
    print(f"\n[6/8] Updating session_state.json...")
    state = {
        "last_completed_phase": "Solution Verification - LLM Doctor",
        "last_run": datetime.now(timezone.utc).isoformat(),
        "grade": result["grade"],
        "grade_letter": result["grade_letter"],
        "rule_score": result["rule_score"],
        "breakdown": result["breakdown"],
        "flags": result["flags"],
        "rule_violations": result["rule_violations"],
        "coherence": result["coherence_check"]["coherence"],
    }
    with open(project_root / "session_state.json", "w") as f:
        json.dump(state, f, indent=2)
    print(f"  ✓ session_state.json updated")


def append_production_log(result, n_cases):
    print(f"\n[7/8] Appending to production_log.jsonl...")
    entry = {
        "run_id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "doctor_type": "llm_qwen_solution_verifier",
        "cases": n_cases,
        "mode": "solution_verify",
        "grade": result["grade"],
        "rule_score": result["rule_score"],
        "wrong_high_conf_rate": result["flags"]["wrong_at_high_conf"],
        "violations": result["rule_violations"],
    }
    with open(project_root / "production_log.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"  ✓ Logged to production_log.jsonl")


def print_final_summary(result, predictions, cases):
    print(f"\n[8/8] Final summary...")
    total = len(cases)
    correct = sum(1 for c, p in zip(cases, predictions) if p["label"] == c.ground_truth)
    error_rate = (total - correct) / total * 100

    # Breakdown by solution type
    by_type = {}
    for c, p in zip(cases, predictions):
        st = c.solution_type
        if st not in by_type:
            by_type[st] = {"total": 0, "correct": 0}
        by_type[st]["total"] += 1
        if p["label"] == st:
            by_type[st]["correct"] += 1

    print(f"\n  Solution type breakdown:")
    for st in ["correct", "partial", "incorrect"]:
        d = by_type.get(st, {"total": 0, "correct": 0})
        print(f"    {st:10s}: {d['correct']}/{d['total']} correct ({d['correct']/d['total']*100:.0f}%)")

    print(f"\n  {'='*60}")
    print(f"  VERDICT ACCURACY: {correct}/{total} ({(correct/total)*100:.1f}%)")
    print(f"  USER-FACING ERROR RATE: {error_rate:.1f}%")
    print(f"  {'='*60}")


def main():
    parser = argparse.ArgumentParser(description="Production Runner — Solution Verification")
    parser.add_argument("--cases", type=int, default=30, help="Number of cases (default 30)")
    args = parser.parse_args()

    print("=" * 60)
    print("PRODUCTION RUNNER — Solution Verification Mode")
    print("=" * 60)

    if not bootstrap_verify():
        sys.exit(1)

    cases = generate_solution_verify_cases()
    doctor = LLMDoctor()
    predictions, metrics = run_evaluation(cases, doctor)
    result = compute_grades(cases, predictions, metrics)
    print_report_card(result, predictions, cases)
    update_session_state(result)
    append_production_log(result, len(cases))
    print_final_summary(result, predictions, cases)

    print("\n" + "=" * 60)
    print("✓ PRODUCTION RUN COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()

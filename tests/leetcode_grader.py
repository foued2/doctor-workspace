"""
LeetCode Grader — Real-World Doctor Evaluation on Actual LeetCode Problems
==========================================================================

Runs the Doctor against 30 real LeetCode problems (10 Easy, 10 Medium, 10 Hard)
and produces a LeetCode-specific report card with user-facing error rate.
"""
from __future__ import annotations

import sys
import io
from pathlib import Path

# Bootstrap: ensure project root is in path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from collections import defaultdict
from typing import Any, Dict, List

from doctor.llm_doctor import LLMDoctor as ProductionDoctor
from doctor.llm_doctor import classify_with_llm
from external_stress_layer import StressCase, StressKind
from external_stress_layer.real_world_data_injector import REAL_LEETCODE_PROBLEMS
from external_stress_layer.enhanced_evaluator import EnhancedEvaluator, detect_rule_violations


def select_balanced_problems(problems: List[Dict], n_per_difficulty: int = 10) -> List[Dict]:
    """Select exactly n_per_difficulty problems from each difficulty level."""
    by_diff = defaultdict(list)
    for p in problems:
        by_diff[p["difficulty"]].append(p)
    
    selected = []
    for diff in ["Easy", "Medium", "Hard"]:
        pool = by_diff.get(diff, [])
        # Take first n_per_difficulty (they're already ordered by problem_id)
        selected.extend(pool[:n_per_difficulty])
    
    return selected


def build_leetcode_cases(problems: List[Dict]) -> List[StressCase]:
    """Convert LeetCode problem dicts into StressCase objects."""
    cases = []
    for p in problems:
        # Build prompt from problem description + constraints + ambiguity
        prompt = (
            f"PROBLEM: {p['title']} (LeetCode #{p['problem_id']}, {p['difficulty']})\n"
            f"DESCRIPTION: {p['description']}\n"
            f"CONSTRAINTS: {p.get('constraints', 'None specified')}\n"
            f"REAL-WORLD AMBIGUITY: {p.get('real_world_ambiguity', 'None')}"
        )
        
        case = StressCase(
            case_id=f"LC-{p['problem_id']:03d}",
            prompt=prompt,
            stress_kind=StressKind.REAL_WORLD,
            ground_truth=p["ground_truth"],
            metadata={
                "title": p["title"],
                "problem_id": p["problem_id"],
                "difficulty": p["difficulty"],
                "source": "leetcode_real",
            },
        )
        cases.append(case)
    
    return cases


def run_leetcode_evaluation(cases: List[StressCase], doctor: ProductionDoctor):
    """Run Doctor on all LeetCode cases and collect detailed results."""
    results = []
    
    for case in cases:
        pred = doctor.predict(case.prompt)
        violations = detect_rule_violations(case, pred)
        
        # Determine if verdict is correct
        verdict_correct = (pred["label"] == case.ground_truth)
        
        # Calculate grade contribution
        if verdict_correct:
            if pred["confidence"] >= 0.7:
                grade_contrib = 0.4
            else:
                grade_contrib = 0.2
        else:
            grade_contrib = 0.0
        
        results.append({
            "case": case,
            "prediction": pred,
            "violations": violations,
            "verdict_correct": verdict_correct,
            "grade_contrib": grade_contrib,
        })
    
    return results


def print_leetcode_report_card(results: List[Dict], cases: List[StressCase]):
    """Print the LeetCode-specific report card."""
    # Group by difficulty
    by_diff = defaultdict(lambda: {"correct": 0, "wrong": 0, "total": 0})
    for r in results:
        diff = r["case"].metadata["difficulty"]
        by_diff[diff]["total"] += 1
        if r["verdict_correct"]:
            by_diff[diff]["correct"] += 1
        else:
            by_diff[diff]["wrong"] += 1
    
    # Overall metrics
    total = len(results)
    correct_count = sum(1 for r in results if r["verdict_correct"])
    wrong_count = total - correct_count
    accuracy = correct_count / total if total > 0 else 0.0
    
    # Rule violations
    r1_count = sum(1 for r in results if "R1" in r["violations"])
    r2_count = sum(1 for r in results if "R2" in r["violations"])
    r3_count = sum(1 for r in results if "R3" in r["violations"])
    
    # Second-pass metrics
    correct_by_luck = sum(
        1 for r in results 
        if r["verdict_correct"] and len(r["violations"]) > 0
    )
    
    missed_undefined = sum(
        1 for r in results 
        if r["case"].ground_truth == "undefined" and r["prediction"]["label"] != "undefined"
    )
    
    undefined_recall_num = sum(
        1 for r in results 
        if r["case"].ground_truth == "undefined" and r["prediction"]["label"] == "undefined"
    )
    undefined_total = sum(1 for r in results if r["case"].ground_truth == "undefined")
    undefined_recall = (undefined_recall_num / undefined_total * 100) if undefined_total > 0 else 0.0
    
    # Grade calculation
    total_grade = sum(r["grade_contrib"] for r in results)
    max_grade = total * 0.4
    grade = total_grade / max_grade if max_grade > 0 else 0.0
    
    # Rule score (weighted violation rate)
    weighted_violations = r1_count * 1.0 + r2_count * 3.0 + r3_count * 2.0
    max_weighted = wrong_count * 3.0 if wrong_count > 0 else 1
    rule_score = 1.0 - (weighted_violations / max_weighted) if max_weighted > 0 else 1.0
    
    # Print report card
    print("\n" + "=" * 60)
    print("╔══════════════════════════════════════════════════════╗")
    print("║       LEETCODE GRADING RESULTS                      ║")
    print("╠══════════════════════════════════════════════════════╣")
    
    for diff in ["Easy", "Medium", "Hard"]:
        d = by_diff[diff]
        label = f"{diff:7s}"
        print(f"║ {label}({d['total']:2d}): {d['correct']:2d} correct  {d['wrong']:2d} wrong       ║")
    
    print("╠══════════════════════════════════════════════════════╣")
    
    # Grade letter
    if grade >= 0.9:
        grade_letter = "A"
    elif grade >= 0.8:
        grade_letter = "B"
    elif grade >= 0.7:
        grade_letter = "C"
    elif grade >= 0.6:
        grade_letter = "D"
    else:
        grade_letter = "F"
    
    print(f"║ Overall Grade:    {grade:.2f}  ({grade_letter}){' ' * 20}║")
    print(f"║ Rule_Score:       {rule_score:.2f}{' ' * 35}║")
    print(f"║ Undefined Recall: {undefined_recall:.1f}%{' ' * 34}║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ Failure breakdown:                                   ║")
    print(f"║   Missed undefined:  {missed_undefined:<42}║")
    print(f"║   Contradiction blind: {r1_count:<40}║")
    print(f"║   Correct by luck:   {correct_by_luck:<40}║")
    print("╚══════════════════════════════════════════════════════╝")
    print("=" * 60)
    
    return {
        "accuracy": accuracy,
        "grade": grade,
        "grade_letter": grade_letter,
        "rule_score": rule_score,
        "undefined_recall": undefined_recall,
        "missed_undefined": missed_undefined,
        "contradiction_blind": r1_count,
        "correct_by_luck": correct_by_luck,
        "r1_violations": r1_count,
        "r2_violations": r2_count,
        "r3_violations": r3_count,
        "wrong_count": wrong_count,
        "total": total,
    }


def print_problem_verdicts(results: List[Dict]):
    """Print per-problem verdict details."""
    print("\n" + "=" * 60)
    print("DETAILED PROBLEM VERDICTS")
    print("=" * 60)
    
    for r in results:
        case = r["case"]
        pred = r["prediction"]
        title = case.metadata["title"]
        diff = case.metadata["difficulty"]
        
        violations_str = ", ".join(r["violations"]) if r["violations"] else "none"
        reasoning = _summarize_reasoning(pred, r["violations"])
        
        print(f"\nProblem: {title} ({diff})")
        print(f"  Doctor Verdict:    {pred['label']}")
        print(f"  Confidence:        {pred['confidence']}")
        print(f"  Ground Truth:      {case.ground_truth}")
        print(f"  Correct:           {'✓' if r['verdict_correct'] else '✗'}")
        print(f"  Rule Violations:   {violations_str}")
        print(f"  Reasoning:         {reasoning}")
        print(f"  Grade contribution: +{r['grade_contrib']}")


def _summarize_reasoning(pred: Dict, violations: List[str]) -> str:
    """Generate one-line summary of Doctor's reasoning."""
    decision_path = pred.get("decision_path", [])
    if not decision_path:
        return "No decision path available"
    
    path_str = " → ".join(decision_path[:2])
    
    if violations:
        return f"Path: {path_str} [VIOLATIONS: {', '.join(violations)}]"
    else:
        return f"Path: {path_str} [Sound reasoning]"


def compute_user_facing_error_rate(results: List[Dict]) -> Dict[str, float]:
    """Compute the user-facing error rate on real LeetCode problems.
    
    This is the percentage of problems where a user would get a wrong verdict
    if relying on the Doctor's classification in a live grading scenario.
    """
    total = len(results)
    wrong_verdicts = sum(1 for r in results if not r["verdict_correct"])
    wrong_with_violations = sum(
        1 for r in results 
        if not r["verdict_correct"] and len(r["violations"]) > 0
    )
    correct_by_luck = sum(
        1 for r in results 
        if r["verdict_correct"] and len(r["violations"]) > 0
    )
    high_conf_wrong = sum(
        1 for r in results 
        if not r["verdict_correct"] and r["prediction"]["confidence"] >= 0.7
    )
    
    # User-facing error rate: verdicts that are wrong
    user_error_rate = wrong_verdicts / total if total > 0 else 0.0
    
    # Dangerous error rate: wrong AND high confidence (user will trust it)
    dangerous_error_rate = high_conf_wrong / total if total > 0 else 0.0
    
    # Unreliable rate: correct verdict but with violations (right for wrong reasons)
    unreliable_rate = correct_by_luck / total if total > 0 else 0.0
    
    return {
        "user_error_rate": user_error_rate,
        "user_error_pct": user_error_rate * 100,
        "dangerous_error_rate": dangerous_error_rate,
        "dangerous_error_pct": dangerous_error_rate * 100,
        "unreliable_rate": unreliable_rate,
        "unreliable_pct": unreliable_rate * 100,
        "total_problems": total,
        "wrong_verdicts": wrong_verdicts,
        "high_conf_wrong": high_conf_wrong,
        "correct_by_luck": correct_by_luck,
    }


def run_leetcode_test():
    """Main entry point: run the full LeetCode evaluation."""
    print("=" * 60)
    print("LEETCODE PRODUCTION TEST")
    print("=" * 60)
    
    # Step 1: Select balanced problem set
    print("\n[Step 1] Building LeetCode test set...")
    problems = select_balanced_problems(REAL_LEETCODE_PROBLEMS, n_per_difficulty=10)
    
    # Verify distribution
    from collections import Counter
    dist = Counter(p["difficulty"] for p in problems)
    print(f"  Selected: {len(problems)} problems")
    print(f"  Distribution: Easy={dist['Easy']}, Medium={dist['Medium']}, Hard={dist['Hard']}")
    
    # Step 2: Build cases
    print("\n[Step 2] Converting to test cases...")
    cases = build_leetcode_cases(problems)
    print(f"  Built {len(cases)} StressCase objects")
    
    # Step 3: Run Doctor
    print("\n[Step 3] Running Doctor on 30 LeetCode problems...")
    doctor = ProductionDoctor()
    results = run_leetcode_evaluation(cases, doctor)
    print(f"  ✓ Completed {len(results)} predictions")
    
    # Step 4: Print detailed verdicts
    print_problem_verdicts(results)
    
    # Step 5: Print report card
    metrics = print_leetcode_report_card(results, cases)
    
    # Step 6: Compute user-facing error rate
    print("\n[Step 6] Computing user-facing error rate...")
    error_stats = compute_user_facing_error_rate(results)
    
    print("\n" + "=" * 60)
    print("USER-FACING ERROR RATE ANALYSIS")
    print("=" * 60)
    print(f"\n  Total problems tested:     {error_stats['total_problems']}")
    print(f"  Wrong verdicts:            {error_stats['wrong_verdicts']}")
    print(f"  High-confidence wrong:     {error_stats['high_conf_wrong']}")
    print(f"  Correct by luck:           {error_stats['correct_by_luck']}")
    print(f"\n  ┌─────────────────────────────────────────────────┐")
    print(f"  │ USER-FACING ERROR RATE: {error_stats['user_error_pct']:5.1f}%{' ' * 20}│")
    print(f"  │ Dangerous error rate:   {error_stats['dangerous_error_pct']:5.1f}%{' ' * 20}│")
    print(f"  │ Unreliable (luck):      {error_stats['unreliable_pct']:5.1f}%{' ' * 20}│")
    print(f"  └─────────────────────────────────────────────────┘")
    
    # Gap analysis
    print("\n" + "=" * 60)
    print("GAP ANALYSIS")
    print("=" * 60)
    
    if error_stats['user_error_pct'] < 20:
        verdict = "ACCEPTABLE for limited production use"
    elif error_stats['user_error_pct'] < 40:
        verdict = "MARGINAL — needs improvement before production"
    else:
        verdict = "UNACCEPTABLE — Doctor not ready for production"
    
    print(f"\n  Current Doctor grade: {metrics['grade']:.2f} ({metrics['grade_letter']})")
    print(f"  User-facing error rate: {error_stats['user_error_pct']:.1f}%")
    print(f"  Verdict: {verdict}")
    
    print(f"\n  At current grade, {error_stats['wrong_verdicts']} out of {error_stats['total_problems']} "
          f"LeetCode problems would receive wrong verdicts in a live grading scenario.")
    print(f"  This translates to a {error_stats['user_error_pct']:.1f}% user-facing error rate.")
    
    if error_stats['dangerous_error_pct'] > 10:
        print(f"\n  ⚠ WARNING: {error_stats['dangerous_error_pct']:.1f}% of problems get wrong verdicts "
              f"at high confidence — users will trust incorrect results.")
    
    if metrics['correct_by_luck'] > 5:
        print(f"  ⚠ WARNING: {metrics['correct_by_luck']} cases get right answer for wrong reasons "
              f"(rule violations present). Reasoning is unreliable.")
    
    if metrics['missed_undefined'] > 3:
        print(f"  ⚠ WARNING: {metrics['missed_undefined']} undefined cases misclassified — "
              f"Doctor fails to recognize genuinely ambiguous specifications.")
    
    print("\n" + "=" * 60)
    print(f"PUBLIC-FACING METRIC: {error_stats['user_error_pct']:.1f}% ERROR RATE ON REAL LEETCODE PROBLEMS")
    print("=" * 60)
    
    return {
        "metrics": metrics,
        "error_stats": error_stats,
        "results": results,
    }


if __name__ == "__main__":
    run_leetcode_test()

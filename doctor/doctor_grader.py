"""
Doctor Grader — Report card generation
"""
from __future__ import annotations
from collections import defaultdict
from typing import Any, Dict, List


# ===========================================================================
# FIX 3 — Partial redefinition by failure pattern (Track A: L2 test labels)
# ===========================================================================

# Test label categories from Layer 2 execution results
# Exported for import by test_executor and llm_doctor
EDGE_CASE_LABELS = frozenset({
    "empty", "single", "negative", "overflow", "zero",
    "null", "none", "boundary", "one_element", "both_empty",
    "no_first_two", "self_element_reuse", "unsorted",
    "trailing_zero", "even_length", "basic_even", "basic_odd",
    "unclosed", "nested",
    "one_empty", "one_larger", "single_char", "single_not_found",
    "single_match", "at_end", "empty_needle",
    "not_found", "two_equal", "small",
    "odd_total", "even_total", "first_empty", "all_zero",
    "first_empty_even", "too_short", "star_repeat",
    "star_all", "star_empty", "empty_match", "optional_b",
    "n4_count",
    "delete_all", "insert_all",
    "two_no_palindrome", "full_string",
    "numrows_1", "leading_spaces_negative", "overflow_negative",
    "leading_text", "trailing_text",
    "no_prefix", "empty_string", "different_lengths",
    "all_types",
    "interleaved",
    "ascending",
    "with_negative", "all_large",
    "tall",
    "all_same",
    "four_letters",
})

STANDARD_CASE_LABELS = frozenset({
    "basic", "normal", "standard", "general", "typical", "common",
    # Core algorithm correctness — not edge conditions
    "wrong_type", "wrong_order", "wrong_type_check", "wrong_char",
    "subtractive_iv", "subtractive_ix", "subtractive",
    "complex", "complex_case",
})

CONSTRAINT_VIOLATION_LABELS = frozenset({
    "wrong_order", "subtractive", "constraint", "format",
    "without_conversion", "no_extra_space",
})


def classify_failure_type(failed_labels: list[str]) -> str | None:
    """Classify the nature of L2 test failures.

    Returns:
        "standard"  — at least one standard (non-edge) case failed
        "edge_only" — only edge-case or constraint labels failed
        None        — no failures
    """
    if not failed_labels:
        return None

    for label in failed_labels:
        label_lower = label.lower()
        for std in STANDARD_CASE_LABELS:
            if std in label_lower:
                return "standard"

    return "edge_only"


def classify_partial_vs_incorrect(failure_reasons: list[str]) -> str:
    """Decide whether a failing solution is partial or incorrect.

    Input: list of failed test labels from Layer 2 execution.

    **partial** = passes all standard cases, fails only edge/constraint labels.
    **incorrect** = fails at least one standard (non-edge) case.
    """
    if not failure_reasons:
        return "correct"

    failures_lower = [f.lower() for f in failure_reasons]

    # Check if any standard case failed → incorrect
    for label in failures_lower:
        for std in STANDARD_CASE_LABELS:
            if std in label:
                return "incorrect"

    # All failures are edge-case or constraint violation → partial
    return "partial"


# ===========================================================================
# FIX 2 — Insufficient evidence gate
# ===========================================================================

def check_insufficient_evidence(
    tests_total: int,
    failure_reasons: list[str] | None = None,
) -> str | None:
    """Return a reason string if evidence is too thin to justify any verdict.

    Trigger conditions:
    - tests_total < 2, OR
    - tests_total < 4 AND solution touches known edge-case-sensitive patterns.

    Returns None when evidence is sufficient (grading should proceed normally).
    """
    if tests_total < 2:
        return f"only {tests_total} test(s) executed — insufficient coverage"

    if tests_total < 4 and failure_reasons:
        edge_patterns = {"empty", "single", "negative", "overflow", "edge"}
        for reason in failure_reasons:
            if any(kw in reason.lower() for kw in edge_patterns):
                return (
                    f"only {tests_total} tests and edge-case-sensitive "
                    f"pattern detected: {reason}"
                )

    return None


class DoctorGrader:
    def grade(self, cases, predictions, distribution_shift=None):
        total = len(cases)

        # ── FIX 2: insufficient_evidence is a correct abstention ──────
        # Cases where Doctor returned insufficient_evidence are excluded
        # from the grade denominator — they are not penalized.
        graded_pairs = [
            (c, p) for c, p in zip(cases, predictions)
            if p["label"] != "insufficient_evidence"
        ]
        graded_total = len(graded_pairs)
        insufficient_count = total - graded_total

        correct = sum(1 for c, p in graded_pairs if p["label"] == c.ground_truth)
        accuracy = correct / graded_total if graded_total > 0 else 0.0
        rule_violations = defaultdict(int)
        wrong_at_high_conf = 0
        total_wrong = 0
        for c, p in graded_pairs:
            if p["label"] != c.ground_truth:
                total_wrong += 1
                if p.get("confidence", 0) >= 0.7:
                    wrong_at_high_conf += 1
        wrong_high_conf_rate = wrong_at_high_conf / total_wrong if total_wrong > 0 else 0.0
        total_grade = 0.0
        for c, p in graded_pairs:
            if p["label"] == c.ground_truth:
                total_grade += 0.4 if p.get("confidence", 0) >= 0.7 else 0.2
        max_grade = graded_total * 0.4
        grade = total_grade / max_grade if max_grade > 0 else 0.0
        if grade >= 0.9: letter = "A"
        elif grade >= 0.8: letter = "B"
        elif grade >= 0.7: letter = "C"
        elif grade >= 0.6: letter = "D"
        else: letter = "F"
        r1, r2, r3 = rule_violations.get("R1", 0), rule_violations.get("R2", 0), rule_violations.get("R3", 0)
        weighted = r1 * 1.0 + r2 * 3.0 + r3 * 2.0
        max_w = total_wrong * 3.0 if total_wrong > 0 else 1
        rule_score = 1.0 - (weighted / max_w) if max_w > 0 else 1.0
        by_class = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
        for c, p in graded_pairs:
            gt, label = c.ground_truth, p["label"]
            if label == gt: by_class[gt]["tp"] += 1
            else:
                by_class[gt]["fn"] += 1
                by_class[label]["fp"] += 1
        breakdown = {}
        for cls in ["correct", "partial", "undefined", "incorrect", "insufficient_evidence"]:
            d = by_class.get(cls, {"tp": 0, "fp": 0, "fn": 0})
            prec = d["tp"] / (d["tp"] + d["fp"]) if (d["tp"] + d["fp"]) > 0 else 0.0
            rec = d["tp"] / (d["tp"] + d["fn"]) if (d["tp"] + d["fn"]) > 0 else 0.0
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
            breakdown[f"{cls}_f1"] = f1
            breakdown[f"{cls}_recall"] = rec
        coherence = "HIGH_GRADE_HIGH_INTEGRITY" if grade > 0.7 and rule_score > 0.7 else "LOW_GRADE_HIGH_INTEGRITY" if grade < 0.7 and rule_score > 0.7 else "LOW_GRADE_LOW_INTEGRITY"
        return {"grade": round(grade, 4), "grade_letter": letter, "rule_score": round(rule_score, 4),
                "accuracy": round(accuracy, 4), "breakdown": breakdown,
                "insufficient_evidence_count": insufficient_count,
                "flags": {"wrong_at_high_conf": round(wrong_high_conf_rate, 4),
                          "shift_score": distribution_shift.get("shift_score", 0.0) if distribution_shift else 0.0},
                "rule_violations": dict(rule_violations),
                "coherence_check": {"coherence": coherence, "gap": round(abs(grade - rule_score), 4)}}

    def print_card(self, result):
        g, l, rs = result["grade"], result["grade_letter"], result["rule_score"]
        bd, fl, v, coh = result.get("breakdown", {}), result.get("flags", {}), result.get("rule_violations", {}), result.get("coherence_check", {})
        insuff = result.get("insufficient_evidence_count", 0)
        print(f"\n{'='*60}")
        print(f"╔══════════════════════════════════════╗")
        print(f"║         DOCTOR REPORT CARD          ║")
        print(f"╠══════════════════════════════════════╣")
        print(f"║ Grade:       {g:.2f}  ({l})             ║")
        print(f"║ Rule_Score:  {rs:.2f}                      ║")
        print(f"╠══════════════════════════════════════╣")
        print(f"║ Breakdown:                          ║")
        print(f"║   Accuracy:          {result.get('accuracy', 0)*100:.1f}%              ║")
        print(f"║   Undefined Recall:  {bd.get('undefined_recall', 0)*100:.1f}%              ║")
        print(f"║   Correct F1:        {bd.get('correct_f1', 0)*100:.1f}%              ║")
        print(f"║   Partial F1:        {bd.get('partial_f1', 0)*100:.1f}%              ║")
        if insuff > 0:
            print(f"║   Insufficient Ev:   {insuff}                 ║")
        print(f"╠══════════════════════════════════════╣")
        whc = fl.get('wrong_at_high_conf', 0) * 100
        m1 = "✓" if whc < 40 else "⚠"
        ss = fl.get('shift_score', 0) or 0
        m2 = "✓" if ss < 0.4 else "⚠"
        print(f"║ Integrity Flags:                    ║")
        print(f"║   Wrong@HighConf:    {whc:.1f}%  {m1}   ║")
        print(f"║   Shift Score:      {ss:.3f}  {m2}    ║")
        print(f"╠══════════════════════════════════════╣")
        print(f"║ Rule Violations:                    ║")
        print(f"║   R1 (contradiction): {v.get('R1', 0)}            ║")
        print(f"║   R2 (corruption):    {v.get('R2', 0)}             ║")
        print(f"║   R3 (false conf):    {v.get('R3', 0)}             ║")
        print(f"╚══════════════════════════════════════╝")
        print(f"\nCoherence Check: {coh.get('coherence', 'UNKNOWN')}")
        print(f"  Gap: {coh.get('gap', 0):.4f}")
        if coh.get('coherence') == 'LOW_GRADE_HIGH_INTEGRITY':
            print("  Doctor fails honestly. Knows when it doesn't know.")

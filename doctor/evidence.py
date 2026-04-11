"""
Evidence-based verification-completeness estimator.

Computes evidence strength from execution artifacts only.
Determines the final label by comparing AI verdict
against execution evidence.

Output is a trust diagnostic, not a score.
"""


def compute_evidence_strength(tests_total, tests_passed, branches_covered=0):
    """
    Measures verification completeness from execution artifacts only.
    
    Operating boundary: returns 0.0 for any problem with no execution tests.
    This is a policy choice — absence of tests = absence of grounding.
    The system does not estimate correctness; it estimates whether
    correctness has been empirically sampled at all.
    
    No linguistic, reasoning, or model-derived signals are used.
    """
    if tests_total == 0:
        return 0.0
    execution_signal = min(tests_total / 10, 1.0)
    pass_signal = tests_passed / tests_total
    return round(execution_signal * 0.6 + pass_signal * 0.4, 3)


def get_final_label(ai_verdict: str, execution_pass_rate: float,
                    evidence_strength: float, ai_confidence: float):
    """
    Determines final label by comparing AI verdict against execution evidence.

    Hard failure flags:
    - FAIL if AI_confidence > evidence_strength
    - HARD RULE: high confidence on weak evidence → suspicious
    """
    # ── HARD RULE: Overconfident AI on weak evidence ──────────────────
    if ai_confidence >= 0.9 and evidence_strength < 0.4:
        return "suspicious", "FAIL:overconfident_on_weak_evidence"

    exec_verdict = "correct" if execution_pass_rate == 1.0 else "incorrect"
    agreement = ai_verdict == exec_verdict

    flag = None
    if ai_confidence > evidence_strength:
        flag = "FAIL:confidence_exceeds_evidence"

    if agreement and evidence_strength >= 0.7:
        label = "strong_correct" if ai_verdict == "correct" else "clear_incorrect"
    elif agreement and evidence_strength < 0.4:
        label = "suspicious_correct" if ai_verdict == "correct" else "weak_rejection"
    elif not agreement:
        label = "contradiction"
    else:
        # Moderate evidence (0.4-0.7) with agreement
        label = "suspicious_correct" if ai_verdict == "correct" else "weak_rejection"

    return label, flag

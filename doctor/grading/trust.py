"""
Trust assessment v1.3 — hierarchical epistemic classifier.

DECISION CONTRACT (v1.3):
    PRIMARY   = type  (diagnosis — failure mode classification)
    SECONDARY = risk  (severity bucket — derived from type, for aggregation only)

This is NOT a triage system. It is a diagnostic system.

Three signals:
    E ∈ {0,1}     oracle correctness (from test execution)
    e ∈ [0,1]     evidence_score (test-based evidence strength)
    c ∈ [0,1]     model_confidence (external belief, from LLM)

Output hierarchy:
    type  — PRIMARY. Use this for all decisions, analysis, and interpretation.
            Encodes: failure mechanism, evidence quality, calibration state.
    risk  — SECONDARY. Derived from type. Use ONLY for aggregation/compression.
            Does NOT drive decisions. Exists for backward compatibility.

Key invariants:
    1. Confidence is only "safe" if evidence is strong enough.
    2. Correct answer != justified confidence.
    3. LOW requires strong justification (e >= 0.7).

Failure modes detected:
    - overconfident_wrong        → model failure (E=0, c high)
    - belief_exceeds_evidence    → calibration failure (E=0, c > e)
    - false_justified_confidence → data limitation masquerading as correctness (E=1, e<0.6, c>=0.8)
    - aligned_but_weak_evidence  → data limitation signal (E=1, e<0.7, c aligned)
    - underconfident_correct     → model calibration signal (E=1, c < e)
    - strong_underconfidence     → severe calibration mismatch
    - aligned_confident_correct  → correct and well-supported
    - expected_failure           → known failure mode (E=0, both low)
    - uncertain_wrong            → unclear failure origin (E=0, moderate)

v1.3 changes:
    - Enforced type-as-primary, risk-as-derived hierarchy
    - risk field is now computed from type, not independently
    - Documented decision contract explicitly
"""

# ── Thresholds ──────────────────────────────────────────────────────
HIGH = 0.75
LOW = 0.4
DELTA_CRITICAL = 0.4
EVIDENCE_FLOOR = 0.6
EVIDENCE_STRONG = 0.7
CONFIDENCE_HIGH = 0.8

# ── Risk derivation table (SECONDARY — derived from type) ────────────
# DO NOT use this for decisions. Use 'type' instead.
_TYPE_TO_RISK = {
    "aligned_confident_correct": "LOW",
    "aligned_but_weak_evidence": "MEDIUM",
    "underconfident_correct": "MEDIUM",
    "strong_underconfidence": "MEDIUM",
    "weakly_supported_correct": "MEDIUM",
    "false_justified_confidence": "HIGH",
    "uncertain_wrong": "HIGH",
    "expected_failure": "LOW",
    "overconfident_wrong": "CRITICAL",
    "belief_exceeds_evidence": "CRITICAL",
}


def compute_trust_v1(E: int, e: float, c: float) -> dict:
    """
    Hierarchical epistemic classifier.

    Args:
        E: oracle correctness (1 = correct, 0 = incorrect)
        e: evidence_score — test-based evidence strength
        c: model_confidence — external belief from LLM

    Returns:
        dict with:
            type:  PRIMARY. Failure mode classification. Use for decisions.
            risk:  SECONDARY. Severity bucket, derived from type.
                   For aggregation/compression only.
            delta: signed mismatch (c - e)
            E, e, c: input signals

    Example:
        result = compute_trust_v1(1, 0.3, 0.85)
        result["type"]   # "false_justified_confidence" — use this
        result["risk"]   # "HIGH" — for aggregation only
    """
    delta = round(c - e, 4)

    # ── Step 1: Classify failure mode (PRIMARY) ─────────────────────
    if E == 1:
        if e < EVIDENCE_FLOOR and c >= CONFIDENCE_HIGH:
            trust_type = "false_justified_confidence"
        elif abs(delta) <= 0.2 and e >= EVIDENCE_STRONG:
            trust_type = "aligned_confident_correct"
        elif abs(delta) <= 0.2 and e < EVIDENCE_STRONG:
            trust_type = "aligned_but_weak_evidence"
        elif c < e - DELTA_CRITICAL:
            trust_type = "strong_underconfidence"
        elif c < e:
            trust_type = "underconfident_correct"
        else:
            trust_type = "weakly_supported_correct"
    else:
        if c >= HIGH:
            trust_type = "overconfident_wrong"
        elif delta >= DELTA_CRITICAL:
            trust_type = "belief_exceeds_evidence"
        elif c < LOW and e < LOW:
            trust_type = "expected_failure"
        else:
            trust_type = "uncertain_wrong"

    # ── Step 2: Derive risk from type (SECONDARY) ──────────────────
    risk = _TYPE_TO_RISK[trust_type]

    return {
        "type": trust_type,
        "risk": risk,
        "delta": delta,
        "E": E,
        "e": e,
        "c": c,
    }


# ── Legacy function (kept for backward compatibility) ─────────────
def compute_risk(ai_confidence: float, evidence_strength: float) -> dict:
    """
    Legacy risk computation.

    DEPRECATED: Use compute_trust_v1 instead.
    This function remains for backward compatibility with existing callers.
    """
    risk = round(ai_confidence * (1 - evidence_strength), 3)
    flagged = ai_confidence >= 0.9 and evidence_strength < 0.4
    return {
        "risk": risk,
        "flagged": flagged,
    }

"""
Failure Capture + Error Taxonomy
=================================
Foundation layer for adaptive adversary.

Every evaluation failure is logged with structured metadata.
Failures are the raw material the adaptive generator learns from.

Storage:
    adversarial_memory/failures.jsonl    — append-only failure log
    adversarial_memory/patterns.json      — extracted failure patterns
    adversarial_memory/generator_state.json — weights, novelty hashes
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# ── Error Taxonomy (non-negotiable) ──────────────────────────────────────────
ERROR_TYPES = {
    "false_positive",            # said correct when truth != correct
    "false_negative",            # said not-correct when truth == correct
    "missed_contradiction",      # failed to detect rule-vs-example conflict
    "trusted_corrupted_label",   # used a wrong sample output as authoritative
    "fooled_by_formatting",      # awarded higher grade due to polished look
    "failed_undefined_detection",# truth=undefined but system gave definitive answer
    "overconfident_answer",       # high confidence on wrong verdict
    "correct_by_luck",            # PHASE 5: verdict correct but reasoning broken
}

# ── PHASE 2: Rule Violation Taxonomy ─────────────────────────────────────────
# These are integrity violations, not just classification errors.
RULE_VIOLATIONS = {
    "R1",  # Contradiction blindness
    "R2",  # Corruption trust
    "R3",  # False confidence
}

# ── Paths ─────────────────────────────────────────────────────────────────────
MEMORY_ROOT = Path(__file__).resolve().parent.parent / "adversarial_memory"


def _ensure_memory_dir():
    MEMORY_ROOT.mkdir(parents=True, exist_ok=True)


# ── Step 1: Failure Classification ───────────────────────────────────────────

def classify_error(case: Dict[str, Any], prediction: Dict[str, Any]) -> Dict[str, Any]:
    """Classify a prediction error into error types and rule violations.

    Returns a dict with:
        - error_types: list of ERROR_TYPES strings
        - rule_violations: list of RULE_VIOLATIONS strings (R1, R2, R3)
    """
    errors = []
    violations = []
    
    truth = case["ground_truth"]
    label = prediction["label"]
    confidence = float(prediction.get("confidence", 0.5))
    matched = (label == truth)

    if matched:
        return {"error_types": [], "rule_violations": []}

    # Core misclassifications
    if truth != "correct" and label == "correct":
        errors.append("false_positive")
    if truth == "correct" and label != "correct":
        errors.append("false_negative")

    # Undefined detection failure
    if truth == "undefined" and label != "undefined":
        errors.append("failed_undefined_detection")

    # Contradiction miss
    if case.get("contradiction") and not prediction.get("conflict_detected"):
        errors.append("missed_contradiction")

    # Corrupted label trust
    if case.get("corrupted_label") and prediction.get("used_sample_output"):
        errors.append("trusted_corrupted_label")

    # Formatting fool
    if case.get("signal_inversion") and not matched and confidence >= 0.7:
        errors.append("fooled_by_formatting")

    # Overconfidence on wrong answer
    if not matched and confidence >= 0.8:
        errors.append("overconfident_answer")

    # ── PHASE 2: Rule Violation Detection ────────────────────────────────────
    
    # R1: Contradiction blindness
    # Case contains contradiction signal AND doctor verdict is correct/partial
    # AND doctor reasoning does not mention contradiction
    has_contradiction = (
        case.get("contradiction", False) or
        case.get("has_contradiction", False)
    )
    prompt = case.get("prompt", "").lower()
    contradiction_keywords = ["contradict", "conflict", "inconsistent", "incompatible", "disagree"]
    has_contradiction_keyword = any(kw in prompt for kw in contradiction_keywords)
    
    if (has_contradiction or has_contradiction_keyword) and label in ("correct", "partial"):
        decision_path = prediction.get("decision_path", [])
        decision_path_str = " ".join(decision_path).lower()
        mentions_contradiction = any(
            kw in decision_path_str 
            for kw in ["contradict", "conflict", "R2", "conflicting_examples"]
        )
        if not mentions_contradiction:
            violations.append("R1")
    
    # R2: Corruption trust
    # Case has corrupted label flag AND doctor verdict used sample evidence
    has_corrupted_label = (
        case.get("corrupted_label", False) or
        case.get("has_corrupted_label", False)
    )
    used_sample_evidence = prediction.get("used_sample_output", False)
    decision_path = prediction.get("decision_path", [])
    decision_path_str = " ".join(decision_path).lower()
    mentions_sample = any(kw in decision_path_str for kw in ["sample", "example", "expected_output"])
    
    # R2 also fires when corrupted label case is classified as "correct" without flagging
    corrupted_but_not_flagged = (
        has_corrupted_label and
        label == "correct" and
        not prediction.get("conflict_detected", False)
    )
    
    if has_corrupted_label and (used_sample_evidence or mentions_sample or corrupted_but_not_flagged):
        violations.append("R2")
    
    # R3: False confidence
    # Ground truth is undefined AND doctor returned correct or partial
    if truth == "undefined" and label in ("correct", "partial"):
        violations.append("R3")

    return {"error_types": errors, "rule_violations": violations}


# ── Step 2: Persistent Failure Logging ───────────────────────────────────────

def log_failure(
    case: Dict[str, Any],
    prediction: Dict[str, Any],
    error_classification: Dict[str, List[str]],
) -> Dict[str, Any]:
    """Append a single failure record to failures.jsonl.

    Args:
        case: The stress case dict
        prediction: The doctor prediction dict
        error_classification: Dict from classify_error() with 'error_types' and 'rule_violations'

    Returns the full failure record dict.
    """
    _ensure_memory_dir()
    failures_path = MEMORY_ROOT / "failures.jsonl"

    error_types = error_classification.get("error_types", [])
    rule_violations = error_classification.get("rule_violations", [])

    record = {
        "case_id": case["case_id"],
        "stratum": case["stratum"],
        "ground_truth": case["ground_truth"],
        "doctor_label": prediction["label"],
        "doctor_confidence": prediction.get("confidence", 0.0),
        "error_types": error_types,
        "rule_violations": rule_violations,  # PHASE 2: New field
        "features": {
            "signal_inversion": case.get("signal_inversion", False),
            "contradiction": case.get("contradiction", False),
            "corrupted_label": case.get("corrupted_label", False),
        },
        "prompt_hash": _hash_prompt(case.get("prompt", "")),
    }

    with open(failures_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record


# ── Step 3: Pattern Extractor ────────────────────────────────────────────────

def extract_pattern(case: Dict[str, Any], error_types: List[str]) -> Dict[str, Any]:
    """Convert a failure into a reusable attack template.

    Patterns are the minimal structural description of a failing case.

    PHASE 4: Added provenance tracking fields.
    """
    prompt = case.get("prompt", "")
    structure = _extract_prompt_structure(prompt)

    # Derive rule_target from case metadata or rule_violations
    rule_violations = case.get("rule_violations", [])
    if rule_violations:
        rule_target = max(rule_violations, key=lambda r: {"R2": 3.0, "R3": 2.0, "R1": 1.0}.get(r, 0.0))
    else:
        rule_target = None

    return {
        "stratum": case["stratum"],
        "error_types": error_types,
        "rule_violations": rule_violations,
        "rule_target": rule_target,
        "has_contradiction": case.get("contradiction", False),
        "has_corruption": case.get("corrupted_label", False),
        "signal_inversion": case.get("signal_inversion", False),
        "is_ambiguous": case.get("is_ambiguous", False),
        "truth": case["ground_truth"],
        "prompt_structure": structure,
        "prompt_text": prompt[:200],  # First 200 chars for novelty comparison
        "count": 1,
        "failure_count": 1,
        "mutation_count": 0,
        "escalation_level": 0,
        # PHASE 4: Provenance tracking
        "origin": case.get("origin", "internal_generator"),
        "escalation_level_label": case.get("escalation_level_label", "L0"),
        "last_used": datetime.now(timezone.utc).isoformat(),
        "retired": False,
        "retirement_reason": None,
    }


def _extract_prompt_structure(prompt: str) -> Dict[str, Any]:
    """Extract minimal structural features from a prompt.

    Returns a small dict suitable for hashing and comparison.
    """
    return {
        "length": len(prompt),
        "has_extra_detail": "Extra detail:" in prompt,
        "has_redundant_note": "Redundant note:" in prompt,
        "has_supervisor_note": "supervisor note" in prompt.lower(),
        "has_missing_constraint": "missing" in prompt.lower() and "constraint" in prompt.lower(),
        "word_count": len(prompt.split()),
    }


def _hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]


# ── Step 4: Pattern Registry (persistent) ────────────────────────────────────

def load_patterns() -> List[Dict[str, Any]]:
    path = MEMORY_ROOT / "patterns.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_patterns(patterns: List[Dict[str, Any]]) -> None:
    _ensure_memory_dir()
    (MEMORY_ROOT / "patterns.json").write_text(
        json.dumps(patterns, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def register_failure_pattern(case: Dict[str, Any], error_classification: Dict[str, List[str]]) -> None:
    """Register or update a failure pattern.

    If an identical pattern exists, increment its count.
    Otherwise create a new pattern entry.

    Args:
        case: The stress case dict
        error_classification: Dict from classify_error() with 'error_types' and 'rule_violations'
    """
    error_types = error_classification.get("error_types", [])
    rule_violations = error_classification.get("rule_violations", [])

    # Ensure rule_violations are in the case dict for extract_pattern to use
    case_with_rules = {**case, "rule_violations": rule_violations}

    new_pattern = extract_pattern(case_with_rules, error_types)

    patterns = load_patterns()

    new_hash = _pattern_hash(new_pattern)
    found = False

    for p in patterns:
        if _pattern_hash(p) == new_hash:
            p["count"] = p.get("count", 1) + 1
            p["failure_count"] = p.get("failure_count", 0) + 1
            p["last_used"] = datetime.now(timezone.utc).isoformat()
            found = True
            break

    if not found:
        patterns.append(new_pattern)

    save_patterns(patterns)


def _pattern_hash(pattern: Dict[str, Any]) -> str:
    key = json.dumps(pattern, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


# ── Step 5: Novelty Check (anti-overfitting) — PHASE 4 UPGRADED ──────────────

def check_novelty(case: Dict[str, Any], threshold: float = 0.85) -> bool:
    """Check whether a case is sufficiently novel compared to existing patterns.

    PHASE 4 UPGRADE: Uses token-level Jaccard similarity on full prompt text
    instead of structural feature similarity.

    Returns True if the case is novel enough to keep.
    If rejected, logs to discarded_duplicates.jsonl.
    """
    patterns = load_patterns()
    # Only compare against active (non-retired) patterns
    active_patterns = [p for p in patterns if not p.get("retired", False)]

    if not active_patterns:
        return True

    prompt = case.get("prompt", "")
    prompt_tokens = set(_tokenize_prompt(prompt))

    for p in active_patterns:
        existing_text = p.get("prompt_text", "")
        existing_tokens = set(_tokenize_prompt(existing_text))

        sim = _token_jaccard(prompt_tokens, existing_tokens)
        if sim > threshold:
            # Log the discarded duplicate
            _log_discarded_duplicate(case, p, sim)
            return False

    return True


def _tokenize_prompt(text: str) -> List[str]:
    """Tokenize prompt into content-bearing tokens."""
    # Lowercase, split on whitespace and punctuation
    import re
    tokens = re.findall(r'[a-z]+', text.lower())
    # Filter out very short tokens and common stop words
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'of', 'to', 'and', 'in', 'that', 'it', 'for', 'on', 'with', 'as', 'by', 'at', 'from', 'this', 'but', 'not', 'or', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'case', 'domain', 'proposed', 'response', 'rule', 'rules', 'sample', 'label', 'example'}
    return [t for t in tokens if len(t) > 2 and t not in stop_words]


def _token_jaccard(set1: Set[str], set2: Set[str]) -> float:
    """Calculate token-level Jaccard similarity."""
    if not set1 and not set2:
        return 1.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def _log_discarded_duplicate(case: Dict[str, Any], similar_pattern: Dict[str, Any], similarity: float) -> None:
    """Log a rejected duplicate to discarded_duplicates.jsonl."""
    _ensure_memory_dir()
    discarded_path = MEMORY_ROOT / "discarded_duplicates.jsonl"

    record = {
        "case_id": case.get("case_id", "unknown"),
        "similarity": round(similarity, 4),
        "similar_to_pattern_hash": _pattern_hash(similar_pattern),
        "similar_pattern_stratum": similar_pattern.get("stratum"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    with open(discarded_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ── PHASE 4: Pattern Retirement Mechanism ────────────────────────────────────

def check_retirement(patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check and retire patterns that are no longer productive.

    A pattern is retired when:
    - Used in 10+ mutations (mutation_count >= 10) AND
    - Produced zero new failures in last 5 uses (failure_count unchanged despite mutations)

    Retired patterns are marked but not deleted. They are excluded from active sampling.

    Returns the updated patterns list.
    """
    changed = False
    for p in patterns:
        if p.get("retired", False):
            continue  # Already retired

        mutation_count = p.get("mutation_count", 0)
        failure_count = p.get("failure_count", 0)
        count = p.get("count", 1)  # Total times used

        # Retirement condition: heavily used but no longer producing failures
        if mutation_count >= 10 and failure_count <= 1 and count >= 5:
            p["retired"] = True
            p["retirement_reason"] = f"stale_after_{mutation_count}_mutations_no_new_failures"
            p["retired_at"] = datetime.now(timezone.utc).isoformat()
            changed = True

    if changed:
        save_patterns(patterns)

    return patterns


def get_active_patterns() -> List[Dict[str, Any]]:
    """Load only active (non-retired) patterns for sampling."""
    all_patterns = load_patterns()
    return [p for p in all_patterns if not p.get("retired", False)]


def get_retired_patterns() -> List[Dict[str, Any]]:
    """Load retired patterns for analysis."""
    all_patterns = load_patterns()
    return [p for p in all_patterns if p.get("retired", False)]


def record_pattern_usage(pattern_hash: str, produced_failure: bool = False) -> None:
    """Update a pattern's usage counters after a mutation.

    PHASE 4: Called after each mutation to track mutation_count and failure production.

    Args:
        pattern_hash: The hash of the pattern that was mutated
        produced_failure: Whether this mutation produced a new failure
    """
    patterns = load_patterns()
    for p in patterns:
        if _pattern_hash(p) == pattern_hash:
            p["mutation_count"] = p.get("mutation_count", 0) + 1
            p["last_used"] = datetime.now(timezone.utc).isoformat()
            if produced_failure:
                p["failure_count"] = p.get("failure_count", 0) + 1
            break

    # Check for retirement after updating
    patterns = check_retirement(patterns)


# ── PHASE 2: Rule Violation Weight Multipliers ───────────────────────────────
# R2 (corruption trust) is the hardest and most critical failure mode
# R3 (false confidence) is medium severity
# R1 (contradiction blindness) is baseline severity
RULE_WEIGHT_MULTIPLIERS = {
    "R1": 1.0,  # Baseline weight
    "R2": 3.0,  # Highest weight - corruption resistance is critical
    "R3": 2.0,  # Medium weight - false confidence
}


# ── Step 6: Adaptive Weight Computation ──────────────────────────────────────

def compute_stratum_weights(alpha: float = 2.0) -> Dict[str, float]:
    """Compute stratum sampling weights based on failure rates.

    Higher weight → more cases generated from that stratum.
    
    PHASE 2 UPDATE: Weight formula now includes rule violation multipliers.
    Formula: weight[stratum] = 1 + failure_rate × alpha × rule_multiplier
    
    Where rule_multiplier is:
    - R2 violations: 3.0 (corruption trust - hardest failure mode)
    - R3 violations: 2.0 (false confidence)
    - R1 violations: 1.0 (contradiction blindness)
    
    If multiple rule violations exist for a stratum, the highest multiplier is used.
    Falls back to uniform if no failure data exists.
    """
    failures_path = MEMORY_ROOT / "failures.jsonl"
    if not failures_path.exists():
        return {"A": 0.2, "B": 0.2, "C": 0.2, "D": 0.2, "E": 0.2}

    # Count failures and rule violations per stratum
    stratum_failures: Dict[str, int] = {}
    stratum_attempts: Dict[str, int] = {}
    stratum_rule_violations: Dict[str, Dict[str, int]] = {}

    with open(failures_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            s = record["stratum"]
            stratum_failures[s] = stratum_failures.get(s, 0) + 1
            stratum_attempts[s] = stratum_attempts.get(s, 0) + 1
            
            # PHASE 2: Track rule violations per stratum
            rule_violations = record.get("rule_violations", [])
            if rule_violations:
                if s not in stratum_rule_violations:
                    stratum_rule_violations[s] = {}
                for rule in rule_violations:
                    stratum_rule_violations[s][rule] = stratum_rule_violations[s].get(rule, 0) + 1

    # We need total attempts per stratum — read patterns for totals
    patterns = load_patterns()
    for p in patterns:
        s = p["stratum"]
        if s not in stratum_attempts:
            stratum_attempts[s] = 0
        stratum_attempts[s] = max(stratum_attempts.get(s, 0), p.get("count", 1))

    # Compute weights with rule violation multipliers
    raw_weights = {}
    for s in ["A", "B", "C", "D", "E"]:
        attempts = stratum_attempts.get(s, 1)
        failures = stratum_failures.get(s, 0)
        failure_rate = failures / attempts if attempts > 0 else 0.0
        
        # PHASE 2: Calculate rule multiplier
        # Use the highest-weighted rule violation for this stratum
        rule_violations = stratum_rule_violations.get(s, {})
        if rule_violations:
            # Weight each rule violation by its count and multiplier
            total_weighted_violations = sum(
                count * RULE_WEIGHT_MULTIPLIERS.get(rule, 1.0)
                for rule, count in rule_violations.items()
            )
            # Average multiplier per failure
            total_violations = sum(rule_violations.values())
            rule_multiplier = total_weighted_violations / total_violations if total_violations > 0 else 1.0
        else:
            rule_multiplier = 1.0  # No rule violations, baseline weight
        
        # Formula: weight = 1 + failure_rate × alpha × rule_multiplier
        raw_weights[s] = 1.0 + failure_rate * alpha * rule_multiplier

    # Normalize
    total = sum(raw_weights.values())
    return {s: w / total for s, w in raw_weights.items()}


# ── Step 7: Weakness Report ──────────────────────────────────────────────────

def weakness_report() -> Dict[str, Any]:
    """Analyze failure patterns to identify system weaknesses."""
    failures_path = MEMORY_ROOT / "failures.jsonl"
    if not failures_path.exists():
        return {"status": "no_failures_recorded"}

    records = []
    with open(failures_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    if not records:
        return {"status": "no_failures_recorded"}

    # Aggregate by error type
    error_counts: Dict[str, int] = {}
    stratum_failures: Dict[str, int] = {}
    trap_failures: Dict[str, int] = {}

    for r in records:
        for et in r.get("error_types", []):
            error_counts[et] = error_counts.get(et, 0) + 1
        s = r["stratum"]
        stratum_failures[s] = stratum_failures.get(s, 0) + 1
        for trap, active in r.get("features", {}).items():
            if active:
                trap_failures[trap] = trap_failures.get(trap, 0) + 1

    total = len(records)
    primary = max(error_counts, key=error_counts.get) if error_counts else "none"

    return {
        "total_failures": total,
        "error_type_distribution": error_counts,
        "stratum_failure_counts": stratum_failures,
        "trap_failure_counts": trap_failures,
        "primary_weakness": primary,
        "stratum_failure_rates": {
            s: stratum_failures.get(s, 0) / total
            for s in ["A", "B", "C", "D", "E"]
        },
    }

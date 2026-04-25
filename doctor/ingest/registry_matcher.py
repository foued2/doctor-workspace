#!/usr/bin/env python3
"""
Registry matcher for Doctor.

Matching now happens inside the single-call parser prompt. This module keeps the
registry-context builder plus the compatibility wrapper that translates the
single-call analysis payload into the historical matcher return shape.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple


SINGLE_CALL_ANALYSIS_KEY = "_single_call_analysis"
NO_MATCH = "no match"
VALID_DECISIONS = {"accept", "reject"}

# Retained for compatibility with older helpers that import this symbol.
_MATCH_PROMPT = (
    "Deprecated: matching is now performed inside doctor.ingest.problem_parser."
)


def get_registry_problems() -> Dict[str, Dict]:
    """Load all problems from the registry."""
    try:
        from doctor.registry.problem_registry import get_problems

        return get_problems()
    except ImportError:
        return {}


def get_problems() -> Dict[str, Dict]:
    """Compatibility alias used by legacy cache helpers."""
    return get_registry_problems()


def _call_llm(prompt: str) -> str:
    raise RuntimeError(
        "registry_matcher no longer makes LLM calls; use problem_parser.parse_problem()"
    )


def normalize_alignment_score(value: Any) -> float:
    """Normalize numeric or percentage-like scores to the 0.0..1.0 range."""
    if isinstance(value, bool):
        return 1.0 if value else 0.0

    if isinstance(value, (int, float)):
        score = float(value)
    elif isinstance(value, str):
        raw = value.strip()
        if not raw:
            return 0.0
        is_percent = raw.endswith("%")
        if is_percent:
            raw = raw[:-1].strip()
        try:
            score = float(raw)
        except ValueError:
            return 0.0
        if is_percent or score > 1.0:
            score /= 100.0
    else:
        return 0.0

    if score < 0.0:
        return 0.0
    if score > 1.0:
        return 1.0
    return score


def normalize_match_candidate(
    match_candidate: Any, problems: Dict[str, Dict]
) -> Optional[str]:
    """Normalize match ids while preserving explicit 'no match' semantics."""
    if match_candidate is None:
        return None

    candidate = str(match_candidate).strip()
    if not candidate:
        return None

    if candidate.lower() in {NO_MATCH, "none", "null"}:
        return None

    if candidate in problems:
        return candidate

    lowered = {problem_id.lower(): problem_id for problem_id in problems}
    return lowered.get(candidate.lower())


def build_registry_context(problems: Dict[str, Dict]) -> str:
    """
    Build compact registry context for the single-call prompt.

    Each line is a JSON object so the LLM receives a stable machine-readable
    summary without depending on prose formatting.
    """
    entries = []

    for problem_id, entry in problems.items():
        if problem_id in ("registry_version", "registry_notes"):
            continue

        spec = entry.get("spec", {})
        execution = entry.get("execution", {})
        normalization = entry.get("normalization", {})

        examples = []
        for test_case in execution.get("test_cases", [])[:2]:
            examples.append(
                {
                    "input": test_case.get("input", []),
                    "expected": test_case.get("expected"),
                    "label": test_case.get("label"),
                }
            )

        summary = {
            "problem_id": problem_id,
            "display_name": spec.get("display_name", problem_id),
            "difficulty": spec.get("difficulty"),
            "function_names": normalization.get("function_names", [])[:3],
            "examples": examples,
        }

        tags = spec.get("tags", [])
        if tags:
            summary["tags"] = tags[:5]

        entries.append(json.dumps(summary, ensure_ascii=True))

    return "\n".join(entries)


def extract_single_call_analysis(model: Dict[str, Any]) -> Dict[str, Any]:
    analysis = model.get(SINGLE_CALL_ANALYSIS_KEY, {})
    return analysis if isinstance(analysis, dict) else {}


def match_to_registry(model: Dict[str, Any]) -> Tuple[Optional[str], str, dict]:
    """
    Translate the single-call parser payload into the legacy matcher contract.

    Returns: (match_id_or_none, justification, decision_trace)
    """
    trace = {
        "source": "single_call",
        "llm_match": None,
        "alignment_score": 0.0,
        "decision": "reject",
        "final": "reject",
        "retry_count": 0,
    }

    if not isinstance(model, dict):
        return None, "Model must be a dict", trace

    analysis = extract_single_call_analysis(model)
    if not analysis:
        return (
            None,
            "Single-call analysis missing; call parse_problem() before match_to_registry()",
            trace,
        )

    problems = get_registry_problems()
    if not problems:
        return None, "Registry empty", trace

    raw_match = analysis.get("match_candidate")
    normalized_match = normalize_match_candidate(raw_match, problems)
    alignment_score = normalize_alignment_score(analysis.get("alignment_score"))
    decision = str(analysis.get("decision", "reject")).strip().lower()
    justification = str(analysis.get("justification", "")).strip()

    retry_count_raw = analysis.get("retry_count", 0)
    try:
        retry_count = int(retry_count_raw)
    except (TypeError, ValueError):
        retry_count = 0

    trace.update(
        {
            "llm_match": normalized_match,
            "raw_match_candidate": raw_match,
            "alignment_score": alignment_score,
            "decision": decision,
            "retry_count": retry_count,
        }
    )

    if decision not in VALID_DECISIONS:
        trace["decision"] = "reject"
        return None, "Invalid decision from single-call analysis", trace

    if raw_match not in (None, "", NO_MATCH) and normalized_match is None:
        return None, f"Single-call analysis returned unknown problem_id: {raw_match}", trace

    if decision == "accept" and normalized_match is None:
        return None, "Accepted decision without a valid registry match", trace

    if decision == "reject":
        reason = justification or "Rejected by single-call analysis"
        return None, reason, trace

    trace["final"] = "accept"
    reason = justification or f"Accepted single-call match for {normalized_match}"
    return normalized_match, reason, trace


if __name__ == "__main__":
    demo_model = {
        "input_type": "array of integers, integer",
        "output_type": "list of integers",
        "objective": "Find indices of two numbers that sum to target",
        "constraints": ["exactly one solution"],
        "edge_conditions": ["duplicates"],
        SINGLE_CALL_ANALYSIS_KEY: {
            "match_candidate": "two_sum",
            "alignment_score": 0.98,
            "decision": "accept",
            "justification": "Inputs, outputs, and objective align with Two Sum.",
            "retry_count": 0,
        },
    }

    match_id, why, decision_trace = match_to_registry(demo_model)
    print(f"Match: {match_id}")
    print(f"Justification: {why}")
    print(f"Trace: {decision_trace}")

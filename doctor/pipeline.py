from __future__ import annotations

from typing import Any, Dict, Optional

from doctor.core.test_executor import TestExecutor
from doctor.grading.evidence import compute_evidence_strength
from doctor.grading.trust import compute_trust_v1
from doctor.ingest.problem_parser import analyze_problem
from doctor.normalize.solution_normalizer import normalize_solution


def _stage(status: str, **details) -> dict:
    return {"status": status, **details}


def _recognition_stages(analysis: dict) -> dict:
    gate_rejected = bool(analysis.get("structural_gate_rejection"))
    schema_info = analysis.get("schema_classification") or {}
    decision = analysis.get("decision", "reject")
    match_candidate = analysis.get("match_candidate")

    if gate_rejected:
        gate = _stage("rejected", reason=analysis.get("justification"))
        schema = _stage("skipped", reason="gate_rejected")
        matcher = _stage("skipped", reason="gate_rejected")
    else:
        gate = _stage("passed")
        if schema_info.get("error"):
            schema = _stage("error", error=schema_info.get("error"))
        else:
            schema = _stage("completed", result=schema_info)
        matcher = _stage(
            "accepted" if decision == "accept" else "rejected",
            match_candidate=match_candidate,
            alignment_score=analysis.get("alignment_score", 0.0),
            reason=analysis.get("justification"),
        )

    return {
        "gate": gate,
        "classify_schema": schema,
        "matcher": matcher,
    }


def _failure_mode_from_recognition(analysis: dict) -> str:
    if analysis.get("structural_gate_rejection"):
        return "gate_rejected"
    if analysis.get("schema_classification", {}).get("error"):
        return "schema_classifier_error"
    return "matcher_rejected"


def run_pipeline(
    statement: str,
    solution_code: Optional[str] = None,
    *,
    model_confidence: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Canonical Doctor pipeline.

    Full verification path:
    gate -> classify_schema -> matcher -> normalizer -> executor -> evidence -> trust -> report

    If solution_code is omitted, the function stops after matcher and returns a
    recognition-only report. This keeps benchmarks on the same entry path while
    avoiding synthetic solution execution.
    """
    analysis = analyze_problem(statement)
    stages = _recognition_stages(analysis)
    trace = {
        "recognition": analysis,
        "pipeline_stages": stages,
    }

    if analysis.get("decision") != "accept":
        stages["normalizer"] = _stage("skipped", reason="recognition_rejected")
        stages["executor"] = _stage("skipped", reason="recognition_rejected")
        stages["evidence"] = _stage("skipped", reason="recognition_rejected")
        stages["trust"] = _stage("skipped", reason="recognition_rejected")
        stages["report"] = _stage("completed")
        return {
            "status": "rejected",
            "problem_id": None,
            "matched": analysis.get("match_candidate"),
            "recognition_decision": analysis.get("decision"),
            "verdict": None,
            "trust_type": None,
            "risk": None,
            "evidence_score": None,
            "pass_rate": None,
            "trace": trace,
            "failure_mode": _failure_mode_from_recognition(analysis),
            "pipeline": stages,
        }

    problem_id = analysis.get("match_candidate")
    if not problem_id or problem_id == "no match":
        stages["normalizer"] = _stage("skipped", reason="no_valid_match")
        stages["executor"] = _stage("skipped", reason="no_valid_match")
        stages["evidence"] = _stage("skipped", reason="no_valid_match")
        stages["trust"] = _stage("skipped", reason="no_valid_match")
        stages["report"] = _stage("completed")
        return {
            "status": "rejected",
            "problem_id": None,
            "matched": problem_id,
            "recognition_decision": analysis.get("decision"),
            "verdict": None,
            "trust_type": None,
            "risk": None,
            "evidence_score": None,
            "pass_rate": None,
            "trace": trace,
            "failure_mode": "matcher_rejected",
            "pipeline": stages,
        }

    if solution_code is None:
        stages["normalizer"] = _stage("skipped", reason="no_solution_code")
        stages["executor"] = _stage("skipped", reason="no_solution_code")
        stages["evidence"] = _stage("skipped", reason="no_solution_code")
        stages["trust"] = _stage("skipped", reason="no_solution_code")
        stages["report"] = _stage("completed")
        return {
            "status": "matched",
            "problem_id": problem_id,
            "matched": problem_id,
            "recognition_decision": analysis.get("decision"),
            "verdict": None,
            "trust_type": None,
            "risk": None,
            "evidence_score": None,
            "pass_rate": None,
            "trace": trace,
            "failure_mode": None,
            "pipeline": stages,
        }

    normalized_code = normalize_solution(solution_code)
    if normalized_code is None:
        stages["normalizer"] = _stage("error", reason="normalization_failed")
        stages["executor"] = _stage("skipped", reason="normalization_failed")
        stages["evidence"] = _stage("skipped", reason="normalization_failed")
        stages["trust"] = _stage("skipped", reason="normalization_failed")
        stages["report"] = _stage("completed")
        return {
            "status": "error",
            "problem_id": problem_id,
            "matched": problem_id,
            "recognition_decision": analysis.get("decision"),
            "verdict": None,
            "trust_type": None,
            "risk": None,
            "evidence_score": None,
            "pass_rate": None,
            "trace": trace,
            "failure_mode": "normalization_failed",
            "pipeline": stages,
        }

    stages["normalizer"] = _stage("completed")
    execution_report = TestExecutor().verify(problem_id, normalized_code)
    stages["executor"] = _stage(
        "completed",
        verdict=execution_report.verdict,
        passed=execution_report.passed,
        total=execution_report.total,
        pass_rate=execution_report.pass_rate,
        error=execution_report.error,
    )

    evidence_strength = compute_evidence_strength(
        execution_report.total,
        execution_report.passed,
    )
    stages["evidence"] = _stage(
        "completed",
        evidence_strength=evidence_strength,
        executor_evidence_score=execution_report.evidence_score,
    )

    E = 1 if execution_report.verdict == "correct" else 0
    c = (
        float(model_confidence)
        if model_confidence is not None
        else float(analysis.get("alignment_score", 0.0) or 0.0)
    )
    trust = compute_trust_v1(E, evidence_strength, c)
    stages["trust"] = _stage(
        "completed",
        trust_type=trust["type"],
        risk=trust["risk"],
        model_confidence=c,
    )
    stages["report"] = _stage("completed")

    return {
        "status": "verified",
        "problem_id": problem_id,
        "matched": problem_id,
        "recognition_decision": analysis.get("decision"),
        "verdict": execution_report.verdict,
        "trust_type": trust["type"],
        "risk": trust["risk"],
        "evidence_score": evidence_strength,
        "executor_evidence_score": execution_report.evidence_score,
        "pass_rate": execution_report.pass_rate,
        "trace": trace,
        "failure_mode": None,
        "pipeline": stages,
    }

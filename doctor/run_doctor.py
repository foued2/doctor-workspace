from doctor.core.test_executor import TestExecutor
from doctor.grading.trust import compute_trust_v1
from doctor.ingest.unified_engine import analyze_statement
from doctor.normalize.solution_normalizer import normalize_solution


def run_doctor(statement: str, solution_code: str) -> dict:
    result = analyze_statement(statement)
    trace = result.get("decision_trace", {})

    if result.get("status") != "success":
        return {
            "status": "rejected",
            "problem_id": result.get("matched"),
            "verdict": None,
            "trust_type": None,
            "risk": None,
            "evidence_score": None,
            "pass_rate": None,
            "trace": trace,
            "failure_mode": result.get("failure_tag"),
        }

    problem_id = result["matched"]
    solution_code = normalize_solution(solution_code)
    if solution_code is None:
        return {
            "status": "error",
            "problem_id": problem_id,
            "verdict": None,
            "trust_type": None,
            "risk": None,
            "evidence_score": None,
            "pass_rate": None,
            "trace": trace,
            "failure_mode": "normalization_failed",
        }

    execution_report = TestExecutor().verify(problem_id, solution_code)
    E = 1 if execution_report.verdict == "correct" else 0
    e = (
        execution_report.evidence_score
        if execution_report.evidence_score is not None
        else 0.0
    )
    c = 0.5
    trust = compute_trust_v1(E, e, c)

    return {
        "status": "verified",
        "problem_id": problem_id,
        "verdict": execution_report.verdict,
        "trust_type": trust["type"],
        "risk": trust["risk"],
        "evidence_score": execution_report.evidence_score,
        "pass_rate": execution_report.pass_rate,
        "trace": trace,
        "failure_mode": None,
    }

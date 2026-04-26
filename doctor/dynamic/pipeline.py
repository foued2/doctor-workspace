#!/usr/bin/env python3
"""
Direction 2: Pipeline

Wires problem extraction, checker generation, and candidate execution.
Task 4: extract_schema + build_checker only.
Task 5: execute_candidate added.
"""
import sys
import io
from typing import Any

from doctor.dynamic.extractor import extract_problem
from doctor.dynamic.checker_generator import generate_checker
from doctor.dynamic.candidate_executor import run_candidate


def extract_schema(problem_statement: str) -> dict | None:
    """Extract schema from a problem statement. Returns schema dict or None."""
    return extract_problem(problem_statement)


def build_checker(schema: dict) -> str | None:
    """Generate and validate a checker from a schema. Returns checker source or None."""
    return generate_checker(schema)


def execute_candidate(candidate_code: str, pipeline_result: dict) -> dict:
    """
    Execute a candidate solution using the pipeline result.
    Merges execution result into pipeline output contract.
    """
    schema = pipeline_result.get("schema")
    checker_source = pipeline_result.get("checker_source")

    if schema is None or checker_source is None:
        pipeline_result["verdict"] = "incorrect"
        pipeline_result["trust"] = "unverified"
        pipeline_result["risk"] = "HIGH"
        pipeline_result["failure_mode"] = pipeline_result.get("failure_mode", "missing_schema_or_checker")
        return pipeline_result

    exec_result = run_candidate(candidate_code, checker_source, schema)

    pipeline_result["verdict"] = exec_result.get("verdict", "incorrect")
    pipeline_result["trust"] = exec_result.get("trust", "unverified")
    pipeline_result["risk"] = exec_result.get("risk", "HIGH")
    pipeline_result["failure_mode"] = exec_result.get("failure_mode")
    pipeline_result["E"] = exec_result.get("E")
    pipeline_result["e"] = exec_result.get("e")
    pipeline_result["tests_passed"] = exec_result.get("tests_passed", 0)
    pipeline_result["tests_total"] = exec_result.get("tests_total", 0)

    if exec_result.get("details"):
        pipeline_result["details"] = exec_result["details"]

    return pipeline_result


def run_pipeline(problem_statement: str, candidate_code: str = None) -> dict:
    """
    Run the Direction 2 pipeline: extract schema, generate checker, optionally execute.
    
    If candidate_code is provided, also executes the candidate against sample cases.
    Returns a result dict with full output contract.
    """
    result = {
        "evaluation_mode": "provisional",
        "checker_confidence": None,
        "verdict": "pending_execution",
        "trust": None,
        "risk": "MEDIUM",
        "failure_mode": None,
        "warning": (
            "This verdict is not authoritative. "
            "Doctor generated its own checker for this problem. "
            "Results may be incorrect if the checker is flawed."
        ),
        "schema": None,
        "checker_source": None,
        "details": [],
    }

    schema = extract_schema(problem_statement)
    if schema is None:
        result["failure_mode"] = "extraction_failed"
        return result
    result["schema"] = schema

    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        checker_source = build_checker(schema)
    finally:
        sys.stdout = old_stdout

    output = captured.getvalue()

    if checker_source is None:
        failure_mode = "extraction_failed"
        for line in output.splitlines():
            if line.startswith("failure_mode:"):
                failure_mode = line.split(":", 1)[1].strip()
                break
        result["failure_mode"] = failure_mode
        return result

    result["checker_source"] = checker_source
    result["checker_confidence"] = "MEDIUM"

    if candidate_code:
        result = execute_candidate(candidate_code, result)

    return result
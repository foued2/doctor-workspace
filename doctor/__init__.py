"""
Doctor: execution-based code evaluation system.

Public API covers the execution / grading / normalization layer only.
Ingestion is a CLI tool; use `python -m doctor.ingest` — not this module.
"""
from .core.test_executor import TestExecutor, TestCase, TestResult, ExecutionReport
from .grading.evidence import compute_evidence_strength, get_final_label
from .grading.trust import compute_trust_v1, compute_risk
from .normalize.solution_normalizer import normalize_solution, extract_function, extract_function_for_problem

__all__ = [
    "TestExecutor", "TestCase", "TestResult", "ExecutionReport",
    "compute_evidence_strength", "get_final_label",
    "compute_trust_v1", "compute_risk",
    "normalize_solution", "extract_function", "extract_function_for_problem",
]

#!/usr/bin/env python3
"""
Doctor - Strict Pipeline with 5 Gates

Each gate either passes or stops. No conversation, no encouragement.
"""
import os
import sys
import json
import subprocess
import signal
import tempfile
import shutil

# ============================================================
# CONFIG
# ============================================================
os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['OPENROUTER_API_KEY'] = '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'

HIGH_CONFIDENCE = 0.90
MEDIUM_CONFIDENCE = 0.70

# ============================================================
# MODIFIER CLASSES
# ============================================================
class_modifiers = [
    ("Class 1", ["ignore case", "case insensitive", "ignore whitespace", "trim"]),
    ("Class 2", ["positive only", "non-negative", "strictly greater", "at least", "maximum of"]),
    ("Class 3", ["modified", "but not", "except", "without using", "only use"]),
]

# ============================================================
# GATE 1: PROBLEM RECOGNITION
# ============================================================
def gate1_recognize(problem_statement: str) -> dict:
    """Pass/fail. Returns binding object"""
    from doctor.ingest.unified_engine import analyze_statement
    
    result = analyze_statement(problem_statement)
    trace = result.get("decision_trace", {})
    alignment = trace.get("alignment_score", 0)
    
    status = result.get("status", "unknown")
    match = result.get("match", trace.get("llm_match", "none"))
    
    if alignment >= HIGH_CONFIDENCE:
        tentative = False
    elif alignment >= MEDIUM_CONFIDENCE:
        tentative = True
    else:
        return {
            "passed": False,
            "stop_reason": "Problem not recognized",
            "confidence": alignment,
            "problem_id": None,
            "tentative": False,
            "modifiers": []
        }
    
    return {
        "passed": True,
        "confidence": alignment,
        "problem_id": match if match not in ["none", "no match"] else None,
        "tentative": tentative,
        "modifiers": []
    }

# ============================================================
# GATE 2: MODIFIER EXTRACTION
# ============================================================
def gate2_modifiers(problem_statement: str, problem_id: str) -> dict:
    """Extract modifiers and classify"""
    from doctor.registry.problem_registry import get_problems
    
    if not problem_id:
        return {"passed": True, "variant_id": None, "modifier_class": None}
    
    # Check for modifiers in statement
    found_modifiers = []
    modifier_class = None
    
    statement_lower = problem_statement.lower()
    
    for cls in ["Class 1", "Class 2", "Class 3"]:
        for kw in class_modifiers.get(cls, []):
            if kw in statement_lower:
                found_modifiers.append(kw)
                modifier_class = cls
                break
    
    # Check for variant in registry
    problems = get_problems()
    variant_id = None
    
    if modifier_class == "Class 3":
        # Look for variant
        base = problem_id
        variant_candidates = [p for p in problems.keys() if base in p or p in base]
        if len(variant_candidates) > 1:  # more than base
            variant_id = variant_candidates[0]  # simplified - pick first variant
    
    if modifier_class == "Class 3" and not variant_id and found_modifiers:
        return {
            "passed": False,
            "stop_reason": "This is a variant I have no tests for",
            "modifier_class": modifier_class,
            "found_modifiers": found_modifiers
        }
    
    return {
        "passed": True,
        "variant_id": variant_id,
        "modifier_class": modifier_class,
        "found_modifiers": found_modifiers
    }

# ============================================================
# GATE 3: SOLUTION INTAKE
# ============================================================
def gate3_solution(solution_code: str) -> dict:
    """Validate Python syntax"""
    try:
        compile(solution_code, "<solution>", "exec")
        return {"passed": True, "valid": True}
    except SyntaxError as e:
        return {
            "passed": False,
            "stop_reason": "Solution is not valid Python",
            "syntax_error": str(e)
        }

# ============================================================
# GATE 4: TEST VERIFICATION
# ============================================================
def gate4_tests(problem_id: str, user_tests: list) -> dict:
    """Check registry for tests"""
    from doctor.registry.problem_registry import get_problems
    
    problems = get_problems()
    
    if problem_id not in problems:
        return {"passed": False, "stop_reason": "No tests available for this problem"}
    
    registry_tests = problems[problem_id].get("execution", {}).get("test_cases", [])
    
    if not registry_tests:
        return {"passed": False, "stop_reason": "No tests available for this problem"}
    
    # User tests are supplementary only
    user_passed = 0
    user_failed = 0
    for tc in user_tests:
        # Can't verify user tests without solution, so just count
        user_failed += 1
    
    return {
        "passed": True,
        "authoritative_tests": registry_tests,
        "user_tests": user_tests,
        "user_passed": user_passed,
        "user_failed": user_failed
    }

# ============================================================
# GATE 5: EXECUTION
# ============================================================
def gate5_execute(solution_code: str, problem_id: str, tests: list, timeout: int = 30) -> dict:
    """Run solution against tests"""
    from doctor.core.test_executor import TestExecutor
    
    executor = TestExecutor()
    report = executor.verify(problem_id, solution_code)
    
    results = [{"label": r.label, "passed": r.passed, "got": r.got, "expected": r.expected, "error": r.error} for r in report.results]
    passed = report.passed
    total = report.total
    
    if report.error:
        return {"passed": False, "stop_reason": f"Execution error: {report.error}"}
    
    return {
        "passed": passed,
        "total": total,
        "results": results,
        "pass_rate": report.pass_rate,
        "error": report.error
    }

# ============================================================
# REPORT GENERATOR
# ============================================================
def generate_report(gate_results: dict) -> str:
    """Generate strict report - no narrative"""
    g1 = gate_results.get("gate1", {})
    g2 = gate_results.get("gate2", {})
    g3 = gate_results.get("gate3", {})
    g4 = gate_results.get("gate4", {})
    g5 = gate_results.get("gate5", {})
    
    problem_id = g1.get("problem_id", "UNKNOWN")
    confidence = g1.get("confidence", 0)
    tentative = g1.get("tentative", False)
    modifiers = g2.get("found_modifiers", [])
    modifier_class = g2.get("modifier_class")
    
    # Verdict
    if g5.get("pass_rate", 0) == 1.0 and not g4.get("user_tests"):
        verdict = "CORRECT"
        trust = "aligned_confident_correct"
        risk = "LOW"
    elif g5.get("pass_rate", 0) == 1.0 and g4.get("user_tests"):
        verdict = "PARTIAL"
        trust = "user_tests_only"
        risk = "MEDIUM"
    elif g5.get("pass_rate", 0) >= 0.5:
        verdict = "PARTIAL"
        trust = "weakly_supported_correct"
        risk = "MEDIUM"
    else:
        verdict = "INCORRECT"
        trust = "false_justified_confidence"
        risk = "HIGH"
    
    # Build report
    lines = []
    lines.append("=" * 50)
    lines.append("DOCTOR REPORT")
    lines.append("=" * 50)
    lines.append("")
    lines.append(f"PROBLEM: {problem_id}")
    lines.append(f"BINDING CONFIDENCE: {confidence:.2f}")
    lines.append(f"TENTATIVE: {'yes' if tentative else 'no'}")
    lines.append("")
    lines.append(f"VERDICT: {verdict}")
    lines.append(f"TRUST: {trust}")
    lines.append(f"RISK: {risk}")
    
    passed = g5.get("passed", 0)
    total = g5.get("total", 0)
    lines.append(f"EVIDENCE: {passed}/{total} tests passed")
    if total > 0:
        lines.append(f"E = {passed/total:.2f}")
    lines.append("")
    
    mods_str = ", ".join(modifiers) if modifiers else "NONE"
    lines.append(f"MODIFIERS APPLIED: {mods_str}")
    
    user_tests = g4.get("user_tests", [])
    if user_tests:
        lines.append(f"USER TESTS: {g4.get('user_passed', 0)}/{len(user_tests)} passed")
    else:
        lines.append("USER TESTS: NONE PROVIDED")
    lines.append("")
    
    # Diagnosis for INCORRECT/PARTIAL
    if verdict in ["INCORRECT", "PARTIAL"]:
        failed_tests = [r["label"] for r in g5.get("results", []) if not r.get("passed")]
        if failed_tests:
            lines.append(f"DIAGNOSIS:")
            lines.append(f"  test_failure(s): {', '.join(failed_tests)}")
    
    # Summary - one sentence
    if verdict == "CORRECT":
        summary = f"Solution correctly solves {problem_id} with {passed}/{total} authoritative tests passing."
    else:
        summary = f"Solution failed {total - passed} of {total} authoritative tests."
    
    lines.append("")
    lines.append("SUMMARY: " + summary)
    lines.append("=" * 50)
    
    return "\n".join(lines)

# ============================================================
# MAIN PIPELINE
# ============================================================
def main():
    print("=" * 50)
    print("DOCTOR - STRICT PIPELINE")
    print("=" * 50)
    print()
    
    gate_results = {}
    
    # GATE 1
    print("[Gate 1] Problem Recognition")
    print("Paste problem statement (Enter twice to finish):")
    problem_lines = []
    while True:
        try:
            line = input()
            if line.strip() == "":
                break
            problem_lines.append(line)
        except EOFError:
            break
    
    problem_statement = "\n".join(problem_lines)
    
    if not problem_statement.strip():
        print("STOP: No problem statement")
        return
    
    g1 = gate1_recognize(problem_statement)
    gate_results["gate1"] = g1
    
    if not g1["passed"]:
        print(f"STOP: {g1['stop_reason']}")
        print(f"Confidence: {g1['confidence']:.2f}")
        return
    
    print(f"MATCH: {g1['problem_id']}")
    print(f"Confidence: {g1['confidence']:.2f}")
    print(f"Tentative: {g1['tentative']}")
    print()
    
    # GATE 2
    print("[Gate 2] Modifier Extraction")
    g2 = gate2_modifiers(problem_statement, g1["problem_id"])
    gate_results["gate2"] = g2
    
    if not g2["passed"]:
        print(f"STOP: {g2['stop_reason']}")
        return
    
    if g2.get("found_modifiers"):
        print(f"Modifiers found: {g2['found_modifiers']}")
    print()
    
    # GATE 3
    print("[Gate 3] Solution Intake")
    print("Paste solution (Enter twice to finish):")
    solution_lines = []
    while True:
        try:
            line = input()
            if line.strip() == "":
                break
            solution_lines.append(line)
        except EOFError:
            break
    
    solution_code = "\n".join(solution_lines)
    
    if not solution_code.strip():
        print("STOP: No solution provided")
        return
    
    g3 = gate3_solution(solution_code)
    gate_results["gate3"] = g3
    
    if not g3["passed"]:
        print(f"STOP: {g3['stop_reason']}")
        return
    
    print("Solution validated as Python")
    print()
    
    # GATE 4
    print("[Gate 4] Test Verification")
    print("Provide test cases? (Enter JSON list, or Enter to skip):")
    user_test_lines = []
    while True:
        try:
            line = input()
            if line.strip() == "":
                break
            user_test_lines.append(line)
        except EOFError:
            break
    
    user_tests = []
    if user_test_lines:
        try:
            user_tests = json.loads("\n".join(user_test_lines))
        except:
            print("Invalid JSON, skipping user tests")
    
    g4 = gate4_tests(g1["problem_id"], user_tests)
    gate_results["gate4"] = g4
    
    if not g4["passed"]:
        print(f"STOP: {g4['stop_reason']}")
        return
    
    print(f"Authoritative tests: {len(g4['authoritative_tests'])}")
    print(f"User tests: {len(user_tests)}")
    print()
    
    # GATE 5
    print("[Gate 5] Execution")
    g5 = gate5_execute(solution_code, g1["problem_id"], g4["authoritative_tests"])
    gate_results["gate5"] = g5
    
    if not g5.get("passed", 0) and g5.get("passed", 0) == 0 and g5.get("total", 0) > 0:
        if g5.get("stop_reason"):
            print(f"STOP: {g5['stop_reason']}")
            return
    
    print(f"Tests: {g5.get('passed', 0)}/{g5.get('total', 0)}")
    for r in g5.get("results", []):
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  {r['label']}: {status}")
    print()
    
    # REPORT
    print(generate_report(gate_results))


if __name__ == "__main__":
    main()
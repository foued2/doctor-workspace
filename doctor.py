#!/usr/bin/env python3
"""
Doctor Prototype - Strict Step-by-Step Conversation
"""
import os
import sys
import json

# ============================================================
# CONFIG
# ============================================================
LLM_PROVIDER = 'openrouter'
API_KEY = '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'
os.environ['LLM_PROVIDER'] = LLM_PROVIDER
os.environ['OPENROUTER_API_KEY'] = API_KEY

ALIGNMENT_THRESHOLD = 0.85

# ============================================================
# STEP 1: CLASSIFY
# ============================================================
def classify_problem(statement: str) -> dict:
    """Attempt to recognize the problem"""
    from doctor.ingest.unified_engine import analyze_statement
    
    result = analyze_statement(statement)
    trace = result.get("decision_trace", {})
    
    return {
        "status": result.get("status"),
        "match": result.get("match", trace.get("llm_match", "none")),
        "alignment": trace.get("alignment_score", 0),
        "constraint": trace.get("constraint_consistency", 0),
        "structural": trace.get("structural_compatibility", 0),
    }

# ============================================================
# STEP 3: LOAD TESTS
# ============================================================
def get_test_cases(problem_id: str) -> list:
    """Get test cases for a problem from registry"""
    from doctor.registry.problem_registry import get_problems
    
    problems = get_problems()
    if problem_id not in problems:
        return []
    
    return problems[problem_id].get("execution", {}).get("test_cases", [])

# ============================================================
# STEP 4: EXECUTE
# ============================================================
def execute_solution(solution_code: str, problem_id: str, test_cases: list) -> dict:
    """Run solution against test cases"""
    from doctor.core.test_executor import _results_equal
    
    results = []
    passed = 0
    total = len(test_cases)
    error = None
    
    # Import solution
    try:
        exec(solution_code, {})
    except Exception as e:
        return {"status": "error", "error": f"Cannot parse solution: {e}"}
    
    # Import target function
    try:
        if problem_id == "arrange_numbers_divisible":
            from cf2225g import solve_case
            func = solve_case
        else:
            return {"status": "error", "error": f"Unknown problem: {problem_id}"}
    except Exception as e:
        return {"status": "error", "error": f"Cannot import solution: {e}"}
    
    # Run tests
    for tc in test_cases:
        try:
            got = func(*tc["input"][0], tc["input"][1])
            expected = tc["expected"]
            equal = _results_equal(got, expected)
            passed += 1 if equal else 0
            results.append({"label": tc.get("label", "?"), "passed": equal, "got": got, "expected": expected})
        except Exception as e:
            passed += 0
            results.append({"label": tc.get("label", "?"), "passed": False, "error": str(e)})
    
    return {
        "status": "complete",
        "passed": passed,
        "total": total,
        "results": results
    }

# ============================================================
# MAIN INTERACTIVE LOOP
# ============================================================
def main():
    print("=" * 60)
    print("Doctor - Strict Step-by-Step Evaluation")
    print("=" * 60)
    print()
    
    # ============================================================
    # STEP 1: PASTE PROBLEM STATEMENT
    # ============================================================
    print("STEP 1: PASTE PROBLEM STATEMENT")
    print("(Press Enter twice to finish)")
    print("> ", end="")
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        except EOFError:
            break
    
    problem_statement = "\n".join(lines)
    
    if not problem_statement.strip():
        print("STOP: No problem statement provided.")
        return
    
    print()
    print("-" * 40)
    print("Analyzing problem...")
    print()
    
    classification = classify_problem(problem_statement)
    
    print(f"Match: {classification['match']}")
    print(f"Status: {classification['status']}")
    print(f"Confidence: {classification['alignment']:.2f}")
    print()
    
    # Check recognition
    if classification['status'] != 'success':
        print("STOP: Problem not recognized.")
        print(f"  Reason: Classification status = {classification['status']}")
        print("  I cannot evaluate a problem I don't recognize.")
        return
    
    if classification['alignment'] < ALIGNMENT_THRESHOLD:
        print("STOP: Low confidence.")
        print(f"  Alignment: {classification['alignment']:.2f} < {ALIGNMENT_THRESHOLD}")
        print("  I don't know this problem well enough to evaluate it.")
        return
    
    if classification['match'] in [None, "none", "no match"]:
        print("STOP: No matching problem found.")
        print("  I cannot find this in my problem registry.")
        return
    
    problem_id = classification['match']
    print(f"Recognized as: {problem_id}")
    print()
    
    # ============================================================
    # STEP 2: PASTE SOLUTION
    # ============================================================
    print("-" * 40)
    print("STEP 2: PASTE SOLUTION CODE")
    print("(Press Enter twice to finish)")
    print("> ", end="")
    
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
        print("STOP: No solution provided.")
        return
    
    # Validate Python
    try:
        compile(solution_code, "<string>", "exec")
    except SyntaxError as e:
        print("STOP: Cannot parse solution.")
        print(f"  SyntaxError: {e}")
        return
    
    print()
    print("Solution parsed successfully.")
    print()
    
    # ============================================================
    # STEP 3: TEST CASES
    # ============================================================
    print("-" * 40)
    print("STEP 3: TEST CASES")
    print("Do you have test cases? (paste them or press Enter to skip)")
    print("> ", end="")
    
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
            if not isinstance(user_tests, list):
                print("STOP: Test cases must be a JSON list.")
                return
        except json.JSONDecodeError as e:
            print("STOP: Invalid JSON for test cases.")
            print(f"  Error: {e}")
            return
        print(f"Using {len(user_tests)} user-provided tests.")
    else:
        print("Using registry tests.")
    
    # Load registry tests
    registry_tests = get_test_cases(problem_id)
    print(f"Registry has {len(registry_tests)} tests.")
    
    # Combine: user tests take priority
    all_tests = user_tests.copy() if user_tests else []
    for tc in registry_tests:
        # Add registry tests that don't duplicate
        existing_labels = [t.get("label") for t in all_tests]
        if tc.get("label") not in existing_labels:
            all_tests.append(tc)
    
    if not all_tests:
        print("STOP: No test cases available.")
        print("  I cannot evaluate fairly without test cases.")
        print("  Either provide tests or ensure this problem has registry tests.")
        return
    
    print(f"Total tests: {len(all_tests)}")
    print()
    
    # ============================================================
    # STEP 4: EXECUTE
    # ============================================================
    print("-" * 40)
    print("STEP 4: Running execution pipeline...")
    print()
    
    execution = execute_solution(solution_code, problem_id, all_tests)
    
    if execution.get("status") == "error":
        print(f"STOP: Execution error.")
        print(f"  {execution.get('error')}")
        return
    
    print(f"Tests passed: {execution['passed']}/{execution['total']}")
    print()
    
    for r in execution.get("results", []):
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  {r['label']}: {status}")
        if r.get("error"):
            print(f"    Error: {r['error']}")
    print()
    
    # ============================================================
    # STEP 5: REPORT
    # ============================================================
    print("=" * 60)
    print("DOCTOR REPORT")
    print("=" * 60)
    print()
    print("CLASSIFICATION:")
    print(f"  Problem: {problem_id}")
    print(f"  Confidence: {classification['alignment']:.2f}")
    print()
    print("EXECUTION:")
    passed = execution['passed']
    total = execution['total']
    pass_rate = passed/total if total > 0 else 0
    print(f"  Tests: {passed}/{total} ({100*pass_rate:.1f}%)")
    print()
    
    # Verdict
    if pass_rate == 1.0:
        verdict = "CORRECT"
        trust = "aligned_confident_correct"
        risk = "LOW"
    elif pass_rate >= 0.5:
        verdict = "PARTIAL"
        trust = "weakly_supported_correct"
        risk = "MEDIUM"
    else:
        verdict = "INCORRECT"
        trust = "false_justified_confidence"
        risk = "HIGH"
    
    print("=" * 60)
    print(f"VERDICT: {verdict}")
    print(f"TRUST: {trust}")
    print(f"RISK: {risk}")
    print("=" * 60)


if __name__ == "__main__":
    main()
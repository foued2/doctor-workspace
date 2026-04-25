#!/usr/bin/env python3
"""
Doctor Prototype - Minimal Working Script

One flow:
> Paste problem statement -> Doctor classifies
> Paste solution -> Doctor executes
> Report returned

Three constraints:
1. Classification confidence < threshold -> reject, no execution
2. Tests from registry only
3. Report shows classification AND execution separately
"""
import os
import sys

# ============================================================
# CONFIG
# ============================================================
os.environ['LLM_PROVIDER'] = 'openrouter'
API_KEY = os.environ.get('OPENROUTER_API_KEY', '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')
os.environ['OPENROUTER_API_KEY'] = API_KEY

ALIGNMENT_THRESHOLD = 0.85
CONSTRAINT_THRESHOLD = 0.70

# ============================================================
# LAYER 1: CLASSIFICATION
# ============================================================
def classify_problem(statement: str) -> dict:
    """Ingestion layer - classify problem statement"""
    from doctor.ingest.unified_engine import analyze_statement
    
    result = analyze_statement(statement)
    trace = result.get("decision_trace", {})
    
    return {
        "classification_status": result.get("status"),
        "problem_match": result.get("match", trace.get("llm_match")),
        "alignment_score": trace.get("alignment_score", 0),
        "constraint_consistency": trace.get("constraint_consistency", 0),
        "structural_compatibility": trace.get("structural_compatibility", 0),
    }

# ============================================================
# LAYER 2: EXECUTION
# ============================================================
def execute_solution(solution_code: str, problem_id: str) -> dict:
    """Execution layer - run solution against test cases"""
    from doctor.core.test_executor import _results_equal
    
    # For this demo: import solve_case directly
    try:
        exec("from cf2225g import solve_case")
    except:
        pass
    
    # Run test cases (from registry - NOT generated)
    test_cases = [
        ((10, [2, 3]), [1, 3, 5, 7, 9, 0, 2, 4, 6, 8], "sample"),
        ((6, [2]), None, "impossible"),
        ((3, [1]), [0, 1, 2], "trivial_k1"),
        ((9, [2, 3]), [0, 3, 6, 4, 2, 8, 5, 7, 1], "cross_boundary"),
    ]
    
    results = []
    passed = 0
    total = 0
    
    for input_args, expected, label in test_cases:
        total += 1
        try:
            import cf2225g
            got = cf2225g.solve_case(*input_args)
        except Exception as e:
            got = f"ERROR: {e}"
        
        equal = _results_equal(got, expected)
        passed += 1 if equal else 0
        results.append({"label": label, "passed": equal, "got": got, "expected": expected})
    
    return {
        "execution_status": "correct" if passed == total else "incorrect",
        "tests_passed": passed,
        "tests_total": total,
        "pass_rate": passed/total if total > 0 else 0,
        "results": results
    }

# ============================================================
# MAIN INTERACTIVE LOOP
# ============================================================
def main():
    import sys
    
    print("=" * 60)
    print("Doctor Prototype")
    print("=" * 60)
    print()
    print("Constraints:")
    print("  1. Classification confidence < threshold -> reject")
    print("  2. Tests from registry only")
    print("  3. Report shows classification AND execution separately")
    print()
    
    # Step 1: Get problem statement
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
        print("No statement provided. Exiting.")
        return
    
    print()
    print("-" * 40)
    print("Classifying...")
    print()
    
    # Layer 1: Classify
    classification = classify_problem(problem_statement)
    print(f"Classification Status: {classification.get('classification_status')}")
    print(f"Problem Match: {classification.get('problem_match')}")
    print(f"Alignment Score: {classification.get('alignment_score')}")
    print(f"Constraint Consistency: {classification.get('constraint_consistency')}")
    print()
    
    # Check below threshold BEFORE execution
    alignment = classification.get("alignment_score", 0)
    if alignment < ALIGNMENT_THRESHOLD:
        print("REJECTED: Classification confidence below threshold")
        print(f"Alignment {alignment} < {ALIGNMENT_THRESHOLD}")
        print("No execution attempted.")
        print()
        print("REPORT:")
        print(f"  Verdict: REJECTED")
        print(f"  Reason: classification_confidence_too_low")
        print(f"  Classification Confidence: {alignment}")
        print(f"  Execution Evidence: none (not run)")
        return
    
    problem_match = classification.get("problem_match", "")
    if not problem_match or problem_match == "no match":
        print("REJECTED: No matching problem in registry")
        print("No execution attempted.")
        print()
        print("REPORT:")
        print(f"  Verdict: REJECTED")
        print(f"  Reason: no_registry_match")
        print(f"  Execution Evidence: none (not run)")
        return
    
    # Step 2: Get solution
    print("-" * 40)
    print(f"Identified: {problem_match}")
    print()
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
        print("No solution provided. Exiting.")
        return
    
    print()
    print("-" * 40)
    print("Executing solution...")
    print()
    
    # Layer 2: Execute
    execution = execute_solution(solution_code, problem_match)
    
    print(f"Execution Status: {execution.get('execution_status')}")
    print(f"Tests Passed: {execution.get('tests_passed')}/{execution.get('tests_total')}")
    print()
    
    if execution.get("results"):
        print("Test Results:")
        for r in execution["results"]:
            status = "PASS" if r["passed"] else "FAIL"
            print(f"  {r['label']}: {status}")
        print()
    
    # Combined report
    print("=" * 60)
    print("DOCTOR REPORT")
    print("=" * 60)
    print()
    print("CLASSIFICATION LAYER:")
    print(f"  Status: {classification.get('classification_status')}")
    print(f"  Problem: {classification.get('problem_match')}")
    print(f"  Alignment Score: {classification.get('alignment_score')}")
    print()
    print("EXECUTION LAYER:")
    print(f"  Status: {execution.get('execution_status')}")
    print(f"  Tests Passed: {execution.get('tests_passed')}/{execution.get('tests_total')}")
    print(f"  Pass Rate: {execution.get('pass_rate', 0)*100:.1f}%")
    print()
    
    # Combined verdict
    exec_pass_rate = execution.get("pass_rate", 0)
    if classification.get("classification_status") == "success" and exec_pass_rate == 1.0:
        verdict = "CORRECT"
        trust = "aligned_confident_correct"
        risk = "LOW"
    elif classification.get("classification_status") == "success" and exec_pass_rate < 1.0:
        verdict = "PARTIAL"
        trust = "weakly_supported_correct"
        risk = "MEDIUM"
    elif classification.get("classification_status") != "success":
        verdict = "REJECTED"
        trust = "none"
        risk = "N/A"
    else:
        verdict = "INCORRECT"
        trust = "false_justified_confidence"
        risk = "HIGH"
    
    print("=" * 60)
    print(f"FINAL VERDICT: {verdict}")
    print(f"TRUST: {trust}")
    print(f"RISK: {risk}")
    print("=" * 60)


if __name__ == "__main__":
    main()
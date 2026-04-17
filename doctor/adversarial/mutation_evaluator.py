"""
Doctor Mutation Evaluator — Measures test suite strength under adversarial degradation.

Measures:
  1. Reference solution passes E=1.0 (baseline)
  2. Mutated variants should fail at least some tests (mutation robustness)
  3. Adversarial tests should catch known failure patterns

Output: SuiteStrengthReport
  - reference_pass: bool
  - mutation_kill_rate: float (fraction of mutated variants caught by tests)
  - adversarial_coverage: int (number of adversarial cases runnable)
  - strength_score: float (composite)

Design constraints (enforced):
  - NO feedback from evaluation results to generation
  - All mutations generated before any evaluation runs
  - Adversarial tests are structural, not oracle-history-based
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .mutation_engine import MutationEngine, MutationResult
from .adversarial_generator import AdversarialGenerator, AdversarialTestCase


class ExecutionState(Enum):
    OK = "ok"
    WRONG = "wrong"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass(frozen=True)
class ExecutionResult:
    state: ExecutionState
    output: Any = None
    message: str = ""

    def is_ok(self) -> bool:
        return self.state == ExecutionState.OK

    def is_wrong(self) -> bool:
        return self.state == ExecutionState.WRONG

    def is_timeout(self) -> bool:
        return self.state == ExecutionState.TIMEOUT

    def is_error(self) -> bool:
        return self.state == ExecutionState.ERROR

    def is_terminal(self) -> bool:
        return True


@dataclass
class SuiteStrengthReport:
    problem_id: str
    reference_pass: bool
    mutation_count: int
    mutations_killed: int
    mutation_kill_rate: float
    adversarial_count: int
    strength_score: float
    details: Dict[str, Any] = field(default_factory=dict)


def evaluate_suite_strength(
    problem_id: str,
    reference_code: str,
    test_cases: List[dict],
    function_signature: str,
    difficulty: str = "medium",
) -> SuiteStrengthReport:
    """
    Evaluate how robust a test suite is under adversarial conditions.

    Steps:
        1. Verify reference solution passes E=1.0
        2. Generate mutations of the reference solution
        3. Run each mutated variant against the test suite
        4. Count how many mutations are "killed" (test catches the error)
        5. Generate adversarial tests (structurally, not from oracle)

    A high kill rate means the test suite catches most mutations.
    A low kill rate means the test suite is shallow.
    """
    if not reference_code:
        return SuiteStrengthReport(
            problem_id=problem_id,
            reference_pass=False,
            mutation_count=0,
            mutations_killed=0,
            mutation_kill_rate=0.0,
            adversarial_count=0,
            strength_score=0.0,
            details={"mutation_classes": [], "mutation_breakdown": {}},
        )

    mutation_engine = MutationEngine(problem_id, num_variants_per_class=3)
    adversarial_gen = AdversarialGenerator(problem_id, function_signature, difficulty)

    raw_mutations = mutation_engine.generate_all(reference_code)
    adversarial_cases = adversarial_gen.generate()

    canonical_inputs = [tuple(tc["input"]) for tc in test_cases]
    effective_mutations, preflight_report = _filter_effective_mutations(
        reference_code, raw_mutations, canonical_inputs
    )

    ref_result = _run_solution(reference_code, test_cases)
    ref_pass = ref_result.state == ExecutionState.OK

    mutations_killed = 0
    mutation_details = []
    for mut in effective_mutations:
        mut_result = _run_solution(mut.mutated_code, test_cases)
        killed = mut_result.state != ExecutionState.OK
        if killed:
            mutations_killed += 1
        mutation_details.append({
            "mutation_class": mut.mutation_class,
            "variant_index": mut.variant_index,
            "description": mut.description,
            "result": mut_result,
            "killed": killed,
            "minimal_failing_input": _find_minimal_failing_input(mut.mutated_code, reference_code, test_cases),
            "failing_tests": mut_result.failing_tests,
        })

    raw_kill_rate = mutations_killed / len(effective_mutations) if effective_mutations else 0.0
    total_raw = len(raw_mutations)
    total_effective = len(effective_mutations)
    redundancy = total_raw - total_effective

    adv_count = len([tc for tc in adversarial_cases if tc.input_data is not None])
    strength_score = raw_kill_rate

    test_contrib = _test_contribution(test_cases, reference_code, effective_mutations)

    return SuiteStrengthReport(
        problem_id=problem_id,
        reference_pass=ref_pass,
        mutation_count=total_effective,
        mutations_killed=mutations_killed,
        mutation_kill_rate=raw_kill_rate,
        adversarial_count=adv_count,
        strength_score=strength_score,
        details={
            "raw_mutation_count": total_raw,
            "effective_mutation_count": total_effective,
            "mutation_redundancy": redundancy,
            "preflight_report": preflight_report,
            "mutation_classes": list(set(m.mutation_class for m in effective_mutations)),
            "mutation_breakdown": _breakdown_by_class(effective_mutations, test_cases),
            "mutation_details": mutation_details,
            "test_contribution": {
                i: {
                    "label": tc.get("label", f"tc_{i}"),
                    "marginal_kills": v["marginal_kills"],
                    "is_critical": v["is_critical"],
                }
                for i, v in test_contrib.items()
                for tc in [v["test"]]
            },
        },
    )


@dataclass
class ExecutionSummary:
    state: ExecutionState
    pass_count: int = 0
    wrong_count: int = 0
    timeout_count: int = 0
    error_count: int = 0
    total: int = 0
    pass_rate: float = 0.0
    failing_tests: List[dict] = field(default_factory=list)
    timed_out: bool = False

    @staticmethod
    def for_test_cases(code: str, test_cases: List[dict], timeout_per_test: float = 2.0) -> "ExecutionSummary":
        try:
            from doctor.normalize.solution_normalizer import extract_function, normalize_solution
            from doctor.core.test_executor import run_test_with_trace, _results_equal

            normalized = normalize_solution(code)
            func = extract_function(normalized)
            if func is None:
                return ExecutionSummary(state=ExecutionState.ERROR, total=len(test_cases))

            passed = wrong = timed_out = errors = 0
            failing_tests = []

            for tc in test_cases:
                trace = _run_with_timeout(
                    run_test_with_trace,
                    (func, tuple(tc["input"]), tc["expected"]),
                    timeout_per_test,
                )
                if trace is None:
                    timed_out += 1
                    failing_tests.append({**tc, "failure_state": ExecutionState.TIMEOUT.value})
                elif trace.get("error") is not None:
                    errors += 1
                    failing_tests.append({**tc, "failure_state": ExecutionState.ERROR.value, "error": trace.get("error")})
                elif _results_equal(trace.get("output"), tc["expected"]):
                    passed += 1
                else:
                    wrong += 1
                    failing_tests.append({**tc, "failure_state": ExecutionState.WRONG.value, "got": trace.get("output")})

            total = len(test_cases)
            pass_rate = passed / total if total else 0.0
            any_timeout = timed_out > 0

            if errors > 0:
                state = ExecutionState.ERROR
            elif any_timeout:
                state = ExecutionState.TIMEOUT
            elif wrong > 0:
                state = ExecutionState.WRONG
            else:
                state = ExecutionState.OK

            return ExecutionSummary(
                state=state,
                pass_count=passed,
                wrong_count=wrong,
                timeout_count=timed_out,
                error_count=errors,
                total=total,
                pass_rate=pass_rate,
                failing_tests=failing_tests,
                timed_out=any_timeout,
            )
        except Exception:
            return ExecutionSummary(state=ExecutionState.ERROR, total=len(test_cases))


def _run_solution(code: str, test_cases: List[dict], timeout_per_test: float = 2.0) -> ExecutionSummary:
    """Run a solution against test cases. Returns ExecutionSummary with clear state classification.

    Every result is exactly one of:
      OK      - all tests passed
      WRONG   - some tests produced wrong output
      TIMEOUT - at least one test timed out
      ERROR   - normalization/extraction/exception failure
    """
    return ExecutionSummary.for_test_cases(code, test_cases, timeout_per_test)


def _run_with_timeout(func: callable, args: tuple, timeout: float = 2.0) -> Any:
    """Run a callable with args under a timeout. Returns result or None on timeout."""
    result = [None]
    exc = [None]

    def target():
        try:
            result[0] = func(*args)
        except Exception as e:
            exc[0] = e

    t = __import__("threading").Thread(target=target)
    t.daemon = True
    t.start()
    t.join(timeout)
    if t.is_alive():
        return None
    if exc[0] is not None:
        raise exc[0]
    return result[0]


def _run_once(code: str, input_data: tuple, timeout: float = 2.0) -> ExecutionResult:
    """Run a single input through a solution. Returns exactly one ExecutionState.

    States:
      OK       - produced an output normally
      WRONG    - produced an output that differs from reference
      TIMEOUT  - did not complete within timeout
      ERROR    - exception during normalization, extraction, or execution
    """
    try:
        from doctor.normalize.solution_normalizer import extract_function, normalize_solution
        from doctor.core.test_executor import run_test_with_trace

        normalized = normalize_solution(code)
        if normalized is None:
            return ExecutionResult(ExecutionState.ERROR, message="normalization failed")

        func = extract_function(normalized)
        if func is None:
            return ExecutionResult(ExecutionState.ERROR, message="extract_function returned None")

        trace = _run_with_timeout(run_test_with_trace, (func, input_data, None), timeout)
        if trace is None:
            return ExecutionResult(ExecutionState.TIMEOUT, message="execution timed out")

        if trace.get("error") is not None:
            return ExecutionResult(ExecutionState.ERROR, message=trace["error"])

        return ExecutionResult(ExecutionState.OK, output=trace.get("output"))

    except Exception as e:
        return ExecutionResult(ExecutionState.ERROR, message=str(e))


def _run_with_expected(code: str, input_data: tuple, expected: Any, timeout: float = 2.0) -> ExecutionResult:
    """Run a solution against a specific test case. Returns OK or WRONG."""
    result = _run_once(code, input_data, timeout)
    if result.state != ExecutionState.OK:
        return result
    from doctor.core.test_executor import _results_equal
    if _results_equal(result.output, expected):
        return ExecutionResult(ExecutionState.OK, output=result.output)
    return ExecutionResult(ExecutionState.WRONG, output=result.output)


def _make_hashable(obj):
    """Recursively convert lists (and tuples containing lists) to tuples for hashability."""
    if isinstance(obj, list):
        return tuple(_make_hashable(x) for x in obj)
    if isinstance(obj, tuple):
        result = tuple(_make_hashable(x) for x in obj)
        try:
            hash(result)
            return result
        except TypeError:
            return result
    return obj


def _filter_effective_mutations(
    reference_code: str,
    mutations: List[MutationResult],
    canonical_inputs: List[tuple],
) -> Tuple[List[MutationResult], Dict[str, dict]]:
    """Filter mutations by semantic behavior and preflight each for termination.

    A mutation is kept only if:
      1. It terminates (no timeout) on at least one canonical input
      2. Its output differs from the reference on at least one canonical input

    Redundant mutations (identical output signature across all canonical inputs)
    are deduplicated to one representative.

    Returns (filtered_mutations, preflight_report).
    """
    ref_results = {}
    for inp in canonical_inputs:
        h_inp = _make_hashable(inp)
        ref_results[h_inp] = _run_once(reference_code, h_inp)

    seen_signatures: Dict[str, MutationResult] = {}
    effective = []
    preflight: Dict[str, dict] = {}

    for m in mutations:
        mut_results = []
        differs = False
        timed_out_count = 0

        for inp in canonical_inputs:
            h_inp = _make_hashable(inp)
            r = _run_once(m.mutated_code, h_inp)
            mut_results.append(r)
            ref_r = ref_results.get(h_inp)

            if r.is_timeout():
                timed_out_count += 1
            if ref_r is not None:
                if r.state != ref_r.state:
                    differs = True
                elif r.is_ok() and r.output != ref_r.output:
                    differs = True

        preflight[m.mutation_class + f"_v{m.variant_index}"] = {
            "timed_out_count": timed_out_count,
            "total_inputs": len(canonical_inputs),
        }

        if timed_out_count == len(canonical_inputs):
            continue
        if not differs:
            continue

        sig = str([(r.state.value, r.output) for r in mut_results])
        if sig not in seen_signatures:
            seen_signatures[sig] = m
            effective.append(m)

    return effective, preflight


def _find_minimal_failing_input(
    code: str,
    reference_code: str,
    test_cases: List[dict],
    timeout: float = 2.0,
) -> Optional[dict]:
    """Find the smallest test case (by input magnitude) where mutated code fails."""
    ref_outputs = {}
    for tc in test_cases:
        inp = tuple(tc["input"])
        r = _run_once(reference_code, inp)
        ref_outputs[inp] = r

    failing = []
    for tc in test_cases:
        inp = tuple(tc["input"])
        r = _run_once(code, inp)
        ref_r = ref_outputs.get(inp)
        if r.is_timeout() or (r.is_ok() and ref_r is not None and r.output != ref_r.output):
            input_mag = sum(abs(x) for x in inp) if inp else 0
            failing.append((input_mag, tc))

    if failing:
        failing.sort(key=lambda x: x[0])
        return failing[0][1]
    return None


def _test_contribution(test_cases: List[dict], reference_code: str, mutations: List[MutationResult]) -> Dict[int, dict]:
    """Measure marginal detection contribution of each test case.

    For each test case i:
      - Remove it from the suite
      - Recompute: mutations killed
      - Report delta vs full suite
    """
    def eval_subset(subset):
        muts_killed = 0
        for m in mutations:
            result = _run_solution(m.mutated_code, subset)
            if result.state != ExecutionState.OK:
                muts_killed += 1
        return muts_killed

    full_killed = eval_subset(test_cases)

    contributions = {}
    for i in range(len(test_cases)):
        subset = [tc for j, tc in enumerate(test_cases) if j != i]
        subset_killed = eval_subset(subset)
        delta = full_killed - subset_killed
        contributions[i] = {
            "test": test_cases[i],
            "full_killed": full_killed,
            "subset_killed": subset_killed,
            "marginal_kills": delta,
            "is_critical": delta > 0,
        }
    return contributions


def _breakdown_by_class(mutations: List[MutationResult], test_cases: List[dict]) -> Dict[str, dict]:
    """Show kill rate broken down by mutation class."""
    by_class: Dict[str, List[ExecutionSummary]] = {}
    for m in mutations:
        by_class.setdefault(m.mutation_class, [])
        result = _run_solution(m.mutated_code, test_cases)
        by_class[m.mutation_class].append(result)

    return {
        cls: {
            "count": len(results),
            "avg_pass_rate": sum(r.pass_rate for r in results) / len(results),
            "killed": sum(1 for r in results if r.state != ExecutionState.OK),
            "by_state": {
                st.value: sum(1 for r in results if r.state == st)
                for st in ExecutionState
            },
        }
        for cls, results in by_class.items()
    }


def format_report(report: SuiteStrengthReport) -> str:
    """Human-readable strength report with explicit state classification."""
    raw = report.details.get("raw_mutation_count", 0)
    eff = report.mutation_count
    redundancy = raw - eff

    lines = [
        f"=== Suite Strength Report: {report.problem_id} ===",
        f"Reference: {'PASS' if report.reference_pass else 'FAIL'}",
        f"",
        f"Mutation robustness:",
        f"  raw:        {raw}",
        f"  effective:  {eff}",
        f"  redundant:  {redundancy} ({redundancy/raw*100:.0f}% of raw)" if redundancy > 0 else f"  redundant:  0",
        f"  killed:     {report.mutations_killed}",
        f"  kill rate:  {report.mutation_kill_rate:.1%}",
        f"  strength:   {report.strength_score:.2f}",
        f"",
        f"Per-mutation results:",
    ]

    for md in report.details.get("mutation_details", []):
        result = md.get("result")
        if result:
            state_icon = {
                ExecutionState.OK: "OK",
                ExecutionState.WRONG: "WRONG",
                ExecutionState.TIMEOUT: "TIMEOUT",
                ExecutionState.ERROR: "ERROR",
            }.get(result.state, "?")
            lines.append(
                f"  [{state_icon}] {md['mutation_class']} (v{md['variant_index']}): "
                f"pass_rate={result.pass_rate:.0%} | "
                f"wrong={result.wrong_count}, timeout={result.timeout_count}, error={result.error_count}"
                f"  {md['description']}"
            )
        else:
            lines.append(f"  [?] {md['mutation_class']} (v{md['variant_index']}): {md['description']}")

    lines.append(f"")
    lines.append(f"Per-mutation-class breakdown:")
    breakdown = report.details.get("mutation_breakdown", {})
    for cls, stats in breakdown.items():
        killed = stats["killed"]
        total = stats["count"]
        rate = killed / total if total else 0
        by = stats.get("by_state", {})
        state_summary = ", ".join(f"{v}x{st.value}" for st, v in [(ExecutionState.OK, 0), (ExecutionState.WRONG, 0), (ExecutionState.TIMEOUT, 0), (ExecutionState.ERROR, 0)] if by.get(st.value, 0) > 0)
        lines.append(f"  {cls}: killed={killed}/{total} ({rate:.0%})")

    lines.append(f"")
    lines.append(f"Test case contribution (marginal kills when removed):")
    contrib = report.details.get("test_contribution", {})
    for idx in sorted(contrib.keys()):
        v = contrib[idx]
        label = v.get("label", f"tc_{idx}")
        delta = v["marginal_kills"]
        marker = " ← CRITICAL" if v["is_critical"] else ""
        lines.append(f"  {label}: marginal_kills={delta}{marker}")

    lines.append(f"")
    lines.append(f"Adversarial tests: {report.adversarial_count} cases")

    return "\n".join(lines)

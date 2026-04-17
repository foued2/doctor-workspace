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
from typing import Any, Dict, List, Optional, Tuple

from .mutation_engine import MutationEngine, MutationResult
from .adversarial_generator import AdversarialGenerator, AdversarialTestCase


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
    effective_mutations = _filter_effective_mutations(reference_code, raw_mutations, canonical_inputs)

    ref_pass = _run_solution(reference_code, test_cases) == 1.0

    mutations_killed = 0
    mutation_details = []
    for mut in effective_mutations:
        mut_rate = _run_solution(mut.mutated_code, test_cases)
        timed_out = _run_once(mut.mutated_code, canonical_inputs[0])[2]
        minimal_tc = _find_minimal_failing_input(mut.mutated_code, reference_code, test_cases)
        killed = mut_rate < 1.0
        if killed:
            mutations_killed += 1
        mutation_details.append({
            "mutation_class": mut.mutation_class,
            "variant_index": mut.variant_index,
            "description": mut.description,
            "pass_rate": mut_rate,
            "timed_out": timed_out,
            "killed": killed,
            "minimal_failing_input": minimal_tc,
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


def _run_solution(code: str, test_cases: List[dict], timeout_per_test: float = 2.0) -> float:
    """Run a solution against test cases. Returns pass rate.

    Each test case is run with a timeout. If it times out (e.g., infinite loop),
    the test case is treated as a failure.
    """
    try:
        from doctor.normalize.solution_normalizer import extract_function, normalize_solution
        from doctor.core.test_executor import run_test_with_trace, _results_equal

        normalized = normalize_solution(code)
        func = extract_function(normalized)
        if func is None:
            return 0.0

        passed = 0
        for tc in test_cases:
            trace = _run_with_timeout(
                run_test_with_trace,
                (func, tuple(tc["input"]), tc["expected"]),
                timeout_per_test,
            )
            if trace is None:
                pass
            elif trace.get("error") is None and _results_equal(trace.get("output"), tc["expected"]):
                passed += 1

        return passed / len(test_cases) if test_cases else 0.0
    except Exception:
        return 0.0


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


def _run_once(code: str, input_data: tuple, timeout: float = 2.0) -> Tuple[Any, Optional[str], bool]:
    """Run a single input through a solution. Returns (output, error, timed_out).

    - output: the function return value, or None if error/timeout
    - error: traceback string if exception, else None
    - timed_out: True if execution exceeded timeout
    """
    try:
        from doctor.normalize.solution_normalizer import extract_function, normalize_solution
        from doctor.core.test_executor import run_test_with_trace
        normalized = normalize_solution(code)
        func = extract_function(normalized)
        if func is None:
            return None, "extract_function returned None", False
        trace = _run_with_timeout(run_test_with_trace, (func, input_data, None), timeout)
        if trace is None:
            return None, None, True
        if trace.get("error") is not None:
            return None, trace["error"], False
        return trace.get("output"), None, False
    except Exception as e:
        return None, str(e), False


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
) -> List[MutationResult]:
    """Filter mutations by semantic behavior.

    A mutation is kept only if its output differs from the reference on at least
    one canonical input. Redundant mutations (identical output signature) are
    deduplicated to one representative.

    Returns filtered + deduplicated list of mutations.
    """
    ref_outputs = {}
    for inp in canonical_inputs:
        h_inp = _make_hashable(inp)
        out, _, timed_out = _run_once(reference_code, h_inp)
        ref_outputs[h_inp] = (out, timed_out)

    seen_signatures: Dict[str, MutationResult] = {}
    effective = []

    for m in mutations:
        sig_parts = []
        differs = False
        for inp in canonical_inputs:
            h_inp = _make_hashable(inp)
            out, _, timed_out = _run_once(m.mutated_code, h_inp)
            ref_out, ref_timed = ref_outputs.get(h_inp, (None, True))
            if timed_out != ref_timed:
                differs = True
            elif not timed_out and out != ref_out:
                differs = True
            sig_parts.append((out, timed_out))

        if not differs:
            continue

        sig = str(sig_parts)
        if sig not in seen_signatures:
            seen_signatures[sig] = m
            effective.append(m)

    return effective


def _find_minimal_failing_input(
    code: str,
    reference_code: str,
    test_cases: List[dict],
    timeout: float = 2.0,
) -> Optional[dict]:
    """Find the smallest test case (by input magnitude) where mutated code fails.

    Returns the test case dict or None if it passes all tests.
    """
    ref_outputs = {}
    for tc in test_cases:
        inp = tuple(tc["input"])
        out, _, _ = _run_once(reference_code, inp)
        ref_outputs[inp] = out

    failing = []
    for tc in test_cases:
        inp = tuple(tc["input"])
        out, err, timed_out = _run_once(code, inp)
        ref_out = ref_outputs.get(inp)
        if timed_out or (err is None and out != ref_out):
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
      - Recompute: bugs caught, mutations killed
      - Report delta vs full suite

    Returns dict keyed by test case index.
    """
    def eval_subset(subset):
        bugs_caught = 0
        muts_killed = 0
        for m in mutations:
            rate = _run_solution(m.mutated_code, subset)
            if rate < 1.0:
                muts_killed += 1
        return muts_killed

    full_killed = eval_subset(test_cases)
    full_count = len(mutations)

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
    by_class: Dict[str, List[float]] = {}
    for m in mutations:
        by_class.setdefault(m.mutation_class, [])
        rate = _run_solution(m.mutated_code, test_cases)
        by_class[m.mutation_class].append(rate)

    return {
        cls: {
            "count": len(rates),
            "avg_pass_rate": sum(rates) / len(rates),
            "fully_killed": sum(1 for r in rates if r < 1.0),
        }
        for cls, rates in by_class.items()
    }


def format_report(report: SuiteStrengthReport) -> str:
    """Human-readable strength report."""
    lines = [
        f"=== Suite Strength Report: {report.problem_id} ===",
        f"Reference solution passes: {report.reference_pass}",
        f"",
        f"Mutation robustness:",
        f"  raw variants:       {report.details.get('raw_mutation_count', report.mutation_count)}",
        f"  effective variants: {report.mutation_count}",
        f"  variants killed:     {report.mutations_killed}",
        f"  kill rate:           {report.mutation_kill_rate:.1%}",
    ]

    redundancy = report.details.get("mutation_redundancy", 0)
    if redundancy > 0:
        lines.append(f"  redundant:          {redundancy} (deduplicated)")

    lines.append(f"")
    lines.append(f"Per-mutation results:")
    for md in report.details.get("mutation_details", []):
        status = "KILLED" if md["killed"] else "SURVIVED"
        timed = " [TIMEOUT]" if md.get("timed_out") else ""
        mfi = md.get("minimal_failing_input")
        mfi_str = f" min_fail={mfi.get('label', '?')}" if mfi else ""
        lines.append(f"  [{status}]{timed} {md['mutation_class']} (v{md['variant_index']}): "
                     f"pass={md['pass_rate']:.0%}{mfi_str} -- {md['description']}")

    lines.append(f"")
    lines.append(f"Per-mutation-class breakdown:")
    breakdown = report.details.get("mutation_breakdown", {})
    for cls, stats in breakdown.items():
        killed = stats["fully_killed"]
        total = stats["count"]
        rate = killed / total if total else 0
        lines.append(f"  {cls}: {killed}/{total} killed ({rate:.0%})")

    lines.append(f"")
    lines.append(f"Test case contribution:")
    contrib = report.details.get("test_contribution", {})
    for idx in sorted(contrib.keys()):
        v = contrib[idx]
        label = v.get("label", f"tc_{idx}")
        delta = v["marginal_kills"]
        marker = " ← CRITICAL" if v["is_critical"] else ""
        lines.append(f"  {label}: marginal_kills={delta}{marker}")

    lines.append(f"")
    lines.append(f"Adversarial tests: {report.adversarial_count} cases generated")
    lines.append(f"Strength score: {report.strength_score:.2f}")

    return "\n".join(lines)

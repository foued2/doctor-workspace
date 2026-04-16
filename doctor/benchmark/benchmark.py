"""
Doctor Benchmark — Mutation robustness across all registered problems.

Produces:
  - Per-problem strength score (mutation kill rate)
  - Breakdown by mutation class
  - Ranked ranking of test suite quality

Output: benchmark_suite_strength_report
"""
from __future__ import annotations

import sys
sys.path.insert(0, 'F:\\pythonProject')

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from doctor.adversarial.mutation_engine import MutationEngine
from doctor.adversarial.adversarial_generator import AdversarialGenerator
from doctor.adversarial.mutation_evaluator import _run_solution
from doctor.registry.problem_registry import get_problems, get_test_cases


def get_reference_from_registry(key: str) -> Optional[str]:
    entry = get_problems().get(key)
    if entry:
        return entry.get("spec", {}).get("reference_solution")
    return None


@dataclass
class ProblemBenchmark:
    problem_id: str
    display_name: str
    difficulty: str
    test_count: int
    ref_passes: bool
    mutation_count: int
    mutations_killed: int
    kill_rate: float
    mutation_breakdown: Dict[str, dict]
    adversarial_count: int
    notes: str = ""


def run_benchmark() -> List[ProblemBenchmark]:
    results = []
    problems = get_problems()

    for key in sorted(problems.keys()):
        entry = problems[key]
        display_name = entry.get("spec", {}).get("display_name", key)
        difficulty = entry.get("spec", {}).get("difficulty", "easy")
        tcs = get_test_cases(key)

        if not tcs:
            results.append(ProblemBenchmark(
                problem_id=key,
                display_name=display_name,
                difficulty=difficulty,
                test_count=0,
                ref_passes=False,
                mutation_count=0,
                mutations_killed=0,
                kill_rate=0.0,
                mutation_breakdown={},
                adversarial_count=0,
                notes="no test cases",
            ))
            continue

        ref_code = get_reference_from_registry(key)
        if not ref_code:
            results.append(ProblemBenchmark(
                problem_id=key,
                display_name=display_name,
                difficulty=difficulty,
                test_count=len(tcs),
                ref_passes=False,
                mutation_count=0,
                mutations_killed=0,
                kill_rate=0.0,
                mutation_breakdown={},
                adversarial_count=0,
                notes="no reference solution available",
            ))
            continue

        engine = MutationEngine(key, num_variants_per_class=3)
        mutations = engine.generate_all(ref_code)

        ref_rate = _run_solution(ref_code, tcs)

        mutations_killed = 0
        breakdown = {}
        for m in mutations:
            m_rate = _run_solution(m.mutated_code, tcs)
            killed = m_rate < 1.0
            if killed:
                mutations_killed += 1
            cls = m.mutation_class
            if cls not in breakdown:
                breakdown[cls] = {"total": 0, "killed": 0}
            breakdown[cls]["total"] += 1
            if killed:
                breakdown[cls]["killed"] += 1

        kill_rate = mutations_killed / len(mutations) if mutations else 0.0

        try:
            gen = AdversarialGenerator(key, f"def {key}(...)", difficulty)
            adv_cases = gen.generate()
            adv_count = len(adv_cases)
        except Exception:
            adv_count = 0

        results.append(ProblemBenchmark(
            problem_id=key,
            display_name=display_name,
            difficulty=difficulty,
            test_count=len(tcs),
            ref_passes=ref_rate == 1.0,
            mutation_count=len(mutations),
            mutations_killed=mutations_killed,
            kill_rate=kill_rate,
            mutation_breakdown=breakdown,
            adversarial_count=adv_count,
        ))

    return results


def format_benchmark(results: List[ProblemBenchmark]) -> str:
    lines = [
        "=" * 80,
        "DOCTOR BENCHMARK — Test Suite Robustness Under Mutation Analysis",
        "=" * 80,
        "",
        f"{'Problem':<35} {'Diff':<8} {'Tests':<6} {'Mutagen':<6} {'Killed':<7} {'Kill%':<7} {'Ref':<5} {'Notes'}",
        "-" * 80,
    ]

    for r in sorted(results, key=lambda x: x.kill_rate):
        mut_str = f"{r.mutations_killed}/{r.mutation_count}" if r.mutation_count > 0 else "n/a"
        ref_str = "PASS" if r.ref_passes else "FAIL"
        pct = f"{r.kill_rate:.0%}" if r.mutation_count > 0 else "n/a"
        note = r.notes if r.notes else ""
        lines.append(
            f"{r.display_name:<35} {r.difficulty:<8} {r.test_count:<6} "
            f"{mut_str:<6} {r.mutations_killed:<7} {pct:<7} {ref_str:<5} {note}"
        )

    lines.append("-" * 80)
    lines.append("")

    # Per-mutation-class aggregate
    class_totals: Dict[str, Dict[str, int]] = {}
    for r in results:
        for cls, stats in r.mutation_breakdown.items():
            if cls not in class_totals:
                class_totals[cls] = {"total": 0, "killed": 0}
            class_totals[cls]["total"] += stats.get("total", 0)
            class_totals[cls]["killed"] += stats.get("killed", 0)

    lines.append("AGGREGATE — Kill Rate by Mutation Class:")
    for cls in sorted(class_totals.keys()):
        t = class_totals[cls]["total"]
        k = class_totals[cls]["killed"]
        rate = k / t if t > 0 else 0
        lines.append(f"  {cls:<35} {k:>3}/{t:<3}  {rate:>6.1%}")

    lines.append("")
    lines.append("=" * 80)

    # Summary stats
    with_ref = [r for r in results if r.ref_passes]
    with_mutations = [r for r in results if r.mutation_count > 0]
    avg_kill = sum(r.kill_rate for r in with_mutations) / len(with_mutations) if with_mutations else 0

    lines.append(f"Problems benchmarked:  {len(results)}")
    lines.append(f"Reference solutions:  {len(with_ref)}/{len(results)} pass")
    lines.append(f"Mutation variants:     {sum(r.mutation_count for r in results)} total")
    lines.append(f"Average kill rate:    {avg_kill:.1%}")
    lines.append("=" * 80)

    return "\n".join(lines)


def main():
    print("Running Doctor benchmark...")
    results = run_benchmark()
    report = format_benchmark(results)
    print(report)

    # Save to file
    with open("doctor/benchmark_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    print("\nReport saved to doctor/benchmark_report.txt")


if __name__ == "__main__":
    main()

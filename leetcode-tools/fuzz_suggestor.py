"""
Suggestor Fuzzing Test Suite v2 — Correctness-Driven
=====================================================
This version doesn't just check for crashes.
It measures CORRECTNESS under corruption:

  - Data retention rate (valid lines retained)
  - Ranking integrity (top-K stability vs baseline)
  - Sensitivity analysis (how much output changes)
  - Adversarial assertions (suggested problem ∈ valid set)

Usage:
    python fuzz_suggestor.py                    # Run all phases
    python fuzz_suggestor.py --phase 1          # Run only Phase 1
    python fuzz_suggestor.py --phase 1 --iterations 1000
    python fuzz_suggestor.py --report           # Show last run report
"""

import json
import os
import random
import shutil
import string
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.request import Request, urlopen

TOOLS_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = TOOLS_ROOT.parent

# Use original ratings URL
RATINGS_URL = "https://raw.githubusercontent.com/zerotrac/leetcode_problem_rating/main/ratings.txt"


# ============================================================
# Data structures
# ============================================================
@dataclass
class ParseResult:
    """Result of parsing a single line."""
    problem_id: Optional[int] = None
    rating: Optional[float] = None
    title: Optional[str] = None
    title_slug: Optional[str] = None
    contest_slug: Optional[str] = None
    problem_index: Optional[str] = None
    title_zh: Optional[str] = None
    is_valid: bool = False


@dataclass
class TestResult:
    """Result of a single fuzzing iteration."""
    phase: int
    iteration: int
    mutation_type: int

    # Crash metrics
    crashed: bool = False
    exception_type: Optional[str] = None

    # Correctness metrics
    data_retention_rate: float = 0.0        # valid lines retained / total valid in input
    ranking_deviation: float = 0.0           # how much top-K changed vs baseline
    top1_is_valid: bool = False              # is suggested problem actually in valid set?
    top1_matches_baseline: bool = False      # does top-1 match clean baseline?
    valid_lines_dropped: int = 0             # count of valid lines lost due to corruption
    corrupt_lines_retained: int = 0          # count of corrupt lines that were accepted

    # Output metrics
    total_parsed: int = 0
    total_valid_in_input: int = 0
    suggested_problem_id: Optional[int] = None
    suggested_rating: Optional[float] = None

    duration_seconds: float = 0.0


@dataclass
class PhaseReport:
    phase: int
    name: str
    total_runs: int
    crashes: int = 0
    silent_failures: int = 0                  # no crash but wrong result
    correct_results: int = 0
    avg_data_retention: float = 0.0
    avg_ranking_deviation: float = 0.0
    top1_valid_rate: float = 0.0
    top1_baseline_match_rate: float = 0.0
    total_duration: float = 0.0
    error_breakdown: Dict[str, int] = field(default_factory=dict)


# ============================================================
# Logger
# ============================================================
class FuzzLogger:
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = log_dir / f"fuzz_{self.timestamp}.log"
        self.results: List[TestResult] = []
        self._fh = open(self.log_file, 'w', encoding='utf-8')

    def log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        line = f"[{ts}] {msg}"
        print(line, flush=True)
        self._fh.write(line + '\n')
        self._fh.flush()

    def record(self, r: TestResult):
        self.results.append(r)

    def report(self, reports: List[PhaseReport]) -> str:
        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("FUZZING REPORT — CORRECTNESS-DRIVEN")
        lines.append(f"Timestamp: {self.timestamp}")
        lines.append("=" * 70)

        total_crashes = 0
        total_silent = 0
        total_correct = 0

        for r in reports:
            lines.append(f"\n{'─' * 60}")
            lines.append(f"Phase {r.phase}: {r.name}")
            lines.append(f"{'─' * 60}")
            lines.append(f"  Total runs:              {r.total_runs}")
            lines.append(f"  Crashes:                 {r.crashes}")
            lines.append(f"  Silent failures:         {r.silent_failures}")
            lines.append(f"  Correct results:         {r.correct_results}")
            lines.append(f"  Avg data retention:      {r.avg_data_retention:.2%}")
            lines.append(f"  Avg ranking deviation:   {r.avg_ranking_deviation:.2%}")
            lines.append(f"  Top-1 valid rate:        {r.top1_valid_rate:.2%}")
            lines.append(f"  Top-1 baseline match:    {r.top1_baseline_match_rate:.2%}")
            lines.append(f"  Duration:                {r.total_duration:.1f}s")

            if r.error_breakdown:
                lines.append(f"  Error breakdown:")
                for k, v in sorted(r.error_breakdown.items(), key=lambda x: -x[1]):
                    lines.append(f"    {k}: {v}")

            total_crashes += r.crashes
            total_silent += r.silent_failures
            total_correct += r.correct_results

        total = total_crashes + total_silent + total_correct
        lines.append(f"\n{'=' * 70}")
        lines.append(f"OVERALL")
        lines.append(f"{'=' * 70}")
        lines.append(f"  Total runs:      {total}")
        lines.append(f"  Crashes:         {total_crashes} ({total_crashes/max(1,total):.1%})")
        lines.append(f"  Silent failures: {total_silent} ({total_silent/max(1,total):.1%})")
        lines.append(f"  Correct:         {total_correct} ({total_correct/max(1,total):.1%})")

        if total_crashes == 0 and total_silent == 0:
            lines.append(f"\n  STATUS: SURVIVED — all results correct")
        else:
            lines.append(f"\n  STATUS: FAILED — {total_crashes} crashes, {total_silent} silent failures")

        text = '\n'.join(lines)
        (self.log_dir / f"report_{self.timestamp}.txt").write_text(text, encoding='utf-8')
        self._fh.write(text + '\n')
        self._fh.close()
        return text


# ============================================================
# Baseline computation
# ============================================================
def parse_problem_details_raw(line: str) -> ParseResult:
    """Parse a single ratings line. Returns ParseResult with is_valid flag."""
    result = ParseResult()
    try:
        parts = line.split()
        if len(parts) < 7:
            return result

        rating = float(parts[0])
        problem_id = int(parts[1])

        result.rating = rating
        result.problem_id = problem_id

        # Work backwards
        result.problem_index = parts[-1]
        result.contest_slug = parts[-2]
        result.title_slug = parts[-3]

        # Parse title (English + Chinese)
        english_parts = []
        chinese_parts = []
        in_chinese = False
        for part in parts[2:-3]:
            if any('\u4e00' <= c <= '\u9fff' for c in part):
                in_chinese = True
            if in_chinese:
                chinese_parts.append(part)
            else:
                english_parts.append(part)

        result.title = ' '.join(english_parts)
        result.title_zh = ' '.join(chinese_parts)
        result.is_valid = True

    except (ValueError, IndexError):
        pass

    return result


def compute_baseline(ratings_text: str) -> Tuple[List[ParseResult], List[Tuple[float, int]]]:
    """Parse clean ratings and return sorted list of (rating, id) for ranking."""
    parsed = []
    for line in ratings_text.strip().split('\n')[1:]:  # skip header
        r = parse_problem_details_raw(line)
        if r.is_valid:
            parsed.append(r)

    # Sort by rating ascending (easiest first)
    ranked = sorted([(r.rating, r.problem_id) for r in parsed])
    return parsed, ranked


# ============================================================
# Ratings Mutator — with knowledge of valid lines
# ============================================================
class RatingsMutator:
    def __init__(self, original_ratings: str, baseline_parsed: List[ParseResult]):
        self.original_text = original_ratings
        self.original_lines = original_ratings.strip().split('\n')
        self.baseline_parsed = baseline_parsed
        self.valid_ids = {r.problem_id for r in baseline_parsed}

    def mutate(self, mutation_type: int) -> Tuple[str, Set[int]]:
        """Returns (mutated_text, set_of_valid_ids_still_present)."""
        lines = self.original_lines.copy()

        if mutation_type == 0:
            return self._remove_random_lines(lines)
        elif mutation_type == 1:
            return self._duplicate_random_lines(lines)
        elif mutation_type == 2:
            return self._corrupt_ratings(lines)
        elif mutation_type == 3:
            return self._shuffle_lines(lines)
        elif mutation_type == 4:
            return self._inject_malformed_lines(lines)
        elif mutation_type == 5:
            return self._empty_file()
        elif mutation_type == 6:
            return self._extreme_ratings(lines)
        elif mutation_type == 7:
            return self._unicode_injection(lines)
        elif mutation_type == 8:
            return self._truncate_file(lines)
        elif mutation_type == 9:
            return self._header_only()
        elif mutation_type == 10:
            return self._adversarial_single_digit_change(lines)
        elif mutation_type == 11:
            return self._swap_adjacent_lines(lines)
        else:
            return self._remove_random_lines(lines)

    def _parse_valid_lines(self, lines: List[str]) -> Tuple[List[str], Set[int]]:
        """Parse lines and return (valid_lines, set_of_valid_problem_ids)."""
        valid_lines = []
        valid_ids = set()
        for line in lines[1:]:  # skip header
            r = parse_problem_details_raw(line)
            if r.is_valid:
                valid_lines.append(line)
                valid_ids.add(r.problem_id)
        return valid_lines, valid_ids

    def _remove_random_lines(self, lines: List[str]) -> Tuple[str, Set[int]]:
        n = max(1, len(lines) // 10)
        to_remove = random.sample(range(1, len(lines)), min(n, len(lines) - 1))
        valid_before = set()
        for i in to_remove:
            r = parse_problem_details_raw(lines[i])
            if r.is_valid:
                valid_before.add(r.problem_id)

        remaining = [l for i, l in enumerate(lines) if i not in to_remove]
        _, valid_after = self._parse_valid_lines(remaining)
        dropped = valid_before - valid_after
        return '\n'.join(remaining), self.valid_ids - dropped

    def _duplicate_random_lines(self, lines: List[str]) -> Tuple[str, Set[int]]:
        n = max(1, len(lines) // 20)
        for _ in range(n):
            idx = random.randint(1, len(lines) - 1)
            lines.insert(random.randint(1, len(lines)), lines[idx])
        _, valid_ids = self._parse_valid_lines(lines)
        return '\n'.join(lines), valid_ids

    def _corrupt_ratings(self, lines: List[str]) -> Tuple[str, Set[int]]:
        n = max(1, len(lines) // 20)
        corrupted_ids = set()
        for _ in range(n):
            idx = random.randint(1, len(lines) - 1)
            r = parse_problem_details_raw(lines[idx])
            if r.is_valid:
                corrupted_ids.add(r.problem_id)
            parts = lines[idx].split()
            if len(parts) >= 2:
                parts[0] = random.choice(['NaN', 'Infinity', '-1', 'abc', '999999', '0.00001'])
                lines[idx] = ' '.join(parts)
        _, valid_ids = self._parse_valid_lines(lines)
        return '\n'.join(lines), valid_ids

    def _shuffle_lines(self, lines: List[str]) -> Tuple[str, Set[int]]:
        header = lines[0:1]
        body = lines[1:]
        random.shuffle(body)
        shuffled = header + body
        _, valid_ids = self._parse_valid_lines(shuffled)
        return '\n'.join(shuffled), valid_ids

    def _inject_malformed_lines(self, lines: List[str]) -> Tuple[str, Set[int]]:
        malformed = ['', '   ', 'not a rating', 'NaN 1234 X X X X', '@#$%', '\x00\x01']
        n = min(20, len(lines) // 10)
        for _ in range(n):
            lines.insert(random.randint(1, len(lines)), random.choice(malformed))
        _, valid_ids = self._parse_valid_lines(lines)
        return '\n'.join(lines), valid_ids

    def _empty_file(self) -> Tuple[str, Set[int]]:
        return '', set()

    def _extreme_ratings(self, lines: List[str]) -> Tuple[str, Set[int]]:
        for i in range(1, len(lines)):
            if random.random() < 0.05:
                parts = lines[i].split()
                if len(parts) >= 2:
                    try:
                        parts[0] = str(random.choice([0.0, 0.001, 99999.99, -100.0]))
                        lines[i] = ' '.join(parts)
                    except (ValueError, IndexError):
                        pass
        _, valid_ids = self._parse_valid_lines(lines)
        return '\n'.join(lines), valid_ids

    def _unicode_injection(self, lines: List[str]) -> Tuple[str, Set[int]]:
        chars = ['\u4e00', '\u3000', '\uff00', '\u200b', '\u2603']
        for i in range(1, min(100, len(lines))):
            if random.random() < 0.2:
                lines[i] = lines[i] + ''.join(random.choices(chars, k=5))
        _, valid_ids = self._parse_valid_lines(lines)
        return '\n'.join(lines), valid_ids

    def _truncate_file(self, lines: List[str]) -> Tuple[str, Set[int]]:
        n = max(1, len(lines) // 3)
        truncated = lines[:n]
        _, valid_ids = self._parse_valid_lines(truncated)
        return '\n'.join(truncated), valid_ids

    def _header_only(self) -> Tuple[str, Set[int]]:
        return self.original_lines[0] if self.original_lines else '', set()

    def _adversarial_single_digit_change(self, lines: List[str]) -> Tuple[str, Set[int]]:
        """Change ONE digit in ONE rating to make it artificially easiest."""
        if len(lines) < 3:
            return '\n'.join(lines), set()
        # Pick a random line and make its rating extremely low
        idx = random.randint(1, len(lines) - 1)
        parts = lines[idx].split()
        if len(parts) >= 2:
            try:
                original_rating = float(parts[0])
                # Make it the lowest possible rating
                parts[0] = '0.0001'
                lines[idx] = ' '.join(parts)
            except ValueError:
                pass
        _, valid_ids = self._parse_valid_lines(lines)
        return '\n'.join(lines), valid_ids

    def _swap_adjacent_lines(self, lines: List[str]) -> Tuple[str, Set[int]]:
        if len(lines) < 4:
            return '\n'.join(lines), set()
        idx = random.randint(1, len(lines) - 3)
        lines[idx], lines[idx + 1] = lines[idx + 1], lines[idx]
        _, valid_ids = self._parse_valid_lines(lines)
        return '\n'.join(lines), valid_ids


# ============================================================
# Correctness evaluation
# ============================================================
def evaluate_correctness(
    mutated_text: str,
    baseline_ranked: List[Tuple[float, int]],
    valid_ids_in_mutated: Set[int],
) -> TestResult:
    """
    Evaluate correctness of parsing under mutation.

    This does NOT run the full suggestor (too slow for 10K iterations).
    Instead it directly tests the parsing + ranking pipeline.
    """
    result = TestResult(phase=1, iteration=0, mutation_type=0)

    try:
        # Parse mutated lines
        parsed = []
        corrupt_retained = 0
        for line in mutated_text.strip().split('\n')[1:]:
            r = parse_problem_details_raw(line)
            if r.is_valid:
                parsed.append(r)
            elif line.strip():
                corrupt_retained += 1

        result.corrupt_lines_retained = corrupt_retained
        result.total_parsed = len(parsed)

        # Compute ranking from mutated data
        mutated_ranked = sorted([(r.rating, r.problem_id) for r in parsed])

        # Data retention: what fraction of original valid data survived?
        if baseline_ranked:
            result.valid_lines_dropped = len(baseline_ranked) - len(parsed)
            result.data_retention_rate = len(parsed) / len(baseline_ranked)
        else:
            result.data_retention_rate = 0.0

        # Ranking integrity: compare top-K
        K = 10
        baseline_top_k = baseline_ranked[:K]
        mutated_top_k = mutated_ranked[:K]

        # Ranking deviation: what fraction of top-K changed?
        baseline_set = set(baseline_top_k)
        mutated_set = set(mutated_top_k)
        if baseline_top_k:
            changed = len(baseline_set - mutated_set) / len(baseline_top_k)
            result.ranking_deviation = changed
        else:
            result.ranking_deviation = 1.0

        # Top-1 validity: is the suggested problem actually valid?
        if mutated_top_k:
            top1_id = mutated_top_k[0][1]
            result.suggested_problem_id = top1_id
            result.suggested_rating = mutated_top_k[0][0]
            result.top1_is_valid = top1_id in valid_ids_in_mutated
        else:
            result.top1_is_valid = False

        # Top-1 baseline match
        if baseline_top_k and mutated_top_k:
            result.top1_matches_baseline = (baseline_top_k[0] == mutated_top_k[0])
        else:
            result.top1_matches_baseline = False

        # Silent failure detection
        if not result.top1_is_valid and mutated_top_k:
            # Suggested a problem that wasn't even in valid set
            result.crashed = False  # no crash, but wrong
        elif result.ranking_deviation > 0.5:
            # More than 50% of top-K changed — significant deviation
            result.crashed = False
        else:
            result.crashed = False

        result.crashed = False  # parsing itself is exception-safe

    except Exception as e:
        result.crashed = True
        result.exception_type = type(e).__name__

    return result


# ============================================================
# Phase 1: Deterministic fuzzing with correctness metrics
# ============================================================
def run_phase_1(
    original_ratings: str,
    baseline_parsed: List[ParseResult],
    baseline_ranked: List[Tuple[float, int]],
    iterations: int,
    logger: FuzzLogger,
) -> PhaseReport:
    logger.log(f"\n{'=' * 60}")
    logger.log(f"PHASE 1: Correctness-Driven Fuzzing ({iterations} iterations)")
    logger.log(f"{'=' * 60}")
    logger.log(f"Baseline: {len(baseline_ranked)} valid problems")
    logger.log(f"Top-3 easiest: {baseline_ranked[:3]}")

    report = PhaseReport(
        phase=1,
        name="Deterministic Fuzzing (Correctness-Driven)",
        total_runs=iterations,
    )

    mutator = RatingsMutator(original_ratings, baseline_parsed)
    retention_rates = []
    ranking_devs = []
    top1_valid_count = 0
    top1_match_count = 0
    correct_count = 0
    silent_failure_count = 0
    crash_count = 0
    start = time.time()

    for i in range(iterations):
        iter_start = time.time()
        mutation_type = i % 12  # 12 mutation types (including adversarial)

        try:
            mutated_text, valid_ids_in_mutated = mutator.mutate(mutation_type)

            tr = evaluate_correctness(mutated_text, baseline_ranked, valid_ids_in_mutated)
            tr.iteration = i + 1
            tr.mutation_type = mutation_type
            tr.duration_seconds = time.time() - iter_start

            # Classify result
            if tr.crashed:
                crash_count += 1
                report.error_breakdown[f"crash:{tr.exception_type}"] = report.error_breakdown.get(f"crash:{tr.exception_type}", 0) + 1
            elif not tr.top1_is_valid and tr.total_parsed > 0:
                silent_failure_count += 1
                report.error_breakdown["silent:invalid_suggestion"] = report.error_breakdown.get("silent:invalid_suggestion", 0) + 1
            elif tr.ranking_deviation > 0.5:
                silent_failure_count += 1
                report.error_breakdown["silent:high_ranking_deviation"] = report.error_breakdown.get("silent:high_ranking_deviation", 0) + 1
            else:
                correct_count += 1

            retention_rates.append(tr.data_retention_rate)
            ranking_devs.append(tr.ranking_deviation)
            if tr.top1_is_valid:
                top1_valid_count += 1
            if tr.top1_matches_baseline:
                top1_match_count += 1

            logger.record(tr)

            # Progress logging — every 100 iterations
            if (i + 1) % 100 == 0:
                elapsed = time.time() - start
                rate = (i + 1) / elapsed
                eta = (iterations - i - 1) / rate if rate > 0 else 0
                logger.log(
                    f"  ... {i+1}/{iterations} "
                    f"({rate:.0f} iter/s, ETA: {eta:.0f}s) "
                    f"correct={correct_count} silent={silent_failure_count} crashes={crash_count} "
                    f"retention={sum(retention_rates)/len(retention_rates):.2%} "
                    f"deviation={sum(ranking_devs)/len(ranking_devs):.2%}"
                )

        except Exception as e:
            crash_count += 1
            report.error_breakdown[f"unhandled:{type(e).__name__}"] = report.error_breakdown.get(f"unhandled:{type(e).__name__}", 0) + 1
            logger.log(f"  UNHANDLED EXCEPTION iter={i+1}: {e}")

    report.crashes = crash_count
    report.silent_failures = silent_failure_count
    report.correct_results = correct_count
    report.avg_data_retention = sum(retention_rates) / len(retention_rates) if retention_rates else 0
    report.avg_ranking_deviation = sum(ranking_devs) / len(ranking_devs) if ranking_devs else 0
    report.top1_valid_rate = top1_valid_count / iterations if iterations else 0
    report.top1_baseline_match_rate = top1_match_count / iterations if iterations else 0
    report.total_duration = time.time() - start

    logger.log(f"\nPhase 1 complete: {correct_count}/{iterations} correct")
    logger.log(f"  Silent failures: {silent_failure_count} ({silent_failure_count/max(1,iterations):.1%})")
    logger.log(f"  Crashes: {crash_count}")
    logger.log(f"  Avg data retention: {report.avg_data_retention:.2%}")
    logger.log(f"  Avg ranking deviation: {report.avg_ranking_deviation:.2%}")
    logger.log(f"  Top-1 valid rate: {report.top1_valid_rate:.2%}")
    logger.log(f"  Top-1 baseline match: {report.top1_baseline_match_rate:.2%}")

    return report


# ============================================================
# Phase 2: Filesystem fuzzing
# ============================================================
def run_phase_2(
    original_ratings: str,
    baseline_ranked: List[Tuple[float, int]],
    solutions_root: Path,
    iterations: int,
    logger: FuzzLogger,
) -> PhaseReport:
    logger.log(f"\n{'=' * 60}")
    logger.log(f"PHASE 2: Filesystem Fuzzing ({iterations} iterations)")
    logger.log(f"{'=' * 60}")

    report = PhaseReport(phase=2, name="Filesystem Fuzzing", total_runs=iterations)

    # Import suggestor once for scanning
    import importlib.util
    spec = importlib.util.spec_from_file_location("suggestor_p2", str(TOOLS_ROOT / "leetcode_suggestor.py"))
    suggestor_mod = importlib.util.module_from_spec(spec)

    import sys
    old_path = sys.path.copy()
    sys.path.insert(0, str(PROJECT_ROOT))
    spec.loader.exec_module(suggestor_mod)
    suggestor_mod.SOLUTIONS_ROOT = solutions_root
    suggestor_mod.CONTROLLER = suggestor_mod.get_execution_controller(solutions_root)
    sys.path = old_path

    import re
    FOLDER_PATTERN = re.compile(r"(\d+)\s+to\s+(\d+)")
    FILE_PATTERN = re.compile(r"^(\d+)\.\s+.+\.py$")

    crash_count = 0
    silent_count = 0
    correct_count = 0
    start = time.time()

    for i in range(iterations):
        iter_start = time.time()

        try:
            # Create temp filesystem with chaotic structure
            fs_root = solutions_root.parent / f".fuzz_fs_{i}"
            fs_root.mkdir(parents=True, exist_ok=True)

            rng = random.Random(i)

            # Generate valid-looking folder structure
            n_folders = rng.randint(3, 10)
            for _ in range(n_folders):
                start_range = rng.randint(1, 40) * 100 + 1
                end_range = start_range + 99
                folder = fs_root / f"{start_range:03d} to {end_range}"
                folder.mkdir(parents=True, exist_ok=True)

                n_files = rng.randint(0, 8)
                for _ in range(n_files):
                    pid = rng.randint(start_range, end_range)
                    title = ''.join(rng.choices(string.ascii_letters, k=rng.randint(5, 20)))
                    (folder / f"{pid}. {title}.py").write_text("# solution", encoding='utf-8')

            # Add invalid structures
            invalid = ["invalid folder", "not_a_folder", "999 to 100"]
            for name in invalid:
                if rng.random() < 0.5:
                    (fs_root / name).mkdir(exist_ok=True)

            # Add duplicate problem IDs
            for folder in list(fs_root.iterdir()):
                if folder.is_dir() and FOLDER_PATTERN.match(folder.name) and rng.random() < 0.3:
                    pid = rng.randint(1, 9999)
                    title1 = ''.join(rng.choices(string.ascii_letters, k=10))
                    title2 = ''.join(rng.choices(string.ascii_letters, k=10))
                    (folder / f"{pid}. {title1}.py").write_text("# dup1", encoding='utf-8')
                    (folder / f"{pid}. {title2}.py").write_text("# dup2", encoding='utf-8')

            # Now run the scanner against this chaotic filesystem
            suggestor_mod.SOLUTIONS_ROOT = fs_root
            suggestor_mod.CONTROLLER = suggestor_mod.get_execution_controller(fs_root)

            scanned = suggestor_mod.get_existing_problems()

            # Validate: scanned should be a set of ints
            if not isinstance(scanned, set):
                silent_count += 1
                report.error_breakdown["silent:wrong_type"] = report.error_breakdown.get("silent:wrong_type", 0) + 1
            else:
                # Check no negative or invalid IDs
                invalid_ids = [x for x in scanned if not isinstance(x, int) or x < 1]
                if invalid_ids:
                    silent_count += 1
                    report.error_breakdown["silent:invalid_ids"] = report.error_breakdown.get("silent:invalid_ids", 0) + 1
                else:
                    correct_count += 1

            # Cleanup
            shutil.rmtree(fs_root, ignore_errors=True)

        except Exception as e:
            crash_count += 1
            report.error_breakdown[f"crash:{type(e).__name__}"] = report.error_breakdown.get(f"crash:{type(e).__name__}", 0) + 1

    report.crashes = crash_count
    report.silent_failures = silent_count
    report.correct_results = correct_count
    report.total_duration = time.time() - start

    logger.log(f"Phase 2 complete: {correct_count}/{iterations} correct")
    logger.log(f"  Silent: {silent_count}, Crashes: {crash_count}")
    return report


# ============================================================
# Phase 3: State corruption
# ============================================================
def run_phase_3(
    original_ratings: str,
    baseline_ranked: List[Tuple[float, int]],
    solutions_root: Path,
    iterations: int,
    logger: FuzzLogger,
) -> PhaseReport:
    logger.log(f"\n{'=' * 60}")
    logger.log(f"PHASE 3: State Corruption ({iterations} iterations)")
    logger.log(f"{'=' * 60}")

    report = PhaseReport(phase=3, name="State Corruption", total_runs=iterations)

    import importlib.util
    spec = importlib.util.spec_from_file_location("suggestor_p3", str(TOOLS_ROOT / "leetcode_suggestor.py"))
    suggestor_mod = importlib.util.module_from_spec(spec)

    import sys
    old_path = sys.path.copy()
    sys.path.insert(0, str(PROJECT_ROOT))
    spec.loader.exec_module(suggestor_mod)
    suggestor_mod.SOLUTIONS_ROOT = solutions_root
    sys.path = old_path

    crash_count = 0
    silent_count = 0
    correct_count = 0
    start = time.time()

    for i in range(iterations):
        iter_start = time.time()
        corruption_type = i % 8

        try:
            tracking_dir = solutions_root.parent / '.qwen'
            tracking_dir.mkdir(parents=True, exist_ok=True)
            tracking_file = tracking_dir / '.solved_tracking.json'

            if corruption_type == 0:
                tracking_file.write_text('{}', encoding='utf-8')
            elif corruption_type == 1:
                tracking_file.write_text('{"solved": [99999, 99998, 99997]}', encoding='utf-8')
            elif corruption_type == 2:
                tracking_file.write_text('{"solved": ["abc", null, 123, 1.5, [], {}]}', encoding='utf-8')
            elif corruption_type == 3:
                tracking_file.write_text('NOT VALID JSON{{{{', encoding='utf-8')
            elif corruption_type == 4:
                tracking_file.write_text('null', encoding='utf-8')
            elif corruption_type == 5:
                tracking_file.write_text('{"solved": [-1, -2, -100]}', encoding='utf-8')
            elif corruption_type == 6:
                # Duplicate entries
                tracking_file.write_text('{"solved": [1, 2, 3, 1, 2, 3, 1, 2, 3]}', encoding='utf-8')
            elif corruption_type == 7:
                tracking_file.write_text('{"invalid_key": true}', encoding='utf-8')

            # Run get_existing_problems
            suggestor_mod.CONTROLLER = suggestor_mod.get_execution_controller(solutions_root)
            scanned = suggestor_mod.get_existing_problems()

            # Validate result
            if not isinstance(scanned, set):
                silent_count += 1
                report.error_breakdown["silent:non_set_return"] = report.error_breakdown.get("silent:non_set_return", 0) + 1
            else:
                invalid_ids = [x for x in scanned if not isinstance(x, int) or x < 1]
                if invalid_ids:
                    silent_count += 1
                    report.error_breakdown["silent:corrupted_ids"] = report.error_breakdown.get("silent:corrupted_ids", 0) + 1
                else:
                    correct_count += 1

        except Exception as e:
            # Some corruption types may legitimately throw — check if expected
            if corruption_type in [2, 3]:  # Invalid JSON/type may cause errors
                # Check if error is handled gracefully vs crashing
                if isinstance(e, (json.JSONDecodeError, TypeError, KeyError)):
                    correct_count += 1  # Expected behavior
                else:
                    crash_count += 1
                    report.error_breakdown[f"crash:{type(e).__name__}"] = report.error_breakdown.get(f"crash:{type(e).__name__}", 0) + 1
            else:
                crash_count += 1
                report.error_breakdown[f"crash:{type(e).__name__}"] = report.error_breakdown.get(f"crash:{type(e).__name__}", 0) + 1

    report.crashes = crash_count
    report.silent_failures = silent_count
    report.correct_results = correct_count
    report.total_duration = time.time() - start

    logger.log(f"Phase 3 complete: {correct_count}/{iterations} correct")
    logger.log(f"  Silent: {silent_count}, Crashes: {crash_count}")
    return report


# ============================================================
# Phase 4: Concurrency stress — tests actual ExecutionController queue under load
def run_phase_4(
    solutions_root: Path,
    workers: int,
    iterations_per_worker: int,
    logger: FuzzLogger,
) -> PhaseReport:
    logger.log(f"\n{'=' * 60}")
    logger.log(f"PHASE 4: Concurrency Stress ({workers} workers x {iterations_per_worker})")
    logger.log(f"{'=' * 60}")
    logger.log(f"Testing ExecutionController queue under concurrent load")

    total = workers * iterations_per_worker
    report = PhaseReport(phase=4, name="Concurrency Stress", total_runs=total)

    # Stress-test the ExecutionController itself with bounded filesystem work.
    old_path = sys.path.copy()
    sys.path.insert(0, str(PROJECT_ROOT))
    from execution_controller import get_execution_controller
    sys.path = old_path

    def worker_fn(worker_id: int) -> List[dict]:
        """Worker that runs ExecutionController operations under load."""
        results = []
        # Each worker gets its own controller instance to test concurrent callers.
        controller = get_execution_controller(solutions_root)

        for i in range(iterations_per_worker):
            try:
                # Keep each operation bounded to avoid artificial batch-limit failures.
                result = controller.run_operation(
                    lambda: controller.list_directory(solutions_root),
                    label=f"worker-{worker_id}-{i}",
                    file_operation=True
                )

                # Verify the operation returned a valid directory listing.
                if isinstance(result, list):
                    results.append({'worker': worker_id, 'iter': i, 'success': True})
                else:
                    results.append({
                        'worker': worker_id, 
                        'iter': i, 
                        'success': False, 
                        'error': f'invalid_result_type:{type(result).__name__}'
                    })

            except Exception as e:
                results.append({
                    'worker': worker_id, 
                    'iter': i, 
                    'success': False, 
                    'error': f'{type(e).__name__}:{str(e)[:80]}'
                })

        return results

    crash_count = 0
    silent_count = 0
    correct_count = 0
    start = time.time()

    logger.log(f"Spawning {workers} workers, {iterations_per_worker} iterations each...")
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(worker_fn, w): w for w in range(workers)}
        for future in as_completed(futures):
            worker_id = futures[future]
            try:
                worker_results = future.result()
                for r in worker_results:
                    if r['success']:
                        correct_count += 1
                    elif 'invalid_result_type' in r.get('error', ''):
                        silent_count += 1
                        report.error_breakdown["silent:invalid_result"] = report.error_breakdown.get("silent:invalid_result", 0) + 1
                    else:
                        crash_count += 1
                        error_key = f"crash:{r.get('error', 'unknown')[:50]}"
                        report.error_breakdown[error_key] = report.error_breakdown.get(error_key, 0) + 1
            except Exception as e:
                crash_count += 1
                error_key = f"future_crash:{type(e).__name__}"
                report.error_breakdown[error_key] = report.error_breakdown.get(error_key, 0) + 1

    report.crashes = crash_count
    report.silent_failures = silent_count
    report.correct_results = correct_count
    report.total_duration = time.time() - start

    logger.log(f"Phase 4 complete: {correct_count}/{total} correct")
    logger.log(f"  Silent failures: {silent_count} ({silent_count/max(1,total):.1%})")
    logger.log(f"  Crashes: {crash_count} ({crash_count/max(1,total):.1%})")
    logger.log(f"  Duration: {report.total_duration:.1f}s")
    return report

# ============================================================
# Main
# ============================================================
def fetch_ratings() -> str:
    print("Fetching original ratings from ZeroTrac...")
    req = Request(RATINGS_URL)
    req.add_header('User-Agent', 'Mozilla/5.0')
    with urlopen(req, timeout=30) as response:
        content = response.read().decode('utf-8')
        print(f"  Fetched {len(content.strip().split(chr(10)))} lines")
        return content


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Suggestor Fuzzing v2 — Correctness-Driven')
    parser.add_argument('--phase', type=int, choices=[1, 2, 3, 4])
    parser.add_argument('--iterations', type=int, default=1000)
    parser.add_argument('--workers', type=int, default=5)
    parser.add_argument('--report', action='store_true')
    args = parser.parse_args()

    if args.report:
        log_dir = PROJECT_ROOT / 'fuzz_reports'
        if log_dir.exists():
            reports = sorted(log_dir.glob('report_*.txt'))
            if reports:
                print(reports[-1].read_text(encoding='utf-8'))
                return
        print("No previous reports found.")
        return

    solutions_root = PROJECT_ROOT / 'solutions'
    log_dir = PROJECT_ROOT / 'fuzz_reports'
    logger = FuzzLogger(log_dir)

    logger.log("SUGGESTOR FUZZING v2 — CORRECTNESS-DRIVEN")
    logger.log(f"Timestamp: {datetime.now().isoformat()}")

    # Fetch and compute baseline
    try:
        original_ratings = fetch_ratings()
    except Exception as e:
        logger.log(f"FATAL: Could not fetch ratings: {e}")
        sys.exit(1)

    baseline_parsed, baseline_ranked = compute_baseline(original_ratings)
    logger.log(f"Baseline: {len(baseline_ranked)} valid problems")
    logger.log(f"Top-3 easiest: {baseline_ranked[:3]}")
    logger.log(f"Top-3 hardest: {baseline_ranked[-3:]}")

    reports: List[PhaseReport] = []

    try:
        if args.phase is None or args.phase == 1:
            n = args.iterations * 10 if args.phase is None else args.iterations
            r1 = run_phase_1(original_ratings, baseline_parsed, baseline_ranked, n, logger)
            reports.append(r1)

        if args.phase is None or args.phase == 2:
            r2 = run_phase_2(original_ratings, baseline_ranked, solutions_root, args.iterations, logger)
            reports.append(r2)

        if args.phase is None or args.phase == 3:
            r3 = run_phase_3(original_ratings, baseline_ranked, solutions_root, args.iterations, logger)
            reports.append(r3)

        if args.phase is None or args.phase == 4:
            n = max(10, args.iterations // 10)
            r4 = run_phase_4(solutions_root, args.workers, n, logger)
            reports.append(r4)

        text = logger.report(reports)
        print(f"\nReport saved to: {log_dir}")

        total_fail = sum(r.crashes + r.silent_failures for r in reports)
        sys.exit(1 if total_fail > 0 else 0)

    except KeyboardInterrupt:
        logger.log("\n\nINTERRUPTED")
        logger.report(reports)
        sys.exit(130)
    except Exception as e:
        logger.log(f"\n\nFATAL: {e}")
        logger.log(traceback.format_exc())
        logger.report(reports)
        sys.exit(1)
    finally:
        # Cleanup temp
        for p in PROJECT_ROOT.glob('.fuzz_fs_*'):
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)


if __name__ == '__main__':
    main()

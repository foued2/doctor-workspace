"""
S-Scaling Experiment v2 — Formal Measurement Framework
========================================================
≥4 input sizes, ≥3 runs per size, variance measurement.
Raw growth metrics only — no classification thresholds.

Outputs:
  - Raw step counts per run
  - Mean + variance per size
  - Log-log slope
  - Slope ratio vs reference (where reference exists)
  - absolute_growth + relative_optimality (orthogonal signals)
  - validation_strength per problem
  - measurement_status (valid / invalid_measurement)
"""

import sys
import json
import copy
import time
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'F:\pythonProject')

from doctor.s_measurement import (
    compute_growth_measurement,
    measurement_to_dict,
    REFERENCE_MODELS,
    VALIDATION_PROFILES,
)


# ═══════════════════════════════════════════════════════════
# TRACE
# ═══════════════════════════════════════════════════════════

class Trace:
    def __init__(self):
        self.steps = 0
        self.unique = set()
        self.solutions = 0

    def record(self, key):
        self.steps += 1
        self.unique.add(str(key))

    def record_solution(self):
        self.solutions += 1


# ═══════════════════════════════════════════════════════════
# N-QUEENS SOLVERS (instrumented)
# ═══════════════════════════════════════════════════════════

def is_valid_nq(board, row, col):
    for r in range(row):
        if board[r] == col or abs(board[r] - col) == abs(r - row):
            return False
    return True

def nq_correct(n, t):
    sols = []
    def bt(row, board):
        t.record(('call', row, tuple(board)))
        if row == n:
            sols.append(board[:]); t.record_solution(); return
        for col in range(n):
            if is_valid_nq(board, row, col):
                board[row] = col; t.record(('place', row, col))
                bt(row+1, board)
                board[row] = -1
    bt(0, [-1]*n)
    return sols

def nq_partial(n, t):
    sols = []
    def bt(row, board):
        t.record(('call', row, tuple(board)))
        if row == n:
            sols.append(board[:]); t.record_solution(); return True
        for col in range(n):
            if is_valid_nq(board, row, col):
                board[row] = col; t.record(('place', row, col))
                if bt(row+1, board): return True
                board[row] = -1
    bt(0, [-1]*n)
    return sols

def nq_bruteforce(n, t):
    sols = []
    def gen(row, board):
        if row == n:
            t.record(('validate', tuple(board)))
            valid = all(
                board[i] != board[j] and abs(board[i]-board[j]) != abs(i-j)
                for i in range(n) for j in range(i)
            )
            if valid: sols.append(board[:]); t.record_solution()
            return
        for col in range(n):
            board[row] = col; t.record(('assign', row, col))
            gen(row+1, board); board[row] = -1
    gen(0, [-1]*n)
    return sols


# ═══════════════════════════════════════════════════════════
# SUDOKU SOLVERS (instrumented) — attempt remediation
# ═══════════════════════════════════════════════════════════

def poss(board, r, c):
    filled = {board[r][k] for k in range(9) if board[r][k] != '.'}
    filled |= {board[k][c] for k in range(9) if board[k][c] != '.'}
    br, bc = 3*(r//3), 3*(c//3)
    for rr in range(br, br+3):
        for cc in range(bc, bc+3):
            if board[rr][cc] != '.': filled.add(board[rr][cc])
    return [d for d in "123456789" if d not in filled]

def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == '.': return (i,j)
    return None

SUDOKU_STD = [
    ["5","3",".",".","7",".",".",".","."],
    ["6",".",".","1","9","5",".",".","."],
    [".","9","8",".",".",".",".","6","."],
    ["8",".",".",".","6",".",".",".","3"],
    ["4",".",".","8",".","3",".",".","1"],
    ["7",".",".",".","2",".",".",".","6"],
    [".","6",".",".",".",".","2","8","."],
    [".",".",".","4","1","9",".",".","5"],
    [".",".",".",".","8",".",".","7","9"],
]

SUDOKU_SOLUTION = [
    ["5","3","4","6","7","8","9","1","2"],
    ["6","7","2","1","9","5","3","4","8"],
    ["1","9","8","3","4","2","5","6","7"],
    ["8","5","9","7","6","1","4","2","3"],
    ["4","2","6","8","5","3","7","9","1"],
    ["7","1","3","9","2","4","8","5","6"],
    ["9","6","1","5","3","7","2","8","4"],
    ["2","8","7","4","1","9","6","3","5"],
    ["3","4","5","2","8","6","1","7","9"],
]

def make_sudoku(empty_count):
    """Create Sudoku board with exactly empty_count empty cells."""
    board = [row[:] for row in SUDOKU_STD]
    current_empty = sum(row.count('.') for row in board)
    if empty_count < current_empty:
        # Fill in some empty cells from solution
        import random
        random.seed(42)
        to_fill = current_empty - empty_count
        empty_cells = [(i,j) for i in range(9) for j in range(9) if board[i][j] == '.']
        random.shuffle(empty_cells)
        for i, j in empty_cells[:to_fill]:
            board[i][j] = SUDOKU_SOLUTION[i][j]
    elif empty_count > current_empty:
        # Remove some filled cells
        import random
        random.seed(42)
        to_remove = empty_count - current_empty
        filled = [(i,j) for i in range(9) for j in range(9) if board[i][j] != '.']
        random.shuffle(filled)
        for i, j in filled[:to_remove]:
            board[i][j] = '.'
    return board

def sudoku_correct(board, t):
    b = copy.deepcopy(board)
    def solve():
        e = find_empty(b)
        if e is None: t.record(('solved',)); t.record_solution(); return True
        r, c = e; p = poss(b, r, c); t.record(('cell', r, c, len(p)))
        for d in p:
            b[r][c] = d; t.record(('try', r, c, d))
            if solve(): return True
            b[r][c] = '.'; t.record(('backtrack', r, c))
        return False
    solve(); return b

def sudoku_bruteforce(board, t):
    """Brute: try all combos for ALL empty cells (uncapped)."""
    b = copy.deepcopy(board)
    empties = [(i,j) for i in range(9) for j in range(9) if b[i][j]=='.']
    def go(idx):
        if idx == len(empties):
            t.record(('validate',))
            return
        r, c = empties[idx]
        for d in "123456789":
            b[r][c] = d; t.record(('assign', r, c, d, idx))
            go(idx+1)
        b[r][c] = '.'
    go(0); return b


# ═══════════════════════════════════════════════════════════
# EXPERIMENT RUNNER
# ═══════════════════════════════════════════════════════════

def run_solver_at_sizes(solver, problem_key, sizes, n_runs=3, time_limit_s=60):
    """Run solver at each input size, collecting N runs of step counts."""
    all_step_counts = []
    for size in sizes:
        run_counts = []
        for run_idx in range(n_runs):
            t = Trace()
            t0 = time.perf_counter()
            try:
                solver(size, t)
                elapsed = time.perf_counter() - t0
                if elapsed > time_limit_s:
                    print(f"      run {run_idx+1}: TIMEOUT ({elapsed:.1f}s)")
                    run_counts.append(0)
                    continue
                run_counts.append(t.steps)
                print(f"      run {run_idx+1}: steps={t.steps:,}  "
                      f"time={elapsed:.3f}s  sols={t.solutions}")
            except Exception as e:
                print(f"      run {run_idx+1}: ERROR — {e}")
                run_counts.append(0)
        all_step_counts.append(run_counts)
    return all_step_counts


def main():
    all_measurements = {}

    # ═══════════════════════════════════════════════════════
    # N-QUEENS — ≥4 sizes, ≥3 runs
    # ═══════════════════════════════════════════════════════
    print("=" * 90)
    print("N-QUEENS — Formal Scaling Measurement")
    print("  Reference: backtracking_with_pruning (external)")
    print("  Validation: strong (structural)")
    print("=" * 90)

    nq_sizes = [4, 5, 6, 7]  # 4 sizes, geometric-ish progression
    nq_variants = {
        'correct':    nq_correct,
        'partial':    nq_partial,
        'bruteforce': nq_bruteforce,
    }

    nq_measurements = {}
    for variant_name, solver in nq_variants.items():
        print(f"\n  --- {variant_name} ---")
        step_counts = run_solver_at_sizes(solver, "N-Queens", nq_sizes, n_runs=3)

        # Get reference measurement (only for comparison)
        ref_m = nq_measurements.get('correct') if variant_name != 'correct' else None

        m = compute_growth_measurement(
            problem_key="N-Queens",
            variant_name=variant_name,
            sizes=nq_sizes,
            step_counts=step_counts,
            ref_measurement=ref_m,
        )

        nq_measurements[variant_name] = m
        all_measurements[f"N-Queens_{variant_name}"] = m

        md = measurement_to_dict(m)
        print(f"    slope={md['log_log_slope']}  quality={md['slope_quality']}")
        print(f"    absolute_growth={md['absolute_growth']}  "
              f"relative_optimality={md['relative_optimality']}")
        print(f"    validation_strength={md['validation_strength']}  "
              f"measurement_status={md['measurement_status']}")
        if md['slope_ratio'] is not None:
            print(f"    slope_ratio={md['slope_ratio']} (vs {md['reference_type']})")

    # ═══════════════════════════════════════════════════════
    # SUDOKU — Remediation attempt
    # ═══════════════════════════════════════════════════════
    print(f"\n{'='*90}")
    print(f"SUDOKU — Remediation Attempt")
    print(f"  Previous status: invalid_measurement (cap saturation)")
    print(f"  Fix: uncapped brute force + fewer empty cells")
    print(f"  Validation: strong (structural)")
    print(f"{'='*90}")

    # Sizes: varying empty cells — start small to keep brute feasible
    sd_sizes = [20, 30, 40, 51]  # 4 sizes

    # Correct: should work at all sizes
    print(f"\n  --- correct ---")
    sd_correct_counts = []
    for empty_count in sd_sizes:
        board = make_sudoku(empty_count)
        run_counts = []
        for run_idx in range(3):
            t = Trace()
            t0 = time.perf_counter()
            try:
                sudoku_correct(copy.deepcopy(board), t)
                elapsed = time.perf_counter() - t0
                run_counts.append(t.steps)
                print(f"    empty={empty_count}: run {run_idx+1}: steps={t.steps:,}  "
                      f"time={elapsed:.3f}s")
            except Exception as e:
                print(f"    empty={empty_count}: run {run_idx+1}: ERROR — {e}")
                run_counts.append(0)
        sd_correct_counts.append(run_counts)

    # Brute force: only try smallest size to see if it's measurable
    print(f"\n  --- bruteforce (remediation probe) ---")
    sd_brute_counts = []
    probe_sizes = [10, 15, 20, 25]  # start very small
    for empty_count in probe_sizes:
        board = make_sudoku(empty_count)
        run_counts = []
        for run_idx in range(1):  # single run to probe
            t = Trace()
            t0 = time.perf_counter()
            try:
                sudoku_bruteforce(copy.deepcopy(board), t)
                elapsed = time.perf_counter() - t0
                run_counts.append(t.steps)
                print(f"    empty={empty_count}: run 1: steps={t.steps:,}  "
                      f"time={elapsed:.3f}s")
            except Exception as e:
                print(f"    empty={empty_count}: run 1: ERROR — {e}")
                run_counts.append(0)
        sd_brute_counts.append(run_counts)

    # Compute measurement for Sudoku correct
    m_sd_correct = compute_growth_measurement(
        problem_key="Sudoku",
        variant_name="correct",
        sizes=sd_sizes,
        step_counts=sd_correct_counts,
    )
    all_measurements["Sudoku_correct"] = m_sd_correct

    md = measurement_to_dict(m_sd_correct)
    print(f"\n    Sudoku correct: slope={md['log_log_slope']}  "
          f"quality={md['slope_quality']}")
    print(f"    status={md['measurement_status']}  "
          f"absolute_growth={md['absolute_growth']}")

    # Mark Sudoku brute as invalid if saturated
    all_ones = all(
        all(c == sd_brute_counts[0][0] for c in counts)
        for counts in sd_brute_counts if counts
    )
    if all_ones and len(sd_brute_counts) > 1:
        print(f"\n    Sudoku bruteforce: status=invalid_measurement")
        print(f"    reason: cap_saturation (constant steps across sizes)")

    # ═══════════════════════════════════════════════════════
    # FULL REPORT
    # ═══════════════════════════════════════════════════════

    print(f"\n{'='*90}")
    print(f"FULL MEASUREMENT REPORT")
    print(f"{'='*90}")

    print(f"\n  Reference Models:")
    for pk, ref in REFERENCE_MODELS.items():
        print(f"    {pk}: type={ref.reference_type}  source={ref.reference_source}  "
              f"absolute={ref.is_absolute}")

    print(f"\n  Validation Strength Distribution:")
    by_strength = {}
    for pk, vp in VALIDATION_PROFILES.items():
        by_strength.setdefault(vp.strength, []).append(pk)
    for strength, problems in sorted(by_strength.items()):
        print(f"    {strength}: {problems}")

    print(f"\n  Growth Measurements:")
    print(f"  {'Experiment':<25s} | {'Slope':>8s} | {'Quality':<18s} | "
          f"{'Abs Growth':<18s} | {'Rel Opt':<15s} | {'Status':<22s}")
    print(f"  {'-'*25}-+-{'-'*8}-+-{'-'*18}-+-{'-'*18}-+-{'-'*15}-+-{'-'*22}")

    for exp_name, m in all_measurements.items():
        md = measurement_to_dict(m)
        slope_str = f"{md['log_log_slope']:.2f}" if md['log_log_slope'] is not None else "N/A"
        print(f"  {exp_name:<25s} | {slope_str:>8s} | {md['slope_quality']:<18s} | "
              f"{md['absolute_growth']:<18s} | {md['relative_optimality']:<15s} | "
              f"{md['measurement_status']:<22s}")

    # Summary: what's ready, what's not
    valid_count = sum(1 for m in all_measurements.values()
                     if m.measurement_status == "valid")
    invalid_count = sum(1 for m in all_measurements.values()
                       if m.measurement_status == "invalid_measurement")
    strong_count = sum(1 for m in all_measurements.values()
                      if m.validation_strength == "strong")
    has_ref = sum(1 for m in all_measurements.values()
                 if m.slope_ratio is not None)

    print(f"\n  Coverage Summary:")
    print(f"    Valid measurements:     {valid_count}/{len(all_measurements)}")
    print(f"    Invalid measurements:   {invalid_count}/{len(all_measurements)}")
    print(f"    Strong validation:      {strong_count}/{len(all_measurements)}")
    print(f"    Has slope ratio:        {has_ref}/{len(all_measurements)}")
    print(f"    Problems with ≥4 sizes: {len(set(m.problem_key for m in all_measurements.values() if len(m.sizes) >= 4))}")

    # Save
    output = {
        "measurements": {k: measurement_to_dict(v) for k, v in all_measurements.items()},
        "reference_models": {k: {"type": v.reference_type, "source": v.reference_source,
                                  "description": v.description, "is_absolute": v.is_absolute}
                             for k, v in REFERENCE_MODELS.items()},
        "validation_profiles": {k: {"strength": v.strength, "method": v.method,
                                     "can_detect_wrong_output": v.can_detect_wrong_output}
                                for k, v in VALIDATION_PROFILES.items()},
        "coverage": {
            "total_measurements": len(all_measurements),
            "valid": valid_count,
            "invalid": invalid_count,
            "strong_validation": strong_count,
            "has_slope_ratio": has_ref,
        }
    }

    path = r'F:\pythonProject\scratch\s_measurement_v2.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved: {path}")


if __name__ == '__main__':
    main()

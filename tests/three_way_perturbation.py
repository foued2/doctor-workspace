"""
Three-way parallel perturbation displacement analysis.

1. +500 rating on ID=3516
2. difficulty: easy → hard on same ID
3. solved: False → True on same ID

Reports displacement magnitude for each.
"""
import sys, builtins, random, math
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

_print = builtins.print
TOOLS_ROOT = Path(__file__).resolve().parent / "leetcode-tools"
PROJECT_ROOT = TOOLS_ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(TOOLS_ROOT))


def fetch_problems():
    _print("Fetching problems...", flush=True)
    from leetcode_suggestor import fetch_ratings, get_existing_problems, find_unsolved_problems
    ratings = fetch_ratings()
    solved = get_existing_problems()
    unsolved = find_unsolved_problems(ratings, solved)
    return unsolved


def normalize_problem(raw):
    problem_id = raw.get('id')
    raw_rating = raw.get('rating', 0.0)
    rating = max(0.0, min(3000.0, float(raw_rating)))
    return {
        'id': problem_id,
        'rating': rating,
        'difficulty': 'hard' if rating > 15 else ('medium' if rating > 8 else 'easy'),
        'solved': False,
    }


def rank(problems):
    """Return dict {id -> position} sorted by (-score, id)."""
    # score = rating; difficulty and solved are not part of the rank key
    # but we include them in the problem dicts for perturbation testing
    sorted_list = sorted(problems, key=lambda p: (-p['rating'], p['id']))
    return {p['id']: i for i, p in enumerate(sorted_list)}


def atomic_shuffle(problems, rng):
    id_keys = ['id', 'solved', 'history']
    global_keys = ['rating', 'difficulty']
    id_block = [{k: p[k] for k in id_keys if k in p} for p in problems]
    global_block = [{k: p[k] for k in global_keys if k in p} for p in problems]
    rng.shuffle(global_block)
    return [{**id_part, **global_part} for id_part, global_part in zip(id_block, global_block)]


def compute_displacement(ranks_a, ranks_b, all_ids):
    return [ranks_a[pid] - ranks_b[pid] for pid in all_ids]


def w1_distance(a, b):
    sa = sorted(a)
    sb = sorted(b)
    n = min(len(sa), len(sb))
    return sum(abs(sa[i] - sb[i]) for i in range(n)) / n if n else 0.0


def run_null_baseline(problems, all_ids, baseline_ranks, K=100):
    """Generate null displacement distribution from K shuffles."""
    rng = random.Random(42)
    null_displacements = []
    for k in range(K):
        shuffled = atomic_shuffle(problems, rng)
        null_ranks = rank(shuffled)
        disp = compute_displacement(baseline_ranks, null_ranks, all_ids)
        null_displacements.append(disp)
    return null_displacements


def compute_stats(null_displacements, real_displacement, n):
    K = len(null_displacements)
    mean_null_vec = [sum(null_displacements[k][i] for k in range(K)) / K for i in range(n)]
    null_w1s = [w1_distance(nd, mean_null_vec) for nd in null_displacements]
    mean_null_w1 = sum(null_w1s) / K
    std_null_w1 = math.sqrt(sum((w - mean_null_w1) ** 2 for w in null_w1s) / K)
    real_w1 = w1_distance(real_displacement, mean_null_vec)

    # Per-element: max displacement, mean |d|
    abs_disp = [abs(d) for d in real_displacement]
    max_disp = max(abs_disp)
    mean_abs_disp = sum(abs_disp) / n
    nonzero = sum(1 for d in real_displacement if d != 0)

    return {
        'w1': real_w1,
        'null_w1_mean': mean_null_w1,
        'null_w1_std': std_null_w1,
        'z_score': (real_w1 - mean_null_w1) / std_null_w1 if std_null_w1 > 0 else float('inf'),
        'max_displacement': max_disp,
        'mean_abs_displacement': mean_abs_disp,
        'nonzero_positions': nonzero,
    }


def main():
    raw_problems = fetch_problems()
    problems = [normalize_problem(p) for p in raw_problems]
    all_ids = [p['id'] for p in problems]
    n = len(problems)

    # Find index of ID=3516
    target_id = 3516
    target_idx = next(i for i, p in enumerate(problems) if p['id'] == target_id)
    _print(f"Target: ID={target_id} at index {target_idx}, rating={problems[target_idx]['rating']:.1f}, difficulty={problems[target_idx]['difficulty']}", flush=True)

    # Baseline ranks
    baseline_ranks = rank(problems)
    _print("Baseline ranks computed.", flush=True)

    # ── Null baseline (shared) ──
    _print("Generating null baseline (100 shuffles)...", flush=True)
    null_disps = run_null_baseline(problems, all_ids, baseline_ranks, K=100)

    # ── Three perturbations ──
    def apply_perturbation(idx, field, value):
        perturbed = [dict(p) for p in problems]
        perturbed[idx][field] = value
        return perturbed

    perturbations = [
        ("+500 rating",       lambda: apply_perturbation(target_idx, 'rating', problems[target_idx]['rating'] + 500)),
        ("difficulty→hard",   lambda: apply_perturbation(target_idx, 'difficulty', 'hard')),
        ("solved: F→T",       lambda: apply_perturbation(target_idx, 'solved', True)),
    ]

    results = {}
    for label, make_perturbed in perturbations:
        perturbed = make_perturbed()
        perturbed_ranks = rank(perturbed)
        real_disp = compute_displacement(baseline_ranks, perturbed_ranks, all_ids)
        stats = compute_stats(null_disps, real_disp, n)
        results[label] = stats

    # ── Report ──
    _print(f"\n{'='*70}")
    _print(f"THREE-WAY PERTURBATION DISPLACEMENT REPORT")
    _print(f"{'='*70}")
    _print(f"Target: ID={target_id}  |  N={n}  |  Null K=100")
    _print(f"")
    _print(f"{'Perturbation':<25} {'W1':>10} {'Null μ':>10} {'Null σ':>10} {'Z-score':>10} {'Max |d|':>10} {'Nonzero':>10}")
    _print(f"{'-'*70}")

    for label, stats in results.items():
        _print(f"{label:<25} {stats['w1']:>10.2f} {stats['null_w1_mean']:>10.2f} {stats['null_w1_std']:>10.2f} {stats['z_score']:>10.1f} {stats['max_displacement']:>10.0f} {stats['nonzero_positions']:>10}")

    _print(f"\n{'='*70}")

    # Interpretation
    _print(f"Key observations:")
    for label, stats in results.items():
        signal = "SIGNAL" if stats['z_score'] > 2 else "NO SIGNAL"
        _print(f"  {label:<25}: max displacement = {stats['max_displacement']:>5},  {signal} (Z={stats['z_score']:.1f})")

    _print(f"\nNull W1 baseline: μ={results['+500 rating']['null_w1_mean']:.2f}, σ={results['+500 rating']['null_w1_std']:.2f}")
    _print(f"{'='*70}")


if __name__ == '__main__':
    main()

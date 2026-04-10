"""
Blind adversarial benchmark for the doctor system.

This script generates a clean baseline corpus and a harder attack corpus made of
OOD, ambiguous, contradictory, and noisy problem submissions. The doctor only
sees observed evaluation/test artifacts; hidden truth is used strictly after the
fact for scoring.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

TOOLS_ROOT = Path(__file__).resolve().parent / "leetcode-tools"
PROJECT_ROOT = TOOLS_ROOT.parent
REPORT_DIR = PROJECT_ROOT / "reports"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from leetcode_doctor import (  # noqa: E402
    _default_skill_state,
    build_grading_output,
    extract_features,
    update_skill_state,
)


TOPICS = ["dp", "graph", "greedy", "recursion", "string"]

TITLE_PARTS_A = [
    "Retroactive", "Cross-Dock", "Fog-Window", "Triage", "Ledger", "Saltwater",
    "Drift", "Escalation", "Split-Shift", "Cold-Chain", "Proxy", "Fallback",
    "Deferred", "Shadow", "Patchwork", "Quota", "Checkpoint", "Transit",
    "Backfill", "Delayed", "Bilingual", "Reservoir", "Cargo", "Switchyard",
    "Batch", "Staggered", "Audit", "Drone", "Shelter", "Mine-Site",
]
TITLE_PARTS_B = [
    "Manifest", "Voucher", "Roster", "Handoff", "Exception", "Repricing",
    "Queue", "Dispatch", "Ledger", "Detour", "Merge", "Routing", "Seal",
    "Certification", "Recall", "Escrow", "Priority", "Sampling", "Coverage",
    "Throttle", "Repair", "Transfer", "Inspection", "Allocation", "Burndown",
    "Normalization", "Arbitration", "Reconciliation", "Window", "Recovery",
]
TITLE_PARTS_C = [
    "Reconciliation", "Arbitrage", "Repair", "Balancing", "Escalation",
    "Sequencing", "Certification", "Rollback", "Resolution", "Dispatch",
    "Forecasting", "Consolidation", "Recovery", "Approval", "Audit",
    "Compaction", "Matching", "Scheduling", "Triage", "Routing",
]

DOMAINS = [
    "ambulance bay turnover", "reef cargo inspections", "rural bus detours",
    "warehouse aisle closures", "storm-drain pump maintenance",
    "school cafeteria substitutions", "ferry passenger manifests",
    "multi-clinic lab batching", "border customs paperwork",
    "temporary shelter cot assignment", "substation outage routing",
    "night-shift hospital paging", "field sensor recalibration",
    "wastewater incident triage", "harbor tug scheduling",
    "retroactive payroll corrections", "parcel locker overflow handling",
    "regional vaccine transfers", "construction crane slotting",
    "election ballot chain-of-custody", "mineral assay blending",
    "food bank cold-room rotation", "market stall electricity credits",
    "telemetry replay suppression", "irrigation district water turns",
    "snow-route plow reassignment", "fuel depot hose certification",
    "museum climate alarm grouping", "drone battery swap queues",
    "bridge lane closure notifications",
]

AMBIGUITIES = [
    "timestamps may arrive out of order",
    "duplicate IDs can refer to different real entities",
    "manual overrides may be revoked retroactively",
    "missing fields inherit from the previous valid record unless a supervisor note exists",
    "local policy can overrule the global rule but only inside a short time window",
    "two sources disagree on quantity units and the unit tag is sometimes absent",
    "records near midnight may belong to either business day",
    "a correction can invalidate several earlier corrections",
    "partial cancellations are legal only when the backlog exceeds an undocumented threshold",
    "events marked urgent may still be lower priority than legally protected events",
]

MISLEADS = [
    "the raw feed looks sorted, but corrections are inserted later",
    "the entities form a tree until exception links create cycles",
    "all weights are positive except refunds that arrive after settlement",
    "the examples reward local choices even when global fairness matters",
    "a greedy pass works on the samples but breaks when two deadlines tie",
    "string normalization appears sufficient until policy aliases collide",
    "the natural graph model hides that costs depend on the previous action",
    "the task looks like interval merging, but retroactive deletions matter",
    "the obvious DP state explodes because approvals can be rescinded",
    "a BFS view is tempting even though resource limits make the state non-Markovian",
]

OOD_SIGNALS = [
    "operators record voice-note summaries that must override stale sensor values",
    "auditors require an explanation trail, not just the final answer",
    "penalties depend on which department caused the inconsistency",
    "a legal exception changes priority ordering only for protected groups",
    "some records were copied from paper and contain transposed digits",
    "teams care about fairness drift across the whole shift, not one batch",
    "the final output must support replay when regulators inspect the decision",
    "risk is asymmetric: false clearance is worse than false blocking",
]

OBJECTIVES = [
    "produce a corrected action list",
    "rank the next batch of interventions",
    "emit the minimum-risk reconciliation plan",
    "choose which items to defer to the next window",
    "build a canonical ledger with explanations",
    "decide which handoffs should be reversed",
    "group records into legally valid bundles",
    "select a dispatch order that preserves safety guarantees",
]

STRUCTURE_TAGS = {
    "dp": ["rollback", "quota", "budget", "stateful exceptions", "carry-over"],
    "graph": ["dependencies", "handoffs", "cross-links", "reachability", "cycles"],
    "greedy": ["windows", "ranking", "dispatch", "priorities", "sweeps"],
    "recursion": ["nested approvals", "hierarchies", "split records", "drill-down"],
    "string": ["normalization", "aliases", "deduplication", "fuzzy codes", "messy labels"],
}

TRADEOFF_POLICIES = {
    "speed_first": {"runtime": 0.60, "memory": 0.15, "robustness": 0.10, "auditability": 0.10, "simplicity": 0.05},
    "memory_first": {"runtime": 0.25, "memory": 0.50, "robustness": 0.10, "auditability": 0.10, "simplicity": 0.05},
    "audit_first": {"runtime": 0.10, "memory": 0.05, "robustness": 0.30, "auditability": 0.45, "simplicity": 0.10},
    "robustness_first": {"runtime": 0.15, "memory": 0.10, "robustness": 0.50, "auditability": 0.15, "simplicity": 0.10},
    "safety_first": {"runtime": 0.10, "memory": 0.05, "robustness": 0.55, "auditability": 0.20, "simplicity": 0.10},
}

CONTRADICTION_KINDS = [
    "docs_pass_tests_fail",
    "docs_fail_tests_pass",
    "runtime_but_perfect_pass_rate",
    "partial_without_errors",
    "perfect_score_with_empty_test_set",
]

STRATEGY_LIBRARY = [
    {
        "name": "event_sweep_with_repair_log",
        "topic": "greedy",
        "strengths": {"windows", "dispatch", "ranking", "retroactive"},
        "handles": {"timestamps may arrive out of order", "manual overrides may be revoked retroactively"},
        "weaknesses": {"a BFS view is tempting even though resource limits make the state non-Markovian"},
        "runtime": 0.88,
        "memory": 0.72,
        "robustness": 0.70,
        "auditability": 0.76,
        "simplicity": 0.66,
    },
    {
        "name": "memoized_exception_planner",
        "topic": "dp",
        "strengths": {"rollback", "quota", "budget", "stateful exceptions", "carry-over"},
        "handles": {"a correction can invalidate several earlier corrections", "manual overrides may be revoked retroactively"},
        "weaknesses": {"the raw feed looks sorted, but corrections are inserted later"},
        "runtime": 0.74,
        "memory": 0.62,
        "robustness": 0.84,
        "auditability": 0.69,
        "simplicity": 0.52,
    },
    {
        "name": "dependency_graph_resolution",
        "topic": "graph",
        "strengths": {"dependencies", "handoffs", "cross-links", "reachability", "cycles"},
        "handles": {"duplicate IDs can refer to different real entities", "a correction can invalidate several earlier corrections"},
        "weaknesses": {"the examples reward local choices even when global fairness matters"},
        "runtime": 0.78,
        "memory": 0.67,
        "robustness": 0.80,
        "auditability": 0.72,
        "simplicity": 0.58,
    },
    {
        "name": "recursive_casefile_splitter",
        "topic": "recursion",
        "strengths": {"nested approvals", "hierarchies", "split records", "drill-down"},
        "handles": {"local policy can overrule the global rule but only inside a short time window"},
        "weaknesses": {"the task looks like interval merging, but retroactive deletions matter"},
        "runtime": 0.63,
        "memory": 0.61,
        "robustness": 0.71,
        "auditability": 0.83,
        "simplicity": 0.60,
    },
    {
        "name": "fuzzy_key_normalizer",
        "topic": "string",
        "strengths": {"normalization", "aliases", "deduplication", "fuzzy codes", "messy labels"},
        "handles": {"two sources disagree on quantity units and the unit tag is sometimes absent", "some records were copied from paper and contain transposed digits"},
        "weaknesses": {"the natural graph model hides that costs depend on the previous action"},
        "runtime": 0.91,
        "memory": 0.84,
        "robustness": 0.58,
        "auditability": 0.54,
        "simplicity": 0.80,
    },
    {
        "name": "priority_queue_heuristic",
        "topic": "greedy",
        "strengths": {"ranking", "dispatch", "priorities", "windows"},
        "handles": {"events marked urgent may still be lower priority than legally protected events"},
        "weaknesses": {"a greedy pass works on the samples but breaks when two deadlines tie"},
        "runtime": 0.92,
        "memory": 0.77,
        "robustness": 0.49,
        "auditability": 0.43,
        "simplicity": 0.87,
    },
    {
        "name": "constraint_propagation_audit",
        "topic": "graph",
        "strengths": {"dependencies", "cross-links", "stateful exceptions", "reachability"},
        "handles": {"events marked urgent may still be lower priority than legally protected events", "local policy can overrule the global rule but only inside a short time window"},
        "weaknesses": {"the raw feed looks sorted, but corrections are inserted later"},
        "runtime": 0.69,
        "memory": 0.57,
        "robustness": 0.90,
        "auditability": 0.88,
        "simplicity": 0.46,
    },
    {
        "name": "rollback_string_repair",
        "topic": "string",
        "strengths": {"normalization", "rollback", "aliases", "messy labels"},
        "handles": {"records near midnight may belong to either business day", "partial cancellations are legal only when the backlog exceeds an undocumented threshold"},
        "weaknesses": {"the entities form a tree until exception links create cycles"},
        "runtime": 0.71,
        "memory": 0.73,
        "robustness": 0.77,
        "auditability": 0.67,
        "simplicity": 0.63,
    },
]


@dataclass
class ObservedEvidence:
    evaluation_results: Dict[str, Dict[str, Any]]
    test_results: Dict[str, Any]
    file_content: str
    noisy_label: bool
    contradiction_kind: str | None


@dataclass
class Candidate:
    candidate_id: str
    strategy: str
    hidden_topic: str
    hidden_true_correctness: float
    hidden_runtime: float
    hidden_memory: float
    hidden_robustness: float
    hidden_auditability: float
    hidden_simplicity: float
    hidden_rank_utility: float
    observed: ObservedEvidence | None = None


@dataclass
class Problem:
    problem_id: str
    title: str
    domain: str
    prompt: str
    hidden_topic: str
    structural_tags: List[str]
    ambiguities: List[str]
    misleading_pattern: str
    ood_signal: str
    objective: str
    tradeoff_policy: str
    submitted_candidate_id: str
    candidates: List[Candidate]


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def pick_unique_title(rng: random.Random, used_titles: set[str]) -> str:
    while True:
        title = f"{rng.choice(TITLE_PARTS_A)} {rng.choice(TITLE_PARTS_B)} {rng.choice(TITLE_PARTS_C)}"
        if title not in used_titles:
            used_titles.add(title)
            return title


def build_prompt(
    rng: random.Random,
    title: str,
    domain: str,
    ambiguities: Sequence[str],
    misleading_pattern: str,
    ood_signal: str,
    objective: str,
    structural_tags: Sequence[str],
) -> str:
    tag_text = ", ".join(structural_tags[:3])
    lines = [
        f"{title}",
        f"A team handling {domain} receives records in bursts from paper notes, radios, and delayed system syncs.",
        f"The data has hidden structure around {tag_text}, but the operational rules are messy.",
        f"Ambiguities: {ambiguities[0]}; {ambiguities[1]}.",
        f"Misleading pattern: {misleading_pattern}.",
        f"OOD requirement: {ood_signal}.",
        f"Goal: {objective}.",
    ]
    if rng.random() < 0.7:
        lines.append("The answer must remain explainable to a non-technical auditor after a retroactive correction lands.")
    if rng.random() < 0.5:
        lines.append("Two different teams may submit partially overlapping truth, and the safer interpretation is not always the faster one.")
    return "\n".join(lines)


def choose_problem_tags(rng: random.Random, hidden_topic: str, attack: bool) -> Tuple[List[str], List[str]]:
    primary_tags = list(STRUCTURE_TAGS[hidden_topic])
    structural_tags = rng.sample(primary_tags, 3)
    if attack and rng.random() < 0.65:
        foreign_topic = rng.choice([topic for topic in TOPICS if topic != hidden_topic])
        structural_tags.append(rng.choice(STRUCTURE_TAGS[foreign_topic]))
    ambiguities = rng.sample(AMBIGUITIES, 2)
    return structural_tags, ambiguities


def strategy_fit(problem: Dict[str, Any], strategy: Dict[str, Any]) -> int:
    score = 0
    if strategy["topic"] == problem["hidden_topic"]:
        score += 2
    score += sum(1 for tag in problem["structural_tags"] if tag in strategy["strengths"])
    score += sum(1 for item in problem["ambiguities"] if item in strategy["handles"])
    if problem["misleading_pattern"] in strategy["weaknesses"]:
        score -= 2
    if "fairness" in problem["ood_signal"] and strategy["name"] == "priority_queue_heuristic":
        score -= 1
    if "explanation trail" in problem["ood_signal"] and strategy["auditability"] < 0.6:
        score -= 1
    return score


def base_true_correctness(fit_score: int) -> float:
    if fit_score >= 4:
        return 1.0
    if fit_score >= 2:
        return 0.5
    return 0.0


def hidden_rank_utility(policy: str, candidate: Dict[str, float]) -> float:
    weights = TRADEOFF_POLICIES[policy]
    utility = candidate["hidden_true_correctness"] * 100.0
    utility += weights["runtime"] * candidate["hidden_runtime"] * 10.0
    utility += weights["memory"] * candidate["hidden_memory"] * 10.0
    utility += weights["robustness"] * candidate["hidden_robustness"] * 10.0
    utility += weights["auditability"] * candidate["hidden_auditability"] * 10.0
    utility += weights["simplicity"] * candidate["hidden_simplicity"] * 10.0
    return round(utility, 4)


def make_candidate(
    rng: random.Random,
    problem: Dict[str, Any],
    strategy: Dict[str, Any],
    index: int,
    attack: bool,
) -> Candidate:
    fit = strategy_fit(problem, strategy)
    correctness = base_true_correctness(fit)
    scale_penalty = 0.05 if attack else 0.02
    runtime = clamp(strategy["runtime"] - scale_penalty * max(0, 3 - fit) + rng.uniform(-0.05, 0.05))
    memory = clamp(strategy["memory"] - scale_penalty * max(0, 2 - fit) + rng.uniform(-0.05, 0.05))
    robustness = clamp(strategy["robustness"] + 0.05 * sum(1 for item in problem["ambiguities"] if item in strategy["handles"]) + rng.uniform(-0.04, 0.04))
    auditability = clamp(strategy["auditability"] + (0.08 if "explanation trail" in problem["ood_signal"] else 0.0) + rng.uniform(-0.04, 0.04))
    simplicity = clamp(strategy["simplicity"] + rng.uniform(-0.04, 0.04))
    candidate_payload = {
        "hidden_true_correctness": correctness,
        "hidden_runtime": runtime,
        "hidden_memory": memory,
        "hidden_robustness": robustness,
        "hidden_auditability": auditability,
        "hidden_simplicity": simplicity,
    }
    utility = hidden_rank_utility(problem["tradeoff_policy"], candidate_payload)
    return Candidate(
        candidate_id=f"{problem['problem_id']}-cand-{index}",
        strategy=strategy["name"],
        hidden_topic=strategy["topic"],
        hidden_true_correctness=correctness,
        hidden_runtime=round(runtime, 4),
        hidden_memory=round(memory, 4),
        hidden_robustness=round(robustness, 4),
        hidden_auditability=round(auditability, 4),
        hidden_simplicity=round(simplicity, 4),
        hidden_rank_utility=utility,
    )


def ensure_strategy_collision(rng: random.Random, problem: Problem) -> None:
    valid = [cand for cand in problem.candidates if cand.hidden_true_correctness >= 1.0]
    if len(valid) >= 2:
        return
    ordered = sorted(problem.candidates, key=lambda c: c.hidden_rank_utility, reverse=True)
    ordered[0].hidden_true_correctness = 1.0
    ordered[0].hidden_rank_utility = hidden_rank_utility(problem.tradeoff_policy, asdict(ordered[0]))
    if len(ordered) > 1 and rng.random() < 0.8:
        ordered[1].hidden_true_correctness = 1.0
        if problem.tradeoff_policy in {"audit_first", "robustness_first", "safety_first"}:
            ordered[1].hidden_auditability = clamp(ordered[1].hidden_auditability + 0.12)
            ordered[1].hidden_robustness = clamp(ordered[1].hidden_robustness + 0.10)
            ordered[1].hidden_runtime = clamp(ordered[1].hidden_runtime - 0.08)
        else:
            ordered[1].hidden_runtime = clamp(ordered[1].hidden_runtime + 0.08)
            ordered[1].hidden_memory = clamp(ordered[1].hidden_memory + 0.05)
        ordered[1].hidden_rank_utility = hidden_rank_utility(problem.tradeoff_policy, asdict(ordered[1]))


def correctness_to_observed(correctness: float, noisy: bool, rng: random.Random) -> float:
    if not noisy:
        return correctness
    if correctness == 1.0:
        return rng.choice([0.0, 0.5])
    if correctness == 0.0:
        return rng.choice([0.5, 1.0])
    return rng.choice([0.0, 1.0])


def make_file_content(problem: Problem, candidate: Candidate, attack: bool, rng: random.Random) -> str:
    strategy = next(item for item in STRATEGY_LIBRARY if item["name"] == candidate.strategy)
    topic_keywords = {
        "dp": "dynamic memoization subproblem rollback budget",
        "graph": "graph bfs dfs node edge dependency traversal",
        "greedy": "greedy heap priority sweep window sort",
        "recursion": "recursive recursion base case split drill-down backtrack",
        "string": "string substring pattern alias normalize char regex",
    }
    primary = topic_keywords[strategy["topic"]]
    if attack:
        foreign = rng.choice([topic_keywords[topic] for topic in TOPICS if topic != strategy["topic"]])
        keyword_block = f"{primary} {foreign}" if rng.random() < 0.8 else primary
    else:
        keyword_block = primary
    loop_lines = ["for record in records:", "    pass"] * rng.randint(1, 2 if attack else 1)
    if attack and rng.random() < 0.55:
        loop_lines.extend(["while pending:", "    break"])
    return "\n".join(
        [
            '"""',
            problem.prompt,
            f"Candidate strategy: {candidate.strategy}",
            f"Keyword hints: {keyword_block}",
            '"""',
            *loop_lines,
        ]
    )


def make_observed_evidence(
    problem: Problem,
    candidate: Candidate,
    attack: bool,
    noisy_label: bool,
    contradiction_kind: str | None,
    rng: random.Random,
) -> ObservedEvidence:
    observed_correctness = correctness_to_observed(candidate.hidden_true_correctness, noisy_label, rng)
    if observed_correctness == 1.0:
        docs = [9.3, 9.1, 9.0]
        solution_grade = 10.0
        pass_rate = 1.0
        errors: List[str] = []
    elif observed_correctness == 0.5:
        docs = [8.4, 7.1, 7.0]
        solution_grade = 6.0
        pass_rate = 0.58
        errors = ["AssertionError: hidden edge case failed"]
    else:
        docs = [4.8, 5.2, 4.6]
        solution_grade = 0.0
        pass_rate = 0.1
        errors = ["AssertionError: expected canonical output mismatch"]

    total_tests = 18 if attack else 12
    if contradiction_kind == "docs_pass_tests_fail":
        docs = [9.6, 9.2, 9.1]
        solution_grade = 6.0
        pass_rate = 0.22
        errors = ["AssertionError: reconciliation failed on regulator replay"]
    elif contradiction_kind == "docs_fail_tests_pass":
        docs = [5.0, 5.5, 5.2]
        solution_grade = 10.0
        pass_rate = 1.0
        errors = []
    elif contradiction_kind == "runtime_but_perfect_pass_rate":
        docs = [9.1, 9.0, 9.4]
        solution_grade = 10.0
        pass_rate = 1.0
        errors = ["TypeError: fallback comparator received None"]
    elif contradiction_kind == "partial_without_errors":
        docs = [9.0, 8.8, 8.9]
        solution_grade = 6.0
        pass_rate = 0.61
        errors = []
    elif contradiction_kind == "perfect_score_with_empty_test_set":
        docs = [9.2, 9.0, 9.1]
        solution_grade = 10.0
        pass_rate = 1.0
        total_tests = 0
        errors = []

    evaluation_results = {
        "problem_statement": {"grade": docs[0], "status": "PASS" if docs[0] >= 8.0 else "FAIL"},
        "approach": {"grade": docs[1], "status": "PASS" if docs[1] >= 8.0 else "FAIL"},
        "complexity": {"grade": docs[2], "status": "PASS" if docs[2] >= 8.0 else "FAIL"},
        "solution": {"grade": solution_grade, "status": "PASS" if solution_grade >= 10.0 else "FAIL"},
    }
    test_results = {
        "pass_rate": pass_rate,
        "total": total_tests,
        "errors": errors,
    }
    file_content = make_file_content(problem, candidate, attack, rng)
    return ObservedEvidence(
        evaluation_results=evaluation_results,
        test_results=test_results,
        file_content=file_content,
        noisy_label=noisy_label,
        contradiction_kind=contradiction_kind,
    )


def generate_problem(rng: random.Random, index: int, attack: bool, used_titles: set[str]) -> Problem:
    hidden_topic = rng.choice(TOPICS)
    structural_tags, ambiguities = choose_problem_tags(rng, hidden_topic, attack)
    title = pick_unique_title(rng, used_titles)
    domain = rng.choice(DOMAINS)
    misleading_pattern = rng.choice(MISLEADS) if attack else rng.choice(MISLEADS[:4])
    ood_signal = rng.choice(OOD_SIGNALS) if attack else "operators only need a consistent final answer"
    tradeoff_policy = rng.choice(list(TRADEOFF_POLICIES)) if attack else rng.choice(["speed_first", "memory_first"])
    objective = rng.choice(OBJECTIVES)
    prompt = build_prompt(rng, title, domain, ambiguities, misleading_pattern, ood_signal, objective, structural_tags)

    strategy_count = 3 if attack and rng.random() < 0.4 else 2
    picked_strategies = rng.sample(STRATEGY_LIBRARY, strategy_count)

    raw_problem = {
        "problem_id": f"{'ATK' if attack else 'BASE'}-{index:04d}",
        "hidden_topic": hidden_topic,
        "structural_tags": structural_tags,
        "ambiguities": ambiguities,
        "misleading_pattern": misleading_pattern,
        "ood_signal": ood_signal,
        "tradeoff_policy": tradeoff_policy,
    }
    candidates = [make_candidate(rng, raw_problem, strategy, idx + 1, attack) for idx, strategy in enumerate(picked_strategies)]
    problem = Problem(
        problem_id=raw_problem["problem_id"],
        title=title,
        domain=domain,
        prompt=prompt,
        hidden_topic=hidden_topic,
        structural_tags=structural_tags,
        ambiguities=ambiguities,
        misleading_pattern=misleading_pattern,
        ood_signal=ood_signal,
        objective=objective,
        tradeoff_policy=tradeoff_policy,
        submitted_candidate_id="",
        candidates=candidates,
    )
    if attack and rng.random() < 0.75:
        ensure_strategy_collision(rng, problem)
    elif not any(cand.hidden_true_correctness >= 1.0 for cand in problem.candidates):
        best = max(problem.candidates, key=lambda c: c.hidden_rank_utility)
        best.hidden_true_correctness = 1.0
        best.hidden_rank_utility = hidden_rank_utility(problem.tradeoff_policy, asdict(best))

    problem.submitted_candidate_id = rng.choice(problem.candidates).candidate_id
    return problem


def assign_observations(problems: List[Problem], attack: bool, noise_rate: float, rng: random.Random) -> None:
    count = len(problems)
    noisy_ids: set[str] = set()
    contradiction_map: Dict[str, str] = {}
    if attack:
        noise_count = round(count * noise_rate)
        contradiction_count = round(count * 0.30)
        noisy_ids = {problem.problem_id for problem in rng.sample(problems, noise_count)}
        contradiction_targets = rng.sample(problems, contradiction_count)
        contradiction_map = {
            problem.problem_id: rng.choice(CONTRADICTION_KINDS)
            for problem in contradiction_targets
        }

    for problem in problems:
        for candidate in problem.candidates:
            noisy_label = attack and candidate.candidate_id == problem.submitted_candidate_id and problem.problem_id in noisy_ids
            contradiction_kind = None
            if attack and candidate.candidate_id == problem.submitted_candidate_id:
                contradiction_kind = contradiction_map.get(problem.problem_id)
            candidate.observed = make_observed_evidence(problem, candidate, attack, noisy_label, contradiction_kind, rng)


def expected_detection(features: Dict[str, Any]) -> bool:
    return features["error_type"] != "none" or features["correctness"] == 0.5


def classification_metrics(samples: Sequence[Dict[str, Any]]) -> Dict[str, float]:
    tp = fp = tn = fn = 0
    for sample in samples:
        truth = sample["actual"] >= 0.8
        pred = sample["predicted"] >= 0.8
        if truth and pred:
            tp += 1
        elif truth and not pred:
            fn += 1
        elif not truth and pred:
            fp += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    accuracy = (tp + tn) / len(samples) if samples else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }


def calibration_metrics(samples: Sequence[Dict[str, Any]], bucket_count: int = 5) -> Dict[str, Any]:
    if not samples:
        return {"mae": 0.0, "brier": 0.0, "ece": 0.0, "bins": []}
    mae = statistics.fmean(abs(sample["predicted"] - sample["actual"]) for sample in samples)
    brier = statistics.fmean((sample["predicted"] - sample["actual"]) ** 2 for sample in samples)
    bins = []
    ece = 0.0
    for bucket_idx in range(bucket_count):
        low = bucket_idx / bucket_count
        high = (bucket_idx + 1) / bucket_count
        bucket = [
            sample
            for sample in samples
            if sample["predicted"] >= low
            and (sample["predicted"] < high or (bucket_idx == bucket_count - 1 and sample["predicted"] <= high))
        ]
        if bucket:
            avg_pred = statistics.fmean(sample["predicted"] for sample in bucket)
            avg_actual = statistics.fmean(sample["actual"] for sample in bucket)
            gap = abs(avg_pred - avg_actual)
            ece += gap * (len(bucket) / len(samples))
            bins.append(
                {
                    "low": round(low, 2),
                    "high": round(high, 2),
                    "count": len(bucket),
                    "avg_pred": round(avg_pred, 4),
                    "avg_actual": round(avg_actual, 4),
                    "gap": round(gap, 4),
                }
            )
        else:
            bins.append({"low": round(low, 2), "high": round(high, 2), "count": 0, "avg_pred": 0.0, "avg_actual": 0.0, "gap": 0.0})
    return {
        "mae": round(mae, 4),
        "brier": round(brier, 4),
        "ece": round(ece, 4),
        "bins": bins,
    }


def evaluate_sequence(problems: List[Problem], attack: bool) -> Dict[str, Any]:
    state = _default_skill_state()
    samples = []
    order = problems[:]
    random.shuffle(order)
    for problem in order:
        submitted = next(c for c in problem.candidates if c.candidate_id == problem.submitted_candidate_id)
        observed = submitted.observed
        assert observed is not None
        features = extract_features(observed.evaluation_results, observed.test_results, observed.file_content)
        state = update_skill_state(state, features)
        output = build_grading_output(state, features, {})
        contradiction_case = bool(observed.noisy_label or observed.contradiction_kind)
        detected = expected_detection(features) if contradiction_case else False
        uncertainty_flag = features["correctness"] == 0.5
        samples.append(
            {
                "problem_id": problem.problem_id,
                "predicted": output["correctness"],
                "actual": submitted.hidden_true_correctness,
                "attack": attack,
                "noisy_label": observed.noisy_label,
                "contradiction_kind": observed.contradiction_kind,
                "contradiction_case": contradiction_case,
                "detected": detected,
                "uncertainty_flag": uncertainty_flag,
                "silent_failure": contradiction_case and not detected,
                "true_topic": problem.hidden_topic,
                "predicted_topic": features["topic"],
                "efficiency_score": output["efficiency_score"],
                "error_type": features["error_type"],
            }
        )

    class_metrics = classification_metrics(samples)
    calib_metrics = calibration_metrics(samples)
    contradiction_cases = [sample for sample in samples if sample["contradiction_case"]]
    contradiction_detection = (
        sum(1 for sample in contradiction_cases if sample["detected"]) / len(contradiction_cases)
        if contradiction_cases
        else 0.0
    )
    uncertainty_rate = (
        sum(1 for sample in contradiction_cases if sample["uncertainty_flag"]) / len(contradiction_cases)
        if contradiction_cases
        else 0.0
    )
    silent_rate = (
        sum(1 for sample in contradiction_cases if sample["silent_failure"]) / len(contradiction_cases)
        if contradiction_cases
        else 0.0
    )
    topic_match = statistics.fmean(1.0 if sample["true_topic"] == sample["predicted_topic"] else 0.0 for sample in samples)

    return {
        "count": len(samples),
        "classification": class_metrics,
        "calibration": calib_metrics,
        "contradiction_cases": len(contradiction_cases),
        "contradiction_detection_rate": round(contradiction_detection, 4),
        "uncertainty_flag_rate": round(uncertainty_rate, 4),
        "silent_failure_rate": round(silent_rate, 4),
        "topic_match_rate": round(topic_match, 4),
        "final_state": state,
        "samples": samples,
    }


def doctor_rank_key(candidate: Candidate) -> Tuple[float, float]:
    assert candidate.observed is not None
    features = extract_features(
        candidate.observed.evaluation_results,
        candidate.observed.test_results,
        candidate.observed.file_content,
    )
    local_state = update_skill_state(_default_skill_state(), features)
    output = build_grading_output(local_state, features, {})
    return (output["correctness"], output["efficiency_score"])


def ranking_metrics(problems: Sequence[Problem]) -> Dict[str, Any]:
    evaluated = []
    top1_correct = 0
    total = 0
    pairwise_total = 0
    pairwise_correct = 0
    for problem in problems:
        if len(problem.candidates) < 2:
            continue
        hidden_best = max(problem.candidates, key=lambda cand: (cand.hidden_rank_utility, cand.hidden_true_correctness))
        doctor_best = max(problem.candidates, key=doctor_rank_key)
        total += 1
        if doctor_best.candidate_id == hidden_best.candidate_id:
            top1_correct += 1

        for i in range(len(problem.candidates)):
            for j in range(i + 1, len(problem.candidates)):
                left = problem.candidates[i]
                right = problem.candidates[j]
                hidden_delta = left.hidden_rank_utility - right.hidden_rank_utility
                if abs(hidden_delta) < 1e-9:
                    continue
                doctor_delta = 1 if doctor_rank_key(left) > doctor_rank_key(right) else -1
                hidden_sign = 1 if hidden_delta > 0 else -1
                pairwise_total += 1
                if doctor_delta == hidden_sign:
                    pairwise_correct += 1

        evaluated.append(
            {
                "problem_id": problem.problem_id,
                "hidden_best": hidden_best.candidate_id,
                "doctor_best": doctor_best.candidate_id,
                "policy": problem.tradeoff_policy,
                "candidate_count": len(problem.candidates),
            }
        )

    return {
        "collision_problem_count": total,
        "top1_accuracy": round(top1_correct / total, 4) if total else 0.0,
        "pairwise_accuracy": round(pairwise_correct / pairwise_total, 4) if pairwise_total else 0.0,
        "details": evaluated,
    }


def summarize_dataset(problems: Sequence[Problem]) -> Dict[str, Any]:
    noisy = 0
    contradictions = 0
    multi_valid = 0
    for problem in problems:
        submitted = next(c for c in problem.candidates if c.candidate_id == problem.submitted_candidate_id)
        if submitted.observed and submitted.observed.noisy_label:
            noisy += 1
        if submitted.observed and submitted.observed.contradiction_kind:
            contradictions += 1
        if sum(1 for cand in problem.candidates if cand.hidden_true_correctness >= 1.0) >= 2:
            multi_valid += 1
    return {
        "problem_count": len(problems),
        "noisy_submission_count": noisy,
        "contradiction_submission_count": contradictions,
        "multi_valid_problem_count": multi_valid,
    }


def checkpoint_verdict(baseline: Dict[str, Any], attack: Dict[str, Any], ranking: Dict[str, Any]) -> str:
    collapse_checks = [
        attack["classification"]["accuracy"] < 0.85,
        (baseline["classification"]["accuracy"] - attack["classification"]["accuracy"]) > 0.10,
        attack["calibration"]["ece"] > 0.20,
        (attack["calibration"]["ece"] - baseline["calibration"]["ece"]) > 0.08,
        attack["contradiction_detection_rate"] < 0.50,
        attack["silent_failure_rate"] > 0.40,
        ranking["top1_accuracy"] < 0.70,
    ]
    return "metrics collapse" if sum(1 for item in collapse_checks if item) >= 2 else "metrics remain high"


def corpus_to_jsonable(problems: Sequence[Problem]) -> List[Dict[str, Any]]:
    return [asdict(problem) for problem in problems]


def build_corpus(
    rng: random.Random,
    count: int,
    attack: bool,
    noise_rate: float,
    used_titles: set[str],
) -> List[Problem]:
    problems = [generate_problem(rng, idx + 1, attack, used_titles) for idx in range(count)]
    assign_observations(problems, attack, noise_rate, rng)
    return problems


def run_benchmark(baseline_count: int, attack_count: int, noise_rate: float, seed: int) -> Dict[str, Any]:
    rng = random.Random(seed)
    used_titles: set[str] = set()

    baseline_problems = build_corpus(rng, baseline_count, False, 0.0, used_titles)
    attack_problems = build_corpus(rng, attack_count, True, noise_rate, used_titles)

    baseline_eval = evaluate_sequence(baseline_problems, attack=False)
    attack_eval = evaluate_sequence(attack_problems, attack=True)
    baseline_ranking = ranking_metrics(baseline_problems)
    attack_ranking = ranking_metrics(attack_problems)

    verdict = checkpoint_verdict(baseline_eval, attack_eval, attack_ranking)
    summary = {
        "generated_at": datetime.now().isoformat(),
        "seed": seed,
        "noise_rate": noise_rate,
        "baseline_dataset": summarize_dataset(baseline_problems),
        "attack_dataset": summarize_dataset(attack_problems),
        "baseline": {
            "classification": baseline_eval["classification"],
            "calibration": baseline_eval["calibration"],
            "contradiction_detection_rate": baseline_eval["contradiction_detection_rate"],
            "uncertainty_flag_rate": baseline_eval["uncertainty_flag_rate"],
            "silent_failure_rate": baseline_eval["silent_failure_rate"],
            "topic_match_rate": baseline_eval["topic_match_rate"],
            "ranking": {
                "top1_accuracy": baseline_ranking["top1_accuracy"],
                "pairwise_accuracy": baseline_ranking["pairwise_accuracy"],
                "collision_problem_count": baseline_ranking["collision_problem_count"],
            },
        },
        "attack": {
            "classification": attack_eval["classification"],
            "calibration": attack_eval["calibration"],
            "contradiction_detection_rate": attack_eval["contradiction_detection_rate"],
            "uncertainty_flag_rate": attack_eval["uncertainty_flag_rate"],
            "silent_failure_rate": attack_eval["silent_failure_rate"],
            "topic_match_rate": attack_eval["topic_match_rate"],
            "ranking": {
                "top1_accuracy": attack_ranking["top1_accuracy"],
                "pairwise_accuracy": attack_ranking["pairwise_accuracy"],
                "collision_problem_count": attack_ranking["collision_problem_count"],
            },
        },
        "delta": {
            "accuracy_drop": round(baseline_eval["classification"]["accuracy"] - attack_eval["classification"]["accuracy"], 4),
            "f1_drop": round(baseline_eval["classification"]["f1"] - attack_eval["classification"]["f1"], 4),
            "ece_increase": round(attack_eval["calibration"]["ece"] - baseline_eval["calibration"]["ece"], 4),
            "mae_increase": round(attack_eval["calibration"]["mae"] - baseline_eval["calibration"]["mae"], 4),
            "ranking_top1_drop": round(baseline_ranking["top1_accuracy"] - attack_ranking["top1_accuracy"], 4),
            "ranking_pairwise_drop": round(baseline_ranking["pairwise_accuracy"] - attack_ranking["pairwise_accuracy"], 4),
        },
        "outcome": {
            "performance_drop": attack_eval["classification"]["accuracy"] < baseline_eval["classification"]["accuracy"],
            "calibration_degrade": attack_eval["calibration"]["ece"] > baseline_eval["calibration"]["ece"],
            "doctor_detects_contradictions": attack_eval["contradiction_detection_rate"] > 0.0,
            "fails_silently": attack_eval["silent_failure_rate"] > 0.0,
            "flags_uncertainty": attack_eval["uncertainty_flag_rate"] > 0.0,
            "checkpoint": verdict,
        },
        "artifacts": {
            "baseline_problems": corpus_to_jsonable(baseline_problems),
            "attack_problems": corpus_to_jsonable(attack_problems),
        },
    }
    return summary


def print_outcome(summary: Dict[str, Any], report_path: Path) -> None:
    baseline = summary["baseline"]
    attack = summary["attack"]
    delta = summary["delta"]
    outcome = summary["outcome"]
    print("DOCTOR ATTACK OUTCOME")
    print(f"report={report_path}")
    print(f"baseline_accuracy={baseline['classification']['accuracy']:.4f}")
    print(f"attack_accuracy={attack['classification']['accuracy']:.4f}")
    print(f"accuracy_drop={delta['accuracy_drop']:.4f}")
    print(f"baseline_f1={baseline['classification']['f1']:.4f}")
    print(f"attack_f1={attack['classification']['f1']:.4f}")
    print(f"f1_drop={delta['f1_drop']:.4f}")
    print(f"baseline_ece={baseline['calibration']['ece']:.4f}")
    print(f"attack_ece={attack['calibration']['ece']:.4f}")
    print(f"ece_increase={delta['ece_increase']:.4f}")
    print(f"attack_contradiction_detection_rate={attack['contradiction_detection_rate']:.4f}")
    print(f"attack_uncertainty_flag_rate={attack['uncertainty_flag_rate']:.4f}")
    print(f"attack_silent_failure_rate={attack['silent_failure_rate']:.4f}")
    print(f"baseline_ranking_top1={baseline['ranking']['top1_accuracy']:.4f}")
    print(f"attack_ranking_top1={attack['ranking']['top1_accuracy']:.4f}")
    print(f"ranking_top1_drop={delta['ranking_top1_drop']:.4f}")
    print(f"baseline_ranking_pairwise={baseline['ranking']['pairwise_accuracy']:.4f}")
    print(f"attack_ranking_pairwise={attack['ranking']['pairwise_accuracy']:.4f}")
    print(f"ranking_pairwise_drop={delta['ranking_pairwise_drop']:.4f}")
    print(f"checkpoint={outcome['checkpoint']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Blind adversarial benchmark for the doctor system.")
    parser.add_argument("--baseline", type=int, default=120, help="Number of clean baseline problems.")
    parser.add_argument("--attack", type=int, default=240, help="Number of attack problems.")
    parser.add_argument("--noise-rate", type=float, default=0.15, help="Label noise rate for attack submissions.")
    parser.add_argument("--seed", type=int, default=20260405, help="Random seed.")
    args = parser.parse_args()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    summary = run_benchmark(args.baseline, args.attack, args.noise_rate, args.seed)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORT_DIR / f"doctor_attack_benchmark_{stamp}.json"
    report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print_outcome(summary, report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

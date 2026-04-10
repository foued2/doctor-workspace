from __future__ import annotations

import random
from typing import Dict, List

DEFAULT_SEEDS = [
    20260405,
    20260406,
    20260407,
    20260408,
    20260409,
    20260410,
    20260411,
]

STRATUM_PROPORTIONS = {
    "A": 0.2,
    "B": 0.2,
    "C": 0.2,
    "D": 0.2,
    "E": 0.2,
}

DOMAINS = [
    "ambulance dispatch",
    "port inspection",
    "food bank cold-chain",
    "ferry handoff",
    "clinic lab batching",
    "payroll backfill",
    "drone battery swap",
    "storm pump routing",
    "shelter intake",
]

IRRELEVANT_DETAILS = [
    "the office printer failed twice",
    "someone mentioned a yellow clipboard",
    "the east gate coffee machine is broken",
    "a manager prefers blue labels",
    "the lunch roster was emailed late",
]

REDUNDANT_DETAILS = [
    "records may be repeated in summaries",
    "some notes restate the same event twice",
    "radio transcripts include corrections after the fact",
    "operators narrate irrelevant context",
]


def _allocate_counts(total: int, proportions: Dict[str, float]) -> Dict[str, int]:
    counts = {key: int(total * value) for key, value in proportions.items()}
    assigned = sum(counts.values())
    keys = list(proportions)
    index = 0
    while assigned < total:
        counts[keys[index % len(keys)]] += 1
        assigned += 1
        index += 1
    return counts


def _allocate_truths(stratum: str, count: int) -> List[str]:
    if stratum == "A":
        mix = {"correct": 0.2, "partial": 0.2, "undefined": 0.6}
    elif stratum == "B":
        mix = {"correct": 0.2, "partial": 0.4, "undefined": 0.4}
    elif stratum == "C":
        mix = {"correct": 0.6, "partial": 0.4, "undefined": 0.0}
    elif stratum == "D":
        mix = {"correct": 0.6, "partial": 0.4, "undefined": 0.0}
    else:
        mix = {"correct": 0.7, "partial": 0.3, "undefined": 0.0}
    truth_counts = _allocate_counts(count, mix)
    return [truth for truth, amount in truth_counts.items() for _ in range(amount)]


def _problem_rule(stratum: str) -> str:
    if stratum == "A":
        return "The policy omits tie-breaking, leaves the state space incomplete, and never states whether retroactive edits replace or append."
    if stratum == "B":
        return "The rules require both minimizing delay and never reordering arrivals, even when the examples violate that."
    if stratum == "C":
        return "A sample output was copied incorrectly from a handwritten note, and operators continue to cite it as authoritative."
    if stratum == "D":
        return "Multiple outputs are valid if they satisfy safety and fairness, but the scoring objective is non-equivalent across teams."
    return "The description mixes relevant records with logs, habits, legacy notes, and operational gossip."


def _response_text(truth: str, stratum: str) -> str:
    if truth == "correct":
        response = "Proposed response preserves legal priority, reconciles late corrections, and keeps an audit trail."
        if stratum == "D":
            response += " It explicitly acknowledges multiple valid frontiers and justifies the selected tradeoff."
        return response
    if truth == "partial":
        response = "Proposed response handles the common path but leaves one exception route unresolved."
        if stratum == "D":
            response += " It picks one frontier without proving why competing valid frontiers are inferior."
        return response
    return "Proposed response commits to a single answer even though the prompt leaves the target underdefined or mutually inconsistent."


def _appearance_text(signal_inversion: bool, truth: str) -> str:
    if signal_inversion and truth == "correct":
        return "Presentation quality: rough notes, duplicated wording, missing bullets, and uneven formatting."
    if signal_inversion:
        return "Presentation quality: polished structure, confident wording, and carefully formatted bullet points."
    return "Presentation quality: ordinary working notes with no strong polish signal."


def _sample_block(corrupted: bool, stratum: str) -> str:
    if corrupted:
        return "Sample label from memo conflicts with the prose and appears to preserve the wrong expected output."
    if stratum == "D":
        return "Examples show more than one valid ordering as long as safety and fairness constraints are preserved."
    return "Examples are internally consistent with the prose."


def _build_prompt(
    rng: random.Random,
    case_id: str,
    stratum: str,
    truth: str,
    signal_inversion: bool,
    corrupted: bool,
) -> str:
    domain = rng.choice(DOMAINS)
    lines = [
        f"CASE {case_id}",
        f"Domain: {domain}.",
        _problem_rule(stratum),
        f"Extra detail: {rng.choice(IRRELEVANT_DETAILS)}.",
        f"Redundant note: {rng.choice(REDUNDANT_DETAILS)}.",
        _sample_block(corrupted, stratum),
        _appearance_text(signal_inversion, truth),
    ]
    if stratum in {"B", "C"}:
        lines.append("A supervisor note explicitly says an example disagrees with the written rule.")
    if truth == "undefined":
        lines.append("A missing or incompatible constraint prevents a single decidable target.")
    lines.append(f"PROPOSED RESPONSE: {_response_text(truth, stratum)}")
    return " ".join(lines)


def _make_public_case(case_id: str, prompt: str) -> Dict[str, str]:
    return {"case_id": case_id, "prompt": prompt}


def _make_private_case(
    case_id: str,
    stratum: str,
    truth: str,
    contradiction: bool,
    corrupted: bool,
    signal_inversion: bool,
) -> Dict[str, object]:
    return {
        "case_id": case_id,
        "stratum": stratum,
        "ground_truth": truth,
        "contradiction": contradiction,
        "corrupted_label": corrupted,
        "signal_inversion": signal_inversion,
    }


def _build_clean_batch(size: int, rng: random.Random) -> Dict[str, object]:
    truths = ["correct"] * int(size * 0.7) + ["partial"] * (size - int(size * 0.7))
    rng.shuffle(truths)
    public_cases = []
    private_key = {}
    for index, truth in enumerate(truths, 1):
        case_id = f"BASE-{index:04d}"
        prompt = " ".join(
            [
                f"CASE {case_id}",
                f"Domain: {rng.choice(DOMAINS)}.",
                "Rules are complete, consistent, and examples are correct.",
                f"Extra detail: {rng.choice(IRRELEVANT_DETAILS)}.",
                "Examples are internally consistent with the prose.",
                "Presentation quality: ordinary working notes with no strong polish signal.",
                f"PROPOSED RESPONSE: {_response_text(truth, 'E')}",
            ]
        )
        public_cases.append(_make_public_case(case_id, prompt))
        private_key[case_id] = _make_private_case(
            case_id=case_id,
            stratum="clean",
            truth=truth,
            contradiction=False,
            corrupted=False,
            signal_inversion=False,
        )
    rng.shuffle(public_cases)
    return {
        "public_cases": public_cases,
        "private_key": private_key,
        "summary": {"count": size},
    }


def _build_attack_batch(size: int, rng: random.Random) -> Dict[str, object]:
    counts = _allocate_counts(size, STRATUM_PROPORTIONS)
    all_case_ids = [f"ATK-{index:04d}" for index in range(1, size + 1)]
    corruption_rate = rng.uniform(0.10, 0.30)
    corrupted_ids = set(rng.sample(all_case_ids, round(size * corruption_rate)))

    public_cases = []
    private_key = {}
    index = 1
    for stratum, count in counts.items():
        truths = _allocate_truths(stratum, count)
        rng.shuffle(truths)
        for truth in truths:
            case_id = f"ATK-{index:04d}"
            signal_inversion = truth == "correct" and rng.random() < 0.45
            if not signal_inversion and truth != "correct":
                signal_inversion = rng.random() < 0.35
            corrupted = case_id in corrupted_ids
            contradiction = stratum in {"A", "B", "C"} or truth == "undefined"
            prompt = _build_prompt(
                rng=rng,
                case_id=case_id,
                stratum=stratum,
                truth=truth,
                signal_inversion=signal_inversion,
                corrupted=corrupted,
            )
            public_cases.append(_make_public_case(case_id, prompt))
            private_key[case_id] = _make_private_case(
                case_id=case_id,
                stratum=stratum,
                truth=truth,
                contradiction=contradiction,
                corrupted=corrupted,
                signal_inversion=signal_inversion,
            )
            index += 1

    rng.shuffle(public_cases)
    undefined_share = sum(1 for item in private_key.values() if item["ground_truth"] == "undefined") / size
    corrupted_share = sum(1 for item in private_key.values() if item["corrupted_label"]) / size
    inversion_share = sum(1 for item in private_key.values() if item["signal_inversion"]) / size
    return {
        "public_cases": public_cases,
        "private_key": private_key,
        "summary": {
            "count": size,
            "strata": counts,
            "fixed_proportions_respected": all(abs((counts[key] / size) - value) < 0.02 for key, value in STRATUM_PROPORTIONS.items()),
            "undefined_share": round(undefined_share, 4),
            "corrupted_share": round(corrupted_share, 4),
            "signal_inversion_share": round(inversion_share, 4),
        },
    }


def build_experiment(seed: int, baseline_size: int, attack_size: int) -> Dict[str, object]:
    rng = random.Random(seed)
    baseline = _build_clean_batch(baseline_size, rng)
    attack = _build_attack_batch(attack_size, rng)
    return {
        "seed": seed,
        "baseline": baseline,
        "attack": attack,
    }

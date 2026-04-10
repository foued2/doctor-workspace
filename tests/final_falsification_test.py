"""
Adversarial Holdout Falsification Test.

Black-box protocol:
- input to doctor: prompt only
- observed output: final label only

No internal flags, traces, evaluator logic, or dataset-generator logic are used.
Metrics are frozen in this module before any evaluation run starts.
"""

from __future__ import annotations

import json
import random
import statistics
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from doctor import RawPromptDoctor

ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "reports"
SEEDS = [20260405, 20260406, 20260407, 20260408, 20260409, 20260410, 20260411]

LAYERS = ["A", "B", "C"]
DIFFICULTY_LEVELS = [1, 2, 3]
CASE_KINDS = ["winner", "compromise", "undecidable"]
GENERATORS = ["incident_report", "ops_sheet"]

CONFLICT_TYPES = [
    "priority_conflicts",
    "mutual_exclusion",
    "temporal_ordering",
    "role_conflicts",
    "semantic_ambiguity",
]

DOMAINS = [
    "after-hours clinic dispatch",
    "cold-chain warehouse intake",
    "harbor manifest control",
    "shelter bed assignment",
    "blood bank routing desk",
    "field repair permit queue",
]

SOFT_PRESSURES = [
    "management still wants the shortest total queue time",
    "finance still wants the cheapest workable board",
    "operations still wants the fewest handoff steps",
]

NOISE_NOTES = [
    "A legacy note about printer paper shortages is still attached to the packet.",
    "A retired supervisor left an outdated habit note in the margin.",
    "The handoff bundle still includes a stale anecdote from last quarter.",
]

EXTRA_CONSTRAINTS = [
    "A separate logbook still has to mirror the final status word for word.",
    "Any overnight carryover must be copied into the fallback register before release.",
    "If a substitute clerk touched the case, the archive sheet must be updated before handoff.",
]

NESTED_NOTES = {
    1: "",
    2: "If the backup lane is used, the same rule still applies after the carryover note is copied.",
    3: "If the backup lane is used and the carryover note came from a substitute shift, the same rule still applies unless the archive copy is missing.",
}

DEPENDENCY_NOTES = {
    1: "",
    2: "The final handoff depends on whether the carryover flag was logged first.",
    3: "The final handoff depends on the carryover flag, which depends on the intake stamp, which depends on the prior-shift ledger entry.",
}


@dataclass(frozen=True)
class FamilySpec:
    family_id: str
    generator: str
    domain: str
    conflict_type: str
    case_kind: str
    density: int
    nesting_depth: int
    dependency_depth: int
    resolvable: bool
    stronger_priority: str | None
    weaker_priority: str | None
    candidate_mode: str
    hard_constraint_should_hold: bool | None
    primary_rule: str
    secondary_rule: str
    tertiary_rule: str
    candidate_text: str
    soft_pressure: str
    noise_note: str
    extra_constraints: List[str]
    nested_note: str
    dependency_note: str


@dataclass(frozen=True)
class Variant:
    family_id: str
    generator: str
    layer: str
    surface_id: int
    prompt: str


@dataclass
class FamilyResult:
    family_id: str
    generator: str
    conflict_type: str
    case_kind: str
    density: int
    nesting_depth: int
    dependency_depth: int
    resolvable: bool
    hard_constraint_should_hold: bool | None
    oracle_label: str
    outputs_by_layer: Dict[str, List[str]]


def _mean(values: List[float]) -> float:
    return round(statistics.fmean(values), 4) if values else 0.0


def _summary_stats(values: List[float]) -> Dict[str, float]:
    return {
        "mean": round(statistics.fmean(values), 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
    }


def _pick(rng: random.Random, items: List[str]) -> str:
    return rng.choice(items)


def _case_material(conflict_type: str, domain: str) -> Dict[str, str]:
    if conflict_type == "priority_conflicts":
        return {
            "primary_rule": f"In {domain}, red-band cases must stay ahead of plain cases.",
            "secondary_rule": "A planning note still pushes the board that clears total waiting time fastest.",
            "tertiary_rule": "A second signed instruction says nobody may ever move ahead of raw arrival order, even red-band cases.",
            "winner_candidate": "The proposed answer keeps every red-band case ahead of plain work and accepts the slower board.",
            "compromise_candidate": "The proposed answer moves one red-band case backward to trim queue time and calls that balanced.",
            "undecidable_candidate": "The proposed answer picks one signed rule and dispatches as if the packet did not contain a clash.",
            "stronger_priority": "explicit_hard_constraint",
            "weaker_priority": "soft_optimization_goal",
        }
    if conflict_type == "mutual_exclusion":
        return {
            "primary_rule": f"In {domain}, sterile totes must remain sealed once intake scans them.",
            "secondary_rule": "The generic release checklist still says every scanned tote must be opened before handoff.",
            "tertiary_rule": "The packet gives no override and still claims the seal rule and opening step are both mandatory for the same tote.",
            "winner_candidate": "The proposed answer leaves sterile totes sealed and uses the manual exception ledger for release.",
            "compromise_candidate": "The proposed answer cracks each sterile tote open for a moment, then reseals it to satisfy both sides halfway.",
            "undecidable_candidate": "The proposed answer follows the opening step and ignores that the seal rule was never reconciled.",
            "stronger_priority": "specific_exception_rule",
            "weaker_priority": "general_release_checklist",
        }
    if conflict_type == "temporal_ordering":
        return {
            "primary_rule": f"In {domain}, chain-hold items must keep collection timestamp order.",
            "secondary_rule": "A throughput note still says the latest correction should jump to the front to cut reruns.",
            "tertiary_rule": "A second signed step says every late correction outranks older chain-hold items without exception.",
            "winner_candidate": "The proposed answer preserves collection order for every chain-hold item and accepts the slower recovery path.",
            "compromise_candidate": "The proposed answer moves one late correction ahead of older chain-hold items to save time.",
            "undecidable_candidate": "The proposed answer fronts the correction slip and treats the ordering clash as if it were already resolved.",
            "stronger_priority": "chain_of_custody_order",
            "weaker_priority": "rerun_reduction_goal",
        }
    if conflict_type == "role_conflicts":
        return {
            "primary_rule": f"In {domain}, nobody may approve a request they personally filed.",
            "secondary_rule": "The night supervisor is still told to approve every after-hours request on that shift.",
            "tertiary_rule": "The same packet names no alternate approver and still forbids delaying approval past handoff.",
            "winner_candidate": "The proposed answer refuses self-approval and routes the request to the alternate duty desk.",
            "compromise_candidate": "The proposed answer lets the supervisor self-approve this one request to keep the shift moving.",
            "undecidable_candidate": "The proposed answer self-approves and treats the identity clash as a paperwork detail.",
            "stronger_priority": "identity_separation_rule",
            "weaker_priority": "general_shift_duty",
        }
    return {
        "primary_rule": f"In {domain}, the glossary defines 'rush' as regulated loads only.",
        "secondary_rule": "A planner shorthand still uses 'rush' for anything leaving within four hours.",
        "tertiary_rule": "The packet uses 'rush' both ways and never names a controlling glossary entry.",
        "winner_candidate": "The proposed answer follows the glossary meaning and ignores the looser planner shorthand.",
        "compromise_candidate": "The proposed answer mixes both meanings and marks some loads rush by payment and others by departure time.",
        "undecidable_candidate": "The proposed answer picks one meaning and schedules the board as if the term were settled.",
        "stronger_priority": "explicit_glossary_definition",
        "weaker_priority": "local_shorthand",
    }


def _oracle_label(spec: FamilySpec) -> str:
    if not spec.resolvable:
        return "undefined"
    if spec.candidate_mode == "select_stronger_constraint":
        return "correct"
    return "partial"


def _build_family_spec(
    rng: random.Random,
    family_id: str,
    generator: str,
    conflict_type: str,
    case_kind: str,
    difficulty: int,
    domain: str,
) -> FamilySpec:
    material = _case_material(conflict_type, domain)
    resolvable = case_kind != "undecidable"

    if case_kind == "winner":
        candidate_mode = "select_stronger_constraint"
        candidate_text = material["winner_candidate"]
        hard_constraint_should_hold = True
    elif case_kind == "compromise":
        candidate_mode = "average_or_select_weaker_constraint"
        candidate_text = material["compromise_candidate"]
        hard_constraint_should_hold = False
    else:
        candidate_mode = "invent_tie_break_for_unresolved_conflict"
        candidate_text = material["undecidable_candidate"]
        hard_constraint_should_hold = None

    extra_constraints = []
    for _ in range(max(0, difficulty - 1)):
        extra_constraints.append(_pick(rng, EXTRA_CONSTRAINTS))

    stronger_priority = material["stronger_priority"] if resolvable else None
    weaker_priority = material["weaker_priority"] if resolvable else None
    if case_kind == "undecidable" and conflict_type == "semantic_ambiguity":
        stronger_priority = None
        weaker_priority = None

    return FamilySpec(
        family_id=family_id,
        generator=generator,
        domain=domain,
        conflict_type=conflict_type,
        case_kind=case_kind,
        density=difficulty,
        nesting_depth=difficulty,
        dependency_depth=difficulty,
        resolvable=resolvable,
        stronger_priority=stronger_priority,
        weaker_priority=weaker_priority,
        candidate_mode=candidate_mode,
        hard_constraint_should_hold=hard_constraint_should_hold,
        primary_rule=material["primary_rule"],
        secondary_rule=material["secondary_rule"],
        tertiary_rule=material["tertiary_rule"],
        candidate_text=candidate_text,
        soft_pressure=_pick(rng, SOFT_PRESSURES),
        noise_note=_pick(rng, NOISE_NOTES),
        extra_constraints=extra_constraints,
        nested_note=NESTED_NOTES[difficulty],
        dependency_note=DEPENDENCY_NOTES[difficulty],
    )


def _rule_block(spec: FamilySpec, layer: str) -> List[str]:
    if spec.case_kind == "undecidable":
        conflict_pair = [spec.primary_rule, spec.tertiary_rule]
    else:
        conflict_pair = [spec.primary_rule, spec.secondary_rule]

    if layer == "A":
        return conflict_pair
    if layer == "B":
        return [
            f"A worked example quietly assumes this: {conflict_pair[0]}",
            f"A later footer pulls the other way: {conflict_pair[1]}",
        ]
    return [
        conflict_pair[0],
        conflict_pair[1],
        spec.soft_pressure.capitalize() + ".",
    ]


def _escalation_block(spec: FamilySpec) -> List[str]:
    notes: List[str] = []
    notes.extend(spec.extra_constraints)
    if spec.nested_note:
        notes.append(spec.nested_note)
    if spec.dependency_note:
        notes.append(spec.dependency_note)
    notes.append(spec.noise_note)
    return notes


def _render_incident_report(spec: FamilySpec, layer: str, surface_id: int) -> str:
    opening = f"Incident brief for {spec.domain}:"
    blocks = _rule_block(spec, layer)
    escalation = _escalation_block(spec) if layer == "C" else _escalation_block(spec)[: spec.density]
    if surface_id == 1:
        sentences = [opening]
        sentences.extend(blocks)
        sentences.extend(escalation)
        sentences.append(f"Candidate reply: {spec.candidate_text}")
    else:
        sentences = [f"Shift summary for {spec.domain}:"]
        sentences.extend(escalation)
        sentences.extend(blocks)
        sentences.append(f"Proposed handling: {spec.candidate_text}")
    return " ".join(sentences)


def _render_ops_sheet(spec: FamilySpec, layer: str, surface_id: int) -> str:
    rule_lines = _rule_block(spec, layer)
    escalation = _escalation_block(spec) if layer == "C" else _escalation_block(spec)[: spec.density]
    head = "SHEET" if surface_id == 1 else "CARD"
    entry = "ENTRY" if surface_id == 1 else "FIELD"
    note_prefix = "NOTE" if surface_id == 1 else "AUX"
    candidate = "CANDIDATE" if surface_id == 1 else "PROPOSED"
    cells = [
        f"{head}={spec.domain}",
        f"{entry}1={rule_lines[0]}",
    ]
    if len(rule_lines) > 1:
        cells.append(f"{entry}2={rule_lines[1]}")
    if len(rule_lines) > 2:
        cells.append(f"{entry}3={rule_lines[2]}")
    for index, item in enumerate(escalation, start=1):
        cells.append(f"{note_prefix}{index}={item}")
    cells.append(f"{candidate}={spec.candidate_text}")
    return " | ".join(cells)


def _render_prompt(spec: FamilySpec, layer: str, surface_id: int) -> str:
    if spec.generator == "incident_report":
        return _render_incident_report(spec, layer, surface_id)
    return _render_ops_sheet(spec, layer, surface_id)


def build_holdout(seed: int) -> Dict[str, object]:
    rng = random.Random(seed)
    variants: List[Variant] = []
    families: Dict[str, FamilySpec] = {}
    domains = DOMAINS[:]
    rng.shuffle(domains)
    family_index = 1

    for generator in GENERATORS:
        for conflict_type in CONFLICT_TYPES:
            for difficulty in DIFFICULTY_LEVELS:
                for case_kind in CASE_KINDS:
                    for domain in domains[:2]:
                        family_id = f"{generator[:2].upper()}-{conflict_type[:3].upper()}-{family_index:03d}"
                        spec = _build_family_spec(
                            rng=rng,
                            family_id=family_id,
                            generator=generator,
                            conflict_type=conflict_type,
                            case_kind=case_kind,
                            difficulty=difficulty,
                            domain=domain,
                        )
                        families[family_id] = spec
                        for layer in LAYERS:
                            for surface_id in (1, 2):
                                variants.append(
                                    Variant(
                                        family_id=family_id,
                                        generator=generator,
                                        layer=layer,
                                        surface_id=surface_id,
                                        prompt=_render_prompt(spec, layer, surface_id),
                                    )
                                )
                        family_index += 1

    rng.shuffle(variants)
    return {"variants": variants, "families": families}


def _majority_label(outputs: List[str]) -> str:
    counts = Counter(outputs)
    label, _ = max(sorted(counts.items()), key=lambda item: item[1])
    return label


def _flatten_outputs(family: FamilyResult) -> List[str]:
    outputs: List[str] = []
    for layer in LAYERS:
        outputs.extend(family.outputs_by_layer[layer])
    return outputs


def _mean_bool(values: List[bool]) -> float:
    return _mean([1.0 if value else 0.0 for value in values])


def _group_accuracy(families: List[FamilyResult], key: str) -> Dict[str, float]:
    grouped: Dict[str, List[bool]] = {}
    for family in families:
        group_key = str(getattr(family, key))
        grouped.setdefault(group_key, []).append(_majority_label(_flatten_outputs(family)) == family.oracle_label)
    return {name: _mean_bool(values) for name, values in sorted(grouped.items())}


def _group_constraint_satisfaction(families: List[FamilyResult], key: str) -> Dict[str, float]:
    grouped: Dict[str, List[bool]] = {}
    for family in families:
        if family.hard_constraint_should_hold is None:
            continue
        predicted_holds = _majority_label(_flatten_outputs(family)) == "correct"
        group_key = str(getattr(family, key))
        grouped.setdefault(group_key, []).append(predicted_holds == family.hard_constraint_should_hold)
    return {name: _mean_bool(values) for name, values in sorted(grouped.items())}


def run_seed(seed: int) -> Dict[str, object]:
    doctor = RawPromptDoctor()
    holdout = build_holdout(seed)
    variants: List[Variant] = holdout["variants"]
    family_specs: Dict[str, FamilySpec] = holdout["families"]
    grouped: Dict[str, FamilyResult] = {}

    for variant in variants:
        label = doctor.predict(variant.prompt)["label"]
        spec = family_specs[variant.family_id]
        if variant.family_id not in grouped:
            grouped[variant.family_id] = FamilyResult(
                family_id=variant.family_id,
                generator=spec.generator,
                conflict_type=spec.conflict_type,
                case_kind=spec.case_kind,
                density=spec.density,
                nesting_depth=spec.nesting_depth,
                dependency_depth=spec.dependency_depth,
                resolvable=spec.resolvable,
                hard_constraint_should_hold=spec.hard_constraint_should_hold,
                oracle_label=_oracle_label(spec),
                outputs_by_layer={layer: [] for layer in LAYERS},
            )
        grouped[variant.family_id].outputs_by_layer[variant.layer].append(label)

    families = list(grouped.values())

    def consistent(family: FamilyResult) -> bool:
        return len(set(_flatten_outputs(family))) == 1

    def layer_consistent(family: FamilyResult, layer: str) -> bool:
        return len(set(family.outputs_by_layer[layer])) == 1

    def oracle_match(family: FamilyResult) -> bool:
        return _majority_label(_flatten_outputs(family)) == family.oracle_label

    def satisfies_constraint(family: FamilyResult) -> bool:
        if family.hard_constraint_should_hold is None:
            return False
        predicted_holds = _majority_label(_flatten_outputs(family)) == "correct"
        return predicted_holds == family.hard_constraint_should_hold

    checkable = [family for family in families if family.hard_constraint_should_hold is not None]

    conflict_arbitration_by_type = _group_accuracy(families, "conflict_type")
    constraint_satisfaction_by_type = _group_constraint_satisfaction(families, "conflict_type")
    oracle_divergence_by_type = {
        name: round(1.0 - accuracy, 4) for name, accuracy in conflict_arbitration_by_type.items()
    }

    metrics = {
        "behavioral_invariance": _mean_bool([consistent(family) for family in families]),
        "behavioral_invariance_paraphrase": _mean_bool([layer_consistent(family, "A") for family in families]),
        "behavioral_invariance_hidden": _mean_bool([layer_consistent(family, "B") for family in families]),
        "behavioral_invariance_collision": _mean_bool([layer_consistent(family, "C") for family in families]),
        "constraint_satisfaction": _mean_bool([satisfies_constraint(family) for family in checkable]),
        "conflict_arbitration_macro": _mean_bool([oracle_match(family) for family in families]),
        "oracle_divergence": _mean([1.0 - (1.0 if oracle_match(family) else 0.0) for family in families]),
        "conflict_arbitration_accuracy_by_type": conflict_arbitration_by_type,
        "constraint_satisfaction_by_type": constraint_satisfaction_by_type,
        "oracle_divergence_by_type": oracle_divergence_by_type,
        "arbitration_accuracy_by_density": _group_accuracy(families, "density"),
        "arbitration_accuracy_by_nesting_depth": _group_accuracy(families, "nesting_depth"),
        "arbitration_accuracy_by_dependency_depth": _group_accuracy(families, "dependency_depth"),
        "oracle_divergence_by_generator": {
            name: round(1.0 - accuracy, 4)
            for name, accuracy in _group_accuracy(families, "generator").items()
        },
    }

    family_rows = []
    for family in families:
        family_rows.append(
            {
                "family_id": family.family_id,
                "generator": family.generator,
                "conflict_type": family.conflict_type,
                "case_kind": family.case_kind,
                "density": family.density,
                "nesting_depth": family.nesting_depth,
                "dependency_depth": family.dependency_depth,
                "oracle_label": family.oracle_label,
                "majority_label": _majority_label(_flatten_outputs(family)),
                "outputs_by_layer": family.outputs_by_layer,
            }
        )

    return {
        "seed": seed,
        "metrics": metrics,
        "families": family_rows,
    }


def aggregate(runs: List[Dict[str, object]]) -> Dict[str, object]:
    scalar_metrics = [
        "behavioral_invariance",
        "behavioral_invariance_paraphrase",
        "behavioral_invariance_hidden",
        "behavioral_invariance_collision",
        "constraint_satisfaction",
        "conflict_arbitration_macro",
        "oracle_divergence",
    ]
    vector_metrics = [
        "conflict_arbitration_accuracy_by_type",
        "constraint_satisfaction_by_type",
        "oracle_divergence_by_type",
        "arbitration_accuracy_by_density",
        "arbitration_accuracy_by_nesting_depth",
        "arbitration_accuracy_by_dependency_depth",
        "oracle_divergence_by_generator",
    ]

    summary: Dict[str, object] = {}
    for name in scalar_metrics:
        summary[name] = _summary_stats([run["metrics"][name] for run in runs])

    for name in vector_metrics:
        keys = sorted(runs[0]["metrics"][name].keys())
        summary[name] = {
            key: _summary_stats([run["metrics"][name][key] for run in runs]) for key in keys
        }

    robust = (
        summary["behavioral_invariance_paraphrase"]["mean"] >= 0.85
        and summary["behavioral_invariance_hidden"]["mean"] >= 0.85
        and summary["conflict_arbitration_macro"]["mean"] >= 0.85
        and summary["constraint_satisfaction"]["mean"] >= 0.85
        and summary["oracle_divergence"]["mean"] <= 0.15
        and all(
            payload["mean"] >= 0.85
            for payload in summary["conflict_arbitration_accuracy_by_type"].values()
        )
    )
    return {"summary": summary, "robust": robust}


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    runs = [run_seed(seed) for seed in SEEDS]
    result = {
        "generated_at": datetime.now().isoformat(),
        "seed_count": len(SEEDS),
        "seeds": SEEDS,
        "metric_frozen_before_evaluation": True,
        "protocol": {
            "doctor_input": "prompt only",
            "doctor_output_used": "final label only",
            "internal_flags_used": False,
            "generator_shared_with_training_benchmark": False,
            "oracle_baseline": "deterministic_decision_tree",
            "contradiction_taxonomy": CONFLICT_TYPES,
        },
        "runs": runs,
        "aggregate": aggregate(runs),
    }
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORT_DIR / f"final_falsification_test_{stamp}.json"
    report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    summary = result["aggregate"]["summary"]
    print("ADVERSARIAL HOLDOUT FALSIFICATION TEST")
    print(f"report={report_path}")
    print("doctor_input=prompt_only")
    print("doctor_output_used=final_label_only")
    print("internal_flags_used=false")
    print("generator_shared_with_training_benchmark=false")
    print(f"behavioral_invariance_mean={summary['behavioral_invariance']['mean']:.4f}")
    print(f"behavioral_invariance_paraphrase_mean={summary['behavioral_invariance_paraphrase']['mean']:.4f}")
    print(f"behavioral_invariance_hidden_mean={summary['behavioral_invariance_hidden']['mean']:.4f}")
    print(f"behavioral_invariance_collision_mean={summary['behavioral_invariance_collision']['mean']:.4f}")
    print(f"constraint_satisfaction_mean={summary['constraint_satisfaction']['mean']:.4f}")
    print(f"conflict_arbitration_macro_mean={summary['conflict_arbitration_macro']['mean']:.4f}")
    print(f"oracle_divergence_mean={summary['oracle_divergence']['mean']:.4f}")
    for conflict_type, payload in summary["conflict_arbitration_accuracy_by_type"].items():
        print(f"conflict_arbitration_accuracy_{conflict_type}_mean={payload['mean']:.4f}")
    for level, payload in summary["arbitration_accuracy_by_density"].items():
        print(f"arbitration_accuracy_density_{level}_mean={payload['mean']:.4f}")
    print(f"robust={result['aggregate']['robust']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

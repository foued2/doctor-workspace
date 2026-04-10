"""
Adaptive Generator — Stage 2
=============================
Transforms the static dataset generator into a memory-driven adversary
that hunts Doctor weaknesses.

Evolution chain:
  Stage 1: static adversary (build_experiment) ← exists
  Stage 2: memory-driven adversary (AdaptiveGenerator) ← this file
  Stage 3: co-evolving adversary (future)

Usage:
    from dataset_generator.adaptive_generator import AdaptiveGenerator
    gen = AdaptiveGenerator(seed=42)
    cases = gen.generate_batch(n=20)
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dataset_generator.generator import (
    DOMAINS,
    IRRELEVANT_DETAILS,
    REDUNDANT_DETAILS,
    _allocate_counts,
    _allocate_truths,
    _build_prompt,
    _make_public_case,
    _make_private_case,
    _response_text,
    _appearance_text,
    _sample_block,
    _problem_rule,
)
from dataset_generator.failure_capture import (
    MEMORY_ROOT,
    compute_stratum_weights,
    load_patterns,
    save_patterns,
    register_failure_pattern,
    check_novelty,
    weakness_report,
)


# ===========================================================================
# PHASE 3 — Rule-Specific Escalation Templates
# ===========================================================================

RULE_ESCALATION_TEMPLATES = {
    # ── L1: Single Rule Attacks ──────────────────────────────────────────
    "R1": {
        "description": "Contradiction blindness attack",
        "technique": "Inject contradictory premises, present them as consistent",
        "metadata": {
            "has_contradiction": True,
            "has_corrupted_label": False,
            "is_ambiguous": False,
        },
        "prompt_additions": [
            "Rule A states the opposite of Rule B, but both are presented as equally valid.",
            "Two conflicting guidelines are cited with no priority order specified.",
            "The example contradicts the written rule, yet no clarification is provided.",
        ],
    },
    "R2": {
        "description": "Corruption trust attack",
        "technique": "Inject corrupted/inverted label, make it look authoritative",
        "metadata": {
            "has_contradiction": False,
            "has_corrupted_label": True,
            "is_ambiguous": False,
        },
        "prompt_additions": [
            "A sample output is provided that appears authoritative but is actually inverted.",
            "The expected label comes from a corrupted dataset with known errors.",
            "An authoritative-looking example demonstrates the wrong classification.",
        ],
    },
    "R3": {
        "description": "False confidence attack",
        "technique": "Make prompt genuinely ambiguous, strip all explicit undefined markers",
        "metadata": {
            "has_contradiction": False,
            "has_corrupted_label": False,
            "is_ambiguous": True,
        },
        "prompt_additions": [
            "The specification lacks clear tie-breaking criteria for edge cases.",
            "Multiple valid interpretations exist with no mechanism to choose between them.",
            "Critical constraints are left unspecified, making a definitive decision impossible.",
        ],
    },

    # ── L2: Dual Rule Attacks ────────────────────────────────────────────
    "R1+R2": {
        "description": "Contradiction + Corruption attack",
        "technique": "Contradiction embedded in corrupted evidence",
        "metadata": {
            "has_contradiction": True,
            "has_corrupted_label": True,
            "is_ambiguous": False,
        },
        "prompt_additions": [
            "Two conflicting memos each contain corrupted sample labels endorsing opposite conclusions.",
            "Contradictory rules are supported by equally authoritative but incompatible evidence.",
        ],
    },
    "R2+R3": {
        "description": "Corruption + False confidence attack",
        "technique": "Corrupted label on an already ambiguous prompt",
        "metadata": {
            "has_contradiction": False,
            "has_corrupted_label": True,
            "is_ambiguous": True,
        },
        "prompt_additions": [
            "An ambiguous specification is paired with a corrupted example that appears to resolve the ambiguity.",
            "The prompt is genuinely undefined, but a misleading sample suggests a false definitive answer.",
        ],
    },
    "R1+R3": {
        "description": "Contradiction + False confidence attack",
        "technique": "Contradictory premises that also hide ambiguity",
        "metadata": {
            "has_contradiction": True,
            "has_corrupted_label": False,
            "is_ambiguous": True,
        },
        "prompt_additions": [
            "Contradictory rules obscure the fact that the underlying objective itself is undefined.",
            "The conflict between two guidelines hides a deeper ambiguity in the specification.",
        ],
    },

    # ── L3: Full Stack Attack ────────────────────────────────────────────
    "R1+R2+R3": {
        "description": "Full stack — all three rules simultaneously",
        "technique": "Maximum pressure, all traps active",
        "metadata": {
            "has_contradiction": True,
            "has_corrupted_label": True,
            "is_ambiguous": True,
        },
        "prompt_additions": [
            "Contradictory rules, corrupted evidence, and an inherently ambiguous specification — all at once.",
            "The prompt presents conflicting guidelines supported by unreliable examples about an undefined objective.",
        ],
    },
}

# Rule escalation levels
ESCALATION_LEVELS = {
    "L1": ["R1", "R2", "R3"],
    "L2": ["R1+R2", "R2+R3", "R1+R3"],
    "L3": ["R1+R2+R3"],
}


# ── Escalation Templates ─────────────────────────────────────────────────────

ESCALATION_RULES = {
    # Increase ambiguity: remove constraints, add vagueness
    "increase_ambiguity": {
        "remove_constraints": True,
        "add_vague_language": True,
    },
    # Strengthen deception: polish formatting, increase confidence tone
    "strengthen_deception": {
        "boost_formatting": True,
        "increase_narrative_coherence": True,
    },
    # Deepen corruption: multiple conflicting examples
    "deepen_corruption": {
        "add_conflicting_examples": True,
        "mix_signals": True,
    },
    # Cross-trap composition: combine multiple trap types
    "cross_trap_composition": {
        "combine_contradiction_corruption": True,
        "add_signal_inversion": True,
    },
}


class AdaptiveGenerator:
    """Memory-driven adversarial case generator.

    Learns from Doctor failures and amplifies patterns that cause them.
    """

    def __init__(self, seed: int = 42, alpha: float = 2.0):
        self.rng = random.Random(seed)
        self.alpha = alpha
        self.stratum_weights = compute_stratum_weights(alpha=alpha)
        self.patterns = load_patterns()
        self._escalation_counts: Dict[str, int] = {}
        
        # PHASE 3: Rule-specific tracking
        self.rule_target_distribution: Dict[str, int] = {}

    def generate_rule_targeted_batch(
        self,
        n_per_rule: int = 10,
        escalation_level: str = "L1",
    ) -> Dict[str, Any]:
        """Generate cases targeting specific rule violations.
        
        PHASE 3: New method for rule-specific adversarial generation.
        
        Args:
            n_per_rule: Number of cases to generate per rule target
            escalation_level: "L1" (single rule), "L2" (dual), "L3" (full stack)
        
        Returns:
            Dict with public_cases, private_key, and summary
        """
        # Get rule targets for this escalation level
        rule_targets = ESCALATION_LEVELS.get(escalation_level, ["R1", "R2", "R3"])
        
        public_cases = []
        private_key = {}
        case_id_counter = 1
        
        for rule_target in rule_targets:
            template = RULE_ESCALATION_TEMPLATES[rule_target]
            
            for i in range(n_per_rule):
                case_id = f"RULE-{rule_target.replace('+', 'x')}-{case_id_counter:04d}"
                
                # Generate case with rule-specific metadata
                case = self._build_rule_targeted_case(
                    case_id=case_id,
                    rule_target=rule_target,
                    template=template,
                )
                
                if case:
                    public_cases.append(case["public"])
                    private_key[case["public"]["case_id"]] = case["private"]
                    case_id_counter += 1
        
        self.rng.shuffle(public_cases)
        
        # Update rule target distribution tracking
        for rule_target in rule_targets:
            self.rule_target_distribution[rule_target] = n_per_rule
        
        undefined_share = sum(
            1 for v in private_key.values() if v["ground_truth"] == "undefined"
        ) / max(len(private_key), 1)
        
        return {
            "public_cases": public_cases,
            "private_key": private_key,
            "summary": {
                "count": len(public_cases),
                "escalation_level": escalation_level,
                "rule_targets": rule_targets,
                "n_per_rule": n_per_rule,
                "undefined_share": round(undefined_share, 4),
            },
        }
    
    def _build_rule_targeted_case(
        self,
        case_id: str,
        rule_target: str,
        template: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Build a case targeting a specific rule violation.
        
        PHASE 3: Creates cases with explicit metadata flags for rule detectors.
        """
        metadata = template["metadata"]
        has_contradiction = metadata["has_contradiction"]
        has_corrupted_label = metadata["has_corrupted_label"]
        is_ambiguous = metadata["is_ambiguous"]
        
        # Determine ground truth based on rule target
        if "R3" in rule_target:
            truth = "undefined"  # R3 targets false confidence on undefined cases
        elif "R1" in rule_target:
            truth = self.rng.choice(["partial", "correct"])  # Contradiction cases
        else:
            truth = self.rng.choice(["partial", "correct"])  # Corruption cases
        
        stratum = self.rng.choice(["A", "B", "C"])  # Rule-targeted cases use harder strata
        domain = self.rng.choice(DOMAINS)
        
        # Build prompt with rule-specific content
        lines = [
            f"CASE {case_id}",
            f"Domain: {domain}.",
            _problem_rule(stratum),
        ]
        
        # Add rule-specific contradiction content
        if has_contradiction:
            contradiction_texts = [
                "Rule A requires outcome X, but Rule B requires the opposite outcome Y.",
                "Two conflicting guidelines are cited with no priority order specified.",
                "The example output contradicts the written rule, yet no clarification is provided.",
                "A supervisor note endorses an interpretation that conflicts with the base specification.",
            ]
            lines.append(self.rng.choice(contradiction_texts))
        
        # Add corrupted label content
        if has_corrupted_label:
            corruption_texts = [
                "Sample output from the authoritative reference dataset: label='correct'.",
                "The expected answer, per the official guidelines, is a definitive 'correct' classification.",
                "A verified example demonstrates the correct classification pattern.",
            ]
            lines.append(self.rng.choice(corruption_texts))
        
        # Add ambiguous/undefined content
        if is_ambiguous:
            ambiguity_texts = [
                "The specification lacks clear tie-breaking criteria for edge cases.",
                "Multiple valid interpretations exist with no mechanism to choose between them.",
                "Critical constraints are left unspecified, making a definitive decision impossible.",
                "No single decidable target exists given the available information.",
            ]
            lines.append(self.rng.choice(ambiguity_texts))
        
        # Add standard details
        lines.append(f"Extra detail: {self.rng.choice(IRRELEVANT_DETAILS)}.")
        lines.append(f"Redundant note: {self.rng.choice(REDUNDANT_DETAILS)}.")
        
        # Add sample block (corrupted if applicable)
        lines.append(_sample_block(has_corrupted_label, stratum))
        
        # Add appearance
        signal_inversion = has_corrupted_label  # Corruption often uses signal inversion
        lines.append(_appearance_text(signal_inversion, truth))
        
        # Add combined escalation content for multi-rule targets
        if "+" in rule_target:
            escalation_additions = template["prompt_additions"]
            lines.append(self.rng.choice(escalation_additions))
        
        # Response
        lines.append(f"PROPOSED RESPONSE: {_response_text(truth, stratum)}")
        
        prompt = " ".join(lines)
        
        # Novelty check
        test_case = {"prompt": prompt, "stratum": stratum}
        if not check_novelty(test_case, threshold=0.85):
            return None
        
        public_case = _make_public_case(case_id, prompt)
        private_case = _make_private_case(
            case_id=case_id,
            stratum=stratum,
            truth=truth,
            contradiction=has_contradiction,
            corrupted=has_corrupted_label,
            signal_inversion=signal_inversion,
        )
        
        # PHASE 3: Add rule-specific metadata
        private_case["rule_target"] = rule_target
        private_case["is_ambiguous"] = is_ambiguous
        
        return {"public": public_case, "private": private_case}

    def generate_batch(self, n: int = 20, memory_fraction: float = 0.7) -> Dict[str, Any]:
        """Generate n cases, biased toward failure zones.

        Args:
            n: Total number of cases to generate
            memory_fraction: Fraction of cases generated from failure patterns
                            (rest are random exploration for novelty)

        Returns:
            Dict with public_cases, private_key, and summary
        """
        # Recompute weights from latest failures
        self.stratum_weights = compute_stratum_weights(alpha=self.alpha)
        self.patterns = load_patterns()

        # Determine how many cases from memory vs random
        memory_count = max(1, int(n * memory_fraction))
        random_count = n - memory_count

        public_cases = []
        private_key = {}

        # ── Memory-driven cases ──────────────────────────────────────────
        memory_generated = 0
        attempts = 0
        max_attempts = memory_count * 5  # Prevent infinite loop

        while memory_generated < memory_count and attempts < max_attempts:
            attempts += 1
            case = self._generate_from_memory()
            if case:
                public_cases.append(case["public"])
                case_id = case["public"]["case_id"]
                private_key[case_id] = case["private"]
                memory_generated += 1

        # ── Random exploration cases (novelty injection) ─────────────────
        stratum_counts = _allocate_counts(random_count, self.stratum_weights)
        case_id_counter = len(public_cases) + 1

        for stratum, count in stratum_counts.items():
            truths = _allocate_truths(stratum, count)
            self.rng.shuffle(truths)

            for truth in truths:
                case_id = f"ADP-{case_id_counter:04d}"
                signal_inversion = truth == "correct" and self.rng.random() < 0.45
                if not signal_inversion and truth != "correct":
                    signal_inversion = self.rng.random() < 0.35

                corrupted = self.rng.random() < 0.20
                contradiction = stratum in {"A", "B", "C"} or truth == "undefined"

                prompt = _build_prompt(
                    rng=self.rng,
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
                case_id_counter += 1

        self.rng.shuffle(public_cases)

        # ── Summary ──────────────────────────────────────────────────────
        undefined_share = sum(
            1 for v in private_key.values() if v["ground_truth"] == "undefined"
        ) / max(len(private_key), 1)

        return {
            "public_cases": public_cases,
            "private_key": private_key,
            "summary": {
                "count": len(public_cases),
                "memory_driven": memory_generated,
                "random_exploration": len(public_cases) - memory_generated,
                "stratum_weights": {k: round(v, 4) for k, v in self.stratum_weights.items()},
                "pattern_count": len(self.patterns),
                "undefined_share": round(undefined_share, 4),
            },
        }

    def _generate_from_memory(self) -> Optional[Dict[str, Any]]:
        """Generate a case by amplifying an existing failure pattern.

        Returns None if no patterns exist or novelty check fails.
        """
        if not self.patterns:
            return None

        # Weight patterns by failure count (more failures → more likely to sample)
        pattern_weights = [p.get("failure_count", 1) for p in self.patterns]
        total_weight = sum(pattern_weights)
        if total_weight == 0:
            return None

        # Sample a pattern proportional to its failure count
        chosen = self.rng.choices(self.patterns, weights=pattern_weights, k=1)[0]

        # Determine escalation level
        esc_level = chosen.get("escalation_level", 0)
        if esc_level < 3:  # Max 3 escalation levels
            chosen["escalation_level"] = esc_level + 1

        # Mutate the pattern to create a harder variant
        mutated = self._mutate_pattern(chosen)

        # Generate case from mutated pattern
        return self._build_case_from_pattern(mutated)

    def _mutate_pattern(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Apply escalation rules to make a pattern harder.

        Each mutation increases the difficulty along one or more axes.
        """
        mutated = pattern.copy()
        esc_level = mutated.get("escalation_level", 1)

        # Always strengthen signal inversion at higher escalation levels
        if esc_level >= 2:
            mutated["signal_inversion"] = True

        # At level 2+, add cross-trap composition
        if esc_level >= 2:
            if mutated.get("has_contradiction"):
                mutated["has_corruption"] = True  # Add corruption to contradiction
            elif mutated.get("has_corruption"):
                mutated["has_contradiction"] = True  # Add contradiction to corruption

        # At level 3, add all traps
        if esc_level >= 3:
            mutated["signal_inversion"] = True
            mutated["has_corruption"] = True
            mutated["has_contradiction"] = True

        return mutated

    def _build_case_from_pattern(self, pattern: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build a concrete case from a pattern template.

        Returns None if novelty check fails.
        """
        stratum = pattern["stratum"]
        truth = pattern.get("truth", "undefined")
        signal_inversion = pattern.get("signal_inversion", False)
        corrupted = pattern.get("has_corruption", False)
        contradiction = pattern.get("has_contradiction", False)

        domain = self.rng.choice(DOMAINS)
        case_id = f"AMP-{self.rng.randint(1000, 9999):04d}"

        # Build prompt with escalated features
        lines = [
            f"CASE {case_id}",
            f"Domain: {domain}.",
            _problem_rule(stratum),
        ]

        # Extra detail (always present)
        lines.append(f"Extra detail: {self.rng.choice(IRRELEVANT_DETAILS)}.")

        # Redundant note
        lines.append(f"Redundant note: {self.rng.choice(REDUNDANT_DETAILS)}.")

        # Escalated sample block
        if pattern.get("has_corruption") and pattern.get("has_contradiction"):
            # Level 3: multiple conflicting signals
            lines.append("Sample labels from two different memos conflict with each other and with the prose.")
            lines.append("A supervisor note endorses one memo while rejecting the other.")
        elif corrupted:
            lines.append(_sample_block(True, stratum))
        else:
            lines.append(_sample_block(False, stratum))

        # Escalated appearance
        if signal_inversion:
            lines.append(_appearance_text(True, truth))
        else:
            lines.append(_appearance_text(False, truth))

        # Escalation-specific additions
        if pattern.get("escalation_level", 0) >= 2:
            lines.append("A secondary review confirms the primary assessment but uses different criteria.")
        if pattern.get("escalation_level", 0) >= 3:
            lines.append("Historical precedent suggests an alternative interpretation, but records are incomplete.")

        # Supervisor note for contradiction strata
        if stratum in {"B", "C"} or contradiction:
            lines.append("A supervisor note explicitly says an example disagrees with the written rule.")

        # Undefined marker
        if truth == "undefined":
            lines.append("A missing or incompatible constraint prevents a single decidable target.")

        # Response
        lines.append(f"PROPOSED RESPONSE: {_response_text(truth, stratum)}")

        prompt = " ".join(lines)

        # Novelty check
        test_case = {"prompt": prompt, "stratum": stratum}
        if not check_novelty(test_case, threshold=0.90):
            # Pattern too similar to existing ones — skip
            return None

        public_case = _make_public_case(case_id, prompt)
        private_case = _make_private_case(
            case_id=case_id,
            stratum=stratum,
            truth=truth,
            contradiction=contradiction,
            corrupted=corrupted,
            signal_inversion=signal_inversion,
        )

        return {"public": public_case, "private": private_case}

    def record_failure(self, case: Dict[str, Any], prediction: Dict[str, Any],
                       error_classification: Dict[str, List[str]]) -> None:
        """Record a Doctor failure and update internal pattern registry."""
        from dataset_generator.failure_capture import log_failure

        log_failure(case, prediction, error_classification)
        register_failure_pattern(case, error_classification)

        # Recompute weights for next generation
        self.stratum_weights = compute_stratum_weights(alpha=self.alpha)
        self.patterns = load_patterns()

    def get_weakness_report(self) -> Dict[str, Any]:
        """Return structured weakness analysis from accumulated failures."""
        return weakness_report()

    def get_generator_state(self) -> Dict[str, Any]:
        """Return current generator state for inspection/debugging."""
        return {
            "stratum_weights": {k: round(v, 4) for k, v in self.stratum_weights.items()},
            "pattern_count": len(self.patterns),
            "patterns_by_stratum": self._patterns_by_stratum(),
            "escalation_levels": self._escalation_distribution(),
        }

    def _patterns_by_stratum(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for p in self.patterns:
            s = p["stratum"]
            counts[s] = counts.get(s, 0) + 1
        return counts

    def _escalation_distribution(self) -> Dict[int, int]:
        counts: Dict[int, int] = {}
        for p in self.patterns:
            level = p.get("escalation_level", 0)
            counts[level] = counts.get(level, 0) + 1
        return counts


# ── Convenience: Full Evaluation Loop ────────────────────────────────────────

def run_adaptive_evaluation(
    generator: AdaptiveGenerator,
    evaluate_fn,  # Callable that takes (public_case) -> prediction dict
    n_cases: int = 20,
    n_rounds: int = 3,
) -> Dict[str, Any]:
    """Run the full feedback loop: generate → evaluate → learn → repeat.

    Args:
        generator: AdaptiveGenerator instance
        evaluate_fn: Function that takes a public case dict and returns
                     a prediction dict with keys: label, confidence, etc.
        n_cases: Number of cases per round
        n_rounds: Number of generate-evaluate-learn cycles

    Returns:
        Dict with per-round metrics and final weakness report.
    """
    round_metrics = []

    for round_num in range(1, n_rounds + 1):
        print(f"\n{'='*60}")
        print(f"ROUND {round_num}/{n_rounds}")
        print(f"{'='*60}")

        # Generate cases (increasing memory_fraction each round)
        memory_frac = min(0.9, 0.5 + round_num * 0.15)
        batch = generator.generate_batch(n=n_cases, memory_fraction=memory_frac)

        print(f"  Cases: {batch['summary']['count']}")
        print(f"  Memory-driven: {batch['summary']['memory_driven']}")
        print(f"  Random exploration: {batch['summary']['random_exploration']}")
        print(f"  Stratum weights: {batch['summary']['stratum_weights']}")

        # Evaluate each case
        results = []
        for pub_case in batch["public_cases"]:
            prediction = evaluate_fn(pub_case)
            priv_case = batch["private_key"][pub_case["case_id"]]

            # Classify errors (PHASE 2: now returns dict with error_types and rule_violations)
            from dataset_generator.failure_capture import classify_error
            error_classification = classify_error(priv_case, prediction)
            error_types = error_classification["error_types"]
            rule_violations = error_classification["rule_violations"]

            # Record failures
            if error_types or rule_violations:
                generator.record_failure(priv_case, prediction, error_classification)

            results.append({
                "case_id": pub_case["case_id"],
                "stratum": priv_case["stratum"],
                "ground_truth": priv_case["ground_truth"],
                "prediction": prediction["label"],
                "confidence": prediction.get("confidence", 0.0),
                "correct": prediction["label"] == priv_case["ground_truth"],
                "error_types": error_types,
                "rule_violations": rule_violations,  # PHASE 2: New field
            })

        # Round metrics
        correct = sum(1 for r in results if r["correct"])
        total = len(results)
        round_metrics.append({
            "round": round_num,
            "accuracy": correct / total if total else 0.0,
            "total_cases": total,
            "correct": correct,
            "failures": total - correct,
            "error_type_counts": _aggregate_errors(results),
        })

        print(f"  Accuracy: {correct}/{total} = {correct/total:.1%}" if total else "  No cases")

    # Final weakness report
    report = generator.get_weakness_report()

    return {
        "rounds": round_metrics,
        "weakness_report": report,
        "generator_state": generator.get_generator_state(),
    }


def _aggregate_errors(results: List[Dict]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for r in results:
        for et in r.get("error_types", []):
            counts[et] = counts.get(et, 0) + 1
    return counts

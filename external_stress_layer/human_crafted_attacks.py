"""
Human-Crafted Attacks
=====================
Manually designed adversarial cases that specifically target suspected Doctor blind spots.

These are gold-standard attacks created by humans who understand:
- The Doctor's architecture (evidence extraction, claim building, decision engine)
- Known failure modes from adaptive testing
- Edge cases the generator doesn't model
- Logical traps that exploit the rule-based reasoning

Each attack is designed to break specific assumptions in the Doctor's pipeline.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from external_stress_layer import StressCase, StressKind


class AttackPattern:
    """Template for a human-crafted adversarial attack."""
    
    def __init__(
        self,
        name: str,
        description: str,
        target_weakness: str,
        prompt_template: str,
        ground_truth: str,
        expected_failure_mode: str,
    ):
        self.name = name
        self.description = description
        self.target_weakness = target_weakness
        self.prompt_template = prompt_template
        self.ground_truth = ground_truth
        self.expected_failure_mode = expected_failure_mode


# Attack patterns designed to exploit known Doctor weaknesses
ATTACK_PATTERNS = [
    # Attack 1: Evidence exhaustion - overwhelm with many weak signals
    AttackPattern(
        name="evidence_exhaustion",
        description="Flood prompt with many weak evidence signals that individually don't reach thresholds but collectively should matter",
        target_weakness="Layer 2 claim scoring: independent scoring may miss cumulative weak signals",
        prompt_template=(
            "CASE: Multi-signal accumulation test\n"
            "Domain: complex policy evaluation.\n"
            "Rules: The policy has several minor gaps and ambiguities.\n"
            "Observation 1: The tie-breaking procedure is not fully specified.\n"
            "Observation 2: Edge cases for retroactive edits are unclear.\n"
            "Observation 3: The audit trail requirements lack detail.\n"
            "Observation 4: Exception handling paths are incompletely described.\n"
            "Observation 5: The escalation procedure has unspecified triggers.\n"
            "Observation 6: Conflict resolution between subsystems is not documented.\n"
            "Observation 7: Priority definitions have overlapping ranges.\n"
            "Observation 8: Timeout behavior is ambiguously specified.\n"
            "Each individual gap is minor, but collectively they prevent a fully correct implementation.\n"
            "PROPOSED RESPONSE: Addresses the major requirements but leaves several edge cases "
            "unresolved due to specification gaps. Partial but reasonable given the input."
        ),
        ground_truth="partial",
        expected_failure_mode="May classify as 'correct' if each signal individually below threshold",
    ),

    # Attack 2: Conflicting meta-signals - signals about signals
    AttackPattern(
        name="conflicting_meta_signals",
        description="Present evidence that conflicts at the meta-level (evidence about evidence)",
        target_weakness="Layer 1 evidence extraction doesn't handle meta-reasoning",
        prompt_template=(
            "CASE: Meta-level conflict test\n"
            "Domain: policy analysis with conflicting documentation.\n"
            "Primary rule: Minimize delay while preserving arrival order.\n"
            "A later memo states: 'The primary rule above was superseded by the revised policy, "
            "which prioritizes order over delay.'\n"
            "However, an even earlier document says: 'All rule changes require unanimous approval, "
            "which was not obtained for the revision.'\n"
            "A third document notes: 'The approval requirement itself was amended in Q2.'\n"
            "The chain of authority is unclear, and documents reference each other circularly.\n"
            "PROPOSED RESPONSE: Applies the original rule, noting the conflict but deferring to "
            "the earliest documented policy as most authoritative."
        ),
        ground_truth="undefined",
        expected_failure_mode="May pick one document as authoritative without recognizing fundamental undecidability",
    ),

    # Attack 3: Self-referential paradox
    AttackPattern(
        name="self_referential_paradox",
        description="Create a self-referential rule that creates logical paradox",
        target_weakness="Decision engine doesn't detect logical paradoxes",
        prompt_template=(
            "CASE: Self-referential rule test\n"
            "Domain: recursive policy evaluation.\n"
            "Rule: This policy should be classified as 'undefined' if and only if it contains "
            "a self-referential paradox.\n"
            "This policy contains a self-referential paradox (see Rule above).\n"
            "Additional context: The policy also specifies that all rules must be consistent, "
            "but this rule is self-referential and therefore potentially inconsistent.\n"
            "PROPOSED RESPONSE: Classifies the policy as 'undefined' due to the self-referential "
            "paradox, which makes the target logically undecidable."
        ),
        ground_truth="undefined",
        expected_failure_mode="May not recognize the paradox and classify based on surface-level signals",
    ),

    # Attack 4: Threshold gaming - signals right at decision boundaries
    AttackPattern(
        name="threshold_gaming",
        description="Construct case with signals precisely at classification thresholds",
        target_weakness="Threshold-based decisions are brittle at boundaries",
        prompt_template=(
            "CASE: Boundary condition test\n"
            "Domain: precision threshold evaluation.\n"
            "The policy explicitly states a single clear objective with no ambiguity.\n"
            "All examples are perfectly consistent with the prose.\n"
            "However, one minor exception route is left unresolved.\n"
            "The proposed response handles the common path correctly.\n"
            "There is a single unresolved edge case that affects less than 1% of inputs.\n"
            "The response acknowledges this limitation but provides no fallback.\n"
            "PROPOSED RESPONSE: Correctly handles the main case, leaves one exception unresolved."
        ),
        ground_truth="partial",
        expected_failure_mode="May classify as 'correct' if exception is deemed too minor, or 'undefined' if over-weighted",
    ),

    # Attack 5: Semantic inversion - correct signals point to wrong answer
    AttackPattern(
        name="semantic_inversion",
        description="All surface-level signals point to one answer but deeper analysis reveals another",
        target_weakness="Evidence extraction is pattern-matching, not deep semantic analysis",
        prompt_template=(
            "CASE: Semantic inversion test\n"
            "Domain: deceptive policy analysis.\n"
            "The policy text uses confident, authoritative language throughout.\n"
            "Rules are stated clearly and appear complete.\n"
            "Examples are provided and seem consistent.\n"
            "The proposed response mirrors the policy language precisely.\n"
            "HOWEVER: A careful reading reveals the policy contains an internal contradiction: "
            "Rule A requires X, Rule B requires NOT X, and no tie-breaking is specified.\n"
            "The contradiction is hidden in subtle wording differences between sections.\n"
            "PROPOSED RESPONSE: Correct and complete implementation of all stated requirements."
        ),
        ground_truth="partial",
        expected_failure_mode="May classify as 'correct' due to strong surface signals, missing hidden contradiction",
    ),

    # Attack 6: Domain mismatch - use unfamiliar domain with familiar structure
    AttackPattern(
        name="domain_mismatch",
        description="Use completely unfamiliar domain but structurally familiar pattern",
        target_weakness="May rely on domain-specific heuristics rather than structural reasoning",
        prompt_template=(
            "CASE: Cross-domain structural test\n"
            "Domain: quantum error correction code scheduling.\n"
            "Rules: The syndrome extraction circuit must preserve fault-distance while minimizing "
            "ancilla qubit reuse. Measurements must be spacelike separated but the scheduling "
            "window allows only timelike separation for certain stabilizer groups.\n"
            "Additional constraint: The decoder assumes independent errors, but the scheduling "
            "creates correlated error patterns.\n"
            "Examples show two different valid schedules with different resource trade-offs.\n"
            "A technical note mentions that 'either schedule preserves the code distance requirement.'\n"
            "PROPOSED RESPONSE: Provides one valid schedule, noting the trade-off but not proving "
            "why it's superior to the alternative."
        ),
        ground_truth="partial",
        expected_failure_mode="May say 'undefined' due to unfamiliar domain, or 'correct' if misses the trade-off",
    ),

    # Attack 7: Temporal reasoning - rules change over time
    AttackPattern(
        name="temporal_reasoning",
        description="Rules that change over time with unclear transition semantics",
        target_weakness="Static evidence extraction doesn't model temporal dynamics",
        prompt_template=(
            "CASE: Temporal rule change test\n"
            "Domain: time-varying policy evaluation.\n"
            "Original policy (effective Jan 1): Priority goes to emergency cases.\n"
            "Amendment (effective Mar 15): Priority goes to emergency cases, then by arrival time.\n"
            "Clarification (effective Feb 1, retroactive to Jan 1): 'Emergency' includes both "
            "immediate and potential emergencies as assessed by intake staff.\n"
            "The retroactive clarification creates ambiguity: do we apply the broader definition "
            "from Jan 1, or the original narrower definition for cases before Mar 15?\n"
            "Cases from January were processed under the original definition.\n"
            "PROPOSED RESPONSE: Applies the retroactive definition uniformly to all cases from Jan 1 onward."
        ),
        ground_truth="partial",
        expected_failure_mode="May say 'correct' if accepts retroactive application, or 'undefined' if sees ambiguity",
    ),

    # Attack 8: Probabilistic reasoning - rules with probabilities
    AttackPattern(
        name="probabilistic_reasoning",
        description="Rules that involve probabilistic statements or uncertain outcomes",
        target_weakness="Binary classification doesn't handle probabilistic uncertainty well",
        prompt_template=(
            "CASE: Probabilistic policy test\n"
            "Domain: stochastic decision framework.\n"
            "Rule: When resource contention occurs, prioritize by expected value (EV = probability "
            "of success × impact).\n"
            "However, probabilities are estimates with confidence intervals, not point values.\n"
            "Case A: EV = 100 (95% CI: [80, 120])\n"
            "Case B: EV = 110 (95% CI: [60, 160])\n"
            "The confidence intervals overlap significantly, making the ranking uncertain.\n"
            "The policy doesn't specify whether to use point estimates or account for uncertainty.\n"
            "PROPOSED RESPONSE: Ranks Case B higher based on point estimate, noting the uncertainty."
        ),
        ground_truth="partial",
        expected_failure_mode="May say 'correct' for point estimate approach or 'undefined' for uncertainty",
    ),

    # Attack 9: Multiple valid interpretations (hard version)
    AttackPattern(
        name="multiple_interpretations_hard",
        description="Multiple interpretations are valid but lead to different classifications",
        target_weakness="Multi-validity resolution may not handle classification-level conflicts",
        prompt_template=(
            "CASE: Interpretation conflict test\n"
            "Domain: ambiguous policy framework.\n"
            "The policy can be reasonably interpreted in two ways:\n"
            "Interpretation A: The rules are complete and consistent, making this decidable. "
            "Under this interpretation, the proposed response is correct.\n"
            "Interpretation B: The rules contain an implicit gap that prevents a single decidable "
            "target. Under this interpretation, the proposed response is partial.\n"
            "Both interpretations are supported by different sections of the policy.\n"
            "A footnote states: 'Where reasonable interpretations differ, consult the working "
            "examples.' But the working examples support different interpretations.\n"
            "PROPOSED RESPONSE: Correct implementation under the most natural reading of the policy."
        ),
        ground_truth="undefined",
        expected_failure_mode="May pick one interpretation and say 'correct' or 'partial' instead of 'undefined'",
    ),

    # Attack 10: Minimal information - barely enough to classify
    AttackPattern(
        name="minimal_information",
        description="Provide barely enough information to make a classification",
        target_weakness="May over-commit or under-commit when information is sparse",
        prompt_template=(
            "CASE: Minimal information test\n"
            "Domain: underspecified system.\n"
            "Rule: Process in order of arrival, with exceptions for priority cases.\n"
            "No definition of 'priority' is provided.\n"
            "One example shows an exception being made, but the reason isn't stated.\n"
            "PROPOSED RESPONSE: Processes in arrival order, handling exceptions as they arise."
        ),
        ground_truth="partial",
        expected_failure_mode="May say 'undefined' (too cautious) or 'correct' (not cautious enough)",
    ),

    # Attack 11: IMPLICIT undefined (NEW - exploits missing undefined detection)
    AttackPattern(
        name="implicit_undefined",
        description="Create genuinely undefined cases WITHOUT using explicit 'undecidable' language",
        target_weakness="Doctor only detects 'undefined' when explicitly stated, not when implicit",
        prompt_template=(
            "CASE: Implicit ambiguity test\n"
            "Domain: scheduling policy.\n"
            "Rule: Process requests in priority order.\n"
            "Two requests arrive simultaneously with identical priority.\n"
            "No tie-breaking mechanism is specified.\n"
            "The examples show one being processed first, but don't explain why.\n"
            "The proposed response processes them in arbitrary order.\n"
            "PROPOSED RESPONSE: Handles the common case correctly, leaves tie-breaking unspecified."
        ),
        ground_truth="undefined",
        expected_failure_mode="Will likely say 'partial' (undercommitment) instead of recognizing fundamental ambiguity",
    ),

    # Attack 12: Correct misclassified as partial (NEW - exploits undercommitment bias)
    AttackPattern(
        name="correct_undercommitment",
        description="A genuinely correct response that Doctor will likely call 'partial' due to bias",
        target_weakness="Doctor's fallback is 'partial' causing undercommitment on correct cases",
        prompt_template=(
            "CASE: Correct response test\n"
            "Domain: priority scheduling.\n"
            "Rule: Process high priority before low priority.\n"
            "High priority request arrives at t=5, low priority at t=3.\n"
            "The proposed response processes high priority first (at t=5), then low priority.\n"
            "This correctly implements the priority rule.\n"
            "All requirements are met, no ambiguities exist.\n"
            "PROPOSED RESPONSE: Correct implementation of the priority scheduling rule."
        ),
        ground_truth="correct",
        expected_failure_mode="May say 'partial' due to default fallback behavior when uncertain",
    ),

    # Attack 13: Contradiction without explicit signals (NEW)
    AttackPattern(
        name="implicit_contradiction",
        description="Hidden contradiction that doesn't match Doctor's regex patterns",
        target_weakness="Evidence extraction relies on specific phrases, misses semantic contradictions",
        prompt_template=(
            "CASE: Hidden contradiction test\n"
            "Domain: access control policy.\n"
            "Section 3.2: All requests must be approved within 24 hours.\n"
            "Section 7.1: All requests require manager approval before processing.\n"
            "Managers are only available during business hours (9am-5pm).\n"
            "A request arrives at 6pm on Friday.\n"
            "The proposed response holds the request until Monday for manager approval.\n"
            "This violates the 24-hour requirement but follows the approval process.\n"
            "PROPOSED RESPONSE: Follows the approval process, acknowledging the 24-hour violation."
        ),
        ground_truth="partial",
        expected_failure_mode="May not detect the contradiction between Sections 3.2 and 7.1",
    ),

    # Attack 14: Performance vs correctness confusion (NEW)
    AttackPattern(
        name="performance_correctness_mix",
        description="Mixes performance requirements with correctness, creating ambiguity",
        target_weakness="Doctor doesn't distinguish between 'correct but slow' and 'incorrect'",
        prompt_template=(
            "CASE: Performance vs correctness test\n"
            "Domain: search algorithm specification.\n"
            "Requirement: Find the shortest path in a graph with 1000 nodes.\n"
            "Constraint: Must complete within 1 second.\n"
            "The proposed response uses BFS (correct but O(V+E), might exceed 1s on dense graphs).\n"
            "The response is algorithmically correct but may violate the time constraint.\n"
            "PROPOSED RESPONSE: Correct algorithm, performance depends on graph density."
        ),
        ground_truth="partial",
        expected_failure_mode="May say 'correct' (algorithmically) or 'undefined' (time constraint unclear)",
    ),

    # Attack 15: Meta-attack on Doctor's architecture (NEW)
    AttackPattern(
        name="doctor_architecture_exploit",
        description="Designed to exploit the specific structure of the Doctor's decision engine",
        target_weakness="The Doctor's R1-R5 rules have gaps; fallback to _classify has biases",
        prompt_template=(
            "CASE: Doctor architecture test\n"
            "Domain: rule evaluation.\n"
            "The specification contains:\n"
            "- No explicit undecidable target (avoids R1)\n"
            "- No conflicting examples (avoids R2)\n"
            "- No competing objectives (avoids R3)\n"
            "- No multi-validity signals (avoids R4)\n"
            "- Minor ambiguity but below threshold (avoids R5)\n"
            "But also no strong CORRECT signals (completeness_score will be low).\n"
            "The proposed response handles the requirements as stated.\n"
            "PROPOSED RESPONSE: Addresses stated requirements, leaves implicit gaps unfilled."
        ),
        ground_truth="partial",
        expected_failure_mode="Will fall through all R1-R5 rules to _classify, which may return wrong label",
    ),
]


class HumanCraftedAttacks:
    """Manually designed adversarial cases targeting Doctor blind spots.
    
    These attacks are crafted by humans who understand the Doctor's architecture
    and can design cases that specifically exploit its weaknesses:
    
    1. Evidence exhaustion - overwhelm with weak signals
    2. Conflicting meta-signals - evidence about evidence
    3. Self-referential paradox - logical traps
    4. Threshold gaming - signals at decision boundaries
    5. Semantic inversion - surface vs. deep conflict
    6. Domain mismatch - unfamiliar domain, familiar structure
    7. Temporal reasoning - rules changing over time
    8. Probabilistic reasoning - uncertainty handling
    9. Multiple interpretations (hard) - classification-level conflicts
    10. Minimal information - sparse input handling
    """
    
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.case_counter = 0
        self.attack_patterns = ATTACK_PATTERNS
    
    def generate_cases(
        self,
        n: int | None = None,
        specific_attacks: List[str] | None = None,
    ) -> List[StressCase]:
        """Generate human-crafted attack cases.
        
        Args:
            n: Number of cases (None = all patterns)
            specific_attacks: Specific attack names to include (None = all)
            
        Returns:
            List of StressCase objects
        """
        # Filter by specific attacks if requested
        if specific_attacks:
            patterns = [p for p in self.attack_patterns if p.name in specific_attacks]
        else:
            patterns = self.attack_patterns
        
        # Sample if n is specified
        if n is not None and n < len(patterns):
            selected = self.rng.sample(patterns, n)
        else:
            selected = list(patterns)
        
        cases = []
        for pattern in selected:
            case = self._create_case(pattern)
            cases.append(case)
        
        self.rng.shuffle(cases)
        return cases
    
    def get_attack_info(self, attack_name: str) -> Optional[AttackPattern]:
        """Get information about a specific attack pattern."""
        for pattern in self.attack_patterns:
            if pattern.name == attack_name:
                return pattern
        return None
    
    def list_attacks(self) -> List[Dict[str, str]]:
        """List all available attack patterns."""
        return [
            {
                "name": p.name,
                "description": p.description,
                "target_weakness": p.target_weakness,
                "expected_failure": p.expected_failure_mode,
            }
            for p in self.attack_patterns
        ]
    
    def _create_case(self, pattern: AttackPattern) -> StressCase:
        """Create a StressCase from an attack pattern."""
        self.case_counter += 1
        case_id = f"HC-{self.case_counter:04d}"
        
        return StressCase(
            case_id=case_id,
            prompt=pattern.prompt_template,
            stress_kind=StressKind.HUMAN_CRAFTED,
            ground_truth=pattern.ground_truth,
            metadata={
                "attack_name": pattern.name,
                "attack_description": pattern.description,
                "target_weakness": pattern.target_weakness,
                "expected_failure_mode": pattern.expected_failure_mode,
            },
        )

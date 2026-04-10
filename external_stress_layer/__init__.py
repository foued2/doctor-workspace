"""
External Stress Layer (ESL) — Stage 3
=======================================
Transitions from internal adversarial testing to real-world stress testing.

Architecture:
  Adaptive Generator (internal adversary)
          +
  External Stress Layer (uncontrolled inputs)
          ↓
      Doctor
          ↓
  Enhanced Evaluator

Components:
  - RealWorldInjector: Injects real LeetCode problems and messy real-world prompts
  - NoiseInjectionLayer: Corrupts inputs in ways the generator doesn't model
  - CrossDomainStressor: Tests generalization with non-domain-specific prompts
  - HumanCraftedAttacks: Manually designed cases that exploit blind spots
  - EnhancedEvaluator: Adds robustness, degradation curves, failure diversity metrics
  - StressTestOrchestrator: Combines all components into a unified pipeline

Usage:
    from external_stress_layer import StressTestOrchestrator
    orchestrator = StressTestOrchestrator(doctor=RawPromptDoctor())
    results = orchestrator.run_stress_test(n_external=50, noise_levels=[0.0, 0.2, 0.4, 0.6])
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum, auto

__all__ = [
    "StressKind",
    "StressCase",
    "StressMetrics",
    "StressTestResult",
    "StressTestOrchestrator",
    "RealWorldInjector",
    "RealWorldDataInjector",
    "NoiseInjectionLayer",
    "CrossDomainStressor",
    "HumanCraftedAttacks",
    "EnhancedEvaluator",
    "MixedBatchRunner",
]


class StressKind(Enum):
    """Types of external stress that can be applied."""
    REAL_WORLD = auto()        # Real LeetCode/messy problems
    NOISE_INJECTION = auto()   # Corrupted/truncated/mixed inputs
    CROSS_DOMAIN = auto()      # Legal, medical, business, etc.
    HUMAN_CRAFTED = auto()     # Manually designed attacks
    MIXED = auto()             # Combination of all above


@dataclass
class StressCase:
    """A single stress test case with metadata.

    Similar to the generator's public/private case structure but with
    additional metadata for tracking stress type and degradation.
    """
    case_id: str
    prompt: str
    stress_kind: StressKind
    ground_truth: str  # "correct", "partial", or "undefined"
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Noise tracking (for degradation curve analysis)
    noise_level: float = 0.0
    original_prompt: Optional[str] = None  # Before noise was applied

    # Failure analysis
    failure_pattern: Optional[str] = None  # What kind of failure occurred
    recovery_attempt: Optional[int] = None  # If this is a retry after failure


@dataclass
class StressMetrics:
    """Extended metrics for stress testing.

    Includes all standard evaluator metrics plus:
    - robustness_score: accuracy(noisy) / accuracy(clean)
    - degradation_curve: accuracy at each noise level
    - failure_diversity: how varied the failures are
    - recovery_rate: success rate after initial failure
    """
    # Standard metrics
    accuracy: float = 0.0
    overconfidence_rate: float = 0.0
    underconfidence_rate: float = 0.0

    # Stress-specific metrics
    robustness_score: float = 0.0
    degradation_curve: Dict[str, float] = field(default_factory=dict)
    failure_diversity: float = 0.0
    recovery_rate: float = 0.0

    # Breakdown by stress kind
    by_stress_kind: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # Failure analysis
    failure_patterns: Dict[str, int] = field(default_factory=dict)
    failure_by_stratum: Dict[str, float] = field(default_factory=dict)

    # PHASE 2: Rule violation metrics
    rule_violations: Dict[str, int] = field(default_factory=dict)  # Count per rule (R1, R2, R3)
    rule_violation_rate: float = 0.0  # Weighted rule violation rate
    rule_violation_cases: List[Dict[str, Any]] = field(default_factory=list)  # Detailed cases

    # PHASE 5: Second-pass evaluation metrics
    second_pass_results: List[Dict[str, Any]] = field(default_factory=list)
    correct_by_luck_count: int = 0
    wrong_with_violation_count: int = 0

    # PHASE 5: Calibration metrics
    calibration: Dict[str, Any] = field(default_factory=dict)

    # PHASE 5: Distribution shift metrics
    distribution_shift: Dict[str, Any] = field(default_factory=dict)

    # Detailed results
    total_cases: int = 0
    correct_cases: int = 0
    failed_cases: int = 0


@dataclass
class StressTestResult:
    """Complete results from a stress test run."""
    metrics: StressMetrics
    cases: List[StressCase]
    predictions: List[Dict[str, Any]]
    configuration: Dict[str, Any]

    def summary(self) -> str:
        """Return a human-readable summary of results."""
        lines = [
            "=" * 60,
            "STRESS TEST RESULTS",
            "=" * 60,
            f"Total cases: {self.metrics.total_cases}",
            f"Accuracy: {self.metrics.accuracy:.2%}",
            f"Robustness score: {self.metrics.robustness_score:.2%}",
            f"Failure diversity: {self.metrics.failure_diversity:.2%}",
            f"Recovery rate: {self.metrics.recovery_rate:.2%}",
            "",
            "Degradation curve:",
        ]
        for noise_level, acc in sorted(self.metrics.degradation_curve.items()):
            lines.append(f"  Noise {noise_level:>5s}: {acc:.2%}")

        if self.metrics.by_stress_kind:
            lines.append("")
            lines.append("By stress kind:")
            for kind, metrics in self.metrics.by_stress_kind.items():
                if isinstance(metrics, dict):
                    lines.append(f"  {kind}: {metrics.get('accuracy', 0):.2%}")
                else:
                    lines.append(f"  {kind}: {metrics:.2%}")

        if self.metrics.failure_patterns:
            lines.append("")
            lines.append("Failure patterns:")
            for pattern, count in sorted(self.metrics.failure_patterns.items(), key=lambda x: -x[1]):
                lines.append(f"  {pattern}: {count}")

        return "\n".join(lines)


# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "StressTestOrchestrator":
        from external_stress_layer.orchestrator import StressTestOrchestrator
        return StressTestOrchestrator
    elif name == "RealWorldInjector":
        from external_stress_layer.real_world_injector import RealWorldInjector
        return RealWorldInjector
    elif name == "RealWorldDataInjector":
        from external_stress_layer.real_world_data_injector import RealWorldDataInjector
        return RealWorldDataInjector
    elif name == "NoiseInjectionLayer":
        from external_stress_layer.noise_injection_layer import NoiseInjectionLayer
        return NoiseInjectionLayer
    elif name == "CrossDomainStressor":
        from external_stress_layer.cross_domain_stressor import CrossDomainStressor
        return CrossDomainStressor
    elif name == "HumanCraftedAttacks":
        from external_stress_layer.human_crafted_attacks import HumanCraftedAttacks
        return HumanCraftedAttacks
    elif name == "EnhancedEvaluator":
        from external_stress_layer.enhanced_evaluator import EnhancedEvaluator
        return EnhancedEvaluator
    elif name == "MixedBatchRunner":
        from external_stress_layer.mixed_batch_runner import MixedBatchRunner
        return MixedBatchRunner
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

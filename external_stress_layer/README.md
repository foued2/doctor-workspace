# External Stress Layer (ESL) — Stage 3

## Overview

The External Stress Layer transitions your Doctor from **internal adversarial testing** (within the synthetic generator's assumptions) to **real-world stress testing** (outside the cage).

### The Problem with Your Current Setup

Your current loop is:
```
generator → doctor → evaluator → generator
```

This creates a **self-consistent system** where:
- The generator and evaluator share assumptions
- The Doctor learns those assumptions
- Performance improves **inside the loop only**

This is controlled adversarial training, not real stress.

### The Solution: External Stress Layer

```
Adaptive Generator (internal adversary)
        +
External Stress Layer (uncontrolled inputs)
        ↓
    Doctor
        ↓
Enhanced Evaluator
```

## Architecture

The ESL consists of 5 core components:

### 1. RealWorldInjector
**Purpose**: Inject real LeetCode problems and messy real-world prompts.

**What it breaks**:
- Synthetic prompt structure
- Clean domain boundaries
- Consistent formatting

**Sources**:
- Real LeetCode problems with inherent ambiguities
- Community forum discussions with contradictory information
- Poorly written community problems
- Incomplete specifications

```python
from external_stress_layer import RealWorldInjector

injector = RealWorldInjector(seed=42)
cases = injector.generate_cases(n=20)

# Or inject into existing batch
combined = injector.inject_into_batch(generator_cases, n_inject=10)
```

### 2. NoiseInjectionLayer
**Purpose**: Corrupt inputs in ways the generator does NOT model.

**Noise types**:
- **Truncation**: Cut off prompt mid-sentence
- **Mixed language**: Insert French fragments into English
- **Formatting destruction**: Remove punctuation, spacing
- **Context flooding**: Add system logs, error messages
- **Character corruption**: Typos, missing letters
- **Semantic noise**: Add contradictory statements

```python
from external_stress_layer import NoiseInjectionLayer

noise_layer = NoiseInjectionLayer(seed=42)

# Apply noise to single case
noised_case = noise_layer.apply_noise(case, noise_level=0.3)

# Apply to batch
noised_batch = noise_layer.apply_noise_batch(cases, noise_level=0.3)

# Test multiple levels for degradation curve
results = noise_layer.apply_noise_levels(cases, noise_levels=[0.0, 0.2, 0.4, 0.6])
```

### 3. CrossDomainStressor
**Purpose**: Test generalization with non-domain-specific prompts.

**Domains**:
- Legal contracts
- Medical instructions
- System design specs
- Business rules
- Academic policies
- Financial regulations

```python
from external_stress_layer import CrossDomainStressor

stressor = CrossDomainStressor(seed=42)

# All domains
cases = stressor.generate_cases(n=20)

# Specific domains only
cases = stressor.generate_cases(n=20, domains=["legal_contract", "medical"])
```

### 4. HumanCraftedAttacks
**Purpose**: Manually designed cases that exploit known Doctor blind spots.

**Attack patterns**:
1. **evidence_exhaustion**: Overwhelm with many weak signals
2. **conflicting_meta_signals**: Evidence about evidence
3. **self_referential_paradox**: Logical traps
4. **threshold_gaming**: Signals at decision boundaries
5. **semantic_inversion**: Surface vs. deep conflict
6. **domain_mismatch**: Unfamiliar domain, familiar structure
7. **temporal_reasoning**: Rules changing over time
8. **probabilistic_reasoning**: Uncertainty handling
9. **multiple_interpretations_hard**: Classification-level conflicts
10. **minimal_information**: Sparse input handling

```python
from external_stress_layer import HumanCraftedAttacks

attacks = HumanCraftedAttacks(seed=42)

# All attacks
cases = attacks.generate_cases()

# Specific attacks only
cases = attacks.generate_cases(specific_attacks=["threshold_gaming", "semantic_inversion"])

# List available attacks
catalog = attacks.list_attacks()
```

### 5. EnhancedEvaluator
**Purpose**: Extended metrics for stress testing.

**New metrics**:
- **Robustness score**: `accuracy(noisy) / accuracy(clean)`
- **Degradation curve**: Accuracy at each noise level
- **Failure diversity**: How varied the failures are (0-1)
- **Recovery rate**: Success rate after initial failure
- **Stress kind breakdown**: Performance by stress type
- **Failure pattern analysis**: What kinds of failures occur

```python
from external_stress_layer import EnhancedEvaluator

evaluator = EnhancedEvaluator()

# Standard evaluation
metrics = evaluator.evaluate_batch(cases, predictions)

# Degradation curve analysis
degradation = evaluator.evaluate_degradation_curve(cases_by_noise)

# Recovery test
recovery = evaluator.evaluate_recovery(initial_preds, retry_preds, cases)
```

## Quick Start

### Comprehensive Stress Test

```python
from doctor.raw_prompt_doctor import RawPromptDoctor
from external_stress_layer import StressTestOrchestrator

# Initialize
doctor = RawPromptDoctor()
orchestrator = StressTestOrchestrator(doctor=doctor, seed=42)

# Run full stress test
results = orchestrator.run_stress_test(
    n_external=50,
    noise_levels=[0.0, 0.2, 0.4, 0.6],
    include_generator=True,
    include_real_world=True,
    include_cross_domain=True,
    include_human_attacks=True,
)

# View results
print(results.summary())
```

### Degradation Analysis

```python
degradation = orchestrator.run_degradation_analysis(
    noise_levels=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
)

print(f"AUC: {degradation['auc_normalized']:.4f}")
print(f"Degradation rate: {degradation['degradation_rate']:.4f}")
```

### Recovery Test

```python
recovery = orchestrator.run_recovery_test()
print(f"Recovery rate: {recovery['recovery_rate']:.2%}")
```

## Metrics Interpretation

### Success Criteria

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| Accuracy | > 80% | 60-80% | < 60% |
| Robustness | > 0.9 | 0.7-0.9 | < 0.7 |
| Failure Diversity | > 0.7 | 0.4-0.7 | < 0.4 |
| Recovery Rate | > 0.5 | 0.3-0.5 | < 0.3 |

### What These Mean

- **High accuracy, low robustness**: Doctor works well in clean conditions but breaks under noise
- **Low failure diversity**: Doctor has specific blind spots (systematically exploitable)
- **Low recovery rate**: Doctor repeats same mistakes, doesn't learn from failures

## Running the Example

```bash
python tests/run_external_stress_test.py
```

This script demonstrates:
1. Attack catalog display
2. Comprehensive stress test
3. Degradation curve analysis
4. Recovery test
5. Individual component tests
6. Noise sensitivity test

## Advanced Usage

### Custom Stress Test Configuration

```python
results = orchestrator.run_stress_test(
    n_external=100,  # More cases
    noise_levels=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],  # Finer granularity
    include_generator=False,  # Only external sources
    include_real_world=True,
    include_cross_domain=False,
    include_human_attacks=True,
)
```

### Testing Specific Attack Patterns

```python
from external_stress_layer import HumanCraftedAttacks

attacks = HumanCraftedAttacks()
specific = attacks.generate_cases(specific_attacks=[
    "self_referential_paradox",
    "temporal_reasoning",
    "probabilistic_reasoning",
])

# Evaluate only these attacks
predictions = [doctor.predict(c.prompt) for c in specific]
metrics = evaluator.evaluate_batch(specific, predictions)
```

### Combining with Internal Generator

```python
from dataset_generator.adaptive_generator import AdaptiveGenerator

# Generate internal cases
gen = AdaptiveGenerator(seed=42)
internal_batch = gen.generate_batch(n=50, memory_fraction=0.7)

# Convert to StressCase format
from external_stress_layer import StressCase, StressKind

internal_cases = []
for pub, priv in zip(internal_batch["public_cases"], internal_batch["private_key"].values()):
    internal_cases.append(StressCase(
        case_id=pub["case_id"],
        prompt=pub["prompt"],
        stress_kind=StressKind.MIXED,
        ground_truth=priv["ground_truth"],
        metadata={"source": "internal_generator"},
    ))

# Run stress test with pre-generated cases
results = orchestrator.run_stress_test(
    generator_cases=internal_cases,
    include_real_world=True,
)
```

## File Structure

```
external_stress_layer/
├── __init__.py                    # Package exports
├── real_world_injector.py         # Real-world problem injection
├── noise_injection_layer.py       # Noise corruption strategies
├── cross_domain_stressor.py       # Cross-domain generalization tests
├── human_crafted_attacks.py       # Manual adversarial cases
├── enhanced_evaluator.py          # Extended metrics
└── orchestrator.py                # Unified pipeline
```

## Next Steps

After running stress tests:

1. **Identify weak points**: Look at failure patterns in results
2. **Target specific issues**: Run focused tests on weak areas
3. **Iterate on Doctor**: Fix identified blind spots
4. **Re-test**: Verify improvements hold under stress
5. **Expand attack surface**: Add new human-crafted attacks

## Philosophy

> "Your generator hunts the Doctor inside a cage. Serious stress testing means opening the cage and seeing if the Doctor survives outside it."

The ESL doesn't replace your internal adversary—it **complements** it by testing whether the Doctor has learned to pattern-match within a closed universe or can actually reason under uncertainty.

Success is not:
- High accuracy
- Low failure rate

But:
> Failure rate stabilizes under *increasing adversarial pressure*

Meaning you keep making attacks harder, and the failure rate doesn't explode.

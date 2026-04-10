# External Stress Layer (ESL) — Stage 3 Implementation Summary

## Overview

This document summarizes the implementation of the External Stress Layer (ESL) 
for the Doctor stress testing pipeline. The ESL transitions from internal 
adversarial testing (Stage 2) to real-world stress testing (Stage 3).

## Architecture

```
Adaptive Generator (internal adversary)
        +
External Stress Layer (uncontrolled inputs)
  ├─ RealWorldDataInjector (actual LeetCode, GitHub, StackOverflow, interview questions)
  ├─ NoiseInjectionLayer (8 noise types including false evidence injection)
  ├─ CrossDomainStressor (legal, medical, business, financial, academic)
  ├─ HumanCraftedAttacks (15 handcrafted attacks targeting specific blind spots)
  └─ MixedBatchRunner (configurable internal/external ratios)
        ↓
    Doctor
        ↓
Enhanced Evaluator
```

## Implementation Status

### ✅ Completed Components

| Component | File | Description |
|-----------|------|-------------|
| Real-World Data Injector | `real_world_data_injector.py` | 15 real LeetCode problems, 5 GitHub issues, 3 StackOverflow questions, 5 FAANG interview questions |
| Enhanced Noise Layer | `noise_injection_layer.py` | 8 noise types: truncation, mixed language, formatting, context flooding, character corruption, semantic noise, **false evidence injection**, **evidence removal** |
| Cross-Domain Stressor | `cross_domain_stressor.py` | 6 domains: legal, medical, system design, business rules, academic, financial |
| Human-Crafted Attacks | `human_crafted_attacks.py` | 15 attacks including 5 new ones targeting identified blind spots |
| Mixed Batch Runner | `mixed_batch_runner.py` | Configurable internal/external ratios, distribution shift analysis, source comparison |
| Enhanced Evaluator | `enhanced_evaluator.py` | Robustness score, degradation curves, failure diversity, recovery rate |
| Stress Dashboard | `tests/run_stress_dashboard.py` | Comprehensive 7-section test report |

### Key Enhancements Made

#### 1. Real-World Data (vs. Synthetic)
- **Actual LeetCode problems** with verbatim descriptions from leetcode.com
- **Real GitHub issues** from tensorflow, cpython, react, kubernetes, vscode
- **Real StackOverflow questions** with contradictory top answers
- **Actual FAANG interview questions** (Google, Meta, Amazon, Netflix, Apple)

#### 2. Advanced Noise Types
The noise layer now includes **8 noise types**:
1. **Truncation** — cuts prompts mid-sentence
2. **Mixed Language** — inserts French fragments
3. **Formatting Destruction** — removes punctuation, newlines
4. **Context Flooding** — adds irrelevant system logs, error messages
5. **Character Corruption** — typos, swaps, deletions
6. **Semantic Noise** — contradictory statements
7. **False Evidence Injection** (NEW) — injects patterns that match Doctor's regex evidence extractors
8. **Evidence Removal** (NEW) — replaces key phrases with [REDACTED]

#### 3. Human-Crafted Attacks (15 total)
Original 10 + 5 new attacks targeting identified blind spots:
- `implicit_undefined` — Tests undefined detection without explicit "undecidable" language
- `correct_undercommitment` — Exploits Doctor's bias toward "partial" classification
- `implicit_contradiction` — Hidden contradictions that don't match regex patterns
- `performance_correctness_mix` — Confuses performance vs. correctness requirements
- `doctor_architecture_exploit` — Designed to fall through all R1-R5 rules to biased fallback

#### 4. Mixed Batch Testing
The MixedBatchRunner enables:
- **Configurable ratios** (0% to 100% internal vs external)
- **Distribution shift analysis** — gradual transition from internal to external
- **Source comparison** — side-by-side performance across sources
- **Noise sensitivity testing** — performance at each noise level

## Stress Test Results

### Overall Performance

| Metric | Value | Assessment |
|--------|-------|------------|
| Overall Accuracy | 47.69% | ⚠ CRITICAL (< 50%) |
| Robustness Score | 101.61% | ✓ Noise has no effect (structural failures) |
| Failure Diversity | 68.31% | ✓ Diverse failure patterns |
| Human Attack Success | 60.00% | 9/15 attacks passed |

### Distribution Shift Analysis

| Internal Ratio | External Ratio | Accuracy | Failures |
|----------------|----------------|----------|----------|
| 100% | 0% | 38.46% | 40/65 |
| 75% | 25% | 38.18% | 34/55 |
| 50% | 50% | 44.90% | 27/49 |
| 25% | 75% | 44.44% | 25/45 |
| 0% | 100% | 50.00% | 26/52 |

**Finding**: The Doctor actually performs **better** on external cases (50%) than 
internal cases (38.46%). This suggests the internal generator creates harder cases 
than real-world problems, OR the Doctor's training is misaligned with its own generator.

### Source Comparison

| Source | Accuracy | Failures | Overconfidence |
|--------|----------|----------|----------------|
| Internal Generator | 20.00% | 16/20 | 10.00% |
| Real-World | 60.00% | 8/20 | 0.00% |
| Cross-Domain | 60.00% | 8/20 | 0.00% |
| Human Attacks | 60.00% | 6/15 | 6.67% |

**Critical Finding**: The Doctor performs 3× better on external sources than internal 
generator cases. This is a major red flag indicating the generator and Doctor are 
misaligned.

### Human Attack Results

| Attack | Expected | Got | Status |
|--------|----------|-----|--------|
| multiple_interpretations_hard | undefined | partial | ✗ FAIL |
| self_referential_paradox | undefined | partial | ✗ FAIL |
| correct_undercommitment | correct | partial | ✗ FAIL |
| conflicting_meta_signals | undefined | partial | ✗ FAIL |
| implicit_undefined | undefined | partial | ✗ FAIL |
| doctor_architecture_exploit | partial | undefined | ✗ FAIL |
| evidence_exhaustion | partial | partial | ✓ PASS |
| probabilistic_reasoning | partial | partial | ✓ PASS |
| temporal_reasoning | partial | partial | ✓ PASS |
| implicit_contradiction | partial | partial | ✓ PASS |
| domain_mismatch | partial | partial | ✓ PASS |
| minimal_information | partial | partial | ✓ PASS |
| threshold_gaming | partial | partial | ✓ PASS |
| semantic_inversion | partial | partial | ✓ PASS |
| performance_correctness_mix | partial | partial | ✓ PASS |

**Failed Attacks Analysis**:
- 5/6 failures are **undefined → partial** misclassifications
- 1 failure is **partial → undefined** (overcautious)
- The `correct_undercommitment` attack succeeds: Doctor says "partial" for "correct"

### Failure Pattern Breakdown

| Pattern | Count | Percentage |
|---------|-------|------------|
| undercommitted_correct | 66 | 65.35% |
| missed_undefined | 33 | 32.67% |
| overclassified_undefined | 2 | 1.98% |

**Two dominant failure modes**:
1. **Undercommitment bias** (65%): Doctor classifies "correct" as "partial"
2. **Missing undefined detection** (33%): Doctor doesn't recognize implicit ambiguity

### Noise Sensitivity

| Noise Level | Accuracy | Noise Types Applied |
|-------------|----------|---------------------|
| 0% | 60.00% | — |
| 20% | 60.00% | context_flooding |
| 40% | 60.00% | context_flooding, evidence_removal |
| 60% | 60.00% | character_corruption, context_flooding |
| 80% | 60.00% | character_corruption, context_flooding |
| 100% | 60.00% | character_corruption, context_flooding, evidence_removal |

**Critical Finding**: Noise has **zero effect** on accuracy (60% constant). This means:
- Failures are **structural**, not noise-dependent
- The Doctor's reasoning is brittle regardless of input quality
- The noise types don't interfere with the Doctor's regex-based evidence extraction

## Root Cause Analysis

### Problem 1: Undercommitment Bias (65% of failures)
**Symptom**: Doctor classifies "correct" responses as "partial"

**Root Cause**: The `_classify()` fallback in `raw_prompt_doctor.py` defaults to 
`"partial", 0.51` at line `F0:uninformed_fallback`. When evidence scores are low 
(no strong signals either way), the Doctor defaults to "partial".

**Impact**: Any case without explicit evidence patterns gets classified as "partial", 
even if the response is genuinely correct.

### Problem 2: Missing Undefined Detection (33% of failures)
**Symptom**: Doctor doesn't recognize genuinely ambiguous/undefined cases

**Root Cause**: The only way to get "undefined" is R1 rule:
```python
if cs.undecidable_score >= UNDECIDABLE_THRESHOLD:
    return Resolution("undefined", ...)
```

But `undecidable_score` requires matching explicit regex patterns like:
- "prevents a single decidable target"
- "no single decidable target is possible"
- "logically undecidable"

Real-world ambiguity is **implicit**, not explicitly stated with these phrases.

**Impact**: Cases with genuine fundamental ambiguity (but without explicit "undecidable" 
language) are misclassified as "partial" or "correct".

### Problem 3: Internal/External Mismatch
**Symptom**: Doctor performs 3× worse on internal cases (20%) vs external (60%)

**Root Cause**: The internal generator creates cases with specific trap patterns 
(signal inversion, corrupted labels, contradictions) that don't match the Doctor's 
evidence extraction patterns. The Doctor was never trained on the generator's output.

**Impact**: The closed-loop system (generator → doctor → evaluator → generator) is 
not self-consistent. The generator and Doctor are operating under different assumptions.

## Recommendations

### Immediate Actions (Priority 1)

1. **Fix Undercommitment Bias**
   - Change fallback from `"partial", 0.51` to a more nuanced decision
   - Add a `"correct"` path in `_classify()` for cases with weak but consistent signals
   - Consider adding a confidence-based threshold: if no strong evidence either way, 
     return "correct" with low confidence

2. **Improve Undefined Detection**
   - Add evidence patterns for **implicit** ambiguity:
     - Missing tie-breaking mechanisms
     - Unspecified edge case handling
     - Contradictory requirements without resolution
   - Lower the `UNDECIDABLE_THRESHOLD` from 0.7 to ~0.5
   - Add a new rule (R6?) for detecting implicit undefined

3. **Align Generator with Doctor**
   - Ensure the generator's trap patterns match the Doctor's evidence extraction
   - Run the generator's output through the Doctor to verify alignment
   - Consider updating the generator to produce cases that trigger Doctor's evidence patterns

### Short-Term Improvements (Priority 2)

4. **Add More Real-World Data**
   - Scrape actual LeetCode discussion pages for ambiguous problems
   - Include real production bug reports with unclear specifications
   - Add API documentation with missing edge cases

5. **Enhance Noise to Actually Affect Doctor**
   - Current noise (formatting, character corruption) doesn't affect regex matching
   - Need **semantic** noise that:
     - Rewrites key phrases to avoid regex matches
     - Adds competing evidence patterns
     - Modifies the "PROPOSED RESPONSE" section to change signal strength

6. **Add Recovery Testing**
   - After failure, provide hints or additional context
   - Measure if Doctor can recover with guidance
   - Test consistency across multiple runs

### Long-Term Architecture (Priority 3)

7. **Implement Meta-Reasoning Layer**
   - Add a layer that reasons about the reasoning process itself
   - Detect when evidence is insufficient (not just absent, but fundamentally ambiguous)
   - Handle self-referential paradoxes and logical traps

8. **Create Adversarial Training Loop**
   - Use ESL failures to retrain/adjust the Doctor
   - Close the loop: ESL → Doctor failures → Doctor improvements → ESL re-test
   - Track progress over multiple iterations

9. **Build Visualization Dashboard**
   - Real-time degradation curve plotting
   - Failure pattern clustering
   - Source-by-source performance heatmaps
   - Historical trend analysis

## How to Run

### Quick Stress Test
```bash
F:\pythonProject\.venv1\Scripts\python.exe tests/run_external_stress_test.py
```

### Comprehensive Dashboard
```bash
F:\pythonProject\.venv1\Scripts\python.exe tests/run_stress_dashboard.py
```

### Programmatic Usage
```python
from doctor.raw_prompt_doctor import RawPromptDoctor
from external_stress_layer.mixed_batch_runner import MixedBatchRunner

doctor = RawPromptDoctor()
runner = MixedBatchRunner(doctor=doctor, seed=42)

# Mixed batch test
results = runner.run_mixed_test(
    internal_ratio=0.5,
    total_cases=100,
    noise_levels=[0.0, 0.2, 0.4, 0.6],
)
print(results.summary())

# Distribution shift analysis
shift = runner.run_distribution_shift_test(
    internal_ratios=[1.0, 0.75, 0.5, 0.25, 0.0],
)

# Source comparison
sources = runner.run_source_comparison_test(cases_per_source=30)
```

## File Structure

```
external_stress_layer/
├── __init__.py                      # Package exports and lazy imports
├── real_world_injector.py           # Original synthetic real-world injector
├── real_world_data_injector.py      # NEW: Actual LeetCode/GitHub/SO data
├── noise_injection_layer.py         # Enhanced with false evidence + evidence removal
├── cross_domain_stressor.py         # Legal, medical, business, etc.
├── human_crafted_attacks.py         # 15 attacks (10 original + 5 new)
├── enhanced_evaluator.py            # Robustness, degradation, diversity metrics
├── mixed_batch_runner.py            # NEW: Configurable internal/external mixing
└── orchestrator.py                  # Full pipeline orchestration

tests/
├── run_external_stress_test.py      # Original test script
└── run_stress_dashboard.py          # NEW: Comprehensive 7-section dashboard
```

## Next Steps

The ESL is now fully operational and providing actionable insights. The next critical 
step is **fixing the Doctor's two systemic biases**:

1. **Undercommitment bias** → Adjust fallback behavior in `_classify()`
2. **Missing undefined detection** → Add implicit ambiguity evidence patterns

Once these are fixed, re-run the ESL to measure improvement. The goal is:
- **Target accuracy**: > 70% on mixed batches (currently 47.69%)
- **Target robustness**: < 15% accuracy drop at 60% noise (currently 0% drop because failures are structural)
- **Target human attack success**: > 80% (currently 60%)

## Conclusion

The External Stress Layer has successfully broken the Doctor out of its synthetic cage. 
The results reveal that the Doctor is struggling with real-world ambiguity, failing 
nearly half of external cases. However, the failures are concentrated in just two 
patterns, indicating clear paths for improvement.

The ESL is now ready for iterative use:
1. Fix Doctor's biases
2. Re-run ESL tests
3. Measure improvement
4. Repeat until targets are met

This closes the loop from Stage 2 (adaptive internal adversary) to Stage 3 
(external validation with real-world stress).

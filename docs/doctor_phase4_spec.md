# Doctor Phase 4 Spec

## Design Invariant

**Doctor is a constraint-satisfaction system: decisions are enforced by satisfying explicit semantic constraints, not by classifying against a learned distribution.**

**Every architectural decision in Phase 4 must be tested against this property:**
1. **Deterministic** — same input always produces same output; no stochastic fallback
2. **Semantic representation** — decisions are grounded in extracted problem structure, not surface keywords
3. **Full causal traceability** — every failure mode has a traceable cause, not an unexplainable "close enough" accept
4. **Constraint-satisfaction framing** — matching requires all constraints (input_type, output_type, objective) to explicitly align, not just similarity

This invariant rejects:
- Learning components that introduce unexplainability before formal semantic model exists
- Heuristic debt without formal grounding (consolidated or not)
- OOD detection crowding out objective-level consistency enforcement
- Similarity-based matching without explicit constraint alignment

## Phase 4 Execution Order

**Critical: Calibration is relative to a domain definition. Boundary formalization must precede calibration or thresholds will encode accidental biases from Phase 3 data.**

1. **Adversarial baseline measurement** — Data acquisition, failure modes observed, no interpretation yet
2. **Boundary formalization** — Explicit policy: what is in-registry, what is a variant vs reject, equivalence classes written as formal rules
3. **Alignment signal validation** — Verify objective_match, constraint_consistency, structural_compatibility are monotonic indicators of correctness before trusting as calibration targets
4. **Calibration** — Now has stable domain definition and validated signals to fit against

Each phase gates the next. Do not proceed to calibration until boundary formalization is complete and signals are validated.

## Formal Decision Contract

**Accept ⇔ (no_contradiction) ∧ (objective_alignment ≥ T) ∧ (constraints_consistent) ∧ (structural_compatible)**

Where:
- `no_contradiction`: ¬∃(neg_keyword ∈ objective ∧ pos_keyword ∉ objective) for matched problem
- `objective_alignment ≥ T`: alignment_score ≥ 0.85 (T is tunable threshold)
- `constraints_consistent`: constraint_consistency ≥ 0.7
- `structural_compatible`: structural_compatibility ≥ 0.7

**Hard branch when json_repair is active:**
- `repair_active → require (alignment ≥ 0.90) ∧ (constraint_consistency ≥ 0.90) ∧ (structural_compatibility ≥ 0.90) OR force reject`
- This is not a recommendation — this is a hard branch in the decision logic
- Repaired output is not equivalent to clean parse; reduced trust requires elevated threshold

**Trace requirements:**
Every decision trace must contain:
- `decision_contract.conditions`: {no_contradiction, alignment_threshold_met, constraints_consistent, structural_compatible}
- `decision_contract.threshold_used`: value of T
- `decision_contract.repair_active`: boolean
- `decision_contract.accept_condition` OR `decision_contract.rejection_reason`

## Registry Boundary Definition

**Belongs in registry:**
- Problems with explicit algorithmic structure (sorting, searching, DP, graphs)
- Problems with canonical input/output contracts
- Problems with testable behavior

**Must reject:**
- Ad-hoc data processing (find duplicates, count occurrences)
- Domain-specific logic not captured by algorithmic pattern
- Problems requiring external knowledge or state

**Domain disguise is valid** if and only if:
1. Input structure maps to canonical type (array, string, tree, graph)
2. Output structure maps to canonical type (index, count, list, boolean)
3. Objective keyword matches a registry problem's core operation

## Signal Validation Gate

Before any sub-score is used as a decision threshold, it must pass validation:

**For each sub-score (objective_match, constraint_consistency, structural_compatibility):**
1. Run held-out test set (distinct from calibration set)
2. Measure monotonic correlation with correctness
3. If score is NOT monotonically increasing with probability of correct match → drop or redesign
4. If score passes validation → use as threshold input
5. If score fails validation → exclude from decision contract, document as diagnostic only

**Validation criteria:**
- Sub-score value should increase monotonically with P(correct match)
- Distribution separation between true positives and false positives must be measurable
- Score must not invert under adversarial formulation

## Calibration Status

**NOT YET ACHIEVED.** Alignment scores are currently qualitative LLM outputs, not calibrated metrics.

**Pre-requisites before calibration:**
1. Boundary formalization complete (domain definition stable)
2. Signal validation passed (all three sub-scores show monotonic correlation)
3. Adversarial baseline measured

**Calibration roadmap:**
1. Tune T (currently 0.85) against false_accept and matcher_miss rates on validated signals
2. Document calibrated thresholds as explicitly tunable parameters
3. Measure score distributions for true positives vs false positives post-calibration

## Scope

Phase 4 follows the single-call Phase 3 ingest flow. The goal is to reduce false accepts on ambiguous or out-of-distribution statements without reintroducing multi-step LLM chains.

## Phase 3 Empirical Findings

- `objective_overreach` confirmed as primary false-accept pattern — LLM accepts underspecified statements when a plausible registry match exists nearby. Mitigation: require explicit objective keyword match, not just structural alignment
- `coverage_gap` was the dominant rejection cause across batch 2 — 3 problems missing from registry (now resolved). Ongoing risk as user language diversifies beyond current 37-problem coverage
- `json_repair` triggered on user_16 — model output truncation is a real failure mode under rate pressure. Fix confirmed working with hard branch requiring 0.90 threshold on repaired inputs
- `rate_limit` is a first-class failure category, not `parser_fail` — update failure taxonomy schema to distinguish them
- Confidence scores non-informative throughout — `alignment_score` marked `diagnostic_only`, suppressed from user-facing output
- Registry expansion (climbing_stairs, coin_change, longest_substring) introduced new collision surfaces: knapsack-like vs coin_change, LCS vs LIS, substring vs subsequence
- False accept rate on completed cases: 1/18 (5.6%), true rate unknown and likely higher

### Failure Taxonomy (Updated)

| Tag | Description | Status |
|-----|-------------|--------|
| `objective_overreach` | LLM accepts underspecified statement | Confirmed (user_8) |
| `coverage_gap` | Statement not in registry | Confirmed, resolved |
| `json_repair` | Model output truncation | Confirmed, fixed with hard branch |
| `rate_limit` | Infrastructure noise | First-class category |
| `validation_leak` | Validation passed but match wrong | Ongoing risk |
| `false_accept` | Matched when should reject | 1/18 on completed (true rate unknown) |
| `matcher_miss` | Correct rejection | Expected behavior |

### Phase 3 Summary

- Valid completed cases: 18 (users 1-16 + adversarial baseline partial)
- Adversarial batch: 9/10 cases pending (rate limit blocked)
- False accept rate: 1/18 (5.6% on completed), true rate unknown
- Coverage gaps: 3 (now resolved)
- Parser failures: 0 (json_repair working)

## Phase 4 Items

### 1. Adversarial Baseline Measurement (First Task)

Run the adversarial batch (phase3_batch3.json) as the first act of Phase 4.

Requirements:
- Collect all 10 adversarial cases under fresh quota
- Observe failure modes without interpretation
- Do NOT calibrate against this data yet — it becomes the held-out validation set

### 2. Boundary Formalization

Write explicit policy for registry membership:

Requirements:
- Formal rules for what belongs in registry
- Formal rules for what must reject (equivalence classes)
- Explicit handling of domain disguise variants
- Collision surface mapping with mitigation rules

### 3. Alignment Signal Validation

Before using sub-scores as thresholds, validate them:

Requirements:
- Run held-out test set distinct from calibration set
- Measure monotonic correlation with correctness for each sub-score
- Drop or redesign scores that fail validation
- Document validated vs non-validated signals

### 4. Calibration (Post-validation)

After boundary formalization and signal validation complete:

Requirements:
- Tune thresholds against false_accept and matcher_miss rates
- Document calibrated thresholds as explicitly tunable parameters
- Measure separation between true positive and false positive distributions

### 5. Unified Validation (Core)

Keep validation in the same decision surface as the single-call analysis instead of adding a second sequential LLM step.

Requirements:
- Preserve one prompt in / one JSON out for the core parser + matcher path.
- Make ambiguity handling explicit in the decision contract.
- Implement formal decision contract: Accept iff all conditions met
- Implement repair-aware decision policy: `json_repair: true` → require 0.90 on all sub-scores OR reject
- Do not add a second accept/reject gate that can contradict the primary LLM decision.

Success criteria:
- Fewer false accepts on underspecified statements
- No regression back to parser/matcher disagreement or retry-chain complexity

### 6. OOD Detection via Embedding Distance

Add an embedding-based pre-filter before the single-call parser runs.

Purpose:
- Reject statements that are structurally far from every registry problem before expensive parsing/matching
- Improve domain-disguise robustness with an explicit, traceable distance signal

Proposed design:
- Compute and store an embedding per registry problem
- Embed the incoming user statement
- Compute cosine similarity or cosine distance against all registry embeddings
- Record:
  - nearest problem id
  - nearest similarity
  - distance margin to the next nearest candidate
- If the nearest distance is beyond a defined OOD threshold, reject early as out-of-distribution

Trace requirements:
- `ood_nearest_problem`
- `ood_similarity`
- `ood_margin`
- `ood_reject` boolean
- threshold value used for the decision

Constraints:
- Lightweight enough to preserve throughput
- Fully offline-precomputable for registry-side embeddings
- No multi-step LLM fallback chain

### 7. Retry Tracking & Observability

Track retry count as first-class telemetry for detecting provider instability.

Trace requirements:
- `retry_count`: total retries across LLM calls
- `provider`: which provider (groq, google)
- `first_attempt_success`: boolean

### 8. Reject Rate Monitoring

Track reject rate per batch to detect degradation.

Monitoring:
- `reject_rate`: rejected / total per batch
- `reject_rate_trend`: rolling average across batches
- Alert threshold: if reject_rate > 40% or < 10%, flag for review
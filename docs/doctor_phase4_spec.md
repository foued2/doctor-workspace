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

## Formal Decision Contract

**Accept ⇔ (no_contradiction) ∧ (objective_alignment ≥ T) ∧ (constraints_consistent) ∧ (structural_compatible)**

Where:
- `no_contradiction`: ¬∃(neg_keyword ∈ objective ∧ pos_keyword ∉ objective) for matched problem
- `objective_alignment ≥ T`: alignment_score ≥ 0.85 (T is tunable threshold)
- `constraints_consistent`: constraint_consistency ≥ 0.7
- `structural_compatible`: structural_compatibility ≥ 0.7

**Additional condition when json_repair is active:**
- `repair_active ∧ objective_alignment < T` → Force reject

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

## Calibration Status

**NOT YET ACHIEVED.** Alignment scores (objective_match, constraint_consistency, structural_compatibility) are currently qualitative LLM outputs, not calibrated metrics. Do not treat them as reliable quantitative thresholds until:
1. Empirical distribution of scores is measured across known match/reject sets
2. Threshold T is tuned against false_accept and matcher_miss rates
3. Score distributions for true positives vs false positives are separated

Phase 4 calibration roadmap:
1. Decompose alignment_score → objective_match + constraint_consistency + structural_compatibility
2. Run calibration batch with 50+ known match/reject cases
3. Tune T to minimize false_accept + matcher_miss jointly
4. Measure separation between true positive and false positive score distributions

## Scope

Phase 4 follows the single-call Phase 3 ingest flow. The goal is to reduce false accepts on ambiguous or out-of-distribution statements without reintroducing multi-step LLM chains.

## Phase 3 Empirical Findings

- `objective_overreach` confirmed as primary false-accept pattern — LLM accepts underspecified statements when a plausible registry match exists nearby. Mitigation: require explicit objective keyword match, not just structural alignment
- `coverage_gap` was the dominant rejection cause across batch 2 — 3 problems missing from registry (now resolved). Ongoing risk as user language diversifies beyond current 37-problem coverage
- `json_repair` triggered on user_16 — model output truncation is a real failure mode under rate pressure. Fix confirmed working. When `json_repair: true`, set `decision_confidence: "reduced"` and bias toward reject if alignment confidence < 0.85
- `rate_limit` is a first-class failure category, not `parser_fail` — update failure taxonomy schema to distinguish them
- Confidence scores non-informative throughout — `alignment_score` marked `diagnostic_only`, suppressed from user-facing output
- Registry expansion (climbing_stairs, coin_change, longest_substring) introduced new collision surfaces: knapsack-like vs coin_change, LCS vs LIS, substring vs subsequence

### Failure Taxonomy (Updated)

| Tag | Description | Status |
|-----|-------------|--------|
| `objective_overreach` | LLM accepts underspecified statement | Confirmed (user_8) |
| `coverage_gap` | Statement not in registry | Confirmed, resolved |
| `json_repair` | Model output truncation | Confirmed, fixed |
| `rate_limit` | Infrastructure noise | First-class category |
| `validation_leak` | Validation passed but match wrong | Ongoing risk |
| `false_accept` | Matched when should reject | 1/12 valid cases |
| `matcher_miss` | Correct rejection | Expected behavior |

### Phase 3 Summary

- Valid completed cases: 16 (users 1-16, 17-20 pending rerun)
- False accept rate: 1/12 (8.3%)
- Coverage gaps: 3 (now resolved)
- Parser failures: 0 (json_repair working)

## Phase 4 Items

### 1. Unified Validation (Core)

Keep validation in the same decision surface as the single-call analysis instead of adding a second sequential LLM step.

Requirements:
- Preserve one prompt in / one JSON out for the core parser + matcher path.
- Make ambiguity handling explicit in the decision contract.
- Implement formal decision contract: Accept iff all conditions met
- Add traceable failure taxonomy for:
  - `objective_overreach`
  - `underspecified_objective`
  - `validation_reject`
- Do not add a second accept/reject gate that can contradict the primary LLM decision.
- Implement repair-aware decision policy: `json_repair: true` + alignment < 0.85 → force reject

Success criteria:
- Fewer false accepts on underspecified statements
- No regression back to parser/matcher disagreement or retry-chain complexity

### 2. OOD Detection via Embedding Distance

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

Open questions:
- embedding provider and cost
- threshold calibration on known match / reject sets
- whether OOD should be a hard reject or an advisory signal during rollout

### 3. Retry Tracking & Observability

Track retry count as first-class telemetry for detecting provider instability.

Trace requirements:
- `retry_count`: total retries across LLM calls
- `provider`: which provider (groq, google)
- `first_attempt_success`: boolean

Add to Phase 4 observability dashboard.

### 4. Reject Rate Monitoring

Track reject rate per batch to detect degradation.

Add monitoring:
- `reject_rate`: rejected / total per batch
- `reject_rate_trend`: rolling average across batches
- Alert threshold: if reject_rate > 40% or < 10%, flag for review

### 5. Alignment Score Calibration

**Status: Not yet achieved**

Currently alignment decomposition produces qualitative scores. Phase 4 must calibrate:

Design:
- Run calibration batch with 50+ known match/reject cases
- Measure score distributions for true positives vs false positives
- Tune T (currently 0.85) to minimize joint error rate
- Document calibrated thresholds as tunable parameters

### 6. Collision Surface Mapping

Registry expansion introduced new collision surfaces. Document them:

| Surface | Problem A | Problem B | Mitigation |
|---------|-----------|-----------|------------|
| knapsack-like | coin_change | 0-1 knapsack | Require explicit "unlimited"/"single use" |
| LCS vs LIS | longest_common_subsequence | longest_increasing_subsequence | Require "common" or "increasing" keyword |
| substring vs subsequence | longest_substring | longest_increasing_subsequence | Require "contiguous" or "subsequence" |
| product vs sum | max_subarray | max_product | Require "sum" keyword for max_subarray |

Phase 4 should add explicit keyword requirements for these surfaces.
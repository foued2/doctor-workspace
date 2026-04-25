# Doctor Phase 4 Spec

## Design Invariant

**Doctor is a deterministic decision enforcement system over a structured semantic representation, with full causal traceability of failure modes.**

Every architectural decision in Phase 4 must be tested against this property:
1. **Deterministic** — same input always produces same output; no stochastic fallback
2. **Semantic representation** — decisions are grounded in extracted problem structure, not surface keywords
3. **Full causal traceability** — every failure mode has a traceable cause, not an unexplainable "close enough" accept

This invariant rejects:
- Learning components that introduce unexplainability before formal semantic model exists
- Heuristic debt without formal grounding (consolidated or not)
- OOD detection crowding out objective-level consistency enforcement

## Scope

Phase 4 follows the single-call Phase 3 ingest flow. The goal is to reduce false accepts on ambiguous or out-of-distribution statements without reintroducing multi-step LLM chains.

## Phase 3 Empirical Findings

- `objective_overreach` confirmed as primary false-accept pattern — LLM accepts underspecified statements when a plausible registry match exists nearby. Mitigation: require explicit objective keyword match, not just structural alignment
- `coverage_gap` was the dominant rejection cause across batch 2 — 3 problems missing from registry (now resolved). Ongoing risk as user language diversifies beyond current 37-problem coverage
- `json_repair` triggered on user_16 — model output truncation is a real failure mode under rate pressure. Fix confirmed working
- `rate_limit` is a first-class failure category, not `parser_fail` — update failure taxonomy schema to distinguish them
- Confidence scores non-informative throughout — `alignment_score` marked `diagnostic_only`, suppressed from user-facing output

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

- Valid completed cases: 12 (users 1-16, excluding rate-limited 17-20)
- False accept rate: 1/12 (8.3%)
- Coverage gaps: 3 (now resolved)
- Parser failures: 0 (json_repair working)

## Phase 4 Items

### 1. Unified Validation

Keep validation in the same decision surface as the single-call analysis instead of adding a second sequential LLM step.

Requirements:
- Preserve one prompt in / one JSON out for the core parser + matcher path.
- Make ambiguity handling explicit in the decision contract.
- Add traceable failure taxonomy for:
  - `objective_overreach`
  - `underspecified_objective`
  - `validation_reject`
- Do not add a second accept/reject gate that can contradict the primary LLM decision.

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
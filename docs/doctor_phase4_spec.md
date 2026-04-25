# Doctor Phase 4 Spec

## Scope

Phase 4 follows the single-call Phase 3 ingest flow. The goal is to reduce false accepts on ambiguous or out-of-distribution statements without reintroducing multi-step LLM chains.

## Inputs from Phase 3

- Single-call parser + matcher is live.
- Phase 3 Batch 1 exposed one confirmed false accept:
  - `user_8`: ambiguous statement accepted as `longest_common_prefix`
  - root cause: `objective_overreach`
- Domain disguise remains the weakest stress point from Phase 2.

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

## Phase 3 Note

Phase 3 runs first. Phase 4 is a follow-on hardening pass, not a blocker for current production evaluation.

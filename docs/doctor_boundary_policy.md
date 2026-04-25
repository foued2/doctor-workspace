# Doctor Boundary Policy

**Purpose:** Define explicit rules for registry membership and rejection. This document is the anchor for boundary formalization in Phase 4. All decisions must trace to a rule in this document.

**Principle:** Domain disguise is valid if and only if the computational structure matches exactly. The domain framing (shopping, temperatures, finance) is irrelevant. Only the algorithmic structure matters.

---

## Interpretation Policy

**Philosophy:** Doctor operates under guided interpretation, not strict semantic determinism.

- Common-usage equivalents of technical terms are accepted when the computational structure is unambiguous ("increasing sequence" → LIS)
- Genuinely ambiguous statements with no clear computational structure → reject
- The distinction between "resolvable" and "unresolvable" ambiguity is a judgment call encoded in boundary decisions, not an automatic gate

**Examples of accepted common-usage equivalents:**
- "increasing sequence" = "increasing subsequence" (LIS)
- "stretch" = "subarray" when contiguous implied
- "balance" = "valid" for bracket matching
- "merge" = "combine" for sorted list merging

**Examples of unresolvable ambiguity → reject:**
- "find the longest subsequence" without "increasing" — subsequence is ambiguous without order constraint
- "maximize the subarray" without sum/product specification — objective unconstrained
- "sort and find common prefix" — operation chain not mapping to single problem

---

## Explicit Inclusions

### two_sum
- **IN** — find two numbers that sum to target
- Reason: canonical array + target pair problem with exact solution structure

### valid_parentheses  
- **IN** — check if brackets/parentheses are balanced
- Reason: stack-based matching with LIFO semantics

### max_subarray
- **IN** — find maximum sum of contiguous subarray
- Reason: requires explicit "sum" keyword; "product" variant is a different problem
- **OUT variant:** max product of subarray — different algorithmic structure (sign flip handling)

### longest_increasing_subsequence
- **IN** — strictly increasing subsequence
- Reason: requires explicit "increasing" or "strictly increasing" keyword
- **OUT variant:** non-decreasing subsequence — requires LIS variant problem
- **OUT variant:** common subsequence — LCS problem, not LIS

### merge_two_sorted_lists
- **IN** — merge two sorted lists/arrays into one sorted
- Reason: merge operation with deterministic ordering

### climbing_stairs
- **IN** — count ways to reach top given 1 or 2 step moves
- Reason: Fibonacci-like DP with exact move set {1, 2}
- **OUT variant:** with 3-step option — needs extended problem or reject
- **OUT variant:** with cost/weight — different problem (min cost climbing)
- **OUT variant:** domino tiling — structurally equivalent but requires explicit mapping

### coin_change
- **IN** — minimum coins needed (unlimited supply)
- Reason: requires explicit "minimum" or "fewest" + "coins" keywords
- **OUT variant:** count ways to make amount — different problem (coin combinations)
- **OUT variant:** 0-1 knapsack — requires "each item once" or "0-1" explicit

### longest_substring_without_repeating_characters
- **IN** — longest substring without repeating characters (contiguous)
- Reason: requires "substring" keyword + "no repeat" constraint
- **OUT variant:** longest subsequence without repeating — non-contiguous, different problem
- **OUT variant:** find all duplicate characters — ad-hoc processing, not algorithmic

---

## Explicit Exclusions

### Must Reject

| Problem Type | Reason |
|--------------|--------|
| Find duplicate characters in string | Ad-hoc string processing, no canonical algorithmic pattern |
| Find all characters appearing more than N times | Ad-hoc counting, not in registry scope |
| Rotated sorted array search | Rotated binary search not in registry |
| Shortest word containing all given substrings | Domain-specific word manipulation |
| Tiling a 2xn board | Requires explicit mapping to climbing_stairs structure |
| Maximum product of subarray | Product not sum — different problem |
| Count operations to convert strings | Edit distance, requires explicit alignment problem |
| Longest common subsequence | LCS not LIS — different algorithmic structure |

---

## Collision Surfaces

### Product vs Sum (max_subarray)
- **Rule:** "Maximum product" or "maximum product of subarray" → OUT
- **Rule:** "Maximum sum" or "maximum sum of contiguous subarray" → IN
- **Rule:** Ambiguous "maximum subarray" → OUT (requires explicit sum keyword)

### LCS vs LIS
- **Rule:** "Longest common subsequence" or "LCS" → OUT (not in registry)
- **Rule:** "Longest increasing subsequence" or "strictly increasing" → IN
- **Rule:** "Longest subsequence" without "increasing" → OUT

### Substring vs Subsequence
- **Rule:** "Substring" (contiguous) → check for no-repeat pattern → IN
- **Rule:** "Subsequence" (non-contiguous) → OUT unless "increasing" present → LIS
- **Rule:** "Longest stretch" ambiguous → check if contiguous implied

### Coin-related
- **Rule:** "Minimum coins" + "unlimited" → coin_change IN
- **Rule:** "Count ways" + "coins" → coin_combinations OUT
- **Rule:** "Knapsack" or "0-1" → 0-1_knapsack OUT
- **Rule:** "Items with weight and value" → knapsack OUT

### Stairs-related
- **Rule:** "Climb n stairs" + "1 or 2 steps" → climbing_stairs IN
- **Rule:** "Climb n stairs" + "cost" or "price" → min_cost_climbing OUT
- **Rule:** "Climb n stairs" + "3 steps" option → reject (not standard)
- **Rule:** "Tile 2xn board" → reject unless explicit climbing_stairs mapping

---

## Domain Disguise Rules

Domain disguise is valid when:

1. Input structure maps to canonical type (array, string, list)
2. Output structure maps to canonical type (index, count, list, boolean)
3. Objective keyword matches registry problem's core operation

**Examples of VALID domain disguise:**
- "Given a month of daily temperatures, find longest stretch where temps kept going up" → LIS (array input, count output, "increasing" implied)
- "Find most profitable contiguous period in list of daily profits/losses" → max_subarray (array input, sum output, "contiguous" + "profitable" maps to max)

**Examples of INVALID domain disguise:**
- "I have a shopping list and need two items that match my budget" → two_sum (actually valid — matches structure exactly)
- "Given daily stock prices, find longest consecutive days of increase" → LIS (valid disguise)

---

## JSON Repair Policy

When `json_repair: true` is active:

**Rule:** Repaired input → require 0.90 on ALL THREE sub-scores (alignment, constraint_consistency, structural_compatibility) OR force reject

- **Not:** equal treatment as clean parse
- **Not:** blanket reject all repaired inputs
- **Not:** only alignment threshold
- **Yes:** elevated threshold across all signals

---

## Decision Trace Requirements

Every reject must log:
- `rejection_reason`: specific rule from this policy that triggered reject
- `boundary_policy_version`: version of this document
- `rule_cited`: which rule from this document applied

Every accept must log:
- `rule_cited`: which inclusion rule applied
- `collision_surface_checked`: which collision surfaces were evaluated
- `domain_disguise_valid`: boolean

---

## Version

v1.1 — Added interpretation policy section, stress expansion agenda

Rules derived from Phase 3 empirical observations:
- user_8: "sort and find what they start with" → LCP (incorrect accept, rule added)
- user_6: "longest subsequence" without increasing → OUT (added)
- user_7: temperatures → LIS (valid disguise, added)
- user_9: "maximum product" → OUT (product vs sum collision, added)
- users 11-13: climbing_stairs, coin_change, longest_substring → now IN (coverage gaps resolved)
- adversarial_4: "consecutive increases" → NOT LIS (sliding window, not subsequence)
- adversarial_6: "increasing sequence" → LIS (common-usage equivalence, documented)

---

## Phase 4 Stress Expansion Agenda

Target the collision surfaces that produce variant explosions:

### Variant Explosions (coin_change variants)
- "minimum coins" → coin_change (IN)
- "count ways to make amount" → coin_combinations (OUT, not in registry)
- "minimum coins with bounded supply" → partially specified, requires clarification
- "minimum coins with cost per coin" → cost variant, not standard

### Objective Mutations (same structure, different objectives)
- "find IF any two sum to target" → exists variant (OUT)
- "find COUNT of pairs summing to target" → count variant (OUT)
- "find MAX pair sum" → max variant (OUT)
- All have identical input/output but different computational goal

### Mixed Constraints (partial specification)
- "find two numbers that sum to target in sorted array" → extra constraint doesn't change problem
- "find max subarray with at least K elements" → constraint variant
- "find LIS of length at least K" → constraint variant

These become Phase 4 batch 1 test cases for boundary stress testing.

---

## Contract Minimality Test (Pre-Phase 4 Code)

**5-case manual test:** Derive expected decision from formal contract expression, compare to actual output. Any mismatch indicates hidden branches in contract.

Cases:
1. "find two numbers that add up to X" → expected accept (two_sum)
2. "find the longest stretch of consecutive increases" → expected reject (not subsequence)
3. "count minimum coins for amount" → expected accept (coin_change)
4. "find duplicate characters in string" → expected reject (ad-hoc processing)
5. "how many ways to climb n stairs" → expected accept (climbing_stairs)

Run these through Doctor. If any output deviates from expected, the formal decision contract has undeclared branches.
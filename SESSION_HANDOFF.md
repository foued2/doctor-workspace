**Session close: April 25, 2026**

**Branch:** phase2-perturbation

**Registry:** 37 problems

**Phase status:**
- Phase 1: closed (8/8)
- Phase 2: closed (94% conditional)
- Phase 3: closed (28 cases, 1 false accept, adversarial 10/10)
- Phase 4: in progress — batch 1 (12/12), batch 2 atomic (10/10), batch 3 (11/12), batch 3 FIXED

**Batch 3 score: 11/12 (91.7%)**

**Full Phase 4 so far: 33/34 (97.1%)**

---

**Batch 3 detailed:**
- Long-tail semantic drift (p4b3_01-03): 3/3 reject ✓
- Unseen phrasing (p4b3_04-06): 3/3 accept ✓
- Multi-constraint conflicts (p4b3_07-09, 11): 4/4 reject ✓
- Compositional/modifier (p4b3_10, 12): 1/2 — FAIL p4b3_10

---

**FAIL: p4b3_10 — "ignore spaces" false accept**

This is NOT a threshold problem. It's a parser/norm layer gap:
- "ignore spaces" modifies the problem structure
- Should be extracted as explicit constraint flag
- Currently absorbed into normalization → treated as minor variation

**Fix required (do NOT implement threshold yet):**
1. Extract structural modifiers ("ignore X", "except X", "only X") as constraint flags
2. Evaluate against registry definition, not normalization
3. Measure recall impact before changing threshold

---

**Three architectural questions — to answer before final decision contract:**

1. Is constraint_consistency authoritative or advisory?
2. What is evaluated before vs after normalization?
3. Is multi-constraint inconsistency pairwise or global set?

---

**Next session (in order):**
1. Fix modifier extraction in normalization layer — DONE (structural_modifier check added)
2. Measure recall cost of any threshold change
3. Answer the three architectural questions in writing
4. THEN write final decision contract

**Provider:** OpenRouter, deepseek/deepseek-v4-flash
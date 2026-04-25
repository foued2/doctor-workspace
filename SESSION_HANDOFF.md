**Session close: April 25, 2026**

**Branch:** phase2-perturbation

**Registry:** 37 problems

**Phase status:**
- Phase 1: closed (8/8)
- Phase 2: closed (94% conditional)
- Phase 3: closed (28 cases, 1 false accept, adversarial 10/10)
- Phase 4: in progress — batch 1 (12/12), batch 2 atomic (10/10), batch 3 (11/12)

**Batch 3 results:**
- Long-tail semantic drift: 3/3 reject (optimal, best, efficient)
- Unseen phrasing: 3/3 accept (valid_parentheses, coin_change, merge_two_sorted_lists)
- Multi-constraint conflicts: 4/4 reject (jointly inconsistent constraints caught correctly)
- Compositional ambiguity: 1/2 reject (p4b3_12), 1 FAIL (p4b3_10: "ignore spaces" accepted)

**Score: 11/12 (91.7%)**

**Key finding: Multi-constraint gap CONFIRMED but nuanced:**
- constraint_consistency = 0.0 → reject (p4b3_07-09)
- constraint_consistency = 0.2 → reject (p4b3_11)  
- constraint_consistency = 0.8 → ACCEPT (p4b3_10) — FALSE POSITIVE
- Gap: constraint_consistency needs min threshold for accept (e.g., ≥ 0.9)

**Next session: Final decision contract + constraint threshold fix**

**Provider:** OpenRouter, deepseek/deepseek-v4-flash
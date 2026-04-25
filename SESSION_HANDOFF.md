**Session close: April 25, 2026**

**Branch:** phase2-perturbation

**Registry:** 37 problems

**Phase status:**
- Phase 1: closed (8/8)
- Phase 2: closed (94% conditional)
- Phase 3: closed (28 cases, 1 false accept, adversarial 10/10)
- Phase 4: in progress — batch 1 (12/12), batch 2 atomic (10/10)

**Next session opens with:**
Phase 4 batch 3 — adversarial generalization sweep. Cases to cover: unseen phrasing variants, long-tail semantic drift ("optimal", "best", "sequence"), multi-constraint conflicts. Then final decision contract — every branch explicit, no implicit behavior.

**Key architectural decisions locked:**
- Atomic evaluation only — batch mode retired as calibration tool
- Objective canonicalization layer active
- constraint_consistency_violation taxonomy (not contradiction)
- json_repair → alignment ≥ 0.90 required or reject
- Gates validated: LLM-first, gates authoritative on override

**Provider:** OpenRouter, deepseek/deepseek-v4-flash

**Open question for next session:** Does constraint enforcement generalize to multi-constraint conflicts, or only single-constraint violations?
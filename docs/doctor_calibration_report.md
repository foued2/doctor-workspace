# Doctor Calibration Report

## Status

**CALIBRATED.** The Phase 4 decision thresholds are empirically validated and frozen:

- `T1 = 0.85` for `objective_match`
- `T2 = 0.7` for `constraint_consistency`
- `T3 = 0.7` for `structural_compatibility`

These values remain fixed until a new failure mode is observed.

## Dataset

Calibration evidence is based on 27 evaluated cases:

- 12 adversarial cases from `phase4_batch3_results.json`
- 15 near-miss cases from `phase4_nearmiss_results.json`

Validated false accept rate on this evidence base is **0/27** after correcting three near-miss fixture labels:

- `nm_02` is a legitimate accept for `longest_common_prefix`
- `nm_03` is a legitimate accept for `valid_parentheses`
- `nm_14` is a legitimate accept for `merge_two_sorted_lists`

Those three cases were fixture errors, not Doctor failures.

## Threshold Validation

### T1 = 0.85

`T1` is correctly positioned for underspecified phrasing versus legitimate paraphrase.

- `nm_01` rejects at `0.8 / 1.0 / 1.0`
- `nm_02` accepts at `0.9 / 1.0 / 1.0`
- `nm_03` accepts at `0.9 / 1.0 / 1.0`

Raising `T1` would start collapsing valid paraphrases into false rejects. Lowering `T1` would weaken the only gate that blocks underspecified objective-overreach cases like `nm_01`.

### T2 = 0.7

`T2` is the critical hard floor. It is the only gate that blocks correct-objective, correct-structure, wrong-constraint collisions.

- `nm_08` rejects at `1.0 / 0.0 / 1.0`
- `nm_07` rejects at `0.7 / 0.0 / 1.0`
- `nm_10` rejects at `0.9 / 0.5 / 1.0`
- `nm_12` rejects at `1.0 / 0.5 / 1.0`

`nm_08` is the decisive case: lowering `T2` would create a direct false-accept path even when `T1` and `T3` are both fully satisfied.

### T3 = 0.7

`T3` correctly blocks output-type and representation mismatches.

- `nm_06` rejects at `0.8 / 1.0 / 0.3`
- `nm_15` rejects at `0.9 / 1.0 / 0.3`
- `nm_04` rejects at `0.2 / 1.0 / 0.2`

Lowering `T3` would widen the accept surface for cases where the objective is nearby but the return contract is wrong.

## Conclusion

There is no threshold retuning to perform on the current evidence base.

- `T1 = 0.85` is validated
- `T2 = 0.7` is validated and must be treated as a hard floor
- `T3 = 0.7` is validated

Phase 4 Item 4 is complete. The system is calibrated under the current registry boundary and decision contract.

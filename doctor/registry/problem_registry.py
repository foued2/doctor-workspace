"""
Problem Registry — Source of truth for all Doctor problems.

Schema (3 layers):
  spec     — problem definition (name, display_name, constraints)
  execution — test cases
  normalization — function name mapping

Registry is stored as JSON on disk, loaded into Python at runtime.
Both test_executor.py and solution_normalizer.py import from here.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

REGISTRY_PATH = Path(__file__).parent / "problem_registry.json"

_PROBLEMS: Optional[Dict[str, dict]] = None


def get_problems() -> Dict[str, dict]:
    global _PROBLEMS
    if _PROBLEMS is None:
        _PROBLEMS = _load_registry()
    return _PROBLEMS


def _load_registry(validate: bool = True) -> Dict[str, dict]:
    if not REGISTRY_PATH.exists():
        return {}
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        data: Dict[str, dict] = json.load(f)
    if validate:
        errors = _validate_registry_data(data)
        if errors:
            raise ValueError(
                f"Registry validation failed on load ({len(errors)} error(s)):\n" +
                "\n".join(f"  - {e}" for e in errors[:10])
            )
    return data


def _validate_registry_data(data: Dict[str, dict]) -> List[str]:
    errors = []
    for key, entry in data.items():
        entry_errors = validate_entry(entry)
        for e in entry_errors:
            errors.append(f"[{key}] {e}")
    return errors


def reload():
    global _PROBLEMS
    _PROBLEMS = _load_registry()


def get_problem(key: str) -> Optional[dict]:
    return get_problems().get(key)


def get_all_keys() -> List[str]:
    return list(get_problems().keys())


# ===========================================================================
# Schema definitions (for validation)
# ===========================================================================

REQUIRED_SPEC_FIELDS = ["problem_id", "display_name", "constraints"]
REQUIRED_EXECUTION_FIELDS = ["test_cases"]
REQUIRED_NORMALIZATION_FIELDS = ["function_names"]
REQUIRED_TEST_CASE_FIELDS = ["input", "expected", "label"]


def validate_entry(entry: dict) -> List[str]:
    errors = []
    spec = entry.get("spec", {})
    execution = entry.get("execution", {})
    normalization = entry.get("normalization", {})

    for field_name in REQUIRED_SPEC_FIELDS:
        if field_name not in spec or spec[field_name] is None:
            errors.append(f"spec.{field_name}: required")

    for field_name in REQUIRED_EXECUTION_FIELDS:
        if field_name not in execution:
            errors.append(f"execution.{field_name}: required")

    for field_name in REQUIRED_NORMALIZATION_FIELDS:
        if field_name not in normalization:
            errors.append(f"normalization.{field_name}: required")

    test_cases = execution.get("test_cases", [])
    if not isinstance(test_cases, list):
        errors.append("execution.test_cases: must be a list")
    elif len(test_cases) < 3:
        errors.append(f"execution.test_cases: need at least 3, got {len(test_cases)}")

    seen_labels = set()
    for i, tc in enumerate(test_cases):
        if not isinstance(tc, dict):
            errors.append(f"execution.test_cases[{i}]: must be a dict")
            continue
        for field_name in REQUIRED_TEST_CASE_FIELDS:
            if field_name not in tc:
                errors.append(f"execution.test_cases[{i}].{field_name}: required")
        label = tc.get("label", "")
        if not label:
            errors.append(f"execution.test_cases[{i}]: label cannot be empty")
        if label in seen_labels:
            errors.append(f"execution.test_cases[{i}]: duplicate label '{label}'")
        seen_labels.add(label)

        if "source" not in tc:
            errors.append(f"execution.test_cases[{i}]: source field required (manual|generated|boundary)")

    func_names = normalization.get("function_names", [])
    if not isinstance(func_names, list) or len(func_names) == 0:
        errors.append("normalization.function_names: must be a non-empty list")

    if spec.get("difficulty") and spec["difficulty"] not in ("easy", "medium", "hard"):
        errors.append(f"spec.difficulty: must be easy|medium|hard, got '{spec['difficulty']}'")

    return errors


def validate_structural_diversity(execution: dict) -> List[str]:
    errors = []
    test_cases = execution.get("test_cases", [])
    if len(test_cases) < 3:
        return errors

    all_numeric_values: list = []
    seen_inputs: set = set()
    all_input_reprs: list = []

    boundary_hints = {"empty", "zero", "single", "min_", "max_", "boundary",
                      "overflow", "first_empty", "both_empty", "one_empty"}
    has_boundary = any(
        any(w in tc.get("label", "").lower() for w in boundary_hints)
        for tc in test_cases
    )

    for tc in test_cases:
        inp = tc.get("input", ())
        inp_repr = str(inp)
        all_input_reprs.append(inp_repr)
        seen_inputs.add(inp_repr)

        for val in _flatten(inp):
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                all_numeric_values.append(val)

    if len(seen_inputs) < len(test_cases):
        dupes = len(test_cases) - len(seen_inputs)
        errors.append(f"structural_diversity: {dupes} duplicate input(s) — all test cases must be unique")

    if all_numeric_values:
        num_unique = len(set(all_numeric_values))
        if num_unique < 2:
            errors.append("structural_diversity: numeric inputs lack value variance — need different values")

    if not has_boundary:
        errors.append("structural_diversity: no edge/boundary test cases detected — add at least one labeled edge case")

    return errors


def validate_determinism(test_cases: List[dict]) -> List[str]:
    errors = []
    allowed = (int, float, bool, str, type(None))
    for i, tc in enumerate(test_cases):
        t = type(tc.get("expected"))
        if t not in allowed and not (t is list and all(type(x) in allowed for x in tc.get("expected", []))):
            errors.append(f"test_cases[{i}].expected: non-deterministic type {t.__name__} — expected must be int|float|bool|str|None|list")
    return errors


def validate_registry_on_load() -> List[str]:
    if not REGISTRY_PATH.exists():
        return []
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return _validate_registry_data(data)


def _flatten(obj):
    if isinstance(obj, (list, tuple)):
        for item in obj:
            yield from _flatten(item)
    else:
        yield obj


# ===========================================================================
# Write helpers (transactional)
# ===========================================================================

def _atomic_write(path: Path, data: dict):
    tmp = path.with_suffix(".tmp.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(path)


def add_problem(key: str, entry: dict) -> List[str]:
    problems = _load_registry(validate=False)
    if key in problems:
        return [f"problem '{key}' already exists — use replace or remove first"]
    problems[key] = entry
    _atomic_write(REGISTRY_PATH, problems)
    reload()
    return []


def replace_problem(key: str, entry: dict) -> List[str]:
    problems = _load_registry(validate=False)
    problems[key] = entry
    _atomic_write(REGISTRY_PATH, problems)
    reload()
    return []


def remove_problem(key: str) -> List[str]:
    problems = _load_registry(validate=False)
    if key not in problems:
        return [f"problem '{key}' not found"]
    del problems[key]
    _atomic_write(REGISTRY_PATH, problems)
    reload()
    return []


# ===========================================================================
# Convenience accessors (used by test_executor / solution_normalizer)
# ===========================================================================

def get_test_cases(key: str) -> Optional[List[dict]]:
    entry = get_problem(key)
    if entry is None:
        return None
    return entry.get("execution", {}).get("test_cases", [])


def get_function_names(key: str) -> Optional[List[str]]:
    entry = get_problem(key)
    if entry is None:
        return None
    return entry.get("normalization", {}).get("function_names", [])


def get_display_name(key: str) -> Optional[str]:
    entry = get_problem(key)
    if entry is None:
        return None
    return entry.get("spec", {}).get("display_name")


def get_all_display_names() -> Dict[str, str]:
    problems = get_problems()
    return {
        v.get("spec", {}).get("display_name", ""): k
        for k, v in problems.items()
        if v.get("spec", {}).get("display_name")
    }


def is_order_sensitive(key: str) -> bool:
    """Return True if problem arguments must not be reordered in perturbation check."""
    entry = get_problem(key)
    if entry is None:
        return True
    return entry.get("spec", {}).get("order_sensitive", True)

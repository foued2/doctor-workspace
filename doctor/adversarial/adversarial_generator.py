"""
Doctor Adversarial Generator — Test generation based on problem structure.

Design constraints (strict):
  - Generator NEVER learns from pass/fail outcomes
  - Tests are based on problem type + known failure patterns
  - No feedback from mutation results back to generation
  - Output diversity is structural, not correctness-based

Test generation strategies:
  1. Boundary analysis — extremal values for input types
  2. Known failure class injection — common off-by-one, type confusion patterns
  3. Symmetry exploitation — tests that should produce same/different outputs
  4. Structural inversion — inputs where correct and wrong solutions diverge
  5. Distribution stress — extreme scales, empty/minimal inputs

Each strategy outputs candidate test cases. The mutation engine then
determines which ones actually distinguish correct from incorrect solutions.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class AdversarialTestCase:
    input_data: Any
    expected: Any
    label: str
    source: str  # always "adversarial_generated"
    strategy: str
    description: str


def _hash_seed(problem_id: str, label: str) -> int:
    import hashlib
    seed_str = f"{problem_id}:adversarial:{label}"
    return int(hashlib.sha256(seed_str.encode()).hexdigest()[:8], 16)


class AdversarialGenerator:
    """
    Generates adversarial test cases based on problem structure.

    Each generator strategy analyzes the problem's known characteristics
    and produces test cases targeting known failure patterns.

    NEVER receives or uses: pass/fail outcomes, mutation results, E values.
    """

    def __init__(self, problem_id: str, problem_signature: str, difficulty: str = "medium"):
        self.problem_id = problem_id
        self.signature = problem_signature
        self.difficulty = difficulty

    def generate(self) -> List[AdversarialTestCase]:
        """Generate adversarial test cases using all applicable strategies."""
        candidates: List[AdversarialTestCase] = []

        for strategy_fn in STRATEGIES:
            try:
                results = strategy_fn(self)
                if results:
                    candidates.extend(results)
            except Exception:
                pass

        seen = set()
        unique: List[AdversarialTestCase] = []
        for tc in candidates:
            key = str(tc.input_data)
            if key not in seen:
                seen.add(key)
                unique.append(tc)

        return unique

    def _rng(self, label: str) -> random.Random:
        rng = random.Random(_hash_seed(self.problem_id, label))
        return rng


# ===========================================================================
# Problem type detection
# ===========================================================================

def _detect_problem_type(signature: str) -> List[str]:
    """Infer problem type(s) from function signature."""
    sig_lower = signature.lower()
    types = []

    if any(k in sig_lower for k in ['sum', 'add', 'plus']):
        types.append("additive")
    if any(k in sig_lower for k in ['sort', 'order', 'arrange']):
        types.append("ordering")
    if any(k in sig_lower for k in ['search', 'find', 'index', 'look']):
        types.append("search")
    if any(k in sig_lower for k in ['contain', 'valid', 'parenthes', 'bracket']):
        types.append("validation")
    if any(k in sig_lower for k in ['palindrom', 'mirror', 'reverse']):
        types.append("palindrome")
    if any(k in sig_lower for k in ['window', 'sliding', 'substr', 'subarray']):
        types.append("subarray")
    if any(k in sig_lower for k in ['merge', 'combin', 'union']):
        types.append("merge")
    if any(k in sig_lower for k in ['queen', 'n_queen']):
        types.append("n_queens")
    if any(k in sig_lower for k in ['trap', 'water', 'container']):
        types.append("water_container")

    if not types:
        types.append("general")
    return types


# ===========================================================================
# Generation strategies (one per pattern family)
# ===========================================================================

def strategy_boundary_extremes(self: AdversarialGenerator) -> List[AdversarialTestCase]:
    """Generate extremal boundary values."""
    cases = []
    rng = self._rng("boundary")
    types = _detect_problem_type(self.signature)

    if "additive" in types or "general" in types:
        cases.extend([
            AdversarialTestCase(
                input_data={"nums": [], "target": 0} if "nums" in self.signature.lower()
                          else [0, 0],
                expected=0,
                label="boundary_empty_input",
                source="adversarial_generated",
                strategy="boundary_extremes",
                description="empty input array",
            ),
            AdversarialTestCase(
                input_data={"nums": [1], "target": 1} if "nums" in self.signature.lower()
                          else [1],
                expected=1 if "nums" not in self.signature.lower() else None,
                label="boundary_single_element",
                source="adversarial_generated",
                strategy="boundary_extremes",
                description="single element input",
            ),
            AdversarialTestCase(
                input_data={"nums": [1, -1], "target": 0} if "nums" in self.signature.lower()
                          else [1, -1],
                expected=0 if "nums" not in self.signature.lower() else None,
                label="boundary_positive_negative",
                source="adversarial_generated",
                strategy="boundary_extremes",
                description="mixed positive/negative",
            ),
        ])

    if "ordering" in types or "general" in types:
        cases.append(AdversarialTestCase(
            input_data={"nums": []},
            expected=[],
            label="boundary_empty_sorted",
            source="adversarial_generated",
            strategy="boundary_extremes",
            description="empty for ordering",
        ))

    return cases


def strategy_off_by_one(self: AdversarialGenerator) -> List[AdversarialTestCase]:
    """Generate off-by-one error cases."""
    cases = []
    rng = self._rng("offbyone")

    cases.extend([
        AdversarialTestCase(
            input_data={"nums": [1, 2], "target": 4} if "nums" in self.signature.lower()
                      else [1, 2, 3],
            expected=None if "nums" in self.signature.lower() else None,
            label="offbyone_one_off_target",
            source="adversarial_generated",
            strategy="off_by_one",
            description="target is one more than any pair sum",
        ),
        AdversarialTestCase(
            input_data={"nums": [1, 1, 1], "target": 2} if "nums" in self.signature.lower()
                      else [1, 1, 1],
            expected=None if "nums" not in self.signature.lower() else None,
            label="offbyone_duplicate_values",
            source="adversarial_generated",
            strategy="off_by_one",
            description="all identical values",
        ),
    ])

    return cases


def strategy_symmetry_exploitation(self: AdversarialGenerator) -> List[AdversarialTestCase]:
    """Tests exploiting symmetry properties."""
    cases = []

    if any(k in self.signature.lower() for k in ['sum', 'add']):
        cases.append(AdversarialTestCase(
            input_data={"nums": [1, 1], "target": 2},
            expected=None,
            label="symmetry_two_identical_pairs",
            source="adversarial_generated",
            strategy="symmetry_exploitation",
            description="multiple valid solutions exist",
        ))

    return cases


def strategy_large_scale(self: AdversarialGenerator) -> List[AdversarialTestCase]:
    """Stress test at extreme scales."""
    cases = []

    if "nums" in self.signature.lower() or "array" in self.signature.lower():
        cases.extend([
            AdversarialTestCase(
                input_data={"nums": list(range(10000)), "target": 19999}
                            if "nums" in self.signature.lower()
                            else list(range(10000)),
                expected=None,
                label="scale_large_array",
                source="adversarial_generated",
                strategy="large_scale",
                description="10000 element array",
            ),
            AdversarialTestCase(
                input_data={"nums": [10**9], "target": 10**9}
                            if "nums" in self.signature.lower()
                            else [10**9],
                expected=None,
                label="scale_overflow_proximity",
                source="adversarial_generated",
                strategy="large_scale",
                description="near-integer-overflow values",
            ),
        ])

    return cases


def strategy_common_corner_cases(self: AdversarialGenerator) -> List[AdversarialTestCase]:
    """Known corner cases from common problem patterns."""
    cases = []

    types = _detect_problem_type(self.signature)

    if "validation" in types:
        cases.extend([
            AdversarialTestCase(
                input_data={"s": ""},
                expected=True,
                label="corner_empty_string",
                source="adversarial_generated",
                strategy="common_corner",
                description="empty string for validation",
            ),
            AdversarialTestCase(
                input_data={"s": "((()))"},
                expected=True,
                label="corner_deeply_nested",
                source="adversarial_generated",
                strategy="common_corner",
                description="deeply nested parentheses",
            ),
            AdversarialTestCase(
                input_data={"s": ")("},
                expected=False,
                label="corner_reversed_brackets",
                source="adversarial_generated",
                strategy="common_corner",
                description="reversed bracket order",
            ),
        ])

    if "additive" in types or "search" in types:
        cases.append(AdversarialTestCase(
            input_data={"nums": [-1, -2, -3], "target": -5}
                        if "nums" in self.signature.lower()
                        else [-1, -2, -3],
            expected=None,
            label="corner_all_negative",
            source="adversarial_generated",
            strategy="common_corner",
            description="all-negative array",
        ))

    if "palindrome" in types:
        cases.extend([
            AdversarialTestCase(
                input_data="a",
                expected="a",
                label="corner_single_char",
                source="adversarial_generated",
                strategy="common_corner",
                description="single character palindrome",
            ),
            AdversarialTestCase(
                input_data="aa",
                expected="aa",
                label="corner_two_char_palindrome",
                source="adversarial_generated",
                strategy="common_corner",
                description="two-character palindrome",
            ),
        ])

    return cases


# ===========================================================================
# Strategy registry
# ===========================================================================

STRATEGIES = [
    strategy_boundary_extremes,
    strategy_off_by_one,
    strategy_symmetry_exploitation,
    strategy_large_scale,
    strategy_common_corner_cases,
]

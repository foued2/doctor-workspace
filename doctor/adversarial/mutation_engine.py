"""
Doctor Mutation Engine — Structured adversarial transformations on reference solutions.

Mutation classes:
  A. boundary_weakness  — remove edge-case guards
  B. control_compression — merge branches into defaults
  C. state_corruption   — break internal invariants
  D. precision_degradation — weaken exact comparisons
  E. input_interpretation_drift — alter preprocessing assumptions

Each mutation is deterministic (problem + class + variant -> same result),
preserves function signature, and should break correctness on at least one test.

Pipeline: solution -> mutation -> evaluation
No reverse arrows: mutation never influences test generation.
"""
from __future__ import annotations

import ast
import hashlib
import random
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class MutationResult:
    mutated_code: str
    mutation_class: str
    variant_index: int
    description: str


MUTATION_CLASSES = [
    "boundary_weakness",
    "control_compression",
    "state_corruption",
    "precision_degradation",
    "input_interpretation_drift",
    "arithmetic_perturbation",
    "sign_flip",
    "coefficient_scaling",
    "range_boundary_shift",
    "operator_substitution",
]


class MutationEngine:
    def __init__(self, problem_id: str, num_variants_per_class: int = 3):
        self.problem_id = problem_id
        self.num_variants = num_variants_per_class
        self._mutators = _build_mutators()

    def _seed(self, mutation_class: str, variant: int) -> random.Random:
        seed_str = f"{self.problem_id}:{mutation_class}:{variant}"
        seed = int(hashlib.sha256(seed_str.encode()).hexdigest()[:8], 16)
        return random.Random(seed)

    def _parse(self, code: str) -> Optional[ast.AST]:
        try:
            return ast.parse(code)
        except SyntaxError:
            return None

    def generate_all(self, reference_code: str) -> List[MutationResult]:
        results = []
        for cls in MUTATION_CLASSES:
            for variant in range(self.num_variants):
                result = self.apply(reference_code, cls, variant)
                if result:
                    results.append(result)
        return results

    def apply(self, code: str, mutation_class: str, variant: int) -> Optional[MutationResult]:
        if mutation_class not in self._mutators:
            return None
        if self._parse(code) is None:
            return None

        rng = self._seed(mutation_class, variant)
        mutator = self._mutators[mutation_class]
        mutated, description = mutator.apply(code, rng)

        if mutated == code or description.startswith("no_"):
            return None
        if self._parse(mutated) is None:
            return None

        return MutationResult(
            mutated_code=mutated,
            mutation_class=mutation_class,
            variant_index=variant,
            description=description,
        )


# ===========================================================================
# Mutator implementations
# ===========================================================================

class _BoundaryWeakness:
    """Remove/bypass edge-case guards and early returns."""
    PATTERNS = [
        (r'\bif\s+\w+\s*==\s*0\b', 'if False'),
        (r'\bif\s+len\(\w+\)\s*==\s*0\b', 'if False'),
        (r'\bif\s+not\s+\w+\s*:', 'if False:'),
        (r'\bif\s+\w+\s*==\s*1\b', 'if False'),
        (r'\bif\s+\w+\s*<=\s*0\b', 'if False'),
        (r'return\s+\[\s*\w+\s*,\s*\w+\s*\]\s*(?=\n)', 'pass  # REMOVED_RETURN'),
        (r'return\s+\w+\s*(?=\n)', 'pass  # REMOVED_RETURN'),
    ]

    def apply(self, code: str, rng: random.Random) -> Tuple[str, str]:
        chosen = rng.choice(self.PATTERNS)
        pattern, replacement = chosen
        mutated = re.sub(pattern, replacement, code)
        if mutated == code:
            return code, "no_boundary_guard_found"
        return mutated, f"removed_boundary_{pattern[:25].strip()}"


class _ControlCompression:
    """Collapse branching logic."""
    def apply(self, code: str, rng: random.Random) -> Tuple[str, str]:
        if 'elif' not in code:
            return code, "no_elif_chain_found"
        lines = code.split('\n')
        new_lines = []
        skip_next = False
        for line in lines:
            if skip_next:
                skip_next = False
                continue
            if re.match(r'\s*elif\b', line):
                skip_next = True
                continue
            new_lines.append(line)
        mutated = '\n'.join(new_lines)
        if mutated != code:
            return mutated, "collapsed_elif_chain"
        return code, "no_elif_chain_found"


class _StateCorruption:
    """Break state management assumptions."""
    PATTERNS = [
        (r'seen\s*=\s*\{\}', 'seen = []'),
        (r'if\s+\w+\s+-\s+\w+\s+in\s+\w+:', 'if False:'),
        (r'\.append\(', '# .append('),
        (r'for\s+\w+\s+in\s+enumerate\(', r'for  # enumerate_removed '),
    ]

    def apply(self, code: str, rng: random.Random) -> Tuple[str, str]:
        for p, r in self.PATTERNS:
            if re.search(p, code):
                mutated = re.sub(p, r, code, count=1)
                if mutated != code:
                    return mutated, f"state_corruption_{p[:20].strip()}"
        return code, "no_state_target_found"


class _PrecisionDegradation:
    """Weaken exact comparisons."""
    def apply(self, code: str, rng: random.Random) -> Tuple[str, str]:
        if ' == ' in code:
            mutated = code.replace(' == ', ' >= ', 1)
            return mutated, "weakened_eq_to_ge"
        if '.round(' in code:
            mutated = code.replace('.round(', 'int(', 1)
            return mutated, "replaced_round_with_int"
        return code, "no_precision_target_found"


class _InputInterpretationDrift:
    """Subtle preprocessing assumption shifts."""
    PATTERNS = [
        (r'\.lower\(\)', '.lower()'),
        (r'\.strip\(\)', '.strip()'),
        (r'\.upper\(\)', '.upper()'),
    ]

    def apply(self, code: str, rng: random.Random) -> Tuple[str, str]:
        for p, r in self.PATTERNS:
            if rng.random() < 0.5 and re.search(p, code):
                mutated = re.sub(p, r + '  # DRIFT', code, count=1)
                if mutated != code:
                    return mutated, f"input_drift_{p[:15]}"
        return code, "no_interpretation_target_found"


def _build_mutators() -> Dict[str, Any]:
    return {
        "boundary_weakness": _BoundaryWeakness(),
        "control_compression": _ControlCompression(),
        "state_corruption": _StateCorruption(),
        "precision_degradation": _PrecisionDegradation(),
        "input_interpretation_drift": _InputInterpretationDrift(),
        "arithmetic_perturbation": _ArithmeticPerturbation(),
        "sign_flip": _SignFlip(),
        "coefficient_scaling": _CoefficientScaling(),
        "range_boundary_shift": _RangeBoundaryShift(),
        "operator_substitution": _OperatorSubstitution(),
    }


class _ArithmeticPerturbation:
    """Modify numeric constants in arithmetic expressions by small amounts."""

    def apply(self, code: str, rng: random.Random) -> Tuple[str, str]:
        mutations = [
            (r'\b(\d+)\s*\*\s*(\d+)', r'\1 * \2 + 1', 'mult_term_plus1'),
            (r'\b(\d+)\s*\*\s*(\d+)', r'\1 * \2 - 1', 'mult_term_minus1'),
            (r'\b(\d+)\s*\+\s*1\b', r'\1 + 2', 'add1_to_add2'),
            (r'\b(\d+)\s*-\s*1\b', r'\1 - 2', 'sub1_to_sub2'),
            (r'\b(\d+)\s*//\s*(\d+)', r'(\1 * 2) // \2', 'div_coefficient_double'),
            (r'\b(\d+)\s*//\s*(\d+)', r'(\1 // 2) // \2', 'div_coefficient_half'),
        ]
        valid = []
        for pattern, replacement, name in mutations:
            if re.search(pattern, code):
                valid.append((pattern, replacement, name))
        if not valid:
            return code, "no_numeric_constant_found"
        pattern, replacement, name = rng.choice(valid)
        mutated = re.sub(pattern, replacement, code, count=1)
        if mutated != code:
            return mutated, f"perturbed_{name}"
        return code, "no_numeric_constant_found"


class _SignFlip:
    """Negate return values or intermediate arithmetic terms."""

    def apply(self, code: str, rng: random.Random) -> Tuple[str, str]:
        mutations = [
            (r'return\s+(-?\d+)', lambda m: 'return ' + str(-int(m.group(1))), 'negate_literal_return'),
            (r'return\s+(\w+)', lambda m: f'return -{m.group(1)}', 'negate_var_return'),
            (r'rev\s*=\s*rev\s*\*\s*10', 'rev = rev * 10', 'drop_sign_flip'),
        ]
        for pattern, replacement, name in mutations:
            if callable(replacement):
                if re.search(pattern, code):
                    mutated = re.sub(pattern, replacement, code, count=1)
                    if mutated != code:
                        return mutated, f"sign_flip_{name}"
            else:
                if re.search(pattern, code):
                    mutated = re.sub(pattern, replacement, code, count=1)
                    if mutated != code:
                        return mutated, f"sign_flip_{name}"
        return code, "no_sign_target_found"


class _CoefficientScaling:
    """Alter multiplicative coefficients in formulas."""

    def apply(self, code: str, rng: random.Random) -> Tuple[str, str]:
        mutations = [
            (r'\b15\b', '30', 'LCM_15_to_30'),
            (r'\b3\b(?!\s*[\*/])', '6', 'coeff_3_to_6'),
            (r'\b5\b(?!\s*[\*/])', '10', 'coeff_5_to_10'),
            (r'\b2\b(?!\s*[\*/])', '4', 'coeff_2_to_4'),
        ]
        valid = []
        for pattern, replacement, name in mutations:
            if re.search(pattern, code):
                valid.append((pattern, replacement, name))
        if not valid:
            return code, "no_coefficient_found"
        pattern, replacement, name = rng.choice(valid)
        mutated = re.sub(pattern, replacement, code, count=1)
        if mutated != code:
            return mutated, f"scaled_{name}"
        return code, "no_coefficient_found"


class _RangeBoundaryShift:
    """Change boundary terms in range expressions: n-1 -> n, n -> n-1, etc."""

    def apply(self, code: str, rng: random.Random) -> Tuple[str, str]:
        mutations = [
            (r'\((\s*n\s*-\s*1\s*)\s*//', r'(n //', 'remove_minus1_in_divisor'),
            (r'\(\s*n\s*-\s*1\s*\)', '(n)', 'remove_minus1_parens'),
            (r'\(\s*n\s*-\s*1\s*/', r'(n /', 'change_minus1_to_n'),
            (r'\brange\(\s*1\s*,\s*n\)', 'range(0, n)', 'shift_range_start'),
            (r'\bfor\s+\w+\s+in\s+range\([^)]*n[^)]*\):', lambda m: m.group(0).replace('n - 1', 'n'), 'extend_range_to_n'),
        ]
        valid = []
        for pattern, replacement, name in mutations:
            if callable(replacement):
                if re.search(pattern, code):
                    valid.append((pattern, replacement, name))
            else:
                if re.search(pattern, code):
                    valid.append((pattern, replacement, name))
        if not valid:
            return code, "no_boundary_term_found"
        pattern, replacement, name = rng.choice(valid)
        if callable(replacement):
            mutated = re.sub(pattern, replacement, code, count=1)
        else:
            mutated = re.sub(pattern, replacement, code, count=1)
        if mutated != code:
            return mutated, f"boundary_shift_{name}"
        return code, "no_boundary_term_found"


class _OperatorSubstitution:
    """Swap arithmetic operators: + for -, * for //, % with different mod."""

    def apply(self, code: str, rng: random.Random) -> Tuple[str, str]:
        mutations = [
            (r'rev\s*=\s*rev\s*\*\s*10\s*\+\s*', 'rev = rev * 10 - ', 'drop_carry_digit'),
            (r'\+\s*1\b', ' - 1', 'flip_add1_to_sub1'),
            (r'\*\s*2\b', ' * 2 + 1', 'add_1_to_double'),
            (r'\s*-\s*1\s*//', ' // ', 'drop_minus1_before_div'),
            (r'\bif\s+\w+\s*%\s*\d+\s*==', 'if False:', 'disable_mod_check'),
            (r'\bif\s+\w+\s*//\s*\d+\s*==', 'if False:', 'disable_div_check'),
        ]
        valid = []
        for pattern, replacement, name in mutations:
            if re.search(pattern, code):
                valid.append((pattern, replacement, name))
        if not valid:
            return code, "no_operator_target_found"
        pattern, replacement, name = rng.choice(valid)
        mutated = re.sub(pattern, replacement, code, count=1)
        if mutated != code:
            return mutated, f"operator_swap_{name}"
        return code, "no_operator_target_found"

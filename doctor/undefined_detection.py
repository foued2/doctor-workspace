"""
Undefined Detection — Layer 0.5 (Stage 4, Phase 1)
====================================================

Detects prompts where the specification is genuinely ambiguous or
incomplete, making a definitive verdict impossible.

Unlike Layer 0 (explicit "undecidable"/"missing constraint" language),
Layer 0.5 uses **heuristic signals** to catch **implicit** undefined cases:

1. CONTRADICTORY CONSTRAINTS — mutually exclusive requirements
2. UNDERSPECIFIED EDGES — missing tiebreaks, incomplete state spaces
3. MULTIPLE INTERPRETATIONS — ambiguous terms leading to different outcomes
4. SELF-REFERENCE / PARADOX — rules that classify themselves
5. UNRESOLVED CONFLICTS — competing objectives with no priority

Each signal category has:
  - A set of regex patterns (heuristics, not exact matches)
  - A strength weight (0.0–1.0) per pattern
  - A minimum threshold for the category to fire

The aggregate undefined score is computed as a weighted sum with
diminishing returns (sub-linear combination) to avoid false positives
from noisy text.

Target: push undefined recall from 52.9% → >70%
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ===========================================================================
# Signal definitions
# ===========================================================================

@dataclass(frozen=True)
class UndefinedSignal:
    """A single heuristic signal that the prompt may be undefined."""
    category: str       # which signal category
    pattern: str        # the regex that matched
    matched_text: str   # the actual substring that matched
    strength: float     # 0.0–1.0, how strong this signal is
    description: str    # human-readable explanation


@dataclass
class UndefinedResult:
    """Result of undefined detection on a prompt."""
    score: float                        # aggregate 0.0–1.0
    signals: List[UndefinedSignal]      # all matched signals
    is_undefined: bool                  # whether to override to "undefined"
    category_scores: Dict[str, float]   # per-category scores
    decision_path: str                  # human-readable path


# ===========================================================================
# Pattern definitions — 5 categories, ~40 patterns total
# ===========================================================================

# Category 1: CONTRADICTORY CONSTRAINTS
# Two or more requirements that cannot simultaneously be satisfied.
_CONTRADICTION_PATTERNS = [
    (r"\bcannot\s+(?:both|simultaneously)\b", 0.85,
     "explicit mutual exclusivity stated"),
    (r"\b(?:mutually\s+exclusive|incompatible\s+(?:with|requirements?))\b", 0.85,
     "mutual exclusivity keywords"),
    (r"\b(?:contradict|contradiction|conflict(?:ing)?|inconsistent)\b", 0.60,
     "contradiction/conflict language"),
    (r"\b(?:must|should|required)\b.*\b(?:must\s+not|should\s+not|cannot|never)\b", 0.75,
     "positive and negative requirement on same action"),
    (r"\b(?:must|should|required)\b.*\b(?:unless|except|but)\b.*\b(?:not|never|impossible)\b", 0.70,
     "conditional negation of requirement"),
    (r"\b(?:both|all)\b.*\b(?:impossible|cannot|can't|no\s+way)\b", 0.80,
     "universal quantifier with impossibility"),
    (r"\bno\s+(?:valid|single|consistent|unique)\b.*\b(?:solution|answer|choice|way)\b", 0.80,
     "no valid solution stated"),
    (r"\b(?:either|one)\b.*\b(?:but\s+(?:not|then)|however|yet)\b.*\b(?:other|another)\b", 0.65,
     "either/or with conflict"),
    (r"\bsuperseded\b", 0.70,
     "rule/policy superseded by another"),
    (r"\bchain\s+of\s+(?:authority|command)\b.*\b(?:unclear|ambiguous|not\s+defined)\b", 0.80,
     "unclear chain of authority"),
    (r"\bcircular\s+(?:references?|dependency|logic|reference)\b", 0.75,
     "circular references between rules/documents"),
    (r"\b(?:amended|modified|changed)\b.*\b(?:approval|consent|unanimous)\b", 0.60,
     "amendment with disputed approval"),
]

# Category 2: UNDERSPECIFIED EDGES
# Missing tiebreaks, incomplete state spaces, gaps in the spec.
_UNDERSPECIFIED_PATTERNS = [
    (r"\b(?:no\s+(?:defined|specified|given)|undefined|not\s+defined|not\s+specified)\b", 0.80,
     "explicitly undefined or not specified"),
    (r"\b(?:missing|lacks|absent|no)\b.*\b(?:tie-?break|tiebreaker|priority|ordering|preference)\b", 0.85,
     "missing tiebreak mechanism"),
    (r"\b(?:depends\s+on|determined\s+by)\b.*\b(?:discretion|judgment|interpretation|context)\b", 0.75,
     "outcome depends on subjective judgment"),
    (r"\b(?:as\s+(?:low|high|fast|slow|soon|much)\s+as\s+possible|TBD|TBA|to\s+be\s+determined)\b", 0.70,
     "vague optimization target"),
    (r"\b(?:next\s+available|appropriate|suitable|reasonable)\b.*\b(?:person|time|method|way|case)\b", 0.65,
     "underspecified selection criterion"),
    (r"\b(?:incomplete|partial|insufficient)\b.*\b(?:information|data|spec(?:ification)?|constraint|rule)\b", 0.75,
     "incomplete specification"),
    (r"\b(?:multiple|several|various)\b.*\b(?:interpretations?|meanings?|readings?|understandings?)\b", 0.70,
     "multiple interpretations acknowledged"),
    (r"\b(?:open\s+to\s+|subject\s+to\s+|left\s+to\s+)\b.*\b(?:interpretation|discretion|judgment)\b", 0.70,
     "left to interpretation"),
    (r"\b(?:don't|do\s+not)\s+explain\s+(?:why|how)", 0.60,
     "unexplained decision in examples"),
    (r"\barbitrary\s+order", 0.70,
     "arbitrary ordering without justification"),
]

# Category 3: MULTIPLE INTERPRETATIONS
# Ambiguous terms that lead to different valid outcomes.
_MULTI_INTERP_PATTERNS = [
    (r"\b(?:ambiguous|ambiguity)\b", 0.75,
     "explicit ambiguity stated"),
    (r"\b(?:could\s+be|can\s+be|may\s+be)\b.*\b(?:interpreted|understood|read)\b.*\b(?:as|to)\b", 0.70,
     "multiple valid interpretations possible"),
    (r"\b(?:two|multiple|several)\b.*\b(?:valid|reasonable|legitimate|defensible)\b.*\b(?:interpretations?|readings?|views?)\b", 0.80,
     "multiple valid interpretations"),
    (r"\b(?:depends\s+on)\b.*\b(?:which|how|whether)\b.*\b(?:interpret|understand|define|classify)\b", 0.70,
     "outcome depends on interpretation choice"),
    (r"\b(?:one\s+(?:view|interpretation|reading)\b.*\b(?:another|other)\b.*\b(?:view|interpretation|reading))\b", 0.75,
     "contrasting interpretations presented"),
    (r"\b(?:equally\s+valid|both\s+correct|either\s+way)\b", 0.80,
     "equally valid alternatives"),
    (r"\b(?:arguably|debatable|disputed|contested)\b", 0.60,
     "disputed/contestable claim"),
]

# Category 4: SELF-REFERENCE / PARADOX
# Rules that refer to themselves, creating logical paradoxes.
_SELF_REF_PATTERNS = [
    (r"\b(?:self-?referential|self-?referencing|refers\s+to\s+itself)\b", 0.90,
     "self-referential rule"),
    (r"\b(?:this\s+rule|this\s+policy|this\s+statement)\b.*\b(?:itself|classif(?:y|ies)|applies?\s+to)\b", 0.85,
     "rule classifying itself"),
    (r"\b(?:paradox|paradoxical|liar['']s?\s+paradox)\b", 0.90,
     "logical paradox referenced"),
    (r"\b(?:if\s+.*\b(?:true|false|classified)\b.*\bthen\b.*\b(?:false|true|reclassified)\b)\b", 0.80,
     "conditional that flips its own classification"),
    (r"\b(?:applies?\s+to\s+(?:itself|its\s+own|the\s+rule\s+itself))\b", 0.85,
     "rule applies to itself"),
    (r"\b(?:infinite\s+loop|circular\s+(?:reference|logic|reasoning)|regress)\b", 0.75,
     "circular reference or infinite regress"),
]

# Category 5: UNRESOLVED CONFLICTS
# Competing objectives with no stated priority.
_UNRESOLVED_PATTERNS = [
    (r"\b(?:competing\s+(?:objectives?|goals?|requirements?|constraints?|interests?))\b", 0.80,
     "competing objectives stated"),
    (r"\b(?:trade-?off|tradeoff|balance\s+between)\b.*\b(?:and)\b", 0.65,
     "tradeoff between competing goals"),
    (r"\b(?:optimize|optimize|minimize|maximize)\b.*\b(?:while|and\s+also|and\s+simultaneously)\b.*\b(?:optimize|minimize|maximize|preserve|maintain)\b", 0.75,
     "multiple optimization targets without priority"),
    (r"\b(?:prefer|priority|precedence)\b.*\b(?:but|however|yet|except)\b.*\b(?:also|must|should|need)\b", 0.75,
     "stated priority contradicted by another requirement"),
    (r"\b(?:no\s+(?:clear|stated|defined))\b.*\b(?:priority|ordering|preference|rule)\b.*\b(?:between|among|for)\b", 0.80,
     "no clear priority between options"),
    (r"\b(?:identical|equal|same)\b.*\b(?:priority|request|claim)\b.*\b(?:simultaneous|at\s+the\s+same\s+time|concurrent)\b|\b(?:simultaneous|at\s+the\s+same\s+time|concurrent)\b.*\b(?:identical|equal|same)\b.*\b(?:priority|request|claim)\b", 0.80,
     "identical-priority simultaneous requests"),
    (r"\bno\s+tie-?breaking\b.*\b(?:rule|mechanism|specified)\b", 0.80,
     "no tie-breaking rule specified"),
    (r"\b(?:neither|none)\b.*\b(?:takes\s+precedence|has\s+priority|overrides)\b", 0.80,
     "no option takes precedence"),
]

# Category 6: NORMATIVE / OPINION AMBIGUITY
# Questions asking "what's the best/right way?" when multiple valid approaches exist.
_NORMATIVE_PATTERNS = [
    (r"\b(?:what\s+(?:is|')?s|which\s+(?:is|')?s|how\s+should)\b.*\b(?:right|best|correct|proper|pythonic|ideal|appropriate)\b", 0.75,
     "normative question with no single right answer"),
    (r"\b(?:they\s+all\s+seem|all\s+seem\s+to)\b.*\b(?:similar|same|equivalent|comparable)\b", 0.70,
     "multiple options appear equally viable"),
    (r"\b(?:when\s+should|whether\s+to)\b.*\b(?:use\s+each|choose|pick|select)\b", 0.65,
     "selection among viable alternatives"),
    (r"\b(?:no\s+(?:single|one|clear|definitive|universal))\b.*\b(?:answer|solution|approach|way|method|right\s+way|best\s+way)\b", 0.80,
     "no single right answer acknowledged"),
    (r"\b(?:depends\s+on)\b.*\b(?:situation|context|circumstances|use\s+case|project|requirements|goals)\b", 0.70,
     "answer depends on context/situation"),
    (r"\b(?:vague|vaguely|vague(?:ly)?\s+defined)\b.*\b(?:criterion|criteria|guidance|standard|rule|threshold|metric)\b", 0.75,
     "vague criterion or guidance"),
    (r"\b(?:no\s+further|no\s+additional|no\s+more)\b.*\b(?:guidance|information|detail|specification|clarification)\b", 0.75,
     "no further guidance provided"),
    (r"\b(?:conflicts?\s+with|conflicting\s+(?:factors|inputs|signals|requirements|objectives))\b", 0.70,
     "conflicting factors/inputs"),
    (r"\b(?:unspecified|un(?!defined))\b.*\b(?:for|when|if|how|which|what)\b", 0.60,
     "unspecified behavior for a situation"),
]

# All categories grouped
_ALL_CATEGORIES = [
    ("contradictory_constraints", _CONTRADICTION_PATTERNS),
    ("underspecified_edges", _UNDERSPECIFIED_PATTERNS),
    ("multiple_interpretations", _MULTI_INTERP_PATTERNS),
    ("self_reference_paradox", _SELF_REF_PATTERNS),
    ("unresolved_conflicts", _UNRESOLVED_PATTERNS),
    ("normative_opinion_ambiguity", _NORMATIVE_PATTERNS),
]

# Pre-compile all patterns
_COMPILED_PATTERNS: List[Tuple[str, re.Pattern, float, str]] = []
for cat_name, patterns in _ALL_CATEGORIES:
    for pat_str, strength, desc in patterns:
        _COMPILED_PATTERNS.append((cat_name, re.compile(pat_str, re.IGNORECASE), strength, desc))


# ===========================================================================
# Scoring — sub-linear combination with category-level boosts
# ===========================================================================

# Weights for each category (some signal types are more reliable than others)
_CATEGORY_WEIGHTS = {
    "contradictory_constraints": 1.0,
    "underspecified_edges": 1.0,
    "multiple_interpretations": 0.9,
    "self_reference_paradox": 1.1,   # paradoxes are strong signals
    "unresolved_conflicts": 0.95,
    "normative_opinion_ambiguity": 0.85,
}

# Diminishing returns: each additional signal in a category contributes less
# score = sum(strength_i * decay^(i-1)) for signals in category, sorted by strength desc
_SIGNAL_DECAY = 0.6

# Thresholds
_UNDEFINED_OVERRIDE_THRESHOLD = 0.45   # score needed to declare "undefined"
_HIGH_CONFIDENCE_THRESHOLD = 0.55      # above this, 1 signal may be enough
_MIN_SIGNALS_FOR_OVERRIDE = 2          # required when score is between 0.45 and 0.55
_MIN_SIGNALS_HIGH_CONF = 1             # required when score >= 0.55

# Patterns strong enough to override with just 1 signal (when score >= 0.55).
# These indicate a critical term in the specification is explicitly left undefined.
# All other patterns require 2+ signals to avoid false positives from noise text.
_SINGLE_SIGNAL_OVERRIDE_PATTERNS = {
    # Explicit "X is left undefined" or "X is not specified" about a critical term
    r"\bundefined\b",                  # bare "undefined" in spec context
    r"\bnot\s+defined\b",              # "not defined"
    r"\bnot\s+specified\b",            # "not specified"
    r"\bno\s+definition\b",            # "no definition of"
    r"\bno\s+tie-?breaking\b",         # "no tie-breaking"
    r"\bto\s+be\s+determined\b",       # "TBD"
    r"\bno\s+further\b.*\bguidance\b", # "no further guidance"
}


def _is_strong_single_signal(signals: List[UndefinedSignal]) -> bool:
    """Check if any signal is strong enough to override on its own.

    Only patterns that explicitly state a critical term is undefined/not
    specified are strong enough. Generic noise patterns (contested,
    conflicting, ambiguous) require corroboration from a second signal.
    """
    for sig in signals:
        # Check if the pattern matches one of the strong override patterns
        for strong_pat in _SINGLE_SIGNAL_OVERRIDE_PATTERNS:
            if re.search(strong_pat, sig.pattern, re.IGNORECASE):
                return True
            # Also check the matched text itself
            if re.search(strong_pat, sig.matched_text, re.IGNORECASE):
                return True
    return False


def detect_undefined(text: str) -> List[UndefinedSignal]:
    """Scan text for undefined-detection heuristic signals.

    Returns all matched signals, each with category, pattern, strength,
    and the actual matched substring.
    """
    signals = []
    for cat_name, pat_re, strength, desc in _COMPILED_PATTERNS:
        match = pat_re.search(text)
        if match:
            signals.append(UndefinedSignal(
                category=cat_name,
                pattern=pat_re.pattern,
                matched_text=match.group(0),
                strength=strength,
                description=desc,
            ))
    return signals


def undefined_score(signals: List[UndefinedSignal]) -> float:
    """Compute aggregate undefined score from matched signals.

    Strategy: take the MAXIMUM per-category score (not average), since a
    single strong signal cluster in one category is sufficient evidence
    that the prompt is undefined. Then apply a cross-category bonus for
    having signals in multiple categories.

    Returns score in [0.0, 1.0].
    """
    if not signals:
        return 0.0

    # Group by category
    by_category: Dict[str, List[UndefinedSignal]] = {}
    for s in signals:
        by_category.setdefault(s.category, []).append(s)

    category_scores = {}
    for cat_name, cat_signals in by_category.items():
        # Sort by strength descending, apply diminishing returns within category
        sorted_signals = sorted(cat_signals, key=lambda s: s.strength, reverse=True)
        raw_score = 0.0
        for i, sig in enumerate(sorted_signals):
            raw_score += sig.strength * (_SIGNAL_DECAY ** i)
        # Normalize: cap at 1.0 per category
        category_scores[cat_name] = min(1.0, raw_score)

    # Primary score: best single category (max, not average)
    # A strong signal in one category is enough to flag undefined
    max_cat_score = max(category_scores.values()) if category_scores else 0.0

    # Cross-category bonus: having signals in N categories adds bonus
    n_categories = len(category_scores)
    category_bonus = min(0.15, (n_categories - 1) * 0.05) if n_categories > 1 else 0.0

    # Weighted combination: 85% best category + 15% cross-category bonus
    final_score = min(1.0, 0.85 * max_cat_score + category_bonus)

    return final_score


def classify_undefined(text: str) -> UndefinedResult:
    """Full undefined detection pipeline: detect signals, score, classify.

    This is the Layer 0.5 entry point. Call this from the Doctor's
    predict() method before any other classification logic.
    """
    signals = detect_undefined(text)
    score = undefined_score(signals)

    # Group by category for per-category scores
    by_category: Dict[str, List[UndefinedSignal]] = {}
    for s in signals:
        by_category.setdefault(s.category, []).append(s)

    category_scores = {}
    for cat_name, cat_signals in by_category.items():
        sorted_signals = sorted(cat_signals, key=lambda s: s.strength, reverse=True)
        raw_score = 0.0
        for i, sig in enumerate(sorted_signals):
            raw_score += sig.strength * (_SIGNAL_DECAY ** i)
        category_scores[cat_name] = min(1.0, raw_score)

    # Adaptive signal requirement:
    # - Score >= 0.55 AND at least one strong signal → 1 signal allowed
    # - Score >= 0.45 but no strong single signal → 2 signals required
    # This avoids false positives from generic noise (contested, conflicting)
    # while catching cases where a critical term is explicitly left undefined.
    if score >= _HIGH_CONFIDENCE_THRESHOLD:
        min_signals = 1 if _is_strong_single_signal(signals) else _MIN_SIGNALS_FOR_OVERRIDE
    else:
        min_signals = _MIN_SIGNALS_FOR_OVERRIDE

    is_undefined = score >= _UNDEFINED_OVERRIDE_THRESHOLD and len(signals) >= min_signals

    # Build decision path
    if is_undefined:
        active_cats = sorted(
            [cat for cat, sc in category_scores.items() if sc > 0.2],
            key=lambda c: category_scores[c],
            reverse=True,
        )
        decision_path = (
            f"L0.5:undefined(score={score:.2f}, signals={len(signals)}, "
            f"categories={','.join(active_cats[:3])})"
        )
    else:
        decision_path = f"L0.5:not_undefined(score={score:.2f}, signals={len(signals)})"

    return UndefinedResult(
        score=score,
        signals=signals,
        is_undefined=is_undefined,
        category_scores=category_scores,
        decision_path=decision_path,
    )


# Module-level constants (used by callers)
UNDEFINED_OVERRIDE_THRESHOLD = _UNDEFINED_OVERRIDE_THRESHOLD
MIN_SIGNALS_FOR_OVERRIDE = _MIN_SIGNALS_FOR_OVERRIDE

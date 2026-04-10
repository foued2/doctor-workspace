"""Quick smoke test for Layer 0.5 undefined detection."""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from doctor.undefined_detection import classify_undefined

test_cases = [
    ("contradictory",
     "The system must minimize delay and also never reorder arrivals, "
     "even when this is impossible to do both simultaneously. "
     "No tiebreak is defined."),

    ("paradox",
     "This rule applies to itself. If this statement is classified as true, "
     "then it must be false. Self-referential paradox."),

    ("underspecified",
     "The next available person handles escalation. "
     "Scope of confidential information is not defined. "
     "Multiple valid interpretations exist."),

    ("multi_interp",
     "There are two valid interpretations. One view says classify as A, "
     "another reading says classify as B. Both are equally valid and "
     "neither takes precedence."),

    ("unresolved_conflict",
     "Competing objectives: minimize cost and maximize quality. "
     "No clear priority between them. Trade-off between speed and accuracy."),

    ("clean_correct",
     "Given an array of integers nums and an integer target, return indices "
     "of the two numbers such that they add up to target."),

    ("clean_partial",
     "Use a hash map to store values and look up complements. "
     "Time O(n), Space O(n). Handles the main case."),

    ("clean_incorrect",
     "For each element, check if it equals target. Return index if true. "
     "This only works when target equals one of the elements."),
]

print("=== Layer 0.5 Undefined Detection Smoke Test ===\n")

for name, text in test_cases:
    r = classify_undefined(text)
    print(f"{name}:")
    print(f"  score={r.score:.3f}  is_undefined={r.is_undefined}  signals={len(r.signals)}")
    print(f"  path: {r.decision_path}")
    if r.signals:
        for s in r.signals[:4]:
            print(f"    [{s.category}] strength={s.strength} matched='{s.matched_text}' — {s.description}")
    print()

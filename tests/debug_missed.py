"""Debug the two missed cases."""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from doctor.undefined_detection import classify_undefined

# Actual conflicting_meta_signals prompt
conflicting = (
    "CASE: Meta-level conflict test\n"
    "Domain: policy analysis with conflicting documentation.\n"
    "Primary rule: Minimize delay while preserving arrival order.\n"
    "A later memo states: 'The primary rule above was superseded by the revised policy, "
    "which prioritizes order over delay.'\n"
    "However, an even earlier document says: 'All rule changes require unanimous approval, "
    "which was not obtained for the revision.'\n"
    "A third document notes: 'The approval requirement itself was amended in Q2.'\n"
    "The chain of authority is unclear, and documents reference each other circularly.\n"
    "PROPOSED RESPONSE: Applies the original rule, noting the conflict but deferring to "
    "the earliest documented policy as most authoritative."
)

# Actual implicit_undefined prompt
implicit = (
    "CASE: Implicit ambiguity test\n"
    "Domain: scheduling policy.\n"
    "Rule: Process requests in priority order.\n"
    "Two requests arrive simultaneously with identical priority.\n"
    "No tie-breaking mechanism is specified.\n"
    "The examples show one being processed first, but don't explain why.\n"
    "The proposed response processes them in arbitrary order.\n"
    "PROPOSED RESPONSE: Handles the common case correctly, leaves tie-breaking unspecified."
)

for name, text in [("conflicting_meta_signals", conflicting), ("implicit_undefined", implicit)]:
    r = classify_undefined(text)
    print(f"{name}: score={r.score:.3f} is_undef={r.is_undefined} signals={len(r.signals)}")
    for s in r.signals:
        print(f"  [{s.category}] strength={s.strength} matched='{s.matched_text}'")
    print()

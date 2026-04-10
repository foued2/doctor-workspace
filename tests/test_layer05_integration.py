"""End-to-end integration test: Layer 0.5 + LLMDoctor."""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from doctor.llm_doctor import predict

print("=== Integration Test: Layer 0.5 + LLMDoctor ===\n")

# --- Undefined cases (should return "undefined") ---
undefined_cases = [
    ("implicit_undefined",
     "CASE: Implicit ambiguity test\n"
     "Domain: scheduling policy.\n"
     "Rule: Process requests in priority order.\n"
     "Two requests arrive simultaneously with identical priority.\n"
     "No tie-breaking mechanism is specified.\n"
     "The examples show one being processed first, but don't explain why.\n"
     "PROPOSED RESPONSE: Processes them in arbitrary order."),

    ("paradox",
     "CASE: Self-referential rule test\n"
     "Rule: This policy should be classified as 'undefined' if and only if "
     "it contains a self-referential paradox.\n"
     "This policy contains a self-referential paradox.\n"
     "PROPOSED RESPONSE: Classifies as undefined."),

    ("conflicting_docs",
     "CASE: Meta-level conflict test\n"
     "Domain: policy analysis with conflicting documentation.\n"
     "Primary rule: Minimize delay while preserving arrival order.\n"
     "A later memo states the primary rule was superseded.\n"
     "However, an earlier document says all rule changes require unanimous approval.\n"
     "The chain of authority is unclear, and documents reference each other circularly.\n"
     "PROPOSED RESPONSE: Applies the original rule."),

    ("multi_interp",
     "CASE: Multiple interpretations\n"
     "There are two valid interpretations. Under one reading the answer is A, "
     "under another equally valid reading the answer is B. "
     "Neither interpretation takes precedence.\n"
     "PROPOSED RESPONSE: Picks interpretation A."),
]

# --- Clean LeetCode cases (should NOT return "undefined") ---
clean_cases = [
    ("twosum_correct",
     "PROBLEM: Given an array of integers nums and an integer target, "
     "return indices of the two numbers such that they add up to target.\n\n"
     "SOLUTION:\n"
     "def twoSum(nums, target):\n"
     "    seen = {}\n"
     "    for i, n in enumerate(nums):\n"
     "        if target - n in seen:\n"
     "            return [seen[target-n], i]\n"
     "        seen[n] = i"),

    ("palindrome_correct",
     "PROBLEM: Determine if an integer is a palindrome.\n\n"
     "SOLUTION:\n"
     "def isPalindrome(x):\n"
     "    if x < 0: return False\n"
     "    rev, orig = 0, x\n"
     "    while x > 0:\n"
     "        rev = rev * 10 + x % 10\n"
     "        x //= 10\n"
     "    return rev == orig"),
]

print("--- Undefined cases (expect label='undefined') ---\n")
undef_hits = 0
for name, text in undefined_cases:
    r = predict(text)
    detected = r["label"] == "undefined"
    if detected:
        undef_hits += 1
    status = "✓" if detected else "✗"
    print(f"{status} {name}: label={r['label']} conf={r['confidence']} kind={r['confidence_kind']}")
    print(f"   path={r['decision_path']}")
    print()

print(f"Undefined: {undef_hits}/{len(undefined_cases)} detected\n")

print("--- Clean LeetCode cases (expect label != 'undefined') ---\n")
clean_ok = 0
for name, text in clean_cases:
    r = predict(text)
    ok = r["label"] != "undefined"
    if ok:
        clean_ok += 1
    status = "✓" if ok else "✗ FALSE POSITIVE"
    print(f"{status} {name}: label={r['label']} conf={r['confidence']} kind={r['confidence_kind']}")
    print()

print(f"Clean: {clean_ok}/{len(clean_cases)} correctly NOT undefined\n")

total = len(undefined_cases) + len(clean_cases)
correct = undef_hits + clean_ok
print(f"=== OVERALL: {correct}/{total} correct ({correct/total*100:.0f}%) ===")

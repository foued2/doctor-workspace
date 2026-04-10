"""Test Layer 0.5 against real ESL attack cases."""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from doctor.undefined_detection import classify_undefined

# Human-crafted attack cases with ground_truth="undefined"
human_attacks = [
    ("conflicting_meta_signals",
     "The document references a policy that references this document. "
     "Chain of authority is unclear. Circular references between documents "
     "make it impossible to determine the authoritative source."),

    ("self_referential_paradox",
     "This rule states: any statement that classifies itself as correct "
     "must be reclassified as incorrect. This is a self-referential paradox "
     "similar to the liar's paradox."),

    ("multiple_interpretations_hard",
     "The specification allows two valid interpretations. Under one reading, "
     "the answer is A. Under another equally valid reading, the answer is B. "
     "Neither interpretation takes precedence over the other."),

    ("implicit_undefined",
     "Two requests arrive simultaneously with identical priority.\n"
     "No tie-breaking mechanism is specified.\n"
     "The examples show one being processed first, but don't explain why.\n"
     "The proposed response processes them in arbitrary order."),
]

# Cross-domain undefined cases
cross_domain = [
    ("legal_nda",
     "The NDA defines confidential information as information that is "
     "confidential. The scope of confidential information is not defined. "
     "Determination is left to reasonable judgment."),

    ("medical_triage",
     "In emergency triage, resources should be allocated to those most "
     "in need. Need is determined by medical staff discretion. "
     "Multiple interpretations of urgency exist."),

    ("system_design",
     "Replication lag should be as low as possible. Schema migration "
     "strategy is TBD. The approach depends on context and interpretation."),

    ("business_approval",
     "Escalation goes to the next available person. No definition of "
     "available exists. The appropriate method is left to discretion."),

    ("academic_integrity",
     "The line between collaboration and plagiarism is determined by "
     "reasonable judgment. Multiple valid interpretations of the boundary exist. "
     "This policy is subject to interpretation."),

    ("financial_risk",
     "Risk tolerance must align with the client's financial situation. "
     "No clear priority between competing objectives. Trade-off between "
     "growth and preservation."),
]

# Clean cases (should NOT be undefined)
clean_cases = [
    ("twosum_correct",
     "PROBLEM: Given an array of integers nums and an integer target, "
     "return indices of the two numbers such that they add up to target.\n"
     "SOLUTION:\ndef twoSum(nums, target):\n"
     "    seen = {}\n"
     "    for i, n in enumerate(nums):\n"
     "        if target - n in seen:\n"
     "            return [seen[target-n], i]\n"
     "        seen[n] = i"),

    ("palindrome_correct",
     "PROBLEM: Determine if an integer is a palindrome without converting to string.\n"
     "SOLUTION:\ndef isPalindrome(x):\n"
     "    if x < 0: return False\n"
     "    rev, orig = 0, x\n"
     "    while x > 0:\n"
     "        rev = rev * 10 + x % 10\n"
     "        x //= 10\n"
     "    return rev == orig"),

    ("valid_parens_incorrect",
     "PROBLEM: Check if a string of parentheses is valid.\n"
     "SOLUTION:\ndef isValid(s):\n"
     "    return len(s) % 2 == 0"),
]

print("=== Layer 0.5 on Human-Crafted Undefined Attacks ===\n")
undefined_detected = 0
undefined_total = 0

for name, text in human_attacks:
    r = classify_undefined(text)
    undefined_total += 1
    detected = r.is_undefined
    if detected:
        undefined_detected += 1
    status = "✓ DETECTED" if detected else "✗ MISSED"
    print(f"{status} {name}")
    print(f"  score={r.score:.3f} signals={len(r.signals)}")
    if r.signals:
        for s in r.signals[:3]:
            print(f"    [{s.category}] '{s.matched_text}'")
    print()

print(f"Human attacks: {undefined_detected}/{undefined_total} detected\n")

print("=== Layer 0.5 on Cross-Domain Undefined Cases ===\n")
cd_detected = 0
cd_total = 0

for name, text in cross_domain:
    r = classify_undefined(text)
    cd_total += 1
    detected = r.is_undefined
    if detected:
        cd_detected += 1
    status = "✓ DETECTED" if detected else "✗ MISSED"
    print(f"{status} {name}")
    print(f"  score={r.score:.3f} signals={len(r.signals)}")
    if r.signals:
        for s in r.signals[:3]:
            print(f"    [{s.category}] '{s.matched_text}'")
    print()

print(f"Cross-domain: {cd_detected}/{cd_total} detected\n")

print("=== Layer 0.5 on Clean Cases (should be NOT undefined) ===\n")
false_positives = 0
clean_total = 0

for name, text in clean_cases:
    r = classify_undefined(text)
    clean_total += 1
    if r.is_undefined:
        false_positives += 1
    status = "✓ CLEAN" if not r.is_undefined else "✗ FALSE POSITIVE"
    print(f"{status} {name}")
    print(f"  score={r.score:.3f} signals={len(r.signals)}")
    print()

print(f"Clean: {clean_total - false_positives}/{clean_total} correct (0 false positives ideal)\n")

total_undefined = undefined_total + cd_total
total_detected = undefined_detected + cd_detected
print(f"=== OVERALL: {total_detected}/{total_undefined} undefined detected ({total_detected/total_undefined*100:.0f}%) ===")
print(f"False positive rate: {false_positives}/{clean_total} ({false_positives/clean_total*100:.0f}%)")

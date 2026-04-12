"""
Wrong@HighConf has two possible interpretations:
1. Among ALL wrong cases: what % were high confidence? (what the grader computes)
2. Among ALL high-conf cases: what % were wrong? (user-facing risk)
"""

results = [
    ("Container_With_Most_Water_correct", "correct", "correct", 0.85),
    ("Container_With_Most_Water_incorrect", "incorrect", "incorrect", 0.0),
    ("Container_With_Most_Water_partial", "partial", "partial", 0.72),
    ("Longest_Palindromic_Substring_correct", "correct", "correct", 0.95),
    ("Longest_Palindromic_Substring_incorrect", "incorrect", "incorrect", 0.75),
    ("Longest_Palindromic_Substring_partial", "incorrect", "incorrect", 0.6),
    ("Merge_Two_Sorted_Lists_correct", "correct", "partial", 0.75),
    ("Merge_Two_Sorted_Lists_incorrect", "incorrect", "incorrect", 0.17),
    ("Merge_Two_Sorted_Lists_partial", "partial", "incorrect", 0.17),
    ("N-Queens_correct", "correct", "partial", 0.6),
    ("N-Queens_incorrect", "incorrect", "partial", 0.6),
    ("N-Queens_partial", "partial", "incorrect", 0.6),
    ("Palindrome_Number_correct", "correct", "correct", 0.85),
    ("Palindrome_Number_incorrect", "partial", "partial", 0.72),
    ("Palindrome_Number_partial", "partial", "partial", 0.72),
    ("Roman_to_Integer_correct", "correct", "correct", 0.85),
    ("Roman_to_Integer_incorrect", "incorrect", "incorrect", 0.75),
    ("Roman_to_Integer_partial", "incorrect", "incorrect", 0.6),
    ("Trapping_Rain_Water_correct", "correct", "correct", 0.85),
    ("Trapping_Rain_Water_incorrect", "incorrect", "incorrect", 0.6),
    ("Trapping_Rain_Water_partial", "incorrect", "incorrect", 0.6),
    ("Two_Sum_correct", "correct", "correct", 0.85),
    ("Two_Sum_incorrect", "incorrect", "incorrect", 0.0),
    ("Two_Sum_partial", "partial", "partial", 0.72),
    ("Valid_Parentheses_correct", "correct", "correct", 0.95),
    ("Valid_Parentheses_incorrect", "incorrect", "incorrect", 0.75),
    ("Valid_Parentheses_partial", "incorrect", "incorrect", 0.75),
]

wrong_cases = [(c, g, p, cf) for c, g, p, cf in results if g != p]
wrong_high = [(c, g, p, cf) for c, g, p, cf in wrong_cases if cf >= 0.70]

print("=" * 100)
print("ALL WRONG CASES (5 total)")
print("=" * 100)
for case_id, gt, pred, conf in wrong_cases:
    hi = " [HIGH CONF]" if conf >= 0.70 else ""
    print(f"  {case_id:<50} GT={gt:<12} Pred={pred:<12} conf={conf:.2f}{hi}")

print(f"\n  Total wrong: {len(wrong_cases)}")
print(f"  Wrong @ high conf (>=0.70): {len(wrong_high)}")
print(f"  Wrong@HighConf rate (grader metric): {len(wrong_high)/len(wrong_cases)*100:.1f}%")

print(f"\n  Among ALL high-conf verdicts: ", end="")
all_high = [r for r in results if r[3] >= 0.70]
wrong_in_high = [r for r in all_high if r[1] != r[2]]
print(f"{len(wrong_in_high)}/{len(all_high)} = {len(wrong_in_high)/len(all_high)*100:.1f}%")

print("\n" + "=" * 100)
print("THE SINGLE OFFENDER:")
print("=" * 100)
for case_id, gt, pred, conf in wrong_high:
    print(f"  {case_id}")
    print(f"    GT = {gt}")
    print(f"    Pred = {pred}")
    print(f"    Confidence = {conf:.2f}")
    print(f"    Why? L2 failed on 'both_empty' test (linked list edge case)")
    print(f"    L1 said correct, L2 said partial (1/5 tests failed = 20%)")
    print(f"    Severity = minor (1 failure out of 5)")
    print(f"    Rule 5 fell back to L2 verdict = partial")
    print(f"    This is a false partial — correct solution misclassified due to")
    print(f"    a test execution artifact (empty linked list handling)")

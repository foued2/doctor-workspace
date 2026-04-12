"""
Identify Wrong@HighConf cases from the CURRENT baseline run output.
Uses the already-printed results from the last baseline run.

From the output, cases with conf >= 0.70 and GT != Pred:
- Misclassified: Merge_Two_Sorted_Lists_correct: GT=correct, Pred=partial, conf=0.75
- Misclassified: Merge_Two_Sorted_Lists_partial: GT=partial, Pred=incorrect, conf=0.17 (NOT high conf)
- Misclassified: N-Queens_correct: GT=correct, Pred=partial, conf=0.60 (NOT high conf)
- Misclassified: N-Queens_incorrect: GT=incorrect, Pred=partial, conf=0.60 (NOT high conf)
- Misclassified: N-Queens_partial: GT=partial, Pred=incorrect, conf=0.60 (NOT high conf)

Now check ALL cases with conf >= 0.70 for GT mismatch.
"""

# All 27 cases from the baseline output, parsed manually:
results = [
    # (case_id, GT, Pred, conf)
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

print("=" * 120)
print("HIGH-CONFIDENCE VERDICTS (confidence >= 0.70)")
print("=" * 120)
print(f"{'Case':<50} {'GT':<12} {'Pred':<12} {'Conf':>6} {'Status'}")
print("-" * 120)

high_conf = []
wrong_high = []

for case_id, gt, pred, conf in results:
    if conf >= 0.70:
        correct = gt == pred
        status = "CORRECT" if correct else "** WRONG **"
        print(f"{case_id:<50} {gt:<12} {pred:<12} {conf:>6.2f} {status}")
        high_conf.append(case_id)
        if not correct:
            wrong_high.append((case_id, gt, pred, conf))

print("-" * 120)
print(f"\nHigh-conf total: {len(high_conf)} | Wrong@HighConf: {len(wrong_high)}")
print(f"Wrong@HighConf rate: {len(wrong_high)/len(high_conf)*100:.1f}%")

if wrong_high:
    print(f"\n{'=' * 120}")
    print("WRONG @ HIGH CONF — OFFENDERS")
    print("=" * 120)
    for case_id, gt, pred, conf in wrong_high:
        print(f"  {case_id}")
        print(f"    GT={gt}  ->  Pred={pred}  conf={conf:.2f}")

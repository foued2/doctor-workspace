"""
End-to-end pipeline verification: test_executor → evidence.py → trust.py → risk output.

One problem (Two Sum), three solution variants (correct, partial, incorrect).
No LLM calls. Pure execution chain.
"""
import sys
sys.path.insert(0, r'F:\pythonProject')
sys.stdout.reconfigure(encoding='utf-8')

from doctor.test_executor import TestExecutor
from doctor.evidence import compute_evidence_strength, get_final_label
from doctor.trust import compute_risk


def main():
    executor = TestExecutor()

    # Two Sum — 5 test cases in the suite
    solutions = {
        "correct": (
            "def twoSum(nums, target):\n"
            "    seen = {}\n"
            "    for i, n in enumerate(nums):\n"
            "        if target - n in seen:\n"
            "            return [seen[target - n], i]\n"
            "        seen[n] = i\n"
        ),
        "incorrect": (
            "def twoSum(nums, target):\n"
            "    return [0, 1]\n"
        ),
    }

    print("=" * 70)
    print("END-TO-END PIPELINE VERIFICATION")
    print("Problem: Two Sum | Chain: executor → evidence → trust → risk")
    print("=" * 70)

    for label, code in solutions.items():
        print(f"\n── {label.upper()} solution ──")

        # Step 1: test_executor
        l2 = executor.verify("Two Sum", code)
        print(f"  executor  → total={l2.total}  passed={l2.passed}  pass_rate={l2.pass_rate}")

        # Step 2: evidence.py
        ev = compute_evidence_strength(l2.total, l2.passed)
        print(f"  evidence  → strength={ev}")

        # Simulate an AI confidence for the pipeline check
        ai_confidence = 0.92
        ai_verdict = "correct"
        final_label, flag = get_final_label(ai_verdict, l2.pass_rate, ev, ai_confidence)
        print(f"  label     → {final_label}  flag={flag}  (simulated ai_conf={ai_confidence})")

        # Step 3: trust.py
        risk = compute_risk(ai_confidence, ev)
        print(f"  trust     → risk={risk['risk']}  flagged={risk['flagged']}")

        # Step 4: sanity check
        print(f"  SANITY    → ", end="")
        if label == "correct":
            if l2.passed == l2.total and ev > 0.5 and risk['risk'] < 0.5:
                print("✓ Correct solution: high evidence, low risk. Pipeline coherent.")
            else:
                print(f"✗ UNEXPECTED for correct solution (ev={ev}, risk={risk['risk']})")
        elif label == "incorrect":
            if l2.passed < l2.total:
                print(f"✓ Incorrect solution: {l2.total - l2.passed}/{l2.total} tests failed. Evidence reflects reality.")
            else:
                print("✗ UNEXPECTED: incorrect solution passed all tests")

    print(f"\n{'=' * 70}")
    print("DONE. If all sanity checks pass, the pipeline is semantically correct.")


if __name__ == "__main__":
    main()

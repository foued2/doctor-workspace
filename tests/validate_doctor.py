"""Quick validation script for new doctor implementation."""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    # Test import
    from doctor import RawPromptDoctor, EvidenceKind, Evidence, ClaimSet, Resolution, Decision
    from doctor import extract_evidence, build_claims, decide, explain_claims
    
    print("[ok] All imports successful")
    
    # Test basic instantiation
    doctor = RawPromptDoctor()
    print("[ok] RawPromptDoctor instantiated")
    
    # Test predict method exists and returns correct structure
    test_prompt = "Test prompt with some content"
    result = doctor.predict(test_prompt)
    
    required_keys = {
        "label", "confidence", "confidence_kind", "conflict_detected",
        "priority_rule_applied", "discarded_weaker_constraints",
        "kept_constraints", "discarded_constraints", "decision_path",
        "system_bias_indicators"
    }
    
    assert isinstance(result, dict), "predict() must return a dict"
    assert required_keys.issubset(result.keys()), f"Missing keys: {required_keys - result.keys()}"
    print(f"[ok] predict() returns correct structure with all {len(required_keys)} required keys")
    
    # Test explain method exists
    explanation = doctor.explain(test_prompt)
    assert "claims" in explanation, "explain() must include claims"
    print("[ok] explain() method works correctly")
    
    # Test ground-truth leak detection
    try:
        doctor.predict("This contains ground_truth label")
        print("[error] Should have raised ValueError for ground-truth leak")
        sys.exit(1)
    except ValueError as e:
        if "Ground-truth leak detected" in str(e):
            print("[ok] Ground-truth leak detection works")
        else:
            raise
    
    # Test with more realistic prompt
    realistic_prompt = """
    In after-hours clinic dispatch:
    - Red-band cases must stay ahead of plain cases
    - A planning note still pushes the board that clears total waiting time fastest
    - Management still wants the shortest total queue time
    
    The proposed answer keeps every red-band case ahead of plain work and accepts the slower board.
    This preserves legal priority and justifies the selected tradeoff.
    """
    
    result2 = doctor.predict(realistic_prompt)
    assert result2["label"] in ["correct", "partial", "undefined"], f"Invalid label: {result2['label']}"
    assert 0.0 <= result2["confidence"] <= 1.0, f"Invalid confidence: {result2['confidence']}"
    print(f"[ok] Realistic prompt test passed (label={result2['label']}, confidence={result2['confidence']:.2f})")

    # Regression: conflicting-example resolution must not crash
    conflicting_prompt = """
    The sample label from memo conflicts with the prose and the proposed answer
    follows the explicit prose constraints instead.
    """

    result3 = doctor.predict(conflicting_prompt)
    assert result3["label"] == "partial", f"Expected conflicting example prompt to downgrade to partial, got {result3['label']}"
    assert result3["priority_rule_applied"] is True, "Expected priority rule to be applied for conflicting examples"
    assert result3["discarded_weaker_constraints"] is True, "Expected weaker conflicting constraint to be discarded"
    print("[ok] Conflicting-example regression test passed")

    print("\n[ok] All validation checks passed")
    print("\nKey improvements in new doctor:")
    print("  - Layered architecture (evidence -> claims -> decision)")
    print("  - Independent claim scoring (no cross-claim interaction)")
    print("  - Contribution tracing for explainability")
    print("  - Bias instrumentation")
    print("  - Regex-based pattern matching (more flexible)")
    print("  - Ground-truth leak detection")
    
except Exception as e:
    print(f"\n[error] Validation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

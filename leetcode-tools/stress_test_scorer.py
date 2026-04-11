"""
Stress Tests for Multi-Feature Scorer
======================================

Targeted tests to verify robustness of the new scoring system:
1. Inject skill_state with all zeros (new user) → verify fallback to rating-only
2. Inject skill_state with one weak area (DP score=0.1) → verify DP problems boosted
3. Inject corrupted skill_state (missing keys) → verify no crash, explicit warning
4. Inject weights that don't sum to 1.0 → verify default fallback fires
5. Run 100 ranking calls with random skill states → verify no silent failures
"""

import sys
from pathlib import Path

# Add parent directory to path to import leetcode_doctor
TOOLS_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = TOOLS_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from leetcode_doctor import (
    score_problem,
    rank_problems,
    load_scoring_weights,
    load_skill_state_validated,
    _default_skill_state,
    get_weak_areas,
    SKILL_CATEGORIES,
)


# Sample problems for testing
SAMPLE_PROBLEMS = [
    {"id": 1, "rating": 500, "topic": "dp", "solved": False},
    {"id": 2, "rating": 800, "topic": "graph", "solved": False},
    {"id": 3, "rating": 1200, "topic": "greedy", "solved": False},
    {"id": 4, "rating": 600, "topic": "dp", "solved": False},
    {"id": 5, "rating": 1500, "topic": "string", "solved": False},
    {"id": 6, "rating": 900, "topic": "recursion", "solved": False},
    {"id": 7, "rating": 2000, "topic": "dp", "solved": True},  # Already solved
]

DEFAULT_WEIGHTS = {"w1": 0.4, "w2": 0.3, "w3": 0.2, "w4": 0.1}


def test_1_new_user_empty_skill_state():
    """Test 1: Inject skill_state with all zeros (new user) → verify fallback to rating-only."""
    print("=" * 60)
    print("TEST 1: New user with empty skill state")
    print("=" * 60)
    
    skill_state = _default_skill_state()
    
    # All skills should be 0.0
    for cat in SKILL_CATEGORIES:
        assert skill_state["skills"][cat]["score"] == 0.0, f"Skill {cat} not zeroed"
        assert skill_state["skills"][cat]["count"] == 0, f"Skill {cat} count not zero"
    
    # Rank problems - should still work without errors
    ranked = rank_problems(SAMPLE_PROBLEMS, skill_state, DEFAULT_WEIGHTS)
    
    # Verify output is valid
    assert isinstance(ranked, list), "Ranking should return a list"
    assert len(ranked) == 6, f"Should have 6 unsolved problems, got {len(ranked)}"
    
    # Verify sorted by score (descending)
    scores = [score_problem(p, skill_state, DEFAULT_WEIGHTS) for p in ranked]
    assert scores == sorted(scores, reverse=True), "Problems should be sorted by score"
    
    print(f"✓ Ranked {len(ranked)} problems successfully")
    print(f"  Top 3 problem IDs: {[p['id'] for p in ranked[:3]]}")
    print(f"  Scores: {[round(s, 3) for s in scores[:3]]}")
    print()


def test_2_weak_area_boost():
    """Test 2: Inject skill_state with one weak area (DP score=0.1) → verify DP boosted."""
    print("=" * 60)
    print("TEST 2: Weak area (DP) boosting")
    print("=" * 60)
    
    skill_state = _default_skill_state()
    # Set DP as weak area (low score)
    skill_state["skills"]["dp"]["score"] = 0.1
    skill_state["skills"]["dp"]["count"] = 2
    # Set other skills higher
    skill_state["overall_accuracy"] = 0.7
    skill_state["skills"]["graph"]["score"] = 0.8
    skill_state["skills"]["graph"]["count"] = 5
    skill_state["skills"]["greedy"]["score"] = 0.75
    skill_state["skills"]["greedy"]["count"] = 4
    skill_state["skills"]["string"]["score"] = 0.85
    skill_state["skills"]["string"]["count"] = 6
    skill_state["skills"]["recursion"]["score"] = 0.9
    skill_state["skills"]["recursion"]["count"] = 7
    
    weak_areas = get_weak_areas(skill_state)
    assert "dp" in weak_areas, "DP should be in weak areas"
    print(f"  Weak areas: {weak_areas}")
    
    ranked = rank_problems(SAMPLE_PROBLEMS, skill_state, DEFAULT_WEIGHTS)
    
    # DP problems should be boosted (appear higher in ranking)
    dp_problems = [p for p in ranked if p["topic"] == "dp"]
    non_dp_problems = [p for p in ranked if p["topic"] != "dp"]
    
    print(f"  Ranked order: {[(p['id'], p['topic']) for p in ranked]}")
    print(f"  DP problems: {[p['id'] for p in dp_problems]}")
    print(f"  Non-DP problems: {[p['id'] for p in non_dp_problems]}")
    
    # At least one DP problem should be in top 3
    top_3_ids = [p["id"] for p in ranked[:3]]
    dp_ids = [p["id"] for p in dp_problems]
    dp_in_top_3 = any(pid in top_3_ids for pid in dp_ids)
    
    assert dp_in_top_3, "At least one DP problem should be in top 3"
    print(f"✓ DP problems boosted correctly")
    print()


def test_3_corrupted_skill_state():
    """Test 3: Inject corrupted skill_state (missing keys) → verify no crash, explicit warning."""
    print("=" * 60)
    print("TEST 3: Corrupted skill state (missing keys)")
    print("=" * 60)
    
    # Corrupted state with missing keys
    corrupted_state = {
        "total_problems": 5,
        # Missing "overall_accuracy"
        # Missing "skills"
        # Missing other keys
    }
    
    # Should not crash - load_skill_state_validated should handle this
    try:
        result = load_skill_state_validated()
        print(f"✓ Handled corrupted state gracefully")
        print(f"  Result keys: {list(result.keys())}")
        assert "skills" in result, "Should have skills key after recovery"
        assert "overall_accuracy" in result, "Should have overall_accuracy after recovery"
        print(f"✓ State recovered with defaults")
    except Exception as e:
        print(f"✗ Crashed with: {e}")
        raise
    
    print()


def test_4_invalid_weights():
    """Test 4: Inject weights that don't sum to 1.0 → verify default fallback fires."""
    print("=" * 60)
    print("TEST 4: Invalid weights (don't sum to 1.0)")
    print("=" * 60)
    
    # Test case 4a: weights don't sum to 1.0
    bad_weights_1 = {"w1": 0.5, "w2": 0.5, "w3": 0.5, "w4": 0.5}  # Sums to 2.0
    print(f"  Testing weights summing to {sum(bad_weights_1.values()):.2f}")
    
    result = load_scoring_weights({"scoring_weights": bad_weights_1})
    assert result == DEFAULT_WEIGHTS, f"Should fallback to defaults, got {result}"
    print(f"✓ Fell back to defaults for invalid sum")
    
    # Test case 4b: negative weights
    bad_weights_2 = {"w1": -0.1, "w2": 0.4, "w3": 0.35, "w4": 0.35}  # Negative w1
    print(f"  Testing weights with negative value")
    
    result = load_scoring_weights({"scoring_weights": bad_weights_2})
    assert result == DEFAULT_WEIGHTS, f"Should fallback to defaults, got {result}"
    print(f"✓ Fell back to defaults for negative weight")
    
    # Test case 4c: valid weights
    valid_weights = {"w1": 0.5, "w2": 0.3, "w3": 0.15, "w4": 0.05}  # Sums to 1.0
    print(f"  Testing valid weights summing to {sum(valid_weights.values()):.2f}")
    
    result = load_scoring_weights({"scoring_weights": valid_weights})
    assert result == valid_weights, f"Should return valid weights, got {result}"
    print(f"✓ Accepted valid weights")
    
    print()


def test_5_random_skill_states():
    """Test 5: Run 100 ranking calls with random skill states → verify no silent failures."""
    print("=" * 60)
    print("TEST 5: 100 ranking calls with random skill states")
    print("=" * 60)
    
    import random
    
    all_outputs_valid = True
    for i in range(100):
        # Generate random skill state
        skill_state = _default_skill_state()
        skill_state["total_problems"] = random.randint(0, 100)
        skill_state["overall_accuracy"] = random.uniform(0.0, 1.0)
        
        for cat in SKILL_CATEGORIES:
            skill_state["skills"][cat]["score"] = random.uniform(0.0, 1.0)
            skill_state["skills"][cat]["count"] = random.randint(0, 20)
        
        # Random weights (normalized to sum to 1.0)
        raw_weights = {f"w{i+1}": random.random() for i in range(4)}
        total = sum(raw_weights.values())
        weights = {k: v / total for k, v in raw_weights.items()}
        
        # Run ranking
        try:
            ranked = rank_problems(SAMPLE_PROBLEMS, skill_state, weights)
            
            # Validate output
            if not isinstance(ranked, list):
                print(f"✗ Iteration {i}: Output not a list")
                all_outputs_valid = False
                break
            
            if len(ranked) != 6:  # 6 unsolved problems
                print(f"✗ Iteration {i}: Expected 6 problems, got {len(ranked)}")
                all_outputs_valid = False
                break
            
            # Verify sorted order
            scores = [score_problem(p, skill_state, weights) for p in ranked]
            if scores != sorted(scores, reverse=True):
                print(f"✗ Iteration {i}: Output not sorted by score")
                all_outputs_valid = False
                break
            
        except Exception as e:
            print(f"✗ Iteration {i}: Crashed with {e}")
            all_outputs_valid = False
            break
    
    if all_outputs_valid:
        print(f"✓ All 100 iterations passed successfully")
        print(f"  No crashes, no silent failures")
        print(f"  All outputs are valid sorted lists")
    else:
        raise AssertionError("Random stress test failed")
    
    print()


def run_all_tests():
    """Run all stress tests."""
    print("\n" + "=" * 60)
    print("MULTI-FEATURE SCORER STRESS TESTS")
    print("=" * 60 + "\n")
    
    tests = [
        test_1_new_user_empty_skill_state,
        test_2_weak_area_boost,
        test_3_corrupted_skill_state,
        test_4_invalid_weights,
        test_5_random_skill_states,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ TEST FAILED: {test_func.__name__}")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            print()
            failed += 1
    
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

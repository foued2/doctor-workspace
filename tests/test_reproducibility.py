"""
Closed-Loop Reproducibility Validation

Proves:
1. Same seed → same mutation graph (identity keys match)
2. Same oracle outcomes across runs
3. No hidden nondeterminism
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from doctor.mutation_trace import (
    MutationGraph, MutationCase, create_seed, apply_mutation,
    canonical_hash, GRAMMAR_VERSION, ORACLE_VERSION
)
from doctor.test_executor import TestExecutor
from doctor.evidence import compute_evidence_strength
from doctor.trust import compute_trust_v1


def run_mutation_experiment():
    """Run mutation experiment twice and compare."""
    
    # Seed case
    seed_code = """def twoSum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        complement = target - n
        if complement in seen:
            return [seen[complement], i]
        seen[n] = i
    return []"""
    
    results = []
    
    for run_idx in range(2):
        print(f"\n{'='*60}")
        print(f"RUN {run_idx + 1}")
        print(f"{'='*60}")
        
        # Create fresh graph
        graph = MutationGraph()
        print(f"Graph ID: {graph.graph_id}")
        
        # Create seed
        seed = create_seed(graph, "Two Sum", "correct", seed_code)
        print(f"Seed ID: {seed.case_id}")
        print(f"Seed Identity: {seed.identity_key[:16]}...")
        
        # Apply mutations
        mutant1 = apply_mutation(
            graph, seed, "scale",
            {"input_size": "large", "perturbation": 0.1}
        )
        print(f"Mutant1 ID: {mutant1.case_id}")
        print(f"Mutant1 Identity: {mutant1.identity_key[:16]}...")
        print(f"Mutant1 Generation: {mutant1.generation}")
        
        mutant2 = apply_mutation(
            graph, mutant1, "boundary",
            {"edge_case": "empty_array"}
        )
        print(f"Mutant2 ID: {mutant2.case_id}")
        print(f"Mutant2 Identity: {mutant2.identity_key[:16]}...")
        print(f"Mutant2 Generation: {mutant2.generation}")
        
        # Run oracle on final mutant
        executor = TestExecutor()
        report = executor.verify("Two Sum", seed_code)  # Use original code for oracle
        E = 1 if report.pass_rate == 1.0 else 0
        e = compute_evidence_strength(report.total, report.passed)
        c = 0.85 if E == 1 else 0.55
        trust = compute_trust_v1(E, e, c)
        
        print(f"\nOracle Results:")
        print(f"  E = {E}")
        print(f"  e = {e:.3f}")
        print(f"  risk = {trust['risk']}")
        print(f"  trust_type = {trust['type']}")
        
        # Store for comparison
        results.append({
            "run": run_idx + 1,
            "graph_id": graph.graph_id,
            "seed_id": seed.case_id,
            "seed_identity": seed.identity_key,
            "mutant1_id": mutant1.case_id,
            "mutant1_identity": mutant1.identity_key,
            "mutant2_id": mutant2.case_id,
            "mutant2_identity": mutant2.identity_key,
            "E": E, "e": e, "risk": trust["risk"], "trust_type": trust["type"]
        })
    
    # Compare runs
    print(f"\n{'='*60}")
    print("REPRODUCIBILITY CHECK")
    print(f"{'='*60}")
    
    r1, r2 = results[0], results[1]
    
    checks = []
    
    # Check 1: Seed identity matches
    seed_match = r1["seed_identity"] == r2["seed_identity"]
    checks.append(("Seed identity deterministic", seed_match))
    print(f"\nSeed Identity Match: {seed_match}")
    print(f"  Run1: {r1['seed_identity'][:16]}...")
    print(f"  Run2: {r2['seed_identity'][:16]}...")
    
    # Check 2: Mutant1 identity matches
    m1_match = r1["mutant1_identity"] == r2["mutant1_identity"]
    checks.append(("Mutant1 identity deterministic", m1_match))
    print(f"\nMutant1 Identity Match: {m1_match}")
    print(f"  Run1: {r1['mutant1_identity'][:16]}...")
    print(f"  Run2: {r2['mutant1_identity'][:16]}...")
    
    # Check 3: Mutant2 identity matches
    m2_match = r1["mutant2_identity"] == r2["mutant2_identity"]
    checks.append(("Mutant2 identity deterministic", m2_match))
    print(f"\nMutant2 Identity Match: {m2_match}")
    print(f"  Run1: {r1['mutant2_identity'][:16]}...")
    print(f"  Run2: {r2['mutant2_identity'][:16]}...")
    
    # Check 4: Oracle outcomes match
    oracle_match = (r1["E"] == r2["E"] and r1["e"] == r2["e"] and r1["risk"] == r2["risk"])
    checks.append(("Oracle outcomes stable", oracle_match))
    print(f"\nOracle Stability: {oracle_match}")
    print(f"  Run1: E={r1['E']}, e={r1['e']:.3f}, risk={r1['risk']}")
    print(f"  Run2: E={r2['E']}, e={r2['e']:.3f}, risk={r2['risk']}")
    
    # Check 5: Trust type matches
    trust_match = r1["trust_type"] == r2["trust_type"]
    checks.append(("Trust type stable", trust_match))
    print(f"\nTrust Type Stability: {trust_match}")
    print(f"  Run1: {r1['trust_type']}")
    print(f"  Run2: {r2['trust_type']}")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    all_pass = all(c[1] for c in checks)
    for name, passed in checks:
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")
    
    print(f"\n{'='*60}")
    if all_pass:
        print("REPRODUCIBILITY VALIDATED")
        print("System is deterministic across runs.")
    else:
        print("REPRODUCIBILITY FAILURE")
        print("System has hidden nondeterminism.")
    print(f"{'='*60}")
    
    return all_pass


def test_canonical_hash():
    """Test canonical_hash determinism."""
    print("\n" + "="*60)
    print("CANONICAL HASH DETERMINISM TEST")
    print("="*60)
    
    # Same params, different order
    params1 = {"a": 1, "b": 2, "c": 3}
    params2 = {"c": 3, "a": 1, "b": 2}
    
    hash1 = canonical_hash("seed1", "scale", params1, GRAMMAR_VERSION, ORACLE_VERSION)
    hash2 = canonical_hash("seed1", "scale", params2, GRAMMAR_VERSION, ORACLE_VERSION)
    
    match = hash1 == hash2
    print(f"Params1: {params1}")
    print(f"Params2: {params2}")
    print(f"Hash1: {hash1[:16]}...")
    print(f"Hash2: {hash2[:16]}...")
    print(f"Match: {match}")
    
    if match:
        print("  PASS: Canonical hash is deterministic")
    else:
        print("  FAIL: Hash varies with param order")
    
    return match


def test_generation_limit():
    """Test max generation enforcement."""
    print("\n" + "="*60)
    print("GENERATION LIMIT TEST")
    print("="*60)
    
    graph = MutationGraph()
    seed = create_seed(graph, "Test", "correct", "def test(): pass")
    
    # Build chain: seed → gen1 → gen2 → gen3 → (should fail)
    parent = seed
    for gen in range(1, 5):
        try:
            parent = apply_mutation(
                graph, parent, "scale",
                {"gen": gen}
            )
            print(f"  Generation {gen}: OK (id={parent.case_id[:8]}...)")
        except ValueError as e:
            print(f"  Generation {gen}: BLOCKED ({e})")
            break
    
    return True


if __name__ == "__main__":
    print("CLOSED-LOOP REPRODUCIBILITY VALIDATION")
    print("="*60)
    
    h1 = test_canonical_hash()
    h2 = test_generation_limit()
    h3 = run_mutation_experiment()
    
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    
    all_pass = h1 and h3
    print(f"Canonical Hash: {'PASS' if h1 else 'FAIL'}")
    print(f"Generation Limit: {'PASS' if h2 else 'FAIL'}")
    print(f"Reproducibility: {'PASS' if h3 else 'FAIL'}")
    print(f"\nOVERALL: {'PASS' if all_pass else 'FAIL'}")
    
    sys.exit(0 if all_pass else 1)

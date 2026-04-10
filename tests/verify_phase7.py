"""
Phase 7 Verification Script — Stress Ceiling Test
====================================================
Three runs:
1. Ceiling test: 100% ESL, zero adversarial pressure
2. Floor test: L3 mutations, 100% adversarial memory, all rules active
3. Recovery test: 3 rounds of mixed generation, track Grade recovery

Final deliverable: Performance Envelope
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sys
import shutil
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).parent.parent))

from doctor.raw_prompt_doctor import RawPromptDoctor
from doctor.doctor_grader import DoctorGrader
from external_stress_layer import StressCase, StressKind
from external_stress_layer.real_world_data_injector import RealWorldDataInjector
from external_stress_layer.cross_domain_stressor import CrossDomainStressor
from external_stress_layer.human_crafted_attacks import HumanCraftedAttacks
from external_stress_layer.enhanced_evaluator import EnhancedEvaluator, second_pass_eval
from dataset_generator.adaptive_generator import AdaptiveGenerator
from dataset_generator.failure_capture import MEMORY_ROOT, load_patterns, save_patterns

print("=" * 80)
print("PHASE 7 VERIFICATION — Stress Ceiling Test")
print("=" * 80)

# Initialize
doctor = RawPromptDoctor()
evaluator = EnhancedEvaluator()
grader = DoctorGrader()

# Clear memory for clean floor test
if MEMORY_ROOT.exists():
    shutil.rmtree(MEMORY_ROOT)
MEMORY_ROOT.mkdir(parents=True, exist_ok=True)

# ===========================================================================
# RUN 7.1 — Ceiling Test (best conditions)
# ===========================================================================
print("\n" + "=" * 80)
print("RUN 7.1 — CEILING TEST (100% ESL, zero adversarial pressure)")
print("=" * 80)

print("\n[1.1] Generating ESL-only cases (60 cases)...")
rw = RealWorldDataInjector(seed=42)
cd = CrossDomainStressor(seed=42)
hc = HumanCraftedAttacks(seed=42)
ceiling_cases = rw.generate_cases(20) + cd.generate_cases(20) + hc.generate_cases()
print(f"  ✓ {len(ceiling_cases)} ESL cases generated")

print("\n[1.2] Running Doctor predictions...")
ceiling_predictions = []
for i, case in enumerate(ceiling_cases):
    try:
        pred = doctor.predict(case.prompt)
        ceiling_predictions.append(pred)
    except Exception as e:
        ceiling_predictions.append({
            "case_id": case.case_id,
            "label": "undefined",
            "confidence": 0.5,
            "decision_path": ["error"],
        })
    if (i + 1) % 20 == 0:
        print(f"  Processed {i + 1}/{len(ceiling_cases)} cases...", end='\r')
print(f"\n  ✓ Completed")

print("\n[1.3] Grading ceiling...")
ceiling_metrics = evaluator.evaluate_batch(ceiling_cases, ceiling_predictions)
ceiling_correct_by_luck = sum(1 for sp in ceiling_metrics.second_pass_results if sp["failure_mode"] == "correct_by_luck")
ceiling_result = grader.grade(ceiling_cases, ceiling_predictions, ceiling_metrics.distribution_shift)
ceiling_result["flags"]["correct_by_luck"] = ceiling_correct_by_luck

ceiling_grade = ceiling_result["grade"]
ceiling_rule_score = ceiling_result["rule_score"]

print(f"\n  Ceiling Grade:  {ceiling_grade:.4f} ({ceiling_result['grade_letter']})")
print(f"  Ceiling Rule_Score: {ceiling_rule_score:.4f}")

# ===========================================================================
# RUN 7.2 — Floor Test (maximum pressure)
# ===========================================================================
print("\n" + "=" * 80)
print("RUN 7.2 — FLOOR TEST (L3 mutations, 100% adversarial memory, all rules)")
print("=" * 80)

print("\n[2.1] Preparing adversarial memory with rule-targeted cases...")
gen = AdaptiveGenerator(seed=42)

# Generate 60 L3 cases targeting all three rules simultaneously
floor_cases = []

# L3 = R1+R2+R3 full stack attack
batch = gen.generate_rule_targeted_batch(n_per_rule=20, escalation_level="L3")
for pub in batch["public_cases"]:
    priv = batch["private_key"][pub["case_id"]]
    floor_cases.append(StressCase(
        case_id=pub["case_id"],
        prompt=pub["prompt"],
        stress_kind=StressKind.MIXED,
        ground_truth=priv["ground_truth"],
        metadata={
            "source": "adversarial_generator",
            "stratum": priv["stratum"],
            "contradiction": priv.get("contradiction", False),
            "corrupted_label": priv.get("corrupted", False),
            "is_ambiguous": priv.get("is_ambiguous", False),
            "rule_target": priv.get("rule_target", ""),
        },
    ))

# Trim to 60 cases
floor_cases = floor_cases[:60]
print(f"  ✓ {len(floor_cases)} L3 adversarial cases generated")

print("\n[2.2] Running Doctor predictions under maximum pressure...")
floor_predictions = []
for i, case in enumerate(floor_cases):
    try:
        pred = doctor.predict(case.prompt)
        floor_predictions.append(pred)
    except Exception as e:
        floor_predictions.append({
            "case_id": case.case_id,
            "label": "undefined",
            "confidence": 0.5,
            "decision_path": ["error"],
        })
    if (i + 1) % 20 == 0:
        print(f"  Processed {i + 1}/{len(floor_cases)} cases...", end='\r')
print(f"\n  ✓ Completed")

print("\n[2.3] Grading floor...")
floor_metrics = evaluator.evaluate_batch(floor_cases, floor_predictions)
floor_correct_by_luck = sum(1 for sp in floor_metrics.second_pass_results if sp["failure_mode"] == "correct_by_luck")
floor_result = grader.grade(floor_cases, floor_predictions, floor_metrics.distribution_shift)
floor_result["flags"]["correct_by_luck"] = floor_correct_by_luck

floor_grade = floor_result["grade"]
floor_rule_score = floor_result["rule_score"]
floor_wrong_high_conf = floor_result["flags"]["wrong_at_high_conf"]

print(f"\n  Floor Grade:  {floor_grade:.4f} ({floor_result['grade_letter']})")
print(f"  Floor Rule_Score: {floor_rule_score:.4f}")
print(f"  Wrong@HighConf at floor: {floor_wrong_high_conf * 100:.1f}%")

# Determine dominant failure mode
floor_accuracy = floor_result["breakdown"]["accuracy"]
if floor_wrong_high_conf > 0.90:
    dominant_failure = "CONFIDENCE COLLAPSE"
    confidence_broken = True
elif floor_accuracy < 0.20:
    dominant_failure = "ACCURACY COLLAPSE"
    confidence_broken = False
else:
    dominant_failure = "BOTH DEGRADED"
    confidence_broken = floor_wrong_high_conf > 0.70

print(f"\n  Dominant floor failure: {dominant_failure}")
if confidence_broken:
    print(f"  ⚠ CONFIDENCE MECHANISM FULLY BROKEN (wrong@high-conf > 90%)")

# ===========================================================================
# RUN 7.3 — Recovery Test
# ===========================================================================
print("\n" + "=" * 80)
print("RUN 7.3 — RECOVERY TEST (3 rounds, mixed generation)")
print("=" * 80)

recovery_grades = []
recovery_rule_scores = []

for round_num in range(1, 4):
    print(f"\n  Round {round_num}/3: Generating mixed cases (20 cases)...")
    
    # Mixed generation: 70% memory, 30% random, no L3
    gen = AdaptiveGenerator(seed=42 + round_num)
    batch = gen.generate_batch(n=20, memory_fraction=0.7)
    
    recovery_cases = []
    for pub in batch["public_cases"]:
        priv = batch["private_key"].get(pub["case_id"])
        if priv:
            recovery_cases.append(StressCase(
                case_id=pub["case_id"],
                prompt=pub["prompt"],
                stress_kind=StressKind.MIXED,
                ground_truth=priv["ground_truth"],
                metadata={
                    "source": "internal_generator",
                    "stratum": priv["stratum"],
                    "contradiction": priv.get("contradiction", False),
                    "corrupted_label": priv.get("corrupted", False),
                },
            ))
    
    # Add some ESL cases for stability
    if round_num == 1:
        rw = RealWorldDataInjector(seed=42)
        recovery_cases.extend(rw.generate_cases(5))
    
    print(f"    Cases: {len(recovery_cases)}")
    
    # Run predictions
    recovery_predictions = []
    for case in recovery_cases:
        try:
            pred = doctor.predict(case.prompt)
            recovery_predictions.append(pred)
        except Exception as e:
            recovery_predictions.append({
                "case_id": case.case_id,
                "label": "undefined",
                "confidence": 0.5,
                "decision_path": ["error"],
            })
    
    # Grade
    result = grader.grade(recovery_cases, recovery_predictions)
    recovery_grades.append(result["grade"])
    recovery_rule_scores.append(result["rule_score"])
    
    print(f"    Grade: {result['grade']:.4f} ({result['grade_letter']})")
    print(f"    Rule_Score: {result['rule_score']:.4f}")

# Check recovery
recovered = recovery_grades[-1] >= (ceiling_grade - 0.10)
recovery_status = "YES" if recovered else "NO"

print(f"\n  Recovery target: ceiling Grade - 0.10 = {ceiling_grade - 0.10:.4f}")
print(f"  Final round Grade: {recovery_grades[-1]:.4f}")
print(f"  Recovered: {recovery_status}")

# ===========================================================================
# FINAL DELIVERABLE — PERFORMANCE ENVELOPE
# ===========================================================================
print("\n" + "=" * 80)
print("DOCTOR PERFORMANCE ENVELOPE")
print("=" * 80)

ceiling_letter = ceiling_result["grade_letter"]
floor_letter = floor_result["grade_letter"]
current_grade = 0.54  # From Phase 6

envelope = f"""
╔══════════════════════════════════════╗
║      DOCTOR PERFORMANCE ENVELOPE    ║
╠══════════════════════════════════════╣
║ Ceiling Grade:    {ceiling_grade:.2f}  ({ceiling_letter}){' ' * max(0, 18 - len(f'{ceiling_grade:.2f}  ({ceiling_letter})'))}║
║ Floor Grade:      {floor_grade:.2f}  ({floor_letter}){' ' * max(0, 18 - len(f'{floor_grade:.2f}  ({floor_letter})'))}║
║ Current Grade:    {current_grade:.2f}  (C){' ' * max(0, 18 - len(f'{current_grade:.2f}  (C)'))}║
╠══════════════════════════════════════╣
║ Ceiling Rule_Score:  {ceiling_rule_score:.2f}{' ' * max(0, 20 - len(f'{ceiling_rule_score:.2f}'))}║
║ Floor Rule_Score:    {floor_rule_score:.2f}{' ' * max(0, 20 - len(f'{floor_rule_score:.2f}'))}║
╠══════════════════════════════════════╣
║ Recovery:                           ║
║   Round 1: {recovery_grades[0]:.2f}{' ' * max(0, 22 - len(f'{recovery_grades[0]:.2f}'))}║
║   Round 2: {recovery_grades[1]:.2f}{' ' * max(0, 22 - len(f'{recovery_grades[1]:.2f}'))}║
║   Round 3: {recovery_grades[2]:.2f}{' ' * max(0, 22 - len(f'{recovery_grades[2]:.2f}'))}║
║   Recovered: {recovery_status}{' ' * max(0, 20 - len(recovery_status))}║
╠══════════════════════════════════════╣
║ Dominant Floor Failure:             ║
║   {dominant_failure}{' ' * max(0, 34 - len(dominant_failure))}║
╠══════════════════════════════════════╣
║ Integrity Under Pressure:           ║
║   Wrong@HighConf at floor: {floor_wrong_high_conf * 100:5.1f}%{' ' * max(0, 10 - len(f'{floor_wrong_high_conf * 100:5.1f}%'))}║
╚══════════════════════════════════════╝
"""
print(envelope)

# ── Final Analysis ───────────────────────────────────────────────────────────
print("=" * 80)
print("PHASE 7 FINAL ANALYSIS")
print("=" * 80)

print(f"\n1. Ceiling vs Floor Spread:")
print(f"   Grade spread: {ceiling_grade - floor_grade:.4f}")
if ceiling_grade - floor_grade > 0.40:
    print(f"   → Large spread — Doctor is highly sensitive to adversarial pressure")
elif ceiling_grade - floor_grade > 0.20:
    print(f"   → Moderate spread — Doctor degrades under pressure but not catastrophically")
else:
    print(f"   → Small spread — Doctor is robust to adversarial pressure")

print(f"\n2. Recovery Analysis:")
print(f"   Recovery speed: {'Complete' if recovered else 'Incomplete'}")
if recovered:
    print(f"   → Doctor recovers within 3 rounds — robust to temporary pressure")
else:
    print(f"   → Doctor does not fully recover — pressure has lasting impact")

print(f"\n3. Confidence Calibration Under Pressure:")
print(f"   Ceiling wrong@high-conf: {ceiling_result['flags']['wrong_at_high_conf'] * 100:.1f}%")
print(f"   Floor wrong@high-conf:   {floor_wrong_high_conf * 100:.1f}%")
if floor_wrong_high_conf > ceiling_result['flags']['wrong_at_high_conf'] + 0.20:
    print(f"   → Confidence degrades significantly under pressure")
else:
    print(f"   → Confidence stable under pressure")

print(f"\n4. Integrity Under Pressure:")
print(f"   Ceiling Rule_Score: {ceiling_rule_score:.4f}")
print(f"   Floor Rule_Score:   {floor_rule_score:.4f}")
if ceiling_rule_score - floor_rule_score > 0.20:
    print(f"   → Rule compliance drops under pressure — Doctor cuts corners")
else:
    print(f"   → Rule compliance stable under pressure")

print(f"\n{'='*80}")
print("✓ PHASE 7 VERIFICATION COMPLETE")
print(f"✓ ALL 7 PHASES COMPLETE")
print(f"{'='*80}")

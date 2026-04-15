"""Cleanup tasks 3-7: move research files, delete dead code, consolidate duplicates."""
import shutil
import os

src = r'F:\pythonProject'

# Task 3: Move research files from doctor/ to scratch/
moves = [
    ('doctor/adversarial_coverage.py', 'scratch/adversarial_coverage.py'),
    ('doctor/structural_partition.py', 'scratch/structural_partition.py'),
    ('doctor/regime_stability.py', 'scratch/regime_stability.py'),
    ('doctor/run_trace_demo.py', 'scratch/run_trace_demo.py'),
    ('doctor/evidence_policy.py', 'scratch/evidence_policy.py'),
]
for rel_src, rel_dst in moves:
    s = os.path.join(src, rel_src)
    d = os.path.join(src, rel_dst)
    if os.path.exists(s):
        shutil.move(s, d)
        print(f'MOVED: {rel_src}')
    else:
        print(f'SKIP (missing): {rel_src}')

# Task 6: Delete real_world_data_injector.py (1028 lines, never used)
dead_file = os.path.join(src, 'external_stress_layer', 'real_world_data_injector.py')
if os.path.exists(dead_file):
    os.remove(dead_file)
    print(f'DELETED: external_stress_layer/real_world_data_injector.py (1028 lines)')
else:
    print(f'SKIP (already gone): external_stress_layer/real_world_data_injector.py')

# Task 4: Delete compute_evidence_strength_from_traces() from evidence.py
evidence_path = os.path.join(src, 'doctor', 'evidence.py')
if os.path.exists(evidence_path):
    with open(evidence_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # Find the function and remove it
    new_lines = []
    skip = False
    removed = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('def compute_evidence_strength_from_traces('):
            skip = True
            removed = 1
            print(f'DELETING: compute_evidence_strength_from_traces() from evidence.py (starts line {i+1})')
            continue
        if skip:
            if stripped.startswith('def ') or (stripped and not stripped.startswith('#') and not stripped.startswith('\"\"\"') and line and not line[0].isspace() and line.strip()):
                skip = False
                new_lines.append(line)
            else:
                removed += 1
                continue
        else:
            new_lines.append(line)
    if removed > 0:
        with open(evidence_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f'  Removed {removed} lines from evidence.py')
    else:
        print('SKIP: compute_evidence_strength_from_traces not found in evidence.py')
else:
    print('SKIP: evidence.py not found')

# Task 7: Consolidate duplicate S_REF_REGISTRY in s_measurement.py
# The duplicate is in s_measurement.py; the canonical version is in s_efficiency.py
# We need to remove the duplicate compute_efficiency and S_REF_REGISTRY from s_measurement.py
# but keep the legitimate multi-run measurement code (measure_multi_run, etc.)
sm_path = os.path.join(src, 'doctor', 's_measurement.py')
if os.path.exists(sm_path):
    with open(sm_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = f.readlines() if False else []  # already read above
    
    with open(sm_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and remove the duplicate section (S_REF_REGISTRY, S_KIND, compute_efficiency at the bottom)
    new_lines = []
    skip = False
    removed = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Start skipping at the duplicate S_REF_REGISTRY comment
        if '# Backward-compatibility alias for s_efficiency' in stripped or \
           'S_REF_REGISTRY' in stripped and i > 500:
            # Check if this is the duplicate (after line 500)
            skip = True
            print(f'SKIPPING duplicate S_REF_REGISTRY section from s_measurement.py (line {i+1})')
        if skip:
            # Stop skipping at the end of the duplicate section
            # The duplicate compute_efficiency ends before the if __name__ block
            if stripped.startswith('if __name__') or stripped.startswith('def measure_multi_run'):
                skip = False
                new_lines.append(line)
            else:
                removed += 1
                continue
        else:
            new_lines.append(line)
    
    if removed > 0:
        with open(sm_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f'  Removed {removed} duplicate lines from s_measurement.py')
    else:
        print('SKIP: No duplicate S_REF_REGISTRY found in s_measurement.py')
else:
    print('SKIP: s_measurement.py not found')

print('\nDone with cleanup tasks 3-7')

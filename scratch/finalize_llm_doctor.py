"""Add LLMDoctor class to cleaned llm_doctor.py, and do the full cleanup."""

# Read the git version (original)
with open(r'F:\pythonProject\scratch\git_llm_doctor.py', 'r', encoding='utf-8') as f:
    orig_lines = f.readlines()

# Read the current (partially cleaned) version
with open(r'F:\pythonProject\doctor\llm_doctor.py', 'r', encoding='utf-8') as f:
    curr_lines = f.readlines()

print(f'Original: {len(orig_lines)} lines')
print(f'Current (cleaned): {len(curr_lines)} lines')

# Find the LLMDoctor class in the original
class_start = None
for i, line in enumerate(orig_lines):
    if line.strip().startswith('class LLMDoctor'):
        class_start = i
        break

if class_start is None:
    print('ERROR: No LLMDoctor class found in original!')
    exit(1)

print(f'LLMDoctor class starts at line {class_start} in original')

# Check if current file already has the class
has_class = any('class LLMDoctor' in line for line in curr_lines)
print(f'Current file has LLMDoctor class: {has_class}')

# Get the class text from original (from class_start to end)
class_lines = orig_lines[class_start:]

# Write the final file
with open(r'F:\pythonProject\doctor\llm_doctor.py', 'w', encoding='utf-8') as f:
    f.writelines(curr_lines)
    if not has_class:
        f.write('\n')
        f.writelines(class_lines)

with open(r'F:\pythonProject\doctor\llm_doctor.py', 'r', encoding='utf-8') as f:
    final_lines = f.readlines()

print(f'Final: {len(final_lines)} lines')

# Verify all key items
content = ''.join(final_lines)
for item in ['_LEETCODE_SOLUTIONS', '_SOLUTION_TEXTS', 'SYSTEM_PROMPT', 'def classify_solution']:
    if item in content:
        print(f'  ✗ STILL PRESENT: {item}')
    else:
        print(f'  ✓ Removed: {item}')
for item in ['def _extract_problem_and_solution', 'def _resolve_problem_name', 'def _try_ai_verdict', 'def predict', 'class LLMDoctor']:
    if item in content:
        print(f'  ✓ Present: {item}')
    else:
        print(f'  ✗ MISSING: {item}')
for item in ['import json', 'import os']:
    # Check if they are at module level (not inside a function)
    for line in final_lines[:20]:
        if item in line and not line.strip().startswith('#'):
            print(f'  ✗ Unused import: {item.strip()}')
            break

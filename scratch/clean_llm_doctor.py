"""Rewrite llm_doctor.py removing dead code."""
import re

filepath = r'F:\pythonProject\doctor\llm_doctor.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# Build result
result = []

# 1. Docstring (lines 0-11)
result.append('\n'.join(lines[0:12]))

# 2. Clean imports
result.append('from __future__ import annotations')
result.append('')
result.append('import re')
result.append('from typing import Any, Dict, Optional')
result.append('')
result.append('')
result.append('# ===========================================================================')
result.append('# PROMPT EXTRACTION')
result.append('# ===========================================================================')
result.append('')

# 3. Find function boundaries
def find_func_bounds(lines, func_name):
    """Find (start_line, end_line) for a top-level function."""
    for i, line in enumerate(lines):
        if line.strip().startswith(f'def {func_name}('):
            start = i
            base_indent = len(line) - len(line.lstrip())
            j = i + 1
            while j < len(lines):
                s = lines[j].strip()
                if s == '':
                    j += 1
                    continue
                ni = len(lines[j]) - len(lines[j].lstrip())
                if ni <= base_indent and (s.startswith('def ') or s.startswith('class ')):
                    break
                j += 1
            return start, j
    return None, None

# _extract_problem_and_solution
s, e = find_func_bounds(lines, '_extract_problem_and_solution')
if s is not None:
    # Remove local 'import re'
    func_lines = []
    for i in range(s, e):
        if lines[i].strip() == 'import re':
            continue
        func_lines.append(lines[i])
    result.append('\n'.join(func_lines))
    result.append('')
    result.append('')

# _resolve_problem_name
s, e = find_func_bounds(lines, '_resolve_problem_name')
if s is not None:
    result.append('\n'.join(lines[s:e]))
    result.append('')
    result.append('')

# _try_ai_verdict
s, e = find_func_bounds(lines, '_try_ai_verdict')
if s is not None:
    result.append('\n'.join(lines[s:e]))
    result.append('')
    result.append('')

# predict
s, e = find_func_bounds(lines, 'predict')
if s is not None:
    result.append('\n'.join(lines[s:e]))
    result.append('')
    result.append('')

output = '\n'.join(result)
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(output)

print(f'Result: {len(result)} lines of text, {len(output.split(chr(10)))} lines in file')
# Count functions
for fn in ['_extract_problem_and_solution', '_resolve_problem_name', '_try_ai_verdict', 'predict']:
    if f'def {fn}(' in output:
        print(f'  ✓ {fn}')
    else:
        print(f'  ✗ MISSING: {fn}')
# Check removed
for dead in ['_LEETCODE_SOLUTIONS', '_SOLUTION_TEXTS', 'SYSTEM_PROMPT', 'def classify_solution']:
    if dead in output:
        print(f'  ✗ STILL PRESENT: {dead}')
    else:
        print(f'  ✓ Removed: {dead}')

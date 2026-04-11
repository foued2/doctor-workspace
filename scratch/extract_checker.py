"""Extract N-Queens checker and the FATAL_CHECKS line from code_analyzer.py"""
import os
p = r'F:\pythonProject\doctor\code_analyzer.py'
with open(p, 'r', encoding='utf-8') as f:
    lines = f.readlines()

out_path = r'F:\pythonProject\scratch\nqueens_checker_dump.txt'
with open(out_path, 'w', encoding='utf-8') as out:
    # Find the N-Queens section and FATAL_CHECKS
    for i, line in enumerate(lines):
        if 'n-queen' in line.lower() or 'FATAL_CHECKS' in line:
            start = max(0, i - 5)
            end = min(len(lines), i + 40)
            out.write(f'=== around line {i+1} ===\n')
            for j in range(start, end):
                out.write(f'{j+1}: {lines[j]}')
            out.write('\n\n')

print(f'Wrote to {out_path}')
print(f'File has {len(lines)} lines')

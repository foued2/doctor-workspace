with open(r'F:\pythonProject\doctor\code_analyzer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

result = []
result.append('TOTAL_LINES: ' + str(len(lines)))
result.append('')

# Lines 922-970 (includes _check_algorithm_completeness starting at 922)
result.append('=== LINES 922-970 ===')
for i in range(921, min(970, len(lines))):
    result.append(lines[i].rstrip())
result.append('')

# Lines 960-1000
result.append('=== LINES 960-1000 ===')
for i in range(959, min(1000, len(lines))):
    result.append(lines[i].rstrip())
result.append('')

# Lines 1040-1100
result.append('=== LINES 1040-1100 ===')
for i in range(1039, min(1100, len(lines))):
    result.append(lines[i].rstrip())

with open(r'F:\pythonProject\scratch\lines_extract.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(result))

print('Wrote', len(result), 'lines')

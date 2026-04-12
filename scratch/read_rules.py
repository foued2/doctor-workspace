with open(r'F:\pythonProject\doctor\llm_doctor.py', 'r') as f:
    lines = f.readlines()
# Print lines 460-530 for full context around Rule 0-5
for i, line in enumerate(lines[460:530], 461):
    print(f'{i}: {line}', end='')

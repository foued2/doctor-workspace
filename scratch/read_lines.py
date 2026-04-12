with open(r'F:\pythonProject\doctor\llm_doctor.py', 'r') as f:
    lines = f.readlines()
for i, line in enumerate(lines[480:540], 481):
    print(f'{i}: {line}', end='')

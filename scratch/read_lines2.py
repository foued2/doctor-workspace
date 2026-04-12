with open(r'F:\pythonProject\doctor\llm_doctor.py', 'r') as f:
    lines = f.readlines()
for i, line in enumerate(lines[540:640], 541):
    print(f'{i}: {line}', end='')

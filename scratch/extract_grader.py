"""Extract classify_partial_vs_incorrect from doctor_grader.py"""
p = r'F:\pythonProject\doctor\doctor_grader.py'
with open(p, 'r', encoding='utf-8') as f:
    lines = f.readlines()

out_path = r'F:\pythonProject\scratch\classify_partial_dump.txt'
with open(out_path, 'w', encoding='utf-8') as out:
    # Find the function and print 40 lines from it
    for i, line in enumerate(lines):
        if 'def classify_partial_vs_incorrect' in line:
            for j in range(i, min(i + 50, len(lines))):
                out.write(f'{j+1}: {lines[j]}')
            break

print(f'Wrote to {out_path}')

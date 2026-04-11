"""Extract the predict function's fusion logic from llm_doctor.py"""
p = r'F:\pythonProject\doctor\llm_doctor.py'
with open(p, 'r', encoding='utf-8') as f:
    lines = f.readlines()

out_path = r'F:\pythonProject\scratch\predict_fusion_dump.txt'
with open(out_path, 'w', encoding='utf-8') as out:
    for i, line in enumerate(lines):
        if 'def predict(' in line:
            for j in range(i, len(lines)):
                out.write(f'{j+1}: {lines[j]}')
            break

print(f'Wrote {len(lines)} lines to {out_path}')

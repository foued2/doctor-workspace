# env_bootstrap.py
import sys
import os

# Fix 1 — Force UTF-8 everywhere
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Fix 2 — Reliable file reader with offset
def read_file_from_line(filepath, start_line=0, end_line=None):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    end = end_line or len(lines)
    for i, line in enumerate(lines[start_line:end], start=start_line+1):
        print(f'{i}: {line}', end='')

# Fix 3 — Reliable Python executor path
PYTHON = r'F:\pythonProject\.venv\Scripts\python.exe'
PROJECT = r'F:\pythonProject'

# Fix 4 — Verify environment is intact
def verify_env():
    required = [
        'doctor/__init__.py',
        'doctor/llm_doctor.py',
        'doctor/undefined_detection.py',
        'external_stress_layer/__init__.py',
        'dataset_generator/generator.py',
        'dataset_generator/failure_capture.py',
        'dataset_generator/adaptive_generator.py'
    ]
    missing = []
    for f in required:
        full = os.path.join(PROJECT, f)
        if not os.path.exists(full):
            missing.append(f)
    if missing:
        print(f'MISSING FILES: {missing}')
    else:
        print(f'Environment OK — all {len(required)} files present')

if __name__ == '__main__':
    verify_env()

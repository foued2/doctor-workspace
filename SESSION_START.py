import sys, os, subprocess

PYTHON = r"F:\pythonProject\venv\Scripts\python.exe"
GIT    = r"C:\Program Files\Git\cmd\git.exe"
PROJECT = r"F:\pythonProject"

os.chdir(PROJECT)
sys.stdout.reconfigure(encoding='utf-8')

for label, path in [("Python", PYTHON), ("Git", GIT), ("Project", PROJECT)]:
    status = "OK" if os.path.exists(path) else "MISSING"
    print(f"{label}: {status} — {path}")

print("CWD:", os.getcwd())
print("Ready.")

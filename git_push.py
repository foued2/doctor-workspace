"""
Auto-commit script for Doctor project shared workspace.
Run after every completed task to push session log and modified files.
Usage: python git_push.py --task "Track A fix" --status "complete"
"""

import subprocess
import argparse
import datetime
import os

GIT = r"C:\Program Files\Git\cmd\git.exe"
PROJECT_ROOT = r"F:\pythonProject"

DOCTOR_FILES = [
    "doctor/llm_doctor.py",
    "doctor/code_analyzer.py",
    "doctor/test_executor.py",
    "doctor/doctor_grader.py",
    "doctor/undefined_detection.py",
    "doctor/confidence_calibrator.py",
    "doctor/__init__.py",
    "external_stress_layer/enhanced_evaluator.py",
    "external_stress_layer/__init__.py",
    "tests/verify_code_only_baseline.py",
    "tests/leetcode_grader.py",
    "production_runner.py",
    "code_only_baseline.json",
    "workspace_log.md",
    "QWEN.md",
]


def run(cmd: str, cwd: str = PROJECT_ROOT) -> str:
    result = subprocess.run(
        cmd, shell=True, cwd=cwd,
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"[ERROR] {cmd}\n{result.stderr}")
    return result.stdout.strip()


def append_log(task: str, status: str, files: list, issues: str, action: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = (
        f"\n## {timestamp}\n"
        f"- **AGENT**: Qwen\n"
        f"- **TASK**: {task}\n"
        f"- **STATUS**: {status}\n"
        f"- **FILES_MODIFIED**: {', '.join(files) if files else 'none'}\n"
        f"- **ISSUES**: {issues if issues else 'none'}\n"
        f"- **ACTION_NEEDED**: {action if action else 'none'}\n"
        f"---\n"
    )
    log_path = os.path.join(PROJECT_ROOT, "workspace_log.md")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"[LOG] Entry written to workspace_log.md")


def get_modified_files() -> list:
    output = run(f'"{GIT}" diff --name-only HEAD')
    staged = run(f'"{GIT}" diff --cached --name-only')
    untracked = run(f'"{GIT}" ls-files --others --exclude-standard')
    all_files = set()
    for line in (output + "\n" + staged + "\n" + untracked).splitlines():
        line = line.strip()
        if line:
            all_files.add(line)
    return list(all_files)


def push(task: str, status: str, issues: str = "", action: str = ""):
    print("[GIT] Staging doctor files...")
    for f in DOCTOR_FILES:
        full = os.path.join(PROJECT_ROOT, f)
        if os.path.exists(full):
            run(f'"{GIT}" add "{f}"')
        else:
            print(f"[WARN] File not found, skipping: {f}")

    modified = get_modified_files()

    append_log(task, status, modified, issues, action)
    run(f'"{GIT}" add workspace_log.md')

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"[{timestamp}] Qwen: {task} — {status}"

    print(f"[GIT] Committing: {commit_msg}")
    run(f'"{GIT}" commit -m "{commit_msg}"')

    print("[GIT] Pushing to origin/main...")
    result = run(f'"{GIT}" push origin main')
    print(f"[GIT] Done. {result}")

    print("\n[CLAUDE REVIEW URL]")
    print(f"https://raw.githubusercontent.com/foued2/doctor-workspace/main/workspace_log.md")
    print(f"https://raw.githubusercontent.com/foued2/doctor-workspace/main/doctor/llm_doctor.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, help="Task name")
    parser.add_argument("--status", required=True, help="complete / partial / blocked")
    parser.add_argument("--issues", default="", help="Any issues encountered")
    parser.add_argument("--action", default="", help="Action needed from Claude")
    args = parser.parse_args()

    push(args.task, args.status, args.issues, args.action)

"""git_push.py — Push output/diagnostic files to GitHub so Claude can read them.

Usage:
    python git_push.py --task "description" --status "complete"

Pattern:
    1. Add files from scratch/ to git
    2. Commit with descriptive message
    3. Push to origin/main
    4. Print raw URLs for Claude to fetch
"""
import argparse
import os
import subprocess
import glob
import sys
from datetime import datetime

PYTHON = r"F:\pythonProject\venv\Scripts\python.exe"
GIT = r"C:\Program Files\Git\cmd\git.exe"
PROJECT = r"F:\pythonProject"

os.chdir(PROJECT)
sys.stdout.reconfigure(encoding='utf-8')

REPO_RAW = "https://raw.githubusercontent.com/foued2/doctor-workspace/main"

def main():
    parser = argparse.ArgumentParser(description="Push scratch files to GitHub")
    parser.add_argument("--task", default="update", help="Task description for commit message")
    parser.add_argument("--status", default="in_progress", help="Status: complete, in_progress, failed")
    parser.add_argument("--files", nargs="*", help="Specific files to push (default: all in scratch/)")
    args = parser.parse_args()

    # Ensure scratch/ exists
    os.makedirs(os.path.join(PROJECT, "scratch"), exist_ok=True)

    # Determine which files to add
    if args.files:
        files = args.files
    else:
        files = glob.glob(os.path.join(PROJECT, "scratch", "*"))

    if not files:
        print("No files in scratch/ to push")
        return

    # Add files to git
    for f in files:
        rel = os.path.relpath(f, PROJECT)
        subprocess.run([GIT, "add", rel], check=False, capture_output=True)

    # Commit
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    msg = f"[{args.status}] {args.task} ({timestamp})"
    result = subprocess.run([GIT, "commit", "-m", msg], capture_output=True, text=True)

    if result.returncode != 0:
        # Might be nothing to commit
        if "nothing to commit" in result.stderr.lower() or "nothing added" in result.stderr.lower():
            print("Nothing new to commit")
        else:
            print(f"Commit failed: {result.stderr.strip()}")
            return

    # Push
    result = subprocess.run([GIT, "push", "origin", "main"], capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"Push failed: {result.stderr.strip()}")
        return

    print(f"Pushed: {msg}")
    print()
    print("Claude can read these at:")
    for f in files:
        rel = os.path.relpath(f, PROJECT).replace("\\", "/")
        print(f"  {REPO_RAW}/{rel}")

if __name__ == "__main__":
    main()

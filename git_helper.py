"""Git operations helper script for doctor-workspace setup."""

import subprocess
import sys
import os

GIT = r"C:\Program Files\Git\cmd\git.exe"
ROOT = r"F:\pythonProject"


def git(*args, check=False):
    """Run a git command and return result."""
    cmd = [GIT] + list(args)
    print(f"[GIT] {' '.join(args)}")
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        print(f"[ERROR] git {' '.join(args)} failed with code {result.returncode}")
        sys.exit(1)
    return result


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "status"

    if action == "status":
        git("status")
        git("branch")
        git("remote", "-v")

    elif action == "init-main":
        # Try to create/switch to main branch
        r = git("checkout", "main")
        if r.returncode != 0:
            git("checkout", "-b", "main")
        git("branch")

    elif action == "add-all":
        git("add", "-A")
        git("status")

    elif action == "commit":
        msg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Initial snapshot"
        git("commit", "-m", msg)

    elif action == "push":
        # Try push; if remote doesn't exist, just show the command
        r = git("push", "-u", "origin", "main")
        if r.returncode != 0:
            print("[NOTE] Push failed — the remote repo may not exist yet.")
            print("[NOTE] Create the repo at: https://github.com/foued2/doctor-workspace")
            print("[NOTE] Then run: git push -u origin main")

    elif action == "push-force":
        r = git("push", "-f", "-u", "origin", "main")
        if r.returncode != 0:
            print("[NOTE] Force push failed — remote repo may not exist yet.")

    elif action == "log":
        git("log", "--oneline", "-5")

    else:
        print(f"Usage: python git_helper.py [status|init-main|add-all|commit|push|push-force|log]")


if __name__ == "__main__":
    main()

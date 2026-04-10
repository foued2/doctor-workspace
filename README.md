# 🧠 LeetCode Learning System

A complete system for learning and practicing LeetCode problems — with **automatic suggestions**, **step-by-step TODO guidance**, and **AI-powered code review**.

> **New to programming?** Start at [🚀 Quick Start — For Beginners](#-quick-start--for-beginners) below.

---

## 🚀 Quick Start — For Beginners

> This section assumes you have **zero** programming experience. We will guide you step by step.

### Step 1: Open the project folder

1. Open **File Explorer** (Windows key + E).
2. Navigate to `F:\pythonProject`.
3. You should see many folders like `001 to 100`, `101 to 200`, etc., and files like `README.md`.

### Step 2: Open the terminal (just once)

1. Click on the **address bar** at the top of File Explorer (where it shows the folder path).
2. Type `cmd` and press **Enter**.
3. A black window (Command Prompt) will appear. This is your **terminal**.

### Step 3: Get your first problem

In the terminal window, **copy and paste** this command, then press **Enter**:

```
.venv1\Scripts\python.exe leetcode-tools\leetcode_suggestor.py
```

**What happens:**
- The system picks the easiest LeetCode problem you haven't solved yet.
- It creates a new file for you in the correct folder.
- The file already contains the problem description, examples, and empty TODO sections for you to fill in.

### Step 4: Open and edit the file

1. Go back to **File Explorer**.
2. Open the folder that was just created (e.g., `3801 to 3900`).
3. Double-click the new `.py` file to open it in your code editor.
4. You will see a structured file with 4 numbered TODO sections.

### Step 5: Fill in the TODOs

The file has **4 numbered steps** you must complete in order:

| Step | What to do |
|------|-----------|
| **TODO #1** | Already filled in for you ✅ — just read the problem description. |
| **TODO #2** | Write **how** you plan to solve it (in plain English). |
| **TODO #3** | Write the **Time** and **Space** complexity (e.g., `O(n)`). |
| **TODO #4** | Write the actual **code** and **test cases**. |

### Step 6: Check your work (The Doctor)

When you think you're done, go back to the **terminal** and run:

```
.venv1\Scripts\python.exe leetcode-tools\leetcode_doctor.py <NUMBER>
```

Replace `<NUMBER>` with your problem number (e.g., `3856`).

**What happens:**
- The system reads your file and checks each TODO.
- If a TODO passes, it moves to the next one.
- If a TODO fails, it gives you a **grade** (out of 10) and tells you **exactly what to fix**.

### Step 7: Repeat

- Fix any errors the Doctor found.
- Run the Doctor again.
- When all 4 TODOs pass, go back to **Step 3** for a new problem.

---

## 📂 Two Types of Files

This project contains **two types of files**. It is important to understand the difference.

### Type A: Already Solved Problems (Old Format)

These are in folders like `001 to 100`, `101 to 200`, etc.

**What they look like:**
- Just Python code with some comments.
- **No** numbered TODO sections.
- The solution is already written.

**What to do with them:**
- **Read them** to learn how other problems are solved.
- **Study** the approach, algorithm, and code patterns.
- You **cannot** run the Doctor on these (they don't have the TODO structure).
- If you want to work through one properly, copy it and add the TODO template manually.

### Type B: New Suggested Problems (New Format)

These are created by the **Suggestor** and live in newer folders like `3801 to 3900`.

**What they look like:**
- A clear structure with 4 numbered TODOs.
- Problem description is already filled in.
- Empty sections for you to complete.

**What to do with them:**
- This is your **active homework**.
- Follow the **Quick Start** steps above: fill TODOs → run Doctor → repeat.

---

## 🔄 The Full Workflow

```
┌─────────────────────────────────────────────────┐
│  1. SUGGESTOR                                   │
│     "Here is your homework."                    │
│     Creates a new file with problem statement   │
│     ↓                                           │
│  2. YOU (Edit the file)                         │
│     TODO #1: Read ✅                            │
│     TODO #2: Plan your approach                 │
│     TODO #3: Analyze complexity                 │
│     TODO #4: Write code + tests                 │
│     ↓                                           │
│  3. DOCTOR                                      │
│     "Here is your grade."                       │
│     Checks each TODO in order                   │
│     ↓                                           │
│  ┌───────┐          ┌──────────┐               │
│  │ PASS  │ ────────>│ Next TODO│               │
│  │ FAIL  │ ────────>│ Fix it!  │ ──> Run again │
│  └───────┘          └──────────┘               │
│     ↓                                           │
│  4. All 4 TODOs passed? ──> Get new problem    │
└─────────────────────────────────────────────────┘
```

---

## 📋 Project Structure

```
pythonProject/
│
├── LeetCode Solutions (problems 1–3500, 3601–3700)
│   ├── 001 to 100/              59 solutions (Type A: already solved)
│   ├── 101 to 200/              28 solutions
│   ├── ... (37 range folders total)
│   └── 3801 to 3900/            New suggestions go here (Type B)
│
├── leetcode-tools/              ← The Suggestor & Doctor
│   ├── leetcode_suggestor.py    Picks easiest unsolved problem
│   ├── leetcode_doctor.py       Grades your work TODO by TODO
│   └── README.md                Detailed tools documentation
│
├── Study Materials
│   ├── Notes                    103 study notes on algorithms
│   ├── Topics                   Problem-to-technique mappings
│   └── Learning/                Session logs
│
└── README.md                    ← You are here
```

---

## 🛠️ Common Commands

| What you want to do | Command |
|---|---|
| **Get a new problem suggestion** | `.venv1\Scripts\python.exe leetcode-tools\leetcode_suggestor.py` |
| **See top 10 easiest unsolved problems** | `...leetcode_suggestor.py --all` |
| **Check your work on problem #3856** | `...leetcode_doctor.py 3856` |
| **Reset progress on a problem** | `...leetcode_doctor.py --reset 3856` |
| **Check most recent file** | `...leetcode_doctor.py` (no number) |

---

## Project Runner

You can also use the root script [`Run-Project.ps1`](Run-Project.ps1) as a single entry point for the project:

```powershell
.\Run-Project.ps1 suggest
.\Run-Project.ps1 doctor 3856
.\Run-Project.ps1 validate-doctor
.\Run-Project.ps1 full-check
```

Use `.\Run-Project.ps1 help` to see every supported task.

---

## 📖 Study Tips

1. **Start easy** — The Suggestor picks the easiest unsolved problem. Trust it.
2. **Read solved problems** — Open files in `001 to 100/` to learn patterns before attempting new ones.
3. **Write TODOs first** — Don't jump straight to code. Planning saves debugging time.
4. **Run the Doctor often** — Each run checks the next TODO. Small steps = steady progress.
5. **Check Topics & Notes** — Before solving, look up the technique in `Topics` and read `Notes`.

---

## 📦 Prerequisites

- **Python 3.10+** (already set up in `.venv1/`)
- **Windows** (this project is configured for Windows)
- No additional setup needed — everything is ready to go.

---

## 📄 License

This is a personal learning repository.

---

**Last Updated:** 2026-04-05
**Total LeetCode Solutions:** ~690
**Problems Suggested & Tracked:** Active

# 🛠️ LeetCode Tools — Suggestor & Doctor

This folder contains two scripts that work together to create a complete LeetCode learning system.

> **New here?** Start with the [Main README](../README.md) for the full beginner guide.

---

## 🚀 Quick Start

Open your terminal in the project folder and run:

### Get a Problem Suggestion
```
.venv1\Scripts\python.exe leetcode-tools\leetcode_suggestor.py
```

### Check Your Work with the Doctor
```
.venv1\Scripts\python.exe leetcode-tools\leetcode_doctor.py 3856
```

Replace `3856` with your problem number.

---

## 📁 What's in this folder

| File | Purpose |
|---|---|
| `leetcode_suggestor.py` | Finds the easiest unsolved LeetCode problem and auto-creates a solution file |
| `leetcode_doctor.py` | AI-powered code reviewer that checks your work TODO by TODO |
| `README.md` | This file |
| `LEETCODE_DOCTOR_README.md` | Full Doctor documentation |
| `LEETCODE_SUGGESTOR_README.md` | Full Suggestor documentation |
| `TODO_ORDER_EXPLANATION.md` | How TODO ordering enforcement works |
| `WORKFLOW_GUIDE.md` | Complete journey from suggestion to mastery |

---

## 🔄 The 4-Step TODO System

Every new solution file follows the same numbered structure:

```
TODO #1 - PROBLEM STATEMENT      ← Auto-filled by suggestor (read & review)
TODO #2 - APPROACH                ← Describe your algorithm step-by-step
TODO #3 - COMPLEXITY              ← State Time/Space complexity with reasoning
TODO #4 - SOLUTION + TESTS        ← Implement code + write comprehensive tests
```

**How it works:**
1. **Suggestor** creates the file with TODO #1 already filled (problem statement from LeetCode API)
2. You work on **TODO #2** (Approach) — describe how you'd solve it
3. You fill in **TODO #3** (Complexity) — analyze time and space
4. You implement **TODO #4** (Solution + Tests) — write the actual code
5. **Doctor** checks each TODO in order — you can't skip ahead (#1 → #2 → #3 → #4)

---

## 📊 Doctor Grading

Each TODO has a passing threshold:

| TODO | What it checks | Pass Threshold |
|---|---|---|
| **#1. Problem Statement** | Has description, examples, constraints | 8/10 |
| **#2. Approach** | Clear algorithm description with valid logic | 8/10 |
| **#3. Complexity** | Accurate time/space complexity analysis | 8/10 |
| **#4. Solution + Tests** | Code runs and passes ALL test cases | 100% pass rate |

### Progressive Hints
When a TODO fails, the Doctor gives hints that get more specific each attempt:
- **Attempt 1:** General direction
- **Attempt 2:** More specific hint
- **Attempt 3:** Offers to show the solution

---

## 🤖 AI Configuration

The Doctor uses **Qwen AI** (Alibaba DashScope) by default for intelligent code review.

### Setup
```bash
# Set your DashScope API key
set DASHSCOPE_API_KEY=your_key_here

# Or configure a different model
.venv1\Scripts\python.exe -c "from tools.leetcode_doctor import *; save_doctor_config({'ai_provider': 'qwen', 'qwen_model': 'qwen-max'})"
```

### Available AI Providers
| Provider | Config | Environment Variable |
|---|---|---|
| **Qwen** (default) | `qwen` | `DASHSCOPE_API_KEY` |
| OpenAI | `openai` | `OPENAI_API_KEY` |
| Claude | `claude` | `ANTHROPIC_API_KEY` |
| Ollama (local) | `ollama` | none needed |
| Rule-based (fallback) | — | — |

> **No API key?** The Doctor falls back to **rule-based evaluation** — it still works!

---

## 📁 Configuration Files

All tracking data is stored in `F:\pythonProject\.qwen\`:

| File | Purpose |
|---|---|
| `doctor_tracking.json` | Grades, attempts, timestamps for each TODO |
| `doctor_config.json` | AI provider and model selection |
| `suggested_problems.json` | Cached list of easiest unsolved problems |

---

## ⚠️ Important Notes

### No Inline File Modification
The Doctor **does NOT modify your solution files**. All feedback is:
- Displayed in the **console output**
- Tracked in `doctor_tracking.json`

This prevents corruption of your solution files from repeated feedback insertions.

### Running from Project Root
Always run the tools from the project root (`F:\pythonProject`), not from inside the `leetcode-tools/` folder. The scripts calculate paths relative to the project root.

---

## 📖 Full Documentation

All documentation is now in this folder:

- [LEETCODE_DOCTOR_README.md](LEETCODE_DOCTOR_README.md) — Full Doctor documentation
- [LEETCODE_SUGGESTOR_README.md](LEETCODE_SUGGESTOR_README.md) — Full Suggestor documentation
- [TODO_ORDER_EXPLANATION.md](TODO_ORDER_EXPLANATION.md) — How TODO ordering enforcement works
- [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) — Complete journey from suggestion to mastery

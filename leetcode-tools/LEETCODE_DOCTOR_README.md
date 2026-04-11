# 👨‍⚕️ LeetCode Doctor - AI-Powered Code Reviewer

Your personal AI code reviewer that analyzes your LeetCode solutions TODO by TODO, providing graded feedback, hints, and progressive guidance until you master each problem.

## 🎯 What It Does

The Doctor:
- ✅ **Analyzes TODOs in order** - Checks each section sequentially
- ✅ **Grades your work** - Out of 10, with clear pass/fail thresholds
- ✅ **Provides feedback** - Inline comments in your file + console output
- ✅ **Blocks progression** - Must pass current TODO before moving to next
- ✅ **Gives progressive hints** - Each failure gets more detailed hints
- ✅ **Offers solutions** - After multiple failures, asks if you want to see the answer
- ✅ **Tracks progress** - Remembers your attempts across sessions

## 🔄 Workflow

### The TODO Sequence:

```
1. Problem Statement (Need 8/10 to pass)
   ↓ PASS
2. Approach (Need 8/10 to pass)
   ↓ PASS
3. Complexity Analysis (Need 8/10 to pass)
   ↓ PASS
4. Solution Implementation (Need 100% test pass rate)
   ↓ PASS
5. Test Cases (Need 8/10 to pass)
   ↓
✅ COMPLETE!
```

**Each TODO blocks the next** - you can't get feedback on #3 until #2 passes!

### Example Session:

```bash
# First run - Check Problem Statement
$ python leetcode_doctor.py 3870

👨‍⚕️ DOCTOR EVALUATION: Problem Statement
Grade: 🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢 (10/10)
Status: PASS
✅ Problem Statement PASSED! Moving to next TODO...

# Second run - Check Approach (still has TODO)
$ python leetcode_doctor.py 3870

👨‍⚕️ DOCTOR EVALUATION: Approach
Grade: 🔴🔴⚪⚪⚪⚪⚪⚪⚪⚪ (2/10)
Status: FAIL
✗ Approach not implemented - still has TODO placeholder
💡 Hint: Think about how you would solve this manually...
❌ Approach needs more work (Attempt #1)

# You fix the approach...

# Third run - Check Approach again
$ python leetcode_doctor.py 3870

👨‍⚕️ DOCTOR EVALUATION: Approach
Grade: 🟢🟢🟢🟢🟢🟢🟢🟢🟢⚪ (9/10)
Status: PASS
✅ Approach PASSED! Moving to next TODO...

# Fourth run - Check Complexity
$ python leetcode_doctor.py 3870

👨‍⚕️ DOCTOR EVALUATION: Complexity
Grade: 🔴🔴🔴🔴⚪⚪⚪⚪⚪⚪ (4/10)
Status: FAIL
✗ Time complexity still has placeholder O(?)
❌ Complexity needs more work (Attempt #2)
```

## 📋 Commands

| Command | What it does |
|---------|-------------|
| `leetcode_doctor.py` | Analyze most recently created file |
| `leetcode_doctor.py 3870` | Analyze problem 3870 |
| `leetcode_doctor.py "3870. Count Commas.py"` | Analyze specific file |
| `leetcode_doctor.py --reset 3870` | Reset evaluation history |
| `leetcode_doctor.py --show-solution 3870` | Show solution (when stuck) |
| `leetcode_doctor.py --help` | Show help |

## 📊 Grading System

### Problem Statement (8/10 to pass)
- **Completeness (4 pts):** Full problem description present
- **Examples (3 pts):** Input/output examples included
- **Constraints (3 pts):** Constraints listed

### Approach (8/10 to pass)
- **Clarity (3 pts):** Algorithm clearly explained
- **Validity (3 pts):** Logic is sound
- **Specificity (2 pts):** Specific techniques mentioned
- **Completeness (2 pts):** Covers full strategy

### Complexity (8/10 to pass)
- **Time Complexity (4 pts):** Stated and accurate
- **Space Complexity (4 pts):** Stated and accurate
- **Justification (2 pts):** Reasoning provided

### Solution (100% test pass rate required)
- **Must pass ALL test cases** - no partial credit
- Tests are auto-generated from problem examples
- Code must run without errors

### Test Cases (8/10 to pass)
- **Coverage (4 pts):** Tests all problem examples
- **Edge Cases (3 pts):** Tests edge cases
- **Correctness (3 pts):** Expected outputs correct

## 💡 Hint System

When a TODO fails, the Doctor provides hints that get progressively more detailed:

**Attempt 1:** General hint
> "Think about how you would solve this manually, then translate that into steps"

**Attempt 2:** More specific hint
> "Try using a loop to iterate through the range and count commas for each number"

**Attempt 3:** Offer solution
> "You've tried 3 times. Would you like to see the solution? (y/n)"

## 🔧 AI Configuration

### Option 1: OpenAI (Recommended)

```bash
# Set your API key
set OPENAI_API_KEY=sk-your-key-here

# Configure doctor to use GPT-4
python -c "from leetcode_doctor import *; save_doctor_config({'ai_provider': 'openai', 'openai_model': 'gpt-4'})"
```

### Option 2: Ollama (Local, Free)

```bash
# Install Ollama: https://ollama.ai
# Pull a model
ollama pull llama3

# Start Ollama
ollama serve

# Configure doctor
python -c "from leetcode_doctor import *; save_doctor_config({'ai_provider': 'ollama', 'ollama_model': 'llama3'})"
```

### Option 3: Claude

```bash
# Set your API key
set ANTHROPIC_API_KEY=sk-ant-your-key-here

# Configure doctor
python -c "from leetcode_doctor import *; save_doctor_config({'ai_provider': 'claude'})"
```

### Option 4: Rule-Based (Default, No Setup)

If no AI is configured, the Doctor uses intelligent rule-based analysis:
- Checks for specific keywords and patterns
- Validates code structure
- Runs test cases
- Provides meaningful feedback

**Still effective!** Just less nuanced than AI evaluation.

## 📁 What Gets Created

### Inline Feedback in Your File:

```python
"""
APPROACH:

# ┌─────────────────────────────────────────────────────────────┐
# │ 👨‍⚕️ DOCTOR FEEDBACK (2026-04-04 20:09)
# │ Grade: 2.0/10 | Status: FAIL
# │ ✗ Approach not implemented - still has TODO placeholder
# └─────────────────────────────────────────────────────────────┘
TODO: Describe your approach
"""
```

### Tracking File (`.qwen/doctor_tracking.json`):

```json
{
  "evaluations": {
    "3801 to 3900/3870. Count Commas in Range.py": {
      "problem_statement": {
        "grade": 10.0,
        "status": "PASS",
        "attempts": 1,
        "timestamp": "2026-04-04T20:08:15"
      },
      "approach": {
        "grade": 9.0,
        "status": "PASS",
        "attempts": 2,
        "timestamp": "2026-04-04T20:15:30"
      }
    }
  }
}
```

## 🎓 How to Use

### 1. Create a Problem File

```bash
python leetcode_suggestor.py
# Creates file with TODOs automatically
```

### 2. Work on Problem Statement

- Fill in the problem statement section (auto-filled by suggestor)
- Run doctor to check:
  ```bash
  python leetcode_doctor.py 3870
  ```

### 3. Write Your Approach

Replace:
```python
APPROACH:
TODO: Describe your approach
```

With:
```python
APPROACH:
I will iterate through numbers from 1 to n. For each number,
I'll convert it to a string and check if it has commas.
Numbers >= 1000 will have commas inserted every 3 digits from right.
I'll count the total commas across all numbers.

Time Complexity: O(n * log(n)) - iterate n numbers, each has log(n) digits
Space Complexity: O(log(n)) - string conversion of each number
```

### 4. Run Doctor Again

```bash
python leetcode_doctor.py 3870
```

If it passes, moves to next TODO. If fails, provides hints.

### 5. Implement Solution

Replace the `solve()` method with actual code.

### 6. Run Doctor to Test Solution

```bash
python leetcode_doctor.py 3870
```

Runs test cases and checks if solution passes 100%.

### 7. Repeat Until All TODOs Pass

Each run checks the next incomplete TODO.

## 🚀 Pro Tips

1. **Run doctor frequently** - Get feedback as you work
2. **Read the inline comments** - Added directly to your file
3. **Use the hints** - They get more specific each attempt
4. **Don't skip TODOs** - Must pass in order
5. **Reset if needed** - `--reset` clears history for fresh start
6. **Configure AI** - Better feedback with GPT-4 or Claude

## 📂 Project Structure

```
pythonProject/
├── leetcode_doctor.py          # The Doctor script
├── leetcode_suggestor.py       # Problem suggestor (separate tool)
├── .qwen/
│   ├── doctor_tracking.json    # Tracks your progress
│   └── doctor_config.json      # AI configuration
└── 3801 to 3900/
    └── 3870. Count Commas in Range.py  # Your solution with doctor feedback
```

## 🔍 What Makes This Different

Unlike static linters, the Doctor:
- ✅ **Understands context** - Knows it's a LeetCode problem
- ✅ **Evaluates algorithm quality** - Not just code style
- ✅ **Checks correctness** - Runs your tests
- ✅ **Provides hints** - Doesn't just say "wrong"
- ✅ **Tracks progress** - Remembers your attempts
- ✅ **Blocks progression** - Ensures mastery before moving on
- ✅ **Inline feedback** - Comments right in your code

## ⚠️ Important Notes

### Test Case Limitations

The current test runner checks if code executes without errors. For full LeetCode test validation:

1. **Manually test** with LeetCode examples
2. **Add comprehensive tests** at bottom of file
3. **Doctor will check** if tests exist and run

### AI vs Rule-Based

- **AI (GPT-4/Claude):** Nuanced understanding, better hints, more accurate grading
- **Rule-Based:** Works out of box, good enough for most cases, completely private

### Multiple Files

The Doctor works on **one file at a time**. Each file has its own evaluation history.

To analyze all files with TODOs, run:
```bash
# Check specific problem
python leetcode_doctor.py 3870

# Or most recent
python leetcode_doctor.py
```

---

**Remember:** The Doctor is your guide, not your enemy. Its goal is to help you learn, not to block you. Use the hints, ask for help when stuck, and don't hesitate to request the solution after multiple attempts!

**Last Updated:** 2026-04-04

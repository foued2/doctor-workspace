# LeetCode Problem Suggestor

Automatically suggests and creates solution files for the easiest LeetCode problems you haven't solved yet, based on ZeroTrac ratings.

## 🎯 How It Works (Simple!)

**Just run the script. That's it.**

```bash
python leetcode_suggestor.py
```

**What happens automatically:**
1. ✅ Scans your project for solved problems
2. ✅ Finds the easiest unsolved problem from ZeroTrac ratings
3. ✅ Fetches the full problem statement from LeetCode API
4. ✅ **Auto-creates the solution file** with complete problem statement
5. ✅ Next time you run it, detects the file exists and suggests the next easiest

## 🔄 Workflow

### First Run:
```bash
$ python leetcode_suggestor.py

Scanning project for solved problems...
✓ Found 681 solved problems

📝 AUTO-CREATING SOLUTION FILE
Problem: 3870. Count Commas in Range
Rating: 1149.48

✓ Created solution file: 3870. Count Commas in Range.py
  Location: F:\pythonProject\3801 to 3900\3870. Count Commas in Range.py
```

### Work on the problem:
- Open the created file
- Read the problem statement (already in the file!)
- Implement your solution
- Test it

### Second Run (after solving):
```bash
$ python leetcode_suggestor.py

Scanning project for solved problems...
✓ Found 682 solved problems  ← Automatically detects 3870 exists!

📝 AUTO-CREATING SOLUTION FILE
Problem: 3861. Minimum Capacity Box  ← Suggests NEXT easiest
Rating: 1154.16

✓ Created solution file: 3861. Minimum Capacity Box.py
```

**That's the complete workflow!** No manual commands needed.

## 📁 What Gets Created

The script creates a ready-to-code file with:

```python
"""
LeetCode 3861. Minimum Capacity Box
============================================================

Problem Number: 3861
Difficulty Rating: 1154.16 (ZeroTrac)
Contest: weekly-contest-492
Problem Index: Q1

LeetCode URL: https://leetcode.com/problems/minimum-capacity-box/

PROBLEM STATEMENT:
============================================================
You are given an integer array `capacity`, where `capacity[i]` 
represents the capacity of the `ith` box, and an integer 
`itemSize` representing the size of an item.

The `ith` box can store the item if `capacity[i] >= itemSize`.

Return an integer denoting the index of the box with the 
**minimum** capacity that can store the item.

Example 1:
Input: capacity = [1,5,3,7], itemSize = 3
Output: 2

Example 2:
Input: capacity = [3,5,4,3], itemSize = 2
Output: 0

Constraints:
- 1 <= capacity.length <= 100
- 1 <= capacity[i] <= 100
- 1 <= itemSize <= 100

DIFFICULTY: Easy
TOPICS: Array
"""

from typing import List, Optional
import heapq
from collections import defaultdict, deque


class Solution:
    @staticmethod
    def solve() -> None:
        """
        TODO: Implement the solution for Minimum Capacity Box
        """
        # TODO: Implement your solution here
        pass


# Test cases
if __name__ == '__main__':
    solution = Solution()
    result = solution.solve()
    print(f"Result: {result}")
```

## 📋 Commands

| Command | What it does |
|---------|-------------|
| `leetcode_suggestor.py` | **Auto-creates** file for easiest unsolved problem |
| `leetcode_suggestor.py --all` | Shows top 10 easiest unsolved (without creating files) |

## ✨ Key Features

### 1. **Fully Automatic File Creation**
- No manual `--create` flag needed
- Just run the script, file is created instantly
- Includes complete problem statement with examples and constraints

### 2. **Complete Problem Statement**
- ✅ Full problem description
- ✅ All examples with input/output/explanation
- ✅ Complete constraints
- ✅ Difficulty rating and topics
- ✅ LeetCode URL for reference

### 3. **Smart Detection**
- Automatically detects existing files in your project
- Once a file exists, it won't be suggested again
- Always suggests the next easiest unsolved problem

### 4. **Follows Your Project Structure**
- Creates correct folders (e.g., `3801 to 3900/`)
- Names files correctly (e.g., `3870. Count Commas in Range.py`)
- Matches your existing solution template

## 🧠 How "Solved" is Detected

A problem is considered **solved** when:

1. **The file exists** in the correct folder
   - Example: `3801 to 3900/3870. Count Commas in Range.py`

That's it! The script scans your project, finds all existing solution files, and automatically excludes them from suggestions.

**No manual marking needed** - just create the file (done automatically) and the script knows it's "in progress" or "solved".

## 📊 Current Stats

- **Total problems in ZeroTrac:** 2,449
- **Problems solved in project:** ~682
- **Remaining unsolved:** ~1,767
- **Easiest unsolved rating:** ~1149

## 🎓 Understanding Ratings

- **Lower rating = Easier problem**
- Problems rated ~1000-1500 are typically Easy
- Problems rated ~2000-2500 are typically Medium
- Problems rated ~3000+ are typically Hard
- Ratings are based on actual contest performance (ZeroTrac Elo system)

## 🚀 Quick Start

```bash
# Using Python from .venv1
.venv1\Scripts\python.exe leetcode_suggestor.py

# Or using .venv
.venv\Scripts\python.exe leetcode_suggestor.py

# Or if python is in your PATH
python leetcode_suggestor.py
```

## 📝 Example Session Flow

```
Run 1: Script creates file for problem 3870 (Rating: 1149.48)
  ↓ You solve it
Run 2: Script detects 3870 exists, creates file for 3861 (Rating: 1154.16)
  ↓ You solve it
Run 3: Script detects both exist, creates file for 3842 (Rating: 1160.95)
  ↓ You solve it
Run 4: And so on...
```

**Each run automatically progresses you to the next easiest problem!**

---

**Rating Source:** [ZeroTrac LeetCode Ratings](https://github.com/zerotrac/leetcode_problem_rating)
**Problem Data:** [LeetCode API](https://leetcode-api-pied.vercel.app)
**Last Updated:** 2026-04-04

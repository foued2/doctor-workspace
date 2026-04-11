# Doctor Old-Format Detection Feature

## Overview
The Doctor now automatically detects when you try to analyze an old-format file (without TODO structure) and offers to convert it to the new format.

## How It Works

### Detection
When you run `python leetcode_doctor.py <problem_number>`, the Doctor checks if the file has:
- ✅ `TODO WORKFLOW` marker
- ✅ `TODO #1`, `TODO #2`, etc. sections
- ✅ Proper TODO structure

If the file has a `class Solution:` but lacks the TODO markers, it's identified as **old format**.

### User Prompt
When an old-format file is detected, the Doctor displays:

```
======================================================================
⚠️  OLD FORMAT DETECTED
======================================================================
File: 9. Palindrome Number.py

This file uses the old format (no TODO structure).
The Doctor cannot evaluate it in its current form.

Would you like to redo this problem in the new format?
The system will:
  1. Back up your current solution as .py.old
  2. Create a fresh TODO template with problem statement
  3. Let you fill in the TODOs properly

Redo this problem in new format? (yes/no):
```

### User Options

#### Option 1: Type "yes" or "y"
**What happens:**
1. ✅ Your current solution is backed up as `<filename>.py.old`
2. 🔄 The Doctor fetches the problem statement from LeetCode
3. 📝 A new TODO-structured file is created with:
   - Problem statement (TODO #1 - pre-filled)
   - Empty Approach section (TODO #2)
   - Empty Complexity section (TODO #3)
   - Empty Solution + Tests section (TODO #4)
4. ✅ You can now fill in the TODOs and run the Doctor normally

**Example output:**
```
🔄 Converting to new format...

============================================================
🔄 REGENERATING FILE IN NEW FORMAT
============================================================
Problem: 9. Palindrome Number
============================================================

Fetching problem statement from LeetCode...
✓ Backed up old file to: 9. Palindrome Number.py.old
✓ Regenerated file with TODO structure: 9. Palindrome Number.py

============================================================
✅ Conversion complete!
============================================================

Next steps:
  1. Open the file in your editor
  2. Fill in TODOs #2, #3, and #4
  3. Run the Doctor when ready: python leetcode_doctor.py 9

Your old solution is backed up at: 9. Palindrome Number.py.old
```

#### Option 2: Type "no" or anything else
**What happens:**
- The Doctor exits gracefully
- Your file is left unchanged
- You're advised to move on to a different problem

**Example output:**
```
👍 No problem! Move on to a different problem.
Run the suggestor to get a new suggestion with the TODO format.
```

## Testing on Problem 9

**Test command:**
```bash
F:\pythonProject\.venv1\Scripts\python.exe leetcode-tools\leetcode_doctor.py 9
```

**Result:** ✅ Successfully detected old format and prompted user

The file `001 to 100\9. Palindrome Number.py` is in old format:
- Has `class Solution:` ✅
- Has working solution code ✅
- No TODO structure ❌

The Doctor correctly identified this and offered conversion.

## Implementation Details

### Key Functions Added

#### 1. `is_old_format_file(file_content: str) -> bool`
Detects old-format files by checking for:
- Presence of `class Solution:`
- Absence of `TODO WORKFLOW` or `TODO #2` markers

```python
def is_old_format_file(file_content: str) -> bool:
    """Detect if a file uses the old format (no TODO structure)."""
    has_todo_workflow = 'TODO WORKFLOW' in file_content or 'TODO #1' in file_content or 'TODO #2' in file_content
    has_todo_sections = 'TODO #2' in file_content and 'TODO #3' in file_content
    
    has_solution_class = 'class Solution:' in file_content
    no_todo_structure = not has_todo_workflow and not has_todo_sections
    
    return has_solution_class and no_todo_structure
```

#### 2. `regenerate_as_new_format(file_path: Path) -> bool`
Converts old format to new format by:
1. Extracting problem number/title from filename
2. Fetching problem statement from LeetCode API
3. Backing up old file
4. Creating new TODO-structured file

### Integration Point
The detection happens in `evaluate_todo_in_sequence()` at line ~735:

```python
# Load file content for THIS TODO ONLY
with open(file_path, 'r', encoding='utf-8') as f:
    file_content = f.read()

# Check if this is an old-format file
if is_old_format_file(file_content):
    # ... prompt user and handle conversion
```

## Dependencies
The feature imports functions from the suggestor:
```python
from leetcode_suggestor import fetch_problem_statement, clean_html_content, get_folder_for_problem
```

These are used to:
- Fetch problem statements from LeetCode API
- Clean HTML content to markdown
- Determine correct folder for the problem

## Benefits
1. **No dead ends**: Users aren't stuck with ungradable files
2. **Automatic backup**: Old solutions are preserved
3. **Consistent workflow**: All problems can use the TODO system
4. **User choice**: Users can skip conversion if they prefer

## Edge Cases Handled
- ✅ Files without LeetCode URLs (manual problem statement needed)
- ✅ User cancels operation (KeyboardInterrupt/EOFError)
- ✅ Filename parsing failures
- ✅ API fetch failures (graceful degradation)

## Future Enhancements
- Batch convert all old-format files
- Auto-detect and suggest without prompting
- Track which files are old format

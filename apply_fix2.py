"""Apply Fix 2 to code_analyzer.py: Replace string-based abs( check with proper AST node check."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'F:\pythonProject\doctor\code_analyzer.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# The buggy pattern: "abs(" in src where src = ast.dump(tree)
# Replace with proper AST node check

# First, add a helper function before the class definition
helper_func = '''

def _has_abs_call(node: ast.AST) -> bool:
    """Detect if the AST contains any call to abs().

    Uses proper AST node traversal instead of string matching on ast.dump().
    """
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name) and child.func.id == 'abs':
                return True
    return False

'''

# Insert helper before "class CodeAnalyzer:"
if 'def _has_abs_call' not in content:
    content = content.replace('\nclass CodeAnalyzer:', helper_func + '\nclass CodeAnalyzer:')

# Now replace the string-based check in _check_algorithm_completeness
# Old: "abs(" in src and ("Eq" in src or "==" in src)
# New: use _has_abs_call(tree) and proper AST check for comparison operators

old_line = '"abs(" in src and ("Eq" in src or "==" in src)'
new_line = '_has_abs_call(tree) and _has_comparison_check(tree)'

if old_line in content:
    content = content.replace(old_line, new_line)
    print(f'Replaced: {old_line!r}')
    print(f'With:     {new_line!r}')
else:
    print(f'WARNING: Could not find old line: {old_line!r}')
    # Try to find similar patterns
    for i, line in enumerate(content.split('\n'), 1):
        if 'abs(' in line and 'src' in line:
            print(f'  Found similar at line {i}: {line.strip()!r}')

# Also need to add _has_comparison_check helper
helper_func2 = '''

def _has_comparison_check(node: ast.AST) -> bool:
    """Detect if the AST contains any comparison operator (==, !=, <, >, etc.).

    Uses proper AST node traversal instead of string matching on ast.dump().
    """
    for child in ast.walk(node):
        if isinstance(child, ast.Compare):
            return True
    return False

'''

if '_has_comparison_check' not in content and 'def _has_comparison_check' not in content:
    # Insert after _has_abs_call
    content = content.replace(
        'def _has_abs_call(node: ast.AST) -> bool:',
        helper_func2.strip() + '\n\n\ndef _has_abs_call(node: ast.AST) -> bool:'
    )

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Fix 2 applied successfully.')

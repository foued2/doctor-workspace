"""Add missing _has_comparison_check helper to code_analyzer.py."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'F:\pythonProject\doctor\code_analyzer.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add _has_comparison_check before _has_abs_call
helper = '''def _has_comparison_check(node: ast.AST) -> bool:
    """Detect if the AST contains any comparison operator (==, !=, <, >, etc.).

    Uses proper AST node traversal instead of string matching on ast.dump().
    """
    for child in ast.walk(node):
        if isinstance(child, ast.Compare):
            return True
    return False


'''

if '_has_comparison_check' not in content or 'def _has_comparison_check' not in content:
    content = content.replace(
        'def _has_abs_call(node: ast.AST) -> bool:',
        helper + 'def _has_abs_call(node: ast.AST) -> bool:'
    )
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Added _has_comparison_check helper.')
else:
    print('_has_comparison_check already exists.')

# Verify syntax
import ast
ast.parse(content)
print('Syntax OK.')

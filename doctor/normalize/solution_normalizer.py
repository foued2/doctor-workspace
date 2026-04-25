"""
Solution Normalizer — Single entry point for external solution code.

Input:  Raw GPT-generated solution code (any format)
Output: Clean standalone callable (ready for test_executor)

Handles:
- typing imports that shadow builtins
- class Solution wrappers
- type hints in signatures
- docstrings
- alternative import styles
- multiple class definitions
- nested classes

This layer is frozen after validation. All external solutions
pass through here before reaching test_executor.
"""
import ast
import re
from typing import Optional, Callable, Dict, Any


class NormalizationError(ValueError):
    """Raised when solution code contains unsupported constructs."""
    pass


SUPPORTED_TYPES = frozenset({
    'int', 'float', 'str', 'bool', 'list', 'dict', 'set', 'tuple',
    'ListNode',
})


class SolutionNormalizer:
    """
    Normalizes arbitrary GPT-generated Python code into a clean,
    executable standalone function.

    Supported subset:
    - Assignments, loops, conditionals, returns
    - List comprehensions (simple)
    - Basic arithmetic and comparison operators
    - Named functions with positional args

    Rejected constructs (hard fail):
    - Walrus operator (:=)
    - Complex default arguments (function calls, arithmetic in defaults)
    - Type stubs, protocol classes
    - Async functions, await expressions
    """

    UNSUPPORTED_PATTERNS = [
        (re.compile(r':='), "walrus operator (:=)"),
        (re.compile(r'async\s+def\b'), "async function"),
        (re.compile(r'\bawait\s+'), "await expression"),
        (re.compile(r'@overload\b'), "type overload decorator"),
        (re.compile(r'@abstractmethod\b'), "abstract method"),
        (re.compile(r'Protocol\b'), "Protocol class"),
    ]

    def __init__(self):
        self.typing_imports = [
            'List', 'Dict', 'Tuple', 'Set', 'Optional', 'Any',
            'Union', 'Callable', 'Iterable', 'Iterator', 'Sequence',
            'Mapping', 'TypeVar', 'Generic', 'FrozenSet', 'Type'
        ]

    def normalize(self, code: str) -> Optional[str]:
        """Main entry point. Returns normalized code or None if validation fails."""
        self._validate_subset(code)
        code = self._strip_typing_imports(code)
        code = self._remove_docstrings(code)
        code = self._unwrap_solution_classes(code)
        code = self._clean_type_hints(code)
        return code

    def _validate_subset(self, code: str) -> None:
        """Check for unsupported constructs. Raises NormalizationError on first match."""
        for pattern, description in self.UNSUPPORTED_PATTERNS:
            if pattern.search(code):
                raise NormalizationError(
                    f"Unsupported construct: {description}. "
                    f"Pattern: {pattern.pattern}"
                )

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise NormalizationError(f"Syntax error: {e}")

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if self._is_complex_default(default):
                        raise NormalizationError(
                            f"Unsupported default argument: complex expression in function "
                            f"'{node.name}' parameter default"
                        )

    def _is_complex_default(self, node: ast.AST) -> bool:
        """True if default arg involves function calls or arithmetic."""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                return True
        return False
    
    def _strip_typing_imports(self, code: str) -> str:
        """Remove 'from typing import' statements."""
        lines = code.split('\n')
        cleaned = []
        
        for line in lines:
            stripped = line.strip()
            # Match: from typing import X, Y, Z
            if stripped.startswith('from typing import'):
                continue
            # Match: import typing
            if stripped == 'import typing':
                continue
            # Match: from collections import Counter, etc. (sometimes used for types)
            if stripped.startswith('from collections import'):
                # Only skip if it looks like type-only imports
                if any(x in stripped for x in self.typing_imports):
                    continue
            cleaned.append(line)
        
        return '\n'.join(cleaned)
    
    def _remove_docstrings(self, code: str) -> str:
        """Remove docstrings from all functions and classes."""
        try:
            tree = ast.parse(code)
            
            class DocstringRemover(ast.NodeTransformer):
                def visit_FunctionDef(self, node):
                    # Remove docstring
                    if (node.body and isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Constant)):
                        node.body = node.body[1:]
                    return node
                
                def visit_ClassDef(self, node):
                    # Remove docstring
                    if (node.body and isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Constant)):
                        node.body = node.body[1:]
                    self.generic_visit(node)
                    return node
            
            transformer = DocstringRemover()
            new_tree = transformer.visit(tree)
            return ast.unparse(new_tree)
        except:
            return code
    
    def _unwrap_solution_classes(self, code: str) -> str:
        """Extract methods from 'class Solution' and expose as standalone functions."""
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == 'Solution':
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_name = item.name
                            
                            # Get method source
                            func_source = ast.unparse(item)
                            
                            # Remove 'self' from signature
                            func_source = re.sub(
                                rf'def\s+{method_name}\s*\(\s*self\s*,\s*',
                                f'def {method_name}(',
                                func_source
                            )
                            func_source = re.sub(
                                rf'def\s+{method_name}\s*\(\s*self\s*\)',
                                f'def {method_name}()',
                                func_source
                            )
                            
                            # Handle *args, **kwargs patterns
                            func_source = re.sub(
                                rf'def\s+{method_name}\s*\(\s*self\s*,\s*\*args',
                                f'def {method_name}(*args',
                                func_source
                            )
                            func_source = re.sub(
                                rf'def\s+{method_name}\s*\(\s*self\s*,\s*\*\*kwargs',
                                f'def {method_name}(**kwargs',
                                func_source
                            )
                            
                            code += '\n' + func_source
            
            return code
        except:
            return code
    
    def _clean_type_hints(self, code: str) -> str:
        """Remove type annotations from function signatures."""
        try:
            tree = ast.parse(code)
            
            class TypeHintCleaner(ast.NodeTransformer):
                def visit_FunctionDef(self, node):
                    # Clear all annotations
                    node.returns = None
                    for arg in node.args.args:
                        arg.annotation = None
                    for arg in node.args.posonlyargs:
                        arg.annotation = None
                    for arg in node.args.kwonlyargs:
                        arg.annotation = None
                    node.args.defaults = []
                    node.args.kw_defaults = []
                    self.generic_visit(node)
                    return node
            
            transformer = TypeHintCleaner()
            new_tree = transformer.visit(tree)
            return ast.unparse(new_tree)
        except:
            return code


def normalize_solution(code: str) -> Optional[str]:
    """
    Standalone function for normalizing solution code.

    Returns normalized code, or None if validation fails.

    Usage:
        normalized = normalize_solution(raw_gpt_code)
        if normalized is None:
            return None
        func = extract_function(normalized)
    """
    try:
        normalizer = SolutionNormalizer()
        return normalizer.normalize(code)
    except NormalizationError:
        return None


def extract_function(code: str, problem_name: str = None) -> Optional[Callable]:
    """
    Extract the solution function from normalized code.
    
    Args:
        code: Normalized Python code
        problem_name: Optional problem name for targeted extraction
    
    Returns:
        The extracted function, or None if extraction fails
    """
    namespace: Dict[str, Any] = {}
    namespace["ListNode"] = _get_listnode()
    
    try:
        exec(code, namespace)
        
        # Collect all callables
        functions = []
        classes = []
        
        for name, val in namespace.items():
            if not name.startswith("_") and name != "ListNode" and callable(val):
                if isinstance(val, type):
                    classes.append((name, val))
                else:
                    functions.append((name, val))
        
        # Priority: standalone functions > classes
        if functions:
            return functions[0][1]
        if classes:
            # Return the class for instantiation
            return classes[0][1]
        
        return None
    except Exception:
        return None


# Lazy import for ListNode to avoid circular imports
_listnode_class = None

def _get_listnode():
    global _listnode_class
    if _listnode_class is None:
        # Import here to avoid circular dependency
        try:
            from doctor.core.test_executor import ListNode
            _listnode_class = ListNode
        except:
            # Fallback: define minimal ListNode
            class ListNode:
                def __init__(self, val=0, next=None):
                    self.val = val
                    self.next = next
            _listnode_class = ListNode
    return _listnode_class


def _build_problem_function_map() -> Dict[str, str]:
    """Build PROBLEM_FUNCTION_MAP from registry: display_name -> function_name."""
    from doctor.registry.problem_registry import get_problems
    result: Dict[str, str] = {}
    for key, entry in get_problems().items():
        if not isinstance(entry, dict):
            continue
        display_name = entry.get("spec", {}).get("display_name", "")
        func_names = entry.get("normalization", {}).get("function_names", [])
        if display_name and func_names:
            result[display_name] = func_names[0]
    return result


PROBLEM_FUNCTION_MAP: Dict[str, str] = _build_problem_function_map()


def extract_function_for_problem(code: str, problem_name: str) -> Optional[Callable]:
    """
    Extract function specifically for a known problem.
    
    Uses the problem name to find the expected function name(s) from registry,
    then extracts that specific function.
    """
    normalized = normalize_solution(code)
    
    expected_func = PROBLEM_FUNCTION_MAP.get(problem_name)
    
    namespace: Dict[str, Any] = {}
    namespace["ListNode"] = _get_listnode()
    
    try:
        exec(normalized, namespace)
        
        if expected_func:
            for name, val in namespace.items():
                if name == expected_func and callable(val) and not isinstance(val, type):
                    return val
        
        for name, val in namespace.items():
            if (not name.startswith("_") and name != "ListNode" and 
                callable(val) and not isinstance(val, type)):
                return val
        
        for name, val in namespace.items():
            if (not name.startswith("_") and name != "ListNode" and 
                callable(val) and isinstance(val, type)):
                return val
        
        return None
    except Exception:
        return None

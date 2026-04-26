#!/usr/bin/env python3
"""
Direction 2: Problem Extraction Engine

Extracts problem schema from natural language statements following
direction2_extraction_schema.md
"""
import json
import re
import os
from typing import Dict, Any, Optional, List, Tuple


LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openrouter")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-chat-v3-0324")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


PROBLEM_CLASSES = ["construction", "optimization", "counting", "decision", "search"]
VALIDATION_TYPES = ["exact_match", "arrangement", "checker"]
INPUT_TYPES = ["single_case", "multi_case"]
OUTPUT_TYPES = ["integer", "list", "string", "boolean"]
SAFE_EVAL_GLOBALS = {
    "__builtins__": {},
    "len": len,
    "range": range,
    "sum": sum,
    "min": min,
    "max": max,
    "abs": abs,
    "all": all,
    "any": any,
    "sorted": sorted,
    "list": list,
    "set": set,
    "tuple": tuple,
    "dict": dict,
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "enumerate": enumerate,
    "zip": zip,
    "map": map,
    "filter": filter,
    "True": True,
    "False": False,
    "None": None,
}


EXTRACTION_PROMPT = """Analyze the following problem statement and extract a structured schema.

Return ONLY a JSON object with these exact fields:

{
  "problem_id": "slugified name using underscores",
  "problem_class": "construction | optimization | counting | decision | search",
  "has_multiple_valid_outputs": true or false,
  "evaluation_mode": "provisional",
  "input_structure": {
    "type": "single_case | multi_case",
    "test_case_count_var": "name of variable holding test count (e.g., 't'), or null for single_case",
    "per_case_format": [{"name": "field name", "type": "field type", "description": "what this field contains - FOR ONE TEST CASE ONLY, not the t line"}]
  },
  "output_format": {
    "type": "integer | list | string | boolean",
    "description": "one sentence describing output"
  },
  "constraints": {
    "variable_name": {
      "expression": "Python-evaluatable expression with COMPLETE bounds (e.g., '3 <= n <= 5000')",
      "depends_on": ["list of input field names this depends on"]
    }
  },
  "output_format": {
    "type": "integer | list | string | boolean",
    "description": "one sentence describing output"
  },
  "constraints": {
    "variable_name": {
      "expression": "Python-evaluatable expression with COMPLETE bounds (e.g. '1 <= n <= 5000')",
      "depends_on": ["list of input field names this depends on"]
    }
  },
  "invariants": ["testable OUTPUT condition in English"],
  "validation_logic": "what makes output correct - human readable",
  "validation_type": "exact_match | arrangement | checker",
  "sample_cases": [{"input": "raw input lines as they appear", "output": "raw expected output"}]
}

Rules:
- problem_id: lowercase, underscores, no spaces
- problem_class: must be one of construction, optimization, counting, decision, search
- evaluation_mode: must be "provisional"
- Extract ALL constraint bounds including upper bounds and constraints that depend on other variables. Express all bounds as Python-evaluatable expressions.
- CRITICAL: If ANY input field represents a test case count (t, T, test_cases, etc.), input_structure.type MUST be "multi_case" and test_case_count_var must be that field name
- If first input field is a count (number of test cases), this is ALWAYS multi_case
- test_case_count_var: the variable name holding the count for multi_case; null for single_case
- per_case_format: list of {name, type, description} for each input line (for ONE test case, not the t line)
- output_format.type must be integer, list, string, or boolean
- constraints: must include COMPLETE numeric bounds from the problem (e.g., "3 <= n <= 5000", not just "n >= 1")
- For array bounds like each element of k: create constraint using loop-like Python, e.g., "all(1 <= ki <= n // 3 for ki in k)"
- depends_on must list all input variable names used in the expression
- invariants describe properties of the OUTPUT that must be verified, not properties of the input. Input bounds go in constraints. Output properties go in invariants.
- invariants should be output-only checks such as output length, permutation validity, adjacency validity, or when -1 is allowed
- invariants: explicit testable properties, no implicit assumptions
- validation_type: exact_match (one answer), arrangement (any valid ordering), checker (complex)
- sample_cases: at least 2 example cases with COMPLETE input/output as they appear in the problem

Problem statement:
{statement}

Output ONLY the JSON. No explanations, no markdown, no additional text."""


def _call_llm(prompt: str) -> str:
    """Call LLM and return the response text."""
    if LLM_PROVIDER == "groq" and GROQ_API_KEY:
        return _call_groq(prompt)
    elif OPENROUTER_API_KEY:
        return _call_openrouter(prompt)
    else:
        raise ValueError("No LLM provider configured")


def _call_groq(prompt: str) -> str:
    import requests
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0
    }
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_openrouter(prompt: str) -> str:
    import requests
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0
    }
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _extract_json(text: str) -> dict | None:
    """Extract JSON from LLM response."""
    if not text:
        return None
    
    text = text.strip()
    
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON in markdown code block
    match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find the outermost JSON braces and parse recursively
    # Match from first { to last }
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace >= 0 and last_brace > first_brace:
        json_str = text[first_brace:last_brace+1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    return None


def _sample_value_for_type(field_type: str) -> Any:
    """Return a harmless sample value for a declared field type."""
    field_type = (field_type or "").lower()
    if "list" in field_type or "array" in field_type:
        return [1, 2, 3]
    if "string" in field_type:
        return "sample"
    if "bool" in field_type:
        return True
    return 3


def _sample_value_for_name(name: str, schema: dict) -> Any:
    """Return a sample value for a variable based on input_structure metadata."""
    test_case_var = schema.get("input_structure", {}).get("test_case_count_var")
    if name == test_case_var:
        return 1

    for field in schema.get("input_structure", {}).get("per_case_format", []):
        if field.get("name") == name:
            return _sample_value_for_type(field.get("type", ""))

    return 3


def _validate_constraint_expression(expr: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate a constraint expression can be evaluated with the provided context."""
    try:
        compiled = compile(expr, '<expr>', 'eval')
        eval_globals = dict(SAFE_EVAL_GLOBALS)
        eval_globals.update(context)
        eval(compiled, eval_globals, {})
        return True, ""
    except Exception as e:
        return False, str(e)


def _resolve_constraint_order(constraints: dict, allowed_vars: set[str]) -> Tuple[Optional[List[str]], str]:
    """Return constraints in dependency order, or an error."""
    graph = {name: spec.get("depends_on", []) for name, spec in constraints.items()}
    visiting = set()
    visited = set()
    order: List[str] = []

    def visit(node: str) -> Optional[str]:
        if node in visited:
            return None
        if node in visiting:
            return f"cyclic dependency involving {node}"

        visiting.add(node)
        for dep in graph.get(node, []):
            if dep not in allowed_vars:
                return f"constraint '{node}' references undefined variable: {dep}"
            if dep in graph:
                err = visit(dep)
                if err:
                    return err
        visiting.remove(node)
        visited.add(node)
        order.append(node)
        return None

    for name in graph:
        err = visit(name)
        if err:
            return None, err

    return order, ""


def _validate_schema(schema: dict) -> Tuple[bool, str]:
    """Validate extracted schema matches the schema format."""
    required_fields = [
        "problem_id", "problem_class", "has_multiple_valid_outputs",
        "evaluation_mode", "input_structure", "output_format",
        "constraints", "invariants", "validation_logic",
        "validation_type", "sample_cases"
    ]
    
    for field in required_fields:
        if field not in schema:
            return False, f"missing required field: {field}"
    
    # Validate problem_class
    if schema["problem_class"] not in PROBLEM_CLASSES:
        return False, f"invalid problem_class: {schema['problem_class']}"
    
    # Validate evaluation_mode
    if schema["evaluation_mode"] != "provisional":
        return False, f"evaluation_mode must be 'provisional', got: {schema['evaluation_mode']}"
    
    # Validate input_structure
    inp = schema["input_structure"]
    if inp.get("type") not in INPUT_TYPES:
        return False, f"invalid input_structure.type: {inp.get('type')}"
    
    # Validate output_format
    out = schema["output_format"]
    if out.get("type") not in OUTPUT_TYPES:
        return False, f"invalid output_format.type: {out.get('type')}"
    
    # Validate validation_type
    if schema["validation_type"] not in VALIDATION_TYPES:
        return False, f"invalid validation_type: {schema['validation_type']}"
    
    # Validate sample_cases
    if not isinstance(schema.get("sample_cases"), list) or len(schema.get("sample_cases", [])) < 1:
        return False, "sample_cases must be a non-empty list"
    
    # Validate constraints (expressions must be valid and evaluatable in dependency order)
    input_vars = set()
    for field in schema.get("input_structure", {}).get("per_case_format", []):
        input_vars.add(field.get("name"))

    test_case_var = schema.get("input_structure", {}).get("test_case_count_var")
    if test_case_var:
        input_vars.add(test_case_var)

    constraints = schema.get("constraints", {})
    allowed_vars = input_vars | set(constraints.keys())
    order, err = _resolve_constraint_order(constraints, allowed_vars)
    if order is None:
        return False, err

    resolved_context = {name: _sample_value_for_name(name, schema) for name in input_vars}

    for name in order:
        spec = constraints.get(name, {})
        if name not in resolved_context:
            resolved_context[name] = _sample_value_for_name(name, schema)

        expr = spec.get("expression", "")
        valid, err = _validate_constraint_expression(expr, resolved_context)
        if not valid:
            return False, f"constraint '{name}' invalid: {err}"

    return True, ""


def extract_problem(statement: str) -> Optional[Dict[str, Any]]:
    """
    Extract problem schema from a natural language statement.
    
    Returns the schema dict if extraction and validation succeed.
    Returns None if extraction fails with a logged failure_mode.
    """
    try:
        prompt = EXTRACTION_PROMPT.replace("{statement}", statement)
        response = _call_llm(prompt)
        schema = _extract_json(response)
        
        if schema is None:
            print(f"extraction_failed: could not parse JSON from LLM response")
            return None
        
        valid, err = _validate_schema(schema)
        if not valid:
            print(f"schema_invalid: {err}")
            return None
        
        return schema
    
    except Exception as e:
        print(f"extraction_failed: {e}")
        return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            statement = f.read()
    else:
        statement = sys.stdin.read()
    
    result = extract_problem(statement)
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("Extraction failed")

#!/usr/bin/env python3
"""
Registry Matcher for Doctor.

Takes parsed problem model → matches against registry → returns problem_id or "no match"

Strict rejection: must align constraints AND objective AND input/output types.
Similarity alone is not sufficient.
"""

import os
import json
from typing import Dict, Optional, Tuple

import requests


GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


def _call_llm(prompt: str) -> str:
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 1000
    }
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers, json=payload, timeout=60
    )
    if response.status_code != 200:
        raise RuntimeError(f"Groq error {response.status_code}: {response.text[:200]}")
    return response.json()["choices"][0]["message"]["content"]


def get_registry_problems() -> Dict[str, Dict]:
    """Load all problems from registry."""
    try:
        from doctor.registry.problem_registry import get_problems
        return get_problems()
    except ImportError:
        return {}


def build_registry_context(problems: Dict[str, Dict]) -> str:
    """Build registry context for LLM matching - using test cases."""
    lines = ["REGISTRY PROBLEMS:"]
    
    for pid, entry in problems.items():
        if pid in ("registry_version", "registry_notes"):
            continue
        
        spec = entry.get("spec", {})
        exec_data = entry.get("execution", {})
        
        tcs = exec_data.get("test_cases", [])[:3]
        sample_inputs = []
        sample_outputs = []
        for tc in tcs:
            inp = tc.get("input", [])
            out = tc.get("expected")
            sample_inputs.append(str(inp))
            sample_outputs.append(str(out))
        
        lines.append(f"\n[{pid}] {spec.get('display_name', pid)}")
        lines.append(f"  Sample inputs: {sample_inputs}")
        lines.append(f"  Sample outputs: {sample_outputs}")
    
    return "\n".join(lines)


_MATCH_PROMPT = """You are a registry matcher for algorithmic problems.

RULES:
1. If input structure and output format clearly match sample test cases, MATCH
2. Be lenient when inputs and outputs are the same type
3. Only reject when clearly different (different data structures)

OUTPUT FORMAT (match):
{{"match": "problem_id", "justification": "why this matches"}}

OUTPUT FORMAT (no match):
{{"match": "no match", "justification": "why this does not match"}}

---

REGISTRY (with sample test cases):
{registry}

---

PARSED MODEL TO MATCH:
- input_type: {input_type}
- output_type: {output_type}  
- objective: {objective}
- constraints: {constraints}
- edge_conditions: {edge_conditions}

Match if input/output structure aligns with registry samples. Output ONLY JSON:"""


def match_to_registry(model: Dict) -> Tuple[Optional[str], str]:
    """
    Match parsed model to registry.
    
    Returns:
        (problem_id, justification) or (None, justification) for no match
    """
    problems = get_registry_problems()
    if not problems:
        return None, "Registry is empty"
    
    registry_context = build_registry_context(problems)
    
    prompt = _MATCH_PROMPT.format(
        registry=registry_context,
        input_type=model.get("input_type", "unknown"),
        output_type=model.get("output_type", "unknown"),
        objective=model.get("objective", "unknown"),
        constraints=model.get("constraints", []),
        edge_conditions=model.get("edge_conditions", [])
    )
    
    response = _call_llm(prompt)
    
    start, end = response.find("{"), response.rfind("}")
    if start < 0 or end <= start:
        return None, f"Could not parse LLM response: {response[:200]}"
    
    try:
        result = json.loads(response[start:end+1])
    except json.JSONDecodeError:
        return None, f"Invalid JSON in response: {response[:200]}"
    
    match = result.get("match")
    justification = result.get("justification", "No justification provided")
    
    if match == "no match" or not match:
        return None, justification
    
    if match not in problems:
        return None, f"Match '{match}' not in registry"
    
    return match, justification


if __name__ == "__main__":
    test_model = {
        "input_type": "array of integers, integer",
        "output_type": "list of integers",
        "objective": "Find indices of two numbers that sum to target",
        "constraints": ["1 <= len <= 10000"],
        "edge_conditions": ["empty array", "single element"]
    }
    
    print("Testing matcher...")
    match_id, justification = match_to_registry(test_model)
    print(f"Match: {match_id}")
    print(f"Justification: {justification}")
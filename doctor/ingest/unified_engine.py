#!/usr/bin/env python3
"""
Unified Doctor Engine - Single LLM call for parse + match + confidence.

Architecture:
- 1 LLM call per statement (vs 3-4 before)
- Parser + Matcher merged into one prompt
- Output: parsed_model + match_candidate + confidence + decision
"""

import os
import json
import hashlib
import pathlib
import time
from typing import Dict, Optional, Tuple

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
PROVIDER = os.environ.get("LLM_PROVIDER", "groq")

CACHE_DIR = pathlib.Path(__file__).parent / ".llm_cache"
CACHE_DIR.mkdir(exist_ok=True)

MAX_RETRIES = 5
INITIAL_BACKOFF = 2

CONTRADICTION_PAIRS = [
    (["product", "maximum product", "multiply"], ["sum", "maximum sum", "total"]),
    (["increasing", "increasing subsequence", "rising"], ["common", "common subsequence", "lcs"]),
    (["cost", "minimum cost", "expense"], ["ways", "number of ways", "count ways"]),
    (["budget", "expense", "spending", "price"], ["subarray", "contiguous"]),
]


def _check_contradiction(objective: str, match_id: str) -> Tuple[bool, str]:
    obj_lower = objective.lower()
    
    if match_id == "max_subarray":
        if "product" in obj_lower and "sum" not in obj_lower:
            return True, "Product objective contradicts sum-based max_subarray"
    
    if match_id == "longest_increasing_subsequence":
        if "common subsequence" in obj_lower or "lcs" in obj_lower:
            return True, "Common subsequence contradicts increasing subsequence"
    
    if match_id == "climbing_stairs":
        if "cost" in obj_lower:
            return True, "Cost objective contradicts counting-ways climbing_stairs"
    
    return False, ""


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def _call_llm(prompt: str, retries: int = 0) -> str:
    h = _hash(prompt)
    cache_file = CACHE_DIR / f"unified_{h}.json"
    
    if cache_file.exists():
        return json.loads(cache_file.read_text())["response"]
    
    import requests
    
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 3000
    }
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
    except requests.exceptions.RequestException as e:
        if retries < MAX_RETRIES:
            wait = INITIAL_BACKOFF ** retries
            time.sleep(wait)
            return _call_llm(prompt, retries + 1)
        raise RuntimeError(f"Request failed after {MAX_RETRIES} retries: {e}")
    
    if response.status_code == 429:
        if retries < MAX_RETRIES:
            wait = INITIAL_BACKOFF ** retries
            time.sleep(wait)
            return _call_llm(prompt, retries + 1)
        raise RuntimeError(f"Rate limit exceeded after {MAX_RETRIES} retries")
    
    if response.status_code != 200:
        raise RuntimeError(f"API error {response.status_code}: {response.text[:300]}")
    
    resp = response.json()["choices"][0]["message"]["content"]
    
    cache_file.write_text(json.dumps({"response": resp}, indent=2))
    return resp


def get_registry_problems() -> Dict[str, Dict]:
    try:
        from doctor.registry.problem_registry import get_problems
        return get_problems()
    except ImportError:
        return {}


def build_registry_context(problems: Dict[str, Dict]) -> str:
    lines = ["REGISTRY:"]
    
    for pid, entry in problems.items():
        if pid in ("registry_version", "registry_notes"):
            continue
        
        spec = entry.get("spec", {})
        exec_data = entry.get("execution", {})
        display = spec.get("display_name", pid)
        
        tcs = exec_data.get("test_cases", [])[:2]
        samples = []
        for tc in tcs:
            inp = tc.get("input", [])
            out = tc.get("expected")
            samples.append(f"{inp} -> {out}")
        
        lines.append(f"\n[{pid}] {display}")
        lines.append(f"  Samples: {samples}")
    
    return "\n".join(lines)


_UNIFIED_PROMPT = """You are a unified problem analyzer. For the given statement, output ONLY valid JSON containing:

1. parsed_model: structured extraction
2. match_candidate: best matching problem_id or "no match"
3. confidence: "high", "medium", or "low" 
4. decision: "accept" or "reject"
5. justification: brief reasoning

CRITICAL RULES:
- Match ONLY if input_type, output_type, AND objective ALL align
- "Increasing subsequence" != "Common subsequence" (LIS vs LCS)
- "Maximum product" != "Maximum sum" (max_product vs max_subarray)
- "Minimum cost" != "Number of ways" (min_cost_climbing vs climbing_stairs)
- Ambiguous = reject, NOT guess
- Domain disguise (shopping, temperatures) is valid if structure matches

Output Schema:
{{
  "parsed_model": {{
    "input_type": "string",
    "output_type": "string", 
    "objective": "string",
    "constraints": ["list or empty if not stated"],
    "edge_conditions": ["list or empty if not stated"],
    "types_explicit": "boolean - true if types stated explicitly, false if inferred"
  }},
  "match_candidate": "problem_id or 'no match'",
  "confidence": "high|medium|low",
  "decision": "accept|reject",
  "justification": "why match/reject - cite key signals"
}}

{registry}

---
STATEMENT: {statement}

Output ONLY JSON:"""


def analyze_statement(statement: str) -> dict:
    """Single LLM call: parse + match + confidence + decision."""
    problems = get_registry_problems()
    registry_context = build_registry_context(problems)
    
    prompt = _UNIFIED_PROMPT.format(
        registry=registry_context,
        statement=statement
    )
    
    response = _call_llm(prompt)
    
    start, end = response.find("{"), response.rfind("}")
    if start < 0 or end <= start:
        raise ValueError(f"Invalid JSON response: {response[:200]}")
    
    result = json.loads(response[start:end+1])
    
    model = result.get("parsed_model", {})
    match = result.get("match_candidate")
    decision = result.get("decision", "reject")
    confidence = result.get("confidence", "low")
    justification = result.get("justification", "")
    
    trace = {
        "llm_match": match,
        "confidence": confidence,
        "contradiction": False,
        "final": None
    }
    
    if decision == "accept" and match and match != "no match":
        is_con, con_reason = _check_contradiction(model.get("objective", ""), match)
        if is_con:
            trace["contradiction"] = True
            trace["final"] = "reject"
            return {
                "status": "rejected",
                "failure_tag": "validation_leak",
                "matched": None,
                "parsed_model": model,
                "decision_trace": trace,
                "error": con_reason
            }
        
        trace["final"] = "accept"
        return {
            "status": "success",
            "failure_tag": None,
            "matched": match,
            "parsed_model": model,
            "confidence": confidence,
            "decision_trace": trace,
            "justification": justification
        }
    
    trace["final"] = "reject"
    return {
        "status": "rejected",
        "failure_tag": "matcher_miss" if match else "parser_fail",
        "matched": match,
        "parsed_model": model,
        "decision_trace": trace,
        "justification": justification
    }


def run_phase3_unified(statement: str, user_id: str) -> dict:
    """Run Phase 3 with unified engine."""
    from datetime import datetime
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "statement": statement,
        "status": None,
        "failure_tag": None,
        "parsed_model": None,
        "matched": None,
        "confidence": None,
        "decision_trace": {},
    }
    
    try:
        analysis = analyze_statement(statement)
        result.update(analysis)
    except Exception as e:
        result["status"] = "error"
        result["failure_tag"] = "parser_fail"
        result["error"] = str(e)
    
    return result


if __name__ == "__main__":
    test_cases = [
        ("I have a list of numbers and a target number. I need to find which two numbers in the list add up to the target.", "test_1"),
        ("How do I check if parentheses in a string are balanced?", "test_2"),
    ]
    
    print("Testing unified engine...")
    for stmt, uid in test_cases:
        print(f"\n=== {uid} ===")
        result = run_phase3_unified(stmt, uid)
        print(f"  Matched: {result.get('matched')}")
        print(f"  Status: {result.get('status')}")
        print(f"  Tag: {result.get('failure_tag')}")
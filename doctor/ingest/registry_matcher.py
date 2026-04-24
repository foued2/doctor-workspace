#!/usr/bin/env python3
"""
Registry Matcher for Doctor.

Takes parsed problem model → matches against registry → returns problem_id or "no match"

Strict rejection: must align constraints AND objective AND input/output types.
Similarity alone is not sufficient.
"""

import os
import json
import time
from typing import Dict, Optional, Tuple

import requests


GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
MAX_RETRIES = 5
INITIAL_BACKOFF = 2

CONTRADICTION_PAIRS = [
    (["product", "maximum product"], ["sum", "maximum sum"]),
    (["increasing", "increasing subsequence"], ["common", "common subsequence"]),
    (["cost", "minimum cost"], ["ways", "number of ways"]),
    (["budget", "expense", "spending"], ["subarray"]),
]


def _check_contradiction(objective: str, match_id: str) -> Tuple[bool, str]:
    obj_lower = objective.lower()
    for neg_keywords, pos_keywords in CONTRADICTION_PAIRS:
        neg_found = any(kw in obj_lower for kw in neg_keywords)
        pos_found = any(kw in obj_lower for kw in pos_keywords)
        if neg_found and pos_found:
            return True, f"Contradiction: '{neg_keywords[0]}' vs '{pos_keywords[0]}'"
    if match_id == "longest_increasing_subsequence":
        if "common subsequence" in obj_lower or "lcs" in obj_lower:
            return True, "LCS not LIS"
    if match_id == "max_subarray":
        if "product" in obj_lower and "sum" not in obj_lower:
            return True, "Product not sum"
    if match_id == "climbing_stairs":
        if "cost" in obj_lower:
            return True, "Cost not ways"
    return False, ""


def _semantic_fallback(model: Dict) -> Tuple[Optional[str], str]:
    input_type = model.get("input_type", "").lower()
    output_type = model.get("output_type", "").lower()
    objective = model.get("objective", "").lower()
    problem_scores = {}
    for pid in ["max_subarray", "longest_increasing_subsequence"]:
        score = 0
        if ("array" in input_type or "list" in input_type):
            score += 2
        if pid == "max_subarray":
            if "subarray" in objective or "contiguous" in objective:
                score += 2
                if "sum" in objective:
                    problem_scores["max_subarray"] = score
        if pid == "longest_increasing_subsequence":
            if "subsequence" in objective or "consecutive" in objective or "increasing" in objective or "rising" in objective:
                score += 2
                if "increasing" in objective or "rising" in objective:
                    problem_scores["longest_increasing_subsequence"] = score
    if problem_scores:
        best = max(problem_scores.items(), key=lambda x: x[1])
        if best[1] >= 4:
            return best[0], f"Semantic fallback: {best[0]}"
    return None, ""


def _validate_objective_alignment(objective: str, match_id: str) -> Tuple[bool, str]:
    obj_lower = objective.lower()
    alignment_requirements = {
        "max_subarray": {"required": ["sum", "contiguous", "subarray"], "reject_keywords": ["product"]},
        "longest_increasing_subsequence": {"required": ["increasing", "subsequence"], "reject_keywords": ["common", "lcs"]},
    }
    if match_id in alignment_requirements:
        reqs = alignment_requirements[match_id]
        for kw in reqs.get("reject_keywords", []):
            if kw in obj_lower:
                return False, f"Reject keyword: '{kw}'"
        if not any(kw in obj_lower for kw in reqs.get("required", [])):
            return False, f"Missing required: {reqs['required']}"
    return True, "aligned"


def _call_llm_with_stats(prompt: str, retries: int = 0) -> Tuple[str, int]:
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 1000
    }
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers, json=payload, timeout=60
        )
    except requests.exceptions.RequestException as e:
        if retries < MAX_RETRIES:
            wait = INITIAL_BACKOFF ** retries
            time.sleep(wait)
            return _call_llm_with_stats(prompt, retries + 1)
        raise RuntimeError(f"Request failed after {MAX_RETRIES} retries: {e}")
    
    if response.status_code == 429:
        if retries < MAX_RETRIES:
            wait = INITIAL_BACKOFF ** retries
            time.sleep(wait)
            return _call_llm_with_stats(prompt, retries + 1)
        raise RuntimeError(f"Groq error 429: rate limit exceeded after {MAX_RETRIES} retries")
    
    if response.status_code != 200:
        raise RuntimeError(f"Groq error {response.status_code}: {response.text[:200]}")
    return response.json()["choices"][0]["message"]["content"], retries


def _call_llm(prompt: str) -> str:
    resp, _ = _call_llm_with_stats(prompt)
    return resp


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

STRICT RULES - REJECTION CONTRACT:
1. Match ONLY if input_type, output_type, AND objective ALL align explicitly with registry
2. Similarity alone is NOT sufficient
3. When in doubt, return no match
4. Reject if objective differs even when input/output types match
5. Ambiguous formulations must reject, NOT guess

OUTPUT FORMAT (match):
{{"match": "problem_id", "justification": "why this matches - cite all three: input_type, output_type, objective"}}

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

Match ONLY if all three (input_type, output_type, objective) align. Output ONLY JSON:"""


def match_to_registry(model: Dict) -> Tuple[Optional[str], str, dict]:
    """
    Match parsed model to registry with full decision trace.
    Returns: (match_id, justification, decision_trace)
    """
    trace = {"llm_match": None, "contradiction": False, "validation": True, "fallback": False, "final": None}
    
    problems = get_registry_problems()
    if not problems:
        trace["final"] = "reject"
        return None, "Registry empty", trace
    
    objective = model.get("objective", "")
    
    registry_context = build_registry_context(problems)
    prompt = _MATCH_PROMPT.format(
        registry=registry_context,
        input_type=model.get("input_type", "unknown"),
        output_type=model.get("output_type", "unknown"),
        objective=objective,
        constraints=model.get("constraints", []),
        edge_conditions=model.get("edge_conditions", [])
    )
    
    response, retry_count = _call_llm_with_stats(prompt)
    trace["retry_count"] = retry_count
    
    start, end = response.find("{"), response.rfind("}")
    if start < 0 or end <= start:
        trace["final"] = "reject"
        return None, f"Parse error: {response[:100]}", trace
    
    try:
        result = json.loads(response[start:end+1])
    except json.JSONDecodeError:
        trace["final"] = "reject"
        return None, "Invalid JSON", trace
    
    match = result.get("match")
    justification = result.get("justification", "")
    trace["llm_match"] = match
    
    # STEP 1: Contradiction check (hard termination)
    if match and match != "no match":
        is_con, con_reason = _check_contradiction(objective, match)
        if is_con:
            trace["contradiction"] = True
            trace["final"] = "reject"
            return None, f"CONTRADICTION: {con_reason}", trace
    
    if match == "no match" or not match:
        trace["llm_match"] = None
        # STEP 2: Validation
        for pm in ["max_subarray", "longest_increasing_subsequence"]:
            is_aligned, _ = _validate_objective_alignment(objective, pm)
            if not is_aligned:
                trace["validation"] = False
        # STEP 3: Fallback only if validation passed
        if trace["validation"]:
            fb_match, fb_reason = _semantic_fallback(model)
            if fb_match:
                trace["fallback"] = True
                trace["final"] = "accept"
                return fb_match, fb_reason, trace
        trace["final"] = "reject"
        return None, justification, trace
    
    if match not in problems:
        trace["final"] = "reject"
        return None, f"Unknown: {match}", trace
    
    # STEP 4: Validate matched entry
    is_aligned, align_reason = _validate_objective_alignment(objective, match)
    trace["validation"] = is_aligned
    if not is_aligned:
        trace["final"] = "reject"
        return None, f"Validation failed: {align_reason}", trace
    
    trace["final"] = "accept"
    return match, justification, trace


if __name__ == "__main__":
    test_model = {
        "input_type": "array of integers, integer",
        "output_type": "list of integers",
        "objective": "Find indices of two numbers that sum to target",
        "constraints": ["1 <= len <= 10000"],
        "edge_conditions": ["empty array", "single element"]
    }
    
    print("Testing matcher...")
    match_id, justification, trace = match_to_registry(test_model)
    print(f"Match: {match_id}")
    print(f"Justification: {justification}")
    print(f"Trace: {trace}")
    print(f"Justification: {justification}")
#!/usr/bin/env python3
"""
Unified Doctor Engine - Single LLM call for parse + match + confidence + decision.

Architecture:
- 1 LLM call per statement (vs 3-4 before)
- Parser + Matcher merged into one prompt
- Output: parsed_model + match_candidate + alignment_score breakdown + decision

IMPORTANT: Batch evaluation is not a valid scoring mode. Use atomic evaluation
only. Batch mode is preserved for infrastructure testing only and must not be used
for threshold calibration or Phase 4 metrics. Multi-statement evaluation creates
inter-statement interference that violates determinism guarantees.
"""

import os
import json
import hashlib
import pathlib
import time
from typing import Dict, Optional, Tuple

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-chat-v3-0324")
OPENROUTER_BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
PROVIDER = os.environ.get("LLM_PROVIDER", "groq")

CACHE_DIR = pathlib.Path(__file__).parent / ".llm_cache"
CACHE_DIR.mkdir(exist_ok=True)

MAX_RETRIES = 5
INITIAL_BACKOFF = 2

CONTRADICTION_PAIRS = [
    (["product", "maximum product", "max product", "multiply", "multiplication"], ["sum", "maximum sum", "max sum", "total"]),
    (["increasing", "increasing subsequence", "rising"], ["common", "common subsequence", "lcs"]),
    (["cost", "minimum cost", "expense"], ["ways", "number of ways", "count ways"]),
    (["budget", "expense", "spending", "price"], ["subarray", "contiguous"]),
]


OPERATION_RESTRICTIONS = {
    "min_distance": {
        "required_operations": ["insert", "delete", "replace"],
        "restrictive_keywords": ["only insert", "only delete", "only insertion", "only deletion", "no replace", "without replace", "no replacement"]
    },
    "edit_distance": {
        "required_operations": ["insert", "delete", "replace"],
        "restrictive_keywords": ["only insert", "only delete", "only insertion", "only deletion", "no replace", "without replace", "no replacement"]
    }
}

STRUCTURAL_MODIFIERS = {
    "required_operations": ["ignore", "except", "excluding", "but not", "only"],
    "restrictive_keywords": [
        "ignore", "excluding", "except", "but not", "only",
        "without using", "do not consider", "skip"
    ]
}


def _check_operation_restriction(objective: str, constraints: list, match_id: str) -> Tuple[bool, str]:
    if match_id not in OPERATION_RESTRICTIONS:
        return False, ""
    
    constraint_text = (objective + " " + " ".join(constraints)).lower()
    
    for keyword in OPERATION_RESTRICTIONS[match_id]["restrictive_keywords"]:
        if keyword in constraint_text:
            return True, f"Constraint '{keyword}' conflicts with required operations for {match_id}"
    
    return False, ""


def _check_structural_modifier(objective: str, constraints: list, match_id: str) -> Tuple[bool, str]:
    """Check if constraints contain structural modifiers that change problem definition."""
    if match_id in ("no match", None, ""):
        return False, ""
    
    constraint_text = (objective + " " + " ".join(constraints)).lower()
    
    for keyword in STRUCTURAL_MODIFIERS["restrictive_keywords"]:
        if keyword in constraint_text:
            return True, f"Structural modifier '{keyword}' changes problem definition"
    
    return False, ""


def _check_contradiction(objective: str, match_id: str) -> Tuple[bool, str]:
    obj_lower = objective.lower()
    
    if match_id == "max_subarray":
        product_keywords = ["product", "multiply", "multiplication", "max product", "maximum product"]
        if any(kw in obj_lower for kw in product_keywords):
            return True, "Product objective contradicts sum-based max_subarray"
    
    if match_id == "longest_increasing_subsequence":
        non_strict_keywords = [
            "at least as large", "at least as big", "non-decreasing", "not decreasing", 
            "greater or equal", "largest possible", "at most as small",
            "greater than or equal", "not smaller", "not less than", "allowing equal",
            "monotonically increasing", "no element is smaller", "no element is less"
        ]
        if any(kw in obj_lower for kw in non_strict_keywords):
            return True, "Non-strict subsequence contradicts strictly increasing LIS"
    
    if match_id == "climbing_stairs":
        if "cost" in obj_lower:
            return True, "Cost objective contradicts counting-ways climbing_stairs"
    
    return False, ""


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


OBJECTIVE_CANONICAL_MAP = {
    "gain": "value",
    "profit": "value",
    "revenue": "value",
    "return": "value",
    "earnings": "value",
    "loss": "cost",
    "expense": "cost",
    "spending": "cost",
    "period": "subarray",
    "window": "subarray",
    "stretch": "subarray",
    "block": "subarray",
    "trend": "subsequence",
    "progression": "subsequence",
}

def canonicalize_objective(objective: str) -> str:
    words = objective.lower().split()
    normalized = [OBJECTIVE_CANONICAL_MAP.get(w, w) for w in words]
    return " ".join(normalized)


def _extract_json_object(response: str, repair_info: dict = None) -> Dict[str, Any]:
    if repair_info is None:
        repair_info = {"repair_used": False, "repair_method": None}
    
    start, end = response.find("{"), response.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Invalid JSON response")
    
    try:
        return json.loads(response[start : end + 1])
    except json.JSONDecodeError:
        pass
    
    last_brace = response.rfind("}")
    if last_brace > start:
        try:
            repair_info["repair_used"] = True
            repair_info["repair_method"] = "truncate"
            return json.loads(response[start : last_brace + 1])
        except json.JSONDecodeError:
            pass
    
    import re
    match = re.search(r'\{[^{}]*\}', response[start:end + 1], re.DOTALL)
    if match:
        try:
            repair_info["repair_used"] = True
            repair_info["repair_method"] = "regex"
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    
    raise ValueError("Invalid JSON response")


def _extract_json_array(response: str, repair_info: dict = None) -> list:
    if repair_info is None:
        repair_info = {"repair_used": False, "repair_method": None}
    
    start, end = response.find("["), response.rfind("]")
    if start < 0 or end <= start:
        raise ValueError("Invalid JSON array response")
    
    try:
        return json.loads(response[start:end+1])
    except json.JSONDecodeError:
        pass
    
    last_bracket = response.rfind("]")
    if last_bracket > start:
        try:
            repair_info["repair_used"] = True
            repair_info["repair_method"] = "truncate"
            return json.loads(response[start:last_bracket+1])
        except json.JSONDecodeError:
            pass
    
    import re
    matches = list(re.finditer(r'\{[^{}]*\}', response[start:end+1], re.DOTALL))
    if matches:
        try:
            repair_info["repair_used"] = True
            repair_info["repair_method"] = "regex_array"
            results = []
            for m in matches:
                try:
                    results.append(json.loads(m.group(0)))
                except json.JSONDecodeError:
                    continue
            if results:
                return results
        except Exception:
            pass
    
    raise ValueError("Invalid JSON array response")


def _call_llm(prompt: str, retries: int = 0) -> str:
    h = _hash(prompt)
    cache_file = CACHE_DIR / f"unified_{h}.json"
    
    if cache_file.exists():
        return json.loads(cache_file.read_text())["response"]
    
    import requests
    
    if PROVIDER == "openrouter" and OPENROUTER_API_KEY:
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 3000
        }
        url = f"{OPENROUTER_BASE_URL}/chat/completions"
        use_openrouter = True
    else:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 3000
        }
        url = "https://api.groq.com/openai/v1/chat/completions"
        use_openrouter = False
    
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
3. alignment_score: OBJECTIVE alignment (0.0-1.0) - explicit keyword match
4. constraint_consistency: CONSTR alignment (0.0-1.0) - constraints match
5. structural_compatibility: STRUCT alignment (0.0-1.0) - input/output type match
6. decision: "accept" or "reject"
7. justification: brief reasoning

CRITICAL RULES:
- Match ONLY if input_type, output_type, AND objective ALL align
- "Increasing subsequence" != "Common subsequence" (LIS vs LCS)
- "Maximum product" != "Maximum sum" (max_product vs max_subarray)
- "Minimum cost" != "Number of ways" (min_cost_climbing vs climbing_stairs)
- Ambiguous = reject, NOT guess
- Domain disguise (shopping, temperatures) is valid if structure matches
- alignment_score requires EXPLICIT keyword match, not inference

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
  "alignment_score": "float 0.0-1.0 - OBJECTIVE keyword match",
  "constraint_consistency": "float 0.0-1.0 - constraints aligned",
  "structural_compatibility": "float 0.0-1.0 - input/output types match",
  "decision": "accept|reject",
  "justification": "why match/reject - cite key signals"
}}

{registry}

---
STATEMENT: {statement}

Output ONLY JSON:"""


ALIGNMENT_THRESHOLD = 0.85


def _evaluate_decision(
    match: str,
    decision: str,
    model: dict,
    alignment_score: float,
    constraint_consistency: float,
    structural_compatibility: float,
    repair_info: dict,
    trace: dict
) -> dict:
    """Formal decision contract: Accept iff (no contradiction) AND (alignment >= T) AND (constraints consistent)"""
    
    trace["decision_contract"] = {
        "conditions": {
            "no_contradiction": True,
            "alignment_threshold_met": alignment_score >= ALIGNMENT_THRESHOLD,
            "constraints_consistent": constraint_consistency >= 0.7,
            "structural_compatible": structural_compatibility >= 0.7
        },
        "threshold_used": ALIGNMENT_THRESHOLD,
        "repair_active": repair_info.get("repair_used", False)
    }
    
    if decision == "accept" and match and match != "no match":
        is_con, con_reason = _check_contradiction(model.get("objective", ""), match)
        if is_con:
            is_constraint_violation = "non-strict" in con_reason.lower() or "strictly" in con_reason.lower()
            
            if is_constraint_violation:
                trace["decision_contract"]["conditions"]["constraints_consistent"] = False
                trace["constraint_consistency_violation"] = True
                trace["decision_contract"]["rejection_reason"] = "constraint_consistency_violation"
            else:
                trace["decision_contract"]["conditions"]["no_contradiction"] = False
                trace["contradiction"] = True
                trace["decision_contract"]["rejection_reason"] = "contradiction"
            
            trace["final"] = "reject"
            return {
                "status": "rejected",
                "failure_tag": "validation_leak",
                "matched": None,
                "parsed_model": model,
                "decision_trace": trace,
                "error": con_reason
            }
        
        is_restricted, restriction_reason = _check_operation_restriction(
            model.get("objective", ""),
            model.get("constraints", []),
            match
        )
        if is_restricted:
            trace["decision_contract"]["conditions"]["constraints_consistent"] = False
            trace["operation_restriction"] = True
            trace["final"] = "reject"
            trace["decision_contract"]["rejection_reason"] = "operation_restriction"
            return {
                "status": "rejected",
                "failure_tag": "validation_leak",
                "matched": None,
                "parsed_model": model,
                "decision_trace": trace,
                "error": restriction_reason
            }
        
        has_modifier, modifier_reason = _check_structural_modifier(
            model.get("objective", ""),
            model.get("constraints", []),
            match
        )
        if has_modifier:
            trace["decision_contract"]["conditions"]["constraints_consistent"] = False
            trace["structural_modifier"] = True
            trace["final"] = "reject"
            trace["decision_contract"]["rejection_reason"] = "structural_modifier"
            return {
                "status": "rejected",
                "failure_tag": "validation_leak",
                "matched": None,
                "parsed_model": model,
                "decision_trace": trace,
                "error": modifier_reason
            }
        
        if repair_info.get("repair_used"):
            repair_threshold = 0.90
            if alignment_score < repair_threshold or constraint_consistency < repair_threshold or structural_compatibility < repair_threshold:
                trace["decision_contract"]["conditions"]["alignment_threshold_met"] = False
                trace["decision_contract"]["conditions"]["constraints_consistent"] = constraint_consistency < repair_threshold
                trace["decision_contract"]["conditions"]["structural_compatible"] = structural_compatibility < repair_threshold
                trace["final"] = "reject"
                trace["decision_contract"]["rejection_reason"] = "reduced_confidence_due_to_repair"
                trace["decision_contract"]["repair_threshold"] = repair_threshold
                return {
                    "status": "rejected",
                    "failure_tag": "matcher_miss",
                    "matched": None,
                    "parsed_model": model,
                    "decision_trace": trace,
                    "justification": f"Accept blocked: json_repair used, requires {repair_threshold} on all sub-scores. Got alignment={alignment_score}, constraint={constraint_consistency}, structural={structural_compatibility}"
                }
        
        all_conditions_met = (
            alignment_score >= ALIGNMENT_THRESHOLD and
            constraint_consistency >= 0.7 and
            structural_compatibility >= 0.7
        )
        
        if all_conditions_met:
            trace["decision_contract"]["conditions"]["alignment_threshold_met"] = True
            trace["decision_contract"]["conditions"]["constraints_consistent"] = True
            trace["decision_contract"]["conditions"]["structural_compatible"] = True
            trace["final"] = "accept"
            trace["decision_contract"]["accept_condition"] = "all_conditions_met"
            return {
                "status": "success",
                "failure_tag": None,
                "matched": match,
                "parsed_model": model,
                "alignment_score": alignment_score,
                "constraint_consistency": constraint_consistency,
                "structural_compatibility": structural_compatibility,
                "decision_trace": trace
            }
        else:
            trace["decision_contract"]["conditions"]["alignment_threshold_met"] = alignment_score >= ALIGNMENT_THRESHOLD
            trace["decision_contract"]["conditions"]["constraints_consistent"] = constraint_consistency >= 0.7
            trace["decision_contract"]["conditions"]["structural_compatible"] = structural_compatibility >= 0.7
            trace["final"] = "reject"
            trace["decision_contract"]["rejection_reason"] = "决策_contract_conditions_not_met"
            return {
                "status": "rejected",
                "failure_tag": "validation_leak",
                "matched": None,
                "parsed_model": model,
                "decision_trace": trace,
                "justification": f"Accept blocked: alignment={alignment_score} (need {ALIGNMENT_THRESHOLD}), constraint={constraint_consistency} (need 0.7), structural={structural_compatibility} (need 0.7)"
            }
    
    trace["final"] = "reject"
    trace["decision_contract"]["rejection_reason"] = "no_valid_match"
    return {
        "status": "rejected",
        "failure_tag": "matcher_miss" if match else "parser_fail",
        "matched": match,
        "parsed_model": model,
        "decision_trace": trace
    }


def analyze_statement(statement: str) -> dict:
    """Single LLM call: parse + match + alignment decomposition + decision."""
    problems = get_registry_problems()
    registry_context = build_registry_context(problems)
    
    prompt = _UNIFIED_PROMPT.format(
        registry=registry_context,
        statement=statement
    )
    
    response = _call_llm(prompt)
    
    repair_info = {}
    try:
        result = _extract_json_object(response, repair_info)
    except ValueError as e:
        raise ValueError(f"Invalid JSON response: {response[:200]}")
    
    model = result.get("parsed_model", {})
    match = result.get("match_candidate")
    decision = result.get("decision", "reject")
    justification = result.get("justification", "")
    
    original_objective = model.get("objective", "")
    canonical_objective = canonicalize_objective(original_objective)
    model["objective_canonical"] = canonical_objective
    
    alignment_score = float(result.get("alignment_score", 0.0))
    constraint_consistency = float(result.get("constraint_consistency", 0.0))
    structural_compatibility = float(result.get("structural_compatibility", 0.0))
    
    if match and match != "no match" and structural_compatibility == 1.0 and constraint_consistency == 1.0:
        if original_objective != canonical_objective:
            alignment_score = 1.0
    
    trace = {
        "llm_match": match,
        "alignment_score": alignment_score,
        "objective_canonical": canonical_objective,
        "constraint_consistency": constraint_consistency,
        "structural_compatibility": structural_compatibility,
        "contradiction": False,
        "json_repair": repair_info
    }
    
    return _evaluate_decision(
        match, decision, model,
        alignment_score, constraint_consistency, structural_compatibility,
        repair_info, trace
    )


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


_BATCH_PROMPT = """Analyze multiple problem statements against a registry.
Return a JSON array, one result object per statement.

Output Schema per statement:
{{
  "statement_id": "string - maps to input order",
  "parsed_model": {{
    "input_type": "string",
    "output_type": "string", 
    "objective": "string",
    "constraints": ["list or empty if not stated"],
    "edge_conditions": ["list or empty if not stated"],
    "types_explicit": "boolean"
  }},
  "match_candidate": "problem_id or 'no match'",
  "alignment_score": "float 0.0-1.0 - OBJECTIVE keyword match",
  "constraint_consistency": "float 0.0-1.0",
  "structural_compatibility": "float 0.0-1.0",
  "decision": "accept|reject",
  "justification": "string"
}}

CRITICAL RULES:
- Match ONLY if input_type, output_type, AND objective ALL align
- "Increasing subsequence" != "Common subsequence"
- "Maximum product" != "Maximum sum"
- "Minimum cost" != "Number of ways"
- alignment_score requires EXPLICIT keyword match

Return ONLY a JSON array. No markdown. No prose.

{registry}

---
STATEMENTS:
{numbered_statements}

Output:"""


def analyze_batch(statements: list, case_ids: list = None) -> list:
    """Batch analyze multiple statements in one LLM call."""
    if case_ids is None:
        case_ids = [f"case_{i}" for i in range(len(statements))]
    
    problems = get_registry_problems()
    registry_context = build_registry_context(problems)
    
    numbered = []
    for i, (case_id, stmt) in enumerate(zip(case_ids, statements)):
        numbered.append(f"{i+1}. [{case_id}] {stmt}")
    
    prompt = _BATCH_PROMPT.format(
        registry=registry_context,
        numbered_statements="\n".join(numbered)
    )
    
    response = _call_llm(prompt)
    
    repair_info = {}
    try:
        results = _extract_json_array(response, repair_info)
    except ValueError as e:
        raise ValueError(f"Batch JSON parse failed: {e}. Response: {response[:500]}")
    
    if not isinstance(results, list):
        raise ValueError(f"Expected JSON array, got {type(results)}")
    
    analyzed = []
    for i, result in enumerate(results):
        case_id = case_ids[i] if i < len(case_ids) else f"case_{i}"
        
        model = result.get("parsed_model", {})
        match = result.get("match_candidate")
        decision = result.get("decision", "reject")
        justification = result.get("justification", "")
        
        original_objective = model.get("objective", "")
        canonical_objective = canonicalize_objective(original_objective)
        model["objective_canonical"] = canonical_objective
        
        alignment_score = float(result.get("alignment_score", 0.0))
        constraint_consistency = float(result.get("constraint_consistency", 0.0))
        structural_compatibility = float(result.get("structural_compatibility", 0.0))
        
        if match and match != "no match" and structural_compatibility == 1.0 and constraint_consistency == 1.0:
            if original_objective != canonical_objective:
                alignment_score = 1.0
        
        trace = {
            "llm_match": match,
            "alignment_score": alignment_score,
            "objective_canonical": canonical_objective,
            "constraint_consistency": constraint_consistency,
            "structural_compatibility": structural_compatibility,
            "contradiction": False,
            "json_repair": repair_info,
            "batch_mode": True
        }
        
        decision_result = _evaluate_decision(
            match, decision, model,
            alignment_score, constraint_consistency, structural_compatibility,
            repair_info, trace
        )
        
        decision_result["statement"] = statements[i]
        decision_result["user_id"] = case_id
        
        analyzed.append(decision_result)
    
    return analyzed


def run_batch_phase3(statements: list, case_ids: list = None) -> list:
    """Run Phase 3 batch with unified engine."""
    from datetime import datetime
    
    results = []
    for i, case_id in enumerate(case_ids or [f"case_{i}" for i in range(len(statements))]):
        results.append({
            "timestamp": datetime.now().isoformat(),
            "user_id": case_id,
            "statement": statements[i],
            "status": None,
            "failure_tag": None,
            "parsed_model": None,
            "matched": None,
            "decision_trace": {},
        })
    
    try:
        analyzed = analyze_batch(statements, case_ids)
        for i, analysis in enumerate(analyzed):
            results[i].update(analysis)
    except Exception as e:
        for r in results:
            r["status"] = "error"
            r["failure_tag"] = "parser_fail"
            r["error"] = str(e)
    
    return results


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
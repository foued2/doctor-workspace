import hashlib
import json
import os
import pathlib
import time
from typing import Any, Dict, Tuple

from doctor.ingest.registry_matcher import (
    NO_MATCH,
    SINGLE_CALL_ANALYSIS_KEY,
    build_registry_context,
    get_registry_problems,
    normalize_alignment_score,
    normalize_match_candidate,
)


GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_MODEL = os.environ.get("GOOGLE_MODEL", "gemini-2.5-flash")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get(
    "OPENROUTER_MODEL",
    "google/gemma-4-31b-it:free",
)
PROVIDER = os.environ.get("LLM_PROVIDER", "groq")

CACHE_DIR = pathlib.Path(__file__).parent / ".llm_cache"
CACHE_DIR.mkdir(exist_ok=True)

MAX_RETRIES = 5
INITIAL_BACKOFF = 2

_PROMPT = """You analyze algorithmic problem statements against a registry of known problems.

Return ONLY valid JSON with this exact top-level structure:
{{
  "parsed_model": {{
    "input_type": "string",
    "output_type": "string",
    "objective": "string",
    "constraints": ["string"],
    "edge_conditions": ["string"],
    "input_type_inferred": true,
    "output_type_inferred": true,
    "constraints_inferred": true,
    "edge_conditions_inferred": true,
    "infer_confidence": "high|low"
  }},
  "match_candidate": "problem_id or 'no match'",
  "alignment_score": 0.0,
  "decision": "accept|reject",
  "justification": "brief explanation"
}}

Rules:
- Use only `problem_id` values that appear in the registry context.
- `alignment_score` must be a number from 0.0 to 1.0.
- Accept only when input type, output type, and objective align with one registry problem.
- Ambiguous or underspecified statements must reject instead of guessing.
- Domain disguises are valid only if the computational structure still matches.
- Output JSON only. No markdown. No prose outside the JSON object.

REGISTRY:
{registry}

STATEMENT:
{problem_statement}

Output ONLY JSON:"""


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def _call_llm_with_stats(prompt: str, retries: int = 0) -> Tuple[str, int]:
    h = _hash(prompt)
    cache_file = CACHE_DIR / f"single_call_{h}.json"

    if cache_file.exists():
        cached = json.loads(cache_file.read_text())
        return cached["response"], int(cached.get("retry_count", 0))

    import requests

    if PROVIDER == "google" and GOOGLE_API_KEY:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GOOGLE_MODEL}:generateContent"
        params = {"key": GOOGLE_API_KEY}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 3000},
        }
        headers = None
        use_google = True
    elif PROVIDER == "openrouter" and OPENROUTER_API_KEY:
        url = "https://openrouter.ai/api/v1/chat/completions"
        params = None
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 3000,
        }
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/foued2/doctor-workspace",
            "X-Title": "doctor-workspace",
        }
        use_google = False
    else:
        if not GROQ_API_KEY:
            raise ValueError(f"{PROVIDER.upper()} credentials not set")
        url = "https://api.groq.com/openai/v1/chat/completions"
        params = None
        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 3000,
        }
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        use_google = False

    try:
        response = requests.post(
            url,
            params=params,
            headers=headers,
            json=payload,
            timeout=120,
        )
    except requests.exceptions.RequestException as exc:
        if retries < MAX_RETRIES:
            wait = INITIAL_BACKOFF ** retries
            time.sleep(wait)
            return _call_llm_with_stats(prompt, retries + 1)
        raise RuntimeError(f"Request failed after {MAX_RETRIES} retries: {exc}")

    if response.status_code == 429:
        if retries < MAX_RETRIES:
            wait = INITIAL_BACKOFF ** retries
            time.sleep(wait)
            return _call_llm_with_stats(prompt, retries + 1)
        raise RuntimeError(f"Rate limit exceeded after {MAX_RETRIES} retries")

    if response.status_code != 200:
        raise RuntimeError(f"API error {response.status_code}: {response.text[:300]}")

    if use_google:
        result = response.json()
        resp = result["candidates"][0]["content"]["parts"][0]["text"]
    else:
        resp = response.json()["choices"][0]["message"]["content"]

    cache_file.write_text(
        json.dumps({"response": resp, "retry_count": retries}, indent=2)
    )
    return resp, retries


def _call_llm(prompt: str, retries: int = 0) -> str:
    response, _ = _call_llm_with_stats(prompt, retries)
    return response


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


def _coerce_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0"}:
            return False
    return default


def _coerce_text(value: Any, field_name: str) -> str:
    if value is None:
        raise ValueError(f"Missing {field_name}")

    if isinstance(value, bool):
        if value is False:
            raise ValueError(f"Missing {field_name}")
        return f"[{field_name} from context]"

    text = str(value).strip()
    if not text:
        raise ValueError(f"Missing {field_name}")
    return text


def _coerce_list(value: Any) -> list[str]:
    if value is None or value is False:
        return []
    if isinstance(value, list):
        items = value
    else:
        items = [value]

    normalized = []
    for item in items:
        text = str(item).strip()
        if text:
            normalized.append(text)
    return normalized


def _normalize_parsed_model(raw_model: Any) -> Dict[str, Any]:
    if not isinstance(raw_model, dict):
        raise ValueError("Missing parsed_model")

    normalized = {
        "input_type": _coerce_text(raw_model.get("input_type"), "input_type"),
        "output_type": _coerce_text(raw_model.get("output_type"), "output_type"),
        "objective": _coerce_text(raw_model.get("objective"), "objective"),
        "constraints": _coerce_list(raw_model.get("constraints")),
        "edge_conditions": _coerce_list(raw_model.get("edge_conditions")),
    }

    infer_confidence = str(raw_model.get("infer_confidence", "low")).strip().lower()
    if infer_confidence not in {"high", "low"}:
        infer_confidence = "low"

    normalized["infer_confidence"] = infer_confidence
    normalized["_inferred"] = {
        "input_type": _coerce_bool(raw_model.get("input_type_inferred")),
        "output_type": _coerce_bool(raw_model.get("output_type_inferred")),
        "constraints": _coerce_bool(raw_model.get("constraints_inferred")),
        "edge_conditions": _coerce_bool(raw_model.get("edge_conditions_inferred")),
        "infer_confidence": infer_confidence,
    }
    return normalized


def analyze_problem(statement: str) -> Dict[str, Any]:
    """Single LLM call: parse + match + alignment decision."""
    problems = get_registry_problems()
    if not problems:
        raise ValueError("Registry empty")

    registry_context = build_registry_context(problems)
    prompt = _PROMPT.format(
        registry=registry_context,
        problem_statement=statement,
    )

    response, retry_count = _call_llm_with_stats(prompt)
    repair_info = {}
    raw_result = _extract_json_object(response, repair_info)

    parsed_model = _normalize_parsed_model(raw_result.get("parsed_model"))
    normalized_match = normalize_match_candidate(
        raw_result.get("match_candidate"),
        problems,
    )
    decision = str(raw_result.get("decision", "reject")).strip().lower()
    if decision not in {"accept", "reject"}:
        decision = "reject"

    justification = str(raw_result.get("justification", "")).strip()
    alignment_score = normalize_alignment_score(raw_result.get("alignment_score"))

    if normalized_match is None:
        match_candidate = NO_MATCH
    else:
        match_candidate = normalized_match

    if decision == "accept" and match_candidate == NO_MATCH:
        decision = "reject"
        if not justification:
            justification = "Accepted without a valid registry problem_id"

    return {
        "parsed_model": parsed_model,
        "match_candidate": match_candidate,
        "alignment_score": alignment_score,
        "alignment_score_diagnostic_only": True,
        "decision": decision,
        "justification": justification,
        "retry_count": retry_count,
        "json_repair": repair_info,
    }


def parse_problem(statement: str) -> Dict[str, Any]:
    analysis = analyze_problem(statement)
    model = analysis["parsed_model"]
    model[SINGLE_CALL_ANALYSIS_KEY] = {
        "match_candidate": analysis["match_candidate"],
        "alignment_score": analysis["alignment_score"],
        "alignment_score_diagnostic_only": True,
        "decision": analysis["decision"],
        "justification": analysis["justification"],
        "retry_count": analysis["retry_count"],
        "json_repair": analysis.get("json_repair"),
    }
    return model


def check_completeness(model: Dict[str, Any]):
    issues = []
    for field_name in ["input_type", "output_type", "objective"]:
        if not model.get(field_name):
            issues.append(f"missing {field_name}")
    return len(issues) == 0, issues


def confirm_model(model: Dict[str, Any]):
    lines = [
        "Problem model extracted:",
        f"INPUT: {model.get('input_type')}",
        f"OUTPUT: {model.get('output_type')}",
        f"OBJECTIVE: {model.get('objective')}",
    ]
    constraints = model.get("constraints", [])
    lines.append(f"CONSTRAINTS(inferred): {constraints or '(none)'}")
    edge_conditions = model.get("edge_conditions", [])
    lines.append(f"EDGE CASES(inferred): {edge_conditions or '(none)'}")
    lines.append("Confirm YES or describe issue:")
    return "\n".join(lines)

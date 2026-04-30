import json
from typing import Any, Dict

from doctor.llm_client import _call_llm, _call_llm_with_stats
from doctor.ingest.registry_matcher import (
    MIN_ALIGNMENT_SCORE,
    NO_MATCH,
    SINGLE_CALL_ANALYSIS_KEY,
    build_registry_context,
    get_registry_problems,
    normalize_alignment_score,
    normalize_match_candidate,
)

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
- Domain disguise rule: When domain术语 ("gain"/"profit"/"return") matches algorithmic structure (contiguous max sum), score alignment at 1.0 — terminology distance should NOT reduce alignment.
- Operation consistency rule: If the problem statement contains explicit operations (sort, rotate, reverse, swap, shuffle, merge without combining, split without separating) OR additional constraints on indices, lengths, positions, counting direction, or ranges that are absent from the matched algorithm's canonical definition, reduce alignment_score by at least 0.3. Extraneous operations and added constraints that alter valid solution criteria are REJECTION signals, not edge conditions to ignore.

REGISTRY:
{registry}

STATEMENT:
{problem_statement}

Output ONLY JSON:"""


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


def classify_objective(statement: str) -> tuple[str, str, str]:
    """Classify problem statement into objective class using LLM.
    
    Returns: (objective_class, confidence, parse_error)
    """
    import json
    
    prompt = f"""Classify this problem statement into exactly one objective class.
Classes: optimization, equality_check, counting, transformation, selection, none

Return only valid JSON:
{{"objective_class": "<class>", "confidence": "high|low"}}

Use none only when no objective class is identifiable.
Use low confidence when class is present but phrasing is indirect.
No explanation. No free text. No class outside this list.

Statement: {statement}

Output JSON:"""
    
    try:
        response, _ = _call_llm_with_stats(prompt)
        data = json.loads(response.strip())
        obj_class = data.get("objective_class", "none")
        confidence = data.get("confidence", "low")
        # Validate class is in allowed list
        allowed = {"optimization", "equality_check", "counting", "transformation", "selection", "none"}
        if obj_class not in allowed:
            return "none", "low", f"invalid class: {obj_class}"
        return obj_class, confidence, ""
    except json.JSONDecodeError as e:
        return "none", "low", f"json parse error: {e}"
    except Exception as e:
        return ["none"], "low", f"call error: {e}"


def _check_structural_sufficiency(statement: str) -> tuple[bool, str]:
    """Check if statement has sufficient structural signal before attempting match.
    
    Returns: (is_sufficient, reason_if_not)
    """
    s = statement.lower()
    
    # 2. Explicit operation (expanded)
    operation_patterns = [
        "find", "locate", "identify", "check", "validate", "determine",
        "return", "compute", "count", "remove", "reverse", "merge", "sort",
        "minimize", "maximize", "add", "combine", "convert", "output",
        "revers", "match", "take", "get", "need", "use", "what", "how",
        "calculate", "figure", "tell", "give"
    ]
    has_operation = any(pat in s for pat in operation_patterns)
    
    # 3. Objective class via LLM (replaces pattern-based objective check)
    obj_class, obj_confidence, obj_error = classify_objective(statement)
    
    # Handle parse errors - log separately, treat as low confidence
    if obj_error:
        obj_confidence = "low"
    
    # Decision rules:
    # - objective_class == none -> reject
    # - objective_class != none + confidence == high -> pass
    # - objective_class != none + confidence == low -> tentative pass (flag for matcher)
    if obj_class == "none":
        return False, f"no objective class (classification failed)"
    
    is_tentative = (obj_confidence == "low")
    
    # Derive input_type from objective class
    # optimization -> numeric/array, equality_check -> string/array, counting -> integer
    # transformation -> array/string/integer (includes aggregation: merge, combine, prefix)
    # selection -> array/numeric
    derived_input_types = {
        "optimization": ["array", "number", "integer", "nums", "string", "characters", "rectangle", "contiguous", "cost", "area", "profit", "values", "elements", "subarray", "denominations", "coins", "amount"],
        "equality_check": ["string", "array", "word", "brackets", "balanced", "parentheses", "anagram", "braces", "opening", "closing", "number", "integer", "digit"],
        "counting": ["integer", "number", "array", "ways", "stairs", "combinations", "paths", "grid", "change", "heights", "bars", "elevation"],
        "transformation": ["array", "string", "integer", "number", "digits", "lists", "sorted", "strings", "elements", "prefix", "common", "values", "subsequence", "pairs", "parentheses", "n"],
        "selection": ["array", "number", "integer", "strings", "lists", "elements", "indices", "kth", "substring"],
    }
    derived_types = derived_input_types.get(obj_class, [])
    def _norm(word):
        return word[:-1] if word.endswith('s') else word
    statement_words = [w.strip('.,!?;:') for w in statement.split()]
    norm_statement_words = [_norm(w) for w in statement_words]
    has_input_type = any(_norm(t) in norm_statement_words for t in derived_types)
    
    # Fragment filter: reject ultra-short statements that are likely fragments
    tokens = statement.split()
    if len(tokens) < 5:
        tight_verbs = ["find", "check", "validate", "determine", "compute", "return", "remove", "reverse", "merge", "combine", "minimize", "maximize", "identify"]
        has_tight_verb = any(tok.lower() in tight_verbs for tok in tokens)
        if not has_tight_verb:
            return False, "fragment: too short, no verb"
    
    # Hard schema validation gate: reject if ANY required field is missing
    if not has_input_type:
        return False, f"no input type (derived from {obj_class})"
    if not has_operation:
        return False, "no operation"
    if len(statement) < 12:
        return False, "too short"
    
    # Pass with tentative flag if low confidence
    if is_tentative:
        return True, f"tentative (low confidence class: {obj_class})"
    
    return True, f"class: {obj_class}"


def analyze_problem(statement: str) -> Dict[str, Any]:
    """Single LLM call: parse + match + alignment decision."""
    
    # Structural sufficiency gate - reject before LLM
    is_sufficient, gate_reason = _check_structural_sufficiency(statement)
    if not is_sufficient:
        return {
            "parsed_model": {
                "input_type": "",
                "output_type": "",
                "objective": "",
                "constraints": [],
                "edge_conditions": [],
            },
            "match_candidate": None,
            "alignment_score": 0.0,
            "decision": "reject",
            "justification": gate_reason,
            "retry_count": 0,
            "structural_gate_rejection": True,
            "schema_classification": {},
        }
    
    problems = get_registry_problems()
    if not problems:
        raise ValueError("Registry empty")

    # Classify schema after gate passes
    try:
        from doctor.schema_classifier import classify_schema
        schema_info = classify_schema(statement)
    except Exception as e:
        schema_info = {"error": str(e)}

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

    if decision == "accept" and alignment_score < MIN_ALIGNMENT_SCORE:
        decision = "reject"
        justification = (
            f"Alignment score {alignment_score:.2f} below minimum "
            f"{MIN_ALIGNMENT_SCORE:.2f}"
        )

    return {
        "parsed_model": parsed_model,
        "match_candidate": match_candidate,
        "alignment_score": alignment_score,
        "alignment_score_diagnostic_only": True,
        "decision": decision,
        "justification": justification,
        "retry_count": retry_count,
        "json_repair": repair_info,
        "schema_classification": schema_info,
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

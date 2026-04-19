import os
import json
import hashlib
import pathlib

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

CACHE_DIR = pathlib.Path(__file__).parent / ".llm_cache"
CACHE_DIR.mkdir(exist_ok=True)

def _hash(text):
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def _call_llm(prompt: str) -> str:
    h = _hash(prompt)
    cache_file = CACHE_DIR / f"parse_{h}.json"
    
    if cache_file.exists():
        return json.loads(cache_file.read_text())["response"]
    
    import requests
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set")
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.2, "max_tokens": 2000}
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=60)
    if response.status_code != 200:
        raise RuntimeError(f"Groq error {response.status_code}: {response.text[:300]}")
    
    resp = response.json()["choices"][0]["message"]["content"]
    cache_file.write_text(json.dumps({"response": resp}, indent=2))
    return resp


_PROMPT = """Extract structured problem model from statement. Output ONLY valid JSON.

Fields:
1. input_type: function input type
2. output_type: function output type  
3. objective: one sentence
4. constraints: list (infer if not stated)
5. edge_conditions: list (infer if not stated)
6. input_type_inferred: boolean
7. output_type_inferred: boolean
8. constraints_inferred: boolean
9. edge_conditions_inferred: boolean

Example for "Two Sum":
{{"input_type": "array of integers, integer", "output_type": "list of integers", "objective": "Find indices of two numbers that sum to target", "constraints": ["1 <= len <= 10000", "exactly one solution"], "edge_conditions": ["empty array", "single element", "duplicates", "no solution exists"], "input_type_inferred": false, "output_type_inferred": false, "constraints_inferred": true, "edge_conditions_inferred": true}}

Problem: {problem_statement}

Output ONLY JSON:"""


def parse_problem(statement: str):
    response = _call_llm(_PROMPT.format(problem_statement=statement))
    start, end = response.find("{"), response.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Invalid JSON response")
    model = json.loads(response[start:end+1])
    
    inferred = {}
    for f in ["input_type", "output_type", "constraints", "edge_conditions"]:
        key = f"{f}_inferred"
        inferred[f] = model.pop(key, False)
    model["_inferred"] = inferred
    
    for f in ["input_type", "output_type", "objective"]:
        if f not in model or not model[f]:
            raise ValueError(f"Missing {f}")
    
    if not model.get("constraints"):
        raise ValueError("constraints empty")
    if not model.get("edge_conditions"):
        raise ValueError("edge_conditions empty")
    
    inf = model.get("_inferred", {})
    if inf.get("input_type") and inf.get("output_type"):
        raise ValueError("Ambiguous: both inferred")
    
    return model


def check_completeness(model):
    issues = []
    for f in ["input_type", "output_type", "objective"]:
        if not model.get(f):
            issues.append(f"missing {f}")
    return len(issues) == 0, issues


def confirm_model(model):
    inf = model.get("_inferred", {})
    lines = [
        "Problem model extracted:",
        f"INPUT: {model.get('input_type')}",
        f"OUTPUT: {model.get('output_type')}",
        f"OBJECTIVE: {model.get('objective')}",
    ]
    cons = model.get("constraints", [])
    lines.append(f"CONSTRAINTS(inferred): {cons or '(none)'}")
    edge = model.get("edge_conditions", [])
    lines.append(f"EDGE CASES(inferred): {edge or '(none)'}")
    lines.append("Confirm YES or describe issue:")
    return "\n".join(lines)
"""
Layer 1 AI — LLM-based solution verifier.

Replaces CodeAnalyzer static analysis with an LLM verdict.
Uses Ollama (local) by default — no API keys, no cost.

Endpoint: http://localhost:11434/api/generate
Model: phi3 (3.8B, runs on 16GB RAM with room to spare)
"""
import json
import re
import requests

_OLLAMA_URL = "http://localhost:11434/api/generate"
_OLLAMA_MODEL = "phi3"


def get_ai_verdict(problem_text: str, solution_code: str) -> dict:
    """Get LLM verdict for a LeetCode solution using Ollama."""
    prompt = f"""You are evaluating a LeetCode solution.

Problem:
{problem_text}

Code:
{solution_code}

Classify as correct, partial, or incorrect.
Output JSON only:
{{"verdict": "correct|partial|incorrect", "confidence": 0.0-1.0, "reasoning": "one sentence"}}"""

    response = requests.post(_OLLAMA_URL, json={
        "model": _OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0}
    }, timeout=120)

    raw = response.json()["response"].strip()

    # Robust JSON extraction — LLM may wrap in markdown or include extra text
    parsed = _extract_json(raw)

    return {
        "model": _OLLAMA_MODEL,
        "prompt": prompt,
        "raw_response": raw,
        "verdict": parsed["verdict"],
        "confidence": parsed["confidence"],
        "reasoning": parsed["reasoning"],
    }


def _extract_json(raw: str) -> dict:
    """Extract JSON from potentially messy LLM output."""
    # Try direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Strip markdown code blocks
    if "```" in raw:
        for block in raw.split("```"):
            block = block.strip()
            if block.startswith("json"):
                block = block[4:].strip()
            try:
                return json.loads(block)
            except json.JSONDecodeError:
                continue

    # Fallback: find first { and last }
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(raw[start:end + 1])
        except json.JSONDecodeError:
            pass

    # Last resort: return defaults
    return {
        "verdict": "incorrect",
        "confidence": 0.5,
        "reasoning": f"Could not parse LLM output: {raw[:200]}"
    }


def check_reasoning_matches_code(reasoning: str, solution_code: str) -> bool:
    """Check if the AI's reasoning actually references the code it was given.
    
    If reasoning shares less than 2 meaningful tokens with the code,
    the AI is likely hallucinating — describing a different solution.
    """
    code_tokens = set(re.findall(r'\b[a-z_][a-z_0-9]*\b', solution_code.lower()))
    reasoning_tokens = set(re.findall(r'\b[a-z_][a-z_0-9]*\b', reasoning.lower()))
    noise = {'the', 'a', 'is', 'in', 'to', 'if', 'for', 'return', 'def',
             'and', 'or', 'not', 'of', 'this', 'that', 'with', 'by', 'it',
             'as', 'an', 'be', 'are', 'was', 'from', 'its', 'on', 'but'}
    overlap = (code_tokens & reasoning_tokens) - noise
    return len(overlap) >= 2

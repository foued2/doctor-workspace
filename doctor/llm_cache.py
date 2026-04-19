#!/usr/bin/env python3
"""
LLM Cache Layer for deterministic evaluation.

Every LLM call is cached: input hash → stored response.
Replays always hit cache, never live API.

Usage:
    from doctor.llm_cache import cached_call
    response = cached_call("prompt_key", lambda: call_api())
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Callable


CACHE_DIR = Path(__file__).parent / ".llm_cache"
CACHE_DIR.mkdir(exist_ok=True)


def _hash_input(text: str) -> str:
    """Create deterministic hash of input text."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def get_cache_path(key: str) -> Path:
    """Get path for cache file."""
    return CACHE_DIR / f"{key}.json"


def cached_call(key: str, fetch_fn: Callable[[], str]) -> str:
    """
    Call LLM with caching.
    
    Args:
        key: Identifier for this call type (e.g., "parser", "matcher")
        fetch_fn: Function that makes live API call
        
    Returns:
        LLM response (from cache or live)
    """
    cache_file = get_cache_path(key)
    
    if cache_file.exists():
        cached = json.loads(cache_file.read_text())
        return cached["response"]
    
    response = fetch_fn()
    
    cache_file.write_text(json.dumps({
        "key": key,
        "response": response,
    }, indent=2))
    
    return response


def cached_parse(problem_statement: str) -> Dict[str, Any]:
    """Parse with caching."""
    from doctor.ingest.problem_parser import _call_llm, _PROMPT
    
    prompt = _PROMPT.format(problem_statement=problem_statement)
    prompt_hash = _hash_input(prompt)
    
    cache_file = get_cache_path(f"parse_{prompt_hash}")
    
    if cache_file.exists():
        print(f"[CACHE HIT] parse: {problem_statement[:30]}...")
        return json.loads(cache_file.read_text())
    
    print(f"[CACHE MISS] parse: {problem_statement[:30]}...")
    response = _call_llm(prompt)
    
    start, end = response.find("{"), response.rfind("}")
    if start >= 0 and end > start:
        model = json.loads(response[start:end+1])
        cache_file.write_text(json.dumps(model, indent=2))
        return model
    
    raise ValueError(f"No JSON in response: {response[:200]}")


def cached_match(model: Dict) -> tuple:
    """Match with caching."""
    from doctor.ingest.registry_matcher import build_registry_context, get_problems, _MATCH_PROMPT
    
    problems = get_problems()
    registry = build_registry_context(problems)
    
    match_input = f"{registry}|{model.get('input_type')}|{model.get('output_type')}|{model.get('objective')}"
    match_hash = _hash_input(match_input)
    
    cache_file = get_cache_path(f"match_{match_hash}")
    
    if cache_file.exists():
        print(f"[CACHE HIT] match: {model.get('input_type')}...")
        cached = json.loads(cache_file.read_text())
        return cached.get("match_id"), cached.get("justification")
    
    print(f"[CACHE MISS] match: {model.get('input_type')}...")
    from doctor.ingest.registry_matcher import _call_llm
    
    prompt = _MATCH_PROMPT.format(registry=registry, **model)
    response = _call_llm(prompt)
    
    start, end = response.find("{"), response.rfind("}")
    if start >= 0 and end > start:
        result = json.loads(response[start:end+1])
        match_id = result.get("match")
        justification = result.get("justification", "")
        
        cache_file.write_text(json.dumps({
            "match_id": match_id,
            "justification": justification,
        }, indent=2))
        
        return match_id, justification
    
    return None, f"Parse error: {response[:200]}"


def cache_stats() -> Dict[str, int]:
    """Return cache statistics."""
    files = list(CACHE_DIR.glob("*.json"))
    return {
        "cached_entries": len(files),
        "cache_dir": str(CACHE_DIR),
    }


def clear_cache():
    """Clear all cached responses."""
    for f in CACHE_DIR.glob("*.json"):
        f.unlink()
    print("Cache cleared.")


if __name__ == "__main__":
    print(f"Cache directory: {CACHE_DIR}")
    stats = cache_stats()
    print(f"Cached entries: {stats['cached_entries']}")
import hashlib
import json
import os
import pathlib
import time
from typing import Tuple


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

CACHE_DIR = pathlib.Path(__file__).parent / "ingest" / ".llm_cache"
CACHE_DIR.mkdir(exist_ok=True)

MAX_RETRIES = 5
INITIAL_BACKOFF = 2


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

import requests
import json
import time

print("Quick mistral test...")

# Simple test first
start = time.time()
resp = requests.post('http://localhost:11435/api/generate', json={
    'model': 'mistral',
    'prompt': 'Say "test" in JSON: {"result": "test"}',
    'stream': False,
    'options': {'temperature': 0}
}, timeout=60)
elapsed = time.time() - start

data = resp.json()
print(f"Simple test: {data.get('response', 'N/A')[:100]} ({elapsed:.1f}s)")

# Slightly longer test
start = time.time()
resp = requests.post('http://localhost:11435/api/generate', json={
    'model': 'mistral',
    'prompt': 'Classify this Python code as correct or incorrect: def add(a,b): return a+b. Output JSON: {"verdict": "correct", "confidence": 0.9}',
    'stream': False,
    'options': {'temperature': 0}
}, timeout=60)
elapsed = time.time() - start

data = resp.json()
print(f"Classification test: {data.get('response', 'N/A')[:200]} ({elapsed:.1f}s)")

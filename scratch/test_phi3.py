import requests
import json
import time

print("Testing phi3 with Ollama API (long timeout)...")

OLLAMA_URL = "http://localhost:11435/api/generate"

for attempt in range(3):
    print(f"\n--- Attempt {attempt+1} ---")
    try:
        print("Calling phi3 (may take 30-60s first time)...")
        resp = requests.post(OLLAMA_URL, json={
            "model": "phi3",
            "prompt": 'Say "yes". Output JSON: {"answer": "yes"}',
            "stream": False,
            "options": {"temperature": 0}
        }, timeout=300)
        data = resp.json()
        print(f"SUCCESS! Response keys: {list(data.keys())}")
        print(f"Response: {data.get('response', 'N/A')[:300]}")
        
        # Test logprobs
        print("\nTesting logprobs...")
        resp2 = requests.post(OLLAMA_URL, json={
            "model": "phi3",
            "prompt": 'Classify as correct. Output JSON: {"verdict": "correct", "confidence": 0.9}',
            "stream": False,
            "options": {"temperature": 0, "num_predict": 50}
        }, timeout=300)
        data2 = resp2.json()
        print(f"Has logprobs: {'logprobs' in data2}")
        print(f"Keys: {list(data2.keys())}")
        break
    except Exception as e:
        print(f"Error: {str(e)[:200]}")
        if attempt < 2:
            print("Retrying in 5s...")
            time.sleep(5)

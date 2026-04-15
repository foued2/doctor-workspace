import requests
import json

print("Testing mistral with logprobs...")

resp = requests.post('http://localhost:11435/api/generate', json={
    'model': 'mistral',
    'prompt': 'Classify as correct. Output JSON: {"verdict": "correct", "confidence": 0.9}',
    'stream': False,
    'options': {'temperature': 0, 'num_predict': 50}
}, timeout=300)
data = resp.json()
print('Keys:', list(data.keys()))
print('Has logprobs:', 'logprobs' in data)
print('Response:', data.get('response', 'N/A')[:200])

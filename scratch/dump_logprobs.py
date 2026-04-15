"""Dump ALL logprobs for probe 1 to understand tokenization."""
import json
import math
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

prompt_text = """You are evaluating a LeetCode solution.

Problem:
Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

Code:
def twoSum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        complement = target - n
        if complement in seen:
            return [seen[complement], i]
        seen[n] = i
    return []

Classify as correct, partial, or incorrect.
Output JSON only:
{"verdict": "correct|partial|incorrect", "confidence": 0.0-1.0, "reasoning": "one sentence"}"""

resp = requests.post(OLLAMA_URL, json={
    "model": MODEL,
    "prompt": prompt_text,
    "stream": False,
    "logprobs": True,
    "options": {"temperature": 0, "num_predict": 512}
}, timeout=300)

data = resp.json()
raw = data["response"].strip()
logprobs = data.get("logprobs", [])

print(f"Response: {raw[:120]}")
print(f"\nAll {len(logprobs)} tokens:")
for i, lp in enumerate(logprobs):
    t = lp["token"]
    lp_val = lp["logprob"]
    prob = math.exp(lp_val)
    # Reconstruct the text so far
    print(f"  [{i:3d}] {repr(t):>20}  logprob={lp_val:>8.4f}  P={prob:.4f}")
